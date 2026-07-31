---
id: DELVE-0036
title: Cap issue asset images at 800px wide, and lint for it
status: implemented
area: [tools, docs]
type: bug
epic:
milestone:
version: 1.11.2
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [pre-reset]
related: [DELVE-0034, DELVE-0035]
supersedes: []
docs: []
changelog:
reason:
---

# Cap issue asset images at 800px wide, and lint for it

## Summary

DELVE-0034 added `issues/assets/` for files attached to an issue, but did not say anything about
size. The five screenshots attached to DELVE-0035 landed at their original screen-capture
resolution (1096-2000px wide, 700KB-1.4MB each), which is far more than a Markdown viewer needs
and needlessly bloats the repo. This resizes those five images down to a manageable width and
extends `tools/issues.py --check` to catch the next oversized one before it is committed, the same
way it already catches a broken asset reference or an orphaned file.

## Motivation / problem

A screenshot attached to clarify a bug (a torn border, a misaligned panel) is read at panel width
in a Markdown viewer; it does not need to be full native screen resolution, and at native
resolution five images already added ~4.8MB to the repo for one issue. Nothing caught this when
DELVE-0035 was written because DELVE-0034 only checked that a reference resolved and wasn't
orphaned, not that the file itself was a reasonable size.

## MUST

- Every PNG/JPEG file added to an `assets/` directory (`issues/assets/`, `issues/archive/assets/`,
  `issues/rejected/assets/`) MUST be at most 800px wide.
- `tools/issues.py --check` MUST read the image's width from its own header (stdlib only, no new
  dependency: PNG's `IHDR` chunk and JPEG's `SOF0`/`SOF2` marker both carry width in-band) and
  report any asset over 800px wide as a lint problem, gathered alongside the existing asset checks.
- The five images already attached to DELVE-0035 (`issues/assets/DELVE-0035-*.png`) MUST be resized
  in place to at most 800px wide, aspect ratio preserved, before this issue is archived.
- `issues/README.md`'s asset convention paragraph MUST say the 800px limit and give the one-line
  macOS command (`sips --resampleWidth 800 file.png`) a maintainer can run before adding a file.

## Non-goals

- No automated resize-on-commit hook; a maintainer resizes by hand before adding a file, the same
  way the em-dash rule and the emoji-sequence rule are caught by review/lint rather than
  auto-fixed.
- No height cap or aspect-ratio enforcement; width is what blows up a screenshot, and 800px wide at
  a screen's native aspect ratio is already a reasonable file size.
- No change to what file types are allowed; still whatever `ASSET_NAME_RE` already accepts
  (DELVE-0034), this only adds a width check for the two formats a screenshot is realistically
  saved as.

## Design notes / links

Extends `tools/issues.py`'s lint (DELVE-0034's asset checks: reference resolves, filename
convention, no orphans) with the same "gather every problem, exit non-zero" style rather than a
separate script. Reading width from a PNG/JPEG header needs no library: a PNG's first chunk after
the 8-byte signature is always `IHDR`, whose first 8 bytes are big-endian width then height; a
JPEG's `SOFn` marker (`0xFFC0`-`0xFFC3`, excluding the multi-scan `0xFFC4`/`0xFFC8`/`0xFFCC`) is
followed by a 2-byte length, 1-byte precision, then big-endian height then width. Both fit in a
handful of lines with `struct`/slicing, matching the repo's stdlib-only, hand-rolled-validation
line (no Pydantic, no Pillow).

## Acceptance / verification

- `tools/issues.py --check` on the resized DELVE-0035 assets stays clean.
- Manual verification: a scratch PNG wider than 800px placed in `issues/assets/` and referenced
  correctly still fails `--check` on width alone; removed before committing.
- `./run-tests.sh` passes, which runs `tools/issues.py --check` as one of its steps.

