"""VT-GOLDEN, VT-LAYOUT, VT-FRAMEBITS, VT-MASK, VT-ROUNDTRIP, VT-BUFFER.

Black-box verification of the generated pack/unpack functions against the
independent oracles (bit-by-bit reference model and cantools).
"""

import pytest

from .checks import expected_frame, expected_values, random_values, rng
from .oracle import bit_oracle
from .support import NODE_CONFIGS, message, model, node_views

pytestmark = pytest.mark.functional

TX_CASES = [(node, v.msg.name) for node, mode in NODE_CONFIGS
            for v in node_views(node, mode) if v.direction == "TX"]
RX_CASES = [(node, v.msg.name) for node, mode in NODE_CONFIGS
            for v in node_views(node, mode) if v.direction == "RX"]
MESSAGES = [m.name for m in model()]

# Hand-calculated vectors (independent of both oracles): raw values -> payload.
GOLDEN = {
    "BMS_Status": ({"PackVoltage": 4000, "PackCurrent": 2500, "Soc": 800, "State": 2,
                    "ContactorClosed": 1, "FaultActive": 0, "MaxCellTemp": 65,
                    "AliveCounter": 5}, "0FA09C4C81404105"),
    "VCU_Heartbeat": ({"HbCounter": 0xA5, "VcuState": 9, "SwVersion": 0x123}, "A59123"),
    "VCU_Command": ({"TorqueRequest": 0x1234, "SpeedLimit": 6000, "DriveMode": 3,
                     "ContactorRequest": 1, "ChargeEnable": 0, "MaxChargeCurrent": 0x2AB,
                     "CmdCounter": 7}, "1234BB83AAB00007"),
    "MCU_Status": ({"MotorSpeed": 0xBEEF, "ActualTorque": 0xABC,
                    "OdometerTicks": 0x23456789, "InverterTemp": 0x2A}, "BEEFABC8D159E26A"),
    "MCU_Diag": ({"ErrorFlags": 0xDEADBEEF, "ErrorCount": 0x155, "LimpMode": 1},
                 "DEADBEEFAAC0"),
    "BMS_Energy": ({"EnergyCounter": 0x0123456789, "BalancingActive": 1, "Derating": 0,
                    "ChargeCycles": 0x2ABCDE}, "0123456789AABCDE"),
}


def receivers_of(name):
    return [node for node, msg in RX_CASES if msg == name]


# ---------------------------------------------------------------- VT-GOLDEN

@pytest.mark.req("LLR-PACK-001", "LLR-PACK-003")
@pytest.mark.parametrize("name", MESSAGES)
def test_golden_pack(harnesses, name):
    values, payload = GOLDEN[name]
    frame = harnesses[message(name).sender].pack(name, [values])[0]
    assert frame == bytes.fromhex(payload)


@pytest.mark.req("LLR-UNPACK-001")
@pytest.mark.parametrize("node,name", RX_CASES)
def test_golden_unpack(harnesses, node, name):
    values, payload = GOLDEN[name]
    view = harnesses[node].views[name]
    result = harnesses[node].unpack(name, [bytes.fromhex(payload)])[0]
    assert result == {s.name: values[s.name] for s in view.signals}


def test_golden_vectors_cover_every_message():
    assert sorted(GOLDEN) == sorted(MESSAGES)


# ---------------------------------------------------------------- VT-LAYOUT

@pytest.mark.req("LLR-PACK-001", "LLR-PACK-003")
@pytest.mark.parametrize("node,name", TX_CASES)
def test_pack_walking_one(harnesses, node, name):
    """Each single signal bit ends up in exactly one, the expected, frame bit."""
    view = harnesses[node].views[name]
    vectors = []
    for sig in view.signals:
        for bit in range(sig.length):
            vector = {s.name: 0 for s in view.signals}
            vector[sig.name] = 1 << bit
            vectors.append(vector)
    frames = harnesses[node].pack(name, vectors)
    for vector, frame in zip(vectors, frames):
        assert frame == expected_frame(view.msg, vector), vector
        assert sum(bin(b).count("1") for b in frame) == 1, vector
    assert len(set(frames)) == len(frames), "two signal bits share a frame bit"


@pytest.mark.req("LLR-PACK-001")
@pytest.mark.parametrize("node,name", TX_CASES)
def test_pack_walking_zero(harnesses, node, name):
    """Each single cleared signal bit clears exactly the expected frame bit."""
    view = harnesses[node].views[name]
    full = {s.name: (1 << s.length) - 1 for s in view.signals}
    vectors = []
    for sig in view.signals:
        for bit in range(sig.length):
            vector = dict(full)
            vector[sig.name] ^= 1 << bit
            vectors.append(vector)
    frames = harnesses[node].pack(name, vectors)
    mask = bit_oracle.used_mask(view.msg.dlc, view.layout)
    for vector, frame in zip(vectors, frames):
        assert frame == expected_frame(view.msg, vector), vector
        differing = sum(bin(a ^ b).count("1") for a, b in zip(frame, mask))
        assert differing == 1, vector


# ------------------------------------------------------------------ VT-MASK

@pytest.mark.req("LLR-PACK-002")
@pytest.mark.parametrize("node,name", TX_CASES)
def test_pack_masks_excess_value_bits(harnesses, node, name):
    """Values wider than the signal never disturb other signals or unused bits."""
    view = harnesses[node].views[name]
    type_max = {s.name: (1 << s.field_bits) - 1 for s in view.signals}
    vectors = [dict(type_max)]
    for sig in view.signals:
        vector = {s.name: 0 for s in view.signals}
        vector[sig.name] = type_max[sig.name]
        vectors.append(vector)
        if sig.length < sig.field_bits:
            only_excess = {s.name: 0 for s in view.signals}
            only_excess[sig.name] = type_max[sig.name] & ~((1 << sig.length) - 1)
            vectors.append(only_excess)
    frames = harnesses[node].pack(name, vectors)
    assert frames[0] == bit_oracle.used_mask(view.msg.dlc, view.layout)
    for vector, frame in zip(vectors, frames):
        assert frame == bit_oracle.pack(view.msg.dlc, view.layout, vector), vector


# ---------------------------------------------------------------- VT-BUFFER

@pytest.mark.req("LLR-PACK-003", "LLR-PACK-004")
@pytest.mark.parametrize("node,name", TX_CASES)
def test_pack_result_independent_of_previous_buffer_content(harnesses, node, name):
    """Exactly data[0..DLC-1] is written, whatever was in the buffer before."""
    view = harnesses[node].views[name]
    source = rng("buffer", name)
    vectors = [{s.name: 0 for s in view.signals}] + \
        [random_values(view, source) for _ in range(20)]
    expected = [expected_frame(view.msg, v) for v in vectors]
    for fill in (0x00, 0xFF, 0xAA, 0x55):
        # Guard bytes around the payload are checked inside Harness.pack().
        assert harnesses[node].pack(name, vectors, fill=fill) == expected, hex(fill)


@pytest.mark.req("LLR-UNPACK-003")
@pytest.mark.parametrize("node,name", RX_CASES)
def test_unpack_writes_every_member_and_keeps_input(harnesses, node, name):
    """Result does not depend on the previous structure content."""
    view = harnesses[node].views[name]
    source = rng("members", name)
    frames = [bytes(view.msg.dlc), bytes([0xFF]) * view.msg.dlc] + \
        [bytes(source.getrandbits(8) for _ in range(view.msg.dlc)) for _ in range(20)]
    expected = [expected_values(view, f) for f in frames]
    for fill in (0x00, 0xFF, 0xA5):
        # Input immutability is checked inside Harness.unpack().
        assert harnesses[node].unpack(name, frames, fill=fill) == expected, hex(fill)


# ------------------------------------------------------------- VT-FRAMEBITS

@pytest.mark.req("LLR-UNPACK-001", "LLR-UNPACK-002")
@pytest.mark.parametrize("node,name", RX_CASES)
def test_unpack_walking_frame_bits(harnesses, node, name):
    """Every frame bit affects only the signal that owns it, with the right weight."""
    view = harnesses[node].views[name]
    dlc = view.msg.dlc
    owners = bit_oracle.owners(view.layout)
    positions = [(byte, bit) for byte in range(dlc) for bit in range(8)]
    ones = [bytes((1 << bit) if i == byte else 0 for i in range(dlc)) for byte, bit in positions]
    zeros = [bytes(b ^ 0xFF for b in frame) for frame in ones]
    results_one = harnesses[node].unpack(name, ones)
    results_zero = harnesses[node].unpack(name, zeros)
    for position, frame, result in zip(positions, ones, results_one):
        expected = {s.name: 0 for s in view.signals}
        if position in owners:
            owner, weight = owners[position]
            expected[owner] = 1 << weight
        assert result == expected, position
        assert result == expected_values(view, frame), position
    for position, frame, result in zip(positions, zeros, results_zero):
        expected = {s.name: (1 << s.length) - 1 for s in view.signals}
        if position in owners:
            owner, weight = owners[position]
            expected[owner] ^= 1 << weight
        assert result == expected, position
        assert result == expected_values(view, frame), position


# ------------------------------------------------------------- VT-ROUNDTRIP

@pytest.mark.req("LLR-PACK-001", "LLR-PACK-003")
@pytest.mark.parametrize("node,name", TX_CASES)
def test_pack_random_vectors(harnesses, node, name):
    view = harnesses[node].views[name]
    source = rng("pack", name)
    vectors = [random_values(view, source) for _ in range(300)]
    assert harnesses[node].pack(name, vectors) == [expected_frame(view.msg, v) for v in vectors]


@pytest.mark.req("LLR-UNPACK-001", "LLR-UNPACK-002")
@pytest.mark.parametrize("node,name", RX_CASES)
def test_unpack_random_frames(harnesses, node, name):
    view = harnesses[node].views[name]
    source = rng("unpack", name)
    frames = [bytes(source.getrandbits(8) for _ in range(view.msg.dlc)) for _ in range(300)]
    assert harnesses[node].unpack(name, frames) == [expected_values(view, f) for f in frames]


@pytest.mark.req("LLR-PACK-001", "LLR-UNPACK-001")
@pytest.mark.parametrize("name", MESSAGES)
def test_roundtrip_sender_to_receivers(harnesses, name):
    """What the sending node packs is what every receiving node unpacks."""
    msg = message(name)
    sender = harnesses[msg.sender]
    source = rng("roundtrip", name)
    vectors = [random_values(sender.views[name], source) for _ in range(200)]
    frames = sender.pack(name, vectors)
    assert receivers_of(name), "message without receiver in the tested configurations"
    for node in receivers_of(name):
        view = harnesses[node].views[name]
        results = harnesses[node].unpack(name, frames)
        assert results == [{s.name: v[s.name] for s in view.signals} for v in vectors], node


@pytest.mark.req("LLR-PACK-003", "LLR-UNPACK-002")
@pytest.mark.parametrize("name", MESSAGES)
def test_repack_of_unpacked_frame(harnesses, name):
    """pack(unpack(frame)) == frame with all bits outside the signals cleared."""
    msg = message(name)
    source = rng("repack", name)
    frames = [bytes(source.getrandbits(8) for _ in range(msg.dlc)) for _ in range(200)]
    merged = [dict() for _ in frames]
    for node in receivers_of(name):
        for target, result in zip(merged, harnesses[node].unpack(name, frames)):
            target.update(result)
    assert all(set(m) == set(msg.layout) for m in merged), "a signal has no receiver"
    mask = bit_oracle.used_mask(msg.dlc, msg.layout)
    repacked = harnesses[msg.sender].pack(name, merged)
    assert repacked == [bytes(a & b for a, b in zip(frame, mask)) for frame in frames]
