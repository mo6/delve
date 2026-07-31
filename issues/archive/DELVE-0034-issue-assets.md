---
id: DELVE-0034
title: Attach files (screenshots) to issues via issues/assets
status: implemented
area: [tools, docs]
type: feature
epic:
milestone:
version: 1.11.1
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [6f5ec48]
related: []
supersedes: []
docs: []
changelog:
reason:
---

# Attach files (screenshots) to issues via issues/assets

## Summary

An issue can only reference a binary file (a screenshot clarifying a rendering bug, a photo of a
terminal) by describing it in prose. This adds a convention and a sibling `assets/` directory next
to each of the three places an issue file can live (`issues/`, `issues/archive/`, `issues/rejected/`),
plus a lint pass in `tools/issues.py --check` so a broken or orphaned attachment is caught the same
way a broken commit reference already is.

## Motivation / problem

A bug report is often clearest as a screenshot (a torn box border, a misaligned panel, a garbled
glyph on an unusual terminal). Today the only place to put one is outside `issues/` entirely, so
the issue file cannot link it, and there is no convention for where such a file would even go.

## Stories

### As a maintainer, I want to attach a screenshot to an issue, so that a rendering bug is evidence rather than a description of one.

- Given a proposed issue `DELVE-0040-some-bug.md` sitting in `issues/`,
  when I add a screenshot,
  then it lives at `issues/assets/DELVE-0040-torn-border.png` and the issue body links it with a
  Markdown image whose target is `assets/DELVE-0040-torn-border.png`.
- Given an asset filename that does not start with its own issue's id,
  when `tools/issues.py --check` runs,
  then it reports a problem naming the offending file.

### As a maintainer, I want an issue's assets to travel with it through archive/rejected, so that the tree stays self-contained and the relative link never breaks.

- Given `DELVE-0040-some-bug.md` moves to `issues/archive/` on implementation,
  when its assets move to `issues/archive/assets/` in the same commit,
  then the `assets/...` relative link in the doc still resolves without editing the doc.
- Given the same move for a rejected issue,
  when its assets move to `issues/rejected/assets/` instead,
  then the link still resolves there.

### As a maintainer, I want `tools/issues.py --check` to catch broken or orphaned assets, so that a missed file during a move or a stray screenshot is caught in CI rather than discovered by a reader.

- Given an issue body references `assets/DELVE-0040-foo.png` and that file does not exist next to
  the issue,
  when `tools/issues.py --check` runs,
  then it reports the missing asset.
- Given a file sits in an `assets/` directory that no issue in that same directory references,
  when `tools/issues.py --check` runs,
  then it reports the orphaned file.
- Given an asset filename that does not match `DELVE-NNNN-slug.ext`,
  when `tools/issues.py --check` runs,
  then it reports the naming problem.

## Non-goals

- No automated "archive this issue" command that moves the `.md` file and its assets together;
  the move stays the existing manual `git mv` per the lifecycle section, now covering two paths
  instead of one.
- No size, format, or binary-diff policy for the files themselves; that's a repo-hygiene question
  for later if it ever comes up, not part of this issue.
- No change to `issues/README.md`'s generated index beyond documenting the new directories in the
  Layout section; assets are not indexed per-row.

## Design notes / links

- Mirrors the existing `DELVE-NNNN-slug.md` naming convention (`issues/README.md` Front matter
  section) so an asset sorts and greps next to its issue's id rather than needing its own
  subdirectory scheme.
- Three sibling `assets/` directories, one per issue location, keep `archive/` and `rejected/`
  self-contained the same way the issue files themselves already are; an issue and its evidence
  never separate.
- Extends `tools/issues.py`'s existing lint (front-matter keys, contiguous ids, known commits,
  no em-dash) with the same "gather every problem before exiting" style, not a separate script.

## Acceptance / verification

`tools/issues.py` has no pytest harness today (it is checked, like `tools/screens.py`, by running
it directly as a step in `run-tests.sh`); this stays that way rather than inventing a new pattern.

- `tools/issues.py --check` on the current tree stays clean (no assets yet, so no new problems).
- Manual verification against a scratch asset, exercising each new failure mode in turn: a
  correctly named + referenced asset passes; a misnamed asset fails; a referenced-but-missing
  asset fails; an orphaned asset fails. Each is checked and then removed before committing, so no
  scratch file ships.
- `./run-tests.sh` passes, which runs `tools/issues.py --check` as one of its steps.

