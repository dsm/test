"""Minimal, dependency-free DBC parser.

Only the statements needed by the generator are interpreted. Statements that
would change the meaning of the generated code but are not supported
(multiplexing, float signals, ...) are kept in the model so that validate.py
can reject them; anything not recognised at all is a parse error.
"""

import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from typing import Dict, List, Tuple

from .errors import DbcError, E_PARSE, E_MUX
from .model import Database, Message, Signal

_RE_BO = re.compile(r"^BO_\s+(\d+)\s+(\w+)\s*:\s*(\d+)\s+(\w+)\s*$")
_RE_SG = re.compile(
    r"^SG_\s+(\w+)\s*(M|m\d+M?)?\s*:\s*(\d+)\|(\d+)@([01])([+-])\s*"
    r"\(\s*([^,\s]+)\s*,\s*([^)\s]+)\s*\)\s*"
    r"\[\s*([^|\s]+)\s*\|\s*([^\]\s]+)\s*\]\s*"
    r"\"([^\"]*)\"\s*(.*)$"
)
_RE_VAL = re.compile(r"^VAL_\s+(\d+)\s+(\w+)\s+(.*);\s*$")
_RE_VAL_PAIR = re.compile(r"(-?\d+)\s+\"([^\"]*)\"")
_RE_CYCLE = re.compile(r"^BA_\s+\"GenMsgCycleTime\"\s+BO_\s+(\d+)\s+(\d+)\s*;\s*$")
_RE_CYCLE_DEF = re.compile(r"^BA_DEF_DEF_\s+\"GenMsgCycleTime\"\s+(\d+)\s*;\s*$")
_RE_VALTYPE = re.compile(r"^SIG_VALTYPE_\s+(\d+)\s+(\w+)\s*:\s*(\d+)\s*;\s*$")

# Statements without influence on the generated code.
_IGNORED = ("VERSION", "BS_", "BA_DEF_DEF_", "BA_DEF_", "BA_", "VAL_TABLE_",
            "BO_TX_BU_", "SIG_GROUP_")


def _number(text: str, line_no: int) -> Fraction:
    try:
        return Fraction(Decimal(text))
    except (InvalidOperation, ValueError):
        raise DbcError(E_PARSE, f"line {line_no}: invalid number '{text}'") from None


def parse_dbc(text: str) -> Database:
    nodes: Tuple[str, ...] = ()
    order: List[int] = []
    headers: Dict[int, Tuple[str, int, str]] = {}
    signals: Dict[int, List[dict]] = {}
    cycle: Dict[int, int] = {}
    cycle_default = 0
    choices: Dict[Tuple[int, str], Tuple[Tuple[int, str], ...]] = {}
    floats = set()

    current = None
    in_ns = False
    in_comment = False

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()

        if in_comment:
            in_comment = not line.endswith('";')
            continue
        if in_ns:
            if line == "":
                in_ns = False
            continue
        if line == "":
            current = None
            continue

        if line.startswith("NS_"):
            in_ns = True
        elif line.startswith("CM_"):
            in_comment = not line.endswith('";')
        elif line.startswith("BU_"):
            if not line.startswith("BU_:"):
                raise DbcError(E_PARSE, f"line {line_no}: malformed BU_")
            nodes = tuple(line[4:].split())
        elif line.startswith("BO_ "):
            match = _RE_BO.match(line)
            if match is None:
                raise DbcError(E_PARSE, f"line {line_no}: malformed BO_")
            current = int(match.group(1))
            if current in headers:
                raise DbcError(E_PARSE, f"line {line_no}: frame id {current} defined twice")
            order.append(current)
            headers[current] = (match.group(2), int(match.group(3)), match.group(4))
            signals[current] = []
        elif line.startswith("SG_ "):
            match = _RE_SG.match(line)
            if match is None or current is None:
                raise DbcError(E_PARSE, f"line {line_no}: malformed or misplaced SG_")
            signals[current].append({
                "name": match.group(1),
                "mux": match.group(2),
                "start": int(match.group(3)),
                "length": int(match.group(4)),
                "byte_order": match.group(5),
                "sign": match.group(6),
                "factor": _number(match.group(7), line_no),
                "offset": _number(match.group(8), line_no),
                "minimum": _number(match.group(9), line_no),
                "maximum": _number(match.group(10), line_no),
                "unit": match.group(11),
                "receivers": tuple(r for r in re.split(r"[,\s]+", match.group(12)) if r),
            })
        elif line.startswith("SG_MUL_VAL_"):
            raise DbcError(E_MUX, f"line {line_no}: extended multiplexing is not supported")
        elif line.startswith("SIG_VALTYPE_"):
            match = _RE_VALTYPE.match(line)
            if match is None:
                raise DbcError(E_PARSE, f"line {line_no}: malformed SIG_VALTYPE_")
            if match.group(3) != "0":
                floats.add((int(match.group(1)), match.group(2)))
        elif line.startswith("VAL_ "):
            match = _RE_VAL.match(line)
            if match is None:
                raise DbcError(E_PARSE, f"line {line_no}: malformed VAL_")
            pairs = tuple((int(v), t) for v, t in _RE_VAL_PAIR.findall(match.group(3)))
            choices[(int(match.group(1)), match.group(2))] = pairs
        elif _RE_CYCLE.match(line):
            match = _RE_CYCLE.match(line)
            cycle[int(match.group(1))] = int(match.group(2))
        elif _RE_CYCLE_DEF.match(line):
            cycle_default = int(_RE_CYCLE_DEF.match(line).group(1))
        elif line.startswith(_IGNORED):
            pass
        else:
            raise DbcError(E_PARSE, f"line {line_no}: unsupported statement '{line[:40]}'")

    messages = []
    for raw_id in order:
        name, dlc, sender = headers[raw_id]
        sigs = tuple(
            Signal(is_float=(raw_id, s["name"]) in floats,
                   choices=choices.get((raw_id, s["name"]), ()),
                   **s)
            for s in signals[raw_id]
        )
        messages.append(Message(raw_id, name, dlc, sender, sigs,
                                cycle.get(raw_id, cycle_default)))
    return Database(nodes, tuple(messages))
