"""Reference model of the saturating conversion (requirements LLR-CONV-*).

IEEE-754 binary32 operations are modelled by computing in binary64 and
rounding the result to binary32; for +, -, *, / on binary32 operands this
double rounding is exact (53 >= 2*24 + 2). The round-half-up step itself is
done in exact rational arithmetic.
"""

import math
import struct
from fractions import Fraction


def f32(value: float) -> float:
    """Round a binary64 value to the nearest binary32 value."""
    try:
        return struct.unpack("<f", struct.pack("<f", value))[0]
    except OverflowError:
        return math.copysign(math.inf, value)


def f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", f32(value)))[0]


def bits_f32(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def nearest_f32(value: Fraction) -> float:
    return f32(float(value))


def encode(factor: float, offset: float, raw_min: int, raw_max: int, phys: float) -> int:
    if math.isnan(phys):
        return raw_min
    quotient = f32(f32(phys - offset) / factor)
    if quotient >= f32(float(raw_max)):
        return raw_max
    if quotient > f32(float(raw_min)):
        exact = Fraction(quotient)
        whole = math.floor(exact)
        return whole + (1 if exact - whole >= Fraction(1, 2) else 0)
    return raw_min


def decode(factor: float, offset: float, raw_min: int, raw_max: int, raw: int) -> float:
    saturated = min(max(raw, raw_min), raw_max)
    return f32(f32(f32(float(saturated)) * factor) + offset)
