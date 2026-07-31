---
id: DELVE-0073
title: Coins and the torch get a real description in Info/Pack, like every other carried item
status: implemented
area: [session, delve]
type: bug
epic:
effort: low
milestone:
version: 1.26.4
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [pre-reset]
related: [DELVE-0068, DELVE-0071, DELVE-0069]
supersedes: []
docs: []
changelog: "1.26.4"
reason:
---

# Coins and the torch get a real description in Info/Pack, like every other carried item

## Summary

Every pack-authored item shows a bold title followed by its authored `look` description in
Info/Pack. The two engine-owned kinds every pack gets for free, money and the torch, currently
render as one bare plain-text line each ("35 coins", "A torch, lit (134 steps left).") with no
description at all, which reads as an inconsistency once a learner is also carrying a real
authored item to compare against. This issue gives both a generic, engine-owned description (both
locales) and renders them with the same bold-title-then-description shape as every other item.

## Motivation / problem

`RunState._pack_body` special-cases the lit torch and gold as single `TextBlock("plain", ...)`
lines, ahead of the loop that builds a `TextBlock("para", ...)` per carried `Stack` with a bold
title and, when the kind has one, its `look` text underneath. Money (`MONEY`) and the torch
(`TORCH`) are both `ItemDef`s with an empty `look` (DELVE-0069 already flagged this: "the
description of the coins and torches are generic"), so neither ever gets the description
treatment a pack-authored item does. Since neither is pack content (CLAUDE.md rule 5: content
never goes in frontmatter, and these two kinds exist under every pack, tutorial included), their
description belongs in the engine's own `Strings` catalogue, not a pack `items/` file.

## MUST / SHOULD

- MUST add a generic description for money (`item.money_look`) and the torch (`item.torch_look`)
  to both `delve/strings/en.toml` and `delve/strings/nl.toml`, written in the same neutral,
  mechanical voice the engine's other item strings already use (not pack-author flavour text).
- MUST render both in Info/Pack with the same bold-title-then-description block shape every other
  carried item already gets (`_pack_body`'s existing `TextBlock("para", ..., spans=(...))` path),
  rather than the current bare plain-text line.
- MUST keep the torch's title showing its remaining steps, using the existing lowercase,
  unpunctuated wording (`item.torch_lit_menu`, DELVE-0071) as the bold title, so the Pack tab and
  the drop menu now share one consistent torch label; the old full-sentence `item.torch_lit`
  ("A torch, lit ({n} steps left).") is retired as no longer used anywhere.
- MUST keep the coins title as today (`_coins(gold)`, e.g. "35 coins"), only adding the
  description underneath it.
- MUST NOT change anything about money's or the torch's actual mechanics (banking, burn-down,
  pickup/drop); this is a display-only change.

## Acceptance / verification

- A test asserting the Pack tab's torch block has a bold title matching `item.torch_lit_menu` and
  a description body matching `item.torch_look`.
- A test asserting the Pack tab's coins block has a bold title matching `_coins(gold)` and a
  description body matching `item.money_look`.
- A test (or an update to the existing DELVE-0071 test) confirming `item.torch_lit` is no longer
  read anywhere.
- `./run-tests.sh` passes in both locales.
