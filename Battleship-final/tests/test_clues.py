"""Tests for the clue bookkeeping in main.py.

Both players (human and computer) reveal the eight numbers around a miss, and
those numbers are refreshed as ships sink.  These tests pin that behaviour down
without starting the whole game loop.
"""

from board import create_board, update_cell
from main import refresh_clues, reveal_clues_around, sunk_cells
from ship import Ship, stamp_on_board


def make_boards():
    """A 10x10 board holding one two-square destroyer at (0,0)-(0,1)."""
    ship_board = create_board(10, 10)
    attack_board = create_board(10, 10)
    ship = Ship("Destroyer", 2, positions=[(0, 0), (0, 1)])
    stamp_on_board(ship_board, ship, marker="S")
    return ship_board, attack_board, ship


def test_clue_numbers_land_on_ship_squares_too():
    """A ship square must show its number, otherwise its silence gives it away."""
    ship_board, attack_board, ship = make_boards()
    cells = set()

    update_cell(attack_board, 1, 1, "miss")
    reveal_clues_around(ship_board, attack_board, [ship], 1, 1, cells)

    # (0,0) and (0,1) hold the ship and must still carry a number
    assert attack_board[0][0] == 1
    assert attack_board[0][1] == 1
    assert attack_board[0][2] == 1        # water square touching the ship
    assert attack_board[2][2] == 0        # nothing near this one
    assert len(cells) == 8


def test_reveal_never_overwrites_a_known_square():
    ship_board, attack_board, ship = make_boards()
    cells = set()

    update_cell(attack_board, 0, 0, "hit")      # already fired at
    reveal_clues_around(ship_board, attack_board, [ship], 1, 1, cells)

    assert attack_board[0][0] == "hit"
    assert (0, 0) not in cells


def test_reveal_skips_the_square_that_was_shot():
    ship_board, attack_board, ship = make_boards()
    cells = set()

    update_cell(attack_board, 1, 1, "miss")
    reveal_clues_around(ship_board, attack_board, [ship], 1, 1, cells)

    assert (1, 1) not in cells


def test_refresh_lowers_numbers_after_a_ship_sinks():
    ship_board, attack_board, ship = make_boards()
    cells = set()

    update_cell(attack_board, 1, 1, "miss")
    reveal_clues_around(ship_board, attack_board, [ship], 1, 1, cells)
    assert attack_board[0][2] == 1

    ship.take_hit(0, 0)
    ship.take_hit(0, 1)                         # the destroyer sinks
    refresh_clues(ship_board, attack_board, [ship], cells)

    assert attack_board[0][2] == 0               # sunk ships no longer count
    assert attack_board[2][2] == 0


def test_refresh_drops_squares_that_were_shot_later():
    ship_board, attack_board, ship = make_boards()
    cells = set()

    update_cell(attack_board, 1, 1, "miss")
    reveal_clues_around(ship_board, attack_board, [ship], 1, 1, cells)

    update_cell(attack_board, 2, 2, "miss")      # fired at afterwards
    refresh_clues(ship_board, attack_board, [ship], cells)

    assert attack_board[2][2] == "miss"
    assert (2, 2) not in cells


def test_sunk_cells_collects_only_sunken_ships():
    afloat = Ship("Cruiser", 2, positions=[(5, 5), (5, 6)])
    sunk = Ship("Destroyer", 2, positions=[(0, 0), (0, 1)])
    sunk.take_hit(0, 0)
    sunk.take_hit(0, 1)

    assert sunk_cells([afloat, sunk]) == {(0, 0), (0, 1)}
    assert sunk_cells([afloat]) == set()
