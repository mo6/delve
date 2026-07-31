# tools/

Standalone dev scripts. None of these are part of the `delve` package and none are imported by
it; they exist to generate or check evidence about the repo (mock-ups, the issues index, this
table), stdlib-only, run from the project's venv.

Run any of them through **`./tools.sh <tool> [args...]`** from the repo root (works from any
working directory, no `activate` needed) — `<tool>` is the script's name with or without `.py`,
dashes or underscores both fine (`effort-table`, `effort_table`, `effort_table.py` all mean
`tools/effort_table.py`). `./tools.sh` with no arguments lists what's available. This is the one
fixed entry point worth granting standing permission to, instead of approving each
`python tools/whatever.py` call separately. Calling a script directly
(`.venv/bin/python tools/effort_table.py`) still works the same way if you don't need that.

## Scripts

### `issues.py` — index and lint the issues/ tree

```
./tools.sh issues            # rebuild the index table in issues/README.md
./tools.sh issues --check    # lint + assert the index is current; write nothing
```

Parses every `DELVE-NNNN-slug.md`'s front matter by hand (no YAML dependency) and checks: ids
unique and contiguous from `DELVE-0001`; required front-matter keys present; `status` is a known
value and the file lives where that status implies (archive/, rejected/, or root); shipped
statuses carry commits, unshipped ones don't; `type`/`epic` links are sane; every listed commit
exists in git; every `assets/...` reference resolves both ways; no oversized images; no em-dashes;
the generated README index block is current. `--check` reports every problem in one run and exits
non-zero if any exist; without it, the index is rewritten. Also prints the next free `DELVE-NNNN`
id, which is what to run before starting a new issue file.

### `screens.py` — generate the screen mock-ups in docs/SCREENS.md

```
./tools.sh screens            # print all screens
./tools.sh screens --check    # geometry assertions only, no output
```

Renders the verified 100x30 M2-slice mock-ups from real pack content
(`packs/security-onboarding/`), asserting every frame is exactly 100x30 and every prose line fits
its window. The mock-ups in `docs/SCREENS.md` are *generated, not drawn* — change a screen here
and re-paste the output, never hand-edit the frames in SCREENS.md or they stop being evidence.

### `infoscreen_mockups.py` — proposed mock-ups for DELVE-0035

```
./tools.sh infoscreen_mockups            # print every mock-up
./tools.sh infoscreen_mockups --check    # assert geometry, print nothing
```

Same drawing primitives and geometry assertions as `screens.py`, reused for a screen that doesn't
exist yet (the DELVE-0035 tabbed information screen). Deliberately kept out of `screens.py`'s
`all_screens()`/`SCREENS.md`, since that file is evidence of what's *built*; this is proposed-issue
scaffolding pasted into `issues/` the same disciplined way instead of hand-drawn ASCII that could
silently drift from the real panel-width/line-length rules.

### `effort_table.py` — Markdown table of issues by effort

```
./tools.sh effort_table                          # proposed issues, low effort first
./tools.sh effort_table --status all             # every issue, any status
./tools.sh effort_table --status proposed,in-progress
```

Reuses `issues.py`'s front-matter parser to print a `| Effort | ID | Type | Created | Updated |
Title |` table, sorted low → high effort (then by creation date). Defaults to `status: proposed`
since that's the usual "what's left to pick up" view.

## Adding a new tool

Give it a module docstring whose first line is a one-sentence summary — `./tools.sh` with no
arguments lists every script in this directory using exactly that line, so it doubles as the menu
entry. Follow the existing scripts' shape: stdlib only, an `argparse` CLI, not imported by
`delve` or by anything under `tests/`. Add a section here too.
