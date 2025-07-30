from akida.core import Layer, LayerParams, LayerType


class VitEncoderBlock(Layer):
    """ Layer corresponding to a ViT encoder block.

     It's composed of the following layers:

        - a pre-attention MadNorm layer
        - Query, Key and Value Dense layers
        - an Attention layer and it Dense projection layer
        - a skip connection (Add) between the input and the output of attention projection
        - a pre-ML MadNorm layer
        - a MLP composed of two Dense layers
        - a skip connection (Add) between the MLP output and the previous Add layer
        - optionally when tokens_to_extract is set to a non zero value, a BatchNormalization
          layer and the given ExtractToken number (1 or 2)
        - optionally when num_classes is set a classification head with one or 2 Dense layers
          depending on the number of tokens

    This layer covers all the above layers operations.

    Note that final output values will be saturated on the range that can be represented with
    output_bits.

    Args:
        hidden_size (int, optional): internal shape of the block. Defaults to 192.
        mlp_dim (int, optional): dimension of the first dense layer of the MLP. Defaults to 768.
        num_heads (int, optional): number of heads in the multi-head attention. Defaults to 3.
        num_classes (int, optional): number of classes to set in the classification head, if zero
            no classification head is added. 'tokens_to_extract' must be different from 0. Defaults
            to 0.
        tokens_to_extract (int, optional): number of non patch tokens to extract. Defaults to 0.
        output_bits (int, optional): output bitwidth. Defaults to 8.
        buffer_bits (int, optional): buffer bitwidth. Defaults to 32.
        post_op_buffer_bits (int, optional): internal bitwidth for post operations. Defaults to 32.
        head_bits (int, optional): similar to 'output_bits' but for the optional head(s). Defaults
            to 28.
        name (str, optional): name of the layer. Defaults to empty string.
    """

    def __init__(self,
                 hidden_size=192,
                 mlp_dim=768,
                 num_heads=3,
                 num_classes=0,
                 tokens_to_extract=0,
                 output_bits=8,
                 buffer_bits=32,
                 post_op_buffer_bits=32,
                 head_bits=28,
                 name=""):
        try:
            params = LayerParams(
                LayerType.VitEncoderBlock, {
                    "hidden_size": hidden_size,
                    "mlp_dim": mlp_dim,
                    "num_heads": num_heads,
                    "num_classes": num_classes,
                    "tokens_to_extract": tokens_to_extract,
                    "output_bits": output_bits,
                    "buffer_bits": buffer_bits,
                    "post_op_buffer_bits": post_op_buffer_bits,
                    "head_bits": head_bits
                })
            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
