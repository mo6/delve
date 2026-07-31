---
id: DELVE-0021
title: Validate that every referenced pack variable is available
status: proposed
area: [content]
type: story
epic: DELVE-0019
effort: medium
milestone:
version:
version_span:
related: [DELVE-0020, DELVE-0023]
supersedes: []
docs: [docs/AUTHORING.md]
created: 2026-07-25
updated: 2026-07-25
commits: []
changelog:
---

# Validate that every referenced pack variable is available

## Summary

Make `delve validate` (and therefore `./run-tests.sh`) fail a pack that uses a variable it does not
provide. Every `{{token}}` in a pack's text must be either declared in that locale's
`variables.template.md` or a known engine built-in; a reference to anything else is an **error**, so
a missing or misspelled variable is caught before a run rather than surfacing as raw `{{token}}` on
screen. The template (which ships) is the authority on which tokens exist; the two locales' templates
must declare the same set of tokens. A variable still at its template placeholder, whether because
the instance `variables.md` is missing or leaves it unset, stays a **warning** (the nudge the six
current placeholder warnings give today, moved from the prose line to the variable).

## Motivation / problem

This is the validation the request explicitly asks for: "all pack-defined variables are available
when testing a pack". Once DELVE-0020 makes `{{token}}` mean substitution, an undeclared or mistyped
token would otherwise fill with nothing or print literally, a silent content bug. The engine already
does exactly this check one layer up: `schema.py` errors on an *unknown scroll placeholder* in
`scroll.md`. This story generalises that guarantee to the whole pack, and folds the existing per-line
placeholder marker (`_check_placeholders`, the source of the six warnings) into a per-variable
"still at its default" warning so the safety net gets stronger, not lost.

## Stories

### As a pack author, I want validation to reject an unavailable variable, so that a typo or a missing declaration fails the pack instead of the learner.

- Given a pack whose prose references `{{help_channl}}` (a typo) that no `variables.template.md`
  declares and that is not a built-in,
  when `delve validate` runs,
  then it reports an error naming the file, line, and the unknown token, and the pack does not
  validate clean.
- Given a token that is a known built-in (`{{player}}`),
  when it is referenced without any declaration,
  then it is accepted (built-ins are always available), not flagged as unknown.
- Given every referenced token is declared or built-in,
  when the pack is validated,
  then there is no variable-availability error.

### As a pack author, I want the two locales to declare the same variables, so that one language is never missing a value.

- Given `en/variables.template.md` declares `{{team}}` but `nl/variables.template.md` does not,
  when the pack is validated,
  then it reports an error: the locale token sets differ (the complete-or-absent rule, alongside the
  existing tree-diff).
- Given both locales' templates declare the same token set,
  when validated,
  then there is no mismatch error, even if the values differ (values are meant to differ; the keys
  are not).

### As a maintainer, I want an unfilled variable to stay a visible warning, so that running a pack before filling it in is still flagged.

- Given a variable whose value is still the template placeholder, because the instance `variables.md`
  is absent or leaves that token unset,
  when the pack is validated,
  then it emits a warning naming the variable ("still at its placeholder default; set it in
  variables.md before running for real"), not an error, so the pilot still validates clean the way it
  does today (shipping only the template).
- Given a variable is declared in the template but referenced nowhere in the pack,
  when validated,
  then it emits a warning (a dead variable), never an error.

### As a maintainer, I want the checks to gather rather than stop at the first, so that one run reports every problem.

- Given a pack with several variable faults across several files,
  when `delve validate` runs,
  then every fault is reported in one run as an `Issue` (schema.py's gathering path), not just the
  first, consistent with how pack-policy checks already behave.

## Non-goals

- The substitution mechanism itself (DELVE-0020) and the deployment override (DELVE-0022). This story
  only checks availability and consistency; it does not fill anything.
- Validating the *content* of a value (that `{{security_email}}` looks like an email). A variable is
  an opaque string; only its presence and locale-consistency are checked.
- Unifying the scroll's own `{name}`-style placeholder check (currently a *warning* on an unknown
  single-brace field) into this `{{ }}` path. That is DELVE-0023; this story's shared token scan is
  what DELVE-0023 reuses for the scroll.

## Design notes / links

The natural home is `content/schema.py`, beside `_check_placeholders` (which this story largely
replaces) and the existing scroll-placeholder error at `schema.py:222`. The checks:

1. Parse each locale's `variables.template.md` into a declared token set (DELVE-0020 adds the parse),
   and the instance `variables.md` (when present) into a filled-value set.
2. Scan every text surface (lesson blocks, question prompts/options/explanations, chapter and pack
   intros, scroll) for `{{token}}` references and error on any token neither declared in the template
   nor built-in, with file and line. Reuse the same token regex DELVE-0020's substituter uses, so "what
   is a token" has one definition.
3. Diff the two locales' template token sets and error on a mismatch (extend the tree-diff, which
   already errors when file trees differ). The template is tracked and so is part of the tree;
   `variables.md` is gitignored and is not diffed.
4. Warn on a variable still at its template placeholder (instance file missing or token unset), and
   on a declared-but-unreferenced variable.

Keep the placeholder *default* detectable: either keep the `placeholder`/`plaatshouder` marker inside
the template's example value (so `PLACEHOLDER_MARKER` still matches, now against the value rather than
an arbitrary prose line), or add an explicit "this is a placeholder" flag to a template declaration.
Either way the six pilot warnings become variable-level warnings after DELVE-0020 migrates that prose,
and they still fire in CI, where only the template ships. All messages are validator `Issue`s
(English, developer-facing), so no `delve/strings` change. A missing `variables.template.md` when the
pack references no token is not an error (a pack may use none), the same lenience `scroll.md` gets.
Design essay: `docs/AUTHORING.md` (document the errors and warnings so an author can act on them).

## Acceptance / verification

- A schema test builds a pack referencing an undeclared token and asserts a validation error naming
  the file, line, and token; a second asserts a referenced built-in (`{{player}}`) is accepted.
- A locale-consistency test declares different token sets in `en` and `nl` and asserts the mismatch
  error; matching sets with differing values pass.
- A warning test asserts a still-default variable warns (not errors) and a declared-but-unused
  variable warns, and that a fully-set pack validates with no variable warnings.
- A gathering test asserts several variable faults are all reported in one `validate` run.
- After DELVE-0020's pilot migration, `delve validate packs/security-onboarding` shows no undeclared or
  mismatch errors, and the six former per-line placeholder warnings appear (if still at defaults) as
  variable-level warnings instead.
- `./run-tests.sh` passes (pytest, ruff, screens, issues-index, `delve validate`).
