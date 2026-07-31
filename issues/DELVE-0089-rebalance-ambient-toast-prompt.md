---
id: DELVE-0089
title: Rebalance the ambient toast prompt away from carried items, toward the keeper and the room's lesson goal
status: proposed
area: [session]
type: feature
epic:
effort: medium
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by:
accepted_at:
commits: []
related: [DELVE-0064, DELVE-0060]
supersedes: []
docs: []
changelog:
reason:
---

# Rebalance the ambient toast prompt away from carried items, toward the keeper and the room's lesson goal

## Summary

The room-entry ambient toast (DELVE-0060/DELVE-0064) currently spends too much of its short
passage on what the learner is carrying and not enough on the keeper guarding the room, why they
guard it, and what the learner is actually there to learn. Adjust `backstory.PROMPT`'s instructions
so a generated passage weighs the keeper's stakes and the room's lesson goal alongside the floor
items, and keeps the learner's own carried items a genuinely minor, passing mention rather than a
detail the model dwells on.

## Motivation / problem

A real generated passage for Rook the Watchman's room (Chapter 3, security-onboarding):

> The floor is scattered with debris: an unbranded USB stick lies like bait, and beside it rests a
> sticky note where secrets have already leaked into entropy. A damp torchlight catches on your
> hardware token while you glance at the urgent memo whose deadline has expired hours ago in this
> dark cavernous silence. Do not touch the USB; here only Rook watches from the shadows of Chapter
> 3, waiting for those who cannot resist plugging their destiny into strangers' devices.

The learner's own hardware token gets a full clause ("A damp torchlight catches on your hardware
token"), while Rook is reduced to a single trailing clause with no sense of who he is or why he's
watching, and the room's actual lesson (what the learner needs to learn/do to pass) never comes
through at all beyond "do not touch the USB". `backstory.PROMPT`
(`delve/session/backstory.py`) explicitly tells the model to "Give these floor items the bulk of
the passage" and to give carrying only "a brief, secondary nod", which is roughly the right shape
for floor items vs. carrying, but the prompt gives the model no comparable instruction to actually
develop the keeper or the lesson objective as content: `keeper_clause` and `lesson_clause`
(`backstory.build_prompt`) are appended as bare, mechanical facts ("They are about to face Rook,
whose room requires a score of 75% to pass" / "This room teaches: recognising phishing bait") that
the model is free to compress into an afterthought, which is exactly what happened here.

## MUST / MUST NOT

1. MUST instruct the model to give the keeper's presence and motivation (who they are, what they
   guard, why, drawing on their name and `kind` voice flavour) real narrative weight, not a single
   trailing clause.
2. MUST instruct the model to work the room's lesson objective (`lesson_topic`, what the learner is
   there to learn or watch out for) into the passage as something the learner should be thinking
   about, not just an appended factual sentence it may or may not echo.
3. MUST NOT let the learner's carried items grow past their existing "brief, secondary nod"; if
   anything, tighten the instruction so a carried item never gets its own full descriptive clause
   the way "a damp torchlight catches on your hardware token" does above.
4. MUST keep the room's floor items as a primary focus (DELVE-0064's fix stands); this is a
   rebalancing among keeper/objective/floor-items/carrying, not a reversal back to atmosphere-led
   or carrying-led prose.
5. MUST NOT add any new authored content field to the pack format (no keeper "backstory" field
   exists today, only `Keeper.name`/`Keeper.kind` and the gate's `lesson.title`); the fix works with
   what `_room_prompt` already gathers, by instructing the model to draw more out of it, not by
   collecting more facts.

## Non-goals

- Not changing the character budget (`_PASSAGE_CHAR_BUDGET`, DELVE-0080) or the dungeon-setting/
  atmosphere framing (`_SETTING`, DELVE-0064's "items first" restructuring).
- Not changing the nudge prompt (`build_nudge_prompt`/`NUDGE_PROMPT`), which has its own, unrelated
  job (telling an idle learner to move).
- Not adding a new authored "keeper backstory" or "room objective" field to the room Markdown
  format; this is prompt-instruction tuning against facts already gathered.

## Design notes / links

- `delve/session/backstory.py` `PROMPT`'s "Focus mainly on..." / "Give these floor items the bulk
  of the passage... You may also give a brief, secondary nod to what the learner is already
  carrying, without dwelling on it" clause is the main seam to adjust, adding a parallel
  instruction for the keeper/objective.
- `build_prompt`'s `keeper_clause`/`lesson_clause` (`delve/session/backstory.py`) are the mechanical
  facts available to draw on; consider whether their own wording (currently phrased as scheduling
  facts, "requires a score of X% to pass") needs to change too, or whether a stronger instruction
  sentence alone is enough to get the model to dramatize them.
- Per DELVE-0064's own research note (`docs/research/ambient-toast-grigor.md`), small models
  reliably follow *structural* reordering/explicit instruction better than a soft "please also
  mention" aside stapled onto unrelated framing; a comparison run against the same models
  (qwen2.5:3b, qwen3.5:9b) before/after the wording change is worth doing the same way DELVE-0064
  did, rather than trusting a single sample.
- `docs/STYLE.md`'s voice rules (no em-dashes, tone) still apply to whatever replacement wording is
  chosen for `PROMPT`.

## Acceptance / verification

- A comparison run (informal, like DELVE-0064's own verification) across a handful of gated rooms
  in the pilot pack showing the new prompt gives the keeper and the lesson topic real narrative
  presence, and no longer gives a carried item its own descriptive clause.
- Existing ambient-toast tests (`tests/test_room_toast.py`, which already covers `build_prompt`/
  `PROMPT`) updated for whatever new clause wording is added, still asserting the room-objects and
  carrying inclusion/omission rules are unchanged.
- `./run-tests.sh` green, both locales.
