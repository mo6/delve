---
id: DELVE-0081
title: Drop an item straight from Info/Pack instead of a standalone drop menu
status: implemented
area: [session, ui]
type: feature
epic:
effort: medium
milestone:
version: 1.31.0
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [d3abf3f]
related: []
supersedes: []
docs: []
changelog: "1.31.0"
reason:
---

# Drop an item straight from Info/Pack instead of a standalone drop menu

## Summary

`d` currently opens a standalone drop flow reachable from walking (`ui/keys.py`'s `_WALK`):
`_drop_menu_overlay` (a `MenuView` numbering every droppable kind, skipped when there is only
one) then, for a multi-count pile, an amount prompt. This issue removes that standalone flow and
moves dropping into the Info/Pack tab instead: `d` becomes valid only while Info/Pack is open and
a row is focused, and drops the focused row's kind, asking for an amount first when it is a
multi-count pile (coins, spare torches), exactly as the amount step already works today.

## Motivation / problem

The learner already picks *which* carried kind by moving the Pack tab's row focus (DELVE-0069's
list, `_pack_select`/`Select`); the standalone drop menu duplicates that same choice as a second,
separately-numbered list reached a different way, right after the learner may have just been
looking at the very row they want to drop. Folding drop into the tab they are already looking at
removes a whole menu step and the duplicated "which kind" decision.

## Stories

### As a learner, I want to drop the item I'm looking at in my pack with one key, so that I don't have to pick it again from a second menu.

- Given the Info/Pack tab is open and showing at least one carried kind,
  when I press `d`,
  then the focused row's kind is dropped: immediately if it is a lone unit (including the
  currently-burning torch), or after an amount prompt if it is a multi-count pile (coins, spare
  torches), the same digit-typing amount field the drop flow already has today.
- Given the amount prompt is open (from a Pack-tab drop),
  when I confirm a number or press Esc to cancel,
  then I land back on the Info/Pack tab, showing the pack's current contents (updated if I
  dropped), not fully closed back to walking.
- Given the Info/Pack tab is empty (nothing carried),
  when I press `d`,
  then nothing happens; there is no row to drop.
- Given I am walking (Info is not open) or any other Info tab, or help, or a lesson/question is
  open,
  when I press `d`,
  then nothing happens; `d` is otherwise unbound.

## Non-goals

- No change to `,` (Pickup) or its own menu; this issue is drop only.
- No change to what counts as droppable, or to the drop mechanics themselves (`_do_drop`,
  `_do_drop_lit_torch`, `can_place`, the lit-torch special case) beyond where the flow returns to.
- No new sort order for the Pack tab's rows.

## Design notes / links

- `ui/keys.py`: remove `ord("d"): Drop()` from `_WALK`; add it inside `panel_command`'s
  `isinstance(overlay, InfoView) and overlay.pack_rows` branch (the same branch that already
  claims up/down for `Select`), so `d` is only ever produced while the Pack tab's row list is
  showing.
- `session/run.py`: `_drop()` is rewritten to act on `self._pack_row` (via a new
  `_pack_droppable(idx)` built in the same order `_pack_entries` already lists rows in: lit torch,
  gold, inventory stacks) instead of `self.active/self._overlay is None` plus a fresh
  `_droppable_list()`/menu choice. `_drop_menu_overlay`, `_drop_select`, `_droppables`, and the
  `_answer`/`_confirm` dispatch's `"drop_menu"` branches are deleted outright (Pickup's own menu
  and `_pickables` are untouched). The `"drop_amount"` overlay kind, its `AmountView`/digit/
  backspace/confirm plumbing, and its `en.toml`/`nl.toml` strings are kept, but its
  Esc/confirm-with-nothing-typed path changes from `_close_item()` (closes the whole panel) to a
  new `_close_pack_drop()` that rebuilds `_info_overlay()` on the Pack tab instead and clamps
  `_pack_row` to the (possibly now shorter) list. `_do_drop`/`_do_drop_lit_torch` switch their own
  tail call from `_close_item()` to `_close_pack_drop()` too, since the Pack tab is now the only
  path that reaches either.
- `session/help.py`: drop `CommandEntry("d", "help.drop", {"walking"})`, add a Pack-tab-scoped
  replacement; drop `"drop_menu"` from `_DISMISSIBLE` and from `help.menu_choose`'s contexts
  (`pickup_menu` keeps it); `"drop_amount"` stays wherever it already appears (Esc/`?`/the amount
  field rows), since it is still a real, if now Pack-only, context.
- `strings/en.toml`/`nl.toml`: `item.nothing` ("You have nothing to drop") becomes dead (no caller
  left, since pressing `d` on an empty pack is silently a no-op per the third story above) and
  should be deleted in both locales; `hint.carrying` (shown while walking once something is
  carried) drops its `Drop: d` mention, since that key no longer does anything from walking;
  `hint.inventory` gains a Pack-tab, non-empty-pack variant that names `Drop: d`
  (mirroring how `hint.inventory_sub` already branches Scoring's own hint off the same `_hint()`
  method); exact wording is an implementation call, not spelled out here.
- Test surface to rewrite, not just delete (`tests/test_items.py`, `tests/test_help.py`,
  `tests/test_help_catalogue.py`, `tests/test_torch.py`): every test that opens the standalone
  drop menu (`run.apply(Drop())` while walking, `run._droppable_list()`, `MenuItem`/`MenuView`
  assertions on a `"drop_menu"` overlay) needs to instead open Info/Pack, move `_pack_select`
  focus to the target row, then send `Drop()`.

## Acceptance / verification

- A test asserting a lone droppable Pack row drops immediately on `d` and the panel stays open on
  an updated Pack tab.
- A test asserting a multi-count Pack row (coins) opens the amount prompt on `d`, and confirming
  an amount drops that many and returns to Pack, not to walking.
- A test asserting Esc from that amount prompt returns to Pack (not a full close), with nothing
  dropped.
- A test asserting `d` does nothing while walking, and does nothing on an empty Pack tab.
- A test asserting the currently-burning torch (DELVE-0062/0071/0067's own lit-torch drop path)
  is still reachable and droppable as a Pack row.
- `./run-tests.sh` passes in both locales.
