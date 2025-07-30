#pragma once

#include "akida/hardware_device.h"
#include "akida/ip_version.h"
#include "akida/np.h"

namespace akida {

/**
 * The layout of a mesh of Neural Processors.
 */
struct AKIDASHAREDLIB_EXPORT Mesh final {
  /**
   * Discover the topology of a Device Mesh.
   */
  static std::unique_ptr<Mesh> discover(HardwareDevice* device);

  explicit Mesh(IpVersion version, const hw::Ident& dma_event,
                const hw::Ident& dma_conf, std::vector<np::Info> nps,
                std::vector<np::Info> skip_dmas = {});

  // TODO: can be replaced by default Three-way comparison in C++20
  bool operator==(const Mesh& other) const {
    return dma_event == other.dma_event && dma_conf == other.dma_conf &&
           nps == other.nps && skip_dmas == other.skip_dmas;
  }

  // TODO: can be replaced by default Three-way comparison in C++20
  bool operator!=(const Mesh& other) const { return !(*this == other); }

  IpVersion version;               /**< The IP version of the mesh (v1 or v2) */
  hw::Ident dma_event;             /**< The DMA event endpoint */
  hw::Ident dma_conf;              /**< The DMA configuration endpoint */
  std::vector<np::Info> nps;       /**< The available Neural Processors */
  std::vector<np::Info> skip_dmas; /**< The available skip dmas */
  /**
   * Size of shared input packet SRAM in bytes available inside the mesh
   * for each two NPs.
   */
  uint32_t np_input_sram_size{};
  /**
   * Size of shared filter SRAM in bytes available inside the mesh for each two
   * NPs.
   */
  uint32_t np_weight_sram_size{};
};

}  // namespace akida
