"""Command line interface: python -m dbcgen --dbc FILE --out DIR --node NAME[:rx|:tx] ..."""

import argparse
import hashlib
import os
import sys
from typing import List

from . import __version__, emit_c, emit_db
from .dbc_parser import parse_dbc
from .errors import DbcError, E_EMPTY, E_NAME, E_NODE
from .naming import snake
from .nodesel import select
from .validate import validate


def generate(dbc_path: str, out_dir: str, node_specs: List[str]) -> List[str]:
    with open(dbc_path, "rb") as handle:
        content = handle.read()
    db = parse_dbc(content.decode("utf-8"))
    validate(db)

    outputs = {}
    for spec in node_specs:
        node, separator, mode = spec.partition(":")
        if separator and mode not in ("rx", "tx"):
            raise DbcError(E_NODE, f"invalid node selection '{spec}' (use NAME, NAME:rx or NAME:tx)")
        mode = mode or "both"
        node_messages = select(db, node, mode)
        if not node_messages:
            raise DbcError(E_EMPTY, f"node '{node}' ({mode}) has no messages")
        names = emit_db.identifiers(node, node_messages)
        for nm in node_messages:
            names += emit_c.identifiers(nm)
        duplicates = sorted({n for n in names if names.count(n) > 1})
        if duplicates:
            raise DbcError(E_NAME, f"node '{node}': identifier clash: {', '.join(duplicates)}")

        meta = {"version": __version__, "dbc_name": os.path.basename(dbc_path),
                "dbc_sha256": hashlib.sha256(content).hexdigest(),
                "node": node, "mode": {"both": "tx+rx"}.get(mode, mode)}
        low = snake(node)
        node_dir = os.path.join(out_dir, low)
        outputs[os.path.join(node_dir, f"can_{low}.h")] = emit_c.emit_header(node_messages, meta)
        outputs[os.path.join(node_dir, f"can_{low}.c")] = emit_c.emit_source(node_messages, meta)
        outputs[os.path.join(node_dir, f"can_{low}_db.h")] = emit_db.emit_header(node_messages, meta)
        outputs[os.path.join(node_dir, f"can_{low}_db.c")] = emit_db.emit_source(node_messages, meta)

    # Nothing is written unless every requested node could be generated.
    written = []
    for path in sorted(outputs):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="ascii", newline="\n") as handle:
            handle.write(outputs[path])
        written.append(path)
    return written


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="dbcgen", description=__doc__)
    parser.add_argument("--dbc", required=True, help="input DBC file")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--node", action="append", required=True, metavar="NAME[:rx|:tx]",
                        help="node to generate for; ':rx' = unpack only, ':tx' = pack only")
    args = parser.parse_args(argv)
    try:
        if len({spec.partition(":")[0] for spec in args.node}) != len(args.node):
            raise DbcError(E_NODE, "a node may be given only once")
        for path in generate(args.dbc, args.out, args.node):
            print(path)
    except DbcError as error:
        print(f"error[{error.code}]: {error.message}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
