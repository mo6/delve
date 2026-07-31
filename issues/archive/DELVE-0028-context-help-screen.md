---
id: DELVE-0028
title: A context-sensitive help screen on ? with Keys and Objectives tabs
status: implemented
area: [session, ui, delve, docs, assess]
type: feature
epic:
effort: high
milestone:
version: 1.22.0
version_span:
created: 2026-07-25
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [7c334a6]
related: [DELVE-0018, DELVE-0013, DELVE-0035, DELVE-0040, DELVE-0041, DELVE-0055, DELVE-0033]
supersedes: []
docs: [docs/SCREENS.md, docs/PLAN.md]
changelog: "1.22.0"
---

# A context-sensitive help screen on ? with Keys and Objectives tabs

## Summary

Add a help overlay, opened with `?`, drawn as its own tabbed panel using the same tab-strip and
pager chrome the `i` Info panel already established (DELVE-0035/DELVE-0040/DELVE-0041), but kept as
a distinct `HelpView` rather than folded into `InfoView`: `i` is "what has happened in my run" (pack
listing, progress, grader status), `?` is "how do I play right now", and the two stay conceptually
separate even though they share the tab/pager machinery. Two tabs:

- **Keys**: the context-sensitive command list from the original scope of this issue, every key
  the learner can press right now (walking, in a lesson, sitting an examination, in the backpack),
  each with a short localised explanation, read from a single command catalogue.
- **Objectives**: a static summary of the pack and the current chapter derived from content that
  already exists (titles, room/keeper names, gate/pass criteria), so no new pack frontmatter is
  required; optionally followed by a short block of LLM-generated scene-setting prose that adds
  time-of-day/day-of-week flavour on top of the static facts. The LLM block is a pure enhancement:
  when no grader model is reachable, or the call fails or times out, Objectives still renders in
  full from static content alone, with no error shown to the learner.

Because `?` is currently the pet-consult key inside a question, that binding moves so `?` can mean
help everywhere (unchanged from the original scope; see the last story below).

## Motivation / problem

Delve is played once by people who are not developers and who may skip the (honest, free) tutorial,
so discoverability is the safety net (CLAUDE.md, "The hint line is not decoration"). The hint line
does real work but is one line: it shows the few most relevant keys and cannot explain them or list
the rest. There is no way today to ask "what can I press here, and what does it do?", nor "what is
this pack even about, and what am I working toward?" A `?` help screen answers both: Keys gives the
original per-context command reference, and Objectives gives the orienting context a learner who
skipped the tutorial and jumped into the middle of a pack currently has no way to see. The optional
LLM prose is a small, low-cost way to make that orientation feel like part of the dungeon's voice
rather than a dry status readout, in the same spirit as the flavour-emoji pass on question prompts
(`session/flavour.py`), without making play depend on it.

## Stories

### As a learner, I want to press `?` and see the keys I can use right now, each explained, so that I can discover commands without the tutorial.

- Given the learner is walking the dungeon,
  when they press `?`,
  then a help overlay opens on the Keys tab listing the walking commands (move, wait, talk, stairs,
  pick up, drop, inventory, message log, rest, quit, and `?` itself), each with a one-line
  explanation in the run's language.
- Given the help overlay is open,
  when the learner presses `?` again or Esc,
  then it closes and returns them to exactly where they were, having cost no turn (help is free,
  like re-reading a lesson).
- Given the message log on `p`,
  when the learner opens help while walking,
  then `p` is listed and explained (the example that motivated this), so it is discoverable.

### As a learner, I want the Keys tab to match my context, so that a lesson, an exam, and the backpack each show their own keys.

- Given a lesson panel is open,
  when the learner presses `?`,
  then Keys lists the lesson keys (page forward, page back, dismiss), not the walking keys.
- Given an examination question is shown,
  when the learner presses `?`,
  then Keys lists the answering keys (the number or two-way keys, ask-the-companion, put-it-down)
  and any exam actions in play, not the walking keys.
- Given the backpack, the drop menu, or the drop-amount field is open,
  when the learner presses `?`,
  then Keys lists that panel's keys.
- Given a context in which a command is conditionally available (the stairs only on a stair tile,
  talk only beside a keeper),
  when help is shown,
  then it reflects what is actually pressable now, consistent with what the hint line already
  decides.

### As a learner, I want an Objectives tab that tells me about the pack and my current goal, so that I have orienting context even if I skipped the tutorial or joined mid-pack.

- Given the help overlay is open,
  when the learner switches to the Objectives tab (arrow keys move the tab focus, matching the `i`
  panel's tab-strip convention),
  then it shows the pack's title, the current chapter's title and position (`Dlvl N of M`), the
  current room/keeper's name, and what passing that room's gate requires, all assembled from data
  the engine already has (no new pack frontmatter).
- Given the learner has already earned some gates in the current chapter,
  when Objectives is shown,
  then it lists rooms done vs. total for the chapter, consistent with the status line's
  `rooms_done`/`rooms_total`.
- Given no LLM grader model is reachable, or the LLM call fails or times out,
  when Objectives is shown,
  then the static summary above still renders in full, with no error message, no delay beyond a
  bounded short timeout, and no indication to the learner that anything was attempted and skipped.

### As a learner, I want a short scene-setting passage on the Objectives tab that reflects the time of day and day of week, so that the orientation feels like part of the dungeon rather than a status dump.

- Given a grader model is reachable and the current run has not yet generated one,
  when the learner first opens the Objectives tab this run,
  then the engine sends one prompt built from the static Objectives facts plus the current
  time-of-day (morning/afternoon/evening/night) and day-of-week, and renders the model's short
  prose reply beneath the static summary.
- Given that prose has already been generated once this run,
  when the learner reopens Objectives (in the same sitting or a later one this run, including
  after a resume),
  then the same cached prose is shown again, unchanged, rather than calling the model again; the
  cached text is part of the run's persisted state so it survives resume like other run data.
- Given the LLM call is in flight,
  when the learner is looking at Objectives,
  then the static summary is shown immediately and the prose block appears once ready, or is
  simply absent if the call fails; the learner is never blocked waiting on it (same non-blocking
  shape as `ThreadedGrader`/`GradeReady`, `session/grading.py`).
- Given the prose call happens at all,
  when it is built,
  then it never touches exam content or grading (rule 1's boundary): it is descriptive dungeon
  flavour, not a question, an answer, or a score, and a failure here can never affect `room_results`
  or HP.

### As a learner, I want the help overlay to page and dismiss like other panels, so that it stays readable as the command set grows.

- Given more Keys entries than fit the panel at 100x30,
  when the help overlay is shown,
  then it paginates with the same pager chrome as a lesson and the `i` panel (more/end labels, page
  counter), breaking between whole entries, never mid-entry.
- Given the help overlay,
  when it is drawn,
  then it is a panel beside or over the map like other overlays, never a full-screen takeover that
  loses the room, and it obeys the 100x30 minimum.

### As a maintainer, I want commands defined in one catalogue that the help and the keymap agree on, so that adding a command surfaces in help without editing scattered code.

- Given a single command catalogue that pairs each command with its key label, a localised
  description, and the contexts it is active in,
  when a new command is added,
  then adding one catalogue entry (plus its `en`/`nl` strings and its `keys.py` binding) is enough
  for it to appear in the right context's Keys tab, with no other help code to touch.
- Given the catalogue and the `ui/keys.py` keymap are separate (rule 2 keeps key bindings in `ui` and
  descriptions in `session`),
  when the test suite runs,
  then a test asserts the two do not drift: every key the catalogue documents for a context is bound
  in `keys.py`, and every binding a learner can reach is documented, so Keys can never silently omit
  or invent a key.

### As a learner, I want `?` to always mean help, so that it is predictable; the pet consult moves to its own key.

- Given `?` currently asks the companion inside a question (`panel_command` returns `Consult`),
  when this feature ships,
  then `?` opens help in that context too, and the pet consult is rebound to `@`, advertised in the
  question hint and the question's Keys entry.
- Given the rebinding,
  when the learner opens help on a question,
  then both `@` (ask the companion) and `?` (help) are listed, so the change is self-documenting.

### As a pack author or learner in either language, I want the help in my language, so that it is as translated as the rest.

- Given the run locale is `nl`,
  when help is shown,
  then every Keys description and every static Objectives label is Dutch (tutoyeer, sentence case),
  drawn from `delve/strings/nl.toml`, with the same set of entries as `en` (complete or absent, per
  CLAUDE.md).
- Given the LLM prose block,
  when the run locale is `nl`,
  then the prompt asks the model to reply in Dutch and the block is simply omitted (falling back to
  static-only Objectives) if the reply cannot be produced, rather than showing English prose in a
  Dutch run.

## Non-goals

- Rebindable keys or a settings screen. The keymap stays fixed; Keys only *documents* it.
- Mouse or clickable help. Keyboard only, like the rest of the game.
- Replacing the tutorial floor. The tutorial still teaches the interface by playing it; help is the
  on-demand reference, and the tutorial may point at `?`.
- Rewriting the one-line hint to derive from the new catalogue. That unification is a reasonable
  follow-up and the catalogue is designed to allow it, but this feature does not require changing
  `_hint()`; the hint line and the Keys tab may share the catalogue or coexist.
- A searchable or full-text manual, command history, or context beyond the keymap.
- New pack frontmatter for author-written descriptions, goals, or hints. Objectives is derived
  entirely from existing engine/pack data plus optional LLM prose; a richer author-authored
  Objectives tab (pack-level `description`/`goals` fields) is a reasonable future story but out of
  scope here, so as not to couple a UI feature to a pack-format change.
- Folding Keys and Objectives into the `i` Info panel's own tab set. They share the tab-strip/pager
  *mechanism* (a second `View` type using the same UI drawing code), not the panel or its `i` key.
- Gating Objectives' LLM prose behind `delve.doctor.ensure_ready` the way grading is gated
  (DELVE-0033). Play must never require a model just to see `?`.

## Design notes / links

Rule 2 is the shaping constraint: `ui/keys.py` owns key -> Command, `session` builds the `Frame`,
and `ui` never imports the strings catalogue. So Keys content is a **session-side command
catalogue**: a table whose entries carry a key label (a display glyph such as `?`, `p`, `hjkl`), a
description string id resolved through `Strings`, and the set of contexts the command is active in.
The contexts are the ones `_hint()` already switches on (`_overlay_kind` of lesson/explanation/
question/grading/scroll/inventory/drop_menu/drop_amount/repelled, plus walking), so Keys and the
hint line share one taxonomy.

`HelpView` is a new dataclass in `session/views.py`, sibling to `InfoView` rather than a variant of
it: same shape (a tab strip of two entries, `active` index, paginated `body: list[TextBlock]`, the
same `more_label`/`end_label`/`page_fmt` chrome), reusing `ui/windows.py`'s existing pager drawing
code (the same function that draws `InfoView`'s body can take a `HelpView`'s, or a shared helper
factored out of both), but a distinct type so a test asserting on a `Frame` can tell "the learner
asked how to play" from "the learner asked what's in my run" without inspecting tab labels. A new
`Help()` command and a `?` binding in both `walk_command` and `panel_command` open it; Esc or `?`
dismisses via the existing `Dismiss`. Arrow-key tab focus follows the same convention DELVE-0056
gave the Info panel's tab strip.

Objectives' static half reads data `session/run.py` already holds: pack/chapter titles, the current
room's keeper name and gate requirement, `rooms_done`/`rooms_total` per chapter (the same figures
`StatusView` already exposes). No new pack-format fields, no schema change, no `docs/AUTHORING.md`
update.

Objectives' LLM half is a new, narrow use of the existing `assess/llm.py` socket seam
(`OllamaClient`), but it must not be routed through `LLMGrader` or anything in `assess/grader.py`:
this is prose generation, not grading, and must never touch `room_results` or HP even on total
failure (rule 1's spirit: keep the training seam pure). A small new function (candidate home:
`session/flavour.py`, which already does deterministic-but-decorative text, or a new
`session/backstory.py` if that module's RNG-seeded, non-LLM nature shouldn't mix with a networked
call) builds one prompt from the static Objectives facts plus `datetime.now()`'s time-of-day bucket
and weekday name, calls `OllamaClient.chat` off a background thread the same non-blocking way
`ThreadedGrader` already does (`session/grading.py`'s `GradeReady` poll pattern), and caches the
result once per run. The cache lives on `RunState` and is part of the snapshot (`session/
snapshot.py`), so a resumed run shows the same prose rather than regenerating it, and so a fresh run
regenerates (new day, new time bucket, worth reflecting). `LLMUnavailable` (transport, timeout, or
empty reply) is caught at this new call site and simply means "no prose block this run"; it must
never surface as a visible error and must never be confused with `LLMGrader`'s keyword-fallback
path, which is a different concern (grading quality, not flavour text).

The `?` collision, key labels, and drift-guard test are unchanged from the original scope: `?`
reclaimed for help, pet consult moves to `@` (coordinate with DELVE-0018's proposed `$` in the same
question-panel keymap), ripple to `keys.py`, `[hint]` strings `answer_two`/`answer_many`, both
locales of `delve/tutorial/` (grep for `?`, per CLAUDE.md), and `docs/SCREENS.md` (regenerate with
`tools/screens.py`, never hand-edit; add a help-overlay mock-up showing both tabs).

Locale impact: new `[help]` entries in `delve/strings/{en,nl}.toml` for Keys descriptions and
Objectives' static labels, one description per command/label, both locales, same set. No `[format]`
change. The hint line should also advertise `?` so the door to help is itself discoverable (append a
`?:help` prompt, at least in the walking hint). Design pointers: `docs/PLAN.md` (the hint line and
interface rationale), `docs/SCREENS.md` (the panel/pager conventions this reuses), `docs/PHASE2.md`
(the LLM socket seam and its non-blocking pattern).

## Acceptance / verification

- A help test drives `?` in the walking context headlessly and asserts the returned `Frame` carries
  a `HelpView` on the Keys tab listing the walking commands including `p` with its explanation, and
  that a second `?` or Esc dismisses it having spent no turn.
- Context tests assert `?` in a lesson, a question, and the backpack each yield a `HelpView` whose
  Keys entries are that context's keys, not the walking set, and that conditional entries (stairs,
  talk) appear only when actually pressable.
- A pagination test builds a context with more Keys entries than fit and asserts the help paginates
  with the same pager chrome as the `i` panel, breaking between entries.
- A drift test imports `ui.keys` and the command catalogue and asserts they agree in both directions
  for every context (no documented-but-unbound key, no reachable-but-undocumented key).
- An Objectives test asserts the static tab renders pack/chapter/room/gate/progress facts matching
  what `StatusView` and the current room already report, with a fake `OllamaClient` returning
  `LLMUnavailable`, and asserts no error surfaces and no prose block appears.
- An Objectives-with-LLM test asserts a fake client's reply appears as a prose block, that a second
  `?` open the same run does not call the fake client again (cache hit), and that the cached prose
  round-trips through a snapshot save/resume unchanged.
- A rebinding test asserts `?` on a question returns `Help`, the pet consult is reachable on `@` and
  still costs the question its score (unchanged from DELVE-0011), and the question hint offers `@`
  for consult rather than `?`.
- A locale test asserts help renders in `nl` with the same Keys/Objectives entry set as `en`, and
  that a `nl` run's LLM prompt asks for Dutch prose.
- `./run-tests.sh` passes (pytest, ruff, `tools/screens.py --check` with the new help mock-up,
  `tools/issues.py --check`, `delve validate`), and `delve/tutorial/` is re-checked in both locales
  for any `?` reference.
