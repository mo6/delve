---
id: DELVE-0019
title: Pack variables - translatable tokens that replace placeholders
status: proposed
area: [content, session, delve, docs]
type: epic
effort: high
milestone:
version:
version_span:
related: [DELVE-0008]
supersedes: []
docs: [docs/AUTHORING.md, docs/PLAN.md]
created: 2026-07-25
updated: 2026-07-25
commits: []
changelog:
---

# Pack variables: translatable tokens that replace placeholders

## Summary

Let a pack carry named variables, `{{tokens}}`, that the engine substitutes into its text, so the
hand-marked placeholders a pack ships with (an organisation name, a security contact, a help
channel, the data-classification tiers) become one filled-in value instead of a phrase repeated and
re-flagged in every file and every locale. The pack ships a per-locale **template** declaring its
tokens with placeholder values; a maintainer copies it to an instance-specific `variables.md` and
fills in their deployment's real values, which stay out of the shared pack. A variable is declared
per locale, so it is translatable; its value can also be set globally across packs without editing
lesson prose; and validating a pack fails if it references a variable that is not available. This
resolves the long-standing open question (CLAUDE.md, "Open questions": *frontmatter variables the
engine substitutes, or fork-per-org?*) in favour of substitution, which is what keeps the two locales
in step.

## Motivation / problem

The pilot pack ships deliberate placeholders (`security@example.com`, `#security-help`, the
classification tiers) and marks each line with the word "placeholder" so `schema.py` can warn on it.
`./run-tests.sh` currently prints six such warnings, three lines in `en` mirrored by three in `nl`:

```
packs/security-onboarding/en/03-the-archive/01-classification.md:25: warning: marks a placeholder ...
packs/security-onboarding/en/03-the-archive/03-devices.md:116: warning: ...
packs/security-onboarding/en/04-the-watchpost/03-reporting.md:59: warning: ...
packs/security-onboarding/nl/03-the-archive/01-classification.md:24: warning: ...
packs/security-onboarding/nl/03-the-archive/03-devices.md:114: warning: ...
packs/security-onboarding/nl/04-the-watchpost/03-reporting.md:56: warning: ...
```

That is the whole problem in miniature: the same real-world value is written out in prose in six
places, must be replaced by hand in six places before a real run, must be kept identical across two
locales, and the only safety net is an advisory per-line warning that a reader can ignore. There is
no way to say "this org is Acme" once. A variable system says it once, per locale, and lets a
deployment override it globally, while validation makes an unfilled or unknown variable a real gate
rather than a warning that scrolls past.

## Child stories

An epic carries no code of its own; it is done when its children are (AGILE.md). The children:

- **[[DELVE-0020]]** - *Declare and substitute translatable pack variables.* The core mechanic: a
  per-locale, shipped `variables.template.md` declaring each `{{token}}` with a placeholder value,
  copied to an instance-specific (gitignored) `variables.md` a maintainer fills in, plus
  engine-provided built-in tokens (the learner's name), substituted into all displayed pack text.
  Includes migrating the pilot's six placeholders to variables in both locales.
- **[[DELVE-0021]]** - *Validate that every referenced variable is available.* The validation this
  request explicitly asks for: `delve validate` errors when a pack references a token that is neither
  declared nor a known built-in, requires the two locales to declare the same token set, and turns
  the old per-line placeholder warning into a per-variable "still at its placeholder default"
  warning.
- **[[DELVE-0022]]** - *Set variable values globally for a deployment.* Defining variables "globally":
  a deployment-level override (a config file and/or `--var key=value`) supplies real values on top of
  the pack's declared defaults, so an org sets its name once without forking the pack.
- **[[DELVE-0023]]** - *Unify the scroll's placeholders into `{{ }}`.* Fold the award scroll's legacy
  single-brace `{name}/{score}/{date}/{pack}` into the same token grammar, built-in set, and
  validation path, so the whole pack, scroll included, speaks one variable language.

## Suggested variables

Drawn from the pilot's actual placeholders and typical onboarding content; the names are a proposed
convention, not a closed list (a pack declares whatever it uses). Author-declared unless marked
built-in:

| Token | Replaces / means | Notes |
|---|---|---|
| `{{organisation}}` | the org's name (Acme Corporation) | usually locale-invariant |
| `{{team}}` | the security team's name | |
| `{{security_email}}` | `security@example.com` in `04-the-watchpost/03-reporting.md` | |
| `{{help_channel}}` | `#security-help` in `03-devices.md` and `03-reporting.md` | |
| `{{service_desk}}` | the service-desk contact or number | |
| `{{tier_public}}` `{{tier_internal}}` `{{tier_confidential}}` `{{tier_restricted}}` | the four data-classification tier names in `03-the-archive/01-classification.md` | translatable; an org may rename them |
| `{{player}}` | the learner's own name | **built-in**, from identity, not declared |
| `{{pack_title}}` | the pack's title | **built-in**, optional |

## Non-goals

- (No longer a non-goal.) Unifying the scroll's single-brace built-ins (`{name}`, `{score}`,
  `{date}`, `{pack}` in `progress/scrolls.py`) into `{{ }}` is now scheduled as its own child,
  **[[DELVE-0023]]**.
- Conditional or computed text (if/else, pluralisation, arithmetic on a value). A variable is a
  literal string substitution, nothing more.
- Per-room or per-chapter variable scopes. Variables are pack-global.
- Substituting into map glyphs or the status line. Variables are for panel/scroll prose only.

## Design notes / links

Rule 5 is the sharp constraint: a variable's *value* (a company name, a contact) is content, so it
must live in a document body, not in `pack.md` frontmatter. That is why DELVE-0020 puts declarations in
a `variables.template.md` body rather than as frontmatter keys. The template-plus-instance split
(`.env.example` to `.env`) is what keeps a deployment's real values out of the shared pack: the
template ships and is the authority on which tokens exist, while the filled `variables.md` is
instance-specific and gitignored. Rule 1 splits the work cleanly: `content/`
owns the token grammar, the per-locale declaration file, and the reference validation; the actual
fill of a built-in like `{{player}}` uses run state and so is the session's job (the same shape as
`render_scroll`, a pure helper in `progress/`, called by the session). Locale rules bind hard: a
variable is declared per locale so it translates, `variables.md` must exist and declare the same
tokens in both `en` and `nl` (the tree-diff and complete-or-absent rules), and no `[format]` change
is involved (a variable is a string, not a number or date). Design essays: `docs/AUTHORING.md` (the
authoring surface this extends) and `docs/PLAN.md` section 8 (locales) and the placeholder open
question. Related: DELVE-0008 (localisation) established the per-locale tree this builds on.

## Acceptance / verification

This epic is done when every child story is implemented, archived with its own commits, and
`./run-tests.sh` is green with the pilot's six placeholder warnings gone (replaced by declared
variables). It ships no code of its own; track completion by the child list above.
