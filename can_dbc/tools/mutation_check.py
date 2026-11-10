#!/usr/bin/env python3
"""Mutation check (VT-MUTATION): verifies the verification suite itself.

Faults are injected one at a time into a copy of the generated code and the
conversion library; the functional verification tests are run against each
mutant. A mutant that the tests do not detect ("survivor") means the suite
has a gap, and makes this check fail.

usage: mutation_check.py [--jobs N] [--per-operator N]
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "build" / "mutation"


def _sub_first(pattern, replacement):
    def apply(line):
        new, count = re.subn(pattern, replacement, line, count=1)
        return new if count else None
    return apply


def _shift(line):
    match = re.search(r"(<<|>>) (\d+)U", line)
    if match is None or "window" not in line:
        return None
    return line[:match.start(2)] + str(int(match.group(2)) + 1) + line[match.end(2):]


def _mask(line):
    match = re.search(r"& 0x([0-9A-F]+)(U|ULL)\)", line)
    if match is None or ("msg->" not in line):
        return None
    return line[:match.start(1)] + f"{int(match.group(1), 16) >> 1:X}" + line[match.end(1):]


def _index(line):
    match = re.search(r"data\[(\d+)\]", line)
    if match is None or "= 0U;" in line:
        return None
    index = int(match.group(1))
    return line[:match.start(1)] + str(index - 1 if index > 0 else index + 1) + line[match.end(1):]


def _delete_clear(line):
    return "" if re.fullmatch(r"\s*data\[\d+\] = 0U;", line) else None


def _db_int(position):
    def apply(line):
        if not line.lstrip().startswith("{"):
            return None
        matches = list(re.finditer(r"\b(0x[0-9A-F]+|\d+)U\b", line))
        if position >= len(matches):
            return None
        match = matches[position]
        value = int(match.group(1), 0) + 1
        text = f"0x{value:X}" if match.group(1).startswith("0x") else str(value)
        return line[:match.start(1)] + text + line[match.end(1):]
    return apply


def _db_float(position):
    def apply(line):
        matches = list(re.finditer(r"(-?\d+\.\d+)F", line))
        if position >= len(matches):
            return None
        match = matches[position]
        return line[:match.start(1)] + repr(float(match.group(1)) * 2.0 + 1.0) + line[match.end(1):]
    return apply


def _db_dir(line):
    if "CAN_DB_DIR_TX" in line:
        return line.replace("CAN_DB_DIR_TX", "CAN_DB_DIR_RX")
    if "CAN_DB_DIR_RX" in line:
        return line.replace("CAN_DB_DIR_RX", "CAN_DB_DIR_TX")
    return None


PACK_UNPACK_OPERATORS = {
    "shift+1": _shift,
    "mask>>1": _mask,
    "byte-index": _index,
    "or-assign->and-assign": _sub_first(r"\|=", "&="),
    "or->and": _sub_first(r"\) \| \(", ") & ("),
    "drop-clear": _delete_clear,
}
DB_OPERATORS = {f"int[{i}]+1": _db_int(i) for i in range(5)}
DB_OPERATORS.update({f"float[{i}]*2+1": _db_float(i) for i in range(4)})
DB_OPERATORS["direction"] = _db_dir

# (text, replacement, occurrence index). Mutants that are equivalent by
# construction (">=" vs ">" at an exactly representable saturation limit)
# are not listed.
CONV_MUTANTS = [
    ("(phys - conv->offset)", "(phys + conv->offset)", 0),
    ("/ conv->factor", "* conv->factor", 0),
    ("raw = conv->raw_max;", "raw = conv->raw_min;", 0),
    ("raw_f >= (float32_t)conv->raw_max", "raw_f <= (float32_t)conv->raw_max", 0),
    ("raw_f > (float32_t)conv->raw_min", "raw_f < (float32_t)conv->raw_min", 0),
    (">= 0.5F", "> 0.5F", 0),
    (">= 0.5F", ">= 0.75F", 0),
    (">= 0.5F", ">= 0.25F", 0),
    ("raw++;", "raw--;", 0),
    ("raw++;", ";", 0),
    ("raw = conv->raw_min;", "raw = conv->raw_max;", 0),
    ("sat > conv->raw_max", "sat < conv->raw_max", 0),
    ("sat = conv->raw_max;", "sat = conv->raw_min;", 0),
    ("sat < conv->raw_min", "sat > conv->raw_min", 0),
    ("sat = conv->raw_min;", "sat = conv->raw_max;", 0),
    ("(float32_t)sat * conv->factor", "(float32_t)raw * conv->factor", 0),
    ("* conv->factor) + conv->offset", "* conv->factor) - conv->offset", 0),
    ("(float32_t)sat * conv->factor", "(float32_t)sat / conv->factor", 0),
]


def line_mutants(path: Path, relative: str, operators, per_operator: int):
    lines = path.read_text().splitlines(keepends=True)
    mutants = []
    for name, operator in operators.items():
        sites = []
        for number, line in enumerate(lines):
            body = line.rstrip("\n")
            mutated = operator(body)
            if mutated is not None and mutated != body:
                sites.append((number, mutated))
        # Deterministic, evenly spread selection of the mutation sites.
        step = max(1, len(sites) // per_operator)
        for number, mutated in sites[::step][:per_operator]:
            new = list(lines)
            new[number] = mutated + "\n" if mutated else ""
            mutants.append((relative, f"{relative}:{number + 1} {name}", "".join(new)))
    return mutants


def conv_mutants(path: Path, relative: str):
    text = path.read_text()
    mutants = []
    for old, new, occurrence in CONV_MUTANTS:
        position = -1
        for _ in range(occurrence + 1):
            position = text.index(old, position + 1)
        mutated = text[:position] + new + text[position + len(old):]
        line = text.count("\n", 0, position) + 1
        mutants.append((relative, f"{relative}:{line} '{old}' -> '{new}'", mutated))
    return mutants


def run_tests(tree: Path) -> bool:
    """True if the functional verification tests pass against `tree`."""
    env = dict(os.environ, CAN_DBC_GENERATED_DIR=str(tree / "generated"),
               CAN_DBC_LIB_DIR=str(tree / "lib"), CAN_DBC_BUILD_DIR=str(tree / "build"),
               CAN_DBC_VARIANT="gcc")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/verification", "-q", "-x",
                             "-m", "functional", "-p", "no:cacheprovider"],
                            cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    parser.add_argument("--per-operator", type=int, default=3,
                        help="mutation sites per operator and file")
    args = parser.parse_args()

    mutants = []
    for source in sorted((ROOT / "generated").glob("*/can_*.c")):
        relative = str(source.relative_to(ROOT))
        operators = DB_OPERATORS if source.name.endswith("_db.c") else PACK_UNPACK_OPERATORS
        mutants += line_mutants(source, relative, operators, args.per_operator)
    mutants += conv_mutants(ROOT / "lib" / "can_conv.c", "lib/can_conv.c")

    shutil.rmtree(WORK, ignore_errors=True)
    trees = []
    for worker in range(args.jobs):
        tree = WORK / f"worker{worker}"
        shutil.copytree(ROOT / "generated", tree / "generated")
        shutil.copytree(ROOT / "lib", tree / "lib")
        trees.append(tree)

    if not run_tests(trees[0]):
        print("mutation check: the unmodified code does not pass; aborting", file=sys.stderr)
        return 1

    def evaluate(job):
        index, (relative, description, content) = job
        tree = trees[index % args.jobs]
        target = tree / relative
        original = target.read_text()
        target.write_text(content)
        try:
            detected = not run_tests(tree)
        finally:
            target.write_text(original)
        return description, detected

    # One worker thread per tree: jobs of a tree run strictly one after another.
    def run_worker(worker):
        return [evaluate(job) for job in list(enumerate(mutants))[worker::args.jobs]]

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = [r for chunk in pool.map(run_worker, range(args.jobs)) for r in chunk]

    survivors = sorted(d for d, detected in results if not detected)
    report = ["# Mutation check", "",
              f"Mutants: {len(results)}, detected: {len(results) - len(survivors)}, "
              f"survivors: {len(survivors)}", ""]
    report += ["| Mutant | Result |", "|---|---|"]
    report += [f"| `{d}` | {'detected' if ok else '**SURVIVED**'} |" for d, ok in sorted(results)]
    out = ROOT / "build" / "report" / "mutation.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[:3]))
    for survivor in survivors:
        print(f"SURVIVED: {survivor}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
