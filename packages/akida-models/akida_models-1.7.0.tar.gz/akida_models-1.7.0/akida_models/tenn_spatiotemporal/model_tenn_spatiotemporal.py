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
TENN spatiotemporal architecture definition.
"""

__all__ = ['tenn_spatiotemporal_dvs128', 'tenn_spatiotemporal_dvs128_pretrained',
           'tenn_spatiotemporal_eye',  'tenn_spatiotemporal_eye_pretrained',
           'tenn_spatiotemporal_jester', 'tenn_spatiotemporal_jester_pretrained']

from keras.models import Model
from keras.layers import Input, AveragePooling3D, Dense, ReLU, Rescaling

from ..utils import fetch_file
from ..model_io import load_model, get_model_path
from ..layer_blocks import spatiotemporal_block, conv3d_block


def tenn_spatiotemporal_dvs128(input_length=15, input_shape=(128, 128, 2), num_classes=10):
    """ Instantiates a TENN spatiotemporal DVS128 architecture.

    Args:
        input_length (int, optional): the input length. Defaults to 15.
        input_shape (tuple, optional): the input shape. Defaults to (128, 128, 2).
        num_classes (int, optional): number of classes. Defaults to 10.

    Returns:
        keras.Model: a TENN spatiotemporal model for DVS128
    """
    # architecture parameters
    channels = [8, 8, 16, 32, 48, 64, 80, 96, 112, 128, 256]
    t_dws = [False, False, True, True, True]
    s_dws = [False, False, True, True, True]
    t_kernel_size = 5

    input_shape = (input_length,) + input_shape
    inputs = Input(shape=input_shape, name='input')

    x = conv3d_block(inputs, channels[0], (1, 3, 3), add_batchnorm=True,
                     relu_activation='ReLU', name="input_conv", strides=(1, 2, 2),
                     use_bias=False, padding='same')

    for index, (i_chan, m_chan, o_chan, temp_dw, spa_dw) in \
            enumerate(zip(channels[0::2], channels[1::2], channels[2::2], t_dws, s_dws)):
        x = spatiotemporal_block(x, i_chan, m_chan, o_chan, t_kernel_size, temp_dw, spa_dw, index)

    # apply GAP over the spatial dimensions but not the temporal dimension
    x = AveragePooling3D(pool_size=(1, x.shape[2], x.shape[3]), name='gap')(x)
    x = Dense(256)(x)
    x = ReLU()(x)
    x = Dense(num_classes)(x)

    return Model(inputs, x, name="pleiades_st_dvs128")


def tenn_spatiotemporal_dvs128_pretrained(quantized=True):
    """
    Helper method to retrieve a `tenn_spatiotemporal_dvs128` model that was trained on DVS128
    dataset.

    Args:
        quantized (bool, optional): a boolean indicating whether the model should be loaded
            quantized or not. Defaults to True.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if quantized:
        model_name_v2 = 'tenn_spatiotemporal_dvs128_buffer_i8_w8_a8.h5'
        file_hash_v2 = '2c117af91de8b1eee65cd521cb6255d247c2786b0f7514fd963fee9ceb34bc31'
    else:
        model_name_v2 = 'tenn_spatiotemporal_dvs128_buffer.h5'
        file_hash_v2 = '2dfd9f50d953eb560dea3b60546abb9102b6ff49c521138358a6297764ecb1c8'

    model_path, model_name, file_hash = get_model_path(
        "tenn_spatiotemporal", model_name_v2=model_name_v2, file_hash_v2=file_hash_v2)
    model_path = fetch_file(model_path, fname=model_name, file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)


def tenn_spatiotemporal_eye(input_length=50, input_shape=(80, 106, 2), input_scaling=(127, 0),
                            reg_factor=None):
    """ Instantiates a TENN spatiotemporal Eye Tracking architecture.

    Args:
        input_length (int, optional): the input length. Defaults to 50.
        input_shape (tuple, optional): the input shape. Defaults to (80, 106, 2).
        input_scaling (None or tuple, optional): scale factor set to the max value of a 8-bits
            unsigned inputs and offset set to 0. Note that following Akida convention, the scale
            factor is a number used as a divisor. If None, no Rescaling layer is added.
            Defaults to (255, 0).
        reg_factor (float, optional): the L1-regularization factor of the ActivityRegularization
            layers that are added after the ReLU layers if reg_factor is not None.
            Defaults to None.

    Returns:
        keras.Model: a TENN spatiotemporal model for Eye Tracking.
    """
    # architecture parameters
    channels = [8, 16, 32, 48, 64, 80, 96, 112, 128, 256]
    t_dws = [False, False, False, True, True]
    s_dws = [False, False, False, True, True]
    t_kernel_size = 5

    in_channels = input_shape[-1]
    channels = [in_channels] + channels

    input_shape = (input_length,) + input_shape
    inputs = Input(shape=input_shape, name='input')
    if input_scaling:
        scale, offset = input_scaling
        x = Rescaling(1. / scale, offset, name="rescaling")(inputs)
    else:
        x = inputs

    for index, (i_chan, m_chan, o_chan, temp_dw, spa_dw) in \
            enumerate(zip(channels[0::2], channels[1::2], channels[2::2], t_dws, s_dws)):
        x = spatiotemporal_block(x, i_chan, m_chan, o_chan, t_kernel_size, temp_dw,
                                 spa_dw, index, reg_factor)

    # Head convolutions
    x = conv3d_block(
        x, channels[-1],
        (t_kernel_size, 1, 1),
        add_batchnorm=True, relu_activation='ReLU', strides=(1, 1, 1),
        padding='same', groups=channels[-1],
        use_bias=False, name=f'HEAD_convt_dw_{index}', reg_factor=reg_factor)
    x = conv3d_block(x, channels[-1], (1, 1, 1), add_batchnorm=True,
                     relu_activation='ReLU', use_bias=False, name=f'HEAD_convt_pw_{index}',
                     reg_factor=reg_factor)

    x = conv3d_block(x, channels[-1], (1, 3, 3), groups=channels[-1], strides=(1, 1, 1),
                     padding='same', use_bias=False, add_batchnorm=False, relu_activation='ReLU',
                     name=f'HEAD_convs_dw_{index}', reg_factor=reg_factor)
    x = conv3d_block(x, 3, (1, 1, 1), strides=(1, 1, 1), use_bias=False,
                     add_batchnorm=False, relu_activation=False, name=f'HEAD_convs_pw_{index}',
                     reg_factor=reg_factor)

    return Model(inputs, x, name="AIS2024_eyetracking")


def tenn_spatiotemporal_eye_pretrained(quantized=True):
    """
    Helper method to retrieve a `tenn_spatiotemporal_eye` model that was trained on Event-based Eye
    Tracking AI for Streaming CVPR 2024 Challenge dataset.

    Args:
        quantized (bool, optional): a boolean indicating whether the model should be loaded
            quantized or not. Defaults to True.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if quantized:
        model_name_v2 = 'tenn_spatiotemporal_eye_buffer_i8_w8_a8.h5'
        file_hash_v2 = '7b9c4bb8ce66d0e2bc1ca5d7e7c4a93ff38c42678e0781c17dcd05e18580ff85'
    else:
        model_name_v2 = 'tenn_spatiotemporal_eye_buffer.h5'
        file_hash_v2 = '60a00c37a59b9787d0c19dc71e1018a435983623769cc62f69f65f244204411e'

    model_path, model_name, file_hash = get_model_path(
        "tenn_spatiotemporal", model_name_v2=model_name_v2, file_hash_v2=file_hash_v2)
    model_path = fetch_file(model_path, fname=model_name, file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)


def tenn_spatiotemporal_jester(input_shape=(16, 100, 100, 3), input_scaling=(127.5, -1.0),
                               n_classes=27):
    """ Instantiates a TENN spatiotemporal Jester architecture.

    Args:
        input_shape (tuple, optional): the input shape. Defaults to (16, 100, 100, 3).
        input_scaling (None or tuple, optional): scale factor set to the max value of a 8-bits
            unsigned inputs and offset set to 0. Note that following Akida convention, the scale
            factor is a number used as a divisor. If None, no Rescaling layer is added.
            Defaults to (127.5, -1.0).
        n_classes (int, optional): number of output features. Defaults to 27.

    Returns:
        keras.Model: a spatiotemporal model relying on TENNS convolutions.
    """
    # architecture parameters
    channels = [8, 20, 40, 80, 120, 160, 200, 240, 280, 320, 640]
    t_dws = [False, False, False, True, True]
    s_dws = [False, False, False, True, True]
    t_kernel_size = 5

    inputs = Input(shape=input_shape, name='input')
    if input_scaling:
        scale, offset = input_scaling
        x = Rescaling(1. / scale, offset, name="rescaling")(inputs)
    else:
        x = inputs

    x = conv3d_block(inputs, channels[0], (1, 3, 3), add_batchnorm=True,
                     relu_activation='ReLU', name="input_conv", strides=(1, 2, 2),
                     use_bias=False, padding='same', reg_factor=1e-8, normalize_reg=True)

    for layer_index, (i_chan, m_chan, o_chan, temp_dw, spa_dw) in \
            enumerate(zip(channels[0::2], channels[1::2], channels[2::2], t_dws, s_dws)):
        index = f"{layer_index}_0"
        x = spatiotemporal_block(x, i_chan, m_chan, o_chan, t_kernel_size, temp_dw, spa_dw, index,
                                 reg_factor=1e-8, normalize_reg=True)

    # apply GAP over the spatial dimensions but not the temporal dimension
    x = AveragePooling3D(pool_size=(1, x.shape[2], x.shape[3]), name='gap')(x)
    x = Dense(channels[-1])(x)
    x = ReLU()(x)
    x = Dense(n_classes)(x)

    return Model(inputs, x, name="jester_video")


def tenn_spatiotemporal_jester_pretrained(quantized=True):
    """
    Helper method to retrieve a `tenn_spatiotemporal_jester` model that was trained on Jester
    dataset.

    Args:
        quantized (bool, optional): a boolean indicating whether the model should be loaded
            quantized or not. Defaults to True.

    Returns:
        keras.Model: a Keras Model instance.

    """
    if quantized:
        model_name_v2 = 'tenn_spatiotemporal_jester_buffer_i8_w8_a8.h5'
        file_hash_v2 = 'b42a446d5527e2971ff4ba613a2dac2565b1aa98d0df9f2fedb7d9f4b058cf40'
    else:
        model_name_v2 = 'tenn_spatiotemporal_jester_buffer.h5'
        file_hash_v2 = '586fc778bdc40975cb4e9e61e1d15056cbbc65fb1e0ecb23da3cfa1007a072dc'

    model_path, model_name, file_hash = get_model_path(
        "tenn_spatiotemporal", model_name_v2=model_name_v2, file_hash_v2=file_hash_v2)
    model_path = fetch_file(model_path, fname=model_name, file_hash=file_hash,
                            cache_subdir='models')
    return load_model(model_path)
