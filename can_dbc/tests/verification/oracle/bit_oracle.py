"""Independent bit-level reference model of the DBC Motorola signal layout.

Deliberately dissimilar to the generator: no windows, shifts or masks. Each
signal is walked one bit at a time using the DBC "sawtooth" rule: starting
at the start bit (the MSB), the next less significant bit is one position
lower in the same byte; after bit 0 of a byte comes bit 7 of the next byte.
DBC bit number = byte * 8 + bit_in_byte, bit_in_byte 7 = MSB of the byte.
"""

from typing import Dict, List, Mapping, Tuple

Layout = Mapping[str, Tuple[int, int]]      # name -> (start bit, length)


def signal_bits(start: int, length: int) -> List[Tuple[int, int]]:
    """(byte, bit_in_byte) of every signal bit, most significant first."""
    bits = []
    position = start
    for _ in range(length):
        bits.append((position // 8, position % 8))
        position = position + 15 if position % 8 == 0 else position - 1
    return bits


def pack(dlc: int, layout: Layout, values: Mapping[str, int]) -> bytes:
    """Frame with every signal placed bit by bit; excess value bits ignored."""
    data = [0] * dlc
    for name, (start, length) in layout.items():
        value = values[name]
        for index, (byte, bit) in enumerate(signal_bits(start, length)):
            if (value >> (length - 1 - index)) & 1:
                data[byte] |= 1 << bit
    return bytes(data)


def unpack(data: bytes, layout: Layout) -> Dict[str, int]:
    values = {}
    for name, (start, length) in layout.items():
        value = 0
        for byte, bit in signal_bits(start, length):
            value = (value << 1) | ((data[byte] >> bit) & 1)
        values[name] = value
    return values


def used_mask(dlc: int, layout: Layout) -> bytes:
    """Frame with exactly the bits that belong to any signal set."""
    return pack(dlc, layout, {name: (1 << length) - 1 for name, (_, length) in layout.items()})


def owners(layout: Layout) -> Dict[Tuple[int, int], Tuple[str, int]]:
    """(byte, bit_in_byte) -> (signal name, weight of that bit in the signal)."""
    table = {}
    for name, (start, length) in layout.items():
        for index, position in enumerate(signal_bits(start, length)):
            assert position not in table, "overlapping signals in reference layout"
            table[position] = (name, length - 1 - index)
    return table
