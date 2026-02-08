from enum import StrEnum

class SignalKind(StrEnum):
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    TRAILING_STOP = "TRAILING_STOP"
    TRAILING_UPDATE = "TRAILING_UPDATE"
