from quarto.types.piece import Piece
from quarto.utils import common_characteristics


class TestUtils:
    def test_common_characteristics_empty_line(self):
        line = [None, None, None, None]
        result = common_characteristics(line)
        assert result == []

    def test_common_characteristics_no_common_bits(self):
        line = [Piece.DRSH, Piece.DRSS, Piece.DRTH, Piece.LSSH]
        result = common_characteristics(line)
        assert result == []

    def test_common_characteristics_common_bit_0(self):
        line = [Piece.DRSH, Piece.DRSS, Piece.DSTH]
        result = common_characteristics(line)
        assert result == [(3, 1)]

    def test_common_characteristics_common_bit_1(self):
        line = [Piece(0b0100), Piece(0b1111)]
        result = common_characteristics(line)
        assert result == [(2, 1)]

    def test_common_characteristics_multiple_common_bits(self):
        line = [Piece.DRTH, Piece.DRSH, Piece.DSTH, Piece.DSSH]
        result = common_characteristics(line)
        assert result == [(0, 1), (3, 1)]
