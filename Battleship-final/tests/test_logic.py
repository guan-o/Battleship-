"""Tests for logic.py: the eight-neighbour clue counter."""

from logic import calculate_clue, calculate_radar, get_surrounding_clues

# A tiny 10x10 board of booleans: True = a ship segment sits there.
BOARD = [[False] * 10 for _ in range(10)]
BOARD[0][0] = True
BOARD[0][1] = True
BOARD[0][2] = True


def test_clue_counts_all_eight_directions():
    # (1, 1) touches all three ship segments: (0,0), (0,1) and (0,2)
    assert calculate_clue(BOARD, 1, 1) == 3
    # (1, 0) touches (0,0) and (0,1) only
    assert calculate_clue(BOARD, 1, 0) == 2
    # (1, 2) touches (0,1) and (0,2) only
    assert calculate_clue(BOARD, 1, 2) == 2


def test_clue_ignores_the_cell_itself():
    assert calculate_clue(BOARD, 0, 1) == 2      # neighbours only, not itself


def test_clue_on_an_empty_area_is_zero():
    assert calculate_clue(BOARD, 9, 9) == 0


def test_clue_at_the_board_edge_does_not_crash():
    assert calculate_clue(BOARD, 0, 0) == 1      # (0,1) only; no negative index


def test_clue_can_exclude_sunk_ships():
    excluded = {(0, 0), (0, 1), (0, 2)}
    assert calculate_clue(BOARD, 1, 1, excluded) == 0


def test_surrounding_clues_returns_eight_squares():
    clues = get_surrounding_clues(BOARD, 5, 5)
    assert len(clues) == 8
    assert (5, 5) not in clues                  # the centre is skipped


def test_surrounding_clues_is_clipped_at_the_edge():
    clues = get_surrounding_clues(BOARD, 0, 0)
    assert len(clues) == 3                      # three in-bounds neighbours
    assert all(0 <= r < 10 and 0 <= c < 10 for r, c in clues)


def test_radar_counts_ship_parts_in_the_area():
    # Radius 1 around (1, 1) covers rows 0-2 and columns 0-2: three segments.
    assert calculate_radar(BOARD, 1, 1, 1) == 3
    assert calculate_radar(BOARD, 9, 9, 1) == 0
