"""Game rules: whose turn it is and whether the game is won or drawn.
"""

from board import Board


class Game:
    """One match of Tic-Tac-Toe. X always moves first."""

    def __init__(self, board=None):
        self.board = board if board is not None else Board()
        self.current_mark = "X"
        self.winner = None  # "X", "O", or None
        self.is_draw = False

    # Read only property to check if the game is over (either won or drawn).
    @property
    def is_over(self):
        """True once someone has won or the board is full with no winner."""
        return self.winner is not None or self.is_draw

    def play(self, row, col):
        """Place the current player's mark at (row, col).

        Return True if the move was made. Return False if the game is over,
        the cell is taken, or the cell is off the board. A rejected move does
        not use up the turn.
        """

        #check game is over or not
        if self.is_over:
            return False
        
        #check if the cell is taken or off the board
        if not self.board.place_mark(row, col, self.current_mark):
            return False

        #Win/Draw/Next Turn  check
        if self.board.has_won(self.current_mark):
            self.winner = self.current_mark
        elif self.board.is_full():
            self.is_draw = True
        else:
            self.current_mark = "O" if self.current_mark == "X" else "X"
        return True