import random

import pytest

from ai import AI, EasyAI, HardAI
from board import Board

SEEDS = [0, 1, 2]


def board_from(layout):
    """Build a Board from three strings such as "XX.", "OO.", "...".

    "X" and "O" are marks and "." is an empty cell. Refuses layouts that
    cannot happen in a real game, so a test can't quietly use one.
    """
    board = Board()
    for r, line in enumerate(layout):
        for c, ch in enumerate(line):
            if ch != ".":
                board.place_mark(r, c, ch)

    x = sum(line.count("X") for line in layout)
    o = sum(line.count("O") for line in layout)
    assert x - o in (0, 1), f"impossible position {layout}: X={x} O={o}"
    assert not (board.has_won("X") and board.has_won("O")), f"both won: {layout}"
    assert not board.has_won("X") or x == o + 1, f"X won but O moved after: {layout}"
    assert not board.has_won("O") or x == o, f"O won but X moved after: {layout}"
    return board


def side_to_move(board):
    """X moves when an even number of marks are down, O when it is odd."""
    return "X" if len(board.empty_cells()) % 2 == 1 else "O"


def snapshot(board):
    """Read every cell through the public API (the grid is private)."""
    return [[board.get_mark(r, c) for c in range(3)] for r in range(3)]


class RecordingRng:
    """A stand-in for random.Random that records what it was asked to choose from."""

    def __init__(self):
        self.seen = None

    def choice(self, seq):
        self.seen = list(seq)
        return seq[-1]


# --- the abstract base class -------------------------------------------------


def test_abstract_ai_cannot_be_created_directly():
    with pytest.raises(TypeError):
        AI()


def test_easy_and_hard_are_ai_subclasses():
    assert isinstance(EasyAI(random.Random(0)), AI)
    assert isinstance(HardAI(random.Random(0)), AI)


# --- EasyAI ------------------------------------------------------------------

# Each layout is a position that can occur in a real game.
EASY_LAYOUTS = [
    ["...", "...", "..."],
    ["X..", "...", "..."],
    ["XO.", "X..", "..."],
    ["XOX", "OXO", "..."],
    ["XOX", "XOO", "OX."],
]


@pytest.mark.parametrize("layout", EASY_LAYOUTS)
def test_easy_always_returns_an_empty_cell(layout):
    board = board_from(layout)
    ai = EasyAI(random.Random(1))
    for _ in range(50):
        assert ai.choose_move(board, side_to_move(board)) in board.empty_cells()


def test_easy_picks_the_only_empty_cell():
    board = board_from(["XOX", "XOO", "OX."])
    assert EasyAI(random.Random(0)).choose_move(board, "X") == (2, 2)


def test_easy_chooses_from_exactly_the_empty_cells_using_the_given_rng():
    board = board_from(["XO.", "X..", "..."])
    rng = RecordingRng()
    move = EasyAI(rng).choose_move(board, "O")
    assert rng.seen == board.empty_cells()
    assert move == board.empty_cells()[-1]  # whatever the rng returned


def test_easy_is_repeatable_with_the_same_seed():
    board = Board()
    first = EasyAI(random.Random(42))
    second = EasyAI(random.Random(42))
    assert [first.choose_move(board, "X") for _ in range(10)] == [
        second.choose_move(board, "X") for _ in range(10)
    ]


def test_easy_different_seeds_give_different_sequences():
    board = Board()
    a = EasyAI(random.Random(1))
    b = EasyAI(random.Random(2))
    assert [a.choose_move(board, "X") for _ in range(20)] != [
        b.choose_move(board, "X") for _ in range(20)
    ]


def test_easy_can_pick_every_empty_cell():
    ai = EasyAI(random.Random(7))
    board = Board()
    moves = {ai.choose_move(board, "X") for _ in range(200)}
    assert moves == set(board.empty_cells())


# --- HardAI ------------------------------------------------------------------


@pytest.mark.parametrize("seed", SEEDS)
def test_hard_takes_a_winning_move(seed):
    # O to move. O wins at (1, 2); X also threatens (0, 2), so Hard must win, not block.
    board = board_from(["XX.", "OO.", "X.."])
    assert side_to_move(board) == "O"
    assert HardAI(random.Random(seed)).choose_move(board, "O") == (1, 2)


@pytest.mark.parametrize("seed", SEEDS)
def test_hard_takes_a_winning_move_as_x(seed):
    # X to move. X wins at (2, 0); O also threatens (2, 2).
    board = board_from(["X.O", "X.O", "..."])
    assert side_to_move(board) == "X"
    assert HardAI(random.Random(seed)).choose_move(board, "X") == (2, 0)


@pytest.mark.parametrize("seed", SEEDS)
def test_hard_blocks_the_opponents_win(seed):
    board = board_from(["XX.", ".O.", "..."])
    assert side_to_move(board) == "O"
    assert HardAI(random.Random(seed)).choose_move(board, "O") == (0, 2)


def test_hard_on_an_empty_board_picks_a_cell_and_leaves_the_board_alone():
    # Smoke test: this is the biggest search Hard ever does.
    board = Board()
    move = HardAI(random.Random(0)).choose_move(board, "X")
    assert move in board.empty_cells()
    assert len(board.empty_cells()) == 9


@pytest.mark.parametrize("ai_class", [EasyAI, HardAI])
def test_choose_move_leaves_the_board_unchanged(ai_class):
    board = board_from(["X..", ".O.", "..X"])
    before = snapshot(board)
    ai_class(random.Random(3)).choose_move(board, side_to_move(board))
    assert snapshot(board) == before


def play_every_x_move(board, ai):
    """Try every X move at every turn, with Hard (O) replying each time.

    Fails if X ever wins. Returns the number of finished games it reached.
    """
    games = 0
    for row, col in board.empty_cells():
        board.place_mark(row, col, "X")
        assert not board.has_won("X"), "X beat the Hard AI"
        if board.is_full():
            games += 1
        else:
            o_row, o_col = ai.choose_move(board, "O")
            board.place_mark(o_row, o_col, "O")
            if board.has_won("O") or board.is_full():
                games += 1
            else:
                games += play_every_x_move(board, ai)
            board.remove_mark(o_row, o_col)
        board.remove_mark(row, col)
    return games


@pytest.mark.parametrize("seed", SEEDS)
def test_hard_never_loses_when_it_plays_second(seed):
    board = Board()
    games = play_every_x_move(board, HardAI(random.Random(seed)))
    assert games > 100  # the search really ran (about 500-600 games)
    assert len(board.empty_cells()) == 9  # and every move was undone
