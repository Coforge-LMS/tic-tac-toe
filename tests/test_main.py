import random

import pytest

from ai import AI, EasyAI, HardAI
from board import Board
from game import Game
from main import (
    ask_choice,
    format_board,
    main,
    parse_move,
    play_game,
    play_two_players,
    play_versus_computer,
)


def script_input(monkeypatch, answers):
    """Make input() return the given answers one at a time.

    Returns the list of prompts input() was called with, in order.
    """
    answers = iter(answers)
    prompts = []

    def fake_input(prompt=""):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)
    return prompts


def count_boards(output):
    """How many times the board was printed (each print starts with a 1 2 3 header)."""
    return sum(1 for line in output.splitlines() if line.split() == ["1", "2", "3"])


class ScriptedAI(AI):
    """A test AI that plays a fixed list of (row, col) moves."""

    def __init__(self, moves):
        self._moves = iter(moves)

    def choose_move(self, board, mark):
        return next(self._moves)


# --- parsing and printing ----------------------------------------------------


def test_parse_move_converts_to_zero_based():
    assert parse_move("2 3") == (1, 2)
    assert parse_move("1 1") == (0, 0)


def test_parse_move_ignores_extra_spaces():
    assert parse_move("  3    1  ") == (2, 0)


@pytest.mark.parametrize("text", ["abc", "", "1", "1 2 3", "a b", "1.5 2", "1,2"])
def test_parse_move_rejects_bad_text(text):
    with pytest.raises(ValueError):
        parse_move(text)


def test_parse_move_leaves_off_board_numbers_for_the_game_to_reject():
    assert parse_move("0 0") == (-1, -1)
    assert Game().play(-1, -1) is False


def test_format_board_shows_marks_and_numbers():
    board = Board()
    board.place_mark(0, 0, "X")
    board.place_mark(1, 1, "O")
    lines = format_board(board).splitlines()
    assert lines[0].split() == ["1", "2", "3"]

    def cells(line):  # drop the row number, split on the "|" separators
        return [cell.strip() for cell in line[4:].split("|")]

    assert cells(lines[1]) == ["X", "", ""]
    assert cells(lines[3]) == ["", "O", ""]
    assert cells(lines[5]) == ["", "", ""]


# --- two-player mode ---------------------------------------------------------


def test_bad_input_does_not_use_up_the_turn(monkeypatch, capsys):
    # X: "abc" (not numbers), then four off-board tries (9 9, 0 1, 1 0, -1 2), then 1 1.
    # O: "1 1" (taken), then 2 1.  Then X 1 2, O 2 2, X 1 3 wins.
    prompts = script_input(
        monkeypatch,
        ["abc", "9 9", "0 1", "1 0", "-1 2", "1 1", "1 1", "2 1", "1 2", "2 2", "1 3"],
    )
    play_two_players()
    out = capsys.readouterr().out
    assert out.count("not a valid move") == 1
    assert out.count("taken or off the board") == 5
    # Whoever made a bad move is asked again, not the other player.
    asked = [prompt[:8] for prompt in prompts]
    assert asked == ["Player X"] * 6 + ["Player O"] * 2 + ["Player X", "Player O", "Player X"]
    assert "Player X wins!" in out


def test_board_is_printed_after_every_move(monkeypatch, capsys):
    # 5 moves: the starting board plus one print after each move. A rejected
    # entry ("abc", "1 1" again) is not a move, so it prints no board.
    script_input(monkeypatch, ["abc", "1 1", "1 1", "2 1", "1 2", "2 2", "1 3"])
    play_two_players()
    assert count_boards(capsys.readouterr().out) == 6


def test_game_reports_a_draw(monkeypatch, capsys):
    # Final board:  X O X
    #               X O O
    #               O X X
    moves = ["1 1", "1 2", "1 3", "2 2", "2 1", "2 3", "3 2", "3 1", "3 3"]
    script_input(monkeypatch, moves)
    play_two_players()
    assert "It's a draw!" in capsys.readouterr().out


# --- menus -------------------------------------------------------------------


def test_ask_choice_returns_zero_based_index(monkeypatch):
    script_input(monkeypatch, ["2"])
    assert ask_choice("Pick:", ["a", "b"]) == 1


def test_ask_choice_retries_on_bad_input(monkeypatch, capsys):
    script_input(monkeypatch, ["", "x", "0", "3", "1"])
    assert ask_choice("Pick:", ["a", "b"]) == 0
    assert capsys.readouterr().out.count("Please type a number") == 4


def test_difficulty_menu_picks_the_matching_ai(monkeypatch):
    chosen = []
    monkeypatch.setattr("main.play_game", lambda ai=None: chosen.append(type(ai)))
    script_input(monkeypatch, ["1"])
    play_versus_computer(random.Random(0))
    script_input(monkeypatch, ["2"])
    play_versus_computer(random.Random(0))
    assert chosen == [EasyAI, HardAI]


def test_mode_menu_picks_the_matching_mode(monkeypatch):
    started = []
    monkeypatch.setattr("main.play_two_players", lambda: started.append("two players"))
    monkeypatch.setattr("main.play_versus_computer", lambda: started.append("computer"))
    script_input(monkeypatch, ["1"])
    main()
    script_input(monkeypatch, ["2"])
    main()
    assert started == ["two players", "computer"]


@pytest.mark.parametrize("error", [KeyboardInterrupt, EOFError])
def test_main_exits_quietly_when_input_is_cancelled(monkeypatch, capsys, error):
    def cancel(prompt=""):
        raise error

    monkeypatch.setattr("builtins.input", cancel)
    main()  # must not raise
    assert "Game cancelled." in capsys.readouterr().out


# --- versus-computer mode ----------------------------------------------------


def test_human_is_x_and_computer_is_o(monkeypatch, capsys):
    # X takes the top row; the scripted O plays (1, 0) then (1, 1), 0-based.
    script_input(monkeypatch, ["1 1", "1 2", "1 3"])
    play_game(ai=ScriptedAI([(1, 0), (1, 1)]))
    out = capsys.readouterr().out
    assert "Computer (O) plays 2 1" in out
    assert "Computer (O) plays 2 2" in out
    assert "Player X wins!" in out
    assert count_boards(out) == 6  # start + 3 human moves + 2 computer moves


def test_computer_can_win(monkeypatch, capsys):
    # O takes the left column; X plays elsewhere.
    script_input(monkeypatch, ["1 2", "2 2", "3 3"])
    play_game(ai=ScriptedAI([(0, 0), (1, 0), (2, 0)]))
    assert "Player O wins!" in capsys.readouterr().out


def test_bad_human_input_in_computer_mode_keeps_the_turn(monkeypatch, capsys):
    script_input(monkeypatch, ["abc", "9 9", "1 1", "1 1", "1 2", "1 3"])
    play_game(ai=ScriptedAI([(1, 0), (1, 1)]))
    out = capsys.readouterr().out
    assert out.count("not a valid move") == 1
    assert out.count("taken or off the board") == 2
    assert "Player X wins!" in out


def test_hard_computer_beats_a_human_who_takes_the_first_free_cell(monkeypatch, capsys):
    # Work out the human's moves by playing the same game on a plain Game with
    # an identically seeded HardAI, then feed those moves to play_game.
    # (Both runs must make the same rng calls, so keep the seeds equal.)
    sim = Game()
    sim_ai = HardAI(random.Random(5))
    typed = []
    while not sim.is_over:
        if sim.current_mark == "X":
            row, col = sim.board.empty_cells()[0]
            typed.append(f"{row + 1} {col + 1}")
        else:
            row, col = sim_ai.choose_move(sim.board, "O")
        sim.play(row, col)

    script_input(monkeypatch, typed)
    play_game(ai=HardAI(random.Random(5)))
    out = capsys.readouterr().out
    assert "Player O wins!" in out
    assert "Player X wins!" not in out
