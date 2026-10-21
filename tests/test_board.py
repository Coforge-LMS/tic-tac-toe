import pytest
from board import Board

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

def test_win_across_a_row():
    board = Board()
    for col in range(3):
        board.place_mark(1, col, "X")
    assert board.has_won("X")
    assert not board.has_won("O")

def test_win_down_a_column():
    board = Board()
    for row in range(3):
        board.place_mark(row, 2, "O")
    assert board.has_won("O")
    assert not board.has_won("X")

def test_win_on_main_diagonal():
    board = Board()
    for i in range(3):
        board.place_mark(i, i, "X")
    assert board.has_won("X")

def test_win_on_anti_diagonal():
    board = Board()
    for i in range(3):
        board.place_mark(i, 2 - i, "O")
    assert board.has_won("O")

def test_two_in_a_line_is_not_a_win():
    board = Board()
    board.place_mark(0, 0, "X")
    board.place_mark(0, 1, "X")
    assert not board.has_won("X")

def test_full_board_with_no_winner_is_a_draw():
    board = Board()
    # Representing a draw layout:
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
