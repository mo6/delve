---
id: DELVE-0014
title: Emoji and richer packs
status: implemented
area: [ui, session, content, delve]
milestone:
version: 1.8.0
version_span: 1.8.0-1.9.0
created: 2026-07-25
updated: 2026-07-25
commits: [pre-reset]
related: [DELVE-0013]
supersedes: []
docs: [docs/DISPLAY.md, docs/WIDEMAP.md]
changelog: "1.9.0"
---

# Emoji and richer packs

## Summary

The low-risk half of the enhanced-display plan, plus richer pilot content. A pack author may put
a single-codepoint emoji in lesson prose; the engine sprinkles one emoji onto a keyword in a
question prompt; every security-onboarding room gets a topic-relevant object; and the lesson
panel grows to use a taller terminal. Delivered across `1.8.0` (panel emoji, objects, taller
panel, placeholder warning) and `1.9.0` (question-prompt garnish).

## Motivation / problem

Map glyphs must stay ASCII (they are a fixed grid where one cell is one column), but flowed panel
text can carry an emoji for flavour at no layout cost, as long as the wrap counts display
columns. A little seasoning makes lessons warmer without touching the map.

## Requirements

1. A pack author MUST be able to put a single-codepoint emoji in a lesson or explanation.
2. Panel text wrap MUST count display columns, not characters (`ui/windows.py:_width`,
   `unicodedata.east_asian_width`), so a wide glyph never runs a line through the box border.
3. The validator MUST error on multi-codepoint emoji hazards (ZWJ, flag, skin-tone,
   variation-selector), which the width oracle cannot measure (`schema.py:_check_emoji`).
4. Map glyphs MUST stay ASCII; emoji MUST NOT be used as a map glyph.
5. The engine MUST garnish question prompts (`session/flavour.py`): at view-build time prepend
   one emoji from a per-locale `[flavour_emoji]` table to at most one keyword, sparsely.
6. The garnish pick MUST be a deterministic CRC of the prompt (never `self.rng`), MUST flavour
   the displayed string only (grading reads the options/answer, not the prompt), and MUST be
   skipped when the author already put an emoji in.
7. Every security-onboarding room MUST scatter one topic-relevant object.
8. The lesson panel MUST grow one body row per terminal row above the 100x30 floor, keeping a
   constant margin; the minimum-size layout MUST be unchanged.
9. `delve validate` MUST warn (advisory, non-blocking) on every author-marked placeholder.

## Non-goals

- The wide-tile emoji map and a `ui` theme layer (future work: `docs/WIDEMAP.md`,
  `docs/DISPLAY.md`).
- Windows/PDCurses emoji rendering, still unverified (the outstanding Windows item).

## Design notes / links

The emoji rules (panel prose allowed single-codepoint; question-prompt garnish; map stays ASCII)
are in `CLAUDE.md`; the full-emoji argument is `docs/DISPLAY.md` and the in-100-columns wide map
is `docs/WIDEMAP.md`. Single-codepoint is enforced by a test.

## Acceptance / verification

- A panel emoji test confirms the wrap counts columns and no line breaches the border.
- `delve validate` errors on a multi-codepoint emoji and warns on a placeholder.
- A garnish test confirms the pick is stable across redraws and does not change what the grader
  reads; about a fifth of the pilot's questions get one.
