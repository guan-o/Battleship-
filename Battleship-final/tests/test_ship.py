"""Tests for ship.py: coordinates, placement rules and damage."""

import pytest

from ship import (
    PlacementError,
    Ship,
    all_sunk,
    can_place_ship,
    format_coordinate,
    parse_coordinate,
    place_ship,
    ship_cells,
)


def test_parse_coordinate_is_one_based():
    assert parse_coordinate("C4") == (3, 2)
    assert parse_coordinate("a1") == (0, 0)
    assert parse_coordinate("J10") == (9, 9)


@pytest.mark.parametrize("bad", ["", "A", "K1", "A0", "A11", "1A", "A1 H"])
def test_parse_coordinate_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        parse_coordinate(bad)


def test_parse_and_format_round_trip():
    for row in range(10):
        for col in range(10):
            assert parse_coordinate(format_coordinate(row, col)) == (row, col)


def test_ship_cells_horizontal_and_vertical():
    assert ship_cells(0, 0, 3, "H") == [(0, 0), (0, 1), (0, 2)]
    assert ship_cells(0, 0, 3, "V") == [(0, 0), (1, 0), (2, 0)]


def test_ship_cells_off_board_raises():
    with pytest.raises(PlacementError):
        ship_cells(0, 8, 3, "H")          # runs past column J
    with pytest.raises(PlacementError):
        ship_cells(8, 0, 3, "V")          # runs past row 10


def test_place_ship_rejects_overlap():
    ships = []
    place_ship(ships, "Cruiser", 3, 0, 0, "H")
    with pytest.raises(PlacementError):
        place_ship(ships, "Destroyer", 2, 0, 2, "H")


def test_can_place_ship_never_raises():
    ships = []
    place_ship(ships, "Cruiser", 3, 0, 0, "H")
    assert can_place_ship(ships, 2, 0, 3, "H") is True     # free row
    assert can_place_ship(ships, 0, 1, 3, "H") is False    # overlaps
    assert can_place_ship(ships, 0, 9, 3, "H") is False    # off board


def test_hits_and_sinking():
    ship = Ship("Destroyer", 2, positions=[(0, 0), (0, 1)])
    assert ship.health == 2
    assert ship.take_hit(0, 0) is True          # first hit counts
    assert ship.take_hit(0, 0) is False         # same square twice is ignored
    assert ship.is_sunk() is False
    assert ship.take_hit(0, 1) is True
    assert ship.is_sunk() is True
    assert ship.health == 0


def test_take_hit_outside_ship_is_ignored():
    ship = Ship("Destroyer", 2, positions=[(0, 0), (0, 1)])
    assert ship.take_hit(5, 5) is False
    assert ship.health == 2


def test_all_sunk_is_true_for_an_empty_fleet():
    """Documents a gotcha: an empty fleet must never be used as a win check."""
    assert all_sunk([]) is True
