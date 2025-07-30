#!/usr/bin/env python
# ******************************************************************************
# Copyright 2024 Brainchip Holdings Ltd.
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

""" Tools to convert a group of Akida layers in a model towards a VitEncoderBlock layer. """

__all__ = ["fold_vitencoderblock"]

import os
from tempfile import TemporaryDirectory
from akida import Model, LayerType, ActivationType, VitEncoderBlock


def _get_attention_layers(model):
    attentions = []
    for layer in model.layers:
        if layer.parameters.layer_type == LayerType.Attention:
            attentions.append(layer)
    return attentions


def _get_outbounds(target_layer, model):
    outbounds = []
    for layer in model.layers:
        if target_layer in layer.inbounds:
            outbounds.append(layer)
    return outbounds


def _validate_head_topology(block_output, model):
    # Validate optional topology: BN + ExtractToken(s) and Dense head(s)
    batch_norm = None
    extract_head, head = None, None
    extract_dist_head, dist_head, add_heads = None, None, None

    # block_output can be the inbound of batch_norm
    outbounds = _get_outbounds(block_output, model)
    if len(outbounds) == 1 and outbounds[0].parameters.layer_type == LayerType.BatchNormalization:
        batch_norm = outbounds[0]
        # batch_norm should have 1 or 2 ExtractToken outbounds
        outbounds = _get_outbounds(batch_norm, model)
        if (len(outbounds) in [1, 2]
                and all(bound.parameters.layer_type == LayerType.ExtractToken
                        for bound in outbounds)):
            if len(outbounds) == 1:
                extract_head = outbounds[0]
                # extract_head can be the inbound of a Dense2D head
                outbounds = _get_outbounds(extract_head, model)
                if len(outbounds) == 1 and outbounds[0].parameters.layer_type == LayerType.Dense1D:
                    head = outbounds[0]
            else:
                # Find which ExtractToken is the base head and which is the dist head
                if (outbounds[0].parameters.begin == 0 and outbounds[0].parameters.end == 1
                        and outbounds[1].parameters.begin == 1
                        and outbounds[1].parameters.end == 2):
                    extract_head = outbounds[0]
                    extract_dist_head = outbounds[1]
                elif (outbounds[1].parameters.begin == 0 and outbounds[1].parameters.end == 1
                        and outbounds[0].parameters.begin == 1
                        and outbounds[0].parameters.end == 2):
                    extract_head = outbounds[1]
                    extract_dist_head = outbounds[0]
                else:
                    # Invalidate batch_norm
                    batch_norm = None
                if extract_head is not None:
                    extract_head_outb = _get_outbounds(extract_head, model)
                    extract_dist_head_outb = _get_outbounds(extract_dist_head, model)
                    # Check for head and dist_head Dense2D
                    if (len(extract_head_outb) == 1
                            and extract_head_outb[0].parameters.layer_type == LayerType.Dense1D
                            and len(extract_dist_head_outb) == 1
                            and (extract_dist_head_outb[0].parameters.layer_type
                                 == LayerType.Dense1D)):
                        head = extract_head_outb[0]
                        dist_head = extract_dist_head_outb[0]
                        # Check for add_heads
                        head_outbounds = _get_outbounds(head, model)
                        dist_head_outbounds = _get_outbounds(dist_head, model)
                        if (len(head_outbounds) == 1 and len(dist_head_outbounds) == 1
                                and head_outbounds[0].parameters.layer_type == LayerType.Add
                                and head_outbounds[0] == dist_head_outbounds[0]):
                            add_heads = head_outbounds[0]
                        else:
                            # Invalidate both heads
                            head, dist_head = None, None
        else:
            # Invalidate batch_norm
            batch_norm = None
    return {'batch_norm': batch_norm,
            'extract_head': extract_head, 'head': head,
            'extract_dist_head': extract_dist_head, 'dist_head': dist_head, 'add_heads': add_heads}


def _validate_topology(attention, model):
    """ This checks that topology is aligned with a VitEncoderBlock.

    The attention inbounds and outbounds are parse and for each bound, the types and number of each
    inbound and outbound is check to match the expected.

    Args:
        attention (Layer): Attention layer to start from
        model (Model): reference model, used to retrieve layers outbounds

    Returns:
        bool or dict: False if no valid topology is found and a dict with VitEncoderBlock topology
            compliant layers
    """
    # 1. Check layers before attention
    # attention inbounds should be query, key and value Dense2D layers
    if (any([not inbound.parameters.layer_type == LayerType.Dense2D
            for inbound in attention.inbounds])):
        return False

    # query, key and value inbounds should have the same norm_mha MadNorm inbound and a single
    # outbound because only self-attention is handled for now
    query, key, value = attention.inbounds
    if (query.inbounds != key.inbounds != value.inbounds
            or not query.inbounds[0].parameters.layer_type == LayerType.MadNorm
            or not len(_get_outbounds(query, model)) == 1
            or not len(_get_outbounds(key, model)) == 1
            or not len(_get_outbounds(value, model)) == 1):
        return False
    norm_mha = query.inbounds[0]

    # norm_mha should have a single outbound
    if len(_get_outbounds(norm_mha, model)) != 3:
        return False
    block_inbound = norm_mha.inbounds[0]

    # 2. Check layers after attention
    # attention is the inbound of a Dense2D projection layer
    outbounds = _get_outbounds(attention, model)
    if len(outbounds) != 1 or not outbounds[0].parameters.layer_type == LayerType.Dense2D:
        return False
    attention_projection = outbounds[0]

    # attention_projection is the first inbound of the first Add layer.
    # The second inbound of Add is the norm_mha inbound otherwise known as the block input.
    # Note that the order of Add inbounds is also important and checked.
    outbounds = _get_outbounds(attention_projection, model)
    if (len(outbounds) != 1 or not outbounds[0].parameters.layer_type == LayerType.Add
            or attention_projection not in outbounds[0].inbounds
            or block_inbound not in outbounds[0].inbounds):
        return False
    skip_connection_1 = outbounds[0]

    # First skip connection is the inbound of both the second Add and of norm_mlp MadNorm layers
    outbounds = _get_outbounds(skip_connection_1, model)
    if (len(outbounds) != 2
            or not any(bound.parameters.layer_type == LayerType.Add for bound in outbounds)
            or not any(bound.parameters.layer_type == LayerType.MadNorm for bound in outbounds)):
        return False

    # skip_connection_2 is further validated later on
    norm_mlp = outbounds[0]
    skip_connection_2 = outbounds[1]
    if outbounds[0].parameters.layer_type == LayerType.Add:
        norm_mlp, skip_connection_2 = skip_connection_2, norm_mlp

    # norm_mlp is the inbound of Dense2D mlp_1
    outbounds = _get_outbounds(norm_mlp, model)
    if len(outbounds) != 1 or not outbounds[0].parameters.layer_type == LayerType.Dense2D:
        return False
    mlp_1 = outbounds[0]

    # mlp_1 is the inbound to Dense2D mlp_2
    outbounds = _get_outbounds(mlp_1, model)
    if len(outbounds) != 1 or not outbounds[0].parameters.layer_type == LayerType.Dense2D:
        return False
    mlp_2 = outbounds[0]

    # mlp_2 is the inbound to skip_connection_2
    outbounds = _get_outbounds(mlp_2, model)
    if len(outbounds) != 1 or outbounds[0] != skip_connection_2:
        return False

    # Further checks on skip_connection_2
    if (skip_connection_1 not in skip_connection_2.inbounds
            or mlp_2 not in skip_connection_2.inbounds):
        return False

    # Topology is validated, build a candidate
    candidate = {'block_inbound': block_inbound,
                 'norm_mha': norm_mha,
                 'query': query, 'key': key, 'value': value,
                 'attention': attention, 'attention_projection': attention_projection,
                 'skip_connection_1': skip_connection_1,
                 'norm_mlp': norm_mlp, 'mlp_1': mlp_1, 'mlp_2': mlp_2,
                 'skip_connection_2': skip_connection_2}

    # 3. Check for optional head layers
    candidate.update(_validate_head_topology(skip_connection_2, model))
    return candidate


def _validate_candidate(candidate):
    # Consider the candidate valid and invalidate as the checks progress
    ret = True

    # Expected values in the block
    hidden_size = 192
    num_heads = 3
    mlp_1_units = 768
    head_bits = 28

    # Initialize other parameters with norm_mha value, later on the checks will ensure a single
    # value throughout the block
    norm_mha = candidate['norm_mha']
    post_op_buffer_bits = norm_mha.parameters.post_op_buffer_bits
    output_bits = norm_mha.parameters.output_bits

    def _check_out_params(layer, dense=False):
        # All output_bits and post_op_buffer_bits should be the same in a block
        return (layer.parameters.output_bits == output_bits
                and layer.parameters.post_op_buffer_bits == post_op_buffer_bits)

    def _check_norm(layer):
        return (layer.input_dims[0] == 1
                and layer.input_dims[2] == hidden_size
                and _check_out_params(layer))

    def _check_dense(layer, units=hidden_size, activation=ActivationType.NoActivation):
        return (layer.parameters.units == units and
                layer.parameters.activation == activation.value and
                _check_out_params(layer))

    # Check block input shape: must be (1, num_non_patch_token + num_token, hidden_size)
    ret &= _check_norm(norm_mha)

    # Check Query, Key, Value: units must be hidden_size
    ret &= _check_dense(candidate['query'])
    ret &= _check_dense(candidate['key'])
    ret &= _check_dense(candidate['value'])

    # Attention
    ret &= candidate['attention'].parameters.num_heads == num_heads
    ret &= _check_out_params(candidate['attention'])

    # Attention projection
    ret &= _check_dense(candidate['attention_projection'])

    # First skip connection
    ret &= _check_out_params(candidate['skip_connection_2'])

    # NormMLP
    ret &= _check_norm(candidate['norm_mlp'])

    # MLP
    ret &= _check_dense(candidate['mlp_1'], units=mlp_1_units, activation=ActivationType.ReLU)
    ret &= _check_dense(candidate['mlp_2'])

    # Second skip connection
    ret &= _check_out_params(candidate['skip_connection_2'])

    # Head
    bn = candidate['batch_norm']
    if bn is not None:
        ret &= (bn.parameters.activation == ActivationType.NoActivation.value and
                _check_out_params(bn))

    head = candidate['head']
    if head is not None:
        ret &= head.parameters.activation == ActivationType.NoActivation.value

        dist_head = candidate['dist_head']
        if dist_head is None:
            ret &= (head.parameters.buffer_bits == head_bits
                    and head.parameters.output_bits == head_bits)
        else:
            ret &= (head.parameters.buffer_bits == head_bits
                    and head.parameters.output_bits == output_bits)
            ret &= (dist_head.parameters.activation == ActivationType.NoActivation.value
                    and dist_head.parameters.buffer_bits == head_bits
                    and dist_head.parameters.output_bits == output_bits)
    return ret


def _set_block_variables(block, candidate):
    for key, ly in candidate.items():
        # Skip 'block_inbound' as it is only here for topology purpose and layers that were not set
        # (optional head layers)
        if key == 'block_inbound' or ly is None:
            continue
        for var in ly.variables.names:
            # 'key' is matching the block 'prefix' for block variables names
            block.set_variable(key + "_" + var, ly.variables[var])

    def _check_and_invert(skip_name, expected):
        if candidate[skip_name].inbounds != expected:
            a_shift = block.get_variable(skip_name + '_a_shift')
            b_shift = block.get_variable(skip_name + '_b_shift')
            block.set_variable(skip_name + '_a_shift', b_shift)
            block.set_variable(skip_name + '_b_shift', a_shift)

    # Skip connection inputs order matters when it comes to variables and because VitEncoderBlock
    # always assumes a specific order for skip connections, it must be checked here
    _check_and_invert('skip_connection_1',
                      [candidate['attention_projection'], candidate['block_inbound']])
    _check_and_invert('skip_connection_2', [candidate['skip_connection_1'], candidate['mlp_2']])
    if candidate['add_heads'] is not None:
        _check_and_invert('add_heads', [candidate['head'], candidate['dist_head']])


def fold_vitencoderblock(original_model):
    """ Look for Attention layer and try to rebuild a VitEncoderBlock by parsing the topology,
    shapes and parameters.

    Layers that can be replaced by a VitEncoderBlock are:

        - MADNorm MHA
        - Query, Key, Value
        - Attention
        - Attention projection
        - First skip connection (input and attention projection addition)
        - MADNorm MLP
        - MLP1 + ReLU
        - MLP2
        - Second skip connection (first skip connection and MLP2 addition)
        - Optional BatchNormalization + ExtractToken
        - Optional Dense heads

    Args:
        original_model (Model): the model to check

    Returns:
        Model: the model with VitEncoderBlock layers when possible, the original model otherwise
    """
    # As there is no API to deep copy layers or model, the original model is duplicated by saving
    # it temporarily, which allows to preserve it and work on the duplicate
    with TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, 'tmp_model.fbz')
        original_model.save(path)
        model = Model(path)

    # Attention is the characteristic component of a VitEncoderBlock, then retrieve them first
    attentions = _get_attention_layers(model)
    if len(attentions) == 0:
        return original_model

    vit_block_candidates = {}
    for attention in attentions:
        # Parse the model topology around the attention layer and try matching with the expected
        candidate = _validate_topology(attention, model)
        # Check candidate shapes and parameters
        if candidate and _validate_candidate(candidate):
            # Build the target block
            tokens_to_extract = 0
            if candidate['extract_head'] is not None:
                tokens_to_extract += (candidate['extract_head'].parameters.end -
                                      candidate['extract_head'].parameters.begin)
                if candidate['extract_dist_head'] is not None:
                    tokens_to_extract += (candidate['extract_dist_head'].parameters.end -
                                          candidate['extract_dist_head'].parameters.begin)

            block = VitEncoderBlock(
                hidden_size=candidate['norm_mha'].input_dims[-1],
                mlp_dim=candidate['mlp_1'].parameters.units,
                num_heads=candidate['attention'].parameters.num_heads,
                num_classes=0 if candidate['head'] is None else candidate['head'].parameters.units,
                tokens_to_extract=tokens_to_extract,
                output_bits=candidate['norm_mha'].parameters.output_bits,
                buffer_bits=candidate['norm_mha'].parameters.buffer_bits,
                post_op_buffer_bits=candidate['norm_mha'].parameters.post_op_buffer_bits)
            vit_block_candidates[block] = candidate

    if len(vit_block_candidates) == 0:
        return original_model

    # Get the model layers list and replace the candidate ones with the block
    all_layers = model.layers
    for block, candidate in vit_block_candidates.items():
        # Insert the block before the first layer of the candidate layers
        all_layers.insert(all_layers.index(candidate['norm_mha']), block)
        # Pop 'block_inbound' from candidate to prevent filtering it
        candidate_copy = candidate.copy()
        del candidate_copy['block_inbound']
        # Remove the candidate layers from all_layers
        all_layers = [c for c in all_layers if c not in candidate_copy.values()]

    # Rebuild a model: layers must be added one by one to ensure they are all properly build
    block_model = Model()
    for ly in all_layers:
        inbounds = []
        # If the layer was in the model, retrieve and set same inbounds
        if ly in model.layers:
            # Get inbounds from the original model
            original_inbounds = model.get_layer(ly.name).inbounds
            for bound in original_inbounds:
                if bound in block_model.layers:
                    # Add the layer if it's in block_model
                    inbounds.append(bound)
                else:
                    # If the layer is not in block_model then it's one of the new
                    # VitEncoderBlock layers
                    for block, candidate in vit_block_candidates.items():
                        if bound in candidate.values():
                            inbounds.append(block)
                            break
        block_model.add(ly, inbound_layers=inbounds)

        # Set back variables using original_model value since the previous call to 'add' would reset
        # them
        try:
            original_layer = original_model.get_layer(ly.name)
            for var in ly.variables.names:
                ly.set_variable(var, original_layer.variables[var])
        except Exception:
            pass

    # Finally, set block variables
    for block, candidate in vit_block_candidates.items():
        _set_block_variables(block, candidate)
    return block_model
