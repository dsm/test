"""C identifier derivation."""

import re

_C_KEYWORDS = frozenset("""
auto break case char const continue default do double else enum extern float
for goto if inline int long register restrict return short signed sizeof
static struct switch typedef union unsigned void volatile while _Bool
_Complex _Imaginary
""".split())

_RE_IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def snake(name: str) -> str:
    """'PackVoltage' -> 'pack_voltage', 'BMS_Status' -> 'bms_status'."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_").lower()


def upper(name: str) -> str:
    return snake(name).upper()


def is_valid_identifier(name: str) -> bool:
    return bool(_RE_IDENT.match(name)) and name not in _C_KEYWORDS
