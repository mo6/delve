#!/usr/bin/env bash
# Run Delve from the repo's virtualenv, from any working directory.
#
# The venv's python is used directly (no `activate` needed), so the launcher leaves no shell
# state behind. Arguments are passed through verbatim with "$@", so `delve.sh --name "Sir Robin"`
# and `delve.sh validate ./pack` both keep their spacing and their relative paths.
#
# Two conveniences on top of a bare `python -m delve`:
#   * the free-text grader is on by default (`--grader-model qwen2.5:3b`), unless the caller
#     already passed a `--grader-model` of their own;
#   * if the grader is wanted but Ollama is not running, we start `ollama serve` for the duration
#     of the game and stop it again when the game exits, so the model is graded on meaning without
#     leaving a service behind. An Ollama that was already up is left untouched.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
py="$here/.venv/bin/python"

if [[ ! -x "$py" ]]; then
    echo "delve: no virtualenv at $here/.venv" >&2
    echo "  create it with:  python3 -m venv .venv && .venv/bin/pip install -e ." >&2
    exit 1
fi

grader_model="qwen2.5:3b"
ollama_host="localhost"
ollama_port="11434"

# The grader default and the Ollama auto-start apply only to the play path. The `validate`,
# `setup`, and `doctor` subcommands manage the grader themselves (or don't take the flag at all).
playing=1
have_grader_flag=0
for a in "$@"; do
    case "$a" in
        validate|setup|doctor) playing=0 ;;
        --grader-model|--grader-model=*) have_grader_flag=1 ;;
    esac
done

# Add the grader default only when playing and the caller did not choose their own model.
args=("$@")
add_grader=0
if [[ "$playing" -eq 1 && "$have_grader_flag" -eq 0 ]]; then
    args+=(--grader-model "$grader_model")
    add_grader=1
fi

# Is the Ollama service accepting connections on its port? Uses bash's /dev/tcp so no curl needed.
ollama_up() {
    (exec 3<>"/dev/tcp/$ollama_host/$ollama_port") 2>/dev/null
}

ollama_pid=""
stop_ollama() {
    if [[ -n "$ollama_pid" ]]; then
        kill "$ollama_pid" 2>/dev/null || true
        wait "$ollama_pid" 2>/dev/null || true
        ollama_pid=""
    fi
}

# Start Ollama only if the grader is in play, the binary exists, and nothing is already listening.
if [[ "$add_grader" -eq 1 ]] && command -v ollama >/dev/null 2>&1 && ! ollama_up; then
    ollama serve >/dev/null 2>&1 &
    ollama_pid=$!
    # Stop our service on any exit (normal, error, or Ctrl-C).
    trap stop_ollama EXIT INT TERM
    # Wait for it to come up (about 15s), so the first grade doesn't race the service.
    for _ in $(seq 1 150); do
        if ollama_up; then
            break
        fi
        sleep 0.1
    done
fi

"$py" -m delve "${args[@]}"
