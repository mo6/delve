#!/usr/bin/env bash
# Delve's development check gate, in one command, from any working directory.
#
# Two ways to use it:
#   ./run-tests.sh                 the whole gate: pytest, ruff (incl. security rules),
#                                  pip-audit, the screen self-check, the issues index,
#                                  and `validate` on shipped packs. Runs every step even if an
#                                  earlier one fails, so one run shows you every problem, and
#                                  exits non-zero if any step failed.
#   ./run-tests.sh <pytest args>   tight iteration: anything you pass is handed straight to
#                                  pytest, e.g. `./run-tests.sh -k tutorial -x` or
#                                  `./run-tests.sh tests/test_languages.py`.
#
# The venv's python is used directly (no `activate`), so the runner leaves no shell state behind
# and works the same from a subdirectory as from the repo root. Mirrors delve.sh's idiom.
#
# Security steps (DELVE-0024..0027; docs/SECURITY.md):
#   - ruff's `S` rules are offline (same binary as the lint step).
#   - pip-audit needs advisory data from the network. A fetch failure fails the step; it never
#     reports a clean bill of health when it could not check. There is no silent skip.

# Note: no `-e`. A test runner that aborts on the first failure hides the others; instead each
# step is run, its result recorded, and the script exits non-zero at the end if any failed.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"
py="$here/.venv/bin/python"
ruff="$here/.venv/bin/ruff"

if [[ ! -x "$py" ]]; then
    echo "run-tests: no virtualenv at $here/.venv" >&2
    echo "  create it with:  python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
    exit 1
fi

# Fast path: forward args to pytest and stop there, for a focused edit-run loop.
if [[ $# -gt 0 ]]; then
    exec "$py" -m pytest "$@"
fi

failed=()
step() {  # step <label> <command...>
    printf '\n=== %s ===\n' "$1"
    if ! "${@:2}"; then
        failed+=("$1")
    fi
}

step "pytest"                           "$py" -m pytest -q
step "ruff"                             "$ruff" check delve tests tools
# Needs network for the Python Packaging Advisory Database; failure (including fetch failure)
# fails this step. See docs/SECURITY.md.
step "pip-audit"                        "$py" -m pip_audit --progress-spinner off
step "issues"                           "$here/tools.sh" issues --check
step "validate tutorial"                "$py" -m delve validate delve/tutorial
step "validate pilot"                   "$py" -m delve validate packs/security-onboarding
step "validate holy-grail"              "$py" -m delve validate packs/holy-grail
step "validate friends-nap-partners"    "$py" -m delve validate packs/friends-nap-partners
step "validate ethics-of-ai"            "$py" -m delve validate packs/ethics-of-ai

printf '\n'
if (( ${#failed[@]} )); then
    printf 'FAILED: %s\n' "${failed[*]}"
    exit 1
fi
printf 'All checks passed.\n'
