# Delve

A NetHack-style training application. Learners descend a dungeon; keepers teach a topic and
examine them on it, multiple-choice or typed free text graded by a locally running LLM; passing
makes a door appear in the wall. Reaching the final chamber awards a certificate, collected across
many training dungeons over time.

*Named for both meanings: dungeon delving, and delving into a subject.*

One training is a **pack** (a dungeon); a module is a **chapter** (a floor); a lesson is a **room**
(one keeper, one examination, one door). You walk a floor, talk to a keeper, read a short lesson,
answer a question or two, and earn a door through the stone. Descend the stairs to the next
chapter; lift the certificate from its pedestal to finish.

Design lives in [docs/PLAN.md](docs/PLAN.md); how to write a pack is in
[docs/AUTHORING.md](docs/AUTHORING.md); voice and translation rules are in [docs/STYLE.md](docs/STYLE.md);
the rules that are expensive to get wrong are in [CLAUDE.md](CLAUDE.md). Structured issues,
written as agile user stories (epics, features, and stories with a shared Definition of Ready and
Done; see [issues/AGILE.md](issues/AGILE.md)), and an archive of the ones already
implemented with their commit ids, live in [issues/](issues/README.md).

Status: **released and playable end to end.** The pilot plays start to finish in English and Dutch,
with a 16-colour map, box-drawn room walls, per-keeper voices, an orientation floor, save/resume,
object pickup/drop, a companion pet that races you for coins and fetches what you drop, coloured
navigable answer lists, a local free-text grader (Phase 2), and a certificate collection. Post-1.0
work continues as fixes and tuning from real play. **Windows is now verified** (DELVE-0046): install
and play both work end to end via `windows-curses`, including an LLM-graded free-text room; see
"Windows notes" below for two install-time gotchas real testing found.

## Requirements

- **Python 3.14+** (Homebrew on macOS; python.org on Windows).
- **macOS, Linux, or Windows.** `curses` is stdlib on macOS/Linux; on Windows, `windows-curses`
  is pulled in automatically by `pip install`.
- A terminal at least **100x30** (Windows Terminal's default). Below that, Delve shows a resize
  overlay and waits; it never degrades.
- **Ollama**, running, with a grader model pulled (e.g. `qwen2.5:3b`). A reachable local LLM
  grader is required to play at all (DELVE-0033): Delve checks it before curses starts and exits
  with a diagnosis rather than launching if it isn't reachable. See "Free-text answers" below.

## Install

macOS/Linux:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Windows (PowerShell):

```powershell
py -3.14 -m venv .venv
.venv\Scripts\pip.exe install -e ".[dev]"
```

### Windows notes

- **Skip `.venv\Scripts\activate` if PowerShell's script-signing policy blocks it** (a common
  "running scripts is disabled on this system" message). Rather than fight the policy, call the
  venv's executables directly throughout, as in the install command above and the play command
  below: `.venv\Scripts\python.exe`, `.venv\Scripts\pip.exe`.
- **If a bare `python -m delve` ever fails with `ModuleNotFoundError: No module named '_curses'`**
  even though `pip list` shows `windows-curses` installed, that means activation silently didn't
  take effect and `python` resolved to a different, non-venv interpreter. Use the full
  `.venv\Scripts\python.exe` path instead.
- **When editing text files by hand on Windows** (e.g. a stand-in `README.md` for a stripped-down
  distribution), don't use plain `>` redirection in PowerShell; it writes UTF-16 with a BOM by
  default, which `pip install`'s UTF-8 readers can't parse. Use
  `"..." | Out-File -Encoding utf8 file.txt` (or `-Encoding utf8NoBOM` on PowerShell 6+) instead.

## Play

```sh
python -m delve                        # macOS/Linux, from the repo root
.venv\Scripts\python.exe -m delve       # Windows (see "Windows notes" above)
./delve.sh                             # macOS/Linux, from any directory; also turns the free-text
                                        # grader on by default and starts/stops a local Ollama for
                                        # the run if needed
```

Delve asks *"Who are you?"* (your name owns your certificate collection; it is trust-based, not a
login), lets you pick a companion (a cat, a dog, or go it alone), offers to skip the orientation
floor if you have finished a training before, and offers to resume an unfinished run where you left
it. Then you are on Dlvl 0, the tutorial floor, which teaches the interface and can be walked out of
at any time.

Your companion moves on its own each turn. A **dog** fetches what lands on the floor, coins or any
object, and trots back to set it down beside you; a **cat** sweeps up coins and makes you catch it
by bumping into it. Either way, you consult it on a question with `?` (it rules an option out, at
the cost of that question's score).

Useful flags:

| Flag | Meaning |
|---|---|
| `--name <name>` | skip the "Who are you?" prompt |
| `--lang <en\|nl>` | play in English or Dutch; defaults to the system locale, falling back to English |
| `--seed <n>` | a specific dungeon layout, so a run is reproducible tile-for-tile |
| `--pack <dir>` | play a pack other than the bundled pilot (the folder holding `en/` and `nl/`) |
| `--grader-model <m>` | which local model grades free-text answers (default `qwen2.5:3b`); a reachable Ollama is required to play regardless (`delve doctor` checks it) |

### Keys

The tutorial teaches these, and the bottom line always names the keys that work right now.

| | |
|---|---|
| Move | `hjkl` or arrow keys (`yubn` for diagonals); `space` waits a turn (your pet still moves) |
| Talk to a keeper | `t`, or just walk into them (which, like a NetHack attack, costs a turn) |
| Read a lesson | `space` to turn the page, `-` to go back, `Esc` to put it down |
| Answer | type your answer for a free-text question; otherwise a number `1`–`n` (or a two-way question's labelled key), or the arrows to move the highlight and `Enter` to confirm |
| Objects | `,` pick up, `d` drop, `i` your pack (money banks itself when you step on it) |
| Recent messages | `p` (the last few lines, in case one scrolled past) |
| Ask your pet | `?` (narrows the options, at the cost of that question's score) |
| Rest | `s` (recover HP) |
| Stairs | `>` to descend, `<` to climb back |
| Quit | `q` (your place is saved) |

Running out of attempts pushes you back from a door; running out of HP wakes you at the floor
entrance with every earned door still open. Neither is death, and re-reading any passed lesson is
always free.

## Packs

Four packs ship in `packs/`, each in English and Dutch: `security-onboarding` (the pilot,
*The Caverns of Compliance*), `ethics-of-ai`, `holy-grail`, and `friends-nap-partners`. Check a
pack (both locales, structure, and capacity) before playing it:

```sh
python -m delve validate packs/security-onboarding
```

Writing your own pack is Markdown in a folder; see [docs/AUTHORING.md](docs/AUTHORING.md).

### Free-text answers (Phase 2)

A pack can ask a question you answer **in your own words** (a `- ?answer:` line, no checkboxes).
`freetext-demo` is a tiny bilingual pack that shows it off, and grades it on **meaning** with a
local model:

```sh
delve setup                     # pull the grader model and warm it up (needs Ollama)
delve doctor                    # report the grader's health; change nothing
python -m delve --pack packs/freetext-demo --grader-model qwen2.5:3b
```

The grader runs entirely on your machine, offline after the one-time model download; typed answers
never leave the device. **A reachable grader is required to play at all** (DELVE-0033): if Ollama
isn't running or the model isn't pulled, `delve` prints the same diagnosis `delve doctor` would and
exits, rather than starting a session on the keyword fallback alone. The keyword grader
(`KeywordGrader`) still exists underneath, but only as *mid-run* resilience: a single reply the
model answers with low confidence falls to it for that one verdict. See [docs/PHASE2.md](docs/PHASE2.md).

## Develop

```sh
./run-tests.sh                  # pytest, ruff (incl. S), pip-audit, screens, reqs, validate
./run-tests.sh -k tutorial -x   # any arguments go straight to pytest, for a focused loop
```

Security procedure for the gate: [docs/SECURITY.md](docs/SECURITY.md). The version scheme, the
architecture rules (the `session` core never touches curses; `ui` only paints), and the findings
that are expensive to relearn are all in [CLAUDE.md](CLAUDE.md).
