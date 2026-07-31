---
id: DELVE-0067
title: A dropped torch remembers its remaining burn steps instead of relighting at full duration
status: implemented
area: [engine, session]
type: bug
epic:
effort: high
milestone:
version: 1.26.5
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [pre-reset]
related: [DELVE-0062, DELVE-0063]
supersedes: []
docs: []
changelog: "1.26.5"
reason:
---

# A dropped torch remembers its remaining burn steps instead of relighting at full duration

## Summary

Dropping the currently-burning torch and picking the same torch back up currently relights it at
full duration (`TORCH_DURATION_STEPS`), silently discarding however many steps it had already
burned. This is not just a display gap: two torches sitting on the floor (one freshly dropped
half-spent, one never used) are today indistinguishable and mechanically identical, since a torch
carries no notion of its own remaining charge once it is a floor `Stack` rather than the single
`player.torch_charge` counter. This issue makes a torch's remaining charge a property of the
individual torch, tracked through drop and pickup.

## Motivation / problem

`engine/items.py:Stack` is a bare `(defn, count)` pair; identical kinds merge on pickup/drop with
no per-unit state, which is exactly right for money and any other kind but loses information for
a torch, whose whole reason for existing (DELVE-0062) is that it *does* have individual state (how
many steps are left). `RunState._do_drop_lit_torch` (`session/run.py`) explicitly documents today's
behaviour as intentional: it "leaves an ordinary torch `Stack(1)` on the tile, exactly what
picking it back up unlit relights" at full duration. That was a reasonable simplification when the
mechanic first shipped (DELVE-0063 added the ability to drop the lit torch specifically to reach
the unlit ambient scene on demand), but it means a learner who parks a mostly-burned torch to grab
a fresh one can never tell them apart later, and picking either back up is always "as good as new."

## Stories

### As a learner, I want a torch I drop to keep whatever charge it had left, so that picking it back up later doesn't unfairly refill it.

- Given the learner is carrying a lit torch with `N` steps remaining (`0 < N < TORCH_DURATION_STEPS`),
  when they drop it,
  then the torch left on the floor remembers `N`, not `TORCH_DURATION_STEPS`.
- Given that torch is later picked back up while the learner has no other working torch,
  when the pickup resolves,
  then it relights with exactly the `N` steps it had when dropped, and continues burning down
  from there.
- Given the learner drops a torch and it is never picked up again,
  when the burn-down mechanic is otherwise exercised,
  then nothing changes about how a *carried, currently-lit* torch burns (`_tick_torch` is
  untouched); this issue is only about what a floor torch remembers.

### As a learner, I want multiple torches on the floor to be distinguishable by their remaining charge, so that I can tell a nearly-spent one from a fresh one.

- Given two torches lie on the same tile, one fresh (never lit) and one dropped with steps
  remaining,
  when the learner looks at the pile (pickup menu, Info/Pack, or wherever piles are listed),
  then each is shown with its own remaining-steps figure rather than being folded into one
  indistinguishable stack of "2 torches."
- Given a fresh, never-lit torch,
  when shown anywhere charge is displayed,
  then it reads as full duration (`TORCH_DURATION_STEPS`), not as charge-less or blank.

## Non-goals

- No change to `TORCH_DURATION_STEPS` or how fast a carried torch burns.
- No stacking/merging of two different-charge torches into one displayed entry; this issue
  accepts that distinct charges must render as distinct entries, however that ends up looking.
- No retroactive fix for existing snapshots written before this change; a torch already on the
  floor with no stored charge in an old save may default to full duration on load.

## Design notes / links

- The core design question this issue must settle during implementation: `engine/items.py:Stack`
  merges identical `defn.id`s into one counted pile, which has no room for two torches at
  different charges. Options include a per-torch charge stored alongside the pile (e.g. a
  parallel structure keyed by floor position, or a `Stack` variant that isn't blindly merged for
  the torch kind specifically) or giving `Stack` an optional `charge: int | None` field that
  `merged()`/`taken()` treat specially for the torch id (never merging two different charges into
  one stack). Whichever is chosen must round-trip through `session/snapshot.py` (a resume must not
  lose a floor torch's remembered charge).
- `RunState._do_drop_lit_torch`/`_do_pickup_torch` (`session/run.py`) are the two call sites that
  currently throw the charge away on drop and reset it to full on pickup; both need to carry the
  charge through instead.
- CLAUDE.md's RNG-streams gotcha and rule 1 are not implicated here, but the snapshot format
  change should be reviewed against `session/snapshot.py`'s existing round-trip tests.

## Acceptance / verification

- A test dropping a partially-burned torch and confirming the floor stack records its remaining
  steps, not full duration.
- A test picking that same torch back up (with no other torch lit) and confirming it relights at
  the remembered charge.
- A test placing a fresh and a partially-burned torch on the same tile and confirming both are
  independently visible with their own remaining-steps figures.
- A snapshot round-trip test confirming a floor torch's charge survives a save/resume cycle.
- `./run-tests.sh` passes.
