"""VT-CONV: saturating conversion library, driven through the generated database."""

import math
from fractions import Fraction

import pytest

from .checks import rng
from .oracle import conv_oracle
from .oracle.conv_oracle import bits_f32, f32_bits, nearest_f32
from .support import NODE_CONFIGS, expected_limits, node_views

pytestmark = pytest.mark.functional

# (node, message index, signal index, message name, signal) for signals <= 32 bit
CASES = [(node, mi, si, view.msg.name, sig)
         for node, mode in NODE_CONFIGS
         for mi, view in enumerate(node_views(node, mode))
         for si, sig in enumerate(view.signals) if sig.length <= 32]
IDS = [f"{c[0]}-{c[3]}.{c[4].name}" for c in CASES]
EXACT_LIMIT = 1 << 20      # raw values up to here are far from float32 resolution


def _has_exact_ties(sig):
    """Half-step values are exactly representable: offset 0, power-of-two factor."""
    raw_min, raw_max = expected_limits(sig)
    denominator = sig.factor.denominator
    return (sig.offset == 0 and sig.factor.numerator == 1
            and (denominator & (denominator - 1)) == 0 and raw_max - raw_min >= 2)


def _subset(predicate):
    chosen = [c for c in CASES if predicate(c[4])]
    return {"argvalues": chosen, "ids": [f"{c[0]}-{c[3]}.{c[4].name}" for c in chosen]}


TIE_CASES = _subset(_has_exact_ties)
FINE_CASES = _subset(lambda sig: expected_limits(sig)[1] <= EXACT_LIMIT)


def params(sig):
    raw_min, raw_max = expected_limits(sig)
    return nearest_f32(sig.factor), nearest_f32(sig.offset), raw_min, raw_max


def phys_of(sig, raw) -> Fraction:
    return raw * sig.factor + sig.offset


def sample_raws(sig):
    raw_min, raw_max = expected_limits(sig)
    high = min(raw_max, EXACT_LIMIT)
    middle = (raw_min + high) // 2
    return sorted({raw_min, min(raw_min + 1, high), middle, max(high - 1, raw_min), high})


@pytest.mark.req("LLR-CONV-001")
@pytest.mark.parametrize("node,mi,si,name,sig", CASES, ids=IDS)
def test_encode_rounds_to_nearest_raw(harnesses, node, mi, si, name, sig):
    """Exact-arithmetic expectation: values within +-0.25 LSB of a raw step give that raw."""
    raw_min, raw_max = expected_limits(sig)
    inputs, expected = [], []
    for raw in sample_raws(sig):
        for delta in (Fraction(0), Fraction(1, 4), Fraction(-1, 4)):
            inputs.append(f32_bits(nearest_f32(phys_of(sig, raw + delta))))
            expected.append(min(max(raw, raw_min), raw_max))
    assert harnesses[node].encode(mi, si, inputs) == expected


@pytest.mark.req("LLR-CONV-001")
@pytest.mark.parametrize("node,mi,si,name,sig", **TIE_CASES)
def test_encode_rounds_half_up(harnesses, node, mi, si, name, sig):
    """Ties: a value exactly half way between two raw steps gives the upper one.

    Only signals whose half-step values are exactly representable are used
    (offset 0 and a power-of-two factor), so the tie is not blurred by
    float32 rounding.
    """
    _, raw_max = expected_limits(sig)
    raws = [r for r in sample_raws(sig) if r < min(raw_max, EXACT_LIMIT)]
    inputs = [f32_bits(float(phys_of(sig, raw + Fraction(1, 2)))) for raw in raws]
    assert harnesses[node].encode(mi, si, inputs) == [raw + 1 for raw in raws]


@pytest.mark.req("LLR-CONV-001", "LLR-CONV-002")
@pytest.mark.parametrize("node,mi,si,name,sig", CASES, ids=IDS)
def test_encode_matches_reference_model(harnesses, node, mi, si, name, sig):
    """Bit-exact comparison with the binary32 reference model, incl. random inputs."""
    factor, offset, raw_min, raw_max = params(sig)
    low, high = float(phys_of(sig, raw_min)), float(phys_of(sig, raw_max))
    span = max(high - low, float(sig.factor))
    source = rng("encode", name, sig.name)
    values = [low, high, 0.0, -0.0, 1.0, -1.0, 3.4e38, -3.4e38, 1e-45, math.inf, -math.inf]
    values += [source.uniform(low - span, high + span) for _ in range(400)]
    values += [source.uniform(low, high) for _ in range(400)]
    inputs = [f32_bits(v) for v in values]
    expected = [conv_oracle.encode(factor, offset, raw_min, raw_max, bits_f32(b)) for b in inputs]
    results = harnesses[node].encode(mi, si, inputs)
    assert results == expected
    assert all(raw_min <= r <= raw_max for r in results)


@pytest.mark.req("LLR-CONV-002")
@pytest.mark.parametrize("node,mi,si,name,sig", CASES, ids=IDS)
def test_encode_saturates(harnesses, node, mi, si, name, sig):
    raw_min, raw_max = expected_limits(sig)
    lsb = sig.factor
    below = [phys_of(sig, raw_min) - k * lsb for k in (1, 2, 1000, 10 ** 7)]
    above = [phys_of(sig, raw_max) + k * lsb for k in (1, 2, 1000, 10 ** 7)]
    inputs = [f32_bits(nearest_f32(v)) for v in below] + [f32_bits(-math.inf), f32_bits(-3.4e38)]
    assert set(harnesses[node].encode(mi, si, inputs)) == {raw_min}
    inputs = [f32_bits(nearest_f32(v)) for v in above] + [f32_bits(math.inf), f32_bits(3.4e38)]
    assert set(harnesses[node].encode(mi, si, inputs)) == {raw_max}
    limits = [f32_bits(nearest_f32(phys_of(sig, raw_min))), f32_bits(nearest_f32(phys_of(sig, raw_max)))]
    assert harnesses[node].encode(mi, si, limits) == [raw_min, raw_max]


@pytest.mark.req("LLR-CONV-003")
@pytest.mark.parametrize("node,mi,si,name,sig", CASES, ids=IDS)
def test_encode_nan_gives_raw_min(harnesses, node, mi, si, name, sig):
    raw_min, _ = expected_limits(sig)
    nans = [0x7FC00000, 0xFFC00000, 0x7F800001, 0xFFFFFFFF]
    assert set(harnesses[node].encode(mi, si, nans)) == {raw_min}


@pytest.mark.req("LLR-CONV-004")
@pytest.mark.parametrize("node,mi,si,name,sig", CASES, ids=IDS)
def test_decode(harnesses, node, mi, si, name, sig):
    """Reference model (bit-exact) and exact arithmetic (tolerance), with saturation."""
    factor, offset, raw_min, raw_max = params(sig)
    source = rng("decode", name, sig.name)
    raws = sorted({0, raw_min, max(raw_min - 1, 0), raw_max, min(raw_max + 1, 0xFFFFFFFF),
                   (raw_min + raw_max) // 2, 0xFFFFFFFF}
                  | {source.randint(0, min(2 * raw_max + 1, 0xFFFFFFFF)) for _ in range(200)})
    results = harnesses[node].decode(mi, si, raws)
    assert results == [f32_bits(conv_oracle.decode(factor, offset, raw_min, raw_max, r)) for r in raws]
    for raw, bits in zip(raws, results):
        exact = phys_of(sig, min(max(raw, raw_min), raw_max))
        tolerance = Fraction(1, 10 ** 6) * max(abs(exact), abs(sig.offset), 1)
        assert abs(Fraction(bits_f32(bits)) - exact) <= tolerance, raw


@pytest.mark.req("LLR-CONV-001", "LLR-CONV-004")
@pytest.mark.parametrize("node,mi,si,name,sig", **FINE_CASES)
def test_decode_of_encode_is_within_half_lsb(harnesses, node, mi, si, name, sig):
    """Only signals whose raw range is well within float32 precision."""
    raw_min, raw_max = expected_limits(sig)
    low, high = phys_of(sig, raw_min), phys_of(sig, raw_max)
    source = rng("roundtrip", name, sig.name)
    values = [bits_f32(f32_bits(source.uniform(float(low), float(high)))) for _ in range(300)]
    raws = harnesses[node].encode(mi, si, [f32_bits(v) for v in values])
    decoded = harnesses[node].decode(mi, si, raws)
    for value, bits in zip(values, decoded):
        clamped = min(max(Fraction(value), low), high)
        error = abs(Fraction(bits_f32(bits)) - clamped)
        assert error <= sig.factor * Fraction(501, 1000), value
