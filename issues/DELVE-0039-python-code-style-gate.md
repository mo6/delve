---
id: DELVE-0039
title: Define Python code style and add a style gate to run-tests.sh
status: proposed
area: [tools, docs]
type: feature
epic:
effort: medium
milestone:
version:
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: []
related: [DELVE-0024]
supersedes: []
docs: [docs/SECURITY.md]
changelog:
---

# Define Python code style and add a style gate to run-tests.sh

## Summary

Write down Delve's Python code style as a short, explicit document, grounded in three widely used references (Guido van Rossum's original style essay, PEP 8, and *The Hitchhiker's Guide to Python*'s style chapter), then extend `./run-tests.sh` so the style is machine-checked, not just documented. Today ruff already runs (`E`, `F`, `I`, `UP`, `B`, `S`), but nothing in the gate checks *formatting* (whitespace, quote style, line breaks) and the project has never written down which of the three source guides it follows and where it deliberately departs (`line-length = 100`, for one). This issue gives maintainers and pack-tooling contributors one page to read and one gate step that enforces it, the same way DELVE-0024..0027 did for security. While drafting DELVE-0039 itself, a second, related honor-system gap surfaced: CLAUDE.md's own "paragraphs are single lines, never hard-wrapped" rule for every Markdown file the project writes (`issues/`, `docs/`, `CHANGELOG.md`) has no gate either, so this issue folds in one story to check that too, since it is the same "written style rule with no enforcement" shape as the Python case, checked from the same `./run-tests.sh` run.

## Motivation / problem

`pyproject.toml`'s `[tool.ruff]` block enforces a rule *set*, but nothing explains *why* those letters and not others, and nothing enforces formatting: two contributors can hand-format the same file two different ways and both pass `./run-tests.sh` today, because the gate only runs `ruff check`, never `ruff format --check`. There is also no single page a new contributor (human or an LLM coding agent) can read to learn Delve's Python conventions; CLAUDE.md documents *design* rules (the five rules, cross-platform, locale) but not code-shape conventions like naming, docstring use, or import layout. The three references named above already agree on the vast majority of this (4-space indent, `snake_case` functions/variables, `PascalCase` classes, one import per line grouped stdlib/third-party/local, a blank-comment-free "why not what" comment discipline); writing it down once, with Delve's specific deviations called out, is cheaper than re-deriving it per PR review.

## Stories

### As a maintainer, I want a written Python style guide for this repo, so that a human or an LLM coding agent has one page to check style questions against instead of re-deriving conventions from review comments.

- Given a new `docs/PYTHON_STYLE.md` essay, when a maintainer reads it, then it names the three source references (python.org style essay, PEP 8, `docs.python-guide.org` style chapter), states which parts Delve adopts as-is, and calls out every deliberate deviation with a reason (at minimum: `line-length = 100` instead of PEP 8's 79, and the project's existing "one core seam opens a socket" and comment-discipline rules already in `CLAUDE.md`, which this essay links to rather than repeats).
- Given the existing `[tool.ruff]` configuration in `pyproject.toml`, when the essay describes it, then it explains what each selected rule code (`E`, `F`, `I`, `UP`, `B`, `S`) checks in plain language, so the config is legible without cross-referencing ruff's own docs.
- Given a contributor asks "does Delve use docstrings / type hints / a particular quote style?", when they check the essay, then the answer is stated explicitly rather than left implicit in existing code.

### As a maintainer, I want a style gate in `./run-tests.sh`, so that a formatting or naming regression fails the same way a lint or security regression already does.

- Given a Python file in `delve/`, `tests/`, or `tools/` that is not formatted per the project's chosen formatter, when `./run-tests.sh` runs, then a new `style` step fails and names the unformatted file(s), the same way the existing `ruff` step already fails on a lint violation.
- Given the existing `ruff` step, when this issue is implemented, then `ruff format --check delve tests tools` runs as its own labelled step (not folded into the existing `ruff` step), so a formatting failure and a lint failure are reported distinctly, consistent with how `pip-audit` and `screens` are already separate labelled steps.
- Given the current codebase, when the new `style` step is first added, then it passes clean on the first run (run `ruff format delve tests tools` once, in its own commit, before wiring the check step, so the gate never lands red on day one).
- Given a maintainer wants stricter naming or docstring checks later (ruff's `N`/`D`/`C90` rule groups), then this issue leaves that as a follow-up, not scope creep here (see Non-goals).

### As a maintainer, I want the "paragraphs are single lines, never hard-wrapped" rule checked automatically, so that a hard-wrapped paragraph in an issue, doc, or the changelog is caught the same way this issue's own first draft should have been.

- Given a Markdown file under `issues/` (excluding `archive/` and `rejected/`, which are frozen once moved) or `docs/`, or `CHANGELOG.md`, when `tools/issues.py --check` runs, then it flags any line inside a body paragraph that is immediately followed by another non-blank line that is not a list item, heading, table row, or code-fence line, since that pattern is the hard-wrap-at-~95-columns habit CLAUDE.md names, not a real second line.
- Given a file that legitimately has consecutive short lines that are not prose (a table, a fenced code block, YAML front matter, a list where each item is one line), when the checker runs, then none of those are flagged; the check only looks inside ordinary paragraph text.
- Given the checker finds a violation, when it reports it, then the message names the file and the first offending line number, the same style as the existing "index is stale" / "ids not contiguous" messages, so a maintainer can jump straight to it.
- Given this check is added, when it is first run over the existing tree, then every current violation (including this issue's own first-draft paragraphs, already fixed by hand) is clean, so the check never lands pre-broken.

## Non-goals

- Not proposing a new tool: ruff already ships a formatter (`ruff format`, Black-compatible), so this reuses the existing dependency rather than adding Black, autopep8, or yapf.
- Not expanding the linted rule set beyond formatting in this issue. Adding `N` (pep8-naming), `D` (pydocstyle), or `C90` (mccabe complexity) is a reasonable follow-up but is separate work with its own churn to review; file a new `DELVE-NNNN` for it if wanted.
- Not a rewrite of existing code to a new style; `ruff format`'s one-time pass (a single commit, no behaviour change) is the only code touched, everything else is gate and docs.
- Not a pack-content style guide; `docs/STYLE.md` (voice, em-dashes, locale rules for lesson prose) already covers pack content and is unrelated to this issue's Python-code scope.
- Not an em-dash checker or any other prose-voice rule from `docs/STYLE.md`; the new `tools/issues.py --check` story is scoped to the single mechanical rule (hard-wrapped paragraphs), not a general prose linter.
- Not an auto-fixer; the check flags and names the offending file/line, the same as every other `--check` failure in this repo, and a maintainer rejoins the paragraph by hand.

## Design notes / links

- Follows the same shape as [DELVE-0024](../issues/archive/DELVE-0024-security-scanning.md) (security gate epic) and its essay [docs/SECURITY.md](../docs/SECURITY.md): a short doc naming purpose and tools, plus labelled `./run-tests.sh` steps that fail the gate on regression.
- `pyproject.toml`'s `[tool.ruff]` (`line-length = 100`, `target-version = "py314"`, `select = ["E", "F", "I", "UP", "B", "S"]`) and `[tool.ruff.lint.per-file-ignores]` are the existing config this issue documents and extends with a `[tool.ruff.format]` section only if a non-default formatter option is needed (Delve should start from ruff's formatter defaults and only override if the default conflicts with something CLAUDE.md already states, e.g. `line-length`).
- CLAUDE.md's own code-shape conventions (rule 1/2 module boundaries, "content never goes in frontmatter", the comment-discipline note under "Editing content that already exists") are design/architecture rules, not formatting; this essay should link to CLAUDE.md rather than duplicate it, the same way `docs/SECURITY.md` links out rather than re-stating PLAN.md.
- No locale impact (this is Python source style, not pack content or `delve/strings`); no screen or tutorial impact.
- The hard-wrap check extends `tools/issues.py` (already run via `./tools.sh issues --check`, already a `run-tests.sh` step), not a new tool; it should live beside the existing front-matter/index checks in that module rather than as a separate script.

## Acceptance / verification

- `docs/PYTHON_STYLE.md` exists, links the three source references, and is linked from this issue's `docs:` front matter once written.
- `./run-tests.sh` gains a `style` step running `ruff format --check delve tests tools`, reported separately from the existing `ruff` (lint) step; a manual check is running `./run-tests.sh` with one file deliberately reformatted out of style and confirming only the `style` step fails, not `ruff`.
- `./run-tests.sh` is green end to end after the one-time `ruff format delve tests tools` pass is committed.
- `./tools.sh issues --check` gains the hard-wrapped-paragraph check and passes clean over the current `issues/` (excluding `archive/`/`rejected/`) and `docs/` trees and `CHANGELOG.md`; a manual check is hard-wrapping one paragraph in a scratch file and confirming the checker names it.
