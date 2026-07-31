---
id: DELVE-0072
title: Dropping with only one droppable thing skips the menu, mirroring pickup
status: implemented
area: [session]
type: bug
epic:
effort: low
milestone:
version: 1.26.3
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [pre-reset]
related: []
supersedes: []
docs: []
changelog: "1.26.3"
reason:
---

# Dropping with only one droppable thing skips the menu, mirroring pickup

## Summary

Pickup already has a convenience: when only one kind sits on the tile, `_pickup` skips straight
to `_pickup_select(0)` instead of opening a menu just to choose the only option, and if that one
kind is a single unit it drops straight into the player's hands with no further prompt. `_drop`
has no equivalent shortcut: even with only one droppable thing in the whole pack (one item, no
gold, no lit torch, or any single one of those alone), it always opens the drop menu first, asking
the learner to confirm a choice that was never actually a choice.

## Motivation / problem

A playtesting note: with a single item in the pack, pressing drop still requires picking "1" from
a one-entry menu before anything happens, an extra keypress and a beat of friction for a decision
that has only one possible answer. `_pickup` already solved this exact shape of problem
(`RunState._pickup`'s `if len(self._pickables) == 1: self._pickup_select(0); return`); `_drop`
should follow the same rule.

## MUST / SHOULD

- MUST make `_drop` skip the drop-menu overlay and go straight to `_drop_select(0)` when
  `_droppable_list()` returns exactly one entry, the same way `_pickup` already skips its menu for
  one pickable.
- MUST preserve the existing single-unit-vs-many rule downstream of that: if the one droppable
  entry's count is 1 (an ordinary single item, the lit torch, or a single coin), it drops
  immediately with no further prompt (`_drop_select`'s existing `available <= 1` branch already
  does this); if its count is greater than 1 (e.g. the only droppable thing is a pile of several
  coins), the amount overlay still opens to ask how many, exactly as pickup already asks for a
  multi-count single kind.
- MUST NOT change behaviour at all when two or more droppable entries exist; the drop menu still
  opens as today.

## Acceptance / verification

- A test dropping with exactly one carried item (nothing else droppable) and confirming it drops
  immediately with no overlay ever shown.
- A test with exactly one droppable entry whose count is greater than one (e.g. only gold, several
  coins) and confirming the amount overlay opens (not the drop menu, and not an immediate drop of
  everything).
- A regression test confirming the drop menu still opens normally with two or more droppable
  entries.
- `./run-tests.sh` passes.
