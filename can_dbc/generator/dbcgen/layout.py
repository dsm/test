"""Bit layout and raw range computation for Motorola (big-endian) signals.

The frame is regarded as one big-endian number: frame bit index 0 ("top") is
bit 7 of byte 0, index 63 is bit 0 of byte 7. A Motorola signal is a
contiguous field in that numbering, starting at its DBC start bit (the MSB).
"""

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from .model import Signal

RAW32_MAX = 0xFFFFFFFF


@dataclass(frozen=True)
class Layout:
    top: int            # frame bit index of the MSB
    bottom: int         # frame bit index of the LSB
    first_byte: int
    last_byte: int
    shift: int          # distance of the LSB from bit 0 of last_byte
    mask: int           # (1 << length) - 1
    window_bits: int    # 32 or 64
    field_bits: int     # 8, 16, 32 or 64


def compute_layout(start: int, length: int) -> Layout:
    top = (start // 8) * 8 + (7 - (start % 8))
    bottom = top + length - 1
    first_byte = top // 8
    last_byte = bottom // 8
    shift = last_byte * 8 + 7 - bottom
    window_bits = 32 if (last_byte - first_byte + 1) <= 4 else 64
    field_bits = next(b for b in (8, 16, 32, 64) if length <= b)
    return Layout(top, bottom, first_byte, last_byte, shift,
                  (1 << length) - 1, window_bits, field_bits)


def raw_limits(sig: Signal) -> Tuple[int, int]:
    """Saturation limits in the raw domain, derived from the DBC [min|max].

    [0|0] means "not specified": the full scale of the signal is used.
    Signals wider than 32 bits are raw-only; their limits are clipped to the
    32-bit range of can_conv_t.
    """
    full = (1 << sig.length) - 1
    if sig.minimum == 0 and sig.maximum == 0:
        low, high = 0, full
    else:
        low = max(0, math.ceil((sig.minimum - sig.offset) / sig.factor))
        high = min(full, math.floor((sig.maximum - sig.offset) / sig.factor))
    return min(low, RAW32_MAX), min(high, RAW32_MAX)


def physical(sig: Signal, raw: int) -> Fraction:
    return raw * sig.factor + sig.offset
