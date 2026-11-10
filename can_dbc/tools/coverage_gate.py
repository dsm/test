#!/usr/bin/env python3
"""Structural coverage gate (VT-COVERAGE).

Reads the gcov data produced by running the functional verification tests
against the coverage build (CAN_DBC_VARIANT=cov) and requires 100 % line
and 100 % branch coverage for the generated code and the conversion
library. Decisions in this code base have a single condition each, so
branch coverage is equivalent to MC/DC.

usage: coverage_gate.py <build dir> <report file>
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path


def gcov_file(obj_dir: Path, name: str):
    """Per-line execution and per-branch taken flags of one source file.

    Returns (lines, branches): lines maps line number -> executed, branches
    maps (line number, branch index) -> taken; None if there is no data.
    """
    with tempfile.TemporaryDirectory() as work:
        subprocess.run(["gcov", "-b", "-c", "-o", str(obj_dir), name],
                       capture_output=True, text=True, cwd=work, check=False)
        listing = Path(work) / (name + ".gcov")
        if not listing.exists():
            return None
        text = listing.read_text()
    lines, branches = {}, {}
    current = 0
    for row in text.splitlines():
        match = re.match(r"\s*([^:]+):\s*(\d+):", row)
        if match:
            count, current = match.group(1).strip(), int(match.group(2))
            if current > 0 and count != "-":
                lines[current] = count not in ("#####", "=====")
            continue
        match = re.match(r"branch\s+(\d+)\s+(taken (\d+)|never executed)", row)
        if match:
            branches[(current, int(match.group(1)))] = bool(match.group(3)) and int(match.group(3)) > 0
    return lines, branches


def main() -> int:
    build, report = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    node_dirs = sorted(d for d in (build / "cov").glob("*") if d.is_dir())
    if not node_dirs:
        print("coverage gate: no coverage build found", file=sys.stderr)
        return 1

    # The conversion library is linked into every node build; its coverage is
    # the union over all builds. Generated files exist in one build each.
    merged = {}
    for node_dir in node_dirs:
        node = node_dir.name
        for name in (f"can_{node}.c", f"can_{node}_db.c", "can_conv.c"):
            data = gcov_file(node_dir, name)
            lines, branches = merged.setdefault(name, ({}, {}))
            if data is None:
                continue
            for key, hit in data[0].items():
                lines[key] = lines.get(key, False) or hit
            for key, hit in data[1].items():
                branches[key] = branches.get(key, False) or hit

    rows, ok = [], True
    for name in sorted(merged):
        lines, branches = merged[name]
        table_only = name.endswith("_db.c")
        passed = all(lines.values()) and all(branches.values()) and (bool(lines) or table_only)
        ok = ok and passed
        rows.append((name, f"{sum(lines.values())}/{len(lines)}",
                     f"{sum(branches.values())}/{len(branches)}",
                     "PASS" if passed else "FAIL"))
    out = ["# Structural coverage (gcov, from the functional verification tests)", "",
           "Decisions have a single condition each, so branch coverage equals MC/DC.",
           "`*_db.c` files contain constant tables only (no executable code).", "",
           "| File | Lines executed | Branches taken | Result |", "|---|---|---|---|"]
    out += [f"| {' | '.join(row)} |" for row in rows]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
