# Changelog

All notable changes to Delve, newest first. Dates are the release date.

From 1.0.0 on the scheme is ordinary semver (`MAJOR.MINOR.PATCH`); the pre-1.0
scheme was `0.<milestone>.<patch>`.

## [1.34.0] — 2026-08-02

- **Retire checked-in screen mock-ups for an on-demand screenshot tool** (DELVE-0092, story, ui/tools/docs): `docs/SCREENS.md` and `tools/screens.py` are gone. `./tools.sh screenshot <scenario>` drives a real `RunState` through the real `delve.ui` renderer onto a shared headless `CursesEmu` (`tools/_fakescreen.py`, also used by render tests) and prints the 100x30 frame with ANSI colour from the same `attrs.py` pair map the live game uses (`NO_COLOR` / non-tty stay plain). `./tools.sh screenshot` with no name lists scenarios; `--all` prints every one in a single pass. Rooms paint with real box-drawing glyphs by default (`enable_fake_acs`, matching `curses.ACS_*`'s real terminal look, which needs `curses.initscr()` and is never available headlessly); `--ascii-walls` shows the raw ASCII fallback on demand. `CursesEmu` correctly drops a wide glyph's phantom trailing column (an emoji title no longer leaves a real terminal's border one column off) rather than reproducing it as an extra printable space. The `screens --check` step leaves `run-tests.sh`; process docs (AGENTS, AGILE, TEMPLATE, tools README) point screen impact at the new tool instead. `infoscreen_mockups.py` keeps its hand-drawn geometry helpers in `tools/_ascii_mock.py` for not-yet-built UI.

## [1.33.1] — 2026-08-02

- **The toast-loading spinner steps one adjacent glyph per redraw** (DELVE-0093, bug, ui): `_TOAST_POLL_MS` (300) and `_SPINNER_MS` (120) were not multiples of each other, so idle redraws while a toast was generating sampled the braille orbit mid-cycle and the empty dot hopped non-adjacent most of the time. `_TOAST_POLL_MS` is now derived from `windows._SPINNER_MS` (120, the same cadence as `_GRADE_POLL_MS`), and a pure `_spinner_glyph` helper plus tests assert both the divisibility relationship and that consecutive poll-spaced samples are adjacent in the cell's missing-dot grid.

## [1.33.0] — 2026-08-01

- **Spend gold to eliminate a wrong MCQ option, priced against the room reward** (DELVE-0018, story, assess/session/ui): during a multiple-choice question with three or more options still showing, `$` buys a removal at `round(R / (n - 1))` where `R` is the room's reward basis (same resolution as `_pay_reward`) and `n` is the still-standing count, so a four-option room at `R=100` costs 33 then 50 and refuses a third buy once only two remain. Paying gold never marks the question `assisted` (the score is kept; a pet consult on the same question still forfeits it). The lifeline is absent on the unscored tutorial floor, on assertions and free-text, and when `R` is 0. Gate tracks an `_eliminated` set of display indices (cleared on shuffle/re-sit; deterministic pick, never `self.rng`) and persists the pet's `_struck` so arrow focus no longer wipes a consult strike; `MenuItem.eliminated` / `PromptView.eliminated` distinguish a paid removal from an advisory strike; selection and digit keys skip eliminated options. New `msg.buy_*` / `hint.answer_many_buy` / `help.eliminate` strings in both locales; examination mock-up regenerated.

## [1.32.1] — 2026-07-31

- **The toast loading spinner no longer outlives a doomed idle nudge** (DELVE-0083, bug, session): a playtesting report found the spinner (DELVE-0082) appearing in a room that already had its own toast, then vanishing with nothing to show for it. Root cause is the one-shot idle nudge (DELVE-0061): it fires only for the starting room and, once fired, keeps its call running even after the learner moves, at which point `_poll_toast`'s own drop rule (`is_nudge and self.turn != 0`) silently discards its text since the learner has already acted on it. `RoomBackstoryRunner` gains `pending_other_than(room_id)`; `RunState.frame()` now suppresses `toast_loading` when the sole reason `_room_backstory.pending()` is true is exactly this doomed nudge with nothing else queued behind it, while still showing it when a genuine room toast is queued behind that same doomed call.

## [1.32.0] — 2026-07-31

- **A small spinner window shows while the ambient toast is still generating** (DELVE-0082, feature, session/ui): the room-entry toast previously gave no feedback while `RoomBackstoryRunner`'s background call was in flight; a learner standing still in a fresh room saw nothing change until the passage appeared or didn't. `Frame` gains `toast_loading: str | None`, computed in `RunState.frame()` alongside the existing `toast_pending`: set only while a call is genuinely queued, in flight, or resolved-but-undelivered, no panel is open, and no fresher toast is already showing (so it never both shows at once with the real toast, and the idle-nudge timer's own "armed but not yet queued" wait names nothing, since nothing is actually generating yet). `ui/render.py` draws it as a third, mutually-exclusive branch alongside the panel/toast ones; `ui/windows.draw_toast_loading` reuses the toast's own corner-anchoring logic but smaller (no title row), prefixed with a braille "dots" spinner (`⣾⣽⣻⢿⡿⣟⣯⣷`) whose animation frame is derived from wall-clock time at paint time, no new state threaded through the app loop or the `Frame`. New `[toast]` strings table (`toast.loading`) in both locales.

## [1.31.0] — 2026-07-31

- **Drop from Info/Pack instead of a standalone drop menu** (DELVE-0081, feature, session/ui): `d` used to open its own overlay from walking, a `MenuView` numbering every droppable kind (skipped when there was only one) then, for a multi-count pile, an amount prompt, duplicating the "which kind" choice the Pack tab's own row focus (DELVE-0069) already makes. `d` is now bound only inside `panel_command`'s Info/Pack row list (`ui/keys.py`), dropping whichever row is currently focused: immediately for a lone unit (including the currently-burning torch), or via the existing amount field for a multi-count pile (coins, spare torches). `RunState._drop` acts on `self._pack_row` via a new `_pack_droppable(idx)` (built in `_pack_entries`'s own order: lit torch, gold, inventory stacks) instead of a fresh menu-ordered list; `_drop_menu_overlay`, `_drop_select`, `_droppables`, and the `"drop_menu"` overlay kind are gone outright. The amount field (still `"drop_amount"`) now returns to Info/Pack on confirm, cancel, or Esc (`_close_pack_drop`, replacing `_close_item`'s full close), showing the pack's current contents rather than closing back to walking; `_pack_row` clamps if the drop emptied a row. `hint.carrying` drops its now-dead `Drop: d` mention; a new `hint.inventory_pack` names `Drop: d` on the Pack tab once there is a row to drop. `item.nothing`/`item.drop_prompt` are deleted (no caller left) in both locales.

## [1.30.0] — 2026-07-31

- **The grader model and the ambient toast model now show as separate rows/sections in Info/Status and Info/Grader** (DELVE-0066, feature, assess/session): Delve runs two different local models per session, the configured grader model (default `qwen2.5:3b`) that grades free-text answers, and a separate, more capable ambient model (`_BACKSTORY_MODEL`, `qwen3.5:9b`) that writes the room-entry toast prose, but both used to fold into one blended `GraderMetrics` accumulator with only the grader's own name shown anywhere. `RunState` now keeps a second, dedicated `_ambient_metrics` instance (`RoomBackstoryRunner` records into it instead of the grader's own), and `_status_body` gains a second `Ambient: {model} @ {host}` row beside the existing `Grader:` one, both omitted together when no model is configured. `_grader_body` splits into two headed sections, `Grading` and `Ambient toast`, each with its own `Model`/`Status`/`This run`/`Avg latency`/`Latency` rows; the ambient section's `This run` counts calls rather than an LLM/keyword verdict split, since a scene-setting passage is never graded, and it always renders, even at zero calls, so its presence never depends on whether a room with a toast has been entered yet. New `item.grader_section_*`/`item.ambient_*`/`item.status_ambient` strings in both locales.

## [1.29.2] — 2026-07-31

- **The ambient toast prompt now states an explicit character budget, so a passage is cut off far less often** (DELVE-0080, bug, session): `backstory.PROMPT`/`NUDGE_PROMPT` only asked the model for "a very short (2-3 sentence)"/"1-2 sentence" reply, which DELVE-0070 already found the model doesn't reliably hold to; a play-feedback screenshot showed a passage cut off mid-clause by `RunState._cap_toast_text`'s word-boundary ellipsis fallback (`_TOAST_TEXT_CAP`, 480 characters), which only fires when even the first sentence overruns the cap. Both prompts now also state a concrete character count (400 for the room passage, 160 for the idle nudge, both comfortably under the 480-character hard cap for margin); models generally hold to a numeric budget far better than a sentence count. The existing cap-and-trim backstop is unchanged, since no prompt instruction can be a guarantee.

## [1.29.1] — 2026-07-31

- **Esc now closes a panel almost instantly instead of taking a full second** (DELVE-0079, bug, ui): every panel (Info, Help, a lesson, a menu) closes on a lone `Esc` keypress, but stock ncurses can't tell that apart from the first byte of an escape sequence (arrow/function keys also start with `\x1b`), so it waits `ESCDELAY` milliseconds, 1000 by default, to see if more bytes follow before delivering a standalone Esc; `delve/ui/app.py:_run` never touched that setting, so every Esc felt like the app had hung. `_set_esc_delay` now calls `curses.set_escdelay(25)` once at startup (guarded against a curses build without the extension, a no-op fallback to the platform default), short enough to feel instant and still comfortably above a real terminal's own escape-sequence byte gap.

## [1.29.0] — 2026-07-31

- **Info/Help panels colour labels and item titles instead of flattening them plain** (DELVE-0078, feature, session/ui): the Grader and Status tabs used to pad each row's label with spaces for column alignment (`"Model       {model} @ {host}"`); they now use the same `"Label: value"` colon convention the Objectives tab already had (`en.toml`/`nl.toml` reworded for both), and a new `TextBlock` kind, `"kv"`, lets `ui/windows.py` colon-split each line and colour the label (`Colour.BRIGHT_CYAN`, reusing the app's existing cyan accent rather than adding a seventeenth colour); Keys and Objectives, already colon-formatted, pick up the same colouring for free. `windows._fill_status_size` no longer hardcodes `kind="plain"` when it splices the live terminal size in, which would have silently dropped the new styling from the whole Status tab. Separately, `windows._draw_pack_columns` (DELVE-0075/0076) was flattening every description-column segment to plain text before drawing it, which discarded `_title_block`'s own bold title styling; it now draws through `_put_line`, the same styled-segment path every other panel uses, so a selected pack item's title renders bold like it always should have.

## [1.28.0] — 2026-07-31

- **The Grader tab grows a latency sparkline** (DELVE-0077, feature, assess/session): `GraderMetrics` gains a bounded `latency_ms_history` deque (capped at ten, the mock-up's own width), appended in `record_call` alongside the existing last/max/avg bookkeeping, plus a pure `_sparkline` quantiser onto eight-level Unicode block glyphs (`▁▂▃▄▅▆▇█`). `_grader_body` appends one more `Latency` line reading it, shown only once two or more calls have been recorded this run (a lone glyph has no shape to show). Ships flat within the Grader tab's existing single body, no `Live`/`Run` sub-tab split (still separately unfiled future work); the axis is labelled `(calls)`, not INFOSCREEN.md §7's mock-up `(sittings)`, since `GraderMetrics` has no sitting boundary to group by and the ambient toast's own calls aren't tied to one at all.

## [1.27.2] — 2026-07-31

- **Info/Pack highlights the focused item's name in the list, not its description** (DELVE-0076, bug, ui): reverses DELVE-0075's own placement, shipped earlier the same day; playtesting a running panel found the solid highlight block reading heavier than intended sitting over the whole description, when it's the list a learner actually scans to find "which one am I looking at". `ui/windows._draw_pack_columns` now applies the `bar_attr` highlight to the focused row's name in the left column instead, leaving the description column plain.

## [1.27.1] — 2026-07-31

- **Info/Pack becomes a two-column list-plus-description layout with a scrolling list** (DELVE-0075, feature, session/ui): replaces DELVE-0069's confirm-to-open/Esc-to-back-out detail toggle, shipped earlier the same day, with a permanent split: the compact list stays on the left, the focused row's own description on the right, both visible at all times and updating live as the selection moves, with no separate confirm/back step (`session._confirm`/`_dismiss`'s "info" branches drop the special-casing DELVE-0069 added; `_pack_row` is the tab's only remaining state). The focused row is marked by highlighting its description (a full-width reverse-video block, `ui/windows._draw_pack_columns`), not a leading list-row indicator. The list scrolls once the carried-kind count outgrows its own visible rows, recomputed statelessly every frame from the focused row alone (`_pack_scroll_offset`) rather than `session` tracking a scroll position, per PLAN.md's "the core never tracks a scroll offset" rule.

## [1.27.0] — 2026-07-31

- **Info/Pack becomes a selectable item list with descriptions on demand, instead of one long page** (DELVE-0069, feature, session/ui): the Pack tab used to concatenate every carried kind's full description into one scrollable block, so a learner carrying several kinds paged through multiple screens just to see what they were holding. It now opens on a compact list, one row per carried kind (the lit torch, gold, then inventory), with no description text inline; up/down move the row focus and Enter/space open the focused row's full description, reusing the existing Select/Confirm commands rather than a new one. Esc backs a detail view out to the list first, then closes the panel on a second press, same as every other tab. Money and the lit torch still show their existing generic descriptions when opened; an empty pack still shows the unchanged `item.inv_empty` message rather than an empty list. `docs/SCREENS.md`'s Info/Pack mock-up is left stale on purpose (already the case since DELVE-0073; its generator is a separate piece of work to bring in line, and `./tools.sh screens --check` only asserts geometry, which still passes).

## [1.26.7] — 2026-07-31

- **A keeper's own candle lights their immediate surroundings regardless of the player's torch** (DELVE-0065, feature, engine/session): a torchless learner used to see only their own one-tile radius, which could leave a keeper standing elsewhere in a dark room invisible until stumbled into. `engine.vision` gains `keeper_halo`, unioning the same immediate-neighbourhood reveal a corridor already gets around every keeper's own position; `RunState._lit_tiles` folds it in only while the learner has no working torch, so a lit room (already fully revealed) is unchanged. Like the player's own torchless reveal (DELVE-0062), the halo never persists into `discovered`: it darkens again once the player is out of range.

## [1.26.6] — 2026-07-31

- **The ambient toast freezes its timeout while the player is idle, and is capped in length** (DELVE-0070, bug, session/ui): `_poll_toast`'s age-out check used to count `_TOAST_TTL` turns from the toast's own creation turn, so a learner who stopped moving to read a longer passage could still, in principle, have it age out from under them. It now stays frozen until the learner has taken at least one turn since the toast appeared (`_toast_ttl_start`), and only counts `_TOAST_TTL` turns from that first move; a learner reading it across any number of idle frame polls never sees it disappear. Separately, `backstory.PROMPT` only *asks* the model for "a very short (2-3 sentence)" passage, which it doesn't reliably honour; a new firm `_TOAST_TEXT_CAP` (480 characters) trims an overlong reply to the last complete sentence that fits (`_cap_toast_text`, falling back to a clean word boundary via `textwrap.shorten` for a long run-on with no punctuation) before the text ever reaches `draw_toast`, instead of relying on that function's own line-count truncation to silently cut it off mid-sentence.

## [1.26.5] — 2026-07-31

- **A dropped torch remembers its remaining burn steps instead of relighting at full duration** (DELVE-0067, bug, engine/session): `Stack` gains a per-unit `charge` field, meaningful only for the torch (`None` for every other kind, and for a never-lit torch, which still reads as full duration); `merged`/`taken` treat it as part of a stack's identity, so two torches at different remaining charge never fold into one indistinguishable floor pile, while identical charges still merge exactly as before. Dropping the currently-burning torch (`_do_drop_lit_torch`) now carries its exact remaining steps onto the floor stack instead of discarding them; picking an unlit torch back up while the learner has no other working light (`_do_pickup_torch`) relights it at that remembered charge rather than always jumping to `TORCH_DURATION_STEPS`. The pickup/drop menus and Info/Pack now label an unlit torch by its own remaining steps (new `item.torch_charge_one`/`torch_charge_many` strings, both locales). A floor torch's charge survives a snapshot round-trip; a pre-1.26.5 save with no stored charge defaults to full duration on load, the accepted non-goal for an old save. `_tick_torch`'s own burnout-relight-from-spare is unchanged by design: it still always relights at full duration, regardless of a spare's own stored charge.

## [1.26.4] — 2026-07-31

- **Coins and the torch get a real description in Info/Pack, like every other carried item** (DELVE-0073, bug, session/delve): money and the torch used to render as a single bare plain-text line ("35 coins", "A torch, lit (134 steps left).") with no description, unlike a pack-authored item's bold title plus its own `look`. New `item.torch_look`/`item.money_look` strings (both locales) give both a generic, engine-owned description, and a shared `RunState._title_block` helper renders them with the same bold-title-then-description block every other carried item already gets. The Pack tab's torch title now reuses the lowercase `item.torch_lit_menu` wording (DELVE-0071), so it matches the drop menu; the old full-sentence `item.torch_lit` is retired.

## [1.26.3] — 2026-07-31

- **Drop skips its menu when there is only one thing to drop** (DELVE-0072, bug, session): mirrors `_pickup`'s existing shortcut for a single kind on the tile. `_drop` now goes straight to `_drop_select(0)` when `_droppable_list()` has exactly one entry: a lone single-unit item drops immediately with no menu at all, and a lone multi-count pile (e.g. only gold, several coins) still opens the amount field, skipping past the drop menu but not past the "how many" question.

## [1.26.2] — 2026-07-31

- **The drop menu's lit-torch label now matches every other row's lowercase, unpunctuated style** (DELVE-0071, bug, session/delve): DELVE-0068 reused Info/Pack's full-sentence `item.torch_lit` ("A torch, lit (33 steps left).") for the drop menu's lit-torch entry, which stood out capitalized and full-stopped among the menu's other bare, lowercase noun phrases ("urgent memo", "15 coins"). A new `item.torch_lit_menu` key (both locales) gives the drop menu its own lowercase, unpunctuated wording; Info/Pack's own line is unchanged.

## [1.26.1] — 2026-07-31

- **Three playtesting fixes: stale hint-line key, torch drop label, and a longer Messages tab** (DELVE-0068, bug, session/delve): the walking hint line still read `Messages: p` (DELVE-0063 retired `p` and gave Info its own `i` key, but the hint text was never updated), in both locales; the drop menu's currently-burning torch entry showed a bare "a torch"/"een fakkel" instead of its remaining steps, unlike the same torch's own row in Info/Pack (`item.torch_lit`), so `_droppable_list` now reuses that same wording for the lit-torch entry; and the Messages tab's history cap (`_HISTORY_MAX`) rises from 5 to 10, since 5 read as cramped once the message log became a full Info tab (DELVE-0063) rather than its own small standalone panel.

## [1.26.0] — 2026-07-31

- **The room ambient toast now leads with what's on the floor, not with dungeon atmosphere** (DELVE-0064, feature, session): `session/backstory.py`'s prompt used to open with the shared dungeon-atmosphere framing (no sunlight, colder/damper by chapter, somber tone) before ever mentioning what's actually in the room, and named a floor or carried object only as a bare noun phrase; since the atmosphere framing is identical room to room, it stopped adding anything past a learner's first few rooms, while the one thing that *is* new each time got the least prompt weight. `RunState._item_bullet` now bullets each object with its own authored description (`ItemDef.look`, whitespace-collapsed since a pack author's item prose, unlike this project's own docs, isn't bound by the single-line rule and may be hard-wrapped across source lines) alongside its name, for both `_room_items_description` and `_backpack_description`. The prompt itself is restructured so floor items lead and are explicitly asked to take the bulk of the passage, the carried backpack is framed as a deliberately brief secondary nod, and the dungeon-atmosphere facts (no sunlight, `dlvl`-scaled cold/damp, somber tone, daypart/weekday nod, the Dutch tutoyeer/`fakkel` clause, `has_light` on/off) are compressed into a trailing paragraph that also explicitly forbids describing the room's shape, walls, or layout. Backed by hand-run research against four prompt variants (`docs/research/ambient-toast-grigor.md`); verified against a live `qwen3.5:9b` using the real generated prompt for a shipped room.

## [1.25.1] — 2026-07-30

- **Five playtesting fixes to the Info/Help panels and the torch** (DELVE-0063, bug, session/ui/delve): Info (`i`) and Help (`?`) now always open on their first tab (Pack / Keys) instead of remembering the last tab visited, reversing DELVE-0040's and DELVE-0028's original "sticky across opens" choice, which read as broken navigation once playtested; the active tab is still remembered while a panel stays open. Scoring > Now's bar rows and Scoring > Rooms' Dlvl/glyph rows were each their own block, wasting a blank row per entry; `ui/windows.py` now batches consecutive `bar` blocks the same way it already batches bullets, and `_scoring_rooms_body` condenses via the existing `_condensed` helper (DELVE-0059). Status folds its grader row into the condensed version/pack/locale span (moved ahead of the terminal-size row, which stays its own block since `ui` substitutes it wholesale by kind), down to two blocks from three. The `p` message log merges into the Info panel as a fifth "Messages" tab instead of a separate standalone panel kind; `p` is now a shortcut straight to that tab. The currently-burning torch (never a `Stack`, DELVE-0062) is now in the drop menu, appended last so it never shifts an existing item's number: dropping it extinguishes it immediately and leaves an ordinary torch on the floor, so the unlit ambient scene can be reached deliberately instead of only by waiting `TORCH_DURATION_STEPS` out.

## [1.25.0] — 2026-07-30

- **A torch that lights the room, runs out after roughly 150 steps, and darkens ambient prose without one** (DELVE-0062, feature, engine/session/ui/delve/docs): vision (`engine/vision.py:lit_tiles`) always used to reveal the whole current room instantly and remember every tile forever. A learner now starts with one torch, already lit; `Player.torch_charge` decrements once per step in `RunState._move`, and while it holds, the room lights and stays remembered exactly as before. Once it runs out (`RunState._tick_torch`), a spare torch already in the pack relights automatically in the same message as the burnout, or the learner is left dark; vision then shrinks to the immediate few tiles (`lit_tiles(..., lit=False)`), and none of a torchless tile is remembered, so it goes black again the moment it leaves that radius (`RunState._observe` only unions into `discovered` while `has_light`). A burned-out torch leaves nothing behind, no spent-husk item. Each pack chapter (never the tutorial, which stays exactly as lit as before) hides one spare torch on a random free floor tile (`_scatter_torch`, its own dedicated `Rng` stream). Picking one up while already lit stows it as a spare; picking one up while dark lights it immediately and re-lights the room on the spot. Four new status messages narrate every state change (burnout-with-relight, burnout-with-nothing, pickup-stowed, pickup-lit). The ambient toast (DELVE-0060) is told whether the learner currently has working light (`backstory.build_prompt`'s new `has_light`), swapping the usual scarce-torchlight framing for total blackness beyond arm's reach when not; the shared prompt setting also now pins the Dutch word for the torch itself to "fakkel" (never "toorts"), and the torch's own session-rendered name bypasses `ItemDef.name` for dedicated `Strings` keys the same way money's coin wording already does, so anything the session itself shows is correct independent of the model. `torch_charge` round-trips through the snapshot like any other floor state.

## [1.24.1] — 2026-07-30

- **The Keys tab no longer wastes half its page to blank lines between entries** (DELVE-0059, bug, ui): `RunState._keys_body` folded a context's entries into one `TextBlock` with a literal `"\n"` between each (the same trick `_pack_body` uses to keep an item's name flush above its description), sidestepping `ui/windows.py`'s generic pager rule that inserts a blank row between distinct top-level blocks, right for prose but wrong for a dense list of one-liners. The walking context's 12 entries now fit on a single page instead of needing two; every other panel's spacing (Objectives, a lesson, the pack, the message log) is unaffected, since only Keys' own body construction changed, not the pager itself. A wrapped entry still never splits across a page boundary. Multi-column was researched and rejected: real entry lengths (26-54 chars) don't fit two per row within the shared 69-column panel width without erasing the savings.

## [1.24.0] — 2026-07-30

- **A one-shot idle nudge toast for a first-time player who hasn't moved** (DELVE-0061, feature, session/ui/delve/docs): if a learner hasn't moved at all (still on turn 0) by the time the starting room's ambient toast (DELVE-0060) appears, and about ten real seconds pass with still no movement, a second background call regenerates it in the same keeper's voice (or the chapter title, ungated), suggesting the arrow keys. Wall-clock (`time.monotonic()`), not turn-based, since turns never advance while idle; folded into the existing `toast_pending` poll-loop plumbing so it fires with no keypress needed. One-shot (`RunState._nudge_state`: `unarmed` -> `waiting` -> `queued` -> `fired`/`cancelled`), cancelled the instant a move happens, and never arms at all past the first move (including on a resumed run). Reuses `RoomBackstoryRunner` keyed distinctly (`f"{room_id}::nudge"`), getting the existing cross-chapter drop guard for free.
- **The ambient toast is cleared the instant any panel opens, not just hidden** (a bug found while testing the above): talking to a keeper used to close the lesson with the same toast still there, or reappearing, having outlived its moment. `RunState._poll_toast` now drops `_toast` outright whenever an overlay is open, so closing that overlay never brings the old one back; an in-flight background call is unaffected, just picked up whenever polling next runs with nothing open.

## [1.23.0] — 2026-07-30

- **An asynchronous ambient toast on first entering a room, replacing Objectives' buried passage** (DELVE-0060, feature, session/ui/delve/docs): the optional LLM scene-setting passage (DELVE-0028, fixed by DELVE-0057) routinely landed on the Objectives tab's page 2, behind a `--More--` a learner had no reason to press. It is now generated once per room instead of once per run, queued the moment the learner first stands inside any room this run (gated or not, including the chapter's own starting room, at construction), at most one call in flight at a time (`session/backstory.py`'s `RoomBackstoryRunner`, further rooms queued behind it). A new `Frame.toast` (`ToastView`), independent of `Frame.overlay`, carries the resolved passage; `ui/render.py` draws it as a small, top-anchored block (`ui/windows.py:draw_toast`) only while no panel is open, so it never blocks walking, talking, or opening a panel, and fades on its own after a few turns (`_TOAST_TTL`), no dismiss key needed. `ChapterRun.visited_rooms` (persisted through the snapshot) tracks which rooms have already shown theirs, so a resume never re-triggers one. The Objectives tab now shows only its static pack/chapter/room/progress facts. `RoomBackstoryRunner._work` catches any exception, not just `LLMUnavailable`, since this call now fires far more casually (and far more often) than a deliberate grade. `docs/SCREENS.md` gains the real, generated screen (16), promoted from the proposal tool used to mock it up before it was built.

## [1.22.1] — 2026-07-30

- **The Objectives tab's optional passage actually contains prose now** (DELVE-0057, bug, assess/session): `OllamaClient.chat` forced Ollama's `format: json` and `temperature: 0` unconditionally, settings `LLMGrader` needs for a strict, parseable verdict but which left a model no legal reply but the empty document `{}` once DELVE-0028's Objectives tab reused the same client for free-form scene-setting prose. `chat` now takes optional `json_mode`/`temperature` parameters, defaulting to exactly `LLMGrader`'s existing behaviour (no change there, no test change needed), and `session/backstory.py` asks for `json_mode=False` at `temperature=0.8`. Verified against a live Ollama: the same prompt that used to return `{ }` now returns real atmospheric prose.

## [1.22.0] — 2026-07-30

- **A `?` help panel with Keys and Objectives tabs** (DELVE-0028, feature, session/ui/delve/docs/assess): pressing `?` now opens a `HelpView`, sharing the Info panel's tab-strip/pager drawing code as a sibling type rather than folding into it. Keys lists every command active in the learner's current context (walking, a lesson, a question, the backpack, ...), each with a one-line explanation, read from a new session-side command catalogue (`session/help.py`) that a test holds to agreement with `ui/keys.py`'s real bindings in both directions. Objectives shows a static pack/chapter/room/progress summary assembled from data `RunState` already holds (no new pack frontmatter), plus an optional short scene-setting passage from whichever grader model is already configured, nodding to the time of day and day of week (`session/backstory.py`): generated at most once per run on a background thread mirroring `ThreadedGrader`, cached and carried through the snapshot so a resume shows the same text, and a silent, non-blocking no-op (never an error, never required to play, unlike DELVE-0033's grading gate) when no model is configured or the call fails. `?` now always means help, everywhere, including stacked over a lesson, a question, or the backpack, where dismissing it hands back exactly what was open before; the pet consult, which used to sit on `?` inside a question, moves to `@`. Both locales carry the new strings, and `docs/SCREENS.md` gains a Help mock-up (screen 15).

## [1.21.0] — 2026-07-30

- **Arrow-key row focus and a distinct colour for the Info panel's focused tab strip** (DELVE-0056, story, [epic DELVE-0035](issues/archive/DELVE-0035-information-screen.md)): a play-feedback refinement to DELVE-0055's Scoring sub-tab strip. Up/down now move keyboard focus between the primary tab row and the active tab's sub-tab row; left/right (and Tab/Shift-Tab) cycle whichever row currently has focus, the same two-level arrow navigation Claude Code's own tab UI uses. `[`/`]` keep their DELVE-0055 direct route to the sub-tab strip, unaffected by which row has focus. Because two rows can each show an "active" tab at once, the one under keyboard focus now draws as a filled highlight; the other row's active tab stays visible in a plainer colour with no fill, so a learner can always tell which row the next arrow press will move. Tabs with no sub-tabs (Pack, Grader, Status) render exactly as before.

## [1.20.0] — 2026-07-30

- **Scoring tab grows a Now/Rooms sub-tab strip; Rooms shows the room pass map** (DELVE-0055, story, [epic DELVE-0035](issues/archive/DELVE-0035-information-screen.md)): the Scoring tab, which has shown only its chapter/HP bars since DELVE-0042/DELVE-0043, gains a second-tier tab row beneath the primary strip. `Now` is exactly that bar body, unchanged (renamed internally from `_scoring_body` to `_scoring_now_body`, output identical). `Rooms` is new: one row per scored chapter (`Dlvl {n}`), one glyph per room in that chapter's own order, filled from `Gate.passed`/`.sittings`/`.attempts_used` (`·` sealed, never sat; `░` sat but not passed; `▒` passed after a retry; `█` passed clean), followed by a legend line. `[`/`]` cycle the sub-tab (wraps; a no-op, not an error, on Pack/Grader/Status); the sub-tab resets to `Now` whenever the primary tab changes away from and back to Scoring, so it is never sticky across a round trip. The mechanism is generic on `InfoView` (`subtabs`/`active_sub` fields, empty/zero by default), so Pack/Grader/Status render with no geometry change and a later tab (a Grader Live/Run split) can reuse the same sub-tab strip.

## [1.19.0] — 2026-07-29

- **Grader tab, take 1: model/status/token rows** (DELVE-0054, story, [epic DELVE-0035](issues/archive/DELVE-0035-information-screen.md)): the `i` panel's Grader tab shows real content now, replacing the `item.tab_soon` placeholder it has carried since DELVE-0040. With a model configured it shows a `Model` row (model and host), a `Status` row (warm or cold, and the last grade's latency in ms, or "no grade yet this run" before the first call), and a `This run` row (prompt/completion tokens, and how many verdicts came from the LLM versus the keyword fallback), all read from `LLMGrader`'s new `GraderMetrics` accumulator (DELVE-0053). With no model configured, the whole tab is a single line, "Keyword floor, no model configured", the same first-class-offline-state treatment the grader stack already gives everywhere else. No sub-tab split and no latency sparkline yet; that needs `GraderMetrics` to keep a per-sitting history, which it does not yet.
- **`OllamaClient.chat` stops discarding Ollama's timing and token fields** (DELVE-0053, story, [epic DELVE-0035](issues/archive/DELVE-0035-information-screen.md)): `chat` now returns a `ChatReply(text, metrics)` instead of a bare string, keeping `total_duration`, `load_duration`, `prompt_eval_count`, and `eval_count` from the reply. `LLMGrader` accumulates a run-scoped `GraderMetrics` (tokens in/out, last/max latency, warm/cold, LLM-vs-keyword-fallback counts) across grade calls, reachable via `ThreadedGrader.grader.metrics`. Plumbing only, no UI change by itself; it is what DELVE-0054 reads.

## [1.18.0] — 2026-07-26

- **Status tab, a fourth primary tab in the Info panel** (DELVE-0044, story, ui/session/docs): the
  `i` panel's tab strip gains `Status` after `Grader`, showing plain key/value rows of app and run
  diagnostics that needed no new plumbing: the app version (`delve.__version__`), the active
  pack's name and locale, the grader model/host when one is configured (omitted, not blank,
  otherwise), and the terminal size in rows x cols. The terminal-size row is the first fact in this
  panel that `ui` owns outright rather than `session`: `session` emits only its localised label,
  and `windows._fill_status_size` fills in the live `stdscr.getmaxyx()` value at paint time, so it
  can never go stale. Both locales carry the new tab and row labels.

## [1.17.0] — 2026-07-26

- **Peer-review acceptance gate before implementation starts** (DELVE-0045, story, maintainer
  process/tooling): a drafted issue no longer moves straight from `status: proposed` to code. It
  is now shown to a peer (in this solo, no-remote project, the human maintainer) and the question
  "do you accept this issue?" is asked outright; only once accepted are `accepted_by:`/
  `accepted_at:` filled and `status:` moved to `in-progress`, before any code for it is written.
  `tools/issues.py --check` enforces the fields from `in-progress` onward (mirroring how it already
  enforces `effort:`), and the gate is documented in `issues/AGILE.md`'s Definition of Ready,
  `issues/TEMPLATE.md`, `docs/SDLC.md` §4, and CLAUDE.md's issue-first paragraph. Not retroactive:
  already-archived issues predate the gate and are not backfilled, except DELVE-0035 (in-progress
  when the gate landed), backfilled with today's date rather than left failing the check.

## [1.16.0] — 2026-07-26

- **Scoring tab, take 2: coloured bars, a rename from Progress, and a stale hint fix** (DELVE-0043, story, [epic DELVE-0035](issues/archive/DELVE-0035-information-screen.md)): the `i` panel's Progress tab is renamed **Scoring** throughout (it shows score, not completion) and its bars now draw as real coloured blocks, `█` filled in `BRIGHT_CYAN` and `░` unfilled in the plain attribute, via `attrs.attr_for`, in place of the `#`/`·` ASCII DELVE-0042 shipped; the bar's column layout (label width, glyph rounding) moved from `session` into `ui/windows.py`, where the rest of the panel's width decisions already live. Also fixes the walking hint line (`hint.carrying`), which had said `Inventory: i` since before DELVE-0040 grew `i` into the tabbed Info panel; it now reads `Info: i` in both locales.

## [1.15.0] — 2026-07-26

- **Progress tab, take 1: horizontal bars for chapter score and HP** (DELVE-0042, story, [epic DELVE-0035](issues/archive/DELVE-0035-information-screen.md)): the `i` panel's Progress tab, a `tab_soon` placeholder since DELVE-0040, now shows a bar row per scored chapter (its mean `passed_score` across passed gates, `n/a` rather than `0%` before any gate in it is passed, mirroring `pack_score`'s own averaging rule scoped to one chapter) plus a final HP bar. The tutorial floor stays omitted, the same way it is already excluded from `pack_score`. No sub-tab row yet; this is the whole Progress body until a later story adds the room pass map.

## [1.14.1] — 2026-07-26

- **Info panel tabs, take 2** (DELVE-0041, bug, playtest feedback on DELVE-0040): the active tab is now a filled pill via `attrs.bar_attr` (black text on a solid colour, falling back to reverse video without colour support) instead of the `[ Pack ]` bracket marker; the left/right arrow keys cycle tabs alongside `Tab`/`Shift-Tab`, matching the horizontal-choice convention `PromptView`'s assertion buttons already use; and the tab strip now shows a fixed `Info` panel title before the tabs, localised in both `en` and `nl`. `docs/SCREENS.md`'s pack screen is regenerated for the new title (the pill colour has no ASCII representation).

## [1.14.0] — 2026-07-26

- **The pack panel grows a tab strip** (DELVE-0040, story, [epic DELVE-0035](issues/archive/DELVE-0035-information-screen.md)): `i` opens a new `InfoView` with a primary tab strip (`Pack` / `Progress` / `Grader`) instead of a plain "Your pack" `TextView`. Pack is the default tab and keeps its exact prior content and pagination; `Tab`/`Shift-Tab` cycle tabs (wrapping), and Progress/Grader render a localised placeholder until their own child stories give them real content. The active tab is sticky within a run. Both locales carry the new tab labels and hint line; `docs/SCREENS.md`'s pack screen is regenerated to show the new header row.

## [1.13.0] — 2026-07-26

- **The LLM grader is required to play** (DELVE-0033, feature): `delve`/`delve play` now refuses to
  start a session when no LLM grader is reachable, printing the same diagnosis `delve doctor` would
  (which check failed, and its remedy) and exiting non-zero before curses starts, instead of
  silently sitting free-text answers through the deterministic `KeywordGrader` for the whole run.
  `KeywordGrader` stays as the mid-run fallback for a single garbled/low-confidence verdict, and
  `delve validate` is unaffected (it never grades, so it keeps working with nothing installed).
  `--grader-model`/`--grader-host` now only pick which model/host to require, not whether to have
  one.

## [1.12.0] — 2026-07-26

- **Arrow-key-only navigation** (DELVE-0038, feature): dropped the NetHack `hjkl`/`yubn` movement
  keys; the player now walks with the four arrow keys only. Diagonal movement goes with it (arrow
  keys have no diagonal of their own), confirmed safe since every generated dungeon's corridors are
  strictly L-shaped and fully reachable cardinally. Updated the walking hint line in both locales,
  the tutorial's "That's movement" lesson (`en`/`nl`), and the design-doc mock-ups that quoted the
  old hint text. `panel_command` (menu/prompt focus) was unaffected; it already used arrows.

## [1.11.3] — 2026-07-26

- **Issue screenshots switch from PNG to JPEG** (DELVE-0037, bug): DELVE-0036's resize of the five
  DELVE-0035 screenshots actually grew one of them, 775KB to 810KB, because `sips` has no PNG
  quality dial and re-encoded a gradient-heavy screenshot worse than its original. Recompressed as
  JPEG at quality 85 instead (spot-checked for legible text/chrome), which shrinks every one of the
  five well below their original size (total assets/ weight: 2.6MB to 516KB) and gives an actual
  size/quality knob for the next screenshot attached to an issue. Dev-tooling only; no runtime code
  changed.

## [1.11.2] — 2026-07-26

- **Issue assets are capped at 800px wide** (DELVE-0036, bug): DELVE-0034 added `issues/assets/`
  but said nothing about size, and the five screenshots attached to DELVE-0035 landed at native
  screen resolution (up to 2000px wide). Resized them and taught `tools/issues.py --check` to
  read a PNG/JPEG's own header (stdlib only, no new dependency) and flag anything over 800px wide.
  Dev-tooling only; no runtime code changed.

## [1.11.1] — 2026-07-26

- **Issues can carry attached files** (DELVE-0034): a sibling `assets/` directory beside each of
  `issues/`, `issues/archive/`, and `issues/rejected/` holds files (a screenshot clarifying a
  rendering bug, say), named after the issue rather than given a subdirectory of its own
  (`assets/DELVE-0034-torn-border.png`) so the directory stays greppable as it grows. Dev-tooling
  only; no runtime code changed. `tools/issues.py --check` now verifies every `assets/...`
  reference in an issue body resolves to a real file that starts with that issue's own id, and
  flags an orphaned file left behind by a manual archive/reject move.

## [1.11.0] — 2026-07-26

- **The tutorial ends with a paid free-text exam** (DELVE-0031): a fourth room, Merryn the
  Teller, closes orientation with three free-text questions checking what the Porter, the
  Peddler, and Alwin already taught. A perfect sitting pays 100 gold, dropped on a random
  interior tile of her room, so learners leave orientation with a purse to spend on the
  downstairs helpline (DELVE-0018). Earlier tutorial rooms stay multiple-choice; the floor
  remains unscored, so the pack score is untouched. A follow-up pass (DELVE-0032) broadened the
  room's free-text accept lists and removed a false-positive-prone bare keyword.

## [1.10.2] — 2026-07-25

- **The message line pages with `--More--`** (DELVE-0030, bug): a status message
  wider than the terminal was cut off at the right edge with no sign text was
  lost. It now shows as much as fits followed by a `--More--` prompt and reveals
  the rest on a keypress (that key reads on, it does not move you), the way
  NetHack pages a long message and the way a long lesson panel already paged.
  Quit still works while a `--More--` is up, so a long line never traps you. The
  paging is UI-owned (the run does not know the message line's width), a pure
  `windows.message_pages` split carrying the test weight.

## [1.10.1] — 2026-07-25

- **Inventory descriptions reflow** (DELVE-0029, bug): an item's `look` text was
  shown in the pack (`i`) with the hard line breaks from its Markdown source
  file intact, then wrapped again to the panel, giving a ragged double-wrapped
  paragraph. It now reflows into a clean paragraph that fills the panel width
  (blank-line paragraph breaks preserved), the way keeper lesson prose already
  did. Render-time fix in the session; the stored `look` is unchanged.

## [1.10.0] — 2026-07-25

- **The dog fetches every item, and drops what it carries beside you** (DELVE-0016):
  the companion dog now chases *any* floor item, not just coins (the Peddler-room
  smooth stone it used to walk past), one stack at a time: it paths to the nearest
  item in range, picks it up, heels back, and sets it down on its own tile beside
  you. Delivery is now a **floor drop for coins too**, not a direct bank: the dog
  drops the money as a `$` pile you collect by stepping over (auto-banked), and an
  object waits for `,`. The old behaviour credited gold the instant the dog
  arrived, which read as the reward vanishing; now you see it land and pick it up.
  The cat is unchanged (money-only sweep-and-hover). New engine state
  (`Pet.carried_item`) is snapshotted, and new en/nl drop messages. The fetch
  itself (seek then heel then deliver) draws no pet RNG, so it is deterministic and
  reproduces tile-for-tile across a rebuild or a resume.

## [1.9.2] — 2026-07-25

- **Reward coins scatter** (DELVE-0015): the on-pass money reward now lands on a
  random walkable interior tile of the keeper's room instead of always the tile
  farthest from the exit, so a room no longer files its reward into the same
  corner and gives its shape away. The detour and the pet-race property are kept.
  The draw is deterministic, seeded from the run seed and the room's content id
  (a dedicated stream, never the exam RNG), so a run stays regenerable
  tile-for-tile and a resume lands the coins on the same tile.

## [1.9.1] — 2026-07-25

- **Security gate** (DELVE-0024..0027): `./run-tests.sh` now runs ruff's Bandit-
  compatible `S` rules over `delve/`, `tests/`, and `tools/`, plus `pip-audit` on
  the installed `[dev]` venv. Fetch failures fail the audit step (no silent
  "clean" when advisories could not be checked). Runbook and standing exceptions
  live in [docs/SECURITY.md](docs/SECURITY.md). The LLM client's URL scheme is
  restricted to `http`/`https`.

## [1.9.0] — 2026-07-25

- **Question-text emoji garnish**: the engine sprinkles a single emoji onto a
  keyword in a question, sparsely, so `email` shows as `📧 email`. A global
  per-locale table (`[flavour_emoji]` in the strings catalogue) maps keyword to
  emoji, so an author writes plain prose and never inserts one. At most one
  keyword per question, chosen deterministically from a stable CRC of the prompt
  (never the exam RNG), so it holds across redraws and runs and never changes what
  the grader reads. Skipped when the prompt already carries an emoji; single-
  codepoint emoji only (a test enforces it). About a fifth of the pilot's
  questions get one. Lives in `session/flavour.py`, applied at view-build time.

## [1.8.0] — 2026-07-25

Richer packs and a panel that uses the whole terminal.

- **Emoji in panel prose** (single-codepoint only): a pack author may put a plain
  emoji in a lesson or explanation for flavour. The panel's text wrap now counts
  display columns, not characters (`ui/windows.py:_width`, stdlib
  `unicodedata.east_asian_width`), so a wide glyph no longer runs a line through
  the box border. The validator errors on multi-codepoint hazards (ZWJ, flag,
  skin-tone, variation-selector), which the width oracle can't measure. The
  tutorial's three summary lines now carry a 👀 / 🎒 / 🚪. Map glyphs stay ASCII;
  Windows/PDCurses emoji rendering is still unverified.
- **An object in every security-onboarding room**: the seven staged drafts in
  `items-later/` are promoted and placed, so all twelve rooms now scatter one
  topic-relevant object (spear-letter, vault-keyring, classification-stamp, …).
- **Taller lesson panel on tall terminals**: the panel body grows one row per
  terminal row above the 100×30 floor, keeping a constant margin, so a lesson
  pages less on a big window (the pilot lesson drops from 4 pages to 2 at 137×42).
  The minimum-size layout is unchanged.
- **Placeholder warning**: `delve validate` now flags every author-marked
  placeholder (the classification tiers, `#security-help`, the reporting channels)
  so a pack isn't shipped for real with them in place. Advisory, non-blocking.

## [1.7.0] — 2026-07-25

The answer UI, the message log, the tutorial's objects room, and a batch of
localisation and pet fixes, from a long session of real play in Dutch.

- **Answer chrome**: assertions and MCQs now render as the same numbered-style
  list with a highlighted focus badge; arrows move the focus and Enter answers,
  alongside the direct number/letter keys. (Boxed buttons were prototyped, then
  dropped for the list.)
- **Message log** on `p`: re-read recent lines (newest first, deduped, capped at
  5); fixed the backpack resurrecting an aged-out top line.
- **Tutorial's third room**: the Peddler (a shopkeeper) teaches `,`/`i`/`d`
  hands-on with a placed `pebble` and a free-text question; one coin always drops
  in the starting room; the stairs message is now honest about already-open stairs.
- **Pet**: follows you through doors; a carrying cat sweeps up every coin in range
  then hovers nearby instead of camping a corner.
- **Localisation**: `[yn]` reads `[Jn]` (takes `j`) in Dutch, pet picker `[k]`/`[h]`;
  the pager chrome is localised; the Dutch engine strings reworded to read native.
- **Rendering**: code blocks are verbatim (no reflow); the keeper reference drops a
  trailing comma.
- **Tooling**: `run-tests.sh` validates all four shipped packs; `delve.sh` defaults
  to the free-text grader and auto-manages Ollama for the run.

## [1.6.1] — 2026-07-22

Free-text play-testing refinements, from real play with the LLM grader.

- A ready verdict is held briefly (~2s) so the hand-over line reads before it folds
  into the explanation.
- Startup grader warning when `--grader-model` is set but Ollama can't grade.
- Centred screens wrap instead of truncating (the win line no longer runs off a
  wide terminal's right edge).

## [1.6.0] — 2026-07-22

- `delve setup` / `delve doctor`: the grader bootstrap. `doctor` is a read-only
  diagnostic (Ollama installed, service up, model pulled, warm-up grade); `setup`
  does the safe remedies. Every side effect is injected, so it tests with nothing
  installed.
- Added the bilingual `freetext-demo` pack.

## [1.5.0] — 2026-07-22

- Phase 2 step 2: the LLM grader (`LLMGrader` over a socket seam to a local Ollama
  model, trusted above a 0.65 confidence floor, falling to the keyword grader
  otherwise) and the non-blocking pending-grade state (`session/grading.py`, a
  threaded runner so the UI never blocks on the model).

## [1.4.0] — 2026-07-21

- Phase 2 step 1: free-text questions (`- ?answer:` / `- ?reject:`, inferred as
  `kind == "freetext"`) and the deterministic `KeywordGrader` (the offline default
  and CI seam). The old "reserved, fails validation" error is gone.

## [1.3.4] — 2026-07-20

- Coloured answer line (green "Correct.", red "Not quite."), no lingering highlight
  on the next question, and a cat that chases money as eagerly as a dog.

## [1.3.3] — 2026-07-20

- Count-aware pickup flavour: an `on_pickup` line pluralises from an authored plural
  form, and stands in for the plain "You pick up" line.

## [1.3.2] — 2026-07-20

- Carry flavour made ambient and quiet: speaks on about half your steps, never
  overrides a more important line, and abbreviates after a few full utterances.

## [1.3.1] — 2026-07-20

- Object play-testing refinements: a fetch cooldown so the pet stops pouncing back
  onto coins at your feet; stepping onto a carriable object names it; pickup asks
  how many; `on_move` takes a minimum count; object messages read as grammar.

## [1.3.0] — 2026-07-20

- Pack-authored objects (completes the objects arc): an item file per locale parses
  into an engine `ItemDef`; a room's `place: <id> xN` scatters stacks deterministically;
  the closed effect vocabulary (`on_pickup`, `on_move`, `look`); pack kinds register
  by id and round-trip through the snapshot.
- Content: one reference object per pack, later seasoned up to five each, both locales.

## [1.2.0] — 2026-07-19

- The companion: a chosen cat or dog (or no pet) that moves for itself each turn as a
  pure engine function. A dog fetches and delivers; a cat flees with coins and must be
  bumped to reclaim; a cat's first consult per room is free. Space is a `Wait` command.
  Selection and carried purse flow through the snapshot.

## [1.1.3] — 2026-07-19

- Render lesson tables (aligned, wrapped columns with a bold header) and bold text
  (`**strong**` survives to the panel as styled spans), both previously mangled.

## [1.1.2] — 2026-07-19

- Boxed input field for the player-name prompt (UTF-8 via `get_wch`, so accented names
  type); the tutorial floor is strewn with a few coins so the learner meets auto-pickup
  before money matters.

## [1.1.1] — 2026-07-19

- Objects/interaction play-testing: the on-pass reward drops in-room on the tile
  farthest from the exit and scales by score; the drop amount is typed into a boxed
  field; re-bumping a passed keeper is a brush-off; the top message line ages out;
  the pack/drop/inventory keys are surfaced; quote blocks are highlighted; the
  assertion connector and question counter are localised.

## [1.1.0] — 2026-07-19

- Objects phase 2: the on-pass money reward. A passed room drops coins for the learner
  to walk onto and bank; the amount is a `reward:` frontmatter key (pack default,
  room override), paid once, as session policy rather than a gate mechanic. The win
  screen shows wealth earned.

## [1.0.1] — 2026-07-19

- Objects phase 1: a generic engine item model (`ItemDef` + `Stack`), money that
  auto-collects, pickup/drop/inventory (`,`/`d`/`i`), floor piles, and the snapshot
  carrying gold, inventory and floor stacks. MCQ answers moved from letters to numbers
  so they don't clash with the new map keys.

## [1.0.0] — 2026-07-18

First release. M1–M8 complete; the pilot plays end to end in English and Dutch.
Includes the M7 play-testing interaction fixes (bump-to-talk, bump costs a turn, the
stair hint winning over the talk hint underfoot).

### Pre-1.0 milestones (`0.<milestone>.<patch>`)

- **0.8.x** — M8 polish: 16-colour map palette, per-keeper voices, win screen, README;
  ACS_ line-drawing room walls; the three M7 interaction fixes.
- **0.6.0 / M6** — the tutorial floor and languages (en/nl `Strings` catalogues,
  `--lang`, locale formatting as data).
- **0.5.x / M5** — chapters, scrolls, progress (SQLite), snapshot/resume, identity,
  the trophy case; play any pack via `--pack`.
- **M4** — stakes and the pet: HP penalties, attempts, REPELLED, respawn, consult.
- **M3** — the Markdown pack parser and `delve validate`, both locales.
- **M2** — the vertical slice: walk to a keeper, sit the exam, the door appears.
- **M1** — walkable generated chapter, the headless loop, the import-rule CI.
- **M0** — foundation: venv, package skeleton, tooling, the curses size-guard.
