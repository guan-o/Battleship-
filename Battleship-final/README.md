# Battleship - Tactical Command Edition

A single-player, turn-based deduction game that runs in a terminal.
You hunt a hidden enemy fleet on a 10 x 10 grid; every miss hands you a number
clue, and the clues are what you actually play against.

## 1. What the game is

You and the computer each deploy five ships. On your turn you fire at one
square of the enemy grid. The computer fires back at yours. First fleet sunk
loses.

The twist is the **clue system**: when you miss, the square shows a number -
how many enemy ship parts touch that square (sideways *or* diagonally). Sunk
ships stop counting, so the numbers stay consistent as the game goes on. It is
minesweeper logic applied to battleship: you are not guessing, you are
deducing. Hits and sinkings pay cash, which buys power-ups.

### Rules in one screen

- Grid is `A-J` (columns) x `1-10` (rows). Type a square such as `B5`.
- One shot per turn; a hit does **not** give a free extra shot (that is what the
  shop item is for).
- A miss reveals number clues on the eight surrounding squares - for **both**
  sides. The computer's misses reveal the same numbers on your board, so both
  players work from identical information.
- `0-8` on a square = enemy ship parts touching it. `o` = miss, `X` = hit,
  `#` = part of a sunk ship, `S` = your own ship (only on your board).
- A number can sit on a square that holds a ship: the number belongs to the
  square, not to what is under it. On your own board your ships still show `S`.
- Cash: +$20 per hit, +$50 bonus when a ship sinks. Starting cash: $50.
- Shop: `radar` ($40) = scan a 3 x 3 area for numbers; `extra strike` ($50) =
  one extra shot on your next turn.
- Win by sinking all five enemy ships; lose if yours all sink. Quit any time
  with `Q`; start again by running the program again.

### Controls

At the attack prompt you may type:

| Input | Meaning |
|---|---|
| `B5` | fire at column B, row 5 |
| `SHOP` | open the shop (does not use your shot) |
| `RADAR` | spend one radar charge (does not use your shot) |
| `Q` | quit the game |
| `Ctrl-D` / `Ctrl-C` | close the input; the game ends without a traceback |

## 2. How to run it

The project runs inside the course container; no extra packages are needed.

```bash
# from the folder that contains compose.yaml
docker compose build
docker compose run --rm game bash
python main.py
```

Outside the container, from the folder that contains `main.py`:

```bash
python main.py
```

- **Container version:** `engg1330-project:2026-v03`
- Python 3.13 (the container image is `python:3.13-slim-bookworm`)
- Standard library only; no third-party imports in the game itself.

## 3. Project structure

| File | Responsibility |
|---|---|
| `main.py` | game loop, turn handling, shop and radar entry points |
| `board.py` | 10 x 10 grids, cell access, attack records |
| `ship.py` | fleet definition, coordinate parsing, placement rules, damage |
| `combat.py` | resolving a shot, clue counting, cash rewards, win check |
| `logic.py` | the eight-neighbour clue maths and the radar area |
| `computer.py` | enemy fleet placement and the targeting AI (levels 1-3) |
| `shop.py` | wallet, prices, purchases, power-up charges |
| `display.py` | everything that draws; keeps output inside 80 x 24 |
| `tests/` | `pytest` suite (see below) |
| `conftest.py` | lets the tests import the modules from the project root |

## 4. Tests

```bash
python -m pytest -q
```

81 checks covering:

- coordinate parsing, including invalid input (`A11`, `K1`, `1A`, empty);
- placement rules: overlap, off-board, touching is allowed;
- damage and sinking, including double hits on one square;
- shot outcomes: hit / sunk / miss / repeat / off-board, and which of them
  consume a turn;
- a hit message that never leaks the ship name or how many squares are left;
- clue maths, including that sunk ships stop counting and that the board edge
  does not crash;
- clue numbers landing on ship squares, and numbers being refreshed after a sink;
- wallet and shop: exact-cash boundary, refused purchase, charges spent once;
- the AI deduction: what a `0` proves, when a clue proves water, when a clue
  proves ships, and that the AI never fires twice at the same square;
- display limits: no line longer than 80 columns, board always 11 lines.

Manual checks done before submission: full playthrough, a wrong coordinate, a
repeated shot, both ends of the board (`A1`, `J10`), buying with too little
cash, quitting, and closing the input with `Ctrl-D`.

## 5. The computer opponent

Three levels, picked in `main.initialize_game()`; the game uses level 3:

| Level | How it plays |
|---|---|
| 1 | fires at random squares |
| 2 | after a hit, hunts the neighbours of hits that have not sunk anything |
| 3 | level 2 **plus** the same deduction the player does: reads the numbers on its own board, stops firing at squares the numbers prove are water, and fires immediately at squares that can only be ships |

Level 3 reads only the board it is shooting at - never the player's fleet - so it
plays with exactly the information the player has. The two rules it uses:

- if a clue equals the number of known hits around it, every remaining unknown
  neighbour is water;
- if the clue can only be reached by assuming every unknown neighbour is a ship,
  then all of them are ships.

Benchmarked over 120 games (computer fleet random, player fleet fixed), average
shots needed to sink all five ships:

| Level 1 | Level 2 | Level 3 |
|---|---|---|
| 94.8 | 66.0 | 50.4 |

## 6. Known limitations

- **Radar results are shown once.** The scan is printed but not written onto the
  board, so the player has to read it and remember it. A future version could
  keep the last scan on screen.
- **The computer does not plan ahead.** Level 3 deduces one square at a time; it
  does not weigh two clues against each other or choose the clue that would
  reveal the most.
- **The computer's fleet placement is random.** It never places ships touching
  each other on purpose (and never avoids it either).
- **No difficulty switch from the UI.** `ComputerAI(level=1)` and `level=2` are
  playable opponents; the level is fixed in `main.py`.
- **One save-free session.** There is no save/load; restarting means running the
  program again (allowed by the brief, but a game cannot be resumed).
- **Terminal smaller than 80 x 24 is not handled.** The two boards need about 60
  columns; below that the display will wrap.

## 7. Contributions

Fill in names and the actual work each member did. Keep it factual - non-coding
work counts.

| Member | Subclass | Contribution |
|---|---|---|
| TODO name | TODO T?A | e.g. `combat.py`, clue rules, balancing |
| TODO name | TODO T?A | e.g. `display.py`, 80 x 24 layout, trailer |
| TODO name | TODO T?A | e.g. `computer.py`, AI levels, demo video |
| TODO name | TODO T?A | e.g. `shop.py`, `tests/`, README, submission |

## 8. Sources and acknowledgements

- Grid, fleet sizes and the rules of battleship are common knowledge; the clue
  mechanic is adapted from minesweeper's neighbour-count rule.
- No third-party code was copied. Standard library only (`random`, `os`,
  `dataclasses`, `typing`).
- Course materials: ENGG1330 project brief (2026-27) and the T2 handout for the
  container setup.
- AI use is disclosed in `ai_use.md`.
