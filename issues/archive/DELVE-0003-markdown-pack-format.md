---
id: DELVE-0003
title: Markdown pack format and validate
status: implemented
area: [content, assess]
milestone: M3
version: 0.3.0
created: 2026-07-17
updated: 2026-07-17
commits: [pre-reset]
related: [DELVE-0002]
supersedes: []
docs: [docs/AUTHORING.md, docs/PLAN.md]
changelog: "0.3.0"
---

# Markdown pack format and validate

## Summary

Replace the hard-coded slice content with real packs authored in Markdown. A pack is a tree
of chapters and rooms; each room is a lesson plus questions in plain Markdown, with metadata
in front matter. `delve validate` checks a pack against the format and pack policy, in both
locales.

## Motivation / problem

The slice proved the experience; now content must be answerable to real authors rather than
baked into Python. Markdown-first means a lesson reads top to bottom as a document, and a
second locale (Dutch) is the cheapest test that the format is about structure, not English.

## Requirements

1. A pack MUST be a directory tree `packs/<pack>/{en,nl}/<chapter>/<room>.md`, folder and file
   names being untranslated slugs.
2. A room MUST be Markdown: prose and questions in the body, metadata in front matter. Content
   MUST NOT live in front matter.
3. Question type MUST be inferred from option count alone: exactly 2 options is an assertion,
   3 or more is multiple choice. A `True`/`False` label check MUST NOT be used.
4. An H3 heading MUST be a question, checkboxes its options, and a `>` blockquote its
   explanation.
5. The parser MUST enforce the file format and raise on the first structural fault within a
   file, with a `file:line` message.
6. `delve validate` MUST enforce cross-file pack policy and gather every issue so one run
   reports all of them. The locale trees MUST match; a mismatch MUST error.
7. A missing `scroll.md` MUST be a warning, not an error.

## Non-goals

- Free-text questions (reserved syntax only; delivered in DELVE-0012).
- Any map file format. Generation stays the only path.

## Design notes / links

Validation split (parser enforces format, `schema.py` enforces policy) and the no-Pydantic
decision are in `CLAUDE.md`; authoring rules in `docs/AUTHORING.md`. The True/False bug that
the Dutch pack (`Waar`/`Niet waar`) exposed is why type is inferred from option count.

## Acceptance / verification

- `delve validate` on both shipped packs is clean, and runs in `./run-tests.sh`.
- Parser tests cover a malformed room raising with a `file:line`.
- The en and nl trees diff equal.
