"""Emission of the pack/unpack module can_<node>.h / can_<node>.c.

Generated functions are straight-line code: no branches, no loops, no
pointer casts. Each signal is handled through a big-endian "window" that is
assembled from / distributed to the payload bytes with shifts only, which
makes the code independent of the endianness of the target.
"""

from typing import List

from .layout import Layout, compute_layout
from .naming import snake, upper
from .nodesel import NodeMessage


def banner(file_name: str, title: str, meta: dict) -> List[str]:
    return [
        "/*",
        f" * {file_name} - {title}",
        " *",
        " * GENERATED FILE - DO NOT EDIT.",
        f" * Generator : dbcgen {meta['version']}",
        f" * Source    : {meta['dbc_name']}",
        f" * SHA-256   : {meta['dbc_sha256']}",
        f" * Node      : {meta['node']} ({meta['mode']})",
        " */",
    ]


def _lit(value: int, bits: int) -> str:
    return f"0x{value:X}" + ("U" if bits == 32 else "ULL")


def _wtype(lay: Layout) -> str:
    return f"uint{lay.window_bits}_t"


def describe(nm: NodeMessage) -> str:
    msg = nm.message
    kind = "extended" if msg.is_extended else "standard"
    return f"{msg.name} (0x{msg.frame_id:X}, {kind}, DLC {msg.dlc}, {nm.direction})"


def _sig_comment(sig, lay: Layout) -> str:
    if lay.first_byte == lay.last_byte:
        where = f"byte {lay.first_byte}"
    else:
        where = f"bytes {lay.first_byte}..{lay.last_byte}"
    return (f"    /* {sig.name}: start {sig.start}, len {sig.length} -> {where}, "
            f"shift {lay.shift}, mask 0x{lay.mask:X} */")


def _window_var(nm: NodeMessage) -> List[str]:
    widths = sorted({compute_layout(s.start, s.length).window_bits for s in nm.signals})
    return [f"    uint{w}_t window{w};" for w in widths]


def _pack_body(nm: NodeMessage) -> List[str]:
    out = _window_var(nm) + [""]
    for index in range(nm.message.dlc):
        out.append(f"    data[{index}] = 0U;")
    for sig in nm.signals:
        lay = compute_layout(sig.start, sig.length)
        var = f"window{lay.window_bits}"
        expr = f"(({_wtype(lay)})msg->{snake(sig.name)} & {_lit(lay.mask, lay.window_bits)})"
        if lay.shift:
            expr += f" << {lay.shift}U"
        out += ["", _sig_comment(sig, lay), f"    {var} = {expr};"]
        ff = _lit(0xFF, lay.window_bits)
        for byte in range(lay.first_byte, lay.last_byte + 1):
            down = 8 * (lay.last_byte - byte)
            src = f"({var} >> {down}U)" if down else var
            out.append(f"    data[{byte}] |= (uint8_t)({src} & {ff});")
    return out


def _unpack_body(nm: NodeMessage) -> List[str]:
    out = _window_var(nm)
    for sig in nm.signals:
        lay = compute_layout(sig.start, sig.length)
        var = f"window{lay.window_bits}"
        terms = []
        for byte in range(lay.first_byte, lay.last_byte + 1):
            up = 8 * (lay.last_byte - byte)
            term = f"({_wtype(lay)})data[{byte}]"
            terms.append(f"({term} << {up}U)" if up else term)
        src = f"({var} >> {lay.shift}U)" if lay.shift else var
        out += ["", _sig_comment(sig, lay),
                f"    {var} = {' | '.join(terms)};",
                f"    msg->{snake(sig.name)} = (uint{lay.field_bits}_t)"
                f"({src} & {_lit(lay.mask, lay.window_bits)});"]
    return out


def _prototype(nm: NodeMessage) -> str:
    base = f"can_{snake(nm.message.name)}"
    if nm.direction == "TX":
        return f"void {base}_pack(const {base}_t *msg, uint8_t *data)"
    return f"void {base}_unpack({base}_t *msg, const uint8_t *data)"


def identifiers(nm: NodeMessage) -> List[str]:
    """All file-scope identifiers emitted for one message (for uniqueness checks)."""
    low, up = f"can_{snake(nm.message.name)}", f"CAN_{upper(nm.message.name)}"
    names = [f"{low}_t", f"{low}_{'pack' if nm.direction == 'TX' else 'unpack'}",
             f"{up}_FRAME_ID", f"{up}_IS_EXTENDED", f"{up}_DLC", f"{up}_CYCLE_TIME_MS"]
    for sig in nm.signals:
        names += [f"{up}_{upper(sig.name)}_{upper(text)}" for _, text in sig.choices]
    return names


def emit_header(node_messages: List[NodeMessage], meta: dict) -> str:
    node = snake(meta["node"])
    guard = f"CAN_{node.upper()}_H"
    out = banner(f"can_{node}.h", "CAN message pack/unpack (raw values).", meta)
    out += [f"#ifndef {guard}", f"#define {guard}", "", "#include <stdint.h>"]
    for nm in node_messages:
        msg = nm.message
        low, up = f"can_{snake(msg.name)}", f"CAN_{upper(msg.name)}"
        out += ["", f"/* ---- {describe(nm)} ---- */", "",
                f"#define {up}_FRAME_ID (0x{msg.frame_id:X}U)",
                f"#define {up}_IS_EXTENDED ({int(msg.is_extended)}U)",
                f"#define {up}_DLC ({msg.dlc}U)",
                f"#define {up}_CYCLE_TIME_MS ({msg.cycle_time_ms}U)"]
        for sig in nm.signals:
            if sig.choices:
                out.append("")
            for value, text in sig.choices:
                out.append(f"#define {up}_{upper(sig.name)}_{upper(text)} ({value}U)")
        out += ["", "typedef struct", "{"]
        for sig in nm.signals:
            lay = compute_layout(sig.start, sig.length)
            unit = f" [{sig.unit}]" if sig.unit else ""
            out.append(f"    uint{lay.field_bits}_t {snake(sig.name)};"
                       f" /* raw, {sig.length} bit{unit} */")
        out += [f"}} {low}_t;", ""]
        if nm.direction == "TX":
            out += ["/*",
                    f" * Writes data[0..{msg.dlc - 1}]. Each value is masked to its signal",
                    " * length, unused bits are written as 0.",
                    " * Preconditions: msg != NULL, data != NULL.",
                    " */"]
        else:
            out += ["/*",
                    f" * Reads data[0..{msg.dlc - 1}] and writes every member of *msg.",
                    " * Preconditions: msg != NULL, data != NULL.",
                    " */"]
        out.append(_prototype(nm) + ";")
    out += ["", f"#endif /* {guard} */", ""]
    return "\n".join(out)


def emit_source(node_messages: List[NodeMessage], meta: dict) -> str:
    node = snake(meta["node"])
    out = banner(f"can_{node}.c", "CAN message pack/unpack (raw values).", meta)
    out.append(f'#include "can_{node}.h"')
    for nm in node_messages:
        body = _pack_body(nm) if nm.direction == "TX" else _unpack_body(nm)
        out += ["", f"/* {describe(nm)} */", _prototype(nm), "{"] + body + ["}"]
    out.append("")
    return "\n".join(out)
