---
id: DELVE-0069
title: Info/Pack becomes a selectable item list with descriptions on demand, instead of one long page
status: implemented
area: [session, ui]
type: feature
epic:
effort: high
milestone:
version: 1.27.0
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [117bdc8]
related: [DELVE-0067]
supersedes: []
docs: []
changelog: "1.27.0"
reason:
---

# Info/Pack becomes a selectable item list with descriptions on demand, instead of one long page

## Summary

The Info/Pack tab currently prints every carried item's full description one after another
(`RunState._pack_body`), so a learner carrying several kinds pages through multiple screens just
to see what they're holding. This issue adds a sub-navigation inside the Pack tab: items list
compactly in columns (name/count, and for a torch, its remaining steps), selectable one at a
time, with the full description shown only for the currently-selected item.

## Motivation / problem

`_pack_body` builds one `TextBlock` per carried kind, each with a bold title line followed by its
full `look` description reflowed as a paragraph (DELVE-0029). This reads fine for one or two
items, but a learner carrying money, a lit torch, and a handful of pack-authored objects ends up
paging through several screens of descriptions just to get an inventory overview, which is the
opposite of what an inventory glance should cost. A compact list-then-detail view (the same shape
Scoring already gives Now/Rooms as sub-tabs, DELVE-0055) lets the learner see everything they
carry at once, and reach any one description only when they actually want it.

## Stories

### As a learner, I want the Pack tab to open on a compact list of what I'm carrying, so that I can see everything at a glance without paging through descriptions.

- Given the learner carries money, a lit torch, and one or more other kinds,
  when the Pack tab is opened,
  then it shows a columnar list of entries (one per kind, plus gold, plus the lit torch if any),
  each showing its label and count, with no description text inline.
- Given a torch (lit or an ordinary spare stack) appears in this list,
  when rendered,
  then its entry always shows remaining steps (the lit torch's own count, matching
  `item.torch_lit`'s wording; see DELVE-0067 for how a floor/spare torch's own charge is tracked).
- Given the learner carries nothing at all,
  when the Pack tab is opened,
  then it shows the existing empty-pack message (`item.inv_empty`), unchanged.

### As a learner, I want to select one item in the list to see its full description, so that the detail is available without being forced on me for every item at once.

- Given the compact list is showing,
  when the learner moves the selection (the same up/down or tab convention Scoring's sub-tabs
  already use) and confirms a selection,
  then the tab shows that one item's full description (its `look` text, reflowed as today), with
  a way back to the list.
- Given money or the lit torch is selected (kinds with no `look` at all, or only a generic one),
  when its description is shown,
  then it reads a generic, honest description (e.g. "coins", "a torch, lit") rather than a blank
  panel.

## Non-goals

- **Phase 2, not this issue:** authored per-item explanations beyond the existing generic `look`
  text (the issue's own example: a spear's description explaining, in depth, how and why the
  object is used). This issue only wires up the list/select/detail navigation using descriptions
  that already exist (`ItemDef.look`, and the generic money/torch text); richer authored content
  is future work and is explicitly out of scope here.
- No change to how items are picked up, dropped, or merged; this is a read-only view.
- No change to the Pack tab's position among Info's tabs, or to any other tab's navigation.

## Design notes / links

- Precedent: Scoring already has a sub-tab strip (Now/Rooms, DELVE-0055) and a row-focus toggle
  (`_info_sub_focus`); the Pack tab's list/detail split is closer to a row-selectable list than a
  second sub-tab strip, so it likely needs its own small piece of session state (which row is
  selected, list vs. detail mode) rather than reusing `_info_subtab` verbatim, but should follow
  the same input conventions for consistency.
- `RunState._pack_body` (`session/run.py`) is today's single-block-per-item builder; this issue
  replaces it with two builders (a list body, a detail body) and the state to switch between them,
  the same shape `_info_overlay`'s dispatch already uses for Scoring's sub_key branch.
- Rule 2 (`ui` paints only): the columnar layout (how many columns, spacing) is a `ui/windows.py`
  concern; `session` only needs to hand over the plain data (label, count, any per-item badge like
  "steps left") for `ui` to lay out.
- `docs/SCREENS.md` mock-ups for Info/Pack will need regenerating (`./tools.sh screens`) once the
  new layout exists, per CLAUDE.md's screen-mockup rule.

## Acceptance / verification

- A test asserting the Pack tab's list view shows one compact row per carried kind (plus gold,
  plus the lit torch when present), with no description text.
- A test asserting selecting an item switches to its detail view showing its full description.
- A test asserting money/the lit torch show a generic, non-blank description when selected.
- A test asserting an empty pack still shows the existing empty message, not an empty list.
- `./tools.sh screens --check` passes with Info/Pack's mock-ups regenerated.
- `./run-tests.sh` passes.
