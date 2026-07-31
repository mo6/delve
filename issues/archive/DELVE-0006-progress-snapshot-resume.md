---
id: DELVE-0006
title: Progress store, snapshot, resume
status: implemented
area: [progress, session, ui]
milestone: M5
version: 0.5.0
created: 2026-07-18
updated: 2026-07-18
commits: [pre-reset]
related: [DELVE-0005]
supersedes: []
docs: [docs/PLAN.md]
changelog: "0.5.0"
---

# Progress store, snapshot, resume

## Summary

Persist who played, what they passed, and where they stood. A SQLite store holds users, runs,
write-once room results, and an append-only scrolls table. A run snapshot lets a learner resume
an unfinished run where they left it, and the trophy case shows every past completion.

## Motivation / problem

A learner's history is their collection. Progress must survive quitting, a run must be
resumable, and passing must be final so the trophy case means something.

## Requirements

1. Identity MUST be asked ("Who are you?") at start, NetHack-style, matching or creating a
   `users` row by name, case-insensitive; it MUST NOT read `$USER`.
2. `room_results.passed_at` MUST be write-once; a keeper MUST re-instruct forever but
   re-examine never.
3. A run MUST be regenerable tile-for-tile from its record (`seed`, `size`, `pack`, stored in
   `runs`); resume MUST re-open earned gates via `Gate.reopen`.
4. Snapshots MUST be written on persist-worthy transitions (gate pass, chapter change) plus a
   checkpoint on quit.
5. An unfinished run of the same pack MUST be offered on arrival via a `[yn]` prompt defaulting
   to yes; declining MUST start a fresh run.
6. Re-taking a pack MUST keep both: every completion writes its own `scrolls` row and none is
   ever updated; the trophy case lists all attempts, newest first.

## Non-goals

- Encrypted scroll export (Phase 2, not in the MVP).
- Authenticity of identity; it is trust-based by design (PLAN sections 10-11).

## Design notes / links

`session/snapshot.py` (RunState to/from a JSON mark) and the append-only schema are in
`CLAUDE.md`; write-once passing is rule 3. Trust-based identity and the "keep both" decision
are settled in PLAN section 10.

## Acceptance / verification

- A snapshot round-trips: rebuild from `seed+size+pack`, earned gates re-open.
- A write-once test confirms a passed room cannot be re-scored.
- Trophy-case test lists multiple completions of one pack, newest first.
