from enum import Enum


class Piece(Enum):
    def __new__(cls, value: int):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    LRTS = 0b0000
    LRTH = 0b0001
    LRSS = 0b0010
    LRSH = 0b0011

    LSTS = 0b0100
    LSTH = 0b0101
    LSSS = 0b0110
    LSSH = 0b0111

    DRTS = 0b1000
    DRTH = 0b1001
    DRSS = 0b1010
    DRSH = 0b1011

    DSTS = 0b1100
    DSTH = 0b1101
    DSSS = 0b1110
    DSSH = 0b1111
