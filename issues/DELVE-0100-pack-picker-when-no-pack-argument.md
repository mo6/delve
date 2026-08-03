---
id: DELVE-0100
title: Offer a pack picker, list-plus-description like Info/Pack, when no --pack is given
status: proposed
area: [delve, ui, session, content]
type: feature
epic:
effort: medium
milestone:
version:
version_span:
created: 2026-08-03
updated: 2026-08-03
accepted_by:
accepted_at:
commits: []
related: [DELVE-0075]
supersedes: []
docs: [docs/PLAN.md]
changelog:
reason:
---

# Offer a pack picker, list-plus-description like Info/Pack, when no --pack is given

## Summary

Running `delve` (or `python -m delve`) without `--pack` today silently loads the pilot pack
(`packs/security-onboarding`), the only one of the shipped packs (`packs/holy-grail`,
`friends-nap-partners`, `ethics-of-ai`, `freetext-demo`, `security-onboarding`) a learner ever sees
unless they already know to pass `--pack <path>`. Instead, when `--pack` is omitted, show an
interactive picker before play starts: every pack under `packs/` in a left column by title, the
focused one's own description in the right column, arrow keys to move focus, Enter to choose,
matching the Info/Pack tab's own list-plus-description layout and its arrow-key row focus
(DELVE-0075).

## Motivation / problem

`_play` (`delve/__main__.py:113`) resolves the pack before curses ever starts: `args.pack is None`
unconditionally calls `launch.load_pilot(lang)`, so `packs/security-onboarding` is the only pack a
learner ever reaches without already knowing another pack's directory name to pass on the command
line. The other shipped packs are otherwise invisible; a learner (or a maintainer demoing Delve)
has no way to discover what else is available short of reading the repository's `packs/` directory
themselves. A picker, shown only when the caller did not already say which pack they want, fixes
the discovery gap without changing anything for a caller who already knows what they want to play.

## Stories

### As a learner or maintainer starting `delve` with no --pack, I want to see and choose from every available pack, so that I'm not stuck with whichever one happens to be the default.

- Given `packs/` ships more than one pack directory,
  when `delve` is launched with no `--pack` argument,
  then a picker screen appears before any name/resume/tutorial prompt, listing each pack's title
  in a left column and the focused pack's own intro text in a right column, laid out like the
  Info/Pack tab's list-plus-description columns (`ui/windows.py:_draw_pack_columns`): a vertical
  divider, the focused row highlighted as a full-width bar, the description wrapped in its own
  column.
- Given the picker is showing,
  when the learner presses the up/down arrow keys,
  then focus moves to the previous/next pack in the list and the description column updates to
  match, with no confirm step (the same "both panes always current" feel as Info/Pack).
- Given a pack is focused,
  when the learner presses Enter,
  then that pack is chosen and play proceeds exactly as if `--pack <that pack's directory>` had
  been passed on the command line (same locale resolution, same tutorial floor, same grader gate).

### As a maintainer who already knows which pack they want, I want --pack to skip the picker entirely, so that scripted or repeat launches are unaffected.

- Given `--pack <path>` is passed explicitly,
  when `delve` is launched,
  then no picker appears; behaviour is unchanged from today (that pack loads directly, or a
  malformed/missing pack still prints the existing clean `delve: cannot load pack: ...` message
  and exits before curses starts).

### As a learner, I want to back out of the picker, so that I'm not forced to start a run I didn't mean to.

- Given the picker is showing,
  when the learner presses Esc,
  then `delve` exits cleanly (return code 0), no run started, no error printed.

## Non-goals

- Not discovering packs outside the shipped `packs/` tree; an explicit `--pack /some/other/path`
  still works exactly as today and is never listed alongside the discovered ones.
- Not auto-selecting or skipping the picker when only one pack happens to exist under `packs/`;
  the picker always shows when `--pack` is omitted, regardless of count, so behaviour does not
  change quietly if packs are added or removed later.
- Not a search/filter box, favourites, or remembering the last-played pack; a plain list is enough
  for the handful of packs Delve ships.
- Not changing `ui.app.main`'s existing contract of receiving an already-loaded `Pack` (rule 2,
  PackError handling stays outside curses); see Design notes for how the picker fits around that,
  not through it.

## Design notes / links

- Today `_play` (`delve/__main__.py:113`) loads the pack fully before `ui_main` (and therefore
  curses) ever starts, deliberately (the comment at line 107: "so a malformed or missing pack
  prints a clean message and never reaches curses"). An interactive, arrow-key picker needs curses
  running before a pack is chosen, so the cleanest seam is a *separate*, short-lived
  `curses.wrapper` call for the picker alone, run from `_play` when `args.pack is None`, before
  `load_pilot`/`load_pack_dir`: it returns a chosen pack directory path (or `None` on Esc), and the
  existing `load_pack_dir(path, lang)` / `PackError` handling then runs exactly as today, still
  outside the main game's own curses session. This keeps `ui.app.main`'s contract (a resolved
  `Pack` in, PackError caught before curses) completely unchanged; only `_play` grows a step.
- New discovery helper, alongside `load_pilot`/`load_pack_dir` in `delve/session/launch.py`: list
  the immediate subdirectories of the `packs/` root (`PILOT_PACK.parent`) that look like a pack
  (reuse `content/parser.py:locale_dirs`'s own "has a `pack.md`" test on at least one locale
  subdirectory), and for each, load its `title` and `intro` for the resolved `lang` (falling back
  to `en` if the pack has no `nl` tree, same as `load_pack` does elsewhere). Skip, rather than
  crash the picker on, any directory that fails to parse.
- New picker screen in `delve/ui/app.py`, alongside `_ask_yn`/`_pick_companion`'s own small curses
  routines: renders via the same column primitives `_draw_pack_columns` uses (`PACK_LIST_W`,
  `PACK_DESC_W`, the `bar_attr` highlight, `_blocks` wrapping for the description), reusing that
  drawing code directly if it can be lifted out of its `InfoView`/`RunState` coupling without
  disturbing the in-run Pack tab, or a small dedicated routine that matches it visually if not;
  either way the two must look the same (same column widths, same highlight, same divider) since
  that visual match is the point of this issue.
- A pack's `intro` (`Pack.intro`, the dungeon's opening screen prose, e.g. `packs/holy-grail/en/pack.md`'s
  "Somewhere under England there is a dungeon...") is the natural per-pack blurb already authored
  for every pack; reuse it as the description column's text rather than inventing a second,
  separate summary field.
- docs/PLAN.md section 8 ("Languages") and the CLI usage table in README.md both describe a bare
  `delve`/`python -m delve` launch; update README's quick-start prose with a one-line mention that
  omitting `--pack` now offers a choice, so it doesn't read as still defaulting straight to the
  pilot.

## Acceptance / verification

- A `__main__`-level test (in the style of `tests/test_main.py`'s existing `ui.app.main` stub)
  asserting that with `args.pack is None`, a picker function is invoked before `load_pack_dir`/
  `load_pilot`, and that its returned path feeds into pack loading exactly as an explicit `--pack`
  value would; and a second test asserting that with `--pack` given explicitly, the picker is never
  invoked at all.
- A discovery-level test asserting the new `launch` helper lists every directory under `packs/`
  that has a valid locale tree, with each entry's title and intro text matching what `load_pack`
  itself would resolve for a given locale, and that a malformed pack directory is skipped rather
  than raising.
- A picker-level test (curses-fake, in the style of `tests/test_app.py`) asserting arrow keys move
  the focused row, Enter returns that row's pack path, and Esc returns `None`/exits without
  starting a run.
- `./run-tests.sh` green, both locales; `./tools.sh screenshot` scenarios for the existing Info/Pack
  tab unaffected (no shared rendering code broken by extracting/reusing the column-drawing helper).
