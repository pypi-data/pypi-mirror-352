from typing import Optional, Sequence, Union

import numpy as np

# @manual=//deeplearning/trt/python:py_tensorrt
import tensorrt as trt
import torch
from torch.fx.node import Target
from torch_tensorrt.dynamo.conversion import impl
from torch_tensorrt.dynamo.conversion._ConversionContext import ConversionContext
from torch_tensorrt.dynamo.conversion.converter_utils import (
    extend_attr_to_tuple,
    get_trt_tensor,
    to_numpy,
)
from torch_tensorrt.fx.converters.converter_utils import (
    SourceIR,
    get_dyn_range,
    has_dynamic_shape,
    mark_as_int8_layer,
    set_layer_name,
)
from torch_tensorrt.fx.types import TRTTensor


def deconvNd(
    ctx: ConversionContext,
    target: Union[Target, str],
    source_ir: Optional[SourceIR],
    name: str,
    is_deconv1d: bool,
    input: TRTTensor,
    weight: Union[TRTTensor, torch.Tensor, np.ndarray],
    bias: Optional[Union[TRTTensor, torch.Tensor, np.ndarray]],
    stride: Union[int, Sequence[int]],
    padding: Union[int, Sequence[int]],
    dilation: Union[int, Sequence[int]],
    groups: Optional[int],
    output_padding: Union[int, Sequence[int]] = 0,
    scale: Optional[Union[torch.Tensor, float]] = None,
    zero_point: Optional[Union[torch.Tensor, float]] = None,
) -> TRTTensor:
    if has_dynamic_shape(input.shape):
        assert input.shape[1] != -1, "Channel dim can't be dynamic for deconvolution."

    if is_deconv1d:
        # Apply an unsqueeze operation to transform the deconv1d problem into deconv2d
        input = impl.unsqueeze.unsqueeze(
            ctx, target, source_ir, name + "_unsqueeze_deconv1d", input, -1
        )

    # Process bias terms
    if isinstance(bias, (torch.Tensor, np.ndarray)):
        # Transform the bias constant into a Numpy array
        bias = to_numpy(bias)

    elif isinstance(bias, TRTTensor):
        bias = get_trt_tensor(ctx, bias, f"{name}_bias")

    elif bias is not None:
        raise RuntimeError(
            f"Deconvolution {name} has bias of type {type(bias)}, Expected Torch Tensor or TRT Tensor"
        )

    # Process weight terms
    if isinstance(weight, TRTTensor):
        weight = get_trt_tensor(ctx, weight, f"{name}_weight")
        # Append new dimension (unsqueeze) if the deconvolution is 1d
        if is_deconv1d:
            input = impl.unsqueeze.unsqueeze(
                ctx, target, source_ir, name + "_unsqueeze_weight", weight, -1
            )

    elif isinstance(weight, (torch.Tensor, np.ndarray)):
        # Transform the weight constant into a Numpy array
        weight = to_numpy(weight)

        # Append new dimension (unsqueeze) if the deconvolution is 1d
        if is_deconv1d:
            weight = np.expand_dims(weight, axis=-1)

    else:
        raise RuntimeError(
            f"Convolution {name} has weight of type {type(weight)}, Expect Optional[Tensor]"
        )

    # add deconv layer
    deconv_layer = ctx.net.add_deconvolution_nd(
        input=input,
        num_output_maps=weight.shape[1] * groups,
        kernel_shape=weight.shape[2:],
        kernel=trt.Weights() if isinstance(weight, TRTTensor) else weight,
        bias=trt.Weights() if isinstance(bias, TRTTensor) else bias,
    )

    # If the weight is a TRTTensor, set it as an input of the layer
    if isinstance(weight, TRTTensor):
        deconv_layer.set_input(1, weight)

    # If the bias is a TRTTensor, set it as an input of the layer
    if isinstance(bias, TRTTensor):
        deconv_layer.set_input(2, bias)

    # Cast certain fields to tuples, in accordance with TRT requirements
    padding = (padding,) if isinstance(padding, int) else padding
    stride = (stride,) if isinstance(stride, int) else stride
    dilation = (dilation,) if isinstance(dilation, int) else dilation

    # Expand parameters manually for Conv1D computations
    if is_deconv1d:
        padding = (tuple(padding) + (0,)) if padding is not None else padding
        stride = extend_attr_to_tuple(stride, 2) if stride is not None else stride
        dilation = (
            extend_attr_to_tuple(dilation, 2) if dilation is not None else dilation
        )

    set_layer_name(deconv_layer, target, name, source_ir)

    # Set relevant attributes of deconvolution layer
    if padding is not None:
        deconv_layer.padding_nd = padding
    if stride is not None:
        deconv_layer.stride_nd = stride
    if dilation is not None:
        deconv_layer.dilation_nd = dilation
    if groups is not None:
        deconv_layer.num_groups = groups

    # Handle quantization cases
    if scale is not None and zero_point is not None:
        # Assume the dtype of activation is torch.quint8
        mark_as_int8_layer(deconv_layer, get_dyn_range(scale, zero_point, torch.quint8))

    result = deconv_layer.get_output(0)

    if is_deconv1d:
        # Apply a squeeze operation to transform the deconv2d problem back into deconv1d
        result = impl.squeeze.squeeze(
            ctx, target, source_ir, name + "_squeeze_deconv1d", result, -1
        )

    return result
