"""Generator error type. Every rejection carries a stable error code."""


class DbcError(Exception):
    """Raised when the DBC cannot be parsed or violates a generator rule."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


E_PARSE = "E001"            # syntax not understood / unsupported statement
E_INTEL = "E002"            # little-endian (Intel) signal
E_SIGNED = "E003"           # signed signal
E_MUX = "E004"              # multiplexed signal
E_FLOAT = "E005"            # IEEE float signal
E_OVERLAP = "E006"          # signals overlap
E_EXCEEDS_DLC = "E007"      # signal does not fit into the message
E_NAME = "E008"             # invalid or duplicate identifier
E_NODE = "E009"             # unknown node
E_DLC = "E010"              # DLC outside 1..8 (CAN FD not supported)
E_SCALING = "E011"          # factor <= 0, or scaling on a signal > 32 bit
E_LENGTH = "E012"           # signal length outside 1..64
E_RANGE = "E013"            # min/max inconsistent
E_FRAME_ID = "E014"         # invalid or duplicate frame id
E_EMPTY = "E015"            # message without signals
