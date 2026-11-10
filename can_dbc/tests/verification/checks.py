"""Checks shared by several verification tests."""

import random
import zlib

from .oracle import bit_oracle
from .support import Harness, cantools_decode, cantools_encode


def rng(*parts) -> random.Random:
    """Deterministic random source, seeded from the test case identity."""
    return random.Random(zlib.crc32("/".join(str(p) for p in parts).encode()))


def expected_frame(msg, values) -> bytes:
    """Expected payload from both oracles (which must agree)."""
    reference = bit_oracle.pack(msg.dlc, msg.layout, values)
    masked = {s.name: values[s.name] & ((1 << s.length) - 1) for s in msg.signals}
    assert cantools_encode(msg, masked) == reference, "oracles disagree"
    return reference


def expected_values(view, frame: bytes) -> dict:
    """Expected unpacked members of a node view from both oracles."""
    reference = bit_oracle.unpack(frame, view.layout)
    decoded = cantools_decode(view.msg, frame)
    assert {name: decoded[name] for name in reference} == reference, "oracles disagree"
    return reference


def random_values(view, source: random.Random) -> dict:
    return {s.name: source.getrandbits(s.length) for s in view.signals}


def check_node_against_oracles(harness: Harness, count: int = 50) -> None:
    """Random pack/unpack vectors of every message of a node against the oracles."""
    for name, view in harness.views.items():
        source = rng("node-check", harness.node, name)
        if view.direction == "TX":
            vectors = [random_values(view, source) for _ in range(count)]
            frames = harness.pack(name, vectors, fill=0xFF)
            assert frames == [expected_frame(view.msg, v) for v in vectors]
        else:
            frames = [bytes(source.getrandbits(8) for _ in range(view.msg.dlc))
                      for _ in range(count)]
            assert harness.unpack(name, frames, fill=0xFF) == \
                [expected_values(view, f) for f in frames]
