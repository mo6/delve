---
id: DELVE-0070
title: The ambient toast freezes its timeout while the player is idle, and is capped in length
status: implemented
area: [session, ui]
type: bug
epic:
effort: medium
milestone:
version: 1.26.6
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [pre-reset]
related: [DELVE-0060, DELVE-0061, DELVE-0064]
supersedes: []
docs: []
changelog: "1.26.6"
reason:
---

# The ambient toast freezes its timeout while the player is idle, and is capped in length

## Summary

Two related rough edges with the ambient room-entry toast (DELVE-0060): its time-out is driven by
turns taken, not wall-clock time or player attention, so a player who stops moving to actually
read a long passage can have it age out from under them mid-read; and the generated passage has
no hard length cap, so an overlong model reply (the prompt only *asks* for 2-3 sentences) can fill
the entire available panel height and still get cut off mid-sentence by `draw_toast`'s line limit,
which reads as a bug rather than a deliberately short flavour aside.

## Motivation / problem

- **Time-out should respect a frozen reader, not just count turns.** `_poll_toast` ages a toast
  out once `self.turn - self._toast_turn >= _TOAST_TTL` (8 turns). Turn count is a reasonable
  proxy for "has the player kept moving," but nothing currently distinguishes "the player kept
  playing while this toast happened to still be up" from "the player stopped to read it and hasn't
  moved since it appeared." A learner who freezes to read a longer passage can watch it vanish
  once `_TOAST_TTL` turns' worth of *game clock* (not their own reading time) has passed, even
  though they haven't taken a single further turn. The toast should stay up indefinitely while the
  player is not moving, and only start counting down again once they move.
- **No hard cap on toast length.** The backstory prompt (`session/backstory.py`) asks the model
  for "a very short (2-3 sentence)" passage, but nothing enforces that on the reply; a longer
  passage than that is entirely possible from the model, and today `draw_toast`
  (`ui/windows.py`) silently truncates to whatever fits in `max_lines`, cutting off mid-sentence
  with no indication anything was cut. A passage that fills the entire panel height reads as
  broken formatting to a learner, not as intentionally-brief ambient flavour.

## Stories

### As a learner, I want a toast I'm reading to stay up while I'm not moving, so that it never disappears out from under me mid-read.

- Given a toast is showing and the player has not moved since it appeared,
  when any number of turns' worth of wall-clock time passes with the player idle,
  then the toast remains visible; the time-out only begins counting once the player actually takes
  another turn (a move, a wait, or any other turn-consuming action) after the toast appeared.
- Given the player does move after the toast has been up for a few turns,
  when `_TOAST_TTL` turns have elapsed *since that first post-toast move*,
  then the toast ages out as before.

### As a learner, I want a generated ambient passage to stay within a firm length, so that it never spills past what the toast panel can show.

- Given the model's reply is longer than the intended firm cap,
  when the toast is built (`_poll_toast`'s call into the ambient runner, or wherever the resolved
  text is first handled),
  then the text is trimmed to the cap (at a sentence or word boundary, not mid-word) before ever
  reaching `draw_toast`, so the rendered toast never relies on `draw_toast`'s line-count truncation
  to hide an overlong reply.
- Given a reply that is already within the cap,
  when the toast is built,
  then it is shown unchanged.

## Non-goals

- No change to the backstory prompt's own instructions asking for a short passage; this issue adds
  an enforced backstop, not a prompt-engineering fix, since the prompt already asks for brevity and
  the model doesn't reliably comply.
- No change to `_TOAST_TTL`'s value (8 turns) or to the idle-nudge toast's own timing (DELVE-0061).
- No change to how a toast is dropped when an overlay opens, or when the player changes chapter
  (the existing "different room, same floor: still shown; different chapter: dropped" rules are
  unaffected).

## Design notes / links

- `_poll_toast`/`_toast_turn` (`session/run.py`) is where the age-out check lives; freezing the
  countdown while idle likely means recording the turn count *at the moment of the first move
  after the toast appeared*, not just at the toast's own creation, or equivalently comparing
  against whether `self.turn` has advanced since the toast appeared at all before applying the TTL
  arithmetic.
- The idle nudge (DELVE-0061) already has its own "never shown once the learner has actually
  moved, `self.turn != 0`" rule; this issue's freeze logic is a related but distinct check (it's
  about a toast already showing, not about whether to show the nudge at all).
- The length cap belongs on the resolved text before it becomes a `ToastView`, most likely in
  `_poll_toast` itself (or a small helper it calls) rather than in `ui/windows.py`, so the cap is a
  visible, testable session-side rule instead of an invisible rendering side effect. Truncation
  should respect `textwrap`'s `break_on_hyphens=False`/word-boundary rules already used elsewhere
  in the codebase (CLAUDE.md's "never break inside a URL/domain/code span" concern doesn't apply
  to prose, but breaking mid-word is still to be avoided).

## Acceptance / verification

- A test asserting a toast stays visible across many idle turns (`self.turn` unchanged) and only
  starts counting down once the player moves again.
- A test asserting an overlong ambient reply is trimmed to the cap at a clean word/sentence
  boundary before being shown.
- A test asserting a reply already within the cap is left unchanged.
- `./run-tests.sh` passes.
