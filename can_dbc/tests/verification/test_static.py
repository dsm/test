"""VT-STATIC and VT-ENDIAN: coding rules, static analysis, big-endian execution."""

import re
import shutil
import subprocess

import pytest

from .checks import check_node_against_oracles
from .support import (BUILD, GENERATED, LIB, NODE_CONFIGS, ToolMissing, build_harness,
                      compile_objects, snake)
from .test_pack_unpack import GOLDEN

NODES = [node for node, _ in NODE_CONFIGS]


def strip_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)


def pack_unpack_sources():
    return [GENERATED / snake(n) / f"can_{snake(n)}.c" for n in NODES]


def all_sources():
    files = [LIB / "can_conv.c", LIB / "can_conv.h", LIB / "can_db_types.h"]
    for node in NODES:
        files += sorted((GENERATED / snake(node)).glob("can_*.[ch]"))
    return files


@pytest.mark.req("LLR-CODE-001")
@pytest.mark.parametrize("compiler", ["gcc", "clang"])
@pytest.mark.parametrize("node", NODES)
def test_compiles_without_warnings_as_c99(node, compiler):
    try:
        compile_objects(node, GENERATED, BUILD / f"strict_{compiler}" / snake(node), compiler)
    except ToolMissing as missing:
        pytest.skip(f"NOT RUN: {missing}")


@pytest.mark.req("LLR-CODE-001")
def test_static_analysis_reports_no_findings():
    if shutil.which("cppcheck") is None:
        pytest.skip("NOT RUN: cppcheck not installed")
    command = ["cppcheck", "--std=c99", "--enable=warning,portability,performance",
               "--inline-suppr", "--error-exitcode=1", "--quiet", "-I", str(LIB)]
    for node in NODES:
        command += ["-I", str(GENERATED / snake(node))]
    command += [str(f) for f in all_sources() if f.suffix == ".c"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0 and result.stderr.strip() == "", result.stderr


# Advisory rules that necessarily fire when a library is analysed without the
# application using it: unused type/tag/macro (2.3, 2.4, 2.5) and external
# tables referenced from one translation unit only (8.7).
MISRA_LIBRARY_ADVISORIES = {"2.3", "2.4", "2.5", "8.7"}


@pytest.mark.req("LLR-CODE-001")
@pytest.mark.parametrize("node", NODES)
def test_misra_checker_reports_only_library_advisories(node):
    """cppcheck MISRA C:2012 addon (the subset of rules it implements)."""
    if shutil.which("cppcheck") is None:
        pytest.skip("NOT RUN: cppcheck not installed")
    low = snake(node)
    command = ["cppcheck", "--addon=misra", "--enable=style", "--std=c99", "--quiet",
               "-I", str(LIB), "-I", str(GENERATED / low),
               str(GENERATED / low / f"can_{low}.c"), str(GENERATED / low / f"can_{low}_db.c"),
               str(LIB / "can_conv.c")]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    findings = re.findall(r"^(\S+?):(\d+):\d+: (\w+): .*\[([\w.-]+)\]$", result.stderr,
                          flags=re.MULTILINE)
    assert findings, "checker produced no output at all: addon not active?"
    unexpected = [f for f in findings
                  if not (f[3].startswith("misra-c2012-")
                          and f[3].split("-")[-1] in MISRA_LIBRARY_ADVISORIES)]
    assert unexpected == []


@pytest.mark.req("LLR-CODE-003")
@pytest.mark.parametrize("source", pack_unpack_sources(), ids=lambda p: p.name)
def test_pack_unpack_is_straight_line_code(source):
    code = strip_comments(source.read_text())
    for keyword in ("if", "else", "switch", "case", "for", "while", "do", "goto"):
        assert not re.search(rf"\b{keyword}\b", code), keyword
    assert "?" not in code and "&&" not in code and "||" not in code
    bodies = re.findall(r"\)\n\{\n(.*?)\n\}", code, flags=re.DOTALL)
    assert bodies, "no function bodies found"
    for body in bodies:
        calls = re.findall(r"\b([A-Za-z_]\w*)\s*\(", body)
        assert calls == [], f"function call in pack/unpack: {calls}"


@pytest.mark.req("LLR-CODE-002")
@pytest.mark.parametrize("source", all_sources(), ids=lambda p: f"{p.parent.name}/{p.name}")
def test_no_endianness_dependent_constructs(source):
    code = strip_comments(source.read_text())
    assert not re.search(r"\bunion\b", code)
    assert not re.search(r"\bmem(cpy|move|set)\b", code)
    assert not re.search(r"^\s*\w[\w\s]*\s+\w+\s*:\s*\d+\s*;", code, flags=re.MULTILINE), "bitfield"
    assert not re.search(r"\(\s*(const\s+)?\w+\s*\*+\s*\)", code), "pointer cast"
    assert "#include <string.h>" not in code


@pytest.mark.req("LLR-CODE-002", "LLR-PACK-001", "LLR-UNPACK-001")
def test_big_endian_target_execution():
    """Golden vectors and random vectors on a big-endian CPU (PowerPC under qemu)."""
    try:
        harnesses = {node: build_harness(node, mode, variant="ppc") for node, mode in NODE_CONFIGS}
    except ToolMissing as missing:
        pytest.skip(f"NOT RUN: {missing}")
    for harness in harnesses.values():
        check_node_against_oracles(harness)
        for name, view in harness.views.items():
            values, payload = GOLDEN[name]
            if view.direction == "TX":
                assert harness.pack(name, [values]) == [bytes.fromhex(payload)]
            else:
                assert harness.unpack(name, [bytes.fromhex(payload)]) == \
                    [{s.name: values[s.name] for s in view.signals}]
