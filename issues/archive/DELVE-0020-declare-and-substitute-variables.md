---
id: DELVE-0020
title: Declare and substitute translatable pack variables
status: implemented
area: [content, session]
type: story
epic: DELVE-0019
effort: medium
milestone:
version: 1.37.0
version_span:
related: [DELVE-0008, DELVE-0023]
supersedes: []
docs: [docs/AUTHORING.md]
created: 2026-07-25
updated: 2026-08-03
accepted_by: George Moses
accepted_at: 2026-08-03
commits: [a252260, 8fcb531]
changelog: "1.37.0"
---

# Declare and substitute translatable pack variables

## Summary

Give a pack a per-locale variables **template** that declares its named tokens with example
(placeholder) values, and have a maintainer copy that template to an instance-specific
`variables.md` and fill in the real values for their deployment. The engine then replaces every
`{{token}}` in the pack's displayed text with the value for the run's locale, taking the filled
`variables.md` first and falling back to the template's placeholder when a value is not yet set. A
small set of tokens is engine-provided (built-in) rather than declared, chief among them
`{{player}}`, the learner's own name from identity. Because each locale has its own template and its
own filled file, variables are translatable; because the values live in a document body, not
frontmatter, rule 5 is respected; and because `variables.md` holds an organisation's real values, it
is instance-specific and kept out of the shared pack (gitignored), while the template is what ships.

## Motivation / problem

Today the same real-world value is written out in prose in several files and both locales, and there
is no way to state it once (DELVE-0019). The template-plus-instance split fixes that the way
`.env.example` does for configuration: the pack author ships a template that documents every token
and shows a safe placeholder value; the maintainer deploying the pack fills a `variables.md` with
their organisation's real values, without touching lesson prose or forking the pack; and the real
values, being specific to that deployment, never enter the shared repository. The learner's name,
which the scroll can already show via `{name}`, becomes usable in lesson and question prose too,
through the built-in `{{player}}`.

## Stories

### As a maintainer deploying a pack, I want a template of its variables to copy and fill in, so that I know exactly what to provide and the pack stays unforked.

- Given the pack ships `variables.template.md` in each locale root, declaring every token the pack
  uses with an example/placeholder value,
  when a maintainer deploys the pack,
  then they copy the template to `variables.md` in the same locale root and fill in real values,
  editing no lesson prose and no template.
- Given `variables.md` holds an organisation's real, instance-specific values,
  when the pack repository is committed,
  then `variables.md` is gitignored and only `variables.template.md` is shipped, so real values never
  enter the shared pack.
- Given a token the filled `variables.md` omits, or no `variables.md` at all,
  when that token is substituted,
  then it falls back to the template's placeholder value for the run's locale (which DELVE-0021 still
  flags as unfilled), rather than rendering blank or raw.

### As a pack author, I want to declare a variable and use it as a token in my prose, so that I state a value once instead of repeating it.

- Given `variables.template.md` declares `` `{{security_email}}` `` and the deployment's
  `variables.md` sets its value,
  when a lesson, question, option, explanation, chapter intro, pack intro, or scroll contains
  `{{security_email}}`,
  then the shown text has that token replaced by the deployment's value.
- Given a token appears more than once across the pack,
  when the pack is shown,
  then every occurrence is replaced, in every one of those text surfaces.
- Given text that contains no token,
  when it is shown,
  then it is unchanged (substitution is a no-op on ordinary prose, including a literal single brace
  in a code span, which is not a token).

### As a pack author, I want variables to be translatable, so that a Dutch learner sees Dutch values.

- Given `en` and `nl` each carry their own template and filled `variables.md`, each declaring
  `{{team}}` with a locale-appropriate value,
  when the pack is run in each locale,
  then `{{team}}` resolves to that locale's value.
- Given the run's locale,
  when a token is substituted,
  then only that locale's files are consulted (no cross-locale fallback; a locale is complete or
  absent, per CLAUDE.md).

### As a learner, I want a keeper to use my name, so that the training addresses me.

- Given a pack uses the built-in `{{player}}`,
  when the text is shown to a learner who identified as "Robin",
  then `{{player}}` is replaced by "Robin".
- Given `{{player}}`,
  when it is resolved,
  then it comes from the run's identity, not from any variables file, and an author does not (and
  cannot) declare or shadow it; built-in tokens are reserved.

### As a maintainer, I want substitution deterministic and layer-clean, so that a run regenerates and the rules hold.

- Given the same run with the same identity and the same filled values,
  when text is substituted,
  then the result is identical every time (plain string replacement, no RNG, no `str.format` so a
  stray brace in prose is left untouched, mirroring `render_scroll`).
- Given the implementation,
  when a built-in like `{{player}}` is filled,
  then the fill uses run state and lives on the session side, while `content/` owns the token grammar,
  the template, and the filled declarations; a pure substitution helper does the string work (rule
  1). `ui` gains nothing (it paints the already-filled `Frame` text).

## Non-goals

- Validation of unknown or unfilled tokens, and enforcing that the two locales declare the same set.
  That is DELVE-0021; this story is the mechanism and may assume templates are well-formed.
- The deployment-*global* override across packs (a config file / `--var`). That is DELVE-0022, a layer
  above this per-pack file.
- Migrating the scroll's existing `{name}`-style single-brace built-ins to `{{ }}`. That unification
  is its own child, DELVE-0023; this story leaves the scroll's syntax untouched.
- Conditional or computed values; a token is a literal string.

## Design notes / links

Proposed files, both in each locale root beside `pack.md`, values in the body so rule 5 holds, one
bullet per variable:

```markdown
<!-- variables.template.md (shipped) -->
# Variables

- `{{organisation}}`: Placeholder. Your organisation's name.
- `{{security_email}}`: security@example.com
- `{{help_channel}}`: #security-help
```

The maintainer copies this to `variables.md` (gitignored) and replaces each value. The bullet form
parses with the existing markup layer and stays readable and greppable; the exact micro-syntax is an
implementation choice, but keep the token in backticks and the value out of frontmatter. The template
is the authority on *which* tokens exist (what DELVE-0021 validates against); `variables.md` supplies
their real values. Add the parsed declarations to the `Pack` (a `variables: dict[str, str]` resolved
as filled-value-or-template-default per token) filled by `load_pack`.

A `.gitignore` entry (`packs/*/*/variables.md`, or a top-level `variables.md` ignore) keeps instance
values out of the repo; only `variables.template.md` is tracked. Optionally, `delve setup` (the
existing bootstrap in `delve/doctor.py`) could scaffold `variables.md` from the template so a
maintainer starts from a copy rather than by hand; a convenience, not required by this story.

Substitution layer: keep the raw templated text in the parsed content and fill at the
content-to-view boundary in the session, the same shape as `session/flavour.py` (which augments a
prompt at view-build) and `render_scroll` (a pure fill called by the session). A single pure helper,
`substitute(text, values)`, does plain `str.replace` per token; the session builds the value map once
per run as `pack.variables` merged with the built-ins (`{{player}}` from identity, optionally
`{{pack_title}}`), and applies it in the overlay builders (`_lesson_overlay`, `_question_overlay`,
the intro/scroll surfaces). Filling at view-build (rather than rewriting the frozen content objects)
keeps `Pack` locale-pure and lets `{{player}}` resolve from live identity; note the frozen-dataclass
reason in the code.

Relationship to the scroll: `progress/scrolls.py:render_scroll` already fills `{name}/{score}/{date}/
{pack}` with single braces; this story does not change that. DELVE-0023 unifies those into `{{ }}` and
reuses this story's `substitute` helper and built-in set, so build this helper with that reuse in
mind (the scroll's `{{score}}`/`{{date}}` will need the formatted-built-in path).

Locale and content impact: `variables.template.md` becomes part of each locale tree and must be
included in the tree-diff (DELVE-0021 enforces matching token sets across locales); `variables.md`,
being gitignored, is not part of the tree-diff. No `delve/strings` change (these are pack values, not
engine UI strings) and no `[format]` change. Migrating the pilot moves real prose, so per CLAUDE.md
"Editing content that already exists", do it by hand, commit first, and keep `en`/`nl` in step.
Design essay: `docs/AUTHORING.md` (document the template/`variables.md` split, the format, and the
built-in list).

## Acceptance / verification

- A template test builds a pack with `variables.template.md` and a filled `variables.md`, whose
  lesson, an option, an explanation, and the intro each contain a declared token; running it
  headlessly asserts every surface shows the filled value, and a token-free text is unchanged
  (including a literal brace in a code span).
- A fallback test omits a token from `variables.md` (or omits the file) and asserts that token
  resolves to the template's placeholder rather than blank or raw.
- A locale test sets `{{team}}` differently in `en` and `nl` and asserts each run resolves to its own
  locale's value with no cross-locale fallback.
- A built-in test identifies as a given name and asserts `{{player}}` resolves to it from identity,
  and that a template/`variables.md` attempting to declare `{{player}}` does not override the
  built-in.
- A determinism test asserts repeated substitution is byte-identical and a stray single brace
  survives.
- The pilot pack's six placeholders (three `en` lines mirrored in `nl`:
  `03-the-archive/01-classification.md`, `03-the-archive/03-devices.md`,
  `04-the-watchpost/03-reporting.md`) are rewritten to use declared tokens in both locales; each
  locale ships a `variables.template.md` carrying the current placeholder text as the example value;
  `variables.md` is gitignored; and the pack still plays end to end in both languages using the
  template defaults (with the unfilled warnings from DELVE-0021).
- `./run-tests.sh` passes (pytest, ruff, screens, issues-index, `delve validate`), with `en`/`nl` trees
  still diffing clean now that each carries a `variables.template.md`.

## Peer review

- Auto (implementing agent), 2026-08-03: `content/variables.py` owns parse/merge/`substitute` (plain `str.replace`, builtins skipped at parse); `Pack.variables` filled by `load_pack`; session applies at view-build in lesson/question/explanation/scroll overlays plus the welcome line, with `{{player}}`/`{{pack_title}}` always winning. `variables.md` gitignored and excluded from locale tree parity; placeholder/emoji checks skip the variables files. Pilot placeholders in both locales moved onto `{{security_email}}`/`{{help_channel}}`/`{{tier_*}}` with shipped `variables.template.md` defaults; classification-stamp look text no longer trips the old placeholder warning. `docs/AUTHORING.md` §2/§11/§15 updated. `tests/test_variables.py` covers filled surfaces, template fallback, locale isolation, builtin shadowing, and determinism; `test_validate` updated for the migration. Left for DELVE-0021 (unknown/unfilled validation, cross-locale token-set equality) and DELVE-0023 (scroll `{name}` unification). `./run-tests.sh` green (701). Ready to land once you say so.
- Claude (peer review), 2026-08-03: verdict accept, two non-blocking notes. (1) `Pack.intro` (the pack-level "dungeon's opening screen" text, distinct from a chapter's own intro) has no reader anywhere in `session`/`ui` today, only `chapters[start_idx].intro` (the chapter's own) feeds the welcome line, so "pack intro" in this issue's stories and in `docs/AUTHORING.md` §15's "chapter or pack intro line" is currently untestable, not a gap this diff introduces; worth a follow-up once something actually renders `Pack.intro`. (2) `Pack.variables: dict[str, str]` is a mutable field on an otherwise all-tuple frozen dataclass (`chapters`/`items`); every current caller copies it (`dict(pack.variables)`) before use so nothing mutates the shared instance today, but a `Mapping` type hint or a comment noting "treat as read-only" would match the rest of the class's immutability convention more explicitly. Verified: token/builtin precedence, locale isolation, stray-brace and determinism behaviour, the pilot's full placeholder migration (4 files x 2 locales, `test_pilot_placeholders_are_gone_after_variables_migration` confirms zero remaining), `variables.md` correctly excluded from locale tree-parity and the placeholder/emoji checks, and MCQ/option text re-wrapping at render time (so a longer real-world substituted value doesn't need its own capacity rule). `./run-tests.sh` green (701, ruff clean, pip-audit ok, `delve validate` clean) on `story/DELVE-0020`. Ready to land.
- George Moses (maintainer), 2026-08-03: peer-reviewed; implementation accepted.
