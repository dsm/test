"""VT-GEN: generator rejection rules, determinism and parser equivalence."""

import hashlib
import re
import sys

import pytest

from .support import DBC, GENERATED, GENERATOR, NODE_CONFIGS, model, run_generator

SPECS = [node if mode == "both" else f"{node}:{mode}" for node, mode in NODE_CONFIGS]
EXAMPLE = DBC.read_text(encoding="utf-8")


def mutate(old, new):
    assert EXAMPLE.count(old) == 1, f"pattern not unique: {old}"
    return EXAMPLE.replace(old, new)


# name -> (modified DBC text, expected error code)
UNSUPPORTED = {
    "intel_byte_order": (mutate("SG_ Soc : 27|10@0+", "SG_ Soc : 27|10@1+"), "E002"),
    "signed_signal": (mutate("SG_ Soc : 27|10@0+", "SG_ Soc : 27|10@0-"), "E003"),
    "multiplexer": (mutate("SG_ State : 33|3@0+", "SG_ State M : 33|3@0+"), "E004"),
    "multiplexed_signal": (mutate("SG_ Soc : 27|10@0+", "SG_ Soc m1 : 27|10@0+"), "E004"),
    "extended_multiplexing": (EXAMPLE + "\nSG_MUL_VAL_ 512 Soc State 1-1;\n", "E004"),
    "float_signal": (EXAMPLE + "\nSIG_VALTYPE_ 784 ErrorFlags : 1;\n", "E005"),
    "can_fd_dlc": (mutate("BO_ 512 BMS_Status: 8 BMS", "BO_ 512 BMS_Status: 12 BMS"), "E010"),
    "zero_dlc": (mutate("BO_ 16 VCU_Heartbeat: 3 VCU", "BO_ 16 VCU_Heartbeat: 0 VCU"), "E010"),
    "unknown_statement": (EXAMPLE + "\nFOO_ 1 2 3;\n", "E001"),
    "malformed_signal": (mutate("SG_ Soc : 27|10@0+", "SG_ Soc : 27-10@0+"), "E001"),
}

INCONSISTENT = {
    "overlapping_signals": (mutate("SG_ Soc : 27|10@0+", "SG_ Soc : 28|10@0+"), "E006"),
    "signal_beyond_dlc": (mutate("SG_ SwVersion : 11|12@0+", "SG_ SwVersion : 11|13@0+"), "E007"),
    "start_bit_beyond_frame": (mutate("SG_ CmdCounter : 59|4@0+", "SG_ CmdCounter : 67|4@0+"), "E007"),
    "zero_length": (mutate("SG_ LimpMode : 46|1@0+", "SG_ LimpMode : 46|0@0+"), "E012"),
    "length_over_64": (mutate("SG_ EnergyCounter : 7|40@0+", "SG_ EnergyCounter : 7|65@0+"), "E012"),
    "zero_factor": (mutate("27|10@0+ (0.1,0)", "27|10@0+ (0,0)"), "E011"),
    "negative_factor": (mutate("27|10@0+ (0.1,0)", "27|10@0+ (-0.1,0)"), "E011"),
    "scaled_wide_signal": (mutate("7|40@0+ (1,0)", "7|40@0+ (0.5,0)"), "E011"),
    "empty_range": (mutate("(0.1,0) [0|100]", "(0.1,0) [200|100]"), "E013"),
    "duplicate_signal_name": (mutate("SG_ Soc :", "SG_ PackVoltage :"), "E008"),
    "keyword_signal_name": (mutate("SG_ Soc :", "SG_ int :"), "E008"),
    "duplicate_message_name": (mutate("BO_ 784 MCU_Diag:", "BO_ 784 MCU_Status:"), "E008"),
    "duplicate_value_name": (mutate('4 "Sport"', '4 "Drive"'), "E008"),
    "unknown_receiver": (mutate('"Nm" VCU', '"Nm" GATEWAY'), "E009"),
    "unknown_sender": (mutate("BO_ 784 MCU_Diag: 6 MCU", "BO_ 784 MCU_Diag: 6 GATEWAY"), "E009"),
    "standard_id_out_of_range": (mutate("BO_ 784 MCU_Diag:", "BO_ 4096 MCU_Diag:"), "E014"),
    "duplicate_frame_id": (mutate("BO_ 784 MCU_Diag:", "BO_ 768 MCU_Diag:"), "E001"),
    "message_without_signals": (EXAMPLE.replace("BS_:", "BS_:\n\nBO_ 99 Empty: 1 VCU\n", 1), "E015"),
}


def expect_rejection(tmp_path, text, code, specs=None):
    dbc = tmp_path / "bad.dbc"
    dbc.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = run_generator(dbc, out, specs or SPECS)
    assert result.returncode == 2, result.stdout + result.stderr
    assert f"error[{code}]" in result.stderr, result.stderr
    assert list(out.iterdir()) == [], "files were written despite the error"


@pytest.mark.req("LLR-GEN-001")
@pytest.mark.parametrize("case", sorted(UNSUPPORTED))
def test_unsupported_content_is_rejected(tmp_path, case):
    expect_rejection(tmp_path, *UNSUPPORTED[case])


@pytest.mark.req("LLR-GEN-002")
@pytest.mark.parametrize("case", sorted(INCONSISTENT))
def test_inconsistent_content_is_rejected(tmp_path, case):
    expect_rejection(tmp_path, *INCONSISTENT[case])


@pytest.mark.req("LLR-GEN-002")
@pytest.mark.parametrize("specs,code", [(["GATEWAY"], "E009"), (["VCU", "BMS:both"], "E009"),
                                        (["VCU", "VCU:rx"], "E009"), (["VCU", "NOPE:rx"], "E009")])
def test_invalid_node_selection_is_rejected(tmp_path, specs, code):
    expect_rejection(tmp_path, EXAMPLE, code, specs)


@pytest.mark.req("LLR-GEN-001", "LLR-GEN-002")
def test_unmodified_example_is_accepted(tmp_path):
    """Control for the rejection tests: the baseline they are derived from is valid."""
    assert run_generator(DBC, tmp_path, SPECS).returncode == 0


def tree(directory):
    return {str(p.relative_to(directory)): p.read_bytes()
            for p in sorted(directory.rglob("*")) if p.is_file()}


@pytest.mark.req("LLR-GEN-003")
def test_generation_is_deterministic_and_committed_code_is_current(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    assert run_generator(DBC, first, SPECS).returncode == 0
    assert run_generator(DBC, second, list(reversed(SPECS))).returncode == 0
    assert tree(first) == tree(second)
    assert len(tree(first)) == 4 * len(SPECS)
    assert tree(first) == tree(GENERATED), "generated/ is not up to date with the DBC/generator"


@pytest.mark.req("LLR-GEN-003")
def test_generated_files_identify_their_source(tmp_path):
    sys.path.insert(0, str(GENERATOR))
    try:
        from dbcgen import __version__
    finally:
        sys.path.remove(str(GENERATOR))
    digest = hashlib.sha256(DBC.read_bytes()).hexdigest()
    files = tree(GENERATED)
    assert files
    for name, content in files.items():
        text = content.decode("ascii")
        assert "GENERATED FILE - DO NOT EDIT." in text, name
        assert f"SHA-256   : {digest}" in text, name
        assert f"Generator : dbcgen {__version__}" in text, name
        assert f"Source    : {DBC.name}" in text, name
        assert not re.search(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}", text), f"{name}: time stamp"


@pytest.mark.req("LLR-GEN-004")
def test_parser_model_equals_cantools_model():
    sys.path.insert(0, str(GENERATOR))
    try:
        from dbcgen.dbc_parser import parse_dbc
    finally:
        sys.path.remove(str(GENERATOR))
    parsed = parse_dbc(EXAMPLE)
    assert parsed.nodes == ("VCU", "BMS", "MCU", "DISPLAY")
    reference = model()
    assert [m.name for m in parsed.messages] == [m.name for m in reference]
    for own, ref in zip(parsed.messages, reference):
        assert (own.frame_id, own.is_extended, own.dlc, own.sender, own.cycle_time_ms) == \
            (ref.frame_id, ref.is_extended, ref.dlc, ref.sender, ref.cycle_time), ref.name
        assert sorted(s.name for s in own.signals) == sorted(s.name for s in ref.signals)
        for sig in own.signals:
            other = ref.signal(sig.name)
            where = f"{ref.name}.{sig.name}"
            assert (sig.start, sig.length, sig.byte_order, sig.sign) == \
                (other.start, other.length, "0", "+"), where
            assert (sig.factor, sig.offset) == (other.factor, other.offset), where
            if other.minimum is None:
                assert (sig.minimum, sig.maximum) == (0, 0), where
            else:
                assert (sig.minimum, sig.maximum) == (other.minimum, other.maximum), where
            assert sig.receivers == other.receivers, where
            assert sig.choices == other.choices, where
            assert sig.mux is None and not sig.is_float, where
