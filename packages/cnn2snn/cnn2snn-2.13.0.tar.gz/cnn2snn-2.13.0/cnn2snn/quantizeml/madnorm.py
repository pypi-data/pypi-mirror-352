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
"""Functions to convert QuantizedLayerNormalization to Akida.
"""
from akida import MadNorm
import quantizeml.layers as qlayers
import numpy as np

from ..akida_versions import AkidaVersion
from .layer_utils import get_inbound_layers
from .weights import broadcast_and_set_variable
from .outputs import set_output_v2_variables, parse_output_bits, parse_post_op_buffer_bits
from .block_converter import BlockConverter, register_conversion_patterns
from .blocks import get_block_out_quantizer

__all__ = ["MadNormBlockConverter"]

_PATTERNS = [(qlayers.QuantizedLayerNormalization,)]


def _set_madnorm_variables(ak_layer, block):
    """Computes and sets the variables for an Akida MadNorm layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        block (list(:obj:`tf.keras.Layer`)): the block of keras layers.
    """
    madnorm = block[0]
    assert isinstance(madnorm.gamma_quantizer, qlayers.WeightQuantizer)
    assert isinstance(madnorm.beta_quantizer, qlayers.AlignedWeightQuantizer)

    # get the QuantizedLayerNormalization gamma and shift
    gamma_ak = madnorm.gamma_quantizer.qweights.value.values.numpy()
    gamma_shift = madnorm.gamma_shift.value.numpy().astype(np.uint8)
    # get the QuantizedLayerNormalization beta and shift
    beta_quantizer = madnorm.beta_quantizer
    beta = beta_quantizer.qweights.value.values.numpy().astype(np.int32)
    beta_shift = beta_quantizer.shift.value.numpy().astype(np.uint8)
    beta_ak = (beta >> beta_shift).astype(np.int8)

    variables_ak = ak_layer.variables

    input_shift = getattr(madnorm, 'input_shift', None)
    if input_shift is not None:
        broadcast_and_set_variable(variables_ak, "input_shift",
                                   input_shift.value.numpy().astype(np.uint8))
    variables_ak["gamma"] = gamma_ak.astype(np.int8)
    broadcast_and_set_variable(variables_ak, "gamma_shift", gamma_shift)
    variables_ak["beta"] = beta_ak.astype(np.int8)
    broadcast_and_set_variable(variables_ak, "beta_shift", beta_shift)
    out_quantizer = get_block_out_quantizer(block)
    if out_quantizer:
        set_output_v2_variables(ak_layer, out_quantizer)


def _create_madnorm(block):
    """Parses a quantizeml QuantizedLayerNormalization layer and returns the
    params to create the corresponding Akida MadNorm layer.

    Args:
        block (list(:obj:`tf.keras.Layer`)): list of quantizeml quantized layers.

    Returns:
        :obj:`akida.MadNorm`: The created akida layer.
    """
    madnorm = block[0]
    # In quantizeml one bit is reserved automatically for the sign, but in
    # akida this is rather checked during the clipping operations.
    block_params = {"buffer_bits": madnorm.buffer_bitwidth + 1}
    # parse the block output bits
    parse_output_bits(block, block_params)
    # parse the block post op buffer bits
    parse_post_op_buffer_bits(block, block_params)

    return MadNorm(**block_params,
                   name=madnorm.name)


def convert_quantized_madnorm(model_ak, block):
    """Converts QuantizedLayerNormalization layer and its variables and adds
    it to the Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        block (list(:obj:`tf.keras.Layer`)): list of quantizeml quantized layers.

    Returns:
        bool: Returns True for a successful conversion.
    """
    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, block[0])
    # Create and add layer to the akida model
    layer_ak = _create_madnorm(block)
    model_ak.add(layer_ak, inbound_layers_ak)
    # Set the akida layer converted variables
    _set_madnorm_variables(layer_ak, block)
    return True


class MadNormBlockConverter(BlockConverter):
    """Main class that should be used to check if the madnorm layer block is compatible to an
    Akida v2 conversion and provides a method to convert it in an equivalent Akida v2 MadNorm layer.

    Args:
        block (list): list of quantizeml quantized layers.
    """

    def __init__(self, block):
        super().__init__(block)
        self._madnorm_additional_checks()

    def _madnorm_additional_checks(self):
        madnorm = self._block[0]
        # if input_shift available, make sure it has no negative values
        input_shift = getattr(madnorm, 'input_shift', None)
        if input_shift is not None:
            if input_shift.value and np.any(input_shift.value < 0):
                raise RuntimeError(
                    f"Layer {madnorm.name} contains negative values for " +
                    "input_shift, that is not supported")

    def convert(self, model_ak):
        return convert_quantized_madnorm(model_ak, self._block)


# Register the valid madnorm block pattern for Akida v2
register_conversion_patterns(AkidaVersion.v2, _PATTERNS, MadNormBlockConverter)
