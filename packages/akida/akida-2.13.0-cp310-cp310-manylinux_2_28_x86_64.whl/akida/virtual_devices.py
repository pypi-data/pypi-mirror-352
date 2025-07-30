from math import ceil, floor, sqrt
from .core import Device, IpVersion, NSoC_v1, NSoC_v2, TwoNodesIP_v1, AKD1500_v1, FPGA_v2, NP


def AKD1000():
    """Returns a virtual device for an AKD1000 NSoC.

    This function returns a virtual device for the Brainchip's AKD1000
    NSoC.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(3, 1, 0)
    dma_conf = NP.Ident(3, 1, 1)
    nps = [
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 1, 2), {NP.Type.CNP1}),
        NP.Info(NP.Ident(3, 1, 3), {NP.Type.CNP1}),
        NP.Info(NP.Ident(3, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 1, 0), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(4, 1, 1), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(4, 1, 2), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(4, 1, 3), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(4, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(4, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(4, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(4, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(4, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(5, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(5, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(5, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(5, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 5, 3), {NP.Type.CNP1, NP.Type.CNP2})
    ]
    mesh = NP.Mesh(IpVersion.v1, dma_event, dma_conf, nps)
    return Device(NSoC_v2, mesh)


def TwoNodesIPv1():
    """Returns a virtual device for a two nodes Akida IP.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.CNP1, NP.Type.CNP2})
    ]
    mesh = NP.Mesh(IpVersion.v1, dma_event, dma_conf, nps)
    return Device(TwoNodesIP_v1, mesh)


def AKD1500():
    """Returns a virtual device for AKD1500 chip.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 1, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 1, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 1, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 1, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 1, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 1, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 1, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 1, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 3), {NP.Type.CNP1, NP.Type.CNP2})
    ]
    mesh = NP.Mesh(IpVersion.v1, dma_event, dma_conf, nps)
    return Device(AKD1500_v1, mesh)


def TwoNodesIPv2():
    """Returns a 2-node virtual device for FPGA v2.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    skipdmas_num_channels = 2
    skip_dmas = [
        NP.Info(
            NP.Ident(1, 1, 3, skipdmas_num_channels),
            {NP.Type.SKIP_DMA_STORE, NP.Type.SKIP_DMA_LOAD})]
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.CNP1}),
        NP.Info(NP.Ident(2, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 2, 3), {NP.Type.CNP1, NP.Type.CNP2})
    ]

    mesh = NP.Mesh(IpVersion.v2, dma_event, dma_conf, nps, skip_dmas)
    return Device(FPGA_v2, mesh)


def SixNodesIPv2():
    """Returns a 6-node virtual device for FPGA v2.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    skipdmas_num_channels = 4
    skip_dmas = [
        NP.Info(
            NP.Ident(1, 1, 3, skipdmas_num_channels),
            {NP.Type.SKIP_DMA_STORE, NP.Type.SKIP_DMA_LOAD})]
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.FNP2}),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.TNP_B, NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.TNP_B, NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.TNP_B, NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 2, 0), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 2, 1), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 2, 2), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 2, 3), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 0), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 1), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 2), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 3), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 0), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 2, 1), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 2), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 3), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 0), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 1), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 2), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 3), {NP.Type.TNP_B, NP.Type.CNP1,
                                    NP.Type.CNP2})
    ]

    mesh = NP.Mesh(IpVersion.v2, dma_event, dma_conf, nps, skip_dmas)
    return Device(FPGA_v2, mesh)


def create_device(num_cnp_tnp,
                  num_fnp,
                  num_skip_dma_channel=0,
                  include_hrc=True,
                  input_buffer_memory=None,
                  weight_memory=None,
                  hw_version=FPGA_v2,
                  ):
    """Creates an Akida device with the specified hardware components.

    Args:
        num_cnp_tnp (int): Number of CNP and TNP_B units (TNP_B is only available on 2.x devices).
        num_fnp (int): Number of FNP units to include. An FNP2 with external memory is added first,
            followed by FNP3 units.
        num_skip_dma_channel (int, optional): Number of skip DMA channels (only applicable for
            2.x devices). Defaults to 0.
        include_hrc (bool, optional): Whether to include the HRC. Defaults to True.
        input_buffer_memory (int, optional): Size of shared input packet SRAM in bytes available
            inside the mesh for each two NPs. Defaults to None.
        weight_memory (int, optional): Size of shared filter SRAM in bytes available inside the
            mesh for each two NPs. Defaults to None.
        hw_version (akida.HwVersion, optional): The version of the device. Defaults to FPGA_v2.

    Returns:
        akida.Device: An Akida device.
    """
    # General akida node info
    SKIP_DMA_ROW = 1
    SKIP_DMA_ID = 3
    MAX_SKIP_DMA_CHANNELS_PER_COL = 4
    NUM_NPS_PER_NODE = 4

    class V1_INFO:
        INPUT_BUFFER_MEMORY = 43008
        WEIGHT_MEMORY = 44800
        HW_VERSIONS = [NSoC_v1, NSoC_v2, TwoNodesIP_v1, AKD1500_v1]

    class V2_INFO:
        INPUT_BUFFER_MEMORY = 65536
        WEIGHT_MEMORY = 51200
        HW_VERSIONS = [FPGA_v2]

    def _get_memory_info(input_buffer_memory, weight_memory, hw_info):
        if input_buffer_memory is None:
            input_buffer_memory = hw_info.INPUT_BUFFER_MEMORY

        if weight_memory is None:
            weight_memory = hw_info.WEIGHT_MEMORY

        return input_buffer_memory, weight_memory

    def _compute_total_nps(num_cnp_tnp, num_fnp):
        total_nps = num_cnp_tnp + num_fnp

        # The nodes are completed with NPs of type CNP1, CNP2 (and TNP_B if hw_version = FPGA_v2)
        # if the requested NPs are not a multiple of NUM_NPS_PER_NODE.
        nps_to_add = (-total_nps) % NUM_NPS_PER_NODE
        num_cnp_tnp += nps_to_add
        total_nps += nps_to_add

        return total_nps, num_cnp_tnp

    def _compute_optimal_nps_grid_shape(total_nps):
        if total_nps == 0:
            return 0, 0
        num_nodes = total_nps / NUM_NPS_PER_NODE
        fractional_diff = (num_nodes / sqrt(num_nodes)) - (num_nodes // sqrt(num_nodes))

        # Increment columns first and then rows
        num_cols = floor(sqrt(num_nodes)) + ceil(fractional_diff)
        num_rows = floor(sqrt(num_nodes)) + round(fractional_diff)

        return num_rows, num_cols

    def _make_skip_dmas(num_cols, num_skip_dma_channel):
        skip_dmas = []

        if hw_version != FPGA_v2 and num_skip_dma_channel > 0:
            raise ValueError(f"Skip DMAs are only supported on v2 devices (hw_version=FPGA_v2). "
                             f"Current hardware version: {hw_version}.")

        if num_skip_dma_channel == 0:
            return skip_dmas

        # Distribute Skip DMAs accross columns as much as possible
        # When the number of Skip DMAs exceeds the number of columns used by nps, we increase
        # the number of columns.
        current_max_skip_dma_channels = num_cols * MAX_SKIP_DMA_CHANNELS_PER_COL
        if (extra_channels := num_skip_dma_channel - current_max_skip_dma_channels) > 0:
            num_cols += ceil((extra_channels) / MAX_SKIP_DMA_CHANNELS_PER_COL)

        # Compute number of channels per skip dma
        num_channels_per_skip_dma = ceil(num_skip_dma_channel / num_cols)

        # Deduce the number of skip dmas in the device
        num_skip_dmas = min(num_skip_dma_channel, num_cols)

        for col in range(1, num_skip_dmas + 1):
            skip_dmas.append(
                NP.Info(
                    NP.Ident(col, SKIP_DMA_ROW, SKIP_DMA_ID, num_channels_per_skip_dma),
                    {NP.Type.SKIP_DMA_STORE, NP.Type.SKIP_DMA_LOAD},
                )
            )

        return skip_dmas

    def _make_nps(num_rows, num_cols, num_cnp_tnp, num_fnp):
        # Construct NP types
        cnp_types = [NP.Type.CNP1, NP.Type.CNP2]
        fnp_types = [NP.Type.CNP1, NP.Type.CNP2, NP.Type.FNP2]

        if hw_version == FPGA_v2:
            cnp_types.insert(0, NP.Type.TNP_B)
            fnp_types.insert(0, NP.Type.TNP_B)

        nps = []

        # Starting from row 2
        for row in range(2, num_rows + 2):
            for col in range(1, num_cols + 1):
                # Now loop over nps
                for id in range(NUM_NPS_PER_NODE):
                    if num_cnp_tnp > 0:
                        nps.append(NP.Info(NP.Ident(col, row, id), cnp_types))
                        num_cnp_tnp -= 1
                    elif num_fnp > 0:
                        nps.append(NP.Info(NP.Ident(col, row, id), fnp_types))
                        # Change FNP2 with FNP3
                        if fnp_types[-1] == NP.Type.FNP2:
                            fnp_types[-1] = NP.Type.FNP3
                        num_fnp -= 1
        return nps

    if not include_hrc:
        raise NotImplementedError("Disabling HRC is not supported.")

    # Get Ip version
    ip_version = IpVersion.v2 if hw_version.product_id == 0xA2 else IpVersion.v1

    # Check HW version
    hw_info = V2_INFO if ip_version == IpVersion.v2 else V1_INFO
    if hw_version not in hw_info.HW_VERSIONS:
        raise ValueError(f"Invalid HW version '{hw_version}'. "
                         f"Expected one of: {hw_info.HW_VERSIONS}.")

    # Fill input and weight memory with defaults if necessary
    input_buffer_memory, weight_memory = _get_memory_info(input_buffer_memory, weight_memory,
                                                          hw_info)

    # Compute total nps and construct the optimal grid for NPs
    # The mesh should be as square as possible
    total_nps, num_cnp_tnp = _compute_total_nps(num_cnp_tnp, num_fnp)
    num_rows, num_cols = _compute_optimal_nps_grid_shape(total_nps)
    if total_nps == 0 and not include_hrc:
        raise ValueError("It is not possible to create a completely empty device. "
                         f"num_cnp_tnp + num_fnp ({total_nps}) must be greater than zero or "
                         "HRC must be included).")

    # Make DMA event and conf
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)

    # Make SkipDMAs
    skip_dmas = _make_skip_dmas(num_cols, num_skip_dma_channel)

    # Make NPs
    nps = _make_nps(num_rows, num_cols, num_cnp_tnp, num_fnp)

    # Make the mesh
    mesh = NP.Mesh(ip_version, dma_event, dma_conf, nps,
                   skip_dmas, input_buffer_memory, weight_memory)

    return Device(hw_version, mesh)
