"""Terminal interface for Tic-Tac-Toe.

This is the only file that prints or reads input. It is also the only place
that converts between the player's 1-based numbers and the 0-based rows and
columns used everywhere else.
"""

import random

from ai import EasyAI, HardAI
from board import SIZE
from game import Game

PROMPT_HELP = "Enter a row and a column from 1 to 3, like: 2 3"
HUMAN_MARK = "X"
COMPUTER_MARK = "O"


def format_board(board):
    """Return the board as a multi-line string with row and column numbers."""
    lines = ["    " + "   ".join(str(c + 1) for c in range(SIZE))]
    for r in range(SIZE):
        cells = [board.get_mark(r, c) or " " for c in range(SIZE)]
        lines.append(f"{r + 1}   " + " | ".join(cells))
        if r < SIZE - 1:
            lines.append("   " + "+".join(["---"] * SIZE))
    return "\n".join(lines)


def parse_move(text):
    """Turn text like "2 3" into the 0-based tuple (1, 2).

    Raises ValueError if the text is not exactly two whole numbers. It does not
    check the board: a number off the board is caught later by Game.play.
    """
    parts = text.split()
    if len(parts) != 2:
        raise ValueError("expected two numbers")
    row, col = int(parts[0]), int(parts[1])
    return row - 1, col - 1


def ask_choice(title, options):
    """Show a numbered menu and keep asking until the player picks one.

    options is a list of labels. Returns the 0-based index of the choice.
    """
    print(title)
    for number, label in enumerate(options, start=1):
        print(f"  {number}) {label}")
    while True:
        text = input(f"Choose 1-{len(options)}: ").strip()
        if text.isdigit() and 1 <= int(text) <= len(options):
            return int(text) - 1
        print(f"Please type a number from 1 to {len(options)}.")


def ask_human_move(game):
    """Ask the current human player for moves until one is accepted."""
    while True:
        text = input(f"Player {game.current_mark}, your move ({PROMPT_HELP}): ")
        try:
            row, col = parse_move(text)
        except ValueError:
            print(f"That is not a valid move. {PROMPT_HELP}")
            continue
        if game.play(row, col):
            return
        print("That cell is taken or off the board. Try again.")


def play_computer_move(game, ai):
    """Let the AI play the current turn and say where it went."""
    row, col = ai.choose_move(game.board, game.current_mark)
    mark = game.current_mark
    game.play(row, col)
    print(f"Computer ({mark}) plays {row + 1} {col + 1}")


def play_game(ai=None):
    """Run one game. With ai=None it is two players; otherwise the human is X
    and the computer (the given AI) is O."""
    game = Game()
    print(format_board(game.board))

    while not game.is_over:
        if ai is not None and game.current_mark == COMPUTER_MARK:
            play_computer_move(game, ai)
        else:
            ask_human_move(game)
        print()
        print(format_board(game.board))

    if game.winner is not None:
        print(f"Player {game.winner} wins!")
    else:
        print("It's a draw!")


def play_two_players():
    """Run one two-player game in the terminal."""
    play_game(ai=None)


def play_versus_computer(rng=None):
    """Ask for a difficulty, then run a game against the computer."""
    rng = rng if rng is not None else random.Random()
    level = ask_choice("Choose a difficulty:", ["Easy", "Hard"])
    ai = EasyAI(rng) if level == 0 else HardAI(rng)
    print(f"You are {HUMAN_MARK}. The computer is {COMPUTER_MARK}.")
    play_game(ai=ai)


def main():
    print("Tic-Tac-Toe")
    try:
        mode = ask_choice("Choose a mode:", ["Two players", "Versus computer"])
        if mode == 0:
            play_two_players()
        else:
            play_versus_computer()
    except (KeyboardInterrupt, EOFError):
        print("\nGame cancelled.")


if __name__ == "__main__":
    main()