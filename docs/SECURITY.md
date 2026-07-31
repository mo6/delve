# Security gate

**Status: implemented (1.9.1).** A maintainer-facing gate, not a certification. It asks two
questions every `./run-tests.sh` run: are there common insecure patterns in our Python, and are any
installed packages known-vulnerable? Issues [DELVE-0024](../issues/archive/DELVE-0024-security-scanning.md)
through DELVE-0027 are the testable *what*; this essay is the *why* and the runbook.

Green here means the checklist below passed. It does **not** mean Delve is an audit system, that
identity is strong, or that a scroll export is authentic. Those limits stay in
[PLAN.md](PLAN.md) sections 10 and 11.

---

## 1. Purpose

Catch regressions that are cheap for a tool to see and expensive for a human to rediscover:

- insecure call shapes (`eval`, `shell=True`, weak hashes, …) via ruff's Bandit-compatible `S` rules;
- known CVEs in the venv via `pip-audit` (PyPA advisory database).

Fix first. Suppress only when the finding is an accepted, documented risk, and keep the ignore
narrow.

## 2. Attack surface

What the scanners (and a reviewing maintainer) should keep in mind:

| Surface | Where | Notes |
|---|---|---|
| Local LLM socket | `delve/assess/llm.py` | The **only** core module that opens a network connection. Default host is `http://localhost:11434` (Ollama). Scheme is restricted to `http`/`https`. |
| Setup subprocess | `delve/doctor.py` | `ollama pull` via an injected `subprocess.run`; not on the play hot path. Prints install hints rather than piping an installer to a shell. |
| Progress store | `delve/progress/` | SQLite on the learner's machine. Identity is trust-based (PLAN §10). |
| Pack loading | `delve/content/` | Markdown from disk. Packs are data; they must never execute code. |
| Curses UI | `delve/ui/` | Render only; no network. |

Out of scope for this gate: the Ollama binary and model weights, the host OS, pack editorial
quality ("is this security advice sound?"), and anything gitignored (including a future instance
`variables.md`).

## 3. Tools in `./run-tests.sh`

| Step | Tool | Network | Scans |
|---|---|---|---|
| `ruff` | ruff with `select` including `S` | offline | `delve/`, `tests/`, `tools/` |
| `pip-audit` | `python -m pip_audit` | **needs** advisory data | packages installed in `.venv` |

Run in isolation while debugging:

```sh
.venv/bin/ruff check delve tests tools
.venv/bin/python -m pip_audit --progress-spinner off
```

`pip-audit` is a `[dev]` extra (`pip install -e '.[dev]'`). It audits the **installed** environment
(the same one the gate uses). There is no lock file today; if one is added later, point the audit
at it and update this section.

**Fetch failure is a failed step.** If advisory data cannot be downloaded, `pip-audit` exits
non-zero. That is intentional: the gate must not report success when it could not check. There is
no silent skip and no "offline means clean" path. Re-run with network, or fix connectivity.

## 4. Findings lifecycle

1. The gate fails and names a ruff rule id (`S###`) or a `pip-audit` advisory id.
2. **Prefer a fix:** change the call shape, or bump the package constraint in `pyproject.toml` and
   refresh the venv.
3. **Suppress only if accepted:** a narrow `per-file-ignores` entry or a single-line `# noqa: S###`
   with a short reason comment. For advisories, ignore by package + advisory id only, with a reason
   in this file.
4. Update the standing-exceptions table below in the same change.
5. Never `ignore = ["S"]` (or any blanket disable of the security set) in `pyproject.toml`.

Severity policy: every non-suppressed `S` finding and every non-ignored advisory fails the gate.
Informational noise is tuned out in `per-file-ignores`, not left for each maintainer to re-triage.

## 5. Standing exceptions

Canonical config: `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml`. Reasons live here so
config stays short.

| Location | Rule / advisory | Reason |
|---|---|---|
| `tests/**` | `S101` | pytest uses `assert`; not a production assert-as-control-flow smell. |
| `delve/engine/rng.py` | `S311` | Deterministic game RNG for tile-for-tile regen; cryptographic randomness would break snapshots. |
| `delve/__main__.py` (seed line) | `S311` (`# noqa`) | Same: choosing a play seed is not a crypto operation. |
| `delve/assess/llm.py` | `S310` | Intentional local Ollama HTTP. `_http_url` rejects non-`http(s)` schemes; ruff still flags every `urllib` use. |
| `tools/**` | `S603`, `S607`, `S101` | Maintainer scripts call `git` with fixed argv lists (no shell, no attacker-controlled executable name). Check scripts (`screens.py`, …) use `assert` as their failure mode, same idea as tests. |

No `pip-audit` ignores at 1.9.1. When one is needed, add a row here (package, advisory id, reason)
and the matching ignore flag/config beside the `pip-audit` step.

## 6. What green does not mean

- **Identity is trust-based.** Anyone can type any name at "Who are you?". See PLAN §10.
- **Scroll export (Phase 2) gives confidentiality, not authenticity.** A public key is public; a
  fabricated scroll can be encrypted. Fine for training; not an audit record. See PLAN §11.
- **The Ollama stack is out of band.** This gate does not patch or version-pin the Ollama binary or
  the pulled model.
- **Pack content is editorial.** `delve validate` enforces format and pack policy, not whether a
  lesson's advice is sound.

## 7. Cadence

- Every `./run-tests.sh` (Definition of Done in [issues/AGILE.md](../issues/AGILE.md)).
- Re-read this essay when adding a socket, a `subprocess` call, a new runtime or `[dev]`
  dependency, or a standing suppression.
- Secrets scanning and hosted CI are deferred (DELVE-0024); revisit when there is a real secret
  surface or a remote.
