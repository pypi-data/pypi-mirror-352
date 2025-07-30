from akida.core import (Layer, LayerParams, LayerType)


class MadNorm(Layer):
    """A function similar to the MAD normalization layer presented
    in quantizeml. (Note that the normalization is only available over
    the last dimension)

    Instead of using the standard deviation (std) during the normalization
    division, the sum of absolute values is used.
    The normalization is performed in this way:

        MadNorm(x) = x * gamma / sum(abs(x)) + beta

    Args:
        output_bits (int, optional): output bitwidth. Defaults to 8
        buffer_bits (int, optional): buffer bitwidth. Defaults to 32.
        post_op_buffer_bits (int, optional): internal bitwidth for post operations. Defaults to 32.
        name (str, optional): name of the layer. Defaults to empty string.

    """

    def __init__(self,
                 output_bits=8,
                 buffer_bits=32,
                 post_op_buffer_bits=32,
                 name=""):
        try:
            params = LayerParams(
                LayerType.MadNorm, {
                    "output_bits": output_bits,
                    "buffer_bits": buffer_bits,
                    "post_op_buffer_bits": post_op_buffer_bits,
                })
            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
