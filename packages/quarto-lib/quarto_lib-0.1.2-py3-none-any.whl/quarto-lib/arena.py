import logging
from typing import Optional, Tuple

from lib.contracts.game_state import GameState
from lib.contracts.informal_agent_interface import InformalAgentInterface
from lib.game import Game
from lib.types.cell import Cell

logger = logging.getLogger(__name__)


class Arena:
    def __init__(self, agent1: InformalAgentInterface, agent2: InformalAgentInterface):
        self.agent1 = agent1
        self.agent2 = agent2
        self.game: Game

    def play(self) -> Tuple[Optional[int], list[list[Cell]]]:
        self.game = Game()
        while not self.game.is_game_over:
            if self.game.is_fresh:
                if self.game.current_player == 0:
                    piece = self.agent1.choose_initial_piece()
                else:
                    piece = self.agent2.choose_initial_piece()
                self.game.choose_piece(piece)
                continue

            # Finish the game if there is only one option left
            if len(self.game.available_cells) == 1:
                cell = self.game.available_cells[0]
                self.game.place_piece(cell)
                continue

            # If not fresh, proceed with the turn
            if self.game.current_player == 0:
                cell, piece = self.agent1.complete_turn(GameState.from_game(self.game))
            else:
                cell, piece = self.agent2.complete_turn(GameState.from_game(self.game))

            logger.debug(f"Player {self.game.current_player} placed piece {piece} at cell {cell}")
            self.game.place_piece(cell)
            if self.game.is_game_over:
                break
            if piece is None:
                raise ValueError("Agent returned None for piece, which is not allowed at this stage of the game.")
            self.game.choose_piece(piece)

        return self.game.winner, self.game.winning_lines
