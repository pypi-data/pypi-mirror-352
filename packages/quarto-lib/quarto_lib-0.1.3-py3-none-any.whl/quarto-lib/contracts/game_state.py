from typing import List, Optional

from lib.game import Game
from lib.types.cell import Cell
from lib.types.piece import Piece


class GameState:
    def __init__(
        self,
        board: List[List[Optional[Piece]]],
        current_piece: Piece,
        available_pieces: Optional[List[Piece]] = None,
        available_cells: Optional[List[Cell]] = None,
    ):
        self.board = board
        self.available_pieces = set(available_pieces if available_pieces is not None else [])
        self.available_cells = set(available_cells if available_cells is not None else [])
        self.current_piece = current_piece

    Board = List[List[Optional[Piece]]]

    @staticmethod
    def from_game(game: Game) -> "GameState":
        if game.current_piece is None:
            raise ValueError("GameState cannot be created from a game without a current piece.")

        return GameState(
            game.board,
            available_pieces=game.available_pieces,
            available_cells=game.available_cells,
            current_piece=game.current_piece,
        )
