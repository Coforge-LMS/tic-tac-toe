# Tic-Tac-Toe with AI Opponent: Plan

## Goal

This project is a terminal Tic-Tac-Toe game on a 3x3 board that supports two human players or one human against a computer opponent. It is played by anyone who can run Python 3.10+ in a terminal, choosing between an Easy (random) and a Hard (unbeatable) computer opponent.

## Requirements

| ID | Requirement | How I will verify it |
|----|-------------|----------------------|
| R1 | A new board is empty and X always moves first; turns alternate X, O, X, O. | pytest: new `Board` has 9 empty cells; `Game` test checks the current mark after each valid move. |
| R2 | A move to a taken cell is rejected and the original mark stays. | pytest: `place_mark` returns `False` on a taken cell and the cell still holds the first mark. |
| R3 | A move off the board (including negative numbers) is rejected. | pytest: `place_mark(-1, 0, "X")`, `place_mark(0, 3, "X")`, etc. all return `False` and the board is unchanged. |
| R4 | An invalid move (taken, off board, or non-numeric input) shows a message and does not use up the turn. | pytest: after a rejected move, the same player is still the current player. Manual run of `main.py` with typed bad input such as `abc` and `9 9`. |
| R5 | A win is detected across a row, down a column, and on both diagonals. | pytest: one test per direction plus both diagonals using `has_won`. |
| R6 | A full board with no winner is a draw. | pytest: fill the board in a no-win pattern; `is_full()` is `True` and neither `has_won("X")` nor `has_won("O")` is `True`. |
| R7 | The abstract AI base class cannot be instantiated directly. | pytest: `AI()` raises `TypeError`. |
| R8 | Easy always returns a cell that is currently empty. | pytest: with a seeded `random.Random`, call `choose_move` on boards at several fill levels and assert the result is in `empty_cells()`. |
| R9 | Hard takes a winning move when one exists. | pytest: set up a board where O (or X) has two in a line; assert `HardAI.choose_move` returns the third cell. |
| R10 | Hard never loses on 3x3 when it plays second. | pytest: play Hard as O against every possible sequence of X moves (exhaustive search) and assert X never wins. |
| R11 | `choose_move` leaves the board unchanged. | pytest: copy the grid before the call, call `choose_move` for Easy and Hard, and compare the grid afterwards. |
| R12 | Only `main.py` uses `print()` and `input()`. | Search the other `.py` files with `grep -n "print(\|input(" board.py ai.py game.py` and confirm no matches. |

## Components

- **`board.py` (`Board`)**: Owns the 3x3 grid (stored in a private `_grid` attribute) and answers questions about it: place or remove a mark, list empty cells, detect a win, and detect a full board.
- **`ai.py` (`AI`, `EasyAI`, `HardAI`)**: Defines the abstract `AI` base class with `choose_move(board, mark)`, and the two subclasses that pick a move by random choice (Easy) or by minimax (Hard).
- **`game.py` (`Game`)**: Runs the rules of a match (whose turn it is, applying moves, and reporting win, draw, or in-progress) without any printing or typing.
- **`main.py`**: The only file that talks to the player: menus, prompts, printing the board, and converting the player's 1-based numbers to 0-based indexes.
- **`tests/`**: pytest files that verify the requirements above.
- **`.github/workflows/ci.yml`**: Runs `pytest` on every pull request and on every push to `main`.

## Decisions

### Decision 1: How Hard chooses a move

- **Options considered:** (a) hand-written priority rules (win, block, centre, corner); (b) minimax over the full game tree; (c) minimax with alpha-beta pruning.
- **Chosen:** (b) plain minimax.
- **Why:** The assignment requires minimax, and the 3x3 game tree is small enough (under about 550,000 nodes from an empty board) that pruning is not needed. Plain minimax is easier to read and to prove correct. Rule-based play can have gaps that let the opponent win, which would break R10.

### Decision 2: How minimax tries moves on the board

- **Options considered:** (a) copy the whole board for every candidate move; (b) place a mark, recurse, then call `remove_mark` to undo it.
- **Chosen:** (b) place and undo on the same board.
- **Why:** The required `Board` API already includes `remove_mark`, which exists for this purpose. It avoids creating thousands of board copies. The cost is that a bug in the undo step could leave the board changed, so R11 has a test specifically checking that `choose_move` leaves the board unchanged.

### Decision 3: Where coordinates are converted

- **Options considered:** (a) convert 1-based to 0-based inside `Board`; (b) convert inside `Game`; (c) convert only in `main.py`.
- **Chosen:** (c) convert only in `main.py`.
- **Why:** The assignment requires one conversion point. Keeping every other file on 0-based indexes means tests and the AI use the same numbering with no off-by-one risk. The player's numbering is a display concern, so it belongs with the other input and output code.

### Decision 4: How randomness reaches the AI

- **Options considered:** (a) call the global `random` module directly; (b) pass a `random.Random` object into the AI constructor.
- **Chosen:** (b) inject `random.Random`.
- **Why:** A seeded `Random` makes Easy's behaviour repeatable in tests (R8), and the assignment forbids tests that depend on unseeded randomness. `main.py` creates a normal unseeded `Random()` for real play.

## What changed

Changes from the plan above, and why.

- **Added `Board.get_mark(row, col)`.** The plan listed only place, remove, empty cells, win and full. But `_grid` is private and `main.py` has to print the board, so it needs a read-only way to see a cell. Tests also use it to compare boards without touching `_grid`.
- **Hard also uses the injected `Random`.** Decision 4 only mentioned Easy. Hard picks among equally good moves with the same `Random`, so its choices are repeatable in tests too. Hard scores a win as `10 - depth` and a loss as `depth - 10`, so it prefers quicker wins and slower losses.
- **One game loop for both modes.** The plan treated the two modes separately. `main.py` has a single `play_game(ai=None)`: `None` means two players, otherwise the computer plays O. This removed duplicate input handling.
- **R12 is now an automated test.** The plan said to check "no `print()` or `input()` outside `main.py`" with a manual `grep`. `tests/test_design.py` now checks `board.py`, `ai.py` and `game.py` on every run.
- **The tests grew past the first plan.**
  - **Win lines:** `has_won` is tested on all 8 winning lines. I first tested one row and one column, and a break in the other lines went unnoticed.
  - **Last-move win:** a win on the 9th move must count as a win, not a draw.
  - **`main()`:** the mode menu and Ctrl-C / EOF handling are tested, and the board is checked to print after every move.
  - **Hard (R10):** it is now checked with three seeds, and the test also confirms it really played hundreds of games and undid every move. Before this, a bug in the undo step could make the test pass without searching the whole tree.
- **Impossible test positions removed.** A review of the tests found positions that can never happen in a real game, such as two X's against two O's with O to move, or three O's with no X. Tests now use legal positions, and the `board_from` helper in `tests/test_ai.py` rejects an impossible layout.
- **README added** with how to run the game and the tests.