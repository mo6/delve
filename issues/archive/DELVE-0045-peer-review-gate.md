---
id: DELVE-0045
title: Explicit peer-review acceptance gate before implementation starts
status: implemented
area: [docs, tools]
type: story
epic:
effort: low
milestone:
version: 1.17.0
version_span:
created: 2026-07-26
updated: 2026-07-26
accepted_by: George Moses
accepted_at: 2026-07-26
commits: [c2b4fc7]
related: []
supersedes: []
docs: [SDLC.md]
changelog: '#1170---2026-07-26'
reason:
---

# Explicit peer-review acceptance gate before implementation starts

## Summary

Add an explicit acceptance step between an issue being drafted (`status: proposed`) and work
starting on it (`status: in-progress`): the issue must be shown to a peer (in this solo,
no-remote project, the human maintainer) who is asked outright whether it is accepted, and that
acceptance is recorded on the issue itself before any code is written against it.

## Motivation / problem

CLAUDE.md already requires "every change gets an issue first", and `issues/AGILE.md`'s
Definition of Ready already gates the move to `in-progress` on a checklist. But nothing in that
checklist requires a second party (human or otherwise) to actually say yes; an agent can draft an
issue and start implementing it in the same breath, with the "acceptance" implicit in nobody
having objected. That is a silent step exactly like the ones `docs/SDLC.md` §1 already calls out:
"places where the process currently depends on a human ... *remembering* a convention rather than
a tool *enforcing* it." Making the ask explicit, and its answer recorded, turns "was this
reviewed" from a question answerable only by memory into one answerable by reading the file.

## Stories

### As a maintainer, I want an issue to require an explicit accept before it moves to in-progress, so that implementation never starts on an unreviewed issue.

- Given a freshly drafted issue with `status: proposed` and no `accepted_by:` set,
  when the next step would be to start implementing it,
  then the issue is presented and the question "do you accept this issue?" is asked outright,
  and implementation does not start until the answer is yes.
- Given the issue is accepted,
  when the acceptance is recorded,
  then `accepted_by:` and `accepted_at:` are filled on the issue's front matter and `status:` is
  set to `in-progress`, in that order, before any code changes for the issue are made.
- Given an issue is not accepted (the peer asks for changes),
  when the issue is revised,
  then it stays `status: proposed` with `accepted_by:`/`accepted_at:` empty until re-asked and
  accepted.

### As a maintainer, I want the gate enforced by tooling, not just documented, so that it cannot be silently skipped.

- Given an issue file with `status: in-progress`, `implemented`, or `superseded`,
  when `./tools.sh issues --check` runs,
  then it fails if `accepted_by:` is empty (mirroring how it already fails an unsized
  `proposed`/`in-progress` issue missing `effort:`).
- Given an issue with `accepted_by:` set,
  when `./tools.sh issues --check` runs,
  then it also fails if `accepted_at:` is empty (the two are always set together).
- Given `status: proposed` or `rejected`,
  when `./tools.sh issues --check` runs,
  then no acceptance fields are required (a proposed issue is, by definition, not yet accepted).

## Non-goals

- Not a multi-person review workflow or a required second engineer; this is a solo, no-remote
  project (CLAUDE.md), so "peer" here is the human maintainer explicitly asked and answering, not
  a second reviewer's sign-off from a different person.
- Not retroactive: existing archived/implemented issues are not backfilled with `accepted_by:`.
- Not a change to the Definition of Ready's existing checklist items, which stay as they are; this
  adds one new gate alongside them, at the `proposed` -> `in-progress` transition specifically.

## Design notes / links

`docs/SDLC.md` §4 ("Define issues: the most mechanical phase") already frames issue definition as
deterministic-enough for a skill; this gate is the one deliberately non-mechanical step in that
phase, so it's called out there as the exception rather than folded into `write-issue`'s
automation. §1's "tool enforcing vs. human remembering" framing is the direct motivation.
`issues/AGILE.md`'s Definition of Ready gains one more bullet for the accepted-fields check;
`issues/TEMPLATE.md`'s front matter gains the two new optional fields, documented the same way
`effort:` already is. `CLAUDE.md`'s "every change gets an issue first" paragraph is updated to
state the gate plainly, since that's the file read every session before any issue work starts.

## Acceptance / verification

- `tools/issues.py --check` rejects an `in-progress`/`implemented`/`superseded` issue with a blank
  `accepted_by:`, and rejects `accepted_by:` set without `accepted_at:`; a `pytest` covering
  `tools/issues.py`'s lint function exercises both.
- `./run-tests.sh` stays green (this issue itself goes through the gate it describes: drafted
  here as `proposed`, then explicitly accepted before its own `status` moves to `in-progress`).
