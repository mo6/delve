---
id: DELVE-0025
title: Static analysis in the test gate
status: implemented
area: [tools]
type: story
epic: DELVE-0024
milestone:
version: 1.9.1
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: [pre-reset]
related: [DELVE-0026, DELVE-0027]
supersedes: []
docs: [docs/SECURITY.md]
changelog: "1.9.1"
---

# Static analysis in the test gate

## Summary

Turn on ruff's security rule set (`S`, the Bandit-compatible checks) as part of the existing ruff
step in `./run-tests.sh`, so insecure Python patterns fail the maintainer gate the same way a lint
failure does. Configure the select list in `pyproject.toml`, clear or justify every hit on the
current tree, and keep suppressions rare, local, and commented. No second SAST binary; the gate
already owns ruff.

## Motivation / problem

Ruff today selects `E`, `F`, `I`, `UP`, `B` only. That catches style and some bug classes, but not
the patterns Bandit was built for: `eval`/`exec`, shell=True subprocess, weak cryptography, asserted
literals, suspicious marks, and similar. Delve's intentional hot spots (`urllib` in `assess/llm.py`,
`subprocess` in `doctor.py`) are exactly the kind of code that wants a permanent rule engine staring
at them, not a one-time review. Extending the existing ruff step keeps one failure channel and one
config file.

## Stories

### As a maintainer, I want the test gate to fail on insecure code patterns, so that a bad change cannot land unnoticed.

- Given ruff's lint `select` includes the security codes (`S`),
  when `./run-tests.sh` runs its ruff step (or an explicitly named adjacent security-ruff step),
  then any `S` diagnostic on the scanned paths fails the gate the same way an `E`/`F` failure does.
- Given the scanned paths,
  when the gate runs,
  then at least `delve/` and `tests/` are included (matching today's ruff invocation); `tools/` is
  included if it is part of the same ruff command or an agreed extension, documented in
  `docs/SECURITY.md`.

### As a maintainer, I want every standing exception justified, so that suppressions do not become a silent hole.

- Given a true positive that is an accepted risk (for example an intentional subprocess in
  `delve/doctor.py`, or the documented local-Ollama socket in `assess/llm.py`),
  when it is suppressed,
  then the suppression is narrow (`per-file-ignores` or a single-line `# noqa: S###` with a short
  reason comment), never a repo-wide `ignore = ["S"]`.
- Given the current tree after enabling `S`,
  when the gate is green,
  then every remaining suppression is listed or summarised in `docs/SECURITY.md` (DELVE-0027) so a
  reader can see what was consciously accepted.

### As a maintainer, I want SAST to stay offline and fast, so that the gate remains usable without network.

- Given a laptop with no network,
  when the ruff security step runs,
  then it still completes using only the installed ruff (no advisory download, no SaaS).
- Given a typical run on this repo,
  when the security rules are enabled,
  then the step stays in the same class of cost as today's ruff check (seconds, not minutes).

## Non-goals

- Dependency CVE scanning; that is DELVE-0026.
- Writing `docs/SECURITY.md`; that is DELVE-0027 (this story may land a stub cross-link, but the essay
  is the sibling's job).
- Semgrep, CodeQL, Bandit-as-a-separate-CLI, or any second SAST installer.
- Changing runtime behaviour or adding runtime dependencies.

## Design notes / links

Proposed config shape in `pyproject.toml` (exact rule fine-tuning is an implementation choice;
document the final select/ignore set in SECURITY.md):

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "S"]

[tool.ruff.lint.per-file-ignores]
# tests may assert on literals, use short throws, etc.
"tests/**" = ["S101"]
```

Expect first-run noise on `S101` (assert used) in tests, and possibly on `subprocess` /
`urllib.request` in doctor and the LLM client. Prefer fixing call shape (pass a list to
`subprocess.run`, keep `shell=False`) over suppressing. The LLM client's localhost HTTP is an
accepted risk of Phase 2; if a rule flags it, suppress narrowly and name it in SECURITY.md.

`run-tests.sh` can either keep a single `ruff check delve tests` (once `S` is in select) or split
`ruff` and `ruff-security` labels; prefer one step unless splitting makes failures clearer. Do not
break the "run every step even if one fails" behaviour.

Locale, screens, tutorial: no impact. Rule 1: scanners stay outside `engine`/`ui` imports.

## Acceptance / verification

- `pyproject.toml` selects `S` (alongside the existing sets); `./run-tests.sh`'s ruff-related step
  fails when a non-suppressed `S` finding is introduced (a small intentional regression test or a
  documented manual check in SECURITY.md is enough; prefer an automated test only if the repo
  already has a pattern for gating tool config).
- The tree is clean under that config: either fixed or narrowly suppressed with comments.
- `./run-tests.sh` stays green offline for this step.
- DELVE-0027's essay names the rule set and the standing suppressions.
