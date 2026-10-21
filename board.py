"""The Tic-Tac-Toe board: stores marks and answers questions about them.

Rows and columns are numbered from 0.
"""

SIZE = 3
# CONSTANTS & CONFIGURATION
# Generate all winning line coordinates:
# 1. Horizontal rows
# 2. Vertical columns
# 3. Main and anti-diagonals
_LINES = (
    [[(r, c) for c in range(SIZE)] for r in range(SIZE)]
    + [[(r, c) for r in range(SIZE)] for c in range(SIZE)]
    + [[(i, i) for i in range(SIZE)], [(i, SIZE - 1 - i) for i in range(SIZE)]]
)


class Board:
    """A 3x3 grid. An empty cell holds None; a taken cell holds "X" or "O"."""

    # Creates a 2D list filled with None values to represent the empty board.
    def __init__(self):
        self._grid = [[None] * SIZE for _ in range(SIZE)]

    # A helper function to check if the given row and col are within the bounds of the board.
    def _on_board(self, row, col):
        return 0 <= row < SIZE and 0 <= col < SIZE

    # Check mark elligibility and place it on the board if valid. Return False if the cell is off the board or already taken.
    def place_mark(self, row, col, mark):
        """Place mark at (row, col). Return False if off the board or taken."""
        if not self._on_board(row, col) or self._grid[row][col] is not None:
            return False
        self._grid[row][col] = mark
        return True

    # Function to remove a mark from the board.
    def remove_mark(self, row, col):
        """Clear the cell at (row, col). Does nothing if it is off the board."""
        if self._on_board(row, col):
            self._grid[row][col] = None

    # Function to retrieve the mark at a specific cell on the board. Returns "X", "O", or None.
    def get_mark(self, row, col):
        """Return "X", "O", or None for an empty cell (used for printing)."""
        return self._grid[row][col]

    # Function to return empty cells as a list of (row, col) tuples.
    def empty_cells(self):
        """Return a list of (row, col) tuples for every empty cell."""
        return [
            (r, c)
            for r in range(SIZE)
            for c in range(SIZE)
            if self._grid[r][c] is None
        ]


    def has_won(self, mark):
        """Return True if mark fills a full row, column, or diagonal."""
        for line in _LINES:
            if all(self._grid[r][c] == mark for r, c in line):
                return True
        return False

    def is_full(self):
        """Return True if no empty cells remain."""
        return not self.empty_cells()