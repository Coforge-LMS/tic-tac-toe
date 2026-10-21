"""Terminal interface for Tic-Tac-Toe.

This is the only file that prints or reads input. It is also the only place
that converts the player's 1-based numbers into the 0-based rows and columns
used everywhere else.
"""

from board import SIZE
from game import Game

PROMPT_HELP = "Enter a row and a column from 1 to 3, like: 2 3"


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


def play_two_players():
    """Run one two-player game in the terminal."""
    game = Game()
    print(format_board(game.board))

    while not game.is_over:
        text = input(f"Player {game.current_mark}, your move ({PROMPT_HELP}): ")
        try:
            row, col = parse_move(text)
        except ValueError:
            print(f"That is not a valid move. {PROMPT_HELP}")
            continue

        if not game.play(row, col):
            print("That cell is taken or off the board. Try again.")
            continue

        print()
        print(format_board(game.board))

    if game.winner is not None:
        print(f"Player {game.winner} wins!")
    else:
        print("It's a draw!")


def main():
    print("Tic-Tac-Toe")
    try:
        play_two_players()
    except (KeyboardInterrupt, EOFError):
        print("\nGame cancelled.")


if __name__ == "__main__":
    main()