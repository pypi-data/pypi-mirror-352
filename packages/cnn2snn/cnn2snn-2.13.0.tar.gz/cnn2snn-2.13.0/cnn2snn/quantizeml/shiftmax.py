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
"""Functions to convert QuantizedShiftmax to Akida.
"""
from akida import Shiftmax
from quantizeml.layers import QuantizedShiftmax
import numpy as np

from ..akida_versions import AkidaVersion
from .layer_utils import get_inbound_layers
from .weights import broadcast_and_set_variable
from .block_converter import BlockConverter, register_conversion_patterns


__all__ = ["ShiftmaxBlockConverter"]

_PATTERNS = [(QuantizedShiftmax,)]


def _set_shiftmax_variables(ak_layer, block):
    """Computes and sets the variables for an Akida Shiftmax layer.

    This function converts the variables of a Keras layer and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        block (list(:obj:`tf.keras.Layer`)): the block of keras layers.
    """
    input_shift = block[0].input_shift.value.numpy().astype(
        np.uint8)
    broadcast_and_set_variable(ak_layer.variables, "input_shift", input_shift)


def _create_shiftmax(block):
    """Parses a quantizeml QuantizedShiftmax layer and returns the
    corresponding Akida Shiftmax layer.

    Args:
        block (list(:obj:`tf.keras.Layer`)): list of quantizeml quantized layers.

    Returns:
        :obj:`akida.Shiftmax`: The created akida layer.
    """
    shiftmax = block[0]
    return Shiftmax(output_bits=shiftmax.exp_bitwidth + 1,
                    buffer_bits=shiftmax.buffer_bitwidth,
                    name=shiftmax.name)


def convert_quantized_shiftmax(model_ak, block):
    """Converts QuantizedShiftmax layer and its variables and adds it to the
    Akida's v2 model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        block (list(:obj:`tf.keras.Layer`)): list of quantizeml quantized layers.

    Returns:
        bool: Returns True for a successful conversion.
    """
    # Retrieve the akida inbound layers
    inbound_layers_ak = get_inbound_layers(model_ak, block[0])
    # Create and add layer to the akida model
    layer_ak = _create_shiftmax(block)
    model_ak.add(layer_ak, inbound_layers_ak)
    # Set the akida layer converted variables
    _set_shiftmax_variables(layer_ak, block)
    return True


class ShiftmaxBlockConverter(BlockConverter):
    """Main class that should be used to check if the Shiftmax layer block is compatible to an
    Akida v2 conversion and provides a method to convert it in an equivalent Akida Shiftmax layer.

    Args:
        block (list): list of quantizeml quantized layers.
    """

    def convert(self, model_ak):
        return convert_quantized_shiftmax(model_ak, self._block)


# Register the valid shiftmax block pattern for Akida v2
register_conversion_patterns(AkidaVersion.v2, _PATTERNS, ShiftmaxBlockConverter)
