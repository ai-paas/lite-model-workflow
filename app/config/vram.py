import math
from enum import Enum


VRAM_MARGIN_RATIO = 1.2
# 1.2배 마진 점유량 기준. 임계치는 요구사항에 명시되지 않아 GPU SKU 경계(8GiB / 24GiB)로 둔다.
VRAM_LEVEL_LOW_MAX_MB = 8 * 1024
VRAM_LEVEL_MID_MAX_MB = 24 * 1024


class VramLevel(str, Enum):
    HIGH = "상"
    MID = "중"
    LOW = "하"

    @classmethod
    def to_regex_pattern(cls) -> str:
        content = "|".join([level.value for level in cls])
        return rf"^({content})$"


def apply_vram_margin(peak_vram_mb: int) -> int:
    """실측 peak VRAM 에 마진 1.2배를 적용한 점유량(MB)."""
    return math.ceil(peak_vram_mb * VRAM_MARGIN_RATIO)


def classify_vram_level(vram_occupancy_mb: int) -> VramLevel:
    """마진이 반영된 점유량을 상/중/하로 분류한다."""
    if vram_occupancy_mb < VRAM_LEVEL_LOW_MAX_MB:
        return VramLevel.LOW
    if vram_occupancy_mb < VRAM_LEVEL_MID_MAX_MB:
        return VramLevel.MID
    return VramLevel.HIGH
