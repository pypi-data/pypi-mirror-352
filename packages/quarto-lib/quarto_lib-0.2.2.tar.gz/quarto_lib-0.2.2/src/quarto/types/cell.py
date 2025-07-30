from enum import Enum


class Cell(Enum):
    def __new__(cls, row: int, col: int):
        obj = object.__new__(cls)
        obj._value_ = (row, col)
        return obj

    A1 = (3, 0)
    A2 = (2, 0)
    A3 = (1, 0)
    A4 = (0, 0)
    B1 = (3, 1)
    B2 = (2, 1)
    B3 = (1, 1)
    B4 = (0, 1)
    C1 = (3, 2)
    C2 = (2, 2)
    C3 = (1, 2)
    C4 = (0, 2)
    D1 = (3, 3)
    D2 = (2, 3)
    D3 = (1, 3)
    D4 = (0, 3)

    @property
    def row(self):
        return self.value[0]

    @property
    def col(self):
        return self.value[1]
