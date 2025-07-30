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
"""
TENN spatiotemporal model conversion from Conv3D to buffer mode.
"""

__all__ = ['convert_to_buffer']

import numpy as np
import tensorflow as tf

from copy import deepcopy
from keras import layers, Sequential
from keras.utils import custom_object_scope
from keras.saving import serialize_keras_object

from quantizeml.models.utils import apply_weights_to_model
from quantizeml.models.transforms.transforms_utils import (get_layers_by_type, get_layer_index,
                                                           update_inbound, get_layers)
from quantizeml.layers import BufferTempConv, DepthwiseBufferTempConv, reset_buffers

from ..layer_blocks import PleiadesLayer


def _drop_input_first_dim(model, config):
    """ Drops input first dimension.

    Args:
        model (keras.Model): original model
        config (dict): model config being updated
    """
    input = get_layers_by_type(model, layers.InputLayer)
    if len(input) != 1:
        raise RuntimeError(f'Detected {len(input)} InputLayer layers while expecting 1.')
    input_index = get_layer_index(config['layers'], input[0].name)
    input_config = config['layers'][input_index]
    shape = input_config['config']['batch_input_shape']
    input_config['config']['batch_input_shape'] = (shape[0], *shape[2:])


def _remove_zeropad3d_actregul(model, config):
    """ Remove ZeroPadding3D and ActivityRegularization layers.

    Args:
        model (keras.Model): original model
        config (dict): model config being updated
    """
    model_layers = config['layers']

    # Retrieve ZeroPadding3D and ActivityRegularization layers.
    removables = get_layers_by_type(model, (layers.ZeroPadding3D, layers.ActivityRegularization))
    if len(removables) == 0:
        return

    # For Sequential models, the changes stop here: the ZeroPad3D and ActivityRegularization
    # layers will simply be removed in the following step.
    # For other models, the layers inbounds/outbounds must be rebuilt.
    if not isinstance(model, Sequential):
        for zero_pad3d in removables:
            # Retrieve the ZeroPad3d inbound_nodes. (Assuming it has only one inbound layer).
            zp_index = get_layer_index(model_layers, zero_pad3d.name)
            # tfmot code: 'inbound_nodes' is a nested list where first element is the inbound
            # layername, e.g: [[['conv1', 0, 0, {} ]]]
            updated_inbound = model_layers[zp_index]['inbound_nodes'][0][0][0]

            # Get the layers after ZeroPad3D, ie. outbounds layers
            zp_outbound_names = [outbound.layer.name for outbound in zero_pad3d.outbound_nodes]
            outbound_ids = [get_layer_index(model_layers, zp_outbound)
                            for zp_outbound in zp_outbound_names]

            # Update ZeroPad3D outbounds layers inputs: their current inbound is the current
            # ZeroPad3D layer that will be removed. So in order to not break the graph connexions,
            # their initial inbound (aka the ZeroPad3D) must be replaced with the ZeroPad3D
            # inbound. This will results in: inbound > ZeroPad3D > outbounds
            # becomes inbound > outbounds.
            for i in outbound_ids:
                update_inbound(model_layers[i], zero_pad3d.name, updated_inbound)

    # Remove ZeroPad3D layers from the config now
    layers_to_remove = get_layers(config, [zp.name for zp in removables])
    for l_zp in layers_to_remove:
        model_layers.remove(l_zp)


def _replace_conv3d(model, config):
    """ Replace Conv3D layers with the appropriate BufferTempConv or Conv2D layer

    Args:
        model (keras.Model): original model
        config (dict): model config being updated
    """
    # Retrieve Conv3D layers
    conv3ds = get_layers_by_type(model, layers.Conv3D)
    if len(conv3ds) == 0:
        raise RuntimeError('Attempting to bufferize a model but no Conv3D layers found.')

    for conv3d in conv3ds:
        conv_index = get_layer_index(config['layers'], conv3d.name)
        conv_config = config['layers'][conv_index]

        # Retrieve convolution parameters that will require an update
        kernel_size = conv_config['config']['kernel_size']
        strides = conv_config['config']['strides']
        dilation_rate = conv_config['config']['dilation_rate']

        # Spatial Conv3D are replaced with Conv2D, those are convolution where first kernel
        # dimension is 1.
        if kernel_size[0] == 1:
            # Set useful param alias
            conv_input_channel = conv3d.input_shape[-1]
            conv_groups = conv_config['config']['groups']
            conv_filters = conv_config['config']['filters']
            # Set common params between depth and full conv layers
            conv_config['config']['kernel_size'] = kernel_size[1:]
            conv_config['config']['strides'] = strides[1:]
            conv_config['config']['dilation_rate'] = dilation_rate[1:]
            # If in_channel==groups==filters the layer behaves as a DepthwiseConv2D
            if conv_input_channel == conv_groups and conv_groups == conv_filters:
                target_class = layers.DepthwiseConv2D
                for param in ['kernel_regularizer', 'kernel_initializer', 'kernel_constraint']:
                    conv_config['config'][param.replace(
                        'kernel', 'depthwise')] = conv_config['config'].pop(param)
                for param in ['filters', "groups"]:
                    conv_config['config'].pop(param)
            # We do support Conv layer with groups==1 only
            elif conv_groups == 1:
                target_class = layers.Conv2D
            else:
                raise RuntimeError("We don't support Conv2D layers with groups!=1 for quantization."
                                   f" Receives the layer {conv3d.name} with groups={conv_groups}")
        else:
            # When first kernel dimension is not 1, the convolution is a temporal one and is thus
            # converted to a BufferTempConv
            conv_config['config']['trainable'] = False
            conv_config['config']['kernel_size'] = kernel_size[0]

            if conv_config['config']['groups'] == 1:
                target_class = BufferTempConv
            else:
                conv_config['config'].pop('filters')
                target_class = DepthwiseBufferTempConv

            # Drop parameters that are not required
            for param in ['padding', 'strides', 'kernel_initializer', 'bias_initializer',
                          'kernel_regularizer', 'bias_regularizer', 'activity_regularizer',
                          'kernel_constraint', 'bias_constraint', 'activation', 'groups',
                          'dilation_rate', 'data_format']:
                conv_config['config'].pop(param)

        new_config = target_class.from_config(conv_config['config'])
        conv_config.update(serialize_keras_object(new_config))


def _update_bn_axis(model, config):
    """ Update BatchNormalization axis.

    BatchNormalization axis set to -1 at layer creation will be saved as the actual positive
    dimension in the configuration (e.g -1 saved to 4). As the temporal dimension is removed, axis
    must be updated.

    Args:
        model (keras.Model): original model
        config (dict): model config being updated
    """
    # Retrieve BatchNormalization layers
    bns = get_layers_by_type(model, layers.BatchNormalization)

    for bn in bns:
        bn_index = get_layer_index(config['layers'], bn.name)
        bn_config = config['layers'][bn_index]
        axis = bn_config['config']['axis']
        axis = [dim - 1 for dim in axis]
        bn_config['config']['axis'] = axis


def _ap3_to_gap(model, config):
    """ Replace AveragePooling3D with GlobalAveragePooling2D.

    Args:
        model (keras.Model): original model
        config (dict): model config being updated
    """
    # Retrieve AP3 layer and config
    ap3 = get_layers_by_type(model, layers.AveragePooling3D)
    if len(ap3) == 0:
        return
    elif len(ap3) != 1:
        raise RuntimeError(f'Detected {len(ap3)} AveragePooling3D layers while expecting 1.')
    gap = ap3[0]
    if gap.padding != "valid":
        raise ValueError(f"To convert to GAP, padding should be valid. Receives layer {gap.name}"
                         f" with padding {gap.padding}")
    if gap.pool_size != gap.strides:
        raise ValueError("To convert to GAP, strides should equal pool_size. Receives layer "
                         f"{gap.name} with strides=={gap.strides} and pool_size=={gap.pool_size}")
    ap3_index = get_layer_index(config['layers'], gap.name)
    ap3_config = config['layers'][ap3_index]

    # Drop parameters that are not required
    for param in ['pool_size', 'padding', 'strides']:
        ap3_config['config'].pop(param)

    # Update layer type
    new_config = layers.GlobalAveragePooling2D.from_config(ap3_config['config'])
    ap3_config.update(serialize_keras_object(new_config))


def _set_weights(weights, dst_model):
    """ Set the given weights in the bufferized model, adapting Conv3D weights to Conv2D or
    BufferTempConv when required.

    Args:
        weights (np.array): original weights
        dst_model (keras.Model): bufferized model to set weights into
    """
    for i, w in enumerate(weights):
        # Update Conv3D weights (ndims > 3) to Conv2D or BufferTempConv weights dimensions
        if w.ndim > 3:
            # Spatial kernels: (T=1, H, W, C, F) -> (H, W, C, F)
            if w.shape[0] == 1:
                axis = 0
                if w.shape[3] == 1:
                    # Depthwise spatial kernels: ((T=1, H, W, C=1, F)) -> (H, W, F, 1)
                    w = np.transpose(w, axes=[0, 1, 2, 4, 3])
                w = np.squeeze(w, axis=axis)
            elif w.shape[3] == 1:
                # Depthwise temporal kernels: (T, H=1, W=1, C=1, F) -> (T, F)
                axis = (1, 2, 3)
                w = np.squeeze(w, axis=axis)
            else:
                # Transpose standard kernels: (T, H, W, C, F) -> (H, W, T, C, F)
                w = np.transpose(w, axes=[1, 2, 0, 3, 4])
                # merge axis 2 and 3: (H, W, T, C, F) -> (H=1, W=1, T * C, F)
                w = np.reshape(w, (*w.shape[:2], -1, w.shape[-1]))
            weights[i] = w
    dst_model.set_weights(weights)


def _replace_pleiades(model, config):
    """Replace Pleiades layers in a given model with Conv3D layers.

    Args:
        model: The input Keras model containing Pleiades layers.
        config: A dictionary containing the model configuration.

    Returns:
        A new model with Pleiades layers replaced by Conv3D layers.

    """
    pleiades_layers = get_layers_by_type(model, PleiadesLayer)
    if len(pleiades_layers) == 0:
        return model

    weights = {var.name: var for var in model.variables}

    for layer in pleiades_layers:
        index = get_layer_index(config['layers'], layer.name)
        conv_config = config['layers'][index]

        # Compute the transformed weight using the Pleiades transformation matrix
        new_weight = tf.tensordot(layer.kernel, layer.transform, axes=[[4], [0]])
        new_weight = tf.transpose(new_weight, perm=[4, 2, 3, 0, 1])
        # Replace the original layer weights with the transformed weights
        weights[layer.kernel.name] = new_weight

        # Create a new Conv3D layer from the updated configuration
        conv_config['config']['kernel_size'] = tuple(new_weight.shape[:3])
        # Remove unused Pleiades-specific parameters
        for param in ['degrees', 'alpha', 'beta']:
            conv_config['config'].pop(param)
        new_config = layers.Conv3D.from_config(conv_config['config'])
        conv_config.update(serialize_keras_object(new_config))

    new_model = model.from_config(config)

    apply_weights_to_model(new_model, weights)

    return new_model


def convert_to_buffer(model):
    """ Converts the given spatiotemporal Conv3D based model to its bufferized version.

    Args:
        model (keras.Model): the source model

    Returns:
        keras.Model: bufferized model
    """
    # Copy configuration before applying modifications
    config = deepcopy(model.get_config())

    # Replace the Pleiades layers with Conv3D layers with the appropriate kernel
    model = _replace_pleiades(model, config)

    # Drop input shape first dimension, data will be streamed to the model
    _drop_input_first_dim(model, config)

    # Remove ZeroPadding3D and ActivityRegularization layers
    _remove_zeropad3d_actregul(model, config)

    # Replace Conv3D layers with the appropriate BufferTempConv or Conv2D layer
    _replace_conv3d(model, config)

    # Update BatchNormalization axis
    _update_bn_axis(model, config)

    # Replace AveragePooling3D with GlobalAveragePooling2D
    _ap3_to_gap(model, config)

    # Since layers were replaced, the built shapes are dropped to allow for a clean rebuild
    for layer_config in config["layers"]:
        layer_config.pop('build_config', None)

    # Reconstruct model from the config, using the cloned layers
    with custom_object_scope({'BufferTempConv': BufferTempConv,
                              'DepthwiseBufferTempConv': DepthwiseBufferTempConv}):
        buffer_model = model.from_config(config)

    # Restore model weights
    _set_weights(model.get_weights(), buffer_model)

    # Reset the model
    reset_buffers(buffer_model)
    return buffer_model
