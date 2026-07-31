---
id: DELVE-0046
title: Windows verification - install, curses rendering, and LLM grader latency
status: implemented
area: [ui, assess, docs]
type: bug
effort: low
milestone:
version: 1.18.0
version_span:
created: 2026-07-27
updated: 2026-07-27
accepted_by: George Moses
accepted_at: 2026-07-27
commits: [pre-reset]
related: []
supersedes: []
docs: []
changelog:
reason:
---

# Windows verification - install, curses rendering, and LLM grader latency

## Summary

CLAUDE.md has long listed Windows verification as outstanding: the `windows-curses` render path,
é/€ text, and the double-line frame fallback all needed a real Windows host to confirm, not just
the cp314 wheel check already done. A bare distribution zip (`./dist.sh`) was built and sent to a
Windows test machine; install and play were exercised there. This issue records what happened,
including two rough edges the test surfaced in the distribution/install path, and the one
still-open question (LLM grader latency) pending numbers from the test machine.

## What was tested

- `./dist.sh` output (`delve` package, `packs/`, `pyproject.toml`, a generated stand-in
  `README.md`, and `WINDOWS-TEST-README.txt`) installed via `py -3.14 -m venv .venv` +
  `pip install .` on a Windows machine.
- `python -m delve` launched and played, including a room requiring the LLM grader (Ollama +
  `qwen2.5:3b`).

## Findings

1. **`pip install .` failed on the bare distribution**: `pyproject.toml`'s `readme = "README.md"`
   requires the file to exist for the build backend, but the original `dist.sh` didn't package
   one. Fixed: `dist.sh` now generates a short stand-in `README.md` in the distribution (the full
   dev README links `docs/` that isn't part of a bare install).
2. **A PowerShell `>` redirection footgun surfaced while hand-editing that stand-in file on the
   test machine**: `date > README.md` writes UTF-16LE with a BOM by default, which
   `pip install .` then failed to decode as UTF-8. Not a Delve bug, but worth the
   `WINDOWS-TEST-README.txt` calling out `Out-File -Encoding utf8` (or `utf8NoBOM` on PowerShell
   6+) instead of bare `>` for anyone editing text files by hand on Windows.
3. **`ModuleNotFoundError: No module named '_curses'`** on first run, despite `windows-curses`
   2.4.2 showing installed in `pip list`. Root cause: PowerShell's script-signing policy silently
   blocked `.venv\Scripts\activate`, so a bare `python -m delve` ran a different, non-venv
   interpreter that had no `windows-curses`. Not a Delve bug; `WINDOWS-TEST-README.txt` was updated
   to call `.venv\Scripts\python.exe`/`pip.exe` directly rather than relying on activation, and to
   name this exact symptom so a future tester recognises it immediately.
4. **Curses rendering, box walls, and the double-line panel frame all worked** once the correct
   interpreter was used; the game ran end to end including a tutorial floor and an LLM-graded
   room. No visual defects reported.
5. **The LLM grader is noticeably slower on the test machine than on the macOS dev machine**, but
   still workable (games remained playable; no timeouts hit). `Measure-Command { ollama run
   qwen2.5:3b "Say OK" }` gave 705ms cold (first run, model load included), then 393ms and 385ms on
   warm subsequent runs. In-game, the free-text questions in the tutorial floor's fourth room
   (Merryn's, the three-question free-text sitting) graded in around 2-3 seconds per answer, judged
   acceptable.

   Test machine: AMD Ryzen 5 7535U with Radeon Graphics (2.90 GHz), 16.0 GB RAM (13.7 GB
   available), AMD Radeon(TM) Graphics (2 GB, integrated), 64-bit Windows, x64 processor. No
   discrete GPU; inference ran on CPU/integrated graphics only, consistent with the sub-second
   warm latency and 2-3s in-game grading being CPU-bound rather than GPU-accelerated.

   For comparison, the same `ollama run qwen2.5:3b "Say OK"` timing on the macOS dev machine
   (Apple M5, 16 GB RAM) via bash `time`, run twice on separate occasions:

   | Run | Cold | Warm 1 | Warm 2 |
   |---|---|---|---|
   | First | 1.651s | 0.153s | 0.347s |
   | Second | 1.187s | 0.380s | 0.414s |

   The cold run is consistently slower in wall time than Windows' single cold run (705ms) but
   that's mostly process/model-load variance, not a like-for-like comparison (`ollama run` here
   also prints a full conversational reply rather than a terse "Ok", so tokens generated differ
   between runs, and cold-start variance alone spans 1.187-1.651s across the two M5 samples).
   The warm runs are the more telling number and now show some run-to-run spread themselves
   (153-414ms across both M5 samples) that overlaps the Ryzen 5 7535U's single warm sample
   (385-393ms) rather than clearly beating it; both remain well within the 2-3s in-game grading
   budget observed on Windows, and neither machine is a graded-latency bottleneck for play.

## Acceptance criteria

Given the Windows test machine's specs are supplied, when this issue is updated with them
alongside a rough LLM grader latency figure (e.g. seconds per grade, from `Measure-Command`
around `ollama run`/`/api/chat` or in-game observation), then this issue records a complete
Windows verification pass and can be archived. **Met**: see Findings item 5.

Given a future tester runs `./dist.sh`'s output on a fresh Windows machine, when they follow
`WINDOWS-TEST-README.txt`, then they should not hit either the missing-`README.md` install failure
or the silent-wrong-interpreter `_curses` failure, since both are now called out or avoided in the
instructions.

## Non-goals

- Not a fix for LLM grader performance; if latency turns out to be a real problem on
  lower-end hardware, that is a separate, future issue.
- Not the é/€ character check across every screen; this pass exercised normal English play only.
  A dedicated Dutch-locale Windows pass is still separately worth doing.
- Does not touch `Grader > Live` latency reporting (DELVE-0035's unfiled future child story); this
  issue's latency numbers are gathered manually, outside the app.
