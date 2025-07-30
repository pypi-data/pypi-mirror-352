from typing import Literal, Optional


from lib.types.cell import Cell
from lib.types.piece import Piece
from lib.utils import common_characteristics


class Game:
    def __init__(self):
        self._board: list[list[Optional[Piece]]] = [[None for _ in range(4)] for _ in range(4)]
        self._current_player: Literal[0, 1] = 0  # 0 for player 1, 1 for player 2
        self._current_turn: Literal[0, 1] = 0  # 0 for choice, 1 for placement
        self._chosen_piece: Optional[Piece] = None
        self._move_history: list[tuple[Piece, Cell]] = []
        self._game_over = False
        self._winner: Optional[int] = None
        self._winning_lines: list[list[Cell]] = []

    @property
    def is_game_over(self) -> bool:
        return self._game_over

    @property
    def current_player(self) -> Literal[0, 1]:
        return self._current_player

    @property
    def current_turn(self) -> Literal[0, 1]:
        return self._current_turn

    @property
    def board(self) -> list[list[Optional[Piece]]]:
        return [row[:] for row in self._board]

    @property
    def winner(self) -> Optional[int]:
        return self._winner

    @property
    def winning_lines(self) -> list[list[Cell]]:
        return self._winning_lines

    @property
    def available_pieces(self) -> list[Piece]:
        all_pieces = list(Piece)
        used_pieces = {piece for row in self._board for piece in row if piece is not None}
        return [piece for piece in all_pieces if piece not in used_pieces and piece != self._chosen_piece]

    @property
    def available_cells(self) -> list[Cell]:
        return [Cell(row, col) for row in range(4) for col in range(4) if self._board[row][col] is None]

    @property
    def current_piece(self) -> Optional[Piece]:
        return self._chosen_piece

    @property
    def is_fresh(self) -> bool:
        return len(self._move_history) == 0 and self._chosen_piece is None

    def _declare_winner(self):
        self._game_over = True
        self._winner = self._current_player

    def _declare_draw(self):
        self._game_over = True
        self._winner = None

    def _check_game_condition(self):
        for i in range(4):
            line = [Cell(i, j) for j in range(4)]
            row_pieces = [piece for piece in self._board[i] if piece is not None]
            if len(row_pieces) == 4 and common_characteristics(row_pieces):
                self._declare_winner()
                self._winning_lines.append(line)

        for j in range(4):
            line = [Cell(i, j) for i in range(4)]
            col_pieces = [piece for piece in [self._board[i][j] for i in range(4)] if piece is not None]
            if len(col_pieces) == 4 and common_characteristics(col_pieces):
                self._declare_winner()
                self._winning_lines.append(line)

        for i in [0, 3]:
            line = [Cell(j, j if i == 0 else 3 - j) for j in range(4)]
            diag_pieces = [
                piece for piece in [self._board[j][j if i == 0 else 3 - j] for j in range(4)] if piece is not None
            ]
            if len(diag_pieces) == 4 and common_characteristics(diag_pieces):
                self._declare_winner()
                self._winning_lines.append(line)

        if self._game_over:
            return

        if len(self.available_pieces) == 0:
            self._declare_draw()

    def choose_piece(self, piece: Piece):
        if self._game_over:
            raise ValueError("The game is already over.")
        if self._current_turn != 0:
            raise ValueError("It's not the choice turn.")
        if piece not in self.available_pieces:
            raise ValueError("Piece is not available.")
        if self._chosen_piece is not None:
            raise ValueError("A piece has already been chosen.")

        self._chosen_piece = piece
        self._current_turn = 1
        self._current_player = 1 - self._current_player

    def place_piece(self, cell: Cell):
        if self._game_over:
            raise ValueError("The game is already over.")
        if self._current_turn != 1:
            raise ValueError("It's not the placement turn.")
        row, col = cell.row, cell.col
        if self._board[row][col] is not None:
            raise ValueError("Cell is already occupied.")
        if self._chosen_piece is None:
            raise ValueError("No piece has been chosen.")

        self._board[row][col] = self._chosen_piece
        self._current_turn = 0
        self._move_history.append((self._chosen_piece, cell))
        self._chosen_piece = None

        self._check_game_condition()
