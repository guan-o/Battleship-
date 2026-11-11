"""Tests for display.py: the 80x24 limits and the board symbols."""

from display import (
    SCREEN_WIDTH,
    attack_symbol,
    board_lines,
    cell_symbol,
    center,
    coord_to_text,
    display_board,
    display_both_boards,
    display_game_status,
    display_message,
    fit,
    pause,
)


def test_fit_never_exceeds_80_columns():
    assert len(fit("x" * 200)) == SCREEN_WIDTH


def test_center_keeps_the_width_limit():
    assert len(center("x" * 200)) <= SCREEN_WIDTH


def test_coordinate_text_is_one_based():
    assert coord_to_text(0, 0) == "A1"
    assert coord_to_text(9, 9) == "J10"


def test_board_is_eleven_lines_and_narrow_enough():
    board = [[None] * 10 for _ in range(10)]
    attacks = [[None] * 10 for _ in range(10)]
    lines = board_lines(board, attacks)
    assert len(lines) == 11                      # header + 10 rows
    assert all(len(line) <= 23 for line in lines)


def test_hidden_ships_are_not_drawn():
    board = [[None] * 10 for _ in range(10)]
    board[3][3] = "S"
    attacks = [[None] * 10 for _ in range(10)]

    visible = board_lines(board, attacks, hide_ships=False)[4]
    hidden = board_lines(board, attacks, hide_ships=True)[4]

    assert "S" in visible
    assert "S" not in hidden


def test_attack_symbols_map_to_one_character():
    assert attack_symbol("hit") == "X"
    assert attack_symbol("sunk") == "#"
    assert attack_symbol("miss") == "o"
    assert attack_symbol(3) == "3"
    assert attack_symbol(0) == "0"
    assert attack_symbol(None) is None


def test_shot_hides_the_ship_under_it():
    assert cell_symbol("S", "hit") == "X"
    assert cell_symbol("S", None) == "S"
    assert cell_symbol(None, None) == "."


def test_own_ship_wins_over_a_clue_number():
    # On your own board the fleet stays readable even if a number was written
    assert cell_symbol("S", 3, hide_ships=False) == "S"
    # On the enemy board the number is the only thing that may be shown
    assert cell_symbol("S", 3, hide_ships=True) == "3"
    # A clue number must never un-hide an enemy ship by accident
    assert cell_symbol("S", None, hide_ships=True) == "."


def test_display_board_stays_within_80_columns(capsys):
    board = [[None] * 10 for _ in range(10)]
    attacks = [[None] * 10 for _ in range(10)]
    display_board(board, attacks)
    out = capsys.readouterr().out
    assert all(len(line) <= SCREEN_WIDTH for line in out.splitlines())


def test_status_bar_fits_one_line_per_item(capsys):
    player = {"cash": 70}
    state = {"turn": 12, "player_ships_left": 5, "computer_ships_left": 4,
             "extra_shots": 1, "radar_charges": 2}
    display_game_status(player, state)
    out = capsys.readouterr().out.splitlines()
    assert "Turn 12" in out[0]
    assert "Cash: $70" in out[0]
    assert all(len(line) <= SCREEN_WIDTH for line in out)


def test_display_message_accepts_a_list(capsys):
    display_message(["line one", "line two"])
    assert capsys.readouterr().out.count("\n") == 2


def test_pause_does_not_block_when_input_is_piped():
    """A piped stdin is not a terminal, so pause() must return at once."""
    pause()          # would block forever if the isatty guard were missing


def test_both_boards_show_your_fleet_and_hide_the_enemy(capsys):
    player_board = [[None] * 10 for _ in range(10)]
    player_board[0][0] = "S"                    # your carrier, visible
    player_attacks = [[None] * 10 for _ in range(10)]
    computer_board = [[None] * 10 for _ in range(10)]
    computer_board[9][9] = "S"                  # enemy ship, must stay hidden
    computer_attacks = [[None] * 10 for _ in range(10)]

    display_both_boards(player_board, player_attacks,
                        computer_board, computer_attacks)

    out = capsys.readouterr().out
    assert "YOUR FLEET" in out
    assert "ENEMY WATERS" in out
    assert all(len(line) <= SCREEN_WIDTH for line in out.splitlines())

    # Lines 1..11 are the board rows; each is "    " + left board (31 wide)
    # + right board, so the enemy board starts at column 35.  (The last line is
    # the legend, which mentions the letter S itself.)
    lines = out.splitlines()
    board_rows = lines[1:12]
    assert len(board_rows) == 11
    assert not any("S" in row[35:] for row in board_rows)
    assert any("S" in row[:35] for row in board_rows)
