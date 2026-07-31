---
id: DELVE-0048
title: PoC - generate ambient one-liners along a simulated game path with the LLM
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
commits: [6f88950]
related: []
supersedes: []
docs: []
changelog:
reason:
---

# PoC - generate ambient one-liners along a simulated game path with the LLM

## Summary

A standalone, throwaway spike script, in the shape of `poc/llm-grader` (its own folder under
`poc/`, its own README, stdlib-only, ignoring the five rules on purpose since it is disposable
evaluation code and never wired into the shipping engine): drive a pack through a **realistic
simulated game path**, using the same headless `RunState.apply(Command) -> Frame` harness the
project's own M1 tests already play whole runs through (`session/run.py`), and at points along that
path ask the local LLM for **10-20 short ambient one-liners**, grounded not just in the room's
authored prose but in *what is actually happening in the simulated run*: which room the player is
in, what they just picked up, what their pet just did, what message just appeared. This replaces
the flat, room-only version of this idea (generate a static batch per room, once, from prose alone)
with one where the same room can produce different, situationally apt lines depending on what
already happened on the way there.

## Motivation / problem

Right now the only atmospheric text a room has is what its author wrote by hand in the lesson body
(e.g. `01-phishing.md`'s "Dust. The smell of old paper and toner..." at the chapter level, or Ada's
dialogue at the room level). There is no ambient flavour text distinct from the lesson itself, and
nothing that reacts to what the learner is actually doing: picking up an item, watching a dog trot
back with a fetched coin, walking past a keeper they've already passed. Before committing to any
engine plumbing (a new pack field, a place to render it, when it would show), this spike answers a
cheaper question first: **can a local model, given both a pack's descriptive prose and a slice of
real, simulated game state, produce short one-liners that read as reacting to the moment**, not
just describing the room in the abstract. Same evaluation shape as `poc/llm-grader` (measure speed
and quality before committing to product code), applied to context-aware generation instead of
grading.

## Inputs the script has available

Two layers, both already producible without new format or engine work:

**Static, per pack/chapter/room** (as before): `pack.md`'s title/description, the chapter's
`chapter.md` title/prose, and the room's own `id`/`name`/`keeper`/heading/body. All parseable today
via `content/`.

**Dynamic, from a simulated run**: the script drives `RunState` (`session/run.py`, built via
`new_game` from a real parsed pack) through a scripted `Command` sequence, `Move`, `Pickup`,
`Drop`, `Talk`, `Consult`, `Rest`, `Descend`, the same primitives the M1 headless harness already
asserts on. Each `apply(Command)` returns a `Frame`; the script collects, per step: the current
room/chapter, the visible message line, any item just picked up or dropped (`Stack`/`ItemDef` from
`engine/items.py`), and any pet event (`engine/pet.py`'s `PetEvent`: a fetch, a coin sweep, a
question consult). That rolling window of recent events is what turns "describe this room" into
"describe this room, given the dog just fetched a dropped pebble and set it beside you."

## Proposed approach

1. `poc/ambient-flavour/` (new folder, its own README, matching `poc/llm-grader`'s shape).
2. A **path builder**: either a small hand-authored `Command` list per pack (walk to each room in
   turn, pick up an item or two, talk to a keeper, let the pet act, pass a gate) or a simple
   scripted walker that moves toward each room in sequence and always talks to the keeper it
   reaches, realistic in the sense of "a plausible player's turn order," not randomised nonsense.
3. Replay the path against `RunState`, collecting a per-step event log (room, message line, pickup/
   drop, pet event) alongside the static pack/chapter/room prose from before.
4. At each room (or at a configurable stride of steps), build a prompt combining the static prose
   with a short window of recent dynamic events, and ask the model for 10-20 ambient one-liners
   that could plausibly appear *at that point in that specific run*.
5. CLI shape on the model of `grade.py --rubrics --selftest`: something like
   `python ambient.py --pack ../../packs/security-onboarding/en` to walk a full simulated path
   through the whole pack, or `--room phishing` to jump straight to one room's slice of the path
   for a fast iterate-on-one-room loop.
6. Print each room's id and the event-log slice that produced it, next to its batch of one-liners,
   so it's possible to tell *why* the model said what it said.
7. Time each generation call the same way `poc/llm-grader` was evaluated for speed; record findings
   (timing, and a qualitative read of output quality/repetition/on-voice-ness/relevance to the
   actual events fed in) in this issue or a short PoC report once run.

## Findings

Built as `poc/ambient-flavour/ambient.py`, walking a real pack through the same headless
`RunState.apply(Command) -> Frame` harness the project's own tests use (a trimmed copy of
`tests/test_dungeon.py`'s BFS walk/approach/pass-room helpers), folding every message line a
player would actually see into a running event log, and combining it with each room's authored
prose into one prompt per room.

Verified end to end against `packs/security-onboarding/en`, all 4 chapters and 12 rooms, with
Ollama and `qwen2.5:3b`: each room generated in roughly 1-4 seconds. Output stayed grounded in
each room's own keeper/setting (dust and toner in the Sorting Office, cold air in the Vault) rather
than drifting into generic fantasy-dungeon flavour. A side-by-side comparison of the same first
room (`phishing`) reached via `--pet dog` versus `--pet none` produced visibly different batches:
the dog run's one-liners picked up on "your dog snatches up a urgent memo" (small
creature/object detail near the pickup), while the no-pet run leaned on ambient office texture
(fluorescent lights, a ringing phone, dust) instead, evidence that the dynamic event log actually
changes the output rather than being ignored. See `poc/ambient-flavour/README.md`'s "Early
observations" for the full comparison.

Not yet tested: repeated runs of the identical path/room to check for repetition or format
breakage across runs, or a run against the Dutch locale. Both are cheap to try with the script as
built (`--lang nl`, or simply re-running the same command) but weren't part of this pass.

## Acceptance criteria

Given a pack directory and a scripted realistic path through it, when the script replays that path
against `RunState` and reaches a room, then it produces a batch of 10-20 ambient one-liners
grounded in both that room's authored prose and the actual events (pickups, pet actions, messages)
that occurred earlier on the simulated path.

Given two different simulated paths through the same room (e.g. one where the player picked up an
item beforehand, one where they didn't), when both are run, then this issue records whether the
generated one-liners visibly differ in a way that reflects that difference, as the core evidence
for whether context-aware generation is worth pursuing over the flat per-room version.

Given a single `--room` is specified, when the script is run, then only that room's slice of the
path and its batch are generated, for a fast iterate-on-one-room loop.

Given the script is run twice against the same path, when the two batches are compared, then this
issue records whether the model's phrasing is repetitive or format-broken across runs.

## Non-goals

- Not production code and not wired into `session`/`ui`/the pack format; nothing here ships to a
  learner. Like `poc/llm-grader`, this deliberately ignores the five rules (a script opening a
  socket directly, and reaching into engine/session internals a real feature wouldn't) because it
  is disposable.
- Not a decision about *where or when* ambient flavour would render in-game (a message-line
  rotation? an idle-turn flavour line? PLAN.md doesn't have this concept yet); that is a follow-up
  design question only worth asking once this spike shows the generation step itself is workable.
- Not a new pack-format field (e.g. `[flavour]` or similar); if this spike succeeds, the format
  question is separate follow-up work, not scope here.
- Not a general-purpose path planner or a fully randomised playthrough; one or a few realistic,
  mostly-linear scripted paths per pack are enough to test whether context changes the output.
- Not a benchmark of generation *speed* across machines (that's DELVE-0047's shape, applied to
  grading, not generation); this issue cares more about output quality, relevance to actual events,
  and repetition than cross-machine latency, though a rough timing note is still worth recording.
