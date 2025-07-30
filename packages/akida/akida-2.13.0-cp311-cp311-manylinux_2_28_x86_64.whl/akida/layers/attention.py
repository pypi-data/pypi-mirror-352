from akida.core import (Layer, LayerParams, LayerType)


class Attention(Layer):
    """Multi-head attention layer.

    From A. Vaswani et al., "Attention is All You Need" (arXiv:1706.03762):
    "Self-attention, sometimes called intra-attention is an attention mechanism
    relating different positions of a single sequence in order to compute a
    representation of the sequence."

    This layer will take three inputs, Query, Key and Value, and perform these
    actions on each head:

    * Multiply Query and Key to obtain a vector of attention scores expressing
      how tokens/patches relate to one another.
    * Divide by a scale factor.
    * Convert the score to a probability mask using a Softmax function
      (replaced by a Shiftmax in our implementation).
    * Multiply the mask by the Values.

    Note that outputs and masks will be saturated on the range that can be
    represented with output_bits.

    Args:
        num_heads (int): number of heads.
        output_bits (int, optional): output bitwidth. Defaults to 8
        buffer_bits (int, optional): internal bitwidth. Defaults to 32
        post_op_buffer_bits (int, optional): internal bitwidth for post operations. Defaults to 32.
        shiftmax_output_bits (int, optional): output bitwidth for shiftmax,
            must be no more than 1/2 of buffer_bits. Defaults to 10
        name (str, optional): name of the layer. Defaults to empty string

    """

    def __init__(self,
                 num_heads,
                 output_bits=8,
                 buffer_bits=32,
                 post_op_buffer_bits=32,
                 shiftmax_output_bits=10,
                 name=""):
        try:
            params = LayerParams(
                LayerType.Attention, {
                    "num_heads": num_heads,
                    "output_bits": output_bits,
                    "buffer_bits": buffer_bits,
                    "post_op_buffer_bits": post_op_buffer_bits,
                    "shiftmax_output_bits": shiftmax_output_bits
                })
            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
