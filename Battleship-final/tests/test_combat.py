"""Tests for combat.py: shot outcomes, cash rewards and the win condition."""

from combat import (
    HIT,
    HIT_REWARD,
    INVALID,
    MISS,
    REPEAT,
    SINK_BONUS,
    SUNK,
    attack,
    check_victory,
    is_game_over,
    process_computer_attack,
    process_player_attack,
)
from ship import Ship


def fleet():
    """A two-ship fleet used by most tests."""
    return [
        Ship("Battleship", 4, positions=[(0, 0), (0, 1), (0, 2), (0, 3)]),
        Ship("Destroyer", 2, positions=[(5, 5), (5, 6)]),
    ]


def test_miss_returns_a_clue_and_costs_a_turn():
    ships = fleet()
    shots = set()
    result = attack(ships, 4, 1, shots)      # empty water next to nothing
    assert result.outcome == MISS
    assert result.clue == 0
    assert result.consumes_turn is True
    assert (4, 1) in shots


def test_clue_counts_neighbouring_ship_parts():
    ships = fleet()
    result = attack(ships, 1, 2, set())      # below the battleship
    # (0,1), (0,2), (0,3) touch the square; (0,0) is two columns away
    assert result.clue == 3


def test_hit_awards_cash_and_damages_the_ship():
    ships = fleet()
    result = attack(ships, 0, 0, set())
    assert result.outcome == HIT
    assert result.reward == HIT_REWARD
    assert ships[0].health == 3


def test_hit_message_does_not_leak_the_ship_or_its_health():
    """A partial hit must not tell the player what ship it is or how big."""
    ships = fleet()
    result = attack(ships, 0, 0, set())

    assert "Battleship" not in result.message
    assert "squares left" not in result.message
    assert "3" not in result.message
    assert result.message == "Hit at A1!"


def test_sinking_awards_the_bonus():
    ships = [Ship("Destroyer", 2, positions=[(0, 0), (0, 1)])]
    shots = set()
    attack(ships, 0, 0, shots)
    result = attack(ships, 0, 1, shots)
    assert result.outcome == SUNK
    assert result.reward == HIT_REWARD + SINK_BONUS
    assert result.ship_name == "Destroyer"


def test_second_shot_on_the_same_square_does_not_consume_a_turn():
    ships = fleet()
    shots = set()
    attack(ships, 4, 4, shots)
    result = attack(ships, 4, 4, shots)
    assert result.outcome == REPEAT
    assert result.consumes_turn is False


def test_off_board_shot_does_not_consume_a_turn():
    result = attack(fleet(), 10, 0, set())
    assert result.outcome == INVALID
    assert result.consumes_turn is False


def test_computer_shots_earn_no_cash():
    ships = fleet()
    result = process_computer_attack(ships, 0, 1, set())
    assert result.outcome == HIT
    assert result.reward == 0


def test_player_attack_matches_the_wrapper():
    ships = fleet()
    result = process_player_attack(ships, 0, 2, set())
    assert result.outcome == HIT
    assert result.reward == HIT_REWARD


def test_victory_needs_the_whole_fleet_sunk():
    player = fleet()
    computer = fleet()
    assert check_victory(player, computer) is None
    assert is_game_over(player, computer) is False

    for col in range(4):
        computer[0].take_hit(0, col)
    computer[1].take_hit(5, 5)

    assert check_victory(player, computer) is None      # one square left
    computer[1].take_hit(5, 6)
    assert check_victory(player, computer) == "player"
    assert is_game_over(player, computer) is True


def test_defeat_when_the_player_fleet_is_gone():
    player = [Ship("Destroyer", 1, positions=[(9, 9)])]
    computer = fleet()
    player[0].take_hit(9, 9)
    assert check_victory(player, computer) == "computer"


def test_clue_ignores_ships_that_already_sank():
    ships = [
        Ship("Destroyer", 2, positions=[(0, 0), (0, 1)]),
        Ship("Cruiser", 3, positions=[(0, 4), (0, 5), (0, 6)]),
    ]
    ships[0].take_hit(0, 0)
    ships[0].take_hit(0, 1)                          # destroyer is now sunk

    # (1, 1) touches the two sunk destroyer squares and nothing else, so the
    # clue must be 0: sunk ships are no longer counted.
    assert attack(ships, 1, 1, set()).clue == 0

    # The cruiser is untouched, so it is still counted from (1, 5).
    assert attack(ships, 1, 5, set()).clue == 3
