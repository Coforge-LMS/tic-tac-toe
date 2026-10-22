# Tic-Tac-Toe

A terminal Tic-Tac-Toe game on a 3x3 board. Play against a friend, or against the computer on Easy or Hard. Hard uses the minimax algorithm and never loses when it plays second.

## Requirements

- Python 3.10 or later
- `pytest` (only needed to run the tests)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the game

```bash
python main.py
```

You will be asked to choose a mode:

1. **Two players**: X and O take turns at the same keyboard.
2. **Versus computer**: you play X, the computer plays O. Then choose a difficulty:
   - **Easy**: the computer picks a random empty cell.
   - **Hard**: the computer uses minimax and never loses when it plays second.

X always goes first.

### How to enter a move

Type a row and a column, numbered from 1, separated by a space. For example, `2 3` is row 2, column 3:

```
    1   2   3
1   X |   |
   ---+---+---
2     | O |
   ---+---+---
3     |   |
```

The board is printed after every move. If you enter a taken cell, a cell off the board, or something that is not two numbers, the game shows a message and asks again. A rejected move does not use up your turn.

Press `Ctrl-C` to quit at any time.

## Run the tests

```bash
pytest
```

The tests use seeded random numbers, so results are the same on every run. The same command runs in CI (`.github/workflows/ci.yml`) on every pull request and on every push to `main`.

## Project layout

| File | Purpose |
|---|---|
| `board.py` | `Board`: the 3x3 grid. Place and remove marks, list empty cells, detect a win or a full board. |
| `game.py` | `Game`: whose turn it is, applying moves, and win or draw detection. |
| `ai.py` | `AI` (abstract base class), `EasyAI`, and `HardAI`. Each has `choose_move(board, mark)`. |
| `main.py` | Menus, prompts, and printing. The only file that uses `print()` and `input()`. |
| `tests/` | pytest tests for the board, game, AI, and terminal interface. |
| `PLAN.md` | The project plan: goal, requirements, components, and design decisions. |

## Design notes

- Game rules are separate from printing and typing. Only `main.py` talks to the player.
- Rows and columns are numbered from 0 inside the code. `main.py` is the one place that converts from the player's 1-based numbers.
- The AI classes take a `random.Random` object, so tests can seed them.
- `Game` calls `choose_move` without knowing whether the AI is Easy or Hard.

