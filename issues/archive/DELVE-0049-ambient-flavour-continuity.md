---
id: DELVE-0049
title: Ambient flavour PoC, take 2 - a continuous story with memory across the whole pack
status: implemented
area: [assess, content, session, docs]
type: story
effort: medium
milestone:
version: 1.18.0
version_span:
created: 2026-07-27
updated: 2026-07-27
accepted_by: George Moses
accepted_at: 2026-07-27
commits: [pre-reset]
related: [DELVE-0048]
supersedes: []
docs: []
changelog:
reason:
---

# Ambient flavour PoC, take 2 - a continuous story with memory across the whole pack

## Summary

[[DELVE-0048]] proved a local LLM can generate ambient one-liners per room, grounded in that
room's own prose plus a short window of recent gameplay events, and that the output visibly shifts
depending on what already happened. This story extends `poc/ambient-flavour/ambient.py` in four
ways requested after trying it against the full pilot pack:

1. **Ambient continuity, not just gameplay continuity.** DELVE-0048 fed each room's prompt the
   recent *gameplay* event log, but never fed back its own previously generated ambient lines. This
   story keeps a running `ambient_log` across the whole pack and includes it in every subsequent
   prompt, so a detail invented early (a phone ringing in a passage) can be picked back up later,
   the way a real environment would, instead of every room's flavour being generated in isolation.
2. **Richer simulated gameplay.** Beyond walking, talking, and passing, the simulated path now
   demonstrates a pet consult (`?`), a brush-off of an already-passed keeper (bumping into one you
   already cleared), and a rest (`s`), so the event log the model draws on has more of the texture
   a real playthrough has, not just "walk, read, answer, pass" on repeat.
3. **Explicit language control.** `--lang nl` was already accepted as a flag, but the engine
   strings weren't loaded for the chosen locale (always English), and the prompt never told the
   model which language to reply in. Both are fixed: `delve.strings.load(lang)` is passed into
   `new_game`, and the prompt explicitly instructs the model to reply in the chosen language.
4. **One continuous trail, not per-room debug blocks.** Output is restructured into a single
   chronological transcript for the whole pack, start to finish, gameplay messages and generated
   ambient lines interleaved in the order they actually occurred, so it reads as one built story
   rather than a series of independent per-room reports.

## Motivation / problem

Running DELVE-0048's script against the whole pilot pack showed each room's flavour was
self-contained: nothing tied a detail mentioned in the Sorting Office back to something in the
Vault two floors down. A real environment (and a real NetHack level) accretes detail; the point of
this take is to test whether feeding the model its own prior output produces that same sense of
one built place rather than twelve disconnected vignettes.

## Proposed approach

- A separate script (`poc/ambient-flavour/story.py`), not an edit to `ambient.py`, so the two can
  be compared side by side; reuse `ambient.py`'s shape (headless `RunState` walk, BFS helpers,
  per-room event folding) rather than importing it, matching how `ambient.py` itself relates to
  `tests/test_dungeon.py`.
- Add an `ambient_log: list[str]` alongside the existing gameplay `events` log. After each room's
  batch is generated, append its lines to `ambient_log`. Every prompt includes both: a window of
  recent gameplay events (as before) and the *ambient lines generated so far this run* (a
  continuity block), with a light instruction that the model may, but need not, bring an earlier
  detail back.
- Add three small, optional simulated interactions, each a real `Command` already in the engine,
  not invented behaviour: one pet `Consult()` on the first eligible (non-freetext) question of the
  run, one brush-off bump on the first room's keeper right after passing it, one `Rest()` per
  chapter. Each produces a real message through the existing strings catalogue.
- Load `delve.strings.load(args.lang)` and pass it into `new_game(..., strings=engine_strings)`,
  so `nl` actually renders Dutch engine messages (rest, consult, brush-off, pickup) rather than
  silently falling back to English.
- Add an explicit locale instruction to the generation prompt (reply in English/Dutch,
  matching STYLE.md's Dutch voice: informal *je*, sentence case in headings, if practical for a
  one-line prompt hint).
- Restructure output into a single ordered trail (a list of `(kind, text)` pairs, `kind` one of
  `game`/`ambient`) printed start to finish for the whole pack, plus an optional `--out <file>` to
  save the transcript.

## Findings

Built as a separate script, `poc/ambient-flavour/story.py`, rather than an edit to `ambient.py`
(DELVE-0048), so the two remain runnable side by side; `ambient.py` is unchanged. All four planned
extensions landed: an `ambient_log` fed back into every prompt, the three demo interactions
(`Consult`, a brush-off bump, `Rest`), correct locale loading (`delve.strings.load(lang)` now
actually passed into `new_game`), and a single tagged, chronological trail.

Continuity itself works over a short run: the `phishing`-room dog/no-pet comparison from
DELVE-0048 still holds under `story.py`. Over a **full 12-room pack walk**, though, it degrades,
and the failure is independent of the `--ambient-window` size. Five values were tried (`0`
unbounded, `100`, `20`, `12`, `6`) against `packs/security-onboarding/en` with `qwen2.5:3b` at
temperature `0.9`:

- Unbounded (`0`, growing to ~150-180 lines by the last chapter) caused near-identical batches by
  the third chapter and full language drift into Chinese by the fourth, despite an explicit
  "reply in English" instruction.
- Every bounded value (`100` down to `6`) avoided the language drift, but all converged onto the
  same underlying problem: a small set of recurring images repeated with only light rewording, and
  **keepers/objects from early chapters bleeding into ambient lines for much later, unrelated
  rooms** (Ada and Grigor, from the first chapter's Sorting Office, recurring in Watchpost-chapter
  batches two chapters later). This happened at every window size tested, including `6`.

Conclusion: capping the fed-back ambient history bounds prompt growth and avoids the
language-drift failure mode, but does not by itself produce coherent, spatially-scoped continuity.
The mechanism as built has no notion of *where* an ambient line happened, so the model has no
signal that a Sorting-Office detail shouldn't recur in the Watchpost. Full findings and the raw
per-window comparison are in `poc/ambient-flavour/README.md`'s "Early observations." The default
was set to `--ambient-window 24` as a reasonable bounded middle ground, explicitly documented as a
stopgap, not a fix for the bleed-through problem; fixing that properly would need scoping the
ambient log to a chapter (reset it at a chapter boundary, or tag each entry with its origin and
instruct the model accordingly), which is unbuilt follow-up work if this direction is pursued
further.

## Acceptance criteria

Given the whole pilot pack is walked with `--lang en` (default), when the transcript is produced,
then it reads as one ordered document, gameplay lines and generated ambient lines interleaved in
the order they occurred, from the first room to the last.

Given a detail invented in an early room's ambient batch, when a later room's prompt is built,
then that detail appears in the "ambient so far" block fed to the model, and this issue records
whether the model actually referenced it again (continuity working) or not (a real result worth
recording either way).

Given `--lang nl`, when the same pack is walked, then engine messages (rest, consult, brush-off,
pickup) render in Dutch, and the generated ambient one-liners are in Dutch too.

Given the three new simulated interactions (`Consult`, a brush-off bump, `Rest`), when the pack is
walked once, then each occurs at least once and its real engine message appears in the trail.

## Non-goals

- Not production code; same disposable-PoC standing as DELVE-0048 (five rules ignored on purpose).
- Not a general continuity *algorithm* (no theme extraction, no embedding search over prior lines);
  "include everything generated so far" is the whole continuity mechanism being tested here.
- Not a rewrite of the DELVE-0048 walk/BFS machinery; this only adds to it.
- Not a decision about shipping any of this in the real engine; still answering "is the idea good"
  before any "how would it ship" design work.
