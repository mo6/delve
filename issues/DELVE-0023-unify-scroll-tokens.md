---
id: DELVE-0023
title: Unify the scroll's placeholders into the {{ }} variable mechanism
status: proposed
area: [content, session, progress]
type: story
epic: DELVE-0019
effort: medium
milestone:
version:
version_span:
related: [DELVE-0020, DELVE-0021]
supersedes: []
docs: [docs/AUTHORING.md]
created: 2026-07-25
updated: 2026-07-25
commits: []
changelog:
---

# Unify the scroll's placeholders into the {{ }} variable mechanism

## Summary

The award scroll fills four placeholders in its own single-brace syntax, `{name}`, `{score}`,
`{date}`, `{pack}` (`progress/scrolls.py:render_scroll`), a mechanism that predates and now sits
beside the `{{token}}` variables of DELVE-0020. Fold them together: make the scroll use `{{ }}` like
every other pack surface, so there is one token grammar, one built-in set, and one validation path.
The learner's name becomes the same `{{player}}` built-in used everywhere; the scroll's score, date,
and pack title become built-in tokens (`{{score}}`, `{{date}}`, `{{pack_title}}`) that the engine
formats from run state through the locale `[format]` table exactly as now. As a side benefit, an
author-declared variable (`{{organisation}}`) becomes usable in the scroll too, which the old
four-field whitelist forbade.

## Motivation / problem

Two token syntaxes in one pack is a trap: an author must remember that a lesson uses `{{player}}` but
the scroll uses `{name}`, and the two are validated by different code (`schema.py:_check_scroll`
warns on an unknown single-brace field; DELVE-0021 errors on an unknown `{{token}}`). DELVE-0019 called
this unification a possible follow-up; this story schedules it, so the whole pack, scroll included,
speaks one variable language. It also removes an inconsistency the old scroll whitelist created: the
scroll could not use any pack variable, only its four built-ins, even though a real award ("Issued by
{{organisation}}") plainly wants one.

## Stories

### As a pack author, I want the scroll to use the same tokens as the rest of my pack, so that I learn one syntax.

- Given a `scroll.md` that writes `{{player}}`, `{{score}}`, `{{date}}`, and `{{pack_title}}`,
  when the award is shown,
  then each is filled: `{{player}}` from identity, `{{score}}` and `{{date}}` formatted through the
  locale `[format]` table (the same numbers and month names as today), and `{{pack_title}}` from the
  pack title.
- Given a `scroll.md` that also uses an author-declared or overridden variable (`{{organisation}}`),
  when the award is shown,
  then it is filled from the same resolved value map every other surface uses (DELVE-0020, DELVE-0022).
- Given the same award context (learner, score, date, pack, locale),
  when the scroll is rendered twice,
  then the output is byte-identical (plain replacement, no RNG), matching the pre-unification text
  character for character apart from the token syntax.

### As a pack author, I want the scroll's whole-pack tokens to make sense only where they have a value, so that I do not put a score in a lesson.

- Given `{{score}}`, `{{date}}`, or `{{pack_title}}` used outside `scroll.md` (in a lesson, question,
  or intro),
  when the pack is validated,
  then it is reported: these three are scroll-scoped built-ins with no value mid-run. (`{{player}}`
  stays valid everywhere, since identity is always known.)
- Given `{{player}}` in the scroll,
  when validated,
  then it is accepted, the one name token shared by the scroll and the rest of the pack.

### As a maintainer, I want one validation path for tokens, so that an unknown token fails the same way everywhere.

- Given `scroll.md` references an unknown `{{token}}` (neither a built-in nor an author-declared
  variable),
  when the pack is validated,
  then it is an **error** via DELVE-0021's shared check, replacing the old scroll-only *warning* on an
  unknown single-brace field (a deliberate tightening: a broken scroll token now blocks).
- Given a leftover single-brace `{name}`, `{score}`, `{date}`, or `{pack}` in a scroll (an
  un-migrated file),
  when validated,
  then it emits a migration warning (it is no longer special and would render literally), so the
  switch to `{{ }}` cannot silently ship a stale placeholder.

## Non-goals

- Re-rendering an already-awarded scroll later in a different locale (open question 3 in CLAUDE.md).
  Unifying the *syntax* does not change *when* the scroll is filled; that remains claim-time in the
  run's locale.
- Adding new scroll built-ins beyond the existing four (score, date, pack title, name). This story
  changes their syntax and validation, not the set.
- Keeping single-brace `{name}` working as a permanent alias. It is migrated away, with only the
  transitional warning above to catch stragglers.

## Design notes / links

`render_scroll` today does `str.replace` for `{name}/{score}/{date}/{pack}`, with `{score}` and
`{date}` pre-formatted by `format_score`/`format_date` from the `[format]` table. Unify by having the
session assemble the scroll's value map, the built-ins (`{{player}}` = identity, `{{score}}` =
`format_score(pack_score, fmt)`, `{{date}}` = `format_date(now, fmt)`, `{{pack_title}}` = pack title)
merged with the pack's resolved variables (DELVE-0020/0022), and pass it to the same pure
`substitute(text, values)` helper the other surfaces use (`_scroll_overlay` in `session/run.py`
already computes name/score/date/pack at line ~1335). `progress/scrolls.py` keeps `format_score` and
`format_date` (the formatting is still its job and still `[format]`-driven, never `strftime`), but the
token replacement moves to the shared helper, so `render_scroll` becomes a thin adapter or is retired.
This keeps rule 1 clean: formatting in `progress/`, the pure string fill in the shared helper, the map
assembled by the session.

Validation: replace `schema.py:_check_scroll`'s single-brace scan with the `{{ }}` scan DELVE-0021
introduces, treating `{{player}}` plus author-declared tokens as valid on any surface and
`{{score}}/{{date}}/{{pack_title}}` as valid only in `scroll.md`. `SCROLL_FIELDS` becomes the
scroll-scoped built-in set. Add the transitional single-brace-leftover warning. Because the scroll
now flows through DELVE-0021, an unknown token there is an error rather than the current warning; call
that out in `docs/AUTHORING.md`.

Content and test impact: migrate the pilot's `scroll.md` in both locales (`{name}` to `{{player}}`,
`{score}` to `{{score}}`, `{date}` to `{{date}}`, `{pack}` to `{{pack_title}}`); the prose is
otherwise untouched (keep `en` as the verbatim fixture it is). `tests/test_validate.py` covers the
scroll placeholder check and must move to the new grammar. No `delve/strings` or `[format]` change
(the formatting logic and the locale tables are unchanged; only the surrounding token syntax moves).

## Acceptance / verification

- A scroll test renders an award whose `scroll.md` uses `{{player}}/{{score}}/{{date}}/{{pack_title}}`
  and asserts the filled output equals the pre-unification single-brace render character for
  character (same formatted score and localised date), in both locales.
- A scroll-variable test uses an author-declared `{{organisation}}` in the scroll and asserts it
  fills from the resolved value map.
- A scoping test asserts `{{score}}` in a lesson is a validation error while `{{player}}` in the
  scroll is accepted.
- A validation test asserts an unknown `{{token}}` in the scroll is an error (not a warning) and a
  leftover `{name}` triggers the migration warning.
- The pilot's `en`/`nl` `scroll.md` are migrated; the pack awards its scroll end to end in both
  locales with identical rendered text to before.
- `./run-tests.sh` passes (pytest, ruff, screens, issues-index, `delve validate`).
