#!/usr/bin/env python3
"""Runs the complete verification campaign and writes the verification report.

Steps:
  1. complete suite with the reference build (gcc)
  2. functional tests with clang, with ASan/UBSan and on a big-endian target
  3. structural coverage from the functional tests + coverage gate
  4. mutation check (only with --mutation)

A step whose tools are not installed is reported as NOT RUN, never as passed.
Results: build/report/verification_report.md (+ JUnit XML, trace matrices).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "build" / "report"
TOOLS = {"clang": ["clang"], "asan": ["gcc"],
         "ppc": ["powerpc-linux-gnu-gcc", "qemu-ppc-static"], "cov": ["gcc", "gcov"]}
TITLES = {"clang": "Functional tests, clang build",
          "asan": "Functional tests, AddressSanitizer + UndefinedBehaviorSanitizer",
          "ppc": "Functional tests, big-endian target (PowerPC, qemu)",
          "cov": "Functional tests, coverage build"}


def pytest(variant: str, functional_only: bool):
    command = [sys.executable, "-m", "pytest", "tests/verification", "-q",
               f"--junitxml={REPORT / f'junit_{variant}.xml'}"]
    if functional_only:
        command += ["-m", "functional"]
    result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, CAN_DBC_VARIANT=variant),
                            capture_output=True, text=True, check=False)
    tail = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    if result.returncode != 0:
        print(result.stdout[-6000:])
    status = "PASS" if result.returncode == 0 else "FAIL"
    if status == "PASS" and "skipped" in tail:
        status = "PASS (some tests NOT RUN)"
    return status, tail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutation", action="store_true", help="also run the mutation check")
    args = parser.parse_args()
    REPORT.mkdir(parents=True, exist_ok=True)
    rows = []

    rows.append(("Complete suite, reference build (gcc)",) + pytest("gcc", False))

    for variant in ("clang", "asan", "ppc"):
        missing = [t for t in TOOLS[variant] if shutil.which(t) is None]
        if missing:
            rows.append((TITLES[variant], "NOT RUN", f"not installed: {', '.join(missing)}"))
        else:
            rows.append((TITLES[variant],) + pytest(variant, True))

    missing = [t for t in TOOLS["cov"] if shutil.which(t) is None]
    if missing:
        rows.append(("Structural coverage gate", "NOT RUN", f"not installed: {', '.join(missing)}"))
    else:
        shutil.rmtree(ROOT / "build" / "cov", ignore_errors=True)
        rows.append((TITLES["cov"],) + pytest("cov", True))
        gate = subprocess.run([sys.executable, "tools/coverage_gate.py", "build",
                               str(REPORT / "coverage.md")], cwd=ROOT,
                              capture_output=True, text=True, check=False)
        rows.append(("Structural coverage gate (100 % lines and branches)",
                     "PASS" if gate.returncode == 0 else "FAIL", "see coverage.md"))

    if args.mutation:
        mutation = subprocess.run([sys.executable, "tools/mutation_check.py"], cwd=ROOT,
                                  capture_output=True, text=True, check=False)
        summary = [l for l in mutation.stdout.splitlines() if l.startswith("Mutants:")]
        rows.append(("Mutation check", "PASS" if mutation.returncode == 0 else "FAIL",
                     summary[0] if summary else mutation.stderr.strip()[-200:]))
    else:
        rows.append(("Mutation check", "NOT RUN", "run with --mutation / make mutation"))

    lines = ["# Verification report", "", "| Step | Result | Details |", "|---|---|---|"]
    lines += [f"| {title} | {status} | {detail} |" for title, status, detail in rows]
    lines += ["", "Requirement traceability: `trace_matrix_<variant>.md`, "
              "coverage: `coverage.md`, mutants: `mutation.md`."]
    (REPORT / "verification_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if any(status == "FAIL" for _, status, _ in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
