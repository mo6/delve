---
id: DELVE-0024
title: Security scanning for code and dependencies
status: implemented
area: [tools, docs]
type: epic
milestone:
version: 1.9.1
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: [96e1b15, 86b1e1d]
related: []
supersedes: []
docs: [docs/SECURITY.md]
changelog: "1.9.1"
---

# Security scanning for code and dependencies

## Summary

Give Delve a maintainer-facing security gate: static analysis of the Python tree for common
insecure patterns, and a dependency advisory check so known-vulnerable packages cannot sit quietly
in the venv. Both checks live beside the existing `./run-tests.sh` steps (pytest, ruff, screens,
issues, validate), so "green" means the same thing for correctness and for a baseline of security
hygiene. A short design essay, `docs/SECURITY.md`, records the attack surface, the tools, severity
rules, and how a finding is fixed or suppressed. This epic is the umbrella; the children are the
concrete gate steps and the documentation.

## Motivation / problem

Delve's runtime surface is deliberately small (stdlib plus a Windows-only `windows-curses`, one
socket seam in `assess/llm.py`, subprocess only in `delve/doctor.py` for setup), but nothing in the
current gate asks "is this pattern unsafe?" or "is a locked dependency known-bad?". Ruff today
enforces style and a few bugbears (`E`, `F`, `I`, `UP`, `B`); it does not run the security rule set.
Dev dependencies (`pytest`, `ruff`) and the Windows wheel are not audited for published advisories.
A maintainer who wants confidence has to invent a private checklist; there is no shared procedure,
no place to record an intentional exception, and no tripwire when a transitive advisory lands. The
project already treats `./run-tests.sh` as the Definition of Done; security belongs there, not as a
one-off manual habit.

## Child stories

An epic carries no code of its own; it is done when its children are (AGILE.md). The children:

- **[[DELVE-0025]]** - *Static analysis in the test gate.* Extend the existing ruff step (or an
  adjacent step) with security rules (`S`, the flake8-bandit set), so insecure patterns fail the
  gate the same way a lint does. Documented, justified suppressions only.
- **[[DELVE-0026]]** - *Dependency vulnerability audit in the test gate.* Add a `pip-audit` step that
  fails on known-vulnerable packages in the installed environment (runtime and `[dev]`), and a
  clear bump-or-pin path when it fires.
- **[[DELVE-0027]]** - *Document the security procedure and finding triage.* Write `docs/SECURITY.md`:
  attack surface, tools, how to run them, severity policy, suppression rules, and the cadence for
  re-checking. Issues stay the *what*; the essay is the *why* and the runbook.

Deferred, not scheduled (recorded so the epic's shape is honest):

- *Secrets scanning (future, no id yet).* Tools like `gitleaks` or `detect-secrets` catch accidental
  credentials in history and working trees. Valuable once packs or deployments start carrying
  instance secrets (see DELVE-0019's gitignored `variables.md`), but out of scope for the first gate:
  Delve currently ships no API keys and the LLM grader talks to a local Ollama. Write a child only
  when there is a real secret surface to protect.
- *Hosted CI (future, no id yet).* The repo is developed without a remote today (CLAUDE.md). When a
  remote and CI exist, re-run the same gate there; do not invent a second, divergent checklist.

## Suggested structure (how to scan)

Keep the procedure thin and aligned with what already works:

| Layer | Tool | Where it runs | What it catches |
|---|---|---|---|
| SAST (code patterns) | ruff rule set `S` (Bandit-compatible) | `./run-tests.sh`, same venv | `eval`, unsafe `subprocess`, weak hashes, asserted True, SQL composition smells, etc. |
| Dependency advisories | `pip-audit` (PyPA) | `./run-tests.sh` step (needs advisory data; see DELVE-0026) | Known CVEs in installed distributions |
| Lint / bugs (existing) | ruff `E`/`F`/`I`/`UP`/`B` | already in the gate | style and common mistakes |
| Pack / schema (existing) | `delve validate` | already in the gate | content policy, not application security |

Why this mix, and not a heavier stack:

- **Extend ruff, do not add Bandit as a second installer.** The gate already has ruff; the `S` codes
  are the same Bandit checks. One tool, one config in `pyproject.toml`, one failure format.
- **`pip-audit` over `safety`.** PyPA-maintained, talks to the Python Packaging Advisory Database,
  fits a stdlib-leaning project that still wants an official advisory source.
- **Skip Semgrep / CodeQL for now.** The codebase is small, Python-only, and almost dependency-free;
  custom rule engines earn their keep when there are many repos or many languages. Revisit if the
  attack surface grows (a served build, a second frontend).
- **One gate, local-first.** Security steps are ordinary `run-tests.sh` steps so Definition of Done
  in AGILE.md stays one command. No parallel "security-only" script that bitrots.

Attack surface to keep in the essay (and to bias which `S` findings matter):

1. `delve/assess/llm.py` - the only core module that opens a socket (local Ollama).
2. `delve/doctor.py` - subprocess for setup/doctor; not on the hot path, but still in scope.
3. `progress/` SQLite - learner data at rest; identity is trust-based (PLAN §10).
4. Pack loading - Markdown from disk; no code execution from packs (keep that invariant).
5. `ui/` curses - no network; render-only.

## Suggested documentation (where the *why* lives)

| Artefact | Role |
|---|---|
| `issues/DELVE-0024`…`0027` | The *what*: testable acceptance criteria, archived when done. |
| `docs/SECURITY.md` (DELVE-0027) | The *why* and the runbook: surface, tools, severity, suppressions, cadence. |
| `CHANGELOG.md` | *When* the gate gained the steps (on release). |
| Inline `# noqa: S###` + comment, or ruff `per-file-ignores` | The *how* of an intentional exception; every suppression points at a reason, never a silent blanket. |

Findings lifecycle (to encode in SECURITY.md):

1. Gate fails with a rule id or advisory id.
2. Fix preferred: change the code, or bump/pin the package.
3. If the finding is a false positive or an accepted risk (e.g. intentional `subprocess` in doctor),
   suppress with a one-line justification next to the ignore, and mention it in SECURITY.md if it is
   standing policy rather than a one-off.
4. Critical / high advisories and high-confidence SAST hits fail the gate; informational noise is
   tuned out in config, not left for every maintainer to re-triage.

## Non-goals

- A penetration test, threat model workshop, or formal audit certificate. This is a developer gate.
- Claiming Delve scrolls or identity are authentic/confidential beyond what PLAN §10-11 already
  states (trust-based identity; Phase 2 export is not an audit record).
- Scanning pack *content* for "insecure advice"; that is editorial, owned by STYLE.md and validate.
- Auto-updating dependencies without a human. The audit flags; a maintainer bumps.
- Windows-host verification of the scanners themselves beyond "they run in the same venv gate"; the
  outstanding Windows item in CLAUDE.md stays about curses rendering.

## Design notes / links

Rule 1 is untouched: scanners live in `tools/` / `pyproject.toml` / `run-tests.sh`, never inside
`engine` or `ui`. No new runtime dependency; scanners are `[dev]` only. The stdlib-only line for the
shipped app stays. Related open honesty in PLAN §10-11 (identity and scroll export) should be
cross-linked from SECURITY.md so a reader does not confuse "the gate is green" with "the product is
an audit system". Child stories carry the concrete config and test-gate wiring.

## Acceptance / verification

This epic is done when every child story is implemented, archived with its own commits,
`docs/SECURITY.md` exists and is linked from the children, and `./run-tests.sh` is green with the
new security steps included. It ships no application feature of its own; track completion by the
child list above.
