from lib.arena import Arena
from lib.contracts.informal_agent_interface import InformalAgentInterface


class TournamentRound:
    def __init__(self, agent1: InformalAgentInterface, agent2: InformalAgentInterface, best_of: int = 1):
        if best_of < 1 or best_of % 2 == 0:
            raise ValueError("best_of must be a positive odd integer.")
        self.best_of = best_of
        self.agent1 = agent1
        self.agent2 = agent2
        self.scores = {0: 0, 1: 0}  # Player 1 and Player 2 scores
        self.current_game = 0

    def play(self):
        arena = Arena(self.agent1, self.agent2)
        while self.current_game < self.best_of:
            winner, _ = arena.play()
            print(
                f"Game {self.current_game + 1} ended. Winner: Player {winner + 1 if winner is not None else 'None (Draw)'}"
            )
            if winner is not None:
                self.scores[winner] += 1

            if self.scores[0] > self.best_of // 2 or self.scores[1] > self.best_of // 2:
                break

            self.current_game += 1
