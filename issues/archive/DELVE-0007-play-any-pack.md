---
id: DELVE-0007
title: "Play any pack (--pack, --lang)"
status: implemented
area: [session, delve, ui]
milestone:
version: 0.5.1
created: 2026-07-18
updated: 2026-07-18
commits: [87d9a4e]
related: [DELVE-0003, DELVE-0008]
supersedes: []
docs: [docs/PLAN.md]
changelog: "0.5.1"
---

# Play any pack (--pack, --lang)

## Summary

Let the game play any pack directory, not just the pilot, and choose the locale for both the
pack content and the engine strings from one flag.

## Motivation / problem

Packs are the portable asset. If the engine can only play the one bundled pack, authoring a
new one is untestable. A single locale switch must cover content and chrome together, or a
Dutch reader gets an English status line.

## Requirements

1. `delve --pack <dir>` MUST play an arbitrary valid pack directory.
2. `--lang <locale>` MUST select the locale for both the pack content and the engine strings.
3. `--lang` MUST default to the system locale read from `$LANG`/`$LC_*` (never
   `locale.setlocale`) and fall back to `en`.
4. A pack MUST be validated on load; an invalid or non-directory pack path MUST fail with a
   clean error, not a traceback.

## Non-goals

- Pack distribution as archives (open question 2); packs stay folders for now.
- The tutorial floor bundling (DELVE-0008).

## Design notes / links

`--lang` semantics and the `$LANG`/`$LC_*` rule are in `CLAUDE.md` (Languages). The launcher
`delve.sh` passes args through verbatim.

## Acceptance / verification

- `./delve.sh --pack ./packs/<any> --lang nl` starts that pack in Dutch.
- `delve validate` on a bad path prints a clean error (45491c6 covered the non-directory case).
