#!/usr/bin/env bash
# Build a distribution zip of Delve for sending to a Windows test machine.
#
# Includes only what's needed to install and run the app: the delve/ package,
# the shipped packs/, and pyproject.toml. Excludes all development files
# (tests/, tools/, docs/, issues/, NetHack/, poc/, .venv/, .git/, CLAUDE.md,
# run-tests.sh, etc.) and any __pycache__/.pyc cruft.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
NAME="delve-${VERSION}-windows-test"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

DEST="$STAGE/$NAME"
mkdir -p "$DEST"

# Application package: exclude __pycache__/.pyc.
mkdir -p "$DEST/delve"
rsync -a --exclude '__pycache__' --exclude '*.pyc' delve/ "$DEST/delve/"

# Shipped training packs.
mkdir -p "$DEST/packs"
rsync -a --exclude '__pycache__' --exclude '*.pyc' packs/ "$DEST/packs/"

# Install metadata. pyproject.toml's readme = "README.md" requires the file to exist for the
# build backend; ship a short stand-in rather than the full dev README (which links docs/ that
# aren't part of this bare distribution).
cp pyproject.toml "$DEST/"
cat > "$DEST/README.md" <<EOF
# Delve (Windows test build)

A NetHack-style training application. See WINDOWS-TEST-README.txt for install/run instructions.
EOF

cat > "$DEST/WINDOWS-TEST-README.txt" <<'EOF'
Delve - Windows test build
===========================

Requirements: Python 3.14+ (https://www.python.org/downloads/), a
terminal at least 100x30 (Windows Terminal's default size), and Ollama
(https://ollama.com) with a grader model pulled (see below).

A local LLM grader is required to play at all, not optional: Delve
checks it's reachable before the game starts, and exits with a
diagnosis instead of launching if it isn't. (Once a run is under way, a
single low-confidence answer can fall back to keyword grading for that
one verdict, but that's mid-run resilience, not a way to play without a
grader from the start.)

Install:

    py -3.14 -m venv .venv
    .venv\Scripts\pip.exe install .

(If PowerShell's script-signing policy allows it, ".venv\Scripts\activate"
lets you drop the ".venv\Scripts\" prefix below and just say "python"/
"pip" for the rest of this session. If activation is blocked or silently
doesn't take effect, skip it and call ".venv\Scripts\python.exe" /
".venv\Scripts\pip.exe" directly, as below - if a bare "python -m delve"
ever fails with "ModuleNotFoundError: No module named '_curses'", that
means it quietly ran a different, non-venv Python; use the full
".venv\Scripts\python.exe" path instead.)

Install and start Ollama, then pull the default grader model:

    ollama pull qwen2.5:3b

Check readiness without launching the game:

    .venv\Scripts\python.exe -m delve doctor

Play:

    .venv\Scripts\python.exe -m delve

Delve asks "Who are you?" (this owns your certificate collection; it's
trust-based, not a login), lets you pick a companion, and offers the
tutorial floor (Dlvl 0), which teaches the controls and can be walked
out of at any time.

To use a different model or host, pass --grader-model / --grader-host,
e.g.: .venv\Scripts\python.exe -m delve --grader-model qwen2.5:3b
EOF

OUT="${NAME}.zip"
rm -f "$OUT"
(cd "$STAGE" && zip -rq "$OLDPWD/$OUT" "$NAME" -x '*.DS_Store')

echo "Built $OUT"
