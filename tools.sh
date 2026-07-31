#!/usr/bin/env bash
# Run one of the tools/ scripts from the repo's virtualenv, from any working directory.
#
#   ./tools.sh <tool> [args...]
#   ./tools.sh                     list the available tools
#
# <tool> is a script's name under tools/, with or without its .py suffix and with - or _
# interchangeably (effort-table, effort_table, and effort_table.py all mean tools/effort_table.py).
# Everything after it is passed through verbatim, e.g. `./tools.sh effort-table --status all`.
#
# This exists as one fixed entry point so a caller (a human or an agent) can be given permission
# to run `./tools.sh` once and use any tool under tools/, rather than needing separate permission
# for every `python tools/whatever.py` invocation. Mirrors delve.sh's and run-tests.sh's idiom:
# the venv's python is used directly (no `activate`), so nothing here leaves shell state behind.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
py="$here/.venv/bin/python"
tools_dir="$here/tools"

if [[ ! -x "$py" ]]; then
    echo "tools: no virtualenv at $here/.venv" >&2
    echo "  create it with:  python3 -m venv .venv && .venv/bin/pip install -e ." >&2
    exit 1
fi

list_tools() {
    for f in "$tools_dir"/*.py; do
        name="$(basename "$f" .py)"
        [[ "$name" == __init__ ]] && continue
        summary="$("$py" - "$f" <<'EOF'
import ast, sys
tree = ast.parse(open(sys.argv[1]).read())
doc = ast.get_docstring(tree) or ""
print(doc.splitlines()[0] if doc else "")
EOF
)"
        printf '  %-16s %s\n' "$name" "$summary"
    done
}

if [[ $# -eq 0 ]]; then
    echo "usage: ./tools.sh <tool> [args...]" >&2
    echo "available tools:" >&2
    list_tools >&2
    exit 1
fi

tool="$1"; shift
# Normalise: drop a trailing .py, turn dashes into underscores (module-style names).
tool="${tool%.py}"
tool="${tool//-/_}"

script="$tools_dir/$tool.py"
if [[ ! -f "$script" ]]; then
    echo "tools: no such tool '$tool' (looked for $script)" >&2
    echo "available tools:" >&2
    list_tools >&2
    exit 1
fi

exec "$py" "$script" "$@"
