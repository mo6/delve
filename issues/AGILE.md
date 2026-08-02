# Agile issues style for Delve

How to write a Delve issue as agile user stories, grouped into features and epics, each
carrying explicit acceptance criteria and a shared Definition of Ready and Definition of Done.
This sits on top of the mechanics in [README.md](README.md) (front matter, lifecycle, the
`DELVE-NNNN` id sequence, `tools/issues.py`); it does not replace them. An issue file is still a
`DELVE-NNNN-slug.md` with the same front matter and the same archive-on-done move. This document is
about the *shape of the prose* inside it.

Adopt as much of this as a change warrants. A one-line tooling fix does not need an epic; a new
in-world system does. The point is a common vocabulary, not ceremony.

## The hierarchy: epic, feature, story

Three tiers, largest first. They map onto the existing `DELVE-NNNN` files; nothing new to install.

- **Epic**: a large body of work, usually a whole arc across several releases. In Delve's
  backfilled set these are things like *Objects, money, on-pass reward* (DELVE-0010, `1.0.1`-`1.3.4`)
  or *The companion pet* (DELVE-0011). An epic is its own `DELVE-NNNN` file whose body is mostly a
  **list of its child features and stories**, each a link to another `DELVE-NNNN`. An epic is rarely
  built in one commit; it is done when its children are.
- **Feature**: a mid-level, shippable slice of an epic that delivers value on its own. Usually one
  release (`1.1.0` "the reward" was a feature of the objects epic). A feature is a `DELVE-NNNN` file
  with real user stories and acceptance criteria.
- **Story**: one actionable change, small enough to build and verify in a sitting. A story is
  either a section inside a feature's issue, or its own `DELVE-NNNN` when it is worth tracking
  and archiving separately.

An issue file is one tier, declared in front matter: `type: epic | feature | story`. A feature
or story names its parent epic in a dedicated `epic: DELVE-NNNN` field; an epic leaves `epic:` blank
(it has no parent). Keeping the parent in its own field, not buried in `related:`, is what makes "all
issues of an epic" a query rather than a grep through prose: `tools/issues.py` reads `epic:`,
generates an **Epics** rollup in the index listing each epic and its children, and checks that every
`epic:` points to a real issue that is itself `type: epic`. Use `related:` for siblings and
dependencies, and `supersedes:` when a split replaces an older file. Do not restate the tier or the
epic in the body; the front matter is the single source, so there is no `Tier:` line to drift.

Every issue also carries `effort: low | medium | high`, an estimate of how much work an LLM coding
agent (Cursor, Claude Code) would need to implement it, judged from the acceptance criteria: how
many modules it touches, whether it needs new parsing/schema, whether it is UI-only or
cross-cutting. `tools/issues.py` requires it while `status` is `proposed` or `in-progress`, so a
newly authored issue is unusable until its author has actually sized it; it is not required (and is
not backfilled) on already-archived or rejected issues, since sizing work that is already done or
turned down has no use. An epic still sets it, as a rollup estimate of its children, since an epic
is itself proposed/in-progress until every child is done.

## User stories

Write the **Issues** section as user stories, not only as bare MUST statements. The MUSTs do
not disappear; they become the testable acceptance criteria under each story.

```
As a <role>, I want <goal>, so that <reason>.
```

Delve's roles are its actors, no invented personas:

- **learner**: descends the dungeon, reads lessons, sits examinations.
- **pack author**: writes a pack in Markdown, in both locales.
- **maintainer**: works on the engine and the tooling (the role for internal changes like the
  issues index or the screen self-check).

The keeper and the pet are in-world characters, not story roles; a story about them is still told
from the learner's or the author's point of view (*As a learner, I want the keeper to ..., so that
...*). Keep the *so that* honest: it is the value, and it is what the Definition of Ready checks is
present. A story with no defensible *so that* is usually a task, not an issue.

## Acceptance criteria

Under each story, give one or more criteria in Given / When / Then form. These are the story's
tests written in prose; each should map to a headless test (rule 2: the whole run is drivable as
`session.apply(Command) -> Frame`, no curses in the loop, so every criterion is checkable without a
terminal).

```
Given <starting state>,
when <the learner or author does X>,
then <the observable, testable outcome>.
```

Keep them observable. *Then the coins land on a walkable interior tile of the keeper's room* is
checkable; *then it feels fairer* is not. Prefer Delve's own vocabulary (pack, chapter, room, sit,
REPELLED), never "level".

## Definition of Ready

An issue is ready to build when all of these hold. Check them before moving `status:` to
`in-progress`.

- [ ] **It has been explicitly accepted.** A proposed issue is shown to a peer (in this solo,
      no-remote project, the human maintainer) and the question "do you accept this issue?" is
      asked outright; implementation does not start on a silent absence of objection. Acceptance
      is recorded on the issue itself, `accepted_by:` and `accepted_at:` in the front matter, at
      the same time `status:` moves to `in-progress`, never before the front matter is filled and
      never after code has already been written. `./tools.sh issues --check` enforces this the
      same way it already enforces `effort:` on a proposed/in-progress issue: `accepted_by:` is
      required from `in-progress` onward, and cannot be set without `accepted_at:`.
- [ ] Each story names a **role, a goal, and a reason** (`As a ... I want ... so that ...`).
- [ ] Acceptance criteria are written **Given / When / Then** and are **testable headlessly**
      (no criterion needs a real terminal to check).
- [ ] The **rule-1 layers** it touches are named in `area:`, and the change **does not require
      breaking the five rules** (if it seems to, stop and say so, per CLAUDE.md).
- [ ] **Locale impact is stated**: does it touch the `en`+`nl` pack trees, the `delve/strings`
      catalogue, or a `[format]` table? A locale is complete or absent; there is no per-room
      fallback.
- [ ] **Screen and tutorial impact is noted**: if it changes what a screen looks like, run
      `./tools.sh screenshot <scenario>` for the affected scenarios, note anything notable in the
      issue, and remember the `delve/tutorial/` coupling (the tutorial hard-codes the interface).
- [ ] **Dependencies and related issues are linked** (`related:` / `supersedes:`).
- [ ] It is **sized to one release**. If it is larger, it is written as an **epic** with the work
      split into child stories (see below), not left as one oversized file.

## Definition of Done

An issue is done when all of these hold. Only then set `status: implemented`, move the file
into `archive/`, and fill `commits:`.

- [ ] **Every acceptance criterion is met and covered by a test** (a named pytest, driven through
      the headless harness).
- [ ] **`./run-tests.sh` is green**: `pytest`, `ruff`, `tools/issues.py --check`,
      and `delve validate` on the shipped packs.
- [ ] **Both locales are updated where touched**: the `en`/`nl` trees still diff clean, strings
      exist in both `.toml` files, and formatting stays in the `[format]` table (never
      `locale.setlocale`, never `strftime('%B')`).
- [ ] **No em-dash** anywhere in the change (repo-wide rule).
- [ ] **The five rules hold**: the `engine` import boundary and the `ui -> session` boundary,
      sealed doors (no path validation), passing is final (`room_results` write-once), REPELLED is
      charged per sitting, content stays out of front matter.
- [ ] **CHANGELOG updated**, and if it ships a release, the version is bumped in **both**
      `delve/__init__.py` and `pyproject.toml`.
- [ ] **The issue is archived**: moved to `archive/`, `commits:` filled, and the index
      regenerated with `./tools.sh issues`.
- [ ] **Peer review is recorded in the issue.** Every review that happened before landing is
      written into the issue's own "Peer review" section (`TEMPLATE.md`), one line per reviewer,
      appended not overwritten: at minimum a reviewing agent's pass (Claude Code or another
      review agent) and the maintainer's own sign-off, each with the reviewer, the date, the
      verdict, and a one-line pointer to any findings (fixed inline, or spun out as a follow-up
      issue rather than silently dropped). This is the track record a "commit and close this out?"
      answer of yes is actually based on, not a separate courtesy step; do this before, not after,
      asking the question below.
- [ ] **It has been explicitly accepted to land.** The Definition of Ready's acceptance gate has a
      twin here: once the change is implemented, tested, and peer-reviewed (by the human
      maintainer, or a review agent whose findings the maintainer has seen), it is shown to the
      maintainer and the question "commit and close this out?" is asked outright. An agent
      (Claude Code, Cursor, or any other) never commits, merges, or archives an issue's branch on
      a silent absence of objection, no matter how green `run-tests.sh` is or how clean a review
      came back; auto-committing incidental intermediate steps *within* ongoing work is fine, this
      gate is specifically the boundary where a story's branch is about to land.
- [ ] **Committed**, with the `DELVE-NNNN:` prefix on the message so `git log --grep` reconstructs
      the arc, on the issue's own branch (`bug/DELVE-NNNN` / `feature/DELVE-NNNN` /
      `story/DELVE-NNNN` / `epic/DELVE-NNNN`, per AGENTS.md).
- [ ] **Merged**: `git checkout main && git merge --no-ff <branch>`, then the branch is deleted.
      No squash, no rebase, so `git log --grep` still finds the arc's individual commits.

For an **epic**, the Definition of Done is simply that **every child story is done** (each archived
with its own commits). An epic carries no code of its own; it is a roll-up.

## Breaking up an issue

Stories can and should be split. Two shapes:

1. **Plan an epic, then carve stories.** Write the epic file first (the roll-up list), then create
   one `DELVE-NNNN` per feature or story, each linking back with `related: [DELVE-<epic>]` and each
   with its own Definition of Ready and Done. Build and archive them independently; the epic closes
   when the last child does.
2. **Split a file that grew too big.** If a single proposed issue turns out to be an epic in
   disguise, keep its id as the epic (or mark it `superseded` and let a new epic replace it), then
   move each chunk into a fresh `DELVE-NNNN` with a new id. **Ids never move and slugs never change**,
   so a split always mints new ids and cross-links rather than renumbering. Precedent: the companion
   pet was carved out of the stakes work into DELVE-0011, linked from DELVE-0004.

Get the next free id from `./tools.sh issues --check`, which prints it. Prefer splitting early:
a story you can hold in your head is one you can write a Given/When/Then for, and one whose
Definition of Done is a short list rather than a negotiation.

## A short template

```markdown
<!-- front matter carries type: story and epic: DELVE-0010; the body starts at the title -->

## Summary
One paragraph: what changes and why, in plain language.

## Motivation / problem
The need this addresses.

## Stories
### As a learner, I want the reward coins scattered, so that a room does not give away its shape.
- Given a scored room the learner has just passed,
  when the keeper pays the reward,
  then the coins land on a random walkable interior tile of that room.
- Given the same run rebuilt from its `(seed, size, pack)`,
  when the reward is paid again,
  then the coins land on the identical tile (regenerable tile-for-tile).

## Non-goals
What is explicitly out of scope.

## Design notes / links
Pointers into docs/, not a re-derivation.

## Acceptance / verification
The named tests and the `./run-tests.sh` steps that judge "done".
```

This is the existing six-section body (README.md) with **Issues** rewritten as **Stories**
plus Given/When/Then. An issue that does not warrant stories can keep the plain numbered MUST
form; the two styles coexist in the same tree.
