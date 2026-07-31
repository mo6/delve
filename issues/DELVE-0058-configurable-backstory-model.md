---
id: DELVE-0058
title: A user config file for a separate, more advanced backstory model
status: proposed
area: [delve, session, docs]
type: feature
epic:
effort: high
milestone:
version:
version_span:
created: 2026-07-30
updated: 2026-07-30
commits: []
related: [DELVE-0028, DELVE-0057, DELVE-0033, DELVE-0062]
supersedes: []
docs: [docs/PHASE2.md, docs/SECURITY.md]
changelog:
---

# A user config file for a separate, more advanced backstory model

## Summary

Today the Objectives tab's optional scene-setting passage (DELVE-0028) always reuses whichever
model the free-text grader is configured with (`--grader-model`/`--grader-host`, or their
defaults). A learner or maintainer may want a smaller, fast model for grading (latency matters
there; the exam pauses on it) and a separate, more capable model for prose (latency matters far
less; it is a background call cached once per run). This adds a small TOML config file at
`~/.config/delve/config.toml` (respecting `$XDG_CONFIG_HOME`) with independent `[grader]` and
`[backstory]` tables, so the two can be pointed at different models/hosts without a CLI flag for
every combination.

## Motivation / problem

There is no config-file mechanism in Delve at all today; every runtime choice is a CLI flag or an
environment variable read once at the edge (`$DELVE_NAME`, `$DELVE_CAT_NAME`/`$DELVE_DOG_NAME`,
`--grader-model`/`--grader-host`). That is fine for a single model used one way, but DELVE-0028
introduced a second, different use of a model (generation, not judgement, PHASE2.md's distinction
sharpened by DELVE-0057), and a maintainer testing both wants to fix the grader model in place
(cheap, fast, proven for grading) while trying different, larger models for prose quality, without
retyping two extra CLI flags every launch.

A follow-up comparison (DELVE-0062's Torchbearer report, comparing `qwen3.5:9b` against a locally
downloaded `gemma3:12b` for ambient prose) surfaced a real ceiling on the local-only premise this
issue originally assumed: every model a maintainer can try is bounded by what fits, and runs fast
enough, on their own machine. A maintainer with a capable laptop but no GPU, or one simply curious
whether a frontier hosted model reads noticeably better for atmospheric prose, has no way to find
out without this issue also covering a non-Ollama provider. Since the backstory call is already an
independent, optional, never-play-gating seam (DELVE-0033's opposite), it is the natural place to
support a hosted API alongside local Ollama, without touching the grader (which stays local-only:
latency matters there, and DELVE-0033 requires it to work offline).

## Stories

### As a maintainer, I want a config file that sets a different model/host for backstory prose than for grading, so that I can use a bigger model for atmosphere without slowing down exams.

- Given `~/.config/delve/config.toml` contains
  ```toml
  [grader]
  model = "qwen2.5:3b"

  [backstory]
  model = "qwen3.5:9b"
  ```
  when a run starts,
  then the free-text grader uses `qwen2.5:3b` and the Objectives passage is generated with
  `qwen3.5:9b`, over whatever `host` each table specifies (or the shared Ollama default if neither
  gives one).

### As a maintainer, I want `[backstory]` to inherit from `[grader]` when it doesn't say otherwise, so that a minimal config only needs to override what actually differs.

- Given a config file with only `[grader]` set (no `[backstory]` table at all, or one with only
  some keys),
  when a run starts,
  then backstory's model/host fall back to `[grader]`'s (and from there to the built-in defaults),
  exactly reproducing today's DELVE-0028 behaviour for anyone who never adds a `[backstory]` table.

### As a player, I want the existing `--grader-model`/`--grader-host` flags to keep working exactly as before, so that adding a config file doesn't change anything for someone who never creates one.

- Given no config file exists,
  when a run starts,
  then behaviour is byte-for-byte what it is today: `--grader-model`/`--grader-host` (or their
  defaults) drive both the grader and, since backstory falls back to grader, the backstory call.
- Given a config file's `[grader]` table sets a model,
  when `--grader-model` is also passed on the command line,
  then the CLI flag wins (CLI over config file, matching how `--lang`/`--pet` already layer over
  their env defaults) for the grader; and since `[backstory]` only inherits from `[grader]`'s
  *config-file* value, not the CLI override, this issue's own story below covers what backstory
  does when the CLI overrides grader but the config file doesn't mention backstory at all.

### As a maintainer, I want the config file, not a CLI flag, to be the only way to set the backstory model, so that quick grader experiments on the command line never accidentally retarget prose generation too.

- Given `--grader-model`/`--grader-host` are passed on the command line and no `[backstory]` table
  exists in the config file,
  when a run starts,
  then backstory still falls back to whatever `[grader]` says *in the config file* (or the built-in
  default if the config file has no `[grader]` table either), never to the CLI-overridden grader
  model; there is no `--backstory-model`/`--backstory-host` flag.

### As a maintainer, I want to point the backstory model at a hosted API (Claude) instead of local Ollama, so that I can try a far more capable model than my own hardware can run.

- Given `~/.config/delve/config.toml` contains
  ```toml
  [backstory]
  provider = "anthropic"
  model = "claude-haiku-4-5"
  ```
  and the environment has `$ANTHROPIC_API_KEY` set,
  when a room's ambient passage is generated,
  then it is requested from the Anthropic API using that model, over `RoomBackstoryRunner`'s
  existing queue/poll machinery unchanged; the grader is unaffected regardless of this setting
  (grading stays local-only, per this issue's own non-goals).
- Given `[backstory].provider` is omitted, or set to `"ollama"`,
  when a run starts,
  then behaviour is exactly what the rest of this issue already specifies (local Ollama,
  `[backstory]` falling back to `[grader]`); `"ollama"` is the default, so every existing story and
  its acceptance criteria hold unchanged for anyone who never sets `provider`.
- Given `[backstory].provider = "anthropic"` and `$ANTHROPIC_API_KEY` is unset or empty,
  when a run starts,
  then a clear one-line diagnostic is printed to stderr naming the missing variable, and backstory
  falls back to being unconfigured (the same silent, non-gating "no toast" state a missing Ollama
  model already leaves it in, DELVE-0028's original design) rather than crashing or retrying; the
  grader is still entirely unaffected.
- Given `[backstory].provider = "anthropic"` and no `model` is set,
  when a run starts,
  then it defaults to `claude-haiku-4-5` (a small, inexpensive model, matching this feature's own
  spirit of "try a different model for cheap," not an invitation to default to the most capable and
  most expensive one every run pays for).

### As a maintainer, I want it obvious that an Anthropic-backed backstory sends pack content to a third party, so that I don't find out by accident.

- Given `[backstory].provider = "anthropic"`,
  when `delve doctor` runs (or, absent that, the first time such a run starts),
  then a one-line notice states plainly that room descriptions, keeper names, lesson topics, and
  the learner's carried items will be sent to Anthropic's API for this feature, the same spirit as
  an existing `delve doctor` diagnostic, not a blocking confirmation prompt (backstory already
  never gates play, and this issue's own non-goals keep it that way).
- Given the pilot pack or any other pack ships only placeholder/example content (the pilot's own
  documented placeholders, CLAUDE.md's "Pilot pack" section),
  this story does not change what content a pack author puts in a room; it only makes the existing
  local-vs-hosted distinction visible at the moment it starts to matter.

### As a maintainer, I want a missing or malformed config file to never block play, so that this stays optional exactly like the backstory passage itself.

- Given no config file exists at the XDG path,
  when a run starts,
  then nothing changes from today (grader and backstory both use CLI flags/defaults as now).
- Given a config file exists but is malformed TOML or has an unexpected shape,
  when a run starts,
  then a clear one-line diagnostic is printed to stderr (naming the file and the problem) and the
  run proceeds with built-in defaults, the same "never gate play on this" principle DELVE-0028 gave
  the backstory passage itself.

## Non-goals

- A config file for anything other than the grader/backstory model and host in this issue; other
  settings (pack path, pet, locale) stay CLI-only for now. A general settings file is a reasonable
  future direction but not scoped here.
- Auto-creating or scaffolding the config file (`delve setup`/`doctor` growing a `--write-config`
  or similar); this issue only reads one if present.
- A `--backstory-model`/`--backstory-host` CLI flag (explicitly rejected above, to keep grader
  experiments on the command line from silently retargeting prose too).
- Validating that a configured backstory model is actually installed/pulled beyond the existing
  `LLMUnavailable` runtime fallback; `delve doctor`/`setup` remain grader-focused.
- An external provider for the **grader**. `[grader].provider` does not exist; grading stays
  Ollama-only, both because DELVE-0033 requires it to work fully offline (no network dependency on
  the exam path) and because sending a learner's free-text answer to a third party is a materially
  different privacy question than sending ambient scene-setting facts, one this issue does not
  attempt to answer.
- Any provider other than Ollama and Anthropic (OpenAI, a generic OpenAI-compatible endpoint,
  etc.). The `provider` field is a closed two-value enum for now; widening it is a future issue if
  one is ever wanted, not a speculative "provider plugin" system built ahead of a second real need.
- Reading the API key from the config file, or from any flag. `$ANTHROPIC_API_KEY` (the standard
  Anthropic SDK/CLI convention, per its own docs) is the only source; a real credential does not
  belong in a file a maintainer might commit, screenshot, or paste into a bug report the way a
  model name harmlessly can.
- A blocking consent prompt before an Anthropic-backed run. The notice story above is informational
  (stderr/`delve doctor`, consistent with every other backstory diagnostic in this issue and
  DELVE-0028's own "never gate play" principle), not a confirmation the maintainer must dismiss.

## Design notes / links

New module, likely `delve/config.py`: a `load_config() -> Config` (or similar) reading
`Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser() / "delve" / "config.toml"`
with stdlib `tomllib` (no new dependency, matching `delve/strings/__init__.py`'s own reasoning for
`tomllib` over anything else), returning defaulted, plain data (e.g. a small frozen dataclass with
`grader_model`/`grader_host`/`backstory_model`/`backstory_host`, all `str | None`) rather than a
raw dict, so `__main__.py`'s resolution logic reads typed fields. A missing file is not an error
(`FileNotFoundError` -> defaults); a parse error prints the diagnostic and falls back the same way,
never raising out of `main()`.

Resolution order, built in `delve/__main__.py` alongside where `--grader-model`/`--grader-host` are
already resolved (`_play`, `_doctor`, `_setup`): grader = CLI flag, else config `[grader]`, else
`DEFAULT_MODEL`/`DEFAULT_HOST`. backstory = config `[backstory]`, else config `[grader]` (the
*file's* value, deliberately not the CLI-resolved grader value, per this issue's own story), else
`DEFAULT_MODEL`/`DEFAULT_HOST`. `RunState`'s constructor already takes a `grader_runner`; this
issue adds a second, independent `OllamaClient` (or `None`) for `backstory.BackstoryRunner`, built
at the same CLI edge as the grader's client, so `session/backstory.py` stops deriving its client
from `RunState._grader_runner` (`_backstory_client`'s current duck-typed lookup, DELVE-0028) and
instead takes one directly, e.g. `RunState(..., backstory_client=...)`. Keeps rule 2's `ui`/`assess`
boundary: the config file is read at the CLI edge only, same as the grader model is today.

Depends on DELVE-0057 landing first (or alongside): the backstory client, once independently
configurable, still needs `OllamaClient.chat`'s non-JSON/non-zero-temperature call shape to
produce usable prose regardless of which model answers it.

**The Anthropic client stays in `delve/assess/llm.py`**, alongside `OllamaClient`, not a new
module: `docs/SECURITY.md`'s attack-surface table already names this file as "the **only** core
module that opens a network connection," and a second socket-opening class in a second file would
quietly break that invariant rather than extend it. A new `AnthropicClient` matches
`OllamaClient.chat`'s exact signature (`chat(self, prompt, *, json_mode=True, temperature=0,
model=None) -> ChatReply`) so `RoomBackstoryRunner` calls either client identically with no
`isinstance` branch anywhere in `session/`; `json_mode` is accepted but unused; the backstory call
always passes `json_mode=False` (DELVE-0057), so the request-shaping difference between providers
never actually matters on this path, and `AnthropicClient` does not need to implement a JSON-forced
mode at all. Uses the official `anthropic` Python package (a new, optional dependency, gated the
same way `windows-curses` already is conditional in `pyproject.toml`, or a plain `try/except
ImportError` at the top of `llm.py` raising `LLMUnavailable` on first use if the package is
missing, so a maintainer who never sets `provider = "anthropic"` never needs it installed).

`model`/`host` stay readable attributes on `AnthropicClient` (`host` is a fixed, cosmetic string
like `"api.anthropic.com"`, not a configurable field, since there is exactly one Anthropic API
endpoint) so `RunState._grader_info`/`_backstory_metrics`-style duck-typed reads (rule 1: no new
`assess.llm` import in `session/run.py`) keep working unchanged for the Status/Grader tab's
display (DELVE-0062's follow-up work made that tab reflect ambient calls too, so an
Anthropic-backed backstory should show up there exactly like an Ollama-backed one, tokens and
latency both, with `host` simply reading `api.anthropic.com` instead of a local address).

**Config shape:** `[backstory]` gains one new key, `provider: str = "ollama"` (the only other legal
value: `"anthropic"`), read by the same `delve/config.py` this issue already specifies; `[grader]`
gets no such key (see this issue's own non-goals). `Config.backstory_provider` joins
`backstory_model`/`backstory_host` as the third field `__main__.py`'s resolution logic reads.
When `provider == "anthropic"`, `backstory_host` is meaningless (ignored, not validated) and
`backstory_model` defaults to `"claude-haiku-4-5"` rather than falling back to `[grader]`'s Ollama
model, since a `[grader]` model string is never a valid Anthropic model id and vice versa;
`RunState`'s constructed backstory client is an `AnthropicClient` reading `$ANTHROPIC_API_KEY` from
the environment at the same CLI edge the rest of this issue's resolution already lives at (`os.environ`,
not `os.getenv` with a silent default, so a missing key is a deliberate, diagnosed state per this
issue's own story, not a client constructed with `api_key=None` that fails confusingly on first
call).

## Acceptance / verification

- A `delve/config.py` test asserts: no file -> all fields `None`/defaults; a file with only
  `[grader]` -> backstory fields fall back to it; a file with both tables -> each independent; a
  malformed file -> defaults plus a printed diagnostic, no exception.
- A `__main__` resolution test (or a session-construction test at the same seam) asserts the CLI
  flag > config `[grader]` > built-in default order for the grader, and config `[backstory]` >
  config `[grader]` (file value, not CLI-overridden) > built-in default order for backstory,
  including the case where `--grader-model` is passed and `[backstory]` is absent.
- A test asserts `RunState` can be given a backstory client independent of its grader runner, and
  `session/backstory.py` no longer reads `_grader_runner` to find one (`_backstory_client` removed
  or repointed).
- A test asserts `provider` defaults to `"ollama"` when omitted, and that every existing
  Ollama-path test in this issue's own suite still passes unmodified with that default.
- A test asserts `provider = "anthropic"` with no `model` set resolves to `"claude-haiku-4-5"`, and
  that it does **not** fall back to `[grader]`'s (Ollama) model when `[grader]` is also set.
- A test asserts a missing/empty `$ANTHROPIC_API_KEY` under `provider = "anthropic"` prints the
  named diagnostic and leaves backstory unconfigured (no toast ever queued, no exception), the same
  outcome shape as today's "no model configured" state.
- A test asserts `AnthropicClient.chat` matches `OllamaClient.chat`'s call signature exactly, using
  a fake/mocked Anthropic client (no real network call in the test suite, matching every existing
  `OllamaClient` test's own convention of injecting a fake).
- A test asserts the Anthropic content-disclosure notice's exact wording (or that `delve doctor`
  emits it) when `provider = "anthropic"` is configured.
- `./run-tests.sh` passes; `docs/PHASE2.md` gains a short note on the two independent models and
  the local-vs-hosted backstory provider choice; `docs/SECURITY.md`'s attack-surface table gains a
  row for the Anthropic API alongside the existing Ollama one, noting it is opt-in and
  backstory-only.
