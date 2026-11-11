"""Turn-level tests: every shot that is recorded must also be drawn.

The bug these tests guard against: a square was accepted as a shot (so firing at
it again said "already fired at") but the board was only redrawn at the start of
the next turn, so the mark never appeared where the player was looking.
"""

import main
from board import create_board
from computer import ComputerAI
from ship import FLEET, Ship, stamp_on_board


def make_state():
    """A ready-to-play state with both fleets already placed."""
    state = {
        "player_board": create_board(10, 10),
        "computer_board": create_board(10, 10),
        "player_attack_board": create_board(10, 10),
        "computer_attack_board": create_board(10, 10),
        "player": {"cash": 0, "ships_remaining": 5},
        "computer": {"ships_remaining": 5},
        "player_ships": [],
        "computer_ships": [],
        "player_shots": set(),
        "computer_shots": set(),
        "computer_ai": ComputerAI(level=3),
        "extra_shots": 0,
        "radar_charges": 0,
        "clue_cells": set(),
        "computer_clue_cells": set(),
        "turn": 1,
        "game_over": False,
        "winner": None,
        "quit": False,
    }

    for index, (name, length) in enumerate(FLEET):
        # Player ships on even rows, computer ships on odd rows: no overlap
        player_ship = Ship(name, length, ship_id=index + 1,
                           positions=[(index * 2, c) for c in range(length)])
        computer_ship = Ship(name, length, ship_id=index + 1,
                             positions=[(index * 2 + 1, c) for c in range(length)])
        state["player_ships"].append(player_ship)
        state["computer_ships"].append(computer_ship)
        stamp_on_board(state["player_board"], player_ship, marker="S")
        stamp_on_board(state["computer_board"], computer_ship, marker="S")

    return state


def run_turn(moves):
    """Play one player turn with scripted input; return the state afterwards."""
    state = make_state()
    queue = list(moves)

    main.clear_screen = lambda: None          # do not shell out to cls/clear
    main.get_player_input = lambda prompt="": queue.pop(0)

    main.player_turn(state)
    return state


def board_is_marked(state):
    """Every square recorded as a shot must show something on the board."""
    board = state["player_attack_board"]
    missing = [
        cell for cell in state["player_shots"]
        if board[cell[0]][cell[1]] is None
    ]
    return missing


def test_every_recorded_shot_is_also_drawn():
    state = run_turn(["B5"])
    assert state["player_shots"] == {(4, 1)}
    assert board_is_marked(state) == []


def test_a_repeat_is_not_recorded_again_and_stays_visible():
    state = make_state()
    state["extra_shots"] = 1
    queue = ["B5", "B5", "C5"]

    main.clear_screen = lambda: None
    main.get_player_input = lambda prompt="": queue.pop(0)
    main.player_turn(state)

    # B5 fired once, C5 fired once; the repeated B5 changed nothing
    assert state["player_shots"] == {(4, 1), (4, 2)}
    assert board_is_marked(state) == []


def test_invalid_input_does_not_record_anything():
    state = run_turn(["ZZ", "A11", "B5"])
    assert state["player_shots"] == {(4, 1)}
    assert board_is_marked(state) == []


def test_two_shots_in_one_turn_are_both_marked():
    """With an extra strike the same turn fires twice; both must show up."""
    state = make_state()
    state["extra_shots"] = 1
    queue = ["B5", "C5"]

    main.clear_screen = lambda: None
    main.get_player_input = lambda prompt="": queue.pop(0)

    main.player_turn(state)

    assert state["player_shots"] == {(4, 1), (4, 2)}
    assert board_is_marked(state) == []


def test_the_frame_is_redrawn_between_the_two_shots():
    """The board must be drawn again before the second prompt of a turn."""
    state = make_state()
    state["extra_shots"] = 1
    queue = ["B5", "C5"]
    frames = []

    main.clear_screen = lambda: None
    main.get_player_input = lambda prompt="": queue.pop(0)
    original = main.display_both_boards
    main.display_both_boards = lambda *args, **kwargs: frames.append(
        [row[:] for row in args[3]]
    )

    try:
        main.player_turn(state)
    finally:
        main.display_both_boards = original

    # At least three frames: one before each prompt, one after the last shot
    assert len(frames) >= 3
    # The second frame must already show the first shot at B5 (row 4, col 1)
    assert frames[1][4][1] is not None
