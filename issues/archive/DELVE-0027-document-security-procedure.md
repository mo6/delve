---
id: DELVE-0027
title: Document the security procedure and finding triage
status: implemented
area: [docs, tools]
type: story
epic: DELVE-0024
milestone:
version: 1.9.1
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: [pre-reset]
related: [DELVE-0025, DELVE-0026]
supersedes: []
docs: [docs/SECURITY.md, docs/PLAN.md]
changelog: "1.9.1"
---

# Document the security procedure and finding triage

## Summary

Write `docs/SECURITY.md` as the design essay and runbook for Delve's security gate: what the attack
surface is, which tools run in `./run-tests.sh`, how a finding is fixed or narrowly suppressed, what
"green" does and does not mean, and how often a maintainer should care beyond the gate. Issues
DELVE-0025 and DELVE-0026 state the testable *what*; this story is the *why* and the shared procedure so
the next maintainer does not reinvent triage.

## Motivation / problem

Without a single essay, the ruff `S` select list, `pip-audit` flags, and any suppressions live only
in config and shell, with no explanation of intent. PLAN.md already records honest limits (trust-based
identity, scroll export that is not an audit record); a security gate that is silent about those
limits invites over-claiming ("we scan, therefore we are secure"). Delve's docs split is deliberate:
`docs/` for design essays, `issues/` for testable *what*, CHANGELOG for *when*. Security needs
the essay slot.

## Stories

### As a maintainer, I want a short security runbook in docs/, so that I know what the gate covers and how to respond when it fails.

- Given `docs/SECURITY.md` exists,
  when a maintainer opens it,
  then it states at least: the in-scope attack surface (LLM socket, doctor subprocess, SQLite
  progress, pack loading, curses UI), the tools in the gate (ruff `S`, `pip-audit`) and how to run
  them via `./run-tests.sh`, the severity / fail policy, and the suppression rules (narrow,
  justified, never a blanket disable).
- Given a gate failure on an `S` rule or a `pip-audit` advisory,
  when the maintainer follows the runbook,
  then the documented first action is to fix (code change or version bump), and only then to
  consider a narrow, commented suppression or ignore with a reason.

### As a maintainer, I want the essay to be honest about what the gate does not prove, so that "All checks passed" is not mistaken for a product security claim.

- Given PLAN.md sections on identity and scroll export,
  when SECURITY.md discusses residual risk,
  then it links those limits (trust-based identity; export confidentiality without authenticity) and
  states that the gate does not make Delve an audit or compliance system.
- Given out-of-band risks (the Ollama binary, the host OS, pack editorial quality),
  when SECURITY.md lists scope,
  then those are named as out of scope for this gate rather than implied covered.

### As a maintainer, I want standing exceptions visible in one place, so that accepted risks do not hide in config only.

- Given DELVE-0025 or DELVE-0026 land suppressions or advisory ignores,
  when SECURITY.md is complete,
  then it summarises those standing exceptions (file or package, rule/advisory id, reason), or points
  at the canonical config location and requires a reason comment there.
- Given a future maintainer adds a new suppression,
  when they follow the runbook,
  then the essay tells them to update that summary (or the reason-comment convention) in the same
  change.

## Non-goals

- Implementing the ruff `S` select or the `pip-audit` step; those are DELVE-0025 and DELVE-0026. This
  story may land before, with, or immediately after them, but its DoD includes reflecting whatever
  config those stories actually shipped.
- A public vulnerability-disclosure policy page, CVE assignment process, or security.txt (optional
  later if Delve is distributed widely; not required for the internal gate).
- Translating SECURITY.md into Dutch; engine/docs essays stay English (pack content and
  `delve/strings` are the localised surfaces).

## Design notes / links

Proposed outline for `docs/SECURITY.md` (match the tone of PLAN.md / OBJECTS.md: short, concrete,
no em-dashes):

1. **Purpose** - developer gate, not a certification.
2. **Attack surface** - the five bullets from DELVE-0024, with file pointers.
3. **Tools in `./run-tests.sh`** - ruff `S` (offline), `pip-audit` (needs advisory data); how to
   run each in isolation if debugging.
4. **Findings lifecycle** - fix, then narrow suppress; where ignores live.
5. **Standing exceptions** - table or list, kept in sync with config.
6. **What green does not mean** - link PLAN §10-11; Ollama/OS/editorial out of scope.
7. **Cadence** - every `./run-tests.sh`; additionally re-read SECURITY.md when adding a socket,
   subprocess, or dependency.

Cross-link from CLAUDE.md only if the essay becomes something every change must remember (like the
five rules); default is a `docs:` link from the issue and a mention under Environment / The
two run scripts once the steps exist. No new issue-index machinery.

Voice: English, no em-dashes, same house style as other `docs/` essays. This is internal
maintainer documentation, not pack content, but the punctuation rule still applies.

## Acceptance / verification

- `docs/SECURITY.md` exists and covers the sections above.
- DELVE-0024 / DELVE-0025 / DELVE-0026 `docs:` front matter resolve to a real file.
- Standing exceptions from the sibling stories are reflected (or the essay explicitly says "none
  yet" at first land and is updated when suppressions appear).
- No change to runtime behaviour required by this story alone; `./run-tests.sh` / `tools/issues.py
  --check` still pass.
- Optional but preferred: a one-line pointer from README.md or CLAUDE.md's "The two run scripts"
  section once DELVE-0025/0026 have added the steps, so discoverability matches screens/issues.
