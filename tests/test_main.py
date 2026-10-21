import pytest

from board import Board
from main import format_board, parse_move, play_two_players


def script_input(monkeypatch, answers):
    """Make input() return the given answers one at a time."""
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))


def test_parse_move_converts_to_zero_based():
    assert parse_move("2 3") == (1, 2)
    assert parse_move("1 1") == (0, 0)


def test_parse_move_ignores_extra_spaces():
    assert parse_move("  3    1  ") == (2, 0)


@pytest.mark.parametrize("text", ["abc", "", "1", "1 2 3", "a b", "1.5 2", "1,2"])
def test_parse_move_rejects_bad_text(text):
    with pytest.raises(ValueError):
        parse_move(text)


def test_format_board_shows_marks_and_numbers():
    board = Board()
    board.place_mark(0, 0, "X")
    board.place_mark(1, 1, "O")
    text = format_board(board)
    assert "1   X |   |  " in text
    assert "2     | O |  " in text
    assert text.splitlines()[0].split() == ["1", "2", "3"]


def test_bad_input_does_not_use_up_the_turn(monkeypatch, capsys):
    # X: "abc" (bad), "9 9" (off board), "1 1" (ok), then O: "1 1" (taken).
    # After the taken-cell error O must still be the one asked to move.
    script_input(
        monkeypatch,
        ["abc", "9 9", "1 1", "1 1", "2 1", "1 2", "2 2", "1 3"],
    )
    play_two_players()
    out = capsys.readouterr().out
    assert out.count("not a valid move") == 1
    assert out.count("taken or off the board") == 2
    assert "Player X wins!" in out


def test_game_reports_a_draw(monkeypatch, capsys):
    # Final board:  X O X
    #               X O O
    #               O X X
    moves = ["1 1", "1 2", "1 3", "2 2", "2 1", "2 3", "3 2", "3 1", "3 3"]
    script_input(monkeypatch, moves)
    play_two_players()
    assert "It's a draw!" in capsys.readouterr().out