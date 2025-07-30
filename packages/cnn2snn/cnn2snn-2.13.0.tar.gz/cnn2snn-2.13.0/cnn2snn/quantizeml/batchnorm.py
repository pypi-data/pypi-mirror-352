#!/usr/bin/env python
# ******************************************************************************
# Copyright 2023 Brainchip Holdings Ltd.
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
"""Functions to convert QuantizedBatchNormalization to Akida.
"""
from akida import BatchNormalization, ActivationType
from quantizeml.layers import (QuantizedBatchNormalization, QuantizedReLU,
                               WeightQuantizer, AlignedWeightQuantizer)
import numpy as np

from .weights import broadcast_and_set_variable
from .outputs import set_output_v2_variables, parse_output_bits, parse_post_op_buffer_bits
from .activations import set_relu_variables
from .layer_utils import get_inbound_layers
from .block_converter import BlockConverter, register_conversion_patterns
from ..akida_versions import AkidaVersion
from .conv_common import get_layer_by_type
from .blocks import get_block_out_quantizer

__all__ = ["BatchNormBlockConverter"]

_PATTERNS = [(QuantizedBatchNormalization,),
             (QuantizedBatchNormalization, QuantizedReLU)]


def _set_batchnorm_variables(ak_layer, block):
    """Computes and sets the variables for an Akida BatchNormalization layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        block (list(:obj:`tf.keras.Layer`)): the block of keras layers.
    """
    layer_bn = block[0]
    assert isinstance(layer_bn.a_quantizer, WeightQuantizer)
    assert isinstance(layer_bn.b_quantizer, AlignedWeightQuantizer)

    # get the QuantizedBatchNormalization a, b and shift
    a_ak = layer_bn.a_quantizer.qweights.value.values.numpy()
    b_quantizer = layer_bn.b_quantizer
    b = b_quantizer.qweights.value.values.numpy().astype(np.int32)
    b_shift = b_quantizer.shift.value.numpy().astype(np.uint8)
    b_ak = (b >> b_shift).astype(np.int8)

    variables_ak = ak_layer.variables

    input_shift = layer_bn.input_shift.value
    if input_shift is not None:
        broadcast_and_set_variable(variables_ak, "input_shift",
                                   input_shift.numpy().astype(np.uint8))

    variables_ak["a"] = a_ak.astype(np.int8)
    variables_ak["b"] = b_ak
    broadcast_and_set_variable(variables_ak, "b_shift", b_shift)

    relu = get_layer_by_type(block, QuantizedReLU)
    if relu:
        set_relu_variables(ak_layer, relu)

    out_quantizer = get_block_out_quantizer(block)
    if out_quantizer:
        set_output_v2_variables(ak_layer, out_quantizer)


def _create_batchnorm(block):
    """Parses a quantizeml QuantizedBatchNormalization layers block and returns the
    corresponding Akida v2 BatchNormalization layer.

    Args:
        block (list(:obj:`tf.keras.Layer`)): list of quantizeml quantized layers.

    Returns:
        :obj:`akida.BatchNormalization`: The created akida layer.
    """
    bn = block[0]
    bn_params = {}
    relu = get_layer_by_type(block, QuantizedReLU)
    if relu:
        bn_params['activation'] = ActivationType.ReLU
    # In quantizeml one bit is reserved for the sign in the buffer bitwidth
    # variable, but in akida this value has to be added back to have the
    # correct clipping.
    bn_params['buffer_bits'] = bn.buffer_bitwidth + 1

    # parse the block output bits
    parse_output_bits(block, bn_params)
    # parse the block post op buffer bits
    parse_post_op_buffer_bits(block, bn_params)

    return BatchNormalization(**bn_params,
                              name=bn.name)


def convert_batchnorm_block(model_ak, block):
    """Converts QuantizedBatchNormalization layer and its variables and adds
    it to the Akida's model. If followed by QuantizedReLU, it will set its
    variables too.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be
            added.
        block (list(:obj:`tf.keras.Layer`)): list of quantizeml quantized layers.

    Returns:
        bool: Returns True for a successful conversion.
    """
    layer_ak = _create_batchnorm(block)
    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, block[0])
    # Add the layer to the Akida model
    model_ak.add(layer_ak, inbound_layers_ak)
    # Set its variables
    _set_batchnorm_variables(layer_ak, block)
    return True


class BatchNormBlockConverter(BlockConverter):
    """Main class that should be used to check if the batch norm layer block is compatible to an
    Akida v2 conversion and provides a method to convert it in an equivalent Akida
    BatchNormalization layer.

    Args:
        block (list): list of quantizeml quantized layers.
    """

    def convert(self, model_ak):
        return convert_batchnorm_block(model_ak, self._block)


# Register the valid batch norm block pattern for Akida v2
register_conversion_patterns(AkidaVersion.v2, _PATTERNS, BatchNormBlockConverter)
