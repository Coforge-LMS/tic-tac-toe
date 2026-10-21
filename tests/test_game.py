from game import Game


def play_all(game, moves):
    """Play a list of (row, col) moves, asserting each one is accepted."""
    for row, col in moves:
        assert game.play(row, col) is True


def test_x_goes_first():
    game = Game()
    assert game.current_mark == "X"
    assert not game.is_over


def test_turns_alternate():
    game = Game()
    game.play(0, 0)
    assert game.current_mark == "O"
    game.play(1, 1)
    assert game.current_mark == "X"
    game.play(2, 2)
    assert game.current_mark == "O"


def test_taken_cell_does_not_use_up_the_turn():
    game = Game()
    game.play(0, 0)  # X
    assert game.play(0, 0) is False  # O tries the same cell
    assert game.current_mark == "O"
    assert game.board.get_mark(0, 0) == "X"


def test_off_board_move_does_not_use_up_the_turn():
    game = Game()
    assert game.play(-1, 0) is False
    assert game.play(0, 3) is False
    assert game.current_mark == "X"
    assert len(game.board.empty_cells()) == 9


def test_x_wins_and_game_is_over():
    game = Game()
    # X takes the top row; O wastes moves in the middle row.
    play_all(game, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    assert game.winner == "X"
    assert game.is_over
    assert not game.is_draw


def test_o_can_win():
    game = Game()
    # O takes the left column.
    play_all(game, [(0, 1), (0, 0), (0, 2), (1, 0), (1, 1), (2, 0)])
    assert game.winner == "O"
    assert game.is_over


def test_draw_is_detected():
    game = Game()
    # Final board:  X O X
    #               X O O
    #               O X X
    play_all(
        game,
        [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)],
    )
    assert game.is_draw
    assert game.winner is None
    assert game.is_over


def test_no_moves_allowed_after_game_over():
    game = Game()
    play_all(game, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])  # X wins
    assert game.play(2, 2) is False
    assert game.board.get_mark(2, 2) is None