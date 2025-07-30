#pragma once

#include <cstdint>

#include "infra/registers_common.h"

namespace akida {

// fields for word 1 cnp
inline constexpr RegDetail CONV_X(0, 11);
inline constexpr RegDetail CONV_Y(16, 27);
inline constexpr RegDetail CONV_POTENTIAL_MSB(28, 31);
// fields for word 2 cnp
inline constexpr RegDetail CONV_F(0, 10);
inline constexpr RegDetail CONV_ACTIVATION(16, 23);
inline constexpr RegDetail CONV_POTENTIAL_LSB(12, 31);
// fields for word 1 fnp
inline constexpr RegDetail FC_F(0, 17);
// fields for word 2 fnp
inline constexpr RegDetail FC_ACTIVATION(0, 25);  // potential is the same
inline constexpr RegDetail FC_POLARITY(31);       // should be set to 1

// fields for output header
inline constexpr RegDetail OUTPUT_WORD_SIZE(0, 27);
inline constexpr RegDetail FORMAT_TYPE(28, 31);

enum class FormatType : uint8_t {
  full_connected_potential = 0x1,
  convolution = 0x2,
  convolution_full_potential_type = 0x3,
  full_connected_activation = 0x5,
  dense_cnp_full_potential = 0x8,
  dense_cnp_short_potential = 0x9,
  dense_fnp_activation = 0xA,
  dense_fnp_potential = 0xB,
  dense_cnp_activation = 0xC,
  dense_np_pksram = 0xD,
  dense_fnp_short_potential = 0xE,
  dma_loop_back = 0xF
};

}  // namespace akida
