# AI Use

Generative AI used: Yes

We used a generative AI assistant for code review, bug fixing, tests and
documentation. Every suggestion was read, run and checked by a group member
before it stayed in the project; the game logic and the design decisions are
ours. Entries below are ordered oldest first.

## Entry

- Member and date: TODO (member name), 2026-11-11
- Tool and model/version: TODO (e.g. Claude / DeepSeek, version shown in the app)
- Purpose: code review of the finished prototype against the project brief;
  find bugs; suggest tests.
- Substantial parts affected (files/materials): `display.py`, `main.py`,
  `shop.py`, `combat.py`, `tests/`, `README.md`, `conftest.py`.
- What was kept, changed, or rejected, and how results were checked (tests or
  corrections):
  - **Kept (bug fixes).** A duplicated `display_game_status` definition in
    `display.py` silently replaced the real status bar with `pass`; we deleted
    the stub and the status bar is now drawn every turn. Verified by playing a
    turn and seeing `Turn / Cash / ships` appear.
  - **Kept (crash fix).** Closing the input (`Ctrl-D`) used to end the program
    with a `PlacementError` traceback. We added `display.EndOfInput`, caught it
    at every prompt, and now the game prints a message and exits with code 0.
    Verified by piping a truncated list of moves into `main.py`.
  - **Kept (consistency).** Revealed clue numbers used to keep counting ships
    that sank later, so the board contradicted itself. We added
    `refresh_clues()` and recompute the revealed numbers after every shot.
    Verified by sinking a ship and watching the neighbouring numbers drop.
  - **Changed (economy).** `shop.py` carried its own `HIT_REWARD` / `SINK_REWARD`
    that disagreed with `combat.py`. We removed the duplicate table so the
    rewards have one owner, and `shop.reward_for_attack` now reuses
    `combat.HIT_REWARD` / `combat.SINK_BONUS`.
  - **Kept (tests).** An AI-drafted `pytest` suite was kept only after we ran it:
    two of the first assertions were wrong (they expected 2 where the board
    really has 3 touching segments) and we corrected the tests, not the code.
  - **Kept (new opponent).** A suggestion to give the computer the same deduction
    the player uses (read the numbers on its own board; a clue saturated by known
    hits proves the rest is water; a clue that only fits if every unknown
    neighbour is a ship proves those ships) was adopted as `computer.analyse_board`
    plus level 3 in `computer.py`. We checked it by benchmark: over 120 simulated
    games the average number of shots to sink a fleet fell from 66.0 (level 2) to
    50.4 (level 3), and 15 unit tests pin down what a `0` proves and when a clue
    proves water or ships. The AI reads only its own attack board, never the
    player's fleet.
  - **Rejected.** A suggestion to add a second puzzle layer (a decoded
    transmission) was held back: it changes the win condition and we want the
    team to agree on the design before it lands.
  - **Rejected.** A suggestion to store radar results in a save file was
    rejected as out of scope; the limitation is documented in `README.md`.

## Entry

- Member and date: TODO (second member, if anyone else used AI), TODO date
- Tool and model/version: TODO
- Purpose: TODO
- Substantial parts affected (files/materials): TODO
- What was kept, changed, or rejected, and how results were checked (tests or
  corrections): TODO
