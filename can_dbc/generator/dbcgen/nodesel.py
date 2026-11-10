"""Selection of the messages and signals relevant for one node."""

from dataclasses import dataclass
from typing import List, Tuple

from .errors import DbcError, E_NODE
from .layout import compute_layout
from .model import Database, Message, Signal

MODES = ("both", "tx", "rx")


@dataclass(frozen=True)
class NodeMessage:
    message: Message
    direction: str                  # "TX" or "RX"
    signals: Tuple[Signal, ...]     # frame order (MSB of the frame first)


def _frame_order(signals) -> Tuple[Signal, ...]:
    return tuple(sorted(signals, key=lambda s: compute_layout(s.start, s.length).top))


def select(db: Database, node: str, mode: str) -> List[NodeMessage]:
    """TX: messages sent by the node, with all signals.
    RX: messages with at least one signal received by the node, reduced to
    the signals the node receives.
    The result is sorted by ascending frame id.
    """
    if node not in db.nodes:
        raise DbcError(E_NODE, f"unknown node '{node}'")
    if mode not in MODES:
        raise DbcError(E_NODE, f"unknown mode '{mode}' for node '{node}'")

    result = []
    for msg in db.messages:
        if msg.sender == node:
            if mode != "rx":
                result.append(NodeMessage(msg, "TX", _frame_order(msg.signals)))
        elif mode != "tx":
            received = [s for s in msg.signals if node in s.receivers]
            if received:
                result.append(NodeMessage(msg, "RX", _frame_order(received)))
    return sorted(result, key=lambda nm: (nm.message.frame_id, nm.message.is_extended))
