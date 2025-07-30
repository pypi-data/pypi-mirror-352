#!/usr/bin/env python
# ******************************************************************************
# Copyright 2022 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
"""Functions to convert QuantizedAttention to Akida.
"""
from akida import Attention
from quantizeml.layers import QuantizedAttention
import numpy as np

from ..akida_versions import AkidaVersion
from .weights import broadcast_and_set_variable
from .layer_utils import get_inbound_layers
from .block_converter import BlockConverter, register_conversion_patterns
from .blocks import get_block_out_quantizer
from .outputs import set_output_v2_variables, parse_output_bits, parse_post_op_buffer_bits


__all__ = ["AttentionBlockConverter"]

_PATTERNS = [(QuantizedAttention,)]


def _set_attention_variables(ak_layer, block):
    """Computes and sets the variables for an Akida v2 Attention layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        block (list(:obj:`tf.keras.Layer`)): the block of keras layers.
    """
    attention_layer = block[0]
    variables_ak = ak_layer.variables

    # Get the QuantizedAttention layer shifts
    value_shift = attention_layer.values_shift.value.numpy().astype(np.uint8)
    broadcast_and_set_variable(variables_ak, "value_shift", value_shift)
    shiftmax = attention_layer.softmax_op
    shiftmax_input_shift = shiftmax.input_shift.value.numpy()
    broadcast_and_set_variable(ak_layer.variables, "shiftmax_input_shift",
                               shiftmax_input_shift.astype(np.uint8))
    out_quantizer = get_block_out_quantizer(block)
    if out_quantizer:
        set_output_v2_variables(ak_layer, out_quantizer)


def _create_attention(block):
    """Parses a quantizeml QuantizedAttention layer and returns the params to
    create the corresponding Akida Attention layer.

    Args:
        block (list(:obj:`tf.keras.Layer`)): list of quantizeml quantized layers.

    Returns:
        :obj:`akida.Attention`: The created akida layer.
    """
    attention_layer = block[0]
    # In quantizeml one bit is reserved automatically for the sign, but in akida
    # this is rather checked during the clipping operations.
    block_params = {"buffer_bits": attention_layer.buffer_bitwidth + 1}

    # parse the block output bits
    parse_output_bits(block, block_params)

    # parse the block post op buffer bits
    parse_post_op_buffer_bits(block, block_params)

    # As with output_bits and buffer_bits, shiftmax_output_bits is set with one
    # bit more.
    block_params['shiftmax_output_bits'] = attention_layer.softmax_op.exp_bitwidth + 1

    block_params['num_heads'] = attention_layer.num_heads
    return Attention(**block_params,
                     name=attention_layer.name)


def convert_quantized_attention(model_ak, block):
    """Converts QuantizedAttention layer and its variables and adds it to the
    Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        block (list(:obj:`tf.keras.Layer`)): list of quantizeml quantized layers.

    Returns:
        bool: Returns True for a successful conversion.
    """
    layer_ak = _create_attention(block)
    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, block[0])
    model_ak.add(layer_ak, inbound_layers_ak)
    _set_attention_variables(layer_ak, block)
    return True


class AttentionBlockConverter(BlockConverter):
    """Main class that should be used to check if the attention layer block is compatible to an
    Akida v2 conversion and provides a method to convert it in an equivalent Akida Attention layer.

    Args:
        block (list): list of quantizeml quantized layers.
    """

    def __init__(self, block):
        super().__init__(block)
        self._attention_additional_checks()

    def _attention_additional_checks(self):
        shiftmax = self._block[0].softmax_op
        # if input_shift available, make sure it has no negative values
        if shiftmax.input_shift.value:
            shiftmax_input_shift = shiftmax.input_shift.value.numpy()
            if np.any(shiftmax_input_shift < 0):
                raise ValueError(
                    f"Layer {self._block[0].name} contains negative values for " +
                    "shiftmax_input_shift, that is not supported")

    def convert(self, model_ak):
        return convert_quantized_attention(model_ak, self._block)


# Register the valid attention block pattern for Akida v2
register_conversion_patterns(AkidaVersion.v2, _PATTERNS, AttentionBlockConverter)
