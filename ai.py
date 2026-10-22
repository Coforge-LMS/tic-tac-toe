"""Computer opponents for Tic-Tac-Toe.

Every AI has the same method, choose_move(board, mark), so the game can use
any of them without knowing which level it has.
"""

#By inheritance, the EasyAI and HardAI classes implement the choose_move method from the AI base class.
from abc import ABC, abstractmethod


class AI(ABC):
    """Base class for computer players."""

    @abstractmethod
    def choose_move(self, board, mark):
        """Return a (row, col) tuple for an empty cell, for the given mark."""


class EasyAI(AI):
    """Picks a random empty cell."""

    def __init__(self, rng):
        self._rng = rng

    def choose_move(self, board, mark):
        return self._rng.choice(board.empty_cells())


class HardAI(AI):
    """Never loses: uses minimax to pick one of the best moves.

    Scores are from the point of view of the AI's own mark. A win scores
    10 - depth and a loss scores depth - 10, so quicker wins and slower losses
    are preferred. A draw scores 0. When several moves tie for best, the
    injected random number generator picks one of them.
    """

    def __init__(self, rng):
        self._rng = rng

    def choose_move(self, board, mark):
        opponent = _other(mark)
        best_score = None
        best_moves = []

        for row, col in board.empty_cells():
            board.place_mark(row, col, mark)
            score = self._minimax(board, opponent, mark, 1)
            board.remove_mark(row, col)  # undo, so the board is unchanged

            if best_score is None or score > best_score:
                best_score = score
                best_moves = [(row, col)]
            elif score == best_score:
                best_moves.append((row, col))

        return self._rng.choice(best_moves)

    def _minimax(self, board, to_move, me, depth):
        """Score the position for `me`, with `to_move` about to play."""
        opponent = _other(me)
        if board.has_won(me):
            return 10 - depth
        if board.has_won(opponent):
            return depth - 10
        if board.is_full():
            return 0

        scores = []
        for row, col in board.empty_cells():
            board.place_mark(row, col, to_move)
            scores.append(self._minimax(board, _other(to_move), me, depth + 1))
            board.remove_mark(row, col)

        return max(scores) if to_move == me else min(scores)


def _other(mark):
    return "O" if mark == "X" else "X"