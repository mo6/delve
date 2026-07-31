---
id: DELVE-0074
title: Generalise Stack's torch-only charge field into per-unit item properties
status: proposed
area: [engine, content, session]
type: feature
epic:
effort: high
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by:
accepted_at:
commits: []
related: [DELVE-0062, DELVE-0067]
supersedes: []
docs: [OBJECTS.md]
changelog:
reason:
---

# Generalise Stack's torch-only charge field into per-unit item properties

## Summary

DELVE-0067 gave `engine/items.py:Stack` a `charge: int | None` field so a dropped torch remembers
its remaining burn steps instead of relighting at full duration, and so two torches at different
charge render as distinct piles instead of merging into one. That field is named, typed, and
documented as torch-specific; nothing about it is reusable by a future pack-authored kind that
needs its own per-unit state. This issue asks whether, and how, to turn `charge` into a general
per-unit property mechanism so any item kind can carry state that distinguishes individual units of
the same kind, rather than adding a new dedicated `Stack` field every time this need recurs.

## Motivation / problem

Today `Stack` is `(defn, count, charge)`. `charge` means one specific thing (torch steps
remaining); `merged()`/`taken()` compare it by name, and `_torch_charge_label` in `session/run.py`
formats it with torch-specific wording and a torch-specific fallback (`TORCH_DURATION_STEPS`). If a
pack author or a future engine-owned kind ever needs comparable per-unit state (a stamp that
remembers which classification tier it was set to, a note that remembers whether it's been read, a
device that remembers a charge level of its own, unrelated to the torch), there is no slot for it:
the only options today are to overload `charge` for an unrelated meaning (confusing, and breaks the
moment two kinds both want it at once) or to add another single-purpose field to `Stack` the same
way, repeating this issue's work per kind. Neither scales. This is a design question raised while
reviewing DELVE-0067, not yet a confirmed requirement: **whether** a generic mechanism is worth
building before a second concrete need for it exists is itself part of what this issue must settle,
against `docs/OBJECTS.md`'s existing design (section 4, "the item model", and section 9,
"pack-defined objects").

## Stories

### As a maintainer, I want to decide whether per-unit item state should be a named single-purpose field (torch charge) or a generic mechanism, before a second need for it forces the decision under pressure.

- Given `docs/OBJECTS.md` section 4 (the item model) and section 9 (pack-defined objects) as the
  standing design, when this issue is implemented, then it either amends those sections with the
  generalised model or records the decision to keep per-unit state single-purpose for now and
  close this issue as not-yet-needed.
- Given the torch is the only kind using `charge` today, when a generic mechanism is designed,
  then the torch is migrated onto it (not left as a special case beside a new general one), so the
  codebase never carries two competing ways to express the same idea.

### As a pack author, I want to declare that an item kind of mine carries its own per-unit state, so I can build something like a torch without the engine needing to special-case my kind by name.

- Given a pack author defines a new item kind with declared per-unit state (the concrete shape,
  e.g. a typed key/value, a single opaque value, or something narrower, is this issue's design
  work to settle),
  when two units of that kind are placed with different state,
  then they behave like two differently-charged torches do today: they never silently merge into
  one indistinguishable pile, and each is shown with its own state in every place a pile is shown
  (pickup menu, drop menu, Info/Pack).
- Given two units of a pack-authored kind carrying identical per-unit state,
  when they end up on the same tile or in the same pack,
  then they merge into one counted stack, exactly as two identical-state torches do today.

### As a maintainer, I want the snapshot format to keep round-tripping any per-unit state generically, so a new stateful kind doesn't need its own snapshot code path the way the torch charge did.

- Given a pack-authored kind with per-unit state placed on the floor or in the pack,
  when a run is snapshotted and resumed,
  then that state survives the round trip the same way `Stack.charge` does today
  (`session/snapshot.py`), without `to_dict`/`apply_dict` growing a new per-kind branch.
- Given a snapshot written before this issue ships,
  when it is loaded after,
  then it still loads (the existing torch-charge backward-compatibility path, or its generalised
  successor, must not regress).

## Non-goals

- No change to the torch's own behaviour or wording as a *result* of this issue; DELVE-0067's
  acceptance criteria stay met. Migrating the torch onto a generalised mechanism must be
  behaviour-preserving.
- Not asking for a new shipped item kind that exercises per-unit state; that's a pack-authoring
  exercise for after this lands, if it lands.
- Not committing in advance to any particular shape (typed field vs. a generic key/value bag vs.
  something narrower); that is exactly what this issue's design pass must decide, weighing
  `content/schema.py`'s hand-rolled validation (CLAUDE.md: "No Pydantic") and rule 5 (content
  never goes in frontmatter, so any declared shape still needs to respect where content and
  metadata are allowed to live).

## Design notes / links

- `engine/items.py:Stack`/`merged`/`taken` (DELVE-0067) is the concrete precedent and the thing
  being generalised or explicitly left as-is.
- `docs/OBJECTS.md` section 4 (the item model) and section 9 (pack-defined objects, the closed
  authoring vocabulary) are the standing design this issue must reconcile with; read both before
  proposing a shape.
- `content/schema.py` is where any new pack-authored declaration would need validation, hand-rolled
  per CLAUDE.md, with file:line author errors.
- `session/snapshot.py`'s `_stacks`/`_unstack` is where round-tripping lives today, torch-specific;
  a generalised version needs the same backward-compatibility discipline for a pre-existing save.
- CLAUDE.md rule 1 (`engine` never imports `content`/`assess`/`session`/`ui`) still applies: whatever
  shape per-unit state takes, `engine/items.py` stays the pure data model, with any pack-authoring
  or session-side interpretation layered outside it.

## Acceptance / verification

This issue's first deliverable is the decision itself (generalise now, or explicitly defer), not
code; write it up against `docs/OBJECTS.md` and get it accepted before implementation work starts,
the same Definition-of-Ready gate every issue uses. If the decision is to build it:

- A test that two units of a pack-authored kind with different declared per-unit state never merge
  on the floor or in the pack (mirroring DELVE-0067's torch tests).
- A test that two units with identical per-unit state do merge.
- A test that the torch, migrated onto the generalised mechanism, still passes every existing
  DELVE-0067 acceptance test unchanged.
- A snapshot round-trip test for a pack-authored kind's per-unit state, plus the existing
  backward-compatibility test for a pre-this-issue save.
- `./run-tests.sh` passes.
