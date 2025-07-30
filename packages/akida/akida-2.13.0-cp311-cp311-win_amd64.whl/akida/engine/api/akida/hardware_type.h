#pragma once

#include <set>

namespace akida::hw {

enum class BasicType {
  none,
  HRC,
  CNP,
  FNP,
  VIT_BLOCK,
  SKIP_DMA,
  TNP_B,
  TNP_R,
  DMA
};
enum class Type {
  none,
  HRC,
  CNP1,
  CNP2,
  FNP2,
  FNP3,
  VIT_BLOCK,
  SKIP_DMA_STORE,
  TNP_B,
  TNP_R,
  SKIP_DMA_LOAD,
  DMA
};
using Types = std::set<Type>;

}  // namespace akida::hw