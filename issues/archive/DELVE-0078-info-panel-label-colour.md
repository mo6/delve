---
id: DELVE-0078
title: Info/Help panels colour labels and item titles instead of flattening them plain
status: implemented
area: [session, ui, docs]
type: story
epic:
effort: medium
milestone:
version: 1.29.0
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [3f93afd]
related: [DELVE-0044, DELVE-0054, DELVE-0075, DELVE-0076]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.29.0"
reason:
---

# Info/Help panels colour labels and item titles instead of flattening them plain

## Summary

Three related gaps, found together while looking at the current build: the Grader and Status tabs
pad each row's label with spaces for column alignment (`"Model       {model} @ {host}"`) instead of
the `"Label: value"` colon convention the Objectives tab already uses, and neither tab colours the
label to set it apart from the value; and separately, Info/Pack's two-column layout
(`_draw_pack_columns`) flattens every description-column segment to plain text before drawing it,
which silently discards the bold styling `_title_block` already puts on the item's title line, so
the title reads as ordinary text instead of standing out. This story fixes both: a new `TextBlock`
kind, `"kv"`, colours the label half of a `"Label: value"` line; Grader and Status switch to that
colon convention (matching Keys and Objectives, which already use it and now pick up the same
colouring); and the Pack detail column draws its styled spans instead of stripping them, so the
existing bold title actually renders bold.

## Motivation / problem

Right now every row in the Grader and Status tabs looks like one undifferentiated block of text; a
learner (or the maintainer glancing at `delve doctor`-adjacent state mid-run) has to read the whole
line to find the label. The Objectives tab already solved this with `"Pack: {pack}"`-style colons,
but Grader/Status predate that convention and still align by padding. Separately, the Pack tab's
two-column layout (DELVE-0075/0076) deliberately kept the description column "plain text" as a
scoping decision at the time, but that means the one piece of styling `_title_block` already
computes, a bold item title, never reaches the screen: `_draw_pack_columns` builds `text = "".join(t
for t, _ in segs)` and calls `_put(stdscr, dr, desc_col, text[:PACK_DESC_W])` with no `attr`,
discarding every span's `strong` flag. This screenshot-confirmed gap is what prompted this story.

## Stories

### As a learner reading the Grader or Status tab, I want each row's label set apart from its value, so that I can scan the panel instead of reading every line in full.

- Given the Grader tab's `Model`/`Status`/`This run`/`Avg latency`/`Latency` rows and the Status
  tab's `Version`/`Pack`/`Locale`/`Terminal`/`Grader` rows, when either tab renders, then each row
  reads `Label: value` (a colon directly after the label, one space, then the value), matching the
  Objectives tab's existing `help.obj_pack` = `"Pack: {pack}"` convention exactly, replacing the
  current fixed-width space padding (`"Model       {model} @ {host}"` becomes `"Model: {model} @
  {host}"`), in both `en.toml` and `nl.toml` (each language keeps its own label word; only the
  separator convention changes).
- Given any of those rows, when drawn, then the label run (the text up to and including the first
  `": "`) paints in a distinct colour from the value that follows, using the existing 16-colour
  palette (no new `Colour`); the value half paints exactly as before (plain).
- Given a value that itself contains a colon (`http://localhost:11434`, `qwen2.5:3b`), when the
  label/value split happens, then only the **first** `": "` (colon immediately followed by a space)
  in the line is treated as the separator, so `Model: qwen2.5:3b @ http://localhost:11434` still
  splits after `Model` and not at either colon inside the value.
- Given the Keys and Objectives tabs, which already use the `"Label: value"` / `"key: description"`
  shape, when this story lands, then they pick up the same label colouring with no wording change
  (their strings already carry a colon; only the render path is shared, not rewritten).
- Given the Scoring > Rooms tab's glyph legend line (`"· sealed   ░ sat   ▒ ok   █ clear"`, no
  colon), when this story lands, then it is unaffected: it is not tagged as a label/value block, so
  it renders exactly as before.

### As a maintainer, I want the label/value split to be an explicit block kind rather than inferred from arbitrary text, so a colon inside ordinary prose elsewhere is never mistaken for a label.

- Given `session/views.py`'s `TextBlock.kind` (currently `'para' | 'bullet' | 'quote' | 'plain' |
  'code' | 'table' | 'bar'`), when this story lands, then it gains one more value, `'kv'`, used only
  by the four tabs above; every other caller of `TextBlock("plain", ...)` (toast/message text,
  `item.grader_offline`'s single explanatory line, etc.) is untouched and never colon-split.
- Given `RunState._condensed` (the shared block-builder for Keys/Objectives/Grader/Status/Scoring >
  Rooms), when reviewed, then it gains a `kv: bool = False` parameter that only changes the returned
  block's `kind` (`"kv"` vs `"plain"`); `_grader_body`, `_status_body`, `_keys_body`, and
  `_objectives_facts` pass `kv=True`, `_scoring_rooms_body` does not.
- Given `ui/windows.py`'s block-to-lines path (`_wrap_block_lines`), when a block's `kind` is
  `"kv"`, then it colon-splits each of the block's lines and colours the label, independent of
  whatever plain `spans` the block already carries (the colouring is computed in `ui`, matching
  rule 2: `session` supplies structured text, `ui` decides colour, the same division already used
  for a Scoring bar's fill colour).
- Given `windows._fill_status_size` (the Status tab's live "rows x cols" splice), when it rebuilds
  the size row's block, then it preserves the original block's `kind` (today it hardcodes
  `TextBlock("plain", ...)`, which would silently drop the new `"kv"` styling from every row in that
  tab, not just the size row, since it replaces the whole block); the `Terminal` row's own string
  changes from trailing-space padding (`"Terminal   "`) to `"Terminal:"` so the spliced `" {rows}x
  {cols}"` lands after a real colon like every other row.

### As a learner opening an item's detail in Info/Pack, I want its title to stand out from its description, so that I can tell at a glance which line is the name and which is the explanation.

- Given a selected pack entry with a `look` (`_title_block` builds `spans=((label, True), ("\n" +
  look, False))`, unchanged by this story), when Info/Pack draws the description column, then the
  title line renders with that span's existing styling (today's `strong=True` → bold/bright-yellow
  convention, the same one already used for `**bold**` markup elsewhere) instead of being flattened
  to plain text.
- Given `ui/windows.py:_draw_pack_columns`, when reviewed, then its description-column loop draws
  each wrapped line through the same styled-segment path every other panel already uses (e.g.
  `_put_line`) instead of `text = "".join(t for t, _ in segs)` followed by an unstyled `_put`, so no
  second, parallel "flatten to plain" code path is left for this one column.
- Given a pack entry with no `look` (`TextBlock("para", label, spans=((label, True),))`, the "bold
  label only" case already in `_pack_detail_body`), when its description column draws, then the
  label still renders styled the same way, since it goes through the same fixed render path as the
  two-line case.

## Non-goals

- No change to which rows exist in the Grader or Status tab, and no change to any value's wording
  or the numbers/tokens/latency shown; only the separator (space-padding to colon) and the new
  colouring.
- No change to the Pack tab's list column (the left column keeps its existing `bar_attr` reverse-
  video highlight on the focused row, DELVE-0076's own scope, untouched here).
- No new `Colour` beyond the existing sixteen (`ui/attrs.py`); this story picks one already-defined
  value for the `"kv"` label colour, it does not add a seventeenth.
- No change to how quote lines, bars, or `**bold**` markup already render; `"kv"` is an additional
  `kind`, not a replacement for any existing one.
- No sub-tab split, no new tab, no change to what data any of these four tabs surfaces; this is
  presentation only.

## Design notes / links

- `delve/session/views.py:TextBlock` is the only structural type change (`kind` gains `'kv'` as a
  documented legal value in its comment).
- `delve/session/run.py:_condensed` is the single shared block-builder to extend; `_grader_body`,
  `_status_body`, `_keys_body`, `_objectives_facts` are its four callers that opt in, `
  _scoring_rooms_body` is the one that does not.
- `delve/ui/windows.py:_wrap_block_lines` is where the new `kind == "kv"` branch belongs, alongside
  the existing `"code"` special case; `windows.py:_blocks`' generic `else: # para, plain, code`
  branch already routes any kind it doesn't special-case through `_wrap_block_lines`, so `"kv"`
  needs no new branch there, only in `_wrap_block_lines` itself.
- `delve/ui/windows.py:_draw_pack_columns` (DELVE-0075/0076) is the other render-side change: swap
  its flatten-and-`_put` loop for the styled-segment path (`_put_line` or equivalent).
- `delve/ui/windows.py:_fill_status_size` (DELVE-0044) needs its one-line fix (stop hardcoding
  `"plain"`) plus the `en.toml`/`nl.toml` `status_size` wording change.
- `delve/strings/en.toml`/`nl.toml`: `status_version`/`status_pack`/`status_locale`/`status_size`/
  `status_grader` and `grader_offline`(unchanged)/`grader_model`/`grader_status_warm`/
  `grader_status_cold`/`grader_status_none`/`grader_run`/`grader_avg`/`grader_latency` all change
  from padded alignment to `"Label: value"`.
- Colour choice: `Colour.BRIGHT_CYAN`, reusing the app's existing "cyan is the accent" language
  (the active tab pill, a Scoring bar's filled run, a quote line) rather than introducing an unused
  value; `Colour.BRIGHT_BLACK` was considered and rejected as the label colour, since bold-black
  renders indistinguishably close to the background on some terminal themes, the opposite of what
  a label needs.

## Acceptance / verification

- A `tests/test_render.py` case builds a `"kv"` block with a `"Model: qwen2.5:3b @
  localhost:11434"` line and asserts the label run (`"Model:"`) paints with the chosen colour's
  attribute while the value half does not.
- A `tests/test_render.py` case confirms a value containing a colon (`"Model:
  http://localhost:11434"`-shaped input) still splits only at the first `": "`.
- `tests/test_render.py:test_pack_views_focused_list_row_is_highlighted_not_the_description` is
  updated (its "the description stays plain" assertion no longer holds for the title line by
  design) to assert the title line *is* styled while the description body beneath it is not, kept
  under a new name reflecting the new behaviour.
- `tests/test_items.py`'s existing Grader/Status body tests are updated for the new colon wording
  (`"Model:"` not `"Model "` + padding) where they assert on exact substrings.
- `tests/test_languages.py` covers the reworded `status_*`/`grader_*` keys in both `en.toml` and
  `nl.toml`; the English wording pinned in tests doubles as the message-drift tripwire CLAUDE.md
  describes.
- `./tools.sh screens --check` and `./tools.sh infoscreen_mockups --check` stay green (neither the
  Status/Grader tabs nor the Pack detail column are in `all_screens()`/`infoscreen_mockups`'s
  asserted set, so no mock-up regeneration is expected, but both checks must still pass clean).
- `./run-tests.sh` is green.
