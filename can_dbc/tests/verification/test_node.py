"""VT-NODE: node and direction selection (which code exists for which node)."""

import re
import subprocess

import pytest

from .checks import check_node_against_oracles
from .support import (BUILD, DBC, GENERATED, NODE_CONFIGS, ToolMissing, build_harness,
                      compile_objects, node_views, run_generator, snake)

# Committed configurations plus direction-restricted variants generated on the fly.
EXTRA_CONFIGS = (("BMS", "rx"), ("MCU", "tx"), ("VCU", "tx"), ("VCU", "rx"), ("DISPLAY", "both"))
ALL_CONFIGS = [(n, m, "committed") for n, m in NODE_CONFIGS] + \
              [(n, m, "generated") for n, m in EXTRA_CONFIGS]


@pytest.fixture(scope="module")
def generated_dirs(tmp_path_factory):
    """Maps (node, mode) to the directory holding the generated code."""
    dirs = {(n, m): GENERATED for n, m in NODE_CONFIGS}
    for node, mode in EXTRA_CONFIGS:
        out = tmp_path_factory.mktemp(f"{node}_{mode}")
        spec = node if mode == "both" else f"{node}:{mode}"
        result = run_generator(DBC, out, [spec])
        assert result.returncode == 0, result.stderr
        dirs[(node, mode)] = out
    return dirs


def defined_symbols(objects):
    """name -> symbol type letter for all external definitions."""
    output = subprocess.run(["nm", "-g", "--defined-only"] + [str(o) for o in objects],
                            capture_output=True, text=True, check=True).stdout
    return {parts[2]: parts[1] for parts in (line.split() for line in output.splitlines())
            if len(parts) == 3}


def structure_members(header_text, type_name):
    body = re.search(r"typedef struct\s*\{([^}]*)\}\s*" + type_name + ";", header_text)
    assert body is not None, type_name
    return re.findall(r"^\s*(uint\d+_t)\s+(\w+);", body.group(1), flags=re.MULTILINE)


@pytest.mark.req("LLR-NODE-001", "LLR-NODE-002", "LLR-NODE-003")
@pytest.mark.parametrize("node,mode,origin", ALL_CONFIGS)
def test_exactly_the_expected_symbols_exist(generated_dirs, node, mode, origin):
    """pack only for TX, unpack only for RX, nothing for unrelated messages."""
    low = snake(node)
    try:
        objects = compile_objects(node, generated_dirs[(node, mode)],
                                  BUILD / "symbols" / f"{low}_{mode}", "gcc")
    except ToolMissing as missing:
        pytest.skip(f"NOT RUN: {missing}")
    symbols = defined_symbols(objects[:2])          # generated objects only
    views = node_views(node, mode)
    # "T": function, "R"/"D": constant table (tables holding pointers may be
    # placed in a relocatable read-only data section, shown as "D").
    expected = {f"can_{low}_messages": "RD"}
    for view in views:
        base = f"can_{snake(view.msg.name)}"
        expected[f"{base}_signals"] = "R"
        expected[f"{base}_{'pack' if view.direction == 'TX' else 'unpack'}"] = "T"
    assert sorted(symbols) == sorted(expected)
    for name, kind in symbols.items():
        assert kind in expected[name], name
    directions = {v.direction for v in views}
    assert directions <= {"both": {"TX", "RX"}, "tx": {"TX"}, "rx": {"RX"}}[mode]


@pytest.mark.req("LLR-NODE-002", "LLR-IF-001")
@pytest.mark.parametrize("node,mode,origin", ALL_CONFIGS)
def test_structures_contain_exactly_the_selected_signals(generated_dirs, node, mode, origin):
    low = snake(node)
    header = (generated_dirs[(node, mode)] / low / f"can_{low}.h").read_text()
    views = node_views(node, mode)
    for view in views:
        members = structure_members(header, f"can_{snake(view.msg.name)}_t")
        assert members == [(f"uint{s.field_bits}_t", snake(s.name)) for s in view.signals]
        if view.direction == "TX":
            assert len(view.signals) == len(view.msg.signals)
        else:
            assert all(node in s.receivers for s in view.signals)
    assert len(re.findall(r"typedef struct", header)) == len(views)


@pytest.mark.req("LLR-NODE-003", "LLR-PACK-001", "LLR-UNPACK-001")
@pytest.mark.parametrize("node,mode", EXTRA_CONFIGS)
def test_direction_restricted_variants_behave_correctly(generated_dirs, node, mode):
    try:
        harness = build_harness(node, mode, generated_dirs[(node, mode)], tag=f"_{mode}")
    except ToolMissing as missing:
        pytest.skip(f"NOT RUN: {missing}")
    check_node_against_oracles(harness)


@pytest.mark.req("LLR-NODE-003")
def test_node_without_messages_in_requested_direction_is_rejected(tmp_path):
    result = run_generator(DBC, tmp_path, ["DISPLAY:tx"])
    assert result.returncode == 2 and "error[E015]" in result.stderr
    assert list(tmp_path.iterdir()) == []
