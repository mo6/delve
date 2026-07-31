---
id: DELVE-0059
title: The Keys tab wastes half its page to blank lines between entries
status: implemented
area: [ui]
type: bug
epic:
effort: low
milestone:
version: 1.24.1
version_span:
created: 2026-07-30
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [93a8340]
related: [DELVE-0028]
supersedes: []
docs: [docs/SCREENS.md]
changelog: "1.24.1"
---

# The Keys tab wastes half its page to blank lines between entries

## Summary

The Help panel's Keys tab renders one `TextBlock("plain", ...)` per catalogue entry
(`RunState._keys_body`), and `ui/windows.py`'s generic pager (`_paginate`) inserts a blank line
between every top-level block, the same rule that gives a lesson's paragraphs breathing room. For
a dense list of one-line key explanations that rule roughly doubles the row count for no reason: at
100x30, the walking context's 12 entries need 2 pages (`--More--`) when every one of them would fit
on a single page if the list were packed tight, one line per entry with no gap. Every other Keys
context is affected the same way, just less visibly (fewer entries).

## Motivation / problem

Confirmed by comparing `windows._text_pages` against the real walking-context `HelpView`: today's
per-entry blocks paginate to `[11, 11]`, two pages, with roughly half of each page's rows spent on
blank separators; folding the same 12 entries into one block with hard line breaks (no blank-line
separator between them, the same trick `RunState._pack_body` already uses to keep a bold item name
directly above its description) paginates to a single page of all 12. The blank-line-between-blocks
rule is right for prose (a lesson, an explanation, the pack's item descriptions) where a paragraph
break is meaningful; Keys is a list of independent one-liners, closer to the message log
(`_history_overlay`), which already renders as tight numbered lines with no gap.

## Stories

### As a learner, I want the Keys tab packed tightly, so that I see as many keys as fit on one screen instead of paging through blank space.

- Given the walking context's 12 catalogue entries,
  when the Keys tab is shown at 100x30,
  then all 12 render on a single page with no `--More--`, matching what fits when there is no
  blank line between entries.
- Given any other context (a lesson, a question, the backpack, ...),
  when its Keys entries are fewer than a full page,
  then they render with no wasted blank rows between them either, and still page normally
  (breaking between whole entries, never mid-entry) once there are genuinely too many to fit.
- Given the Objectives tab and every other existing panel (a lesson, the pack, the message log,
  an explanation),
  when they are shown,
  then their spacing is completely unchanged; this is scoped to the Keys tab's own body
  construction, not `windows.py`'s general block-spacing rule.

## Non-goals

- Changing paragraph spacing for prose panels (lessons, explanations, the pack, the scroll): the
  blank line between blocks stays exactly as it is everywhere except Keys.
- A multi-column ("several entries per row") layout. Researched below; rejected for now as a poor
  fit given real entry lengths, not merely deferred for lack of time.
- Shortening or rewording any catalogue entry's explanation to make room for columns; explanations
  stay full sentences.

## Design notes / links

The fix mirrors `RunState._pack_body`'s existing pattern (`session/run.py`, DELVE-0029): instead of
one `TextBlock` per entry, build a single `TextBlock("plain", joined_text, spans=...)` whose spans
carry a literal `"\n"` between entries. `ui/windows.py`'s `_wrap_spans` already treats an embedded
`"\n"` as a hard line break with no inserted gap (that is precisely what keeps a bold item name
sitting directly above its wrapped `look` text, and is documented as such in that function's own
docstring), whereas `_paginate`'s blank-line rule only fires *between distinct top-level blocks*.
Folding all of a context's entries into one block sidesteps that rule entirely, with no change to
`_paginate`/`_blocks` themselves, so every other panel is provably unaffected (same code path,
untouched). Long individual entries continue to word-wrap within their own line as they do today;
`_wrap_spans` wraps each hard-break-separated segment independently, so a wrapped two-line entry
never gets a spurious blank inserted mid-entry either.

**Multi-column research** (measured against the real catalogue via `delve.strings.load("en")`):
entry lengths (`"{key}: {description}"`) range from ~26 to 54 characters, with most of the longer,
more useful ones (the ones a new command needs the most explaining) sitting at 40-54: `"t: Talk to
(or re-read) an adjacent keeper"` (42), `"@: Ask your companion for a hint (costs score)"` (46),
`"←→ / Enter: Move the highlight, then answer with Enter"` (54). The panel's inner text width is a
fixed 69 columns (`TEXT_W`, shared by every overlay, not something Keys can widen on its own
without a broader panel-width change affecting every other screen). Two side-by-side entries per
row would get roughly 32-33 columns each after a gap, shorter than most real entries, so a literal
two-entries-per-row layout would force most rows to wrap internally, very likely erasing the row
savings this issue is chasing and reintroducing per-entry alignment complexity for little gain. A
"key column, description column" table (one entry per row, just vertically aligned, via the
existing `kind="table"` block type / `_layout_table`) was also considered: it does not save any
rows at all (still one row per entry), so it does not address this issue's actual problem and is a
separate, purely cosmetic idea if ever wanted later. **Conclusion: multi-column is not recommended
here.** The tight single-column list from this issue's fix already gets the walking context (the
largest) down to one page; a genuine column layout would need either a wider panel (a bigger change
touching every overlay) or materially shorter descriptions (against the tab's whole purpose of
fully explaining a key, not abbreviating it like the one-line hint already does), so it is not
worth the complexity unless a future context's entry count grows much larger than today's.

## Acceptance / verification

- A test builds the walking-context `HelpView` and asserts `windows.page_count` (or
  `windows._text_pages`) returns exactly 1 page for its current 12 entries at 100x30, versus more
  than 1 before the fix.
- A test with a context deliberately given more entries than fit one page still asserts pagination
  breaks between whole entries (a wrapped entry's own lines never split across a page boundary).
- A test asserts the Objectives tab, a lesson, the pack (`i`), and the message log render with
  byte-identical spacing to before this change (no regression to the general pager).
- `./tools.sh screens --check` passes with the Help mock-up (DELVE-0028's screen 15) updated to
  show the denser list if its page count changes.
- `./run-tests.sh` passes.
