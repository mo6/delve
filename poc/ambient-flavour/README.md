# PoC: LLM-generated ambient one-liners along a simulated game path

Two throwaway spikes measuring whether a local LLM can generate short ambient one-liners that read
as reacting to what actually just happened in a specific playthrough, not just a static
description of a room in the abstract:

- **`ambient.py` (DELVE-0048)**: per-room generation, grounded in that room's own prose plus a
  window of recent gameplay events.
- **`story.py` (DELVE-0049)**: the same idea extended into one continuous story for the whole
  pack, feeding every ambient line generated so far back into each later prompt (so an early
  detail can recur), a richer simulated path (a pet consult, a keeper brush-off, a rest, all real
  engine interactions), and explicit `en`/`nl` language control.

Both are **not** production code and are never wired into the shipping engine or the pack format,
the same discipline as `../llm-grader`: they deliberately ignore the five rules (a script opening
a socket directly, and reaching into `session`/`engine` internals a real feature never would)
because they are disposable evaluation code answering one question cheaply. `story.py` is a
separate file rather than an edit to `ambient.py`, so the two can be run side by side and compared.

## What `ambient.py` does

1. Loads a real pack (`delve.content.parser.load_pack`) and drives it through the same headless
   `RunState.apply(Command) -> Frame` harness the project's own tests use to play a whole run
   (the BFS walk/approach/pass-room helpers here are a trimmed copy of
   `tests/test_dungeon.py`'s, since `tests/` isn't a package this can import from).
2. While walking, it folds every message line the player would actually see (a keeper's brush-off,
   "Correct.", a dog trotting back with a fetched item, a reward paid out) into a running event
   log.
3. At each room, it builds one prompt combining that room's (and its chapter's, and its pack's)
   own authored prose with a window of the most recent events, and asks the model for 10-20 short
   ambient one-liners.

## What `story.py` adds

1. **Continuity**: every generated ambient line, across the whole pack, is kept in a running
   `ambient_log` and included in *every later prompt* (not just the recent gameplay window), with
   an instruction that the model may bring an earlier detail back but doesn't have to.
   `--ambient-window <n>` caps how much of that log is fed back; `0` means all of it (default `24`,
   see "Early observations" for why unbounded is a bad idea).
2. **A richer simulated path**: beyond walk/talk/answer/pass, the run now demonstrates one pet
   `Consult()` (on the first eligible non-freetext question), one brush-off bump into an
   already-passed keeper, and one `Rest()` per chapter, each a real `Command` the engine already
   supports, toggle with `--consult-demo`/`--brushoff-demo`/`--rest-demo` (`--no-...` to disable).
3. **Explicit language**: `--lang nl` now also loads `delve.strings.load("nl")` into the run (so
   engine messages actually render in Dutch, not just the pack prose) and tells the model
   explicitly which language to reply in.
4. **One trail, not per-room blocks**: output is a single ordered transcript, gameplay lines and
   generated ambient lines interleaved exactly in the order they happened, `--tag`/`--no-tag` to
   show or hide which is which, `--out <file>` to also save it to a plain text file.
5. **(DELVE-0050) One line at a time, not a batch.** Instead of a 10-20 line dump once per room,
   `story.py` now generates exactly one line (`--count` still exists, default `1`) at two triggers:
   arriving at a room (grounded in that room specifically), and every `--step-interval` simulated
   steps while walking between rooms (default `5`, grounded in the current floor generically, since
   there's no single room to ground it in between keepers, `_static_context`'s corridor fallback).
   `--room <id>` now means "stop the walk once this room is reached," since generation is
   continuous rather than gated per room.

## Files

| File | What |
|---|---|
| `ambient.py` | DELVE-0048: per-room generation, BFS walk, event log, Ollama call, CLI |
| `story.py` | DELVE-0049/0050: continuity, a richer path, locale, one trail, one line at a time |
| `README.md` | this file |

## Run it

Needs Ollama running locally with a model pulled (`ollama pull qwen2.5:3b`, the project default).

```sh
python ambient.py                              # walk the whole pilot pack, every room
python ambient.py --room phishing --count 8     # just one room, fewer lines, fast iteration
python ambient.py --pet none                    # compare against a run with no pet events at all

python story.py                                 # the whole pack as one continuous story
python story.py --lang nl                       # the same, in Dutch, engine strings included
python story.py --out /tmp/trail.txt --no-tag    # save a plain-text transcript
python story.py --room phishing                 # stop after this room instead of the whole pack
python story.py --step-interval 8               # a sparser walking cadence
python story.py --ambient-window 0              # feed back the whole story so far (see findings)
```

Useful flags shared by both: `--pack <dir>` (any pack holding `en/`/`nl/`), `--lang en|nl`,
`--seed <n>`, `--pet cat|dog|none`, `--window <n>` (how many recent gameplay events to feed back;
`0` = the whole log), `--temperature <f>` (generation isn't judgement, so this defaults to `0.9`,
unlike the production grader's pinned `0`), `--grader-model`/`--grader-host`. `story.py` adds
`--ambient-window`, `--step-interval`, `--tag`/`--no-tag`,
`--consult-demo`/`--brushoff-demo`/`--rest-demo`, `--out`.

## What to look for (DELVE-0048/DELVE-0049's acceptance criteria)

- Does a room's batch read as grounded in that room's own prose, not generic dungeon flavour?
- Run the same room via two different paths (e.g. `--pet dog` vs. `--pet none`, or `--room` after
  different amounts of prior play) and compare: does the output visibly differ in a way that
  reflects what actually happened, or does it read the same regardless of context?
- With `story.py`: does a detail invented early (a sound, an object) actually recur later, and
  does the whole pack read as one accreting place rather than twelve disconnected vignettes?
- Run the same room+path twice: is the phrasing repetitive or format-broken across runs?
- Rough timing is printed per room (seconds per generation call); no cross-machine benchmark is
  the point here (see DELVE-0047 for that shape applied to grading), but it's worth noting if a
  room's generation ever feels slow enough to matter.

## Early observations

**`ambient.py`**: a pass against `packs/security-onboarding/en`'s first room (`phishing`), same
room and same prior path, differing only in whether the pet was a dog or none, produced visibly
different output: the dog run's log included "your dog snatches up a urgent memo," and its batch
leaned toward small creature/object detail near the pickup; the no-pet run's batch instead leaned
on ambient office texture (fluorescent lights, a ringing phone, dust). Both stayed on-voice for the
room (dust, toner, old paper, Ada's letter) rather than drifting into generic fantasy-dungeon
flavour. Generation took 2-4s per 8-line batch on the macOS dev machine (Apple M5), well within
the latency already judged acceptable for grading (DELVE-0046).

**`story.py`**: continuity works over a short run (see the `phishing`-room dog/no-pet comparison
above, which still holds), but degrades over a **full 12-room pack walk** regardless of how much
ambient history is fed back, `qwen2.5:3b`, temperature `0.9`. Five `--ambient-window` values were
tried against the whole pilot pack (`0` = unbounded/all, `100`, `20`, `12`, `6`), and every one
showed the same underlying problem, only differing in degree:

- **`0` (unbounded, ~150-180 lines by the last chapter)**: batches for consecutive rooms became
  near-identical by the third chapter, and by the fourth the model drifted into replying in
  **Chinese entirely**, ignoring the explicit "reply in English" instruction. Likely cause: the
  prompt grows large and self-similar, and a 3B model under a non-zero temperature loses the
  instruction under that much repeated context.
- **`100`, `20`, `12`, `6` all avoided the language drift** (stayed in English the whole walk), but
  every one converged onto the same failure: a small set of recurring images repeated with only
  light rewording room after room ("Ada taps the letter softly," "a spider pauses mid-hop," "an
  old key rattles") **and, worse, cross-chapter bleed-through**: Ada and Grigor, two keepers from
  the *first* chapter (the Sorting Office), kept reappearing in ambient lines generated for rooms
  in the Archive and the Watchpost, two and three chapters later, with no in-fiction reason they'd
  be there. This happened at every window size tested, including the smallest (`6`).
- **Conclusion: window size alone bounds prompt growth and prevents the language-drift failure,
  but does not fix cross-chapter bleed-through.** The mechanism as built (a flat list of every
  ambient line generated so far, with no indication of *where* each one happened) gives the model
  no way to know a detail belongs to a different room and shouldn't recur elsewhere. Fixing that
  properly likely needs scoping (reset or heavily discount the ambient log at a chapter boundary,
  or tag each entry with the chapter/room it came from and instruct the model accordingly) rather
  than a window-size number; that scoping work is not yet built. The default was set to `24` as a
  reasonable middle ground (bounded, avoids the worst repetition seen at `100`/unbounded) but this
  is a stopgap, not a fix for the bleed-through finding above.

**DELVE-0050 (one line at a time)**: the room-entry and step-tick triggers both work mechanically
(verified: entering `phishing` fires exactly one line; a corridor walk between rooms fires one
every `--step-interval` steps, correctly grounded in the corridor fallback when no specific room
applies). But the cadence change makes the DELVE-0049 lock-in problem **markedly worse**, not
better, at every `--ambient-window` tried (default `24`, and a much tighter `4`):

- At `--ambient-window 24` (the default), a full pack walk fixated on a single image, "Ada's voice
  hums softly, stirring the last lingering dust motes...", from partway through chapter 2 onward,
  and repeated it with only cosmetic noun-swaps ("crystalline formations" -> "frost flowers" ->
  "ice spikes" -> "crystalline shards"...) for the rest of the run, well into chapters 3 and 4,
  the same cross-chapter bleed-through as DELVE-0049 but now as a single obsessive motif rather
  than a rotating handful of images.
- At `--ambient-window 4` (tried specifically to see if a tighter cap would help), the effect got
  worse still: the model locked onto one line, "Toner fumes swirl, ink stains shift under the cold
  draft.", and repeated it **verbatim, unchanged**, dozens of times through the rest of the pack,
  with no rewording at all.
- Likely cause: at one line per call, the "ambient details already established" list the model
  sees is now dominated by its own immediately-preceding output (since calls happen every ~5 steps
  rather than once per room), so each call is effectively being asked "continue what you just
  said" rather than "here is a spread of prior context, write something new." A smaller window
  makes this worse, not better, because it removes what little variety a longer history provided.
- **This is the opposite of what the smaller cadence was expected to fix.** The batch-mode
  convergence in DELVE-0049 was already a problem; per-line generation with the same flat
  continuity mechanism turns it into near-total fixation. This strongly suggests the continuity
  mechanism itself (a flat list of every prior ambient line, fed back verbatim) is the wrong shape
  for this cadence, not just a tuning problem; a fix would likely need either far less frequent
  continuity injection (e.g. only remind the model of the single most-recent *room-entry* line, not
  every step-tick line), explicit "don't just reword your last line" instruction, or dropping
  continuity for step-tick generations entirely and reserving it for room-entry lines only. None of
  that is built; this is a documented finding, not a fix.
