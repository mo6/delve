---
id: DELVE-0029
title: Inventory item descriptions keep their source line breaks instead of reflowing
status: implemented
area: [session]
type: bug
epic: DELVE-0011
milestone:
version: 1.10.1
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: [pre-reset]
related: [DELVE-0016]
supersedes: []
docs: [docs/OBJECTS.md]
changelog:
---

# Inventory item descriptions keep their source line breaks instead of reflowing

## Summary

When the learner opens the pack (`i`), each carried object's `look` description is shown with the
hard line breaks from its Markdown source file still in place, then wrapped again to the panel
width. The result is a ragged, double-wrapped paragraph: a source line ends mid-sentence ("The
sender almost looks"), the next source line starts ("right, the link"), and the panel wrap adds its
own breaks on top. The description should reflow into a clean paragraph that fills the panel width,
the same way a keeper's lesson prose already does.

## Motivation / problem

`RunState._inventory_overlay` builds one `TextBlock("para", …)` per item from
`f"{label}\n{s.defn.look}"`, embedding `s.defn.look` verbatim. But `look` is stored as
`body.strip()` by the item parser (`content/parser.py`), so it is the raw item-file body, wrapped
at the author's source width (~90 columns). Those newlines survive into the panel as hard breaks.
Lesson and explanation prose does not have this problem because it goes through
`content/markup.py:tokenize`, whose paragraph rule joins wrapped source lines with a space
("paragraphs (wrapped source lines joined by a space)"). The inventory panel bypasses that
flattening, so the same prose reads correctly in a lesson and wrongly in the pack. A paragraph
ending mid-sentence is exactly the reading cost the panel wrapping exists to avoid (CLAUDE.md,
"Long text breaks on paragraph boundaries").

## Stories

### As a learner, I want an item's description to reflow to the panel, so that it reads as a paragraph and not a column of broken lines.

- Given a carried item whose `look` description is wrapped across several lines in its source file,
  when the learner opens the pack (`i`) and reads that item,
  then the description is shown as a single reflowed paragraph filling the panel width, with no
  break inherited from the source file's line wrapping.
- Given an item whose `look` is written as two or more paragraphs separated by a blank line,
  when it is shown in the pack,
  then the blank-line paragraph breaks are preserved (each paragraph reflows on its own), so a
  genuine break is kept while a soft wrap is not.
- Given an item's bold name heading its description,
  when the item is shown,
  then the name still sits directly above the reflowed description with no blank row between them
  (unchanged layout), and the name stays bold.
- Given the panel wraps a description that contains a domain, URL, or `code` span,
  when it reflows,
  then that span is not broken across lines (the existing `break_on_hyphens=False` /
  no-break-in-a-span rule from the lesson wrapping still holds).

## Non-goals

- Changing how `look` is stored (`content/parser.py` keeps `body.strip()`); the fix is at render
  time in the session, not in the parsed model.
- Changing the lesson, explanation, scroll, or message-log panels; they already reflow correctly.
- Any change to the pagination chrome, the `--More--` behaviour, or the panel height rules.

## Design notes / links

The reflow logic already exists: `content/markup.py:tokenize` turns a body into paragraph tokens
with wrapped source lines joined by a space, and it also handles blank-line paragraph splits and
inline `**bold**`/`` `code` `` spans. The fix is to route each item's `look` through the same
paragraph flattening the lesson uses, rather than embedding the raw string, while keeping the bold
item name as the block's heading. Because the session already imports `tokenize` (it builds lesson
views), no new dependency crosses a rule-1 boundary; this stays session-side view assembly (rule
2). Design essay: `docs/OBJECTS.md` (the inventory panel).

## Acceptance / verification

- A session test gives the learner an item whose `look` has hard-wrapped source lines and asserts
  the rendered inventory block contains the description as one reflowed run (no mid-sentence source
  break), with the item name still bold and directly above it. Covers the first and third stories.
- A test with a two-paragraph `look` asserts the blank-line break is preserved as a paragraph
  boundary. Covers the second story.
- `./run-tests.sh` passes (pytest, ruff, screen and issues-index checks).
