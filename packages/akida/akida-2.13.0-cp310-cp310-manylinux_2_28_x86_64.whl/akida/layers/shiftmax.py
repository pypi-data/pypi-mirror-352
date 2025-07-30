from akida.core import (Layer, LayerParams, LayerType)


class Shiftmax(Layer):
    """A function similar to the softmax.

    Instead of using e as base, it uses 2 and a shift. So we replace

    .. math::
        softmax(x_i) = \\frac{e^{x_i}}{sum(e^{x_k})}

    with

    .. math::
        shiftmax(x_i) = \\frac{2^{x_i}}{round(log2(sum(2^{x_k})))}

    This is evaluated with a shift.

    Args:
        output_bits (int, optional): output bitwidth. Defaults to 8.
        buffer_bits (int, optional): internal bitwidth. Defaults to 32.
        post_op_buffer_bits (int, optional): internal bitwidth for post operations. Defaults to 32.
    """

    def __init__(self,
                 output_bits=8,
                 buffer_bits=32,
                 post_op_buffer_bits=32,
                 name=""):
        try:
            params = LayerParams(
                LayerType.Shiftmax, {
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
