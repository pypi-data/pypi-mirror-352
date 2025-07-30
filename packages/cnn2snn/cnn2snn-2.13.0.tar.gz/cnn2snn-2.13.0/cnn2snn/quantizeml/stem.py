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
"""Functions to convert Stem block quantized layers to Akida.
Those layers are:
    - The Embedding layer
    - The Reshape layer
    - The ClassToken (+ the DistToken for distilled models) layer(s)
    - The AddPosEmbedding layer
"""
from akida import LayerType, Stem
from quantizeml.layers import (QuantizedConv2D, QuantizedReshape,
                               QuantizedClassToken, QuantizedAddPositionEmbs, OutputQuantizer)
import numpy as np
from .blocks import get_block_out_quantizer
from .outputs import set_output_v2_variables
from .weights import broadcast_and_set_variables
from .block_converter import BlockConverter, register_conversion_patterns
from ..akida_versions import AkidaVersion

_PATTERNS = [(QuantizedConv2D, QuantizedReshape, QuantizedClassToken, QuantizedAddPositionEmbs),
             (QuantizedConv2D, QuantizedReshape, QuantizedAddPositionEmbs),
             (QuantizedConv2D, QuantizedReshape, QuantizedClassToken, QuantizedClassToken,
              QuantizedAddPositionEmbs)]


def _get_cls_layers(block):
    """Helper that returns the QuantizedClassToken layers of a stem block.

    Args:
        block (list): the quantizeml quantized layers of the Stem to convert.

    Returns:
        list: Returns a list of the QuantizedClassToken layers of a stem block.
    """

    return [layer for layer in block if isinstance(layer, QuantizedClassToken)]


def _set_stem_variables(ak_layer, block):
    """Computes and sets the variables for an Akida Stem layer.

    This function converts the variables of a Keras layers and sets them into
    the corresponding variables of the equivalent Akida layer.

    Args:
        ak_layer (:obj:`akida.Layer`): the targeted akida layer.
        block (list): list of the source quantized layers block.
    """
    assert ak_layer.parameters.layer_type == LayerType.Stem

    embedding_layer = block[0]

    # Get the optional QuantizedClassToken layer(s) and the QuantizedAddPositionEmbs layer
    cls_layers = _get_cls_layers(block)
    add_pos_emb_layer = block[-1]

    # Prepare a dict for akida variables
    variables_ak = {}

    # get the Embedding weights
    weights_ak = embedding_layer.weight_quantizer.qweights.value.fp.values.numpy()

    # get the Embedding bias
    bias_quantizer = embedding_layer.bias_quantizer
    bias = bias_quantizer.qweights.value.values.numpy().astype(np.int32)
    bias_shift = bias_quantizer.shift.value.numpy().astype(np.uint8)
    bias_ak = (bias >> bias_shift).astype(np.int8)

    if len(cls_layers) > 0:
        tokens_ak = []
        shifts_tokens_ak = []
        for cls_layer in cls_layers:
            # get the ClassToken layer token variable (aka cls member)
            cls_quantizer = cls_layer.cls_quantizer
            token = cls_quantizer.qweights.value.values.numpy().astype(np.int32)
            token_shift = cls_quantizer.shift.value.numpy().astype(np.uint8)
            token_ak = (token >> token_shift).astype(np.int8)
            # Insert the token value at the first position. This allows us to match
            # the model concatenation order.
            tokens_ak.insert(0, np.squeeze(token_ak))
            shifts_tokens_ak.insert(0, token_shift)
        variables_ak["tokens"] = np.stack(tokens_ak)
        variables_ak["tokens_shift"] = np.concatenate(shifts_tokens_ak)

    # get the positional embedding matrix
    pos_emb_quantizer = add_pos_emb_layer.pe_quantizer
    pos_emb = pos_emb_quantizer.qweights.value.values.numpy().astype(np.int32)
    pos_emb_shift = pos_emb_quantizer.shift.value.numpy().astype(np.uint8)
    pos_emb_ak = pos_emb >> pos_emb_shift
    variables_ak["pos_embedding"] = pos_emb_ak.astype(np.int8)
    # Get the QuantizedAddPositionEmbs layer shifts
    variables_ak["pos_embs_shift"] = pos_emb_shift

    variables_ak["weights"] = weights_ak.astype(np.int8)
    variables_ak["bias"] = bias_ak
    # Get the Embedding layer shifts
    variables_ak["bias_shift"] = bias_shift.astype(np.uint8)

    broadcast_and_set_variables(ak_layer, variables_ak)


def _parse_stem_block_layers(block):
    """Parses the quantizeml quantized additional layers of the Stem block and returns the
    params to create the corresponding Akida Stem layer.

    Args:
        layers (list): the quantizeml quantized layers of the Stem to convert.

    Returns:
        dict: the corresponding akida parameters.
    """
    # Extract neural layer of the block
    embedding = block[0]

    # Get the QuantizedClassToken layer(s)
    cls_layers = _get_cls_layers(block)

    # A block of layers always end with an OutputQuantizer. Extract it.
    out_quantizer = get_block_out_quantizer(block)
    assert isinstance(out_quantizer, OutputQuantizer)

    return dict(input_shape=embedding.input_shape[1:],
                filters=embedding.filters,
                kernel_size=embedding.kernel_size[0],
                buffer_bits=embedding.buffer_bitwidth + 1,
                output_bits=out_quantizer.bitwidth,
                num_non_patch_tokens=len(cls_layers),
                name=embedding.name)


def convert_quantized_stem_layers(model_ak, block):
    """Converts stem block layers and their variables and adds them to the
    Akida's model.

    Args:
        model_ak (:obj:`akida.Model`): the Akida model where the model will be added.
        block (list): the quantizeml quantized layers of the Stem to convert.

    Returns:
        bool: Returns True for a successful conversion.
    """
    # Parse the Stem block layers parameters
    stem_params = _parse_stem_block_layers(block)

    layer_ak = Stem(**stem_params)
    model_ak.add(layer_ak)
    _set_stem_variables(layer_ak, block)
    # Get out_quantizer of the block.
    out_quantizer = get_block_out_quantizer(block)
    set_output_v2_variables(layer_ak, out_quantizer)

    return True


class StemBlockConverter(BlockConverter):
    """Main class that should be used to check if the stem block is compatible to an Akida v2
    conversion and provides a method to convert it in an equivalent Akida stem layer.

    Args:
        block (list): list of quantizeml quantized layers.
    """

    def __init__(self, block):
        super().__init__(block)
        self._stem_additional_checks()

    def convert(self, model_ak):
        assert len(model_ak.layers) == 0, "Stem layer should be the first model layer."
        return convert_quantized_stem_layers(model_ak, self._block)

    def _stem_additional_checks(self):
        embedding = self._block[0]
        # Get embedding layer input shape without the batch size.
        input_shape = embedding.input_shape[1:]
        # Stem handles only square inputs
        if (input_shape[0] != input_shape[1]):
            raise ValueError("input should have square spatial dimensions. Receives: "
                             f"x_size={input_shape[0]} and y_size={input_shape[1]}")
        # Stem handles only image-like inputs (1-D or 3-D uint8 inputs)
        if input_shape[-1] not in (1, 3):
            raise ValueError("Stem layer can only handle image like inputs (i.e 3-D or 1-D input "
                             f"shape). Received: {embedding.input_shape[1:]}.")
        # Get the kernel size
        kernel_size = embedding.kernel_size
        # Stem handles only square kernels.
        if (kernel_size[0] != kernel_size[1]):
            raise ValueError("input should have square kernels. Receives: "
                             f"k_x={kernel_size[0]} and k_y={kernel_size[1]}")
        # Stem input size must be a multiple of kernel size.
        if (input_shape[0] % kernel_size[0] != 0):
            raise ValueError("Input spatial dimension size must be a multiple of kernel size")
        stride_x = embedding.strides[0]
        stride_y = embedding.strides[1]
        # Stem handles only same strides along its spatial dims
        if (stride_x != stride_y):
            raise ValueError("Input should have the same strides along its spatial dims. "
                             f"Receives: x_stride={stride_x} and y_stride={stride_y}")
        # Stem kernel size should be equal kernel stride.
        if (kernel_size[0] != stride_x):
            raise ValueError("Input kernel size should be equal kernel stride. "
                             f"Received: kernel_size={kernel_size[0]} and stride={stride_x}")


# Register the valid stem block pattern for Akida v2
register_conversion_patterns(AkidaVersion.v2, _PATTERNS, StemBlockConverter, input_pattern=True)
