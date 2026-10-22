import pytest
from board import Board

ALL_CELLS = [(r, c) for r in range(3) for c in range(3)]

# Every winning line, by name.
LINES = {
    "row 0": [(0, 0), (0, 1), (0, 2)],
    "row 1": [(1, 0), (1, 1), (1, 2)],
    "row 2": [(2, 0), (2, 1), (2, 2)],
    "col 0": [(0, 0), (1, 0), (2, 0)],
    "col 1": [(0, 1), (1, 1), (2, 1)],
    "col 2": [(0, 2), (1, 2), (2, 2)],
    "main diagonal": [(0, 0), (1, 1), (2, 2)],
    "anti diagonal": [(0, 2), (1, 1), (2, 0)],
}


def test_new_board_is_empty():
    board = Board()
    assert len(board.empty_cells()) == 9
    assert not board.is_full()
    assert not board.has_won("X")
    assert not board.has_won("O")


def test_place_mark_on_empty_cell_succeeds():
    board = Board()
    assert board.place_mark(1, 1, "X") is True
    assert board.get_mark(1, 1) == "X"
    assert (1, 1) not in board.empty_cells()


def test_taken_cell_is_rejected_and_first_mark_stays():
    board = Board()
    board.place_mark(0, 0, "X")
    assert board.place_mark(0, 0, "O") is False
    assert board.get_mark(0, 0) == "X"


@pytest.mark.parametrize("row, col", [
    (-1, 0), (0, -1), (-1, -1), (3, 0), (0, 3), (5, 5)
])
def test_off_board_positions_are_rejected(row, col):
    board = Board()
    assert board.place_mark(row, col, "X") is False
    assert len(board.empty_cells()) == 9


def test_remove_mark_clears_a_cell():
    board = Board()
    board.place_mark(2, 2, "O")
    board.remove_mark(2, 2)
    assert (2, 2) in board.empty_cells()
    assert board.place_mark(2, 2, "X") is True


def test_remove_mark_off_board_does_nothing():
    board = Board()
    board.remove_mark(-1, 5)
    assert len(board.empty_cells()) == 9


@pytest.mark.parametrize("line", LINES.values(), ids=LINES.keys())
def test_x_wins_on_every_line(line):
    # X has the whole line; O has two marks elsewhere (X moved first, so X=3, O=2 is legal).
    board = Board()
    for row, col in line:
        board.place_mark(row, col, "X")
    for row, col in [cell for cell in ALL_CELLS if cell not in line][:2]:
        board.place_mark(row, col, "O")
    assert board.has_won("X")
    assert not board.has_won("O")


def test_o_can_win_too():
    # O completes column 0; X has three marks elsewhere that make no line.
    board = Board()
    for row, col in [(0, 0), (1, 0), (2, 0)]:
        board.place_mark(row, col, "O")
    for row, col in [(0, 1), (1, 2), (2, 1)]:
        board.place_mark(row, col, "X")
    assert board.has_won("O")
    assert not board.has_won("X")


def test_two_in_a_line_is_not_a_win():
    board = Board()
    board.place_mark(0, 0, "X")
    board.place_mark(1, 1, "O")
    board.place_mark(0, 1, "X")
    assert not board.has_won("X")


def test_a_line_with_both_marks_is_not_a_win():
    # X X O across the top row: full, but not all the same mark.
    board = Board()
    board.place_mark(0, 0, "X")
    board.place_mark(0, 2, "O")
    board.place_mark(0, 1, "X")
    assert not board.has_won("X")
    assert not board.has_won("O")


def test_full_board_with_no_winner_is_a_draw():
    board = Board()
    # X O X
    # X O O
    # O X X
    layout = [
        ("X", "O", "X"),
        ("X", "O", "O"),
        ("O", "X", "X")
    ]
    for r, row_marks in enumerate(layout):
        for c, mark in enumerate(row_marks):
            board.place_mark(r, c, mark)

    assert board.is_full()
    assert not board.has_won("X")
    assert not board.has_won("O")
