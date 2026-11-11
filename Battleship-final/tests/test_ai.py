"""Tests for the computer opponent, especially the clue deduction (level 3)."""

from computer import ComputerAI, analyse_board, neighbours, read_board


def empty_board():
    return [[None] * 10 for _ in range(10)]


def test_read_board_sorts_values_into_clues_shots_and_ships():
    board = empty_board()
    board[0][0] = 3          # clue number
    board[0][1] = "hit"
    board[0][2] = "miss"
    board[0][3] = "sunk"

    clues, ships, sunk, shots = read_board(board)

    assert clues == {(0, 0): 3}
    assert ships == {(0, 1)}
    assert sunk == {(0, 3)}
    assert shots == {(0, 1), (0, 2), (0, 3)}


def test_neighbours_stay_on_the_board():
    assert len(list(neighbours(5, 5))) == 8
    assert len(list(neighbours(0, 0))) == 3
    assert (0, 0) not in list(neighbours(0, 0))


def test_zero_clue_proves_the_whole_neighbourhood_is_water():
    board = empty_board()
    board[5][5] = 0

    safe, certain = analyse_board(board)

    assert len(safe) == 8
    assert (5, 5) not in safe            # the clue square itself is not water
    assert certain == set()


def test_zero_clue_at_a_corner_proves_three_squares():
    board = empty_board()
    board[0][0] = 0

    safe, certain = analyse_board(board)

    assert safe == {(0, 1), (1, 0), (1, 1)}


def test_clue_saturated_by_hits_proves_the_rest_is_water():
    board = empty_board()
    board[5][5] = 2
    board[4][4] = "hit"
    board[4][5] = "hit"

    safe, certain = analyse_board(board)

    assert len(safe) == 6                # 8 neighbours - the 2 known ships
    assert (4, 4) not in safe
    assert (4, 5) not in safe
    assert certain == set()


def test_clue_that_only_fits_if_every_unknown_is_a_ship():
    board = empty_board()
    board[5][5] = 2
    # Six of the eight neighbours have already been fired at and missed
    for cell in [(4, 4), (4, 6), (5, 4), (5, 6), (6, 4), (6, 6)]:
        board[cell[0]][cell[1]] = "miss"
    board[4][5] = None
    board[6][5] = None

    safe, certain = analyse_board(board)

    assert certain == {(4, 5), (6, 5)}
    assert safe == set()


def test_sunk_squares_are_not_counted_as_unknown_ships():
    board = empty_board()
    board[5][5] = 0
    board[4][4] = "sunk"

    safe, certain = analyse_board(board)

    assert (4, 4) not in safe            # already resolved, not "water"
    assert len(safe) == 7


def test_empty_board_proves_nothing():
    safe, certain = analyse_board(empty_board())
    assert safe == set()
    assert certain == set()


def test_ai_never_fires_at_the_same_square_twice():
    ai = ComputerAI(level=3)
    board = empty_board()
    board[5][5] = 0                      # eight squares marked safe

    for _ in range(50):
        row, col = ai.generate_computer_attack(board)
        assert not ai.shot[row][col]
        ai.shot[row][col] = True


def test_ai_takes_a_proven_ship_immediately():
    ai = ComputerAI(level=3)
    board = empty_board()
    board[5][5] = 2
    for cell in [(4, 4), (4, 6), (5, 4), (5, 6), (6, 4), (6, 6)]:
        board[cell[0]][cell[1]] = "miss"

    for _ in range(20):
        assert ai.generate_computer_attack(board) in {(4, 5), (6, 5)}


def test_ai_avoids_squares_proven_to_be_water():
    ai = ComputerAI(level=3)
    board = empty_board()
    board[5][5] = 0
    safe = {(4, 4), (4, 5), (4, 6), (5, 4), (5, 6), (6, 4), (6, 5), (6, 6)}

    for _ in range(60):
        assert ai.generate_computer_attack(board) not in safe


def test_ai_still_works_without_a_board():
    ai = ComputerAI(level=3)
    row, col = ai.generate_computer_attack()
    assert 0 <= row < 10 and 0 <= col < 10


def test_level_one_ignores_the_numbers():
    """Level 1 must stay a random opponent, whatever the board shows."""
    ai = ComputerAI(level=1)
    board = empty_board()
    board[5][5] = 2
    for cell in [(4, 4), (4, 6), (5, 4), (5, 6), (6, 4), (6, 6)]:
        board[cell[0]][cell[1]] = "miss"

    picks = {ai.generate_computer_attack(board) for _ in range(200)}

    # A deduction AI would only ever pick the two proven squares
    assert picks != {(4, 5), (6, 5)}


def test_hunting_prefers_neighbours_of_an_unresolved_hit():
    ai = ComputerAI(level=2)
    ai.pending_hits = [(5, 5)]

    picks = {ai.generate_computer_attack(empty_board()) for _ in range(30)}

    assert picks <= set(neighbours(5, 5))


def test_sunk_ship_clears_pending_hits():
    ai = ComputerAI(level=3)
    ai.report_result(5, 5, "HIT")
    assert ai.pending_hits == [(5, 5)]

    ai.report_result(5, 5, "SUNK", sunk_ship_cells=[(5, 5), (5, 6)])
    assert ai.pending_hits == []
    assert ai.sunk_cells == {(5, 5), (5, 6)}
