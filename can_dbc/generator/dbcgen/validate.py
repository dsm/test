"""Rule checks. Anything the generator cannot translate faithfully is rejected."""

from .errors import (DbcError, E_DLC, E_EMPTY, E_EXCEEDS_DLC, E_FLOAT, E_FRAME_ID,
                     E_INTEL, E_LENGTH, E_MUX, E_NAME, E_NODE, E_OVERLAP, E_RANGE,
                     E_SCALING, E_SIGNED)
from .layout import compute_layout, raw_limits
from .model import Database, Message, NO_NODE, Signal
from .naming import is_valid_identifier, snake


def _check_name(kind: str, name: str) -> None:
    if not is_valid_identifier(name) or not is_valid_identifier(snake(name)):
        raise DbcError(E_NAME, f"{kind} name '{name}' is not usable as a C identifier")


def _check_signal(msg: Message, sig: Signal, nodes) -> None:
    where = f"{msg.name}.{sig.name}"
    _check_name("signal", sig.name)
    if sig.mux is not None:
        raise DbcError(E_MUX, f"{where}: multiplexed signals are not supported")
    if sig.byte_order != "0":
        raise DbcError(E_INTEL, f"{where}: little-endian (Intel) signals are not supported")
    if sig.sign != "+":
        raise DbcError(E_SIGNED, f"{where}: signed signals are not supported")
    if sig.is_float:
        raise DbcError(E_FLOAT, f"{where}: float signals are not supported")
    if not 1 <= sig.length <= 64:
        raise DbcError(E_LENGTH, f"{where}: length {sig.length} outside 1..64")
    if sig.start > 63 or compute_layout(sig.start, sig.length).bottom >= msg.dlc * 8:
        raise DbcError(E_EXCEEDS_DLC, f"{where}: does not fit into {msg.dlc} byte(s)")
    if sig.factor <= 0:
        raise DbcError(E_SCALING, f"{where}: factor must be greater than zero")
    if sig.length > 32 and (sig.factor != 1 or sig.offset != 0):
        raise DbcError(E_SCALING, f"{where}: signals wider than 32 bit must have "
                                  "factor 1 and offset 0")
    low, high = raw_limits(sig)
    if low > high:
        raise DbcError(E_RANGE, f"{where}: [min|max] does not contain any raw value")
    for node in sig.receivers:
        if node != NO_NODE and node not in nodes:
            raise DbcError(E_NODE, f"{where}: unknown receiver '{node}'")
    seen = set()
    for value, text in sig.choices:
        ident = snake(text)
        if value < 0 or value >= (1 << sig.length):
            raise DbcError(E_RANGE, f"{where}: value table entry {value} out of range")
        if not is_valid_identifier("x" + ident) or ident == "" or ident in seen:
            raise DbcError(E_NAME, f"{where}: value name '{text}' is invalid or duplicated")
        seen.add(ident)


def _check_message(msg: Message, nodes) -> None:
    _check_name("message", msg.name)
    if not 1 <= msg.dlc <= 8:
        raise DbcError(E_DLC, f"{msg.name}: DLC {msg.dlc} outside 1..8 "
                              "(CAN FD is not supported)")
    limit = 0x1FFFFFFF if msg.is_extended else 0x7FF
    if msg.frame_id > limit:
        raise DbcError(E_FRAME_ID, f"{msg.name}: frame id 0x{msg.frame_id:X} out of range")
    if msg.sender != NO_NODE and msg.sender not in nodes:
        raise DbcError(E_NODE, f"{msg.name}: unknown sender '{msg.sender}'")
    if not 0 <= msg.cycle_time_ms <= 0xFFFF:
        raise DbcError(E_RANGE, f"{msg.name}: cycle time out of range")
    if len(msg.signals) == 0:
        raise DbcError(E_EMPTY, f"{msg.name}: message has no signals")

    used = {}
    names = set()
    for sig in msg.signals:
        _check_signal(msg, sig, nodes)
        if snake(sig.name) in names:
            raise DbcError(E_NAME, f"{msg.name}: duplicate signal name '{sig.name}'")
        names.add(snake(sig.name))
        lay = compute_layout(sig.start, sig.length)
        for bit in range(lay.top, lay.bottom + 1):
            if bit in used:
                raise DbcError(E_OVERLAP, f"{msg.name}: '{sig.name}' overlaps '{used[bit]}'")
            used[bit] = sig.name


def validate(db: Database) -> None:
    nodes = set(db.nodes)
    for node in db.nodes:
        _check_name("node", node)
    if len(nodes) != len(db.nodes):
        raise DbcError(E_NAME, "duplicate node name")
    ids = set()
    names = set()
    for msg in db.messages:
        _check_message(msg, nodes)
        if msg.raw_id in ids:
            raise DbcError(E_FRAME_ID, f"{msg.name}: duplicate frame id")
        if snake(msg.name) in names:
            raise DbcError(E_NAME, f"duplicate message name '{msg.name}'")
        ids.add(msg.raw_id)
        names.add(snake(msg.name))
