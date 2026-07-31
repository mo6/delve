---
id: DELVE-0022
title: Set pack variable values globally for a deployment
status: proposed
area: [content, session, delve]
type: story
epic: DELVE-0019
effort: high
milestone:
version:
version_span:
related: [DELVE-0020]
supersedes: []
docs: [docs/AUTHORING.md, docs/PLAN.md]
created: 2026-07-25
updated: 2026-07-25
commits: []
changelog:
---

# Set pack variable values globally for a deployment

## Summary

Let a deployment supply real variable values from *outside any one pack*, so an organisation sets its
name, contact, and channels once and every pack it runs picks them up, without editing even a
per-pack `variables.md`. A global source (a config file and/or repeatable `--var key=value` flags)
sits above the per-pack instance file (DELVE-0020): where the global source names a token it wins, and
where it is silent the pack's own `variables.md`, then its template placeholder, still applies for
that locale, so translation is preserved. This is the cross-pack half of "defined globally" and the
reason the substitution approach beats fork-per-org: the shared pack stays pristine and in-sync
across locales while a deployment sets its common values in one place.

## Motivation / problem

DELVE-0020 lets a pack declare variables with default values, but those defaults ship as placeholders,
and editing them means changing the pack, which then diverges from upstream and from its other locale.
An organisation wants to say "we are Acme, our contact is security@acme.example" once, globally, and
have it applied wherever those tokens appear, in either language. A global override does that and
keeps the pack a shared, updatable artifact.

## Stories

### As a maintainer deploying a pack, I want to set a variable's value globally, so that I do not edit or fork the pack.

- Given a global override sets `organisation = Acme Corporation`,
  when any pack that declares `{{organisation}}` is run,
  then `{{organisation}}` resolves to "Acme Corporation", overriding the pack's declared default.
- Given a token the global override does not mention,
  when it is substituted,
  then it falls back to the pack's instance `variables.md` for the run's locale, and then to the
  template placeholder (so an unset variable still shows its translated placeholder, not blank).
- Given both a config file and a `--var` flag set the same token,
  when they conflict,
  then the more specific source wins by a stated precedence (proposed: `--var` over config file over
  per-pack `variables.md` over template default), and the precedence is documented.

### As a maintainer, I want the global source to be locale-aware where it needs to be, so that values that differ by language still can.

- Given an override value that is the same in every locale (a company name),
  when it is set once,
  then it applies in both `en` and `nl`.
- Given a value that differs by locale (a renamed classification tier),
  when the override provides per-locale values,
  then each locale resolves to its own; a locale the override omits falls back to the pack default for
  that locale.

### As a maintainer, I want overrides validated too, so that a typo in the global source is caught.

- Given a global override sets a token no loaded pack declares or that is a built-in,
  when the pack is validated or run with that override,
  then it is reported (an error on `validate`; at least a warning at run start), so a stray or
  misspelled override does not pass silently.

### As a maintainer, I want overrides to keep runs deterministic, so that a run still regenerates.

- Given a run built with a given override set,
  when its snapshot is resumed,
  then the same values apply and the substituted text is identical (the resolved value map is part of
  the run's inputs, alongside `seed`, `size`, and pack).

## Non-goals

- A UI for editing variables. The override is a config file and/or CLI flags, edited outside the game.
- Secrets management. Variable values are ordinary strings (a name, an email, a channel), not
  credentials; nothing here encrypts or protects them.
- Overriding built-in tokens (`{{player}}`). Built-ins come from run state and are not deployment
  configuration.
- Per-run interactive prompting for values. Out of scope; the override is set ahead of time.

## Design notes / links

Precedence, high to low: built-in tokens (unoverridable) > `--var key=value` (repeatable CLI) >
global config file > per-pack instance `variables.md` (DELVE-0020) > per-pack `variables.template.md`
placeholder, each resolved per locale. The config file should be stdlib-only:
TOML via `tomllib` fits the codebase (the same choice the strings and format tables make), read from
a documented path (proposed: `$XDG_CONFIG_HOME/delve/variables.toml`, with a `[locale]` section for
per-locale values and a top-level table for locale-invariant ones), never process-global state. The
resolved value map is assembled by the session at run start (where identity and locale are already
known, so it sits beside `{{player}}` resolution from DELVE-0020) and threaded into the same
`substitute` helper; the pack stays unmodified on disk. Because the resolved map is a run input, it
must be recorded or reconstructable for a resume so substitution matches (note it near the snapshot's
`seed+size+pack` inputs). Validation of override keys reuses DELVE-0021's declared-plus-built-in token
set. CLI surface lives in `delve/` (argument parsing) and is documented in `docs/AUTHORING.md`
(authoring and deploying) with a pointer from `docs/PLAN.md`'s placeholder open question, which this
story closes. No `delve/strings` change (override values are pack content, not engine UI); a run-start
warning about a stray override key is a validator-style developer message.

## Acceptance / verification

- An override test resolves a pack with a config value and asserts the token shows the override, not
  the pack default; an unset token falls back to the translated pack default.
- A precedence test sets the same token in config and `--var` and asserts `--var` wins, and that a
  built-in cannot be overridden.
- A locale test provides a per-locale override value and asserts each locale resolves correctly, with
  an omitted locale falling back to the pack default.
- A validation test asserts a stray override key (undeclared, non-built-in) is reported on `validate`
  and warned at run start.
- A resume test builds a run with an override set, snapshots and resumes it, and asserts the
  substituted text is identical.
- `./run-tests.sh` passes (pytest, ruff, screens, issues-index, `delve validate`).
