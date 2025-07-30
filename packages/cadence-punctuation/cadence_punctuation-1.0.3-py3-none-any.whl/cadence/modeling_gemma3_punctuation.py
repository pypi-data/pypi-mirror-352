"""
Custom Gemma3 model for token classification with non-causal attention
"""

import torch
import torch.nn as nn
from typing import Optional, Tuple, List, Dict, Any
import types

from transformers import PretrainedConfig, PreTrainedModel
from transformers import Gemma3ForCausalLM
from transformers.models.gemma3.modeling_gemma3 import (
    Gemma3Attention,
    repeat_kv,
    apply_rotary_pos_emb,
    ALL_ATTENTION_FUNCTIONS,
    Cache,
    FlashAttentionKwargs,
)
from transformers.modeling_outputs import TokenClassifierOutput
from transformers.utils import logging

logger = logging.get_logger(__name__)


class Gemma3PunctuationConfig(PretrainedConfig):
    """
    Configuration class for Gemma3 punctuation model.
    """
    
    model_type = "cadence_punctuation"
    
    def __init__(
        self,
        num_labels: int = 31,
        classifier_dropout_prob: float = 0.0,
        use_non_causal_attention: bool = True,
        **kwargs
    ):
        self.num_labels = num_labels
        self.classifier_dropout_prob = classifier_dropout_prob
        self.use_non_causal_attention = use_non_causal_attention
        super().__init__(**kwargs)


def _extract_padding_mask_corrected(
    combined_mask_4d: Optional[torch.Tensor],
    debug_print: bool = False
) -> Optional[torch.Tensor]:
    """Extract padding mask from combined 4D attention mask."""
    if combined_mask_4d is None:
        return None
    
    mask_value = torch.finfo(combined_mask_4d.dtype).min
    is_key_padding = (combined_mask_4d == mask_value).all(dim=2, keepdim=True)
    padding_only_mask = torch.where(
        is_key_padding.expand_as(combined_mask_4d),
        torch.full_like(combined_mask_4d, mask_value),
        torch.zeros_like(combined_mask_4d)
    )
    return padding_only_mask


def non_causal_eager_attention_forward_with_padding(
    module: nn.Module, 
    query: torch.Tensor, 
    key: torch.Tensor, 
    value: torch.Tensor,
    attention_mask: Optional[torch.Tensor], 
    **kwargs: Any,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Non-causal eager attention implementation."""
    dropout = kwargs.get("dropout", 0.0)
    scaling = kwargs.get("scaling", None)
    softcap = kwargs.get("softcap", None)

    if scaling is None:
        head_dim = getattr(module, "head_dim", query.shape[-1])
        scaling = head_dim**-0.5
    
    num_key_value_groups = getattr(module, "num_key_value_groups", 1)
    key_states = repeat_kv(key, num_key_value_groups)
    value_states = repeat_kv(value, num_key_value_groups)
    
    attn_weights = torch.matmul(query, key_states.transpose(2, 3)) * scaling
    
    if softcap is not None:
        attn_weights = attn_weights / softcap
        attn_weights = torch.tanh(attn_weights)
        attn_weights = attn_weights * softcap
    
    if attention_mask is not None:
        mask_slice = attention_mask[:, :, :, : key_states.shape[-2]]
        attn_weights = attn_weights + mask_slice
        
    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query.dtype)
    is_training = getattr(module, "training", False)
    attn_weights = nn.functional.dropout(attn_weights, p=dropout, training=is_training)
    attn_output = torch.matmul(attn_weights, value_states)
    attn_output = attn_output.transpose(1, 2).contiguous()
    return attn_output, attn_weights


def modified_gemma3_attention_forward_non_causal(
    self: Gemma3Attention, 
    hidden_states: torch.Tensor, 
    position_embeddings: torch.Tensor,
    attention_mask: Optional[torch.Tensor], 
    past_key_value: Optional[Cache] = None,
    cache_position: Optional[torch.LongTensor] = None, 
    **kwargs: Any,
) -> tuple[torch.Tensor, Optional[torch.Tensor], Optional[Cache]]:
    """Modified Gemma3 attention forward for non-causal behavior."""
    bsz, q_len, _ = hidden_states.size()
    input_shape = hidden_states.shape[:-1]
    hidden_shape = (*input_shape, -1, self.head_dim)

    query_states = self.q_proj(hidden_states).view(hidden_shape).transpose(1, 2)
    key_states = self.k_proj(hidden_states).view(hidden_shape).transpose(1, 2)
    value_states = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)

    query_states = self.q_norm(query_states)
    key_states = self.k_norm(key_states)
    cos, sin = position_embeddings
    query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)

    if past_key_value is not None:
        cache_kwargs = {
            "sin": sin, 
            "cos": cos, 
            "cache_position": cache_position, 
            "sliding_window": self.sliding_window
        }
        key_states, value_states = past_key_value.update(
            key_states, value_states, self.layer_idx, cache_kwargs
        )

    effective_attn_implementation = self.config._attn_implementation
    output_attentions = kwargs.get("output_attentions", False)

    if effective_attn_implementation == "sdpa" and output_attentions:
        effective_attn_implementation = "eager"
    elif effective_attn_implementation == "flash_attention_2" and output_attentions:
        effective_attn_implementation = "eager"

    padding_only_mask = _extract_padding_mask_corrected(attention_mask)
    use_causal_flag = False  # Non-causal for punctuation

    # Select attention interface
    if effective_attn_implementation == "eager":
        attention_interface = non_causal_eager_attention_forward_with_padding
    elif effective_attn_implementation == "sdpa":
        attention_interface = ALL_ATTENTION_FUNCTIONS.get("sdpa", non_causal_eager_attention_forward_with_padding)
    elif effective_attn_implementation == "flash_attention_2":
        attention_interface = ALL_ATTENTION_FUNCTIONS.get("flash_attention_2", non_causal_eager_attention_forward_with_padding)
    else:
        attention_interface = non_causal_eager_attention_forward_with_padding

    final_attention_mask = padding_only_mask
    if final_attention_mask is not None:
        final_attention_mask = final_attention_mask.to(query_states.device)

    # Prepare kwargs for attention interface
    attn_specific_kwargs: Dict[str, Any] = {}
    if attention_interface == non_causal_eager_attention_forward_with_padding:
        attn_specific_kwargs = {
            "dropout": 0.0, 
            "scaling": self.scaling, 
            "softcap": getattr(self, "softcap", None)
        }
    elif effective_attn_implementation == "sdpa":
        attn_specific_kwargs = {"is_causal": use_causal_flag}
        if output_attentions: 
            attn_specific_kwargs["output_attentions"] = True
    elif effective_attn_implementation == "flash_attention_2":
        attn_specific_kwargs = {
            "causal": use_causal_flag,
            "softcap": getattr(self, "softcap", None),
            "dropout": 0.0
        }
        if output_attentions: 
            attn_specific_kwargs["output_attentions"] = True
    
    attn_output, attn_weights = attention_interface(
        self, query_states, key_states, value_states, final_attention_mask, **attn_specific_kwargs
    )

    attn_output = attn_output.reshape(*input_shape, -1).contiguous()
    attn_output = self.o_proj(attn_output)
    
    returned_weights = attn_weights if output_attentions and attn_weights is not None else None
   
    return attn_output, returned_weights


class Gemma3ForTokenClassification(Gemma3ForCausalLM):
    """
    Gemma3 model for token classification (punctuation prediction).
    Inherits from Gemma3ForCausalLM and replaces the LM head with classification head.
    """
    
    config_class = Gemma3PunctuationConfig
    
    def __init__(self, config):
        # Initialize the parent Gemma3ForCausalLM
        super().__init__(config)
        self.num_labels = config.num_labels
        
        # Replace the lm_head with classification head
        # Don't create a separate classifier - just replace lm_head directly
        classifier_dropout_prob = getattr(config, 'classifier_dropout_prob', 0.0)
        self.lm_head = nn.Sequential(
            nn.Dropout(classifier_dropout_prob),
            nn.Linear(config.hidden_size, config.num_labels)
        )
        
        # Update config for classification
        self.config.num_labels = config.num_labels
        
        # Initialize weights for the new head
        self.post_init()
        
        # Apply non-causal attention patching if requested
        if getattr(config, 'use_non_causal_attention', True):
            self._patch_attention_layers()
    
    def _patch_attention_layers(self):
        """Patch attention layers to use non-causal attention."""
        count = 0
        
        # The model structure is self.model.layers (inherited from Gemma3ForCausalLM)
        if hasattr(self, 'model') and hasattr(self.model, 'layers'):
            target_layers = self.model.layers
        else:
            logger.warning("Could not find model.layers for attention patching")
            return
            
        for idx, layer in enumerate(target_layers):
            if hasattr(layer, 'self_attn') and isinstance(layer.self_attn, Gemma3Attention):
                layer.self_attn.layer_idx = idx
                layer.self_attn.forward = types.MethodType(
                    modified_gemma3_attention_forward_non_causal, 
                    layer.self_attn
                )
                count += 1
        
        logger.info(f"Patched {count} attention layers for non-causal attention")
    
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        cache_position: Optional[torch.LongTensor] = None,
    ) -> TokenClassifierOutput:
        """
        Forward pass for token classification.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        # Call the parent's forward method but get the hidden states instead of logits
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            cache_position=cache_position,
        )

        # Get the hidden states from the model output
        sequence_output = outputs[0]
        
        # Apply the classification head (which is now self.lm_head)
        logits = self.lm_head(sequence_output)

        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))

        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output

        return TokenClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )


# Register the model for AutoModel
from transformers import AutoConfig, AutoModel
AutoConfig.register("cadence_punctuation", Gemma3PunctuationConfig)
AutoModel.register(Gemma3PunctuationConfig, Gemma3ForTokenClassification)