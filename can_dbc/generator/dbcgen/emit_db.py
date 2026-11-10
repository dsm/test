"""Emission of the constant message/signal database can_<node>_db.h / .c."""

import struct
from fractions import Fraction
from typing import List

from .emit_c import banner, describe
from .layout import physical, raw_limits
from .naming import snake, upper
from .nodesel import NodeMessage


def _f32(value: Fraction) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def f32_literal(value: Fraction) -> str:
    """Decimal literal that converts to the nearest float32 of value.

    Integral values are written exactly, others with the fewest digits that
    still convert to the same float32.
    """
    target = _f32(value)
    text = repr(target)
    exact_integer = target == int(target) and "e" not in text
    for digits in range(0 if exact_integer else 1, 10 if not exact_integer else 0):
        candidate = repr(float(f"{target:.{digits}g}"))
        if "e" not in candidate and _f32(Fraction(candidate)) == target:
            text = candidate
            break
    return text + "F"


def msg_index(node: str, nm: NodeMessage) -> str:
    return f"CAN_{upper(node)}_MSG_{upper(nm.message.name)}"


def sig_index(nm: NodeMessage, sig) -> str:
    return f"CAN_{upper(nm.message.name)}_SIG_{upper(sig.name)}"


def identifiers(node: str, node_messages: List[NodeMessage]) -> List[str]:
    names = [f"can_{snake(node)}_messages", f"CAN_{upper(node)}_MSG_COUNT",
             f"can_{snake(node)}_msg_index_t"]
    for nm in node_messages:
        low, up = f"can_{snake(nm.message.name)}", f"CAN_{upper(nm.message.name)}"
        names += [msg_index(node, nm), f"{low}_signals", f"{low}_sig_index_t",
                  f"{up}_SIG_COUNT"]
        names += [sig_index(nm, sig) for sig in nm.signals]
    return names


def emit_header(node_messages: List[NodeMessage], meta: dict) -> str:
    node = meta["node"]
    low_node = snake(node)
    guard = f"CAN_{low_node.upper()}_DB_H"
    out = banner(f"can_{low_node}_db.h", "CAN message/signal database.", meta)
    out += [f"#ifndef {guard}", f"#define {guard}", "", '#include "can_db_types.h"', "",
            f"/* Index into can_{low_node}_messages (ascending frame id). */",
            "typedef enum", "{"]
    for position, nm in enumerate(node_messages):
        init = " = 0" if position == 0 else ""
        out.append(f"    {msg_index(node, nm)}{init}, /* {describe(nm)} */")
    out += [f"    CAN_{upper(node)}_MSG_COUNT", f"}} can_{low_node}_msg_index_t;"]
    for nm in node_messages:
        low, up = f"can_{snake(nm.message.name)}", f"CAN_{upper(nm.message.name)}"
        out += ["", f"/* Index into {low}_signals. */", "typedef enum", "{"]
        for position, sig in enumerate(nm.signals):
            init = " = 0" if position == 0 else ""
            out.append(f"    {sig_index(nm, sig)}{init},")
        out += [f"    {up}_SIG_COUNT", f"}} {low}_sig_index_t;"]
    out.append("")
    for nm in node_messages:
        low, up = f"can_{snake(nm.message.name)}", f"CAN_{upper(nm.message.name)}"
        out.append(f"extern const can_db_signal_t {low}_signals[{up}_SIG_COUNT];")
    out += [f"extern const can_db_message_t can_{low_node}_messages"
            f"[CAN_{upper(node)}_MSG_COUNT];",
            "", f"#endif /* {guard} */", ""]
    return "\n".join(out)


def emit_source(node_messages: List[NodeMessage], meta: dict) -> str:
    node = meta["node"]
    low_node = snake(node)
    out = banner(f"can_{low_node}_db.c", "CAN message/signal database.", meta)
    out.append(f'#include "can_{low_node}_db.h"')
    for nm in node_messages:
        low, up = f"can_{snake(nm.message.name)}", f"CAN_{upper(nm.message.name)}"
        out += ["", f"/* {describe(nm)} */",
                f"const can_db_signal_t {low}_signals[{up}_SIG_COUNT] =", "{",
                "    /* start, len, { factor, offset, phys_min, phys_max, raw_min, raw_max } */"]
        for sig in nm.signals:
            raw_min, raw_max = raw_limits(sig)
            conv = ", ".join([f32_literal(sig.factor), f32_literal(sig.offset),
                              f32_literal(physical(sig, raw_min)),
                              f32_literal(physical(sig, raw_max)),
                              f"{raw_min}U", f"{raw_max}U"])
            out.append(f"    {{ {sig.start}U, {sig.length}U, {{ {conv} }} }}, /* {sig.name} */")
        out[-1] = out[-1].replace(" }, /*", " }  /*")
        out.append("};")
    out += ["", f"const can_db_message_t can_{low_node}_messages[CAN_{upper(node)}_MSG_COUNT] =",
            "{", "    /* id, is_extended, dlc, dir, cycle_time_ms, signals, signal_count */"]
    for position, nm in enumerate(node_messages):
        msg = nm.message
        low, up = f"can_{snake(msg.name)}", f"CAN_{upper(msg.name)}"
        comma = "," if position + 1 < len(node_messages) else ""
        out.append(f"    {{ 0x{msg.frame_id:X}U, {int(msg.is_extended)}U, {msg.dlc}U, "
                   f"CAN_DB_DIR_{nm.direction}, {msg.cycle_time_ms}U, "
                   f"{low}_signals, (uint8_t){up}_SIG_COUNT }}{comma}")
    out += ["};", ""]
    return "\n".join(out)
