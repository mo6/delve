---
id: DELVE-NNNN
title: <short imperative title>
status: proposed          # proposed | in-progress | implemented | superseded | rejected
area: []                  # subset of: engine, content, assess, session, progress, ui, delve, docs, tools
type:                     # optional: epic | feature | story | bug (see AGILE.md)
epic:                     # the parent epic's REQ id (a feature/story); blank on an epic itself
effort:                   # low | medium | high; how much work an LLM coding agent (Cursor,
                          # Claude Code) would need to implement it. Required while proposed
                          # or in-progress; set it before moving out of proposed.
milestone:                # optional; omit for post-1.0 work
version:                  # target version; fill the shipped version on implementation
version_span:             # optional; first-last (e.g. 1.0.1-1.3.4) if the work spanned releases
created: YYYY-MM-DD
updated: YYYY-MM-DD
accepted_by:               # who explicitly accepted this issue (peer-review gate, AGILE.md);
                          # blank while status: proposed, required from in-progress onward
accepted_at:               # YYYY-MM-DD the acceptance above was given; set together with accepted_by
commits: []               # short SHAs, filled on implementation
related: []               # other REQ ids (siblings/dependencies); the parent epic goes in epic:, not here
supersedes: []            # REQ ids this replaces, if any
docs: []                  # design essays in docs/ that back this
changelog:                # CHANGELOG.md anchor, filled on release
reason:                   # optional; why a rejected issue was turned down
---

# <title>

## Summary

One paragraph: what changes and why, in plain language a non-developer could follow.

## Motivation / problem

The need this addresses. What is wrong, missing, or harder than it should be today.

## Stories

One or more user stories. Each is `As a <role>, I want <goal>, so that <reason>`, followed by its
acceptance criteria in Given / When / Then form. The roles are Delve's actors: **learner**, **pack
author**, **maintainer**. Keep every criterion observable and headlessly testable (rule 2). See
[AGILE.md](AGILE.md) for the full style.

### As a <role>, I want <goal>, so that <reason>.

- Given <starting state>,
  when <the role does X>,
  then <the observable, testable outcome>.
- Given <another state>,
  when <action>,
  then <outcome>.

### As a <role>, I want <goal>, so that <reason>.

- Given <...>, when <...>, then <...>.

<!-- A small change that does not warrant stories may instead use a plain numbered list of
     testable MUST / SHOULD / MUST NOT statements; the two forms coexist in the tree. -->

## Non-goals

What is explicitly out of scope, so the issue is not read as asking for more than it is.

## Design notes / links

Pointers into `docs/` and constraints from `CLAUDE.md` (the five rules, cross-platform,
locale). Do not re-derive the design here; link it. If the change affects what a screen looks
like, name the `./tools.sh screenshot` scenarios to re-check and note anything notable here.

## Acceptance / verification

How "done" is judged: named tests, `./run-tests.sh`, `delve validate`, or a manual play
path. Each story's Given / When / Then should map to a named test here. An issue with no
way to check it is not finished being written. The shared bar is the Definition of Ready (before
building) and Definition of Done (before archiving) in [AGILE.md](AGILE.md).

## Peer review

Left blank until the change is implemented and tested. Filled in as part of the Definition of
Done's landing gate ([AGILE.md](AGILE.md)): one line per reviewer, agent or human, appended (never
overwritten) as each review happens. At minimum this is the reviewing agent's pass and the
maintainer's own sign-off, in that order:

- **<reviewer name>** (agent|maintainer), YYYY-MM-DD: verdict, and a one-line pointer to any
  findings (fixed inline, or left as a follow-up issue), not a re-statement of what the diff does.
