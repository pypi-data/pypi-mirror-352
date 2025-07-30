#pragma once

#include <cstdint>

#include "infra/registers_common.h"

namespace akida {
namespace dma {

// DMA header format
inline constexpr uint32_t HDR_WORD1 = 0x0;
inline constexpr RegDetail HDR_NP_COL(24, 31);
inline constexpr RegDetail HDR_NP_ROW(16, 23);
inline constexpr RegDetail HDR_NP_DST(8, 11);
inline constexpr RegDetail HDR_HRC_EN(6, 7);
inline constexpr RegDetail HDR_UID(0, 3);

inline constexpr uint32_t HDR_WORD2 = 0x1;
inline constexpr RegDetail HDR_XL(31);
inline constexpr RegDetail HDR_BLOCK_LEN(16, 29);
inline constexpr RegDetail HDR_START_ADDR(0, 15);

inline constexpr uint8_t HDR_UID_CNP_FILTER = 0;
inline constexpr uint8_t HDR_UID_CNP_FILTER_COMPACT = 1;
inline constexpr uint8_t HDR_UID_INPUT_SHIFT = 2;  // SRAM_C2
inline constexpr uint8_t HDR_UID_CNP_LEARN_THRES = 2;
inline constexpr uint8_t HDR_UID_CNP_THRES_FIRE = 4;
inline constexpr uint8_t HDR_UID_CNP_BIAS_OUT_SCALES = 4;  // SRAM_C4
inline constexpr uint8_t HDR_UID_FNP_WEIGHT = 6;
inline constexpr uint8_t HDR_UID_NP_REGS = 8;
inline constexpr uint8_t HDR_UID_HRC_SRAM = 0;
inline constexpr uint8_t HDR_UID_HRC_REGS = 8;
// IB Packet SRAM_C3 for Skip Merging Add shift
inline constexpr uint8_t HDR_UID_IB_PCK = 0x3;

// ViT block specific UID
inline constexpr uint8_t HDR_UID_NMHA = 0x0;
inline constexpr uint8_t HDR_UID_QKV = 0x1;
inline constexpr uint8_t HDR_UID_MHA_SHIFTMAX = 0x2;
inline constexpr uint8_t HDR_UID_MHA_OP = 0x3;
inline constexpr uint8_t HDR_UID_CONCAT = 0x4;
inline constexpr uint8_t HDR_UID_SKIP_CONNECTION_1 = 0x5;
inline constexpr uint8_t HDR_UID_NMLP = 0x6;
inline constexpr uint8_t HDR_UID_MLP_1 = 0x7;
inline constexpr uint8_t HDR_UID_ACTIVATION = 0xa;
inline constexpr uint8_t HDR_UID_MLP2 = 0xb;
inline constexpr uint8_t HDR_UID_SKIP_CONNECTION_2 = 0xc;
inline constexpr uint8_t HDR_UID_BATCH_NORM = 0xd;
inline constexpr uint8_t HDR_UID_CLASS_SP = 0xe;

// Read word
inline constexpr uint32_t HDR_READ_WORD1 = 0x0;
inline constexpr RegDetail HDR_READ_PACKET_SZ(0, 15);

}  // namespace dma
}  // namespace akida
