---
id: DELVE-0064
title: Rework the room ambient prompt to lead with floor items, not atmosphere
status: implemented
area: [session]
type: feature
epic:
effort: low
milestone:
version: 1.26.0
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [697a569]
related: [DELVE-0060]
supersedes: []
docs: [docs/research/ambient-toast-grigor.md]
changelog: "1.26.0"
reason:
---

# Rework the room ambient prompt to lead with floor items, not atmosphere

## Summary

`session/backstory.py`'s `PROMPT`/`build_prompt` (DELVE-0060) opens every room's ambient toast
request with the shared dungeon-atmosphere framing (`_SETTING`: no sunlight, colder/damper by
`dlvl`, somber tone, a daypart/weekday nod) before ever mentioning what is actually on the floor,
and the room's own objects are named as a bare, undescribed noun phrase (`On the floor of this
room: a spear letter.`). Since the atmosphere framing is identical room to room, it stops adding
anything once a learner has seen a couple of rooms, while the one thing that *is* new each time,
the objects actually placed in this room, gets the least prompt weight and the least descriptive
material handed to the model. This issue reworks the prompt to lead with the floor items (using
each item's own authored description, not just its name), keep the carried backpack as a brief
secondary mention, and compress the dungeon-atmosphere framing to a single trailing constraint
rather than the opening paragraph.

## Motivation / problem

Manual research against the real prompt, recorded in
[docs/research/ambient-toast-grigor.md](../docs/research/ambient-toast-grigor.md), tested four
prompt variants against the shipped `01-the-sorting-office/02-targeted.md` room (Grigor, Who Was
Impersonated; floor object `spear-letter`, carried object `urgent-memo`) on both locally
configured models, `qwen2.5:3b` and `qwen3.5:9b` (the primary model for toast generation):

- **v1** (today's shipped prompt): atmosphere-first, bare object names. All three later variants
  were compared against this baseline.
- **v2**: same structure as v1, but each object's own `items/*.md` body is included alongside its
  name, giving the model real material to draw on instead of just a noun phrase.
- **v3**: v2's object descriptions, plus a reworded closing sentence asking the model to "describe
  the situation" and weave in floor items rather than "the room's own shape, light, and
  atmosphere." This alone did not work: `qwen3.5:9b` still opened on room atmosphere every time,
  because the *leading* two-thirds of the prompt (`_SETTING`) is still atmosphere-first framing,
  and it primes the reply before the closing sentence is ever reached. v3 also dropped the carried
  item from the reply entirely in both models' output.
- **v4**: restructures the whole prompt, not just the closing ask. Floor items are described first
  and explicitly asked to take "the bulk of the passage"; the carried item is framed as a
  deliberately brief secondary nod; the atmosphere/dungeon facts are compressed into a single
  trailing paragraph, with an explicit instruction not to describe the room's shape, walls, or
  layout, and not to open the passage with a scene-setting line. Tested against `qwen3.5:9b` only.
  Result: atmosphere shrank to a single opening clause ("The damp air smells of wet stone and
  stale ink..."), the floor item got a full sentence built from its own description, the carried
  item got a genuine (not dropped) secondary mention, and no sentence described the room's
  shape or walls.

v4 is the variant this issue proposes to ship, adapted from a single hand-run test into
`build_prompt`'s general form (every room's floor items, not just this one room's).

## Stories

### As a learner, I want each room's ambient passage to describe what is actually new in front of me, so that the toast keeps adding information past the first few rooms instead of repeating dungeon-mood boilerplate.

- Given a room with one or more floor objects,
  when its ambient prompt is built,
  then each floor object's own authored description (its `items/*.md` body, the same source
  `_room_items_description` already reads the name from) is included alongside its name, not just
  the bare noun phrase.
- Given the same room,
  when the prompt's closing instruction is read,
  then it asks the model to give the floor items the bulk of the passage and explicitly forbids
  describing the room's shape, walls, or layout, or opening the passage with a scene-setting line.

### As a learner, I want the backpack I'm carrying to still get a brief mention, so that the toast doesn't ignore items I'm holding just because the prompt now favours the room's own objects.

- Given the learner is carrying one or more items,
  when the prompt is built,
  then the carrying clause is framed as a deliberately secondary, brief nod (distinct from the
  floor-items clause), and is present whenever `carrying` is non-blank, exactly as today.
- Given the learner is carrying nothing,
  when the prompt is built,
  then the carrying clause is omitted entirely, exactly as today's blank-clause convention.

### As a maintainer, I want the dungeon-atmosphere facts (no sunlight, `dlvl`-scaled cold/damp, somber tone, daypart/weekday nod, the Dutch tutoyeer/`fakkel` clause, the `has_light` on/off framing) to still all reach the model, so that reworking the prompt's emphasis doesn't silently drop an existing, tested constraint.

- Given the same inputs `build_prompt` takes today (`pack`, `dlvl`, `chapter_title`, `keeper`,
  `requirement`, `lesson_topic`, `room_objects`, `carrying`, `pet`, `has_light`, `language`, `now`),
  when the reworked prompt is built,
  then every fact the current `_SETTING`/`PROMPT` express is still present somewhere in the
  output text (no sunlight/daylight/window ever, `dlvl`'s colder/damper clause, the somber-tone
  instruction, the daypart/weekday nod restricted to mood/torchlight/keeper-rhythm, the
  `has_light` on/off wording, and the Dutch-only tutoyeer/`fakkel` clause when `language ==
  "Dutch"`), just compressed and moved to a trailing paragraph instead of the opening one.
- Given an ungated room or one with a bare floor,
  when the prompt is built,
  then the existing blank-clause conventions for `keeper_clause`/`lesson_clause`/`objects_clause`
  (a room with nothing on its floor states that truthfully, "the floor of this room is bare",
  rather than omitting the clause) are unchanged.

## Non-goals

- Any change to `NUDGE_PROMPT`/`build_nudge_prompt` (the idle-nudge line), which has no floor-item
  clause to rework and is out of scope here.
- Any change to which model is used, `RoomBackstoryRunner`'s threading/queueing behaviour, or
  `RunState._room_prompt`'s call site beyond passing the same arguments to a reworded
  `build_prompt`.
- A wording/copy pass on the `_DUTCH_CLAUSE`, `_LIGHT_ON`/`_LIGHT_OFF`, or `_SETTING` constants
  beyond moving/compressing them; their content is unchanged.
- Re-running the research against `qwen2.5:3b`; the research doc notes v4 was only tested against
  `qwen3.5:9b` (the primary model for toast generation), and this issue does not require expanding
  that before shipping, though it may be worth doing informally during implementation.

## Design notes / links

Full instruction text and side-by-side model output for all four variants:
[docs/research/ambient-toast-grigor.md](../docs/research/ambient-toast-grigor.md). The v4
instruction there is the template to adapt into `backstory.PROMPT`/`build_prompt`; the object
description text used in that research (`spear-letter`'s and `urgent-memo`'s `items/*.md` bodies)
should generalize to whatever `_room_items_description`/`_backpack_description` already gather,
extended to also carry each item's description text, not just its `_item_phrase` name.

CLAUDE.md's own gotcha, DELVE-0057: never force `format: json` on this call (unaffected by this
issue, `json_mode=False` stays as-is). DELVE-0052: `think: False` stays unconditional. The research
doc also flags that `qwen2.5:3b` reached for an em-dash unprompted in two of the four variants
when given item descriptions to draw on; CLAUDE.md's em-dash ban is a pack-content rule, not
strictly an engine-string one, but worth a `-` in the prompt's own instruction text if this
recurs against the shipped model during implementation.

## Acceptance / verification

- A `test_backstory.py` (or equivalent) test asserts `build_prompt` includes a floor item's
  description text (not just its name) when `room_objects`/an equivalent richer parameter is
  supplied, and asserts the closing instruction text forbids room-shape/layout description.
- A test asserts the carrying clause remains present, brief, and secondary when `carrying` is
  non-blank, and is omitted when blank, matching today's convention.
- A test asserts every existing atmosphere fact (`_SETTING`'s no-sunlight/daylight/window
  constraint, the `dlvl` cold/damp clause, the Dutch tutoyeer/`fakkel` clause when
  `language == "Dutch"`, `has_light` on/off wording) is still present in the built prompt string,
  guarding against a silent drop while compressing `_SETTING` into a trailing paragraph.
- A manual spot-check against a live Ollama (`qwen3.5:9b`), reproducing this issue's own research
  method, that a real room with a floor object produces a toast that opens on the item rather than
  the room, mirroring the v4 result already recorded in the research doc.
- `./run-tests.sh` passes.
