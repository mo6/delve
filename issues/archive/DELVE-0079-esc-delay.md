---
id: DELVE-0079
title: Esc takes a full second to close a panel, because ncurses' default ESCDELAY is untouched
status: implemented
area: [ui]
type: bug
epic:
effort: low
milestone:
version: 1.29.1
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [6d0a194]
related: []
supersedes: []
docs: []
changelog: "1.29.1"
reason:
---

# Esc takes a full second to close a panel, because ncurses' default ESCDELAY is untouched

## Summary

Every panel (Info, Help, a lesson, a menu) closes on the literal `Esc` key
(`delve/ui/app.py`, `if key == "\x1b": return Dismiss()`, two call sites). Stock ncurses cannot
tell a lone `Esc` press apart from the first byte of an escape sequence (arrow keys, function
keys, etc. all start with `\x1b`), so after reading `\x1b` it waits `ESCDELAY` milliseconds to see
if more bytes follow before delivering it as a standalone key. `ESCDELAY` defaults to **1000ms**
and `delve/ui/app.py:_run` never sets it, so every Esc press takes a full second to register,
noticeably slower than every other key in the app. The fix is one line: `curses.set_escdelay`,
called once at startup, right after `stdscr.keypad(True)`.

## Motivation / problem

A learner closing Info/Help with Esc (the hint line's own documented key) waits a full second for
the panel to go away, which reads as the app hanging rather than as an intentional delay; every
other key (arrows, Tab, digits, Enter) responds instantly by comparison. This is a well-known
ncurses default, not a bug in Delve's own dispatch: `app.py`'s two `key == "\x1b"` checks are
correct and unconditional, they simply never fire until ncurses itself decides the escape sequence
is over.

## Stories

### As a learner pressing Esc to close a panel, I want it to close about as fast as any other key, so the app never feels like it is hanging.

- Given the app has just started (`_run`, right after `curses.curs_set(0)` and
  `stdscr.keypad(True)`), when curses is initialised, then `curses.set_escdelay` is called with a
  short delay (25ms), so a lone `Esc` press is delivered to `getch`/`get_wch` well under 100ms
  later instead of the ncurses default 1000ms.
- Given the changed delay, when an actual escape sequence arrives (an arrow key, a function key,
  anything else that begins with `\x1b` and is followed by more bytes within the shortened
  window), then it is still recognised correctly as that key, not split into a spurious lone Esc
  followed by garbage; 25ms is comfortably above the byte-arrival latency of a real terminal's own
  escape sequence, the same value commonly recommended for exactly this trade-off (e.g. Vim's own
  `ttimeoutlen` default guidance).
- Given a platform where `curses.set_escdelay` is unavailable (older ncurses without the
  `set_escdelay` extension), when `_run` starts, then the call is wrapped so its absence never
  crashes startup; the app simply falls back to the ncurses default delay on that platform, no
  worse than today.

## Non-goals

- No change to what key closes a panel, or to any other keybinding; `Esc` still maps to `Dismiss`
  exactly as it does today.
- No change to `_freetext_command`'s own Esc handling (already reads `\x1b` from `get_wch`, which
  is governed by the same `ESCDELAY`, so this one process-wide setting fixes it too, with no
  second code change needed there).
- No new configuration surface (no `--esc-delay` flag); the value is a fixed, tuned constant.

## Design notes / links

- `delve/ui/app.py:_run` is the one call site: `curses.set_escdelay(ESC_DELAY_MS)` belongs right
  after `stdscr.keypad(True)`, alongside `attrs.init()`'s own one-time startup setup.
- Python's `curses.set_escdelay` wraps ncurses' own `set_escdelay(3X)`, present since Python 3.9;
  the project targets 3.14, so availability is not actually a concern in practice, but the call is
  still guarded (`AttributeError`) for platform safety, matching the project's general defensive
  posture around curses/PDCurses drift (CLAUDE.md's cross-platform section).
- Windows/PDCurses (`windows-curses`) is the one platform CLAUDE.md flags as still needing
  verification generally; `set_escdelay` is part of the same wrapper package's API surface, so no
  extra risk beyond what is already documented as outstanding.

## Acceptance / verification

- A test in `tests/test_app.py` (or wherever `_run`'s startup sequence is already exercised against
  a fake curses module) asserts `set_escdelay` is called with the chosen value during startup.
- A test confirms startup does not raise when the fake curses module has no `set_escdelay`
  attribute at all (the guarded fallback path).
- `./run-tests.sh` is green.
