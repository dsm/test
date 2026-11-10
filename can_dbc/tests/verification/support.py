"""Verification environment: expected model, harness build and control.

The expected model is read with cantools (third-party parser), never with
the generator under test. Naming and selection rules are re-implemented here
from the requirements (docs/requirements.md).
"""

import functools
import math
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cantools

from .oracle import bit_oracle

ROOT = Path(__file__).resolve().parents[2]
DBC = ROOT / "dbc" / "example_vehicle.dbc"
GENERATOR = ROOT / "generator"
GENERATED = Path(os.environ.get("CAN_DBC_GENERATED_DIR", ROOT / "generated"))
LIB = Path(os.environ.get("CAN_DBC_LIB_DIR", ROOT / "lib"))
BUILD = Path(os.environ.get("CAN_DBC_BUILD_DIR", ROOT / "build"))
VARIANT = os.environ.get("CAN_DBC_VARIANT", "gcc")

# Node configurations of the committed generated code.
NODE_CONFIGS = (("VCU", "both"), ("BMS", "both"), ("MCU", "both"), ("DISPLAY", "rx"))

STRICT_FLAGS = ["-std=c99", "-pedantic", "-Wall", "-Wextra", "-Wconversion",
                "-Wsign-conversion", "-Wshadow", "-Wcast-qual", "-Wstrict-prototypes",
                "-Wmissing-prototypes", "-Werror", "-ffp-contract=off"]

VARIANTS = {
    "gcc": {"cc": "gcc", "flags": ["-O2"], "runner": []},
    "clang": {"cc": "clang", "flags": ["-O2"], "runner": []},
    "asan": {"cc": "gcc", "runner": [],
             "flags": ["-O1", "-g", "-fsanitize=address,undefined,float-cast-overflow",
                       "-fno-sanitize-recover=all"]},
    "cov": {"cc": "gcc", "flags": ["-O0", "--coverage"], "runner": []},
    "ppc": {"cc": "powerpc-linux-gnu-gcc", "flags": ["-O2", "-static"],
            "runner": ["qemu-ppc-static"]},
}


class ToolMissing(Exception):
    """A tool of the selected build variant is not installed."""


def snake(name: str) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()


@dataclass(frozen=True)
class Sig:
    name: str
    start: int
    length: int
    factor: Fraction
    offset: Fraction
    minimum: Optional[Fraction]
    maximum: Optional[Fraction]
    receivers: Tuple[str, ...]
    choices: Tuple[Tuple[int, str], ...]

    @property
    def field_bits(self) -> int:
        return next(b for b in (8, 16, 32, 64) if self.length <= b)


@dataclass(frozen=True)
class Msg:
    name: str
    frame_id: int
    is_extended: bool
    dlc: int
    sender: str
    cycle_time: int
    signals: Tuple[Sig, ...]

    @property
    def layout(self) -> Dict[str, Tuple[int, int]]:
        return {s.name: (s.start, s.length) for s in self.signals}

    def signal(self, name: str) -> Sig:
        return next(s for s in self.signals if s.name == name)


@dataclass(frozen=True)
class View:
    """A message as seen by one node."""
    msg: Msg
    direction: str              # "TX" / "RX"
    signals: Tuple[Sig, ...]    # frame order

    @property
    def layout(self) -> Dict[str, Tuple[int, int]]:
        return {s.name: (s.start, s.length) for s in self.signals}


def _fraction(value) -> Optional[Fraction]:
    return None if value is None else Fraction(repr(value))


@functools.lru_cache(maxsize=None)
def cantools_db():
    return cantools.database.load_file(str(DBC))


@functools.lru_cache(maxsize=None)
def model() -> Tuple[Msg, ...]:
    messages = []
    for ct in cantools_db().messages:
        signals = []
        for s in ct.signals:
            assert s.byte_order == "big_endian" and not s.is_signed
            choices = tuple((int(v), str(t)) for v, t in (s.choices or {}).items())
            signals.append(Sig(s.name, s.start, s.length, _fraction(s.conversion.scale),
                               _fraction(s.conversion.offset), _fraction(s.minimum),
                               _fraction(s.maximum), tuple(s.receivers), choices))
        assert len(ct.senders) == 1
        messages.append(Msg(ct.name, ct.frame_id, ct.is_extended_frame, ct.length,
                            ct.senders[0], ct.cycle_time or 0, tuple(signals)))
    return tuple(messages)


def message(name: str) -> Msg:
    return next(m for m in model() if m.name == name)


def _frame_order(signals) -> Tuple[Sig, ...]:
    def key(sig):
        byte, bit = bit_oracle.signal_bits(sig.start, sig.length)[0]
        return (byte, -bit)
    return tuple(sorted(signals, key=key))


def node_views(node: str, mode: str) -> List[View]:
    """Expected content for a node: LLR-NODE-001/002/003, LLR-DB-002."""
    views = []
    for msg in model():
        if msg.sender == node:
            if mode in ("both", "tx"):
                views.append(View(msg, "TX", _frame_order(msg.signals)))
        elif mode in ("both", "rx"):
            received = [s for s in msg.signals if node in s.receivers]
            if received:
                views.append(View(msg, "RX", _frame_order(received)))
    return sorted(views, key=lambda v: v.msg.frame_id)


def expected_limits(sig: Sig) -> Tuple[int, int]:
    """Raw saturation limits required by LLR-DB-005."""
    full = (1 << sig.length) - 1
    if sig.minimum is None and sig.maximum is None:
        low, high = 0, full
    else:
        low = max(0, math.ceil((sig.minimum - sig.offset) / sig.factor))
        high = min(full, math.floor((sig.maximum - sig.offset) / sig.factor))
    return min(low, 0xFFFFFFFF), min(high, 0xFFFFFFFF)


def cantools_encode(msg: Msg, values: Dict[str, int]) -> bytes:
    ct = cantools_db().get_message_by_name(msg.name)
    return bytes(ct.encode(values, scaling=False, padding=False, strict=False))


def cantools_decode(msg: Msg, data: bytes) -> Dict[str, int]:
    ct = cantools_db().get_message_by_name(msg.name)
    return dict(ct.decode(data, decode_choices=False, scaling=False))


# --------------------------------------------------------------------------
# Generator invocation and harness build
# --------------------------------------------------------------------------

def run_generator(dbc: Path, out: Path, specs: List[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONPATH=str(GENERATOR))
    command = ["python3", "-m", "dbcgen", "--dbc", str(dbc), "--out", str(out)]
    for spec in specs:
        command += ["--node", spec]
    return subprocess.run(command, env=env, capture_output=True, text=True, check=False)


def _run(command: List[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(command)}\n{result.stdout}{result.stderr}")


def compile_objects(node: str, gen_dir: Path, out_dir: Path, variant: str) -> List[Path]:
    """Compile generated code and library of one node with the strict flag set."""
    config = VARIANTS[variant]
    if shutil.which(config["cc"]) is None:
        raise ToolMissing(f"compiler '{config['cc']}' not installed")
    out_dir.mkdir(parents=True, exist_ok=True)
    low = snake(node)
    sources = [gen_dir / low / f"can_{low}.c", gen_dir / low / f"can_{low}_db.c",
               LIB / "can_conv.c"]
    objects = []
    for source in sources:
        obj = out_dir / (source.stem + ".o")
        _run([config["cc"]] + STRICT_FLAGS + config["flags"]
             + ["-I", str(gen_dir / low), "-I", str(LIB), "-c", str(source), "-o", str(obj)])
        objects.append(obj)
    return objects


class Harness:
    """Drives the test executable of one node through its stdin/stdout protocol."""

    def __init__(self, node: str, mode: str, exe: Path, runner: List[str]) -> None:
        self.node = node
        self.mode = mode
        self.exe = exe
        self.runner = runner
        self.views = {v.msg.name: v for v in node_views(node, mode)}

    def run(self, lines: List[str]) -> List[str]:
        result = subprocess.run(self.runner + [str(self.exe)], input="\n".join(lines) + "\n",
                                capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"harness {self.node} failed ({result.returncode}):\n"
                               f"{result.stdout[-2000:]}\n{result.stderr[-4000:]}")
        output = result.stdout.splitlines()
        assert len(output) >= len(lines), "harness produced too little output"
        return output

    def pack(self, name: str, vectors: List[Dict[str, int]], fill: int = 0x00) -> List[bytes]:
        """Pack each vector into a buffer pre-filled with `fill`.

        The buffer has 4 guard bytes on each side of the DLC payload bytes;
        the guards must be untouched (LLR-PACK-004).
        """
        view = self.views[name]
        assert view.direction == "TX"
        lines = [f"P {name} {fill} " + " ".join(str(v[s.name]) for s in view.signals)
                 for v in vectors]
        frames = []
        for line in self.run(lines):
            raw = bytes.fromhex(line)
            assert len(raw) == view.msg.dlc + 8
            assert raw[:4] == bytes([fill]) * 4 and raw[-4:] == bytes([fill]) * 4, \
                f"{name}: pack wrote outside data[0..DLC-1]"
            frames.append(raw[4:-4])
        return frames

    def unpack(self, name: str, frames: List[bytes], fill: int = 0x00) -> List[Dict[str, int]]:
        """Unpack each frame into a structure pre-filled with `fill`.

        The input buffer is exactly DLC bytes long (heap allocated, so that
        sanitizers see out-of-range reads) and must be unchanged afterwards
        (LLR-UNPACK-003).
        """
        view = self.views[name]
        assert view.direction == "RX"
        lines = [f"U {name} {fill} {frame.hex()}" for frame in frames]
        results = []
        for frame, line in zip(frames, self.run(lines)):
            fields, _, after = line.partition("|")
            assert bytes.fromhex(after.strip()) == frame, f"{name}: unpack modified its input"
            numbers = [int(x) for x in fields.split()]
            assert len(numbers) == len(view.signals)
            results.append({s.name: n for s, n in zip(view.signals, numbers)})
        return results

    def dump(self):
        """Database tables as (messages, signals-by-message-index)."""
        messages, signals = [], {}
        for line in self.run(["D"]):
            parts = line.split()
            if parts[0] == "M":
                messages.append(dict(zip(("index", "id", "ext", "dlc", "dir", "cycle", "count"),
                                         (int(p) for p in parts[1:]))))
            elif parts[0] == "S":
                entry = {"start": int(parts[3]), "length": int(parts[4]),
                         "factor": int(parts[5], 16), "offset": int(parts[6], 16),
                         "phys_min": int(parts[7], 16), "phys_max": int(parts[8], 16),
                         "raw_min": int(parts[9]), "raw_max": int(parts[10])}
                signals.setdefault(int(parts[1]), []).append(entry)
        return messages, signals

    def constants(self) -> Dict[str, int]:
        return {k: int(v) for k, v in (line.split()[1:] for line in self.run(["K"]))}

    def encode(self, msg_index: int, sig_index: int, phys_bits: List[int]) -> List[int]:
        lines = [f"E {msg_index} {sig_index} 0x{bits:08x}" for bits in phys_bits]
        return [int(line) for line in self.run(lines)]

    def decode(self, msg_index: int, sig_index: int, raws: List[int]) -> List[int]:
        lines = [f"C {msg_index} {sig_index} {raw}" for raw in raws]
        return [int(line, 16) for line in self.run(lines)]


def build_harness(node: str, mode: str, gen_dir: Path = GENERATED,
                  variant: str = VARIANT, tag: str = "") -> Harness:
    from . import harness_gen

    config = VARIANTS[variant]
    for tool in [config["cc"]] + config["runner"]:
        if shutil.which(tool) is None:
            raise ToolMissing(f"'{tool}' not installed (variant {variant})")
    low = snake(node)
    out_dir = BUILD / (variant + tag) / low
    objects = compile_objects(node, gen_dir, out_dir, variant)
    source = out_dir / "harness.c"
    source.write_text(harness_gen.generate(node, mode), encoding="ascii")
    exe = out_dir / "harness"
    _run([config["cc"], "-std=c99", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function"]
         + config["flags"]
         + ["-I", str(gen_dir / low), "-I", str(LIB), str(source)]
         + [str(o) for o in objects] + ["-o", str(exe)])
    return Harness(node, mode, exe, config["runner"])
