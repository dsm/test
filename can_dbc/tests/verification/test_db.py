"""VT-DB: generated database tables and constants against the cantools model."""

import pytest

from .oracle.conv_oracle import f32_bits, nearest_f32
from .support import NODE_CONFIGS, expected_limits, node_views, snake

pytestmark = pytest.mark.functional
NODES = [node for node, _ in NODE_CONFIGS]
MODE = dict(NODE_CONFIGS)


def up(name):
    return snake(name).upper()


@pytest.mark.req("LLR-DB-001")
@pytest.mark.parametrize("node", NODES)
def test_message_table_content(harnesses, node):
    messages, _ = harnesses[node].dump()
    expected = [{"index": i, "id": v.msg.frame_id, "ext": int(v.msg.is_extended),
                 "dlc": v.msg.dlc, "dir": 0 if v.direction == "TX" else 1,
                 "cycle": v.msg.cycle_time, "count": len(v.signals)}
                for i, v in enumerate(node_views(node, MODE[node]))]
    assert messages == expected


@pytest.mark.req("LLR-DB-002")
@pytest.mark.parametrize("node", NODES)
def test_message_table_sorted_and_unique(harnesses, node):
    ids = [m["id"] for m in harnesses[node].dump()[0]]
    assert ids and all(a < b for a, b in zip(ids, ids[1:]))


@pytest.mark.req("LLR-DB-003")
@pytest.mark.parametrize("node", NODES)
def test_signal_tables_layout_and_scaling(harnesses, node):
    _, signals = harnesses[node].dump()
    views = node_views(node, MODE[node])
    assert sorted(signals) == list(range(len(views)))
    for index, view in enumerate(views):
        got = [(s["start"], s["length"], s["factor"], s["offset"]) for s in signals[index]]
        want = [(s.start, s.length, f32_bits(nearest_f32(s.factor)),
                 f32_bits(nearest_f32(s.offset))) for s in view.signals]
        assert got == want, view.msg.name


@pytest.mark.req("LLR-DB-005")
@pytest.mark.parametrize("node", NODES)
def test_signal_tables_saturation_limits(harnesses, node):
    _, signals = harnesses[node].dump()
    for index, view in enumerate(node_views(node, MODE[node])):
        for sig, entry in zip(view.signals, signals[index]):
            raw_min, raw_max = expected_limits(sig)
            where = f"{view.msg.name}.{sig.name}"
            assert (entry["raw_min"], entry["raw_max"]) == (raw_min, raw_max), where
            assert entry["phys_min"] == f32_bits(nearest_f32(raw_min * sig.factor + sig.offset)), where
            assert entry["phys_max"] == f32_bits(nearest_f32(raw_max * sig.factor + sig.offset)), where
            if sig.length > 32:
                assert (sig.factor, sig.offset, raw_min, raw_max) == (1, 0, 0, 0xFFFFFFFF), where


@pytest.mark.req("LLR-DB-004")
@pytest.mark.parametrize("node", NODES)
def test_index_enumerations_match_table_positions(harnesses, node):
    constants = harnesses[node].constants()
    views = node_views(node, MODE[node])
    assert constants[f"CAN_{up(node)}_MSG_COUNT"] == len(views)
    for index, view in enumerate(views):
        msg_index = f"CAN_{up(node)}_MSG_{up(view.msg.name)}"
        assert constants[msg_index] == index
        assert constants[f"{msg_index}.signals_ok"] == 1
        assert constants[f"CAN_{up(view.msg.name)}_SIG_COUNT"] == len(view.signals)
        for position, sig in enumerate(view.signals):
            assert constants[f"CAN_{up(view.msg.name)}_SIG_{up(sig.name)}"] == position


@pytest.mark.req("LLR-IF-002")
@pytest.mark.parametrize("node", NODES)
def test_message_constants_and_value_tables(harnesses, node):
    constants = harnesses[node].constants()
    for view in node_views(node, MODE[node]):
        prefix = f"CAN_{up(view.msg.name)}"
        assert constants[f"{prefix}_FRAME_ID"] == view.msg.frame_id
        assert constants[f"{prefix}_IS_EXTENDED"] == int(view.msg.is_extended)
        assert constants[f"{prefix}_DLC"] == view.msg.dlc
        assert constants[f"{prefix}_CYCLE_TIME_MS"] == view.msg.cycle_time
        for sig in view.signals:
            for value, text in sig.choices:
                assert constants[f"{prefix}_{up(sig.name)}_{up(text)}"] == value


@pytest.mark.req("LLR-IF-001")
@pytest.mark.parametrize("node", NODES)
def test_structure_member_types(harnesses, node):
    """Each member is the smallest of uint8/16/32/64_t that holds the signal."""
    constants = harnesses[node].constants()
    for view in node_views(node, MODE[node]):
        for sig in view.signals:
            key = f"sizeof.can_{snake(view.msg.name)}_t.{snake(sig.name)}"
            assert constants[key] * 8 == sig.field_bits, key
