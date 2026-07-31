---
id: DELVE-0026
title: Dependency vulnerability audit in the test gate
status: implemented
area: [tools]
type: story
epic: DELVE-0024
milestone:
version: 1.9.1
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: [96e1b15, 86b1e1d]
related: [DELVE-0025, DELVE-0027]
supersedes: []
docs: [docs/SECURITY.md]
changelog: "1.9.1"
---

# Dependency vulnerability audit in the test gate

## Summary

Add a `pip-audit` step to `./run-tests.sh` that fails when any package installed in the project
venv (runtime dependencies and the `[dev]` extra) has a known vulnerability in the Python Packaging
Advisory Database. Document how a maintainer bumps or pins out of a finding, and how the step
behaves when advisory data cannot be fetched. Delve's dependency tree is tiny on purpose; this story
keeps it that way under an automatic check rather than by hope.

## Motivation / problem

Runtime depends only on `windows-curses` on Win32; `[dev]` pulls `pytest` and `ruff` (and, after
this story, `pip-audit` itself). That surface is small, but it is not zero, and nothing currently
asks whether a installed version is known-vulnerable. Hand-checking PyPI advisories does not scale
even for three packages, and a future bump can reintroduce a bad pin without a tripwire. `pip-audit`
is the PyPA tool for this job; wiring it into the same gate as pytest/ruff makes "dependencies are
not known-bad" part of Definition of Done.

## Stories

### As a maintainer, I want the test gate to fail on known-vulnerable packages, so that a bad pin cannot sit unnoticed.

- Given the project venv has the `[dev]` extra installed (including `pip-audit`),
  when `./run-tests.sh` runs its dependency-audit step,
  then it audits the environment that the gate itself uses and exits non-zero if any finding is
  reported (unless explicitly and narrowly ignored per the policy in `docs/SECURITY.md`).
- Given a package with a published advisory that applies to the installed version,
  when the audit step runs,
  then the step fails and the output names the package and the advisory id, so a maintainer knows
  what to bump.

### As a maintainer, I want a clear fix path when the audit fails, so that "update for security" is routine rather than archaeology.

- Given the audit fails on a `[dev]` or runtime package,
  when a maintainer addresses it,
  then the fix is to bump the version constraint in `pyproject.toml` (and refresh the venv), not to
  delete the audit step or blanket-ignore all advisories.
- Given an advisory that does not apply (wrong platform, unreachable code path, or a disputed
  false positive),
  when it is ignored,
  then the ignore is narrow (package + advisory id), recorded in config or SECURITY.md with a
  reason, and reviewed when the package is next bumped.

### As a maintainer, I want the audit's network needs to be honest, so that a failed fetch is not mistaken for a clean bill of health.

- Given advisory data cannot be fetched (offline, blocked network),
  when the audit step runs,
  then it does **not** report success as if the tree were clean: it fails with an actionable
  message, or skips only under an explicit, documented opt-out that still prints that the audit
  did not run (never a silent pass).
- Given normal networked development,
  when `./run-tests.sh` runs,
  then the audit step runs by default with no extra flags required.

## Non-goals

- SAST / ruff `S` rules; that is DELVE-0025.
- Writing the full SECURITY.md essay; that is DELVE-0027 (this story supplies the audit-specific
  behaviour that essay must describe).
- Renovate/Dependabot auto-PRs, lock-file policy beyond what the project already uses, or a second
  packaging tool.
- Auditing the NetHack reference clone or anything gitignored.
- Claiming the audit covers non-Python supply chain (OS packages, the Ollama binary the grader
  talks to). Those stay out of this gate; SECURITY.md may mention them as out-of-band.

## Design notes / links

Add `pip-audit` to `[project.optional-dependencies] dev` in `pyproject.toml`, install via the same
`pip install -e '.[dev]'` path `run-tests.sh` already assumes. New step sketch:

```bash
step "pip-audit"  "$py" -m pip_audit --progress-spinner off
```

Exact flags (whether to pass `--strict`, how to point at a requirements export, whether to use
`pip-audit`'s ignore file) are implementation choices; the acceptance criteria above bind the
behaviour. Prefer auditing the **installed** environment over a frozen lock the repo does not
currently keep; if the project later adds a lock file, point the audit at that and update
SECURITY.md.

Network: unlike ruff, `pip-audit` needs advisory data. That is the one gate step that is not
fully offline. Document it next to the step in `run-tests.sh` comments and in SECURITY.md. Do not
weaken the "run every step, report all failures" pattern; a fetch failure is a failed step.

Runtime `windows-curses` only installs on Win32; on macOS/Linux the audit still covers `[dev]` and
whatever else is installed. On Windows, the same step should see `windows-curses` too. No change to
the five rules or to shipped package metadata beyond the `[dev]` extra.

## Acceptance / verification

- `pip-audit` is a `[dev]` dependency; a fresh `pip install -e '.[dev]'` provides it.
- `./run-tests.sh` includes a `pip-audit` (or equivalently named) step that fails on known
  vulnerabilities in the audited environment.
- Offline / fetch-failure behaviour matches the story (no silent pass); documented in
  `docs/SECURITY.md`.
- Current pins are clean under the audit, or carry narrow documented ignores only.
- `./run-tests.sh` remains green on a normal networked maintainer machine with the other existing
  steps unchanged in spirit.
