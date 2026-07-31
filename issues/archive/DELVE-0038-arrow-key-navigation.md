---
id: DELVE-0038
title: Move to arrow-key-only navigation
status: implemented
area: [ui, delve, docs]
type: feature
epic:
milestone:
version: 1.12.0
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [1caffae, 119927e]
related: []
supersedes: []
docs: []
changelog: "1.12.0"
reason:
---

# Move to arrow-key-only navigation

## Summary

Delve currently walks the player on either the classic NetHack letter keys (`hjkl` cardinal,
`yubn` diagonal) or the arrow keys, with both bound side by side. This drops the letter keys
entirely and keeps only the four arrow keys for movement, since the audience is not NetHack
veterans (the hint line design already says as much: "Un-NetHack on purpose"). Diagonal movement
goes with it, since arrow keys have no diagonal of their own and no generated dungeon needs one to
be fully reachable.

## Motivation / problem

`hjkl`/`yubn` is muscle memory for NetHack players, not for Delve's actual audience, who the hint
line design already assumes "most run this once" (CLAUDE.md, "The hint line is not decoration").
Keeping two parallel input schemes for the same eight directions is one more thing a first-time
player has to parse off the hint line for no benefit to anyone who wasn't already a NetHack
player. Cutting it to arrows-only is simpler to teach, matches the project's stated audience, and
removes a whole rank of keys (letters that could collide with an assertion's own first-letter
shortcut, noted as a deliberate carve-out in `keys.py` today).

## Stories

### As a learner, I want to move with the arrow keys only, so that I don't have to learn a second, NetHack-specific set of movement keys I'll never reuse elsewhere.

- Given the player is standing on an open floor tile, when they press an arrow key toward a walkable
  neighbour, then they move there, exactly as today.
- Given the player is standing anywhere, when they press `h`, `j`, `k`, `l`, `y`, `u`, `b`, or `n`,
  then nothing happens (no `Move` command is produced; the key is simply unbound during walking).
- Given the player is reading the hint line on any walking screen, when they look at it, then it
  says `Move: arrows` (English) or `Beweeg: pijltjes` (Dutch), never `hjkl`.

### As a pack author, I want the tutorial's movement lesson to describe the real controls, so that a new learner isn't taught a key that no longer does anything.

- Given a learner reaches the Porter's first lesson (`tutorial-screen`), when they read "That's
  movement", then the prose describes only the arrow keys, in both English and Dutch.

### As a maintainer, I want the mock-ups and design docs to match the shipped keymap, so that they stay evidence rather than drifting into a stale description of the game.

- Given `python tools/screens.py --check` is run, then the regenerated mock-ups reflect arrow-only
  hint text and pass their assertions.
- Given a maintainer greps `docs/` for `hjkl`, when the issue is archived, then no remaining hit
  describes current player-facing behaviour (historical/design-rationale mentions may remain where
  they explain *why* the change was made, not what the keys do today).

## Non-goals

- No change to the `Direction` enum in `engine/world.py`; `NE`/`NW`/`SE`/`SW` stay defined (other
  code, e.g. pathing helpers, may still reason about eight directions). Only the UI keymap stops
  producing them from a keypress.
- No mouse or pointer-driven movement; "cursor" here means the arrow keys, not a literal pointing
  device.
- No change to non-movement keys (`t`, `s`, `>`, `<`, `,`, `d`, `i`, `p`, space, `q`/`Q`) or to
  panel/menu navigation in `panel_command`, which already uses arrows (not `hjkl`) for focus and is
  unaffected.
- No new diagonal-movement affordance (e.g. shift+arrow); dropping `yubn` means the game is
  4-directional only, confirmed safe since every generated dungeon's corridors are strictly
  L-shaped (cardinal-only BFS already proves full reachability in `tests/test_dungeon.py`).

## Design notes / links

`delve/ui/keys.py`'s `_WALK` dict is the single source of truth for the walking keymap (rule 2:
`ui` only maps a keypress to a `Command`). Removing the `ord("h"/"j"/"k"/"l"/"y"/"u"/"b"/"n")`
entries and leaving the four `curses.KEY_*` entries is the entire behavioural change; everything
else in this issue is documentation and hint-string fallout from that one edit
(`delve/strings/en.toml`, `delve/strings/nl.toml`, `delve/tutorial/{en,nl}/00-the-threshold/01-the-screen.md`,
`tools/screens.py`'s mock-up hint text, and the `docs/` prose that quotes the hint line).

## Acceptance / verification

- A new `tests/test_keys.py` asserts `walk_command` maps each arrow key to its `Move(Direction.*)`
  and returns `None` for every one of `h`, `j`, `k`, `l`, `y`, `u`, `b`, `n` (this mapping had no
  direct test before; the gap is closed here, not just the behaviour changed).
- `python tools/screens.py --check` passes after `docs/SCREENS.md` is regenerated.
- `python tools/issues.py --check` passes.
- `./run-tests.sh` is green (pytest, ruff, pip-audit, screens check, issues check, `validate` on
  shipped packs).
