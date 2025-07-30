from akida.core import (Layer, LayerParams, LayerType)


class Stem(Layer):
    """Stem layer corresponding to the Stem block of Transformer models.

    It's composed of the following layers:

        - The Embedding layer
        - The Reshape layer
        - The ClassToken (+ DistToken for distilled model) layer(s)
        - The AddPosEmbedding layer

    This layer covers all the above layers operations.

    Note that final output values will be saturated on the range that can
    be represented with output_bits.

    Args:
        input_shape (tuple): the spatially square 3D input shape.
        filters (int, optional): Positive integer, dimensionality of the output space.
            Defaults to 192.
        kernel_size (int, optional): kernel size. Defaults to 16.
        output_bits (int, optional): output bitwidth. Defaults to 8.
        buffer_bits (int, optional): buffer bitwidth. Defaults to 32.
        post_op_buffer_bits (int, optional): internal bitwidth for post operations. Defaults to 32.
        num_non_patch_tokens (int, optional): number of non patch tokens to concatenate
            with the input along it last axis. Defaults to 0.
        name (str, optional): name of the layer. Defaults to empty string.

    """

    def __init__(self,
                 input_shape,
                 filters=192,
                 kernel_size=16,
                 output_bits=8,
                 buffer_bits=28,
                 post_op_buffer_bits=32,
                 num_non_patch_tokens=0,
                 name=""):
        try:
            params = LayerParams(
                LayerType.Stem, {
                    "input_spatial_size": input_shape[0],
                    "input_channels": input_shape[2],
                    "filters": filters,
                    "kernel_size": kernel_size,
                    "output_bits": output_bits,
                    "buffer_bits": buffer_bits,
                    "post_op_buffer_bits": post_op_buffer_bits,
                    "num_non_patch_tokens": num_non_patch_tokens
                })
            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
