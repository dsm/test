"""Immutable in-memory model of the DBC content used by the generator."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Tuple

EXTENDED_FLAG = 0x80000000
NO_NODE = "Vector__XXX"


@dataclass(frozen=True)
class Signal:
    name: str
    start: int                 # DBC start bit
    length: int
    byte_order: str            # "0" Motorola, "1" Intel
    sign: str                  # "+" unsigned, "-" signed
    factor: Fraction
    offset: Fraction
    minimum: Fraction
    maximum: Fraction
    unit: str
    receivers: Tuple[str, ...]
    mux: Optional[str]
    is_float: bool
    choices: Tuple[Tuple[int, str], ...]


@dataclass(frozen=True)
class Message:
    raw_id: int                # as written in the DBC (bit 31 = extended)
    name: str
    dlc: int
    sender: str
    signals: Tuple[Signal, ...]
    cycle_time_ms: int

    @property
    def is_extended(self) -> bool:
        return (self.raw_id & EXTENDED_FLAG) != 0

    @property
    def frame_id(self) -> int:
        return self.raw_id & ~EXTENDED_FLAG


@dataclass(frozen=True)
class Database:
    nodes: Tuple[str, ...]
    messages: Tuple[Message, ...]
