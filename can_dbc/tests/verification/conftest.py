"""pytest configuration: harness fixtures and requirement traceability."""

import re
from collections import defaultdict

import pytest

from .support import BUILD, NODE_CONFIGS, ROOT, VARIANT, ToolMissing, build_harness

REQUIREMENTS = ROOT / "docs" / "requirements.md"
_outcomes = {}
_requirements_of = {}


def requirement_ids():
    text = REQUIREMENTS.read_text(encoding="utf-8")
    return sorted(set(re.findall(r"^\| (LLR-[A-Z]+-\d{3}) \|", text, flags=re.MULTILINE)))


def pytest_configure(config):
    config.addinivalue_line("markers", "req(*ids): low-level requirements verified by the test")
    config.addinivalue_line("markers", "functional: executes the code under test (run in "
                                       "every build variant, used for coverage and mutation)")


@pytest.fixture(scope="session")
def harnesses():
    """Test executables of all committed node configurations, by node name."""
    try:
        return {node: build_harness(node, mode) for node, mode in NODE_CONFIGS}
    except ToolMissing as missing:
        pytest.skip(f"NOT RUN: {missing}")


def pytest_collection_modifyitems(items):
    for item in items:
        ids = [i for mark in item.iter_markers("req") for i in mark.args]
        _requirements_of[item.nodeid] = ids


def pytest_runtest_logreport(report):
    if report.when == "call" or report.outcome != "passed":
        previous = _outcomes.get(report.nodeid)
        if previous != "failed":
            _outcomes[report.nodeid] = report.outcome


def pytest_sessionfinish(session):
    """Write the requirement <-> test traceability matrix of this run."""
    by_requirement = defaultdict(list)
    for nodeid, ids in _requirements_of.items():
        for req in ids:
            by_requirement[req].append(nodeid)
    lines = [f"# Traceability matrix (variant: {VARIANT})", "",
             "| Requirement | Result | Tests (passed/failed/not run) |", "|---|---|---|"]
    for req in requirement_ids():
        tests = by_requirement.get(req, [])
        outcomes = [_outcomes.get(t, "skipped") for t in tests]
        passed, failed = outcomes.count("passed"), outcomes.count("failed")
        not_run = len(outcomes) - passed - failed
        if failed:
            result = "FAIL"
        elif passed and not not_run:
            result = "PASS"
        elif passed:
            result = "PASS (partly NOT RUN)"
        else:
            result = "NOT RUN"
        lines.append(f"| {req} | {result} | {passed}/{failed}/{not_run} |")
    lines += ["", "## Tests per requirement", ""]
    for req in requirement_ids():
        lines.append(f"### {req}")
        for test in sorted({t.split('[')[0] for t in by_requirement.get(req, [])}):
            lines.append(f"- `{test}`")
        lines.append("")
    report_dir = BUILD / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"trace_matrix_{VARIANT}.md").write_text("\n".join(lines), encoding="utf-8")
