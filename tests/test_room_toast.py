"""The ambient room-entry toast (DELVE-0060): one short LLM passage per room, queued the moment
the learner first stands inside it (including the chapter's own starting room, at construction),
shown as a `Frame.toast` independent of `Frame.overlay` so it never blocks walking, talking, or a
panel, and ageing out on its own. Replaces DELVE-0028/0057's single once-per-run Objectives
passage, which routinely landed on page 2 behind a `--More--` a learner had no reason to press.
"""

from test_dungeon import _approach, _pass_room, _path, _walk

from delve.assess.grader import LLMGrader
from delve.assess.llm import ChatMetrics, ChatReply, LLMUnavailable
from delve.session import backstory
from delve.session.commands import Talk
from delve.session.grading import ThreadedGrader
from delve.session.run import _TOAST_TTL, new_run
from delve.session.snapshot import apply_dict, to_dict
from delve.strings import load as load_strings

_NO_METRICS = ChatMetrics(None, None, None, None)


class FakeClient:
    """Stands in for `OllamaClient` (mirrors test_llm_grader.py's fake): returns a canned reply,
    or raises `LLMUnavailable`, and counts calls/records `json_mode`/`temperature`/`model` so a
    test can assert the room-entry call asks for prose, not a verdict (DELVE-0057), and for the
    ambient-specific model override (`RoomBackstoryRunner`'s own `model`, distinct from whatever
    this fake stands in for as the grader's client)."""

    def __init__(self, reply=None, raises=False):
        self.reply = reply
        self.raises = raises
        self.calls = 0
        self.last_prompt = ""
        self.last_json_mode: bool | None = None
        self.last_temperature: float | None = None
        self.last_model: str | None = None

    def chat(self, prompt: str, *, json_mode: bool = True, temperature: float = 0,
             model: str | None = None) -> ChatReply:
        self.calls += 1
        self.last_prompt = prompt
        self.last_json_mode = json_mode
        self.last_temperature = temperature
        self.last_model = model
        if self.raises:
            raise LLMUnavailable("no model")
        return ChatReply(text=self.reply, metrics=_NO_METRICS)


def _settle(run) -> None:
    """Force whichever background call is currently in flight to finish, so a test can assert on
    it without a real sleep/poll loop (a `FakeClient` resolves almost instantly, but a test must
    still wait for it deterministically)."""
    thread = run._room_backstory._thread
    if thread is not None:
        thread.join(timeout=2)


def _enter_room(run, room_id: str) -> None:
    """Walk the learner from wherever they stand into the named room's centre."""
    room = next(r for r in run.chapter.rooms if r.id == room_id)
    path = _path(run.chapter.grid, run.player.pos, room.center, blocked=set(run.keepers))
    assert path is not None, f"cannot reach {room_id}"
    _walk(run, path)


# -- queueing and dedup -----------------------------------------------------------------------


def test_the_starting_room_is_queued_at_construction():
    client = FakeClient(reply="A quiet start.")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    assert "phishing" in run.cur.visited_rooms
    _settle(run)
    frame = run.frame()
    assert frame.toast is not None
    assert "A quiet start." in frame.toast.body[0].text


def test_entering_a_new_room_queues_its_own_call():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()                                  # consume the starting room's toast
    _pass_room(run, run.gates["phishing"])       # opens the sealed door onward (rule 2)
    _enter_room(run, "sorting-2")
    assert "sorting-2" in run.cur.visited_rooms
    _settle(run)
    assert client.calls == 2                     # once for the start room, once for this one


def test_reentering_a_room_never_queues_a_second_call():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    _pass_room(run, run.gates["phishing"])
    _enter_room(run, "sorting-2")
    _settle(run)
    calls_after_both = client.calls
    assert calls_after_both == 2

    _enter_room(run, "phishing")                 # back to the room already visited at start
    _settle(run)
    assert client.calls == calls_after_both       # no third call


# -- per-model GraderMetrics (DELVE-0066) ---------------------------------------------------------


def test_an_ambient_call_is_recorded_in_the_runs_own_ambient_metrics():
    """A playtesting note (DELVE-0062) found the Grader tab showed no change at all right after an
    ambient toast appeared, because `RoomBackstoryRunner` never touched any metrics. DELVE-0066
    then split grading and ambient into two separate `GraderMetrics` instances, so an ambient call
    is counted on `RunState._ambient_metrics` and never on the configured `LLMGrader`'s own."""
    client = FakeClient(reply="text")
    client.model, client.host = "qwen2.5:3b", "http://localhost:11434"
    grader = LLMGrader(client)
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(grader))
    _settle(run)
    assert run._ambient_metrics.ambient_calls == 1
    assert grader.metrics.ambient_calls == 0
    assert grader.metrics.llm_verdicts == 0 and grader.metrics.keyword_verdicts == 0
    texts = [b.text for b in run._grader_body()]
    assert any("calls 1" in t.lower() for t in texts)


def test_grader_body_reports_grading_and_ambient_latency_separately():
    class TimedClient:
        model = "qwen2.5:3b"
        host = "http://localhost:11434"

        def chat(self, prompt, *, json_mode=True, temperature=0, model=None):
            ms = 400 if json_mode else 800
            return ChatReply(text="text" if not json_mode else '{"verdict": "ACCEPT", '
                                   '"confidence": 0.9}',
                              metrics=ChatMetrics(total_duration_ms=ms, load_duration_ms=0,
                                                  prompt_tokens=10, completion_tokens=5))

    grader = LLMGrader(TimedClient())
    from delve.assess.question import Question
    grader.grade_text(Question(prompt="p", explanation="e", accept=("x",)), "x")   # 400ms

    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(grader))
    _settle(run)                                        # the starting room's own call, 800ms
    texts = [b.text for b in run._grader_body()]
    assert any("calls 1" in t.lower() for t in texts)
    assert any("400 ms" in t for t in texts)             # the grading section's own mean
    assert any("800 ms" in t for t in texts)             # the ambient section's own mean


# -- non-blocking, ageing -----------------------------------------------------------------------


def test_toast_never_blocks_play_while_pending():
    client = FakeClient(reply="Dust and quiet.")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    turn = run.turn
    frame = run.frame()
    # Whether or not the call has already resolved by the time this assertion runs is a race with
    # the daemon thread; what must hold either way is that nothing about the frame is blocked.
    assert frame.overlay is None
    assert run.turn == turn


def test_toast_appears_once_the_call_resolves():
    client = FakeClient(reply="Dust and quiet.")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    frame = run.frame()
    assert frame.toast is not None
    assert "Dust and quiet." in frame.toast.body[0].text
    assert frame.overlay is None                  # still nothing blocking


def _settle_nudge(run) -> None:
    thread = run._room_backstory._thread
    if thread is not None:
        thread.join(timeout=2)


# -- the one-shot idle nudge (DELVE-0061) --------------------------------------------------------


def test_nudge_delay_is_twenty_seconds():
    """Regression pin: it originally fired after 10s, too soon for someone still reading the
    first toast, per a play-testing report."""
    from delve.session import run as run_module
    assert run_module._NUDGE_DELAY_SECONDS == 20.0


def test_nudge_fallback_appends_arrow_keys_when_the_model_omits_them():
    """Regression guard: a real generated nudge once said only "urging you to explore further",
    with no key named at all, useless to someone who genuinely doesn't know what to press."""
    client = FakeClient(reply="The dim torchlight flickers before you, urging you to explore.")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()
    run._nudge_deadline -= 999
    run.frame()
    _settle_nudge(run)
    frame = run.frame()
    assert "arrow key" in frame.toast.body[0].text.lower()


def test_nudge_text_unchanged_when_the_model_already_names_the_arrow_keys():
    client = FakeClient(reply="Try the arrow keys to explore further!")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()
    run._nudge_deadline -= 999
    run.frame()
    _settle_nudge(run)
    frame = run.frame()
    assert frame.toast.body[0].text == "Try the arrow keys to explore further!"


def test_dutch_nudge_fallback_names_the_pijltjestoetsen():
    client = FakeClient(reply="De duisternis nodigt je uit om verder te gaan.")
    run = new_run(seed=1, cols=100, rows=30, strings=load_strings("nl"),
                  grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()
    run._nudge_deadline -= 999
    run.frame()
    _settle_nudge(run)
    frame = run.frame()
    assert "pijltjes" in frame.toast.body[0].text.lower()


def test_nudge_fires_after_the_delay_with_no_movement():
    client = FakeClient(reply="Try the arrows!")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()                                     # delivers the starting toast, arms the nudge
    assert run._nudge_state == "waiting"
    run._nudge_deadline -= 999                       # force the deadline into the past
    run.frame()                                      # _poll_nudge_timer queues the second call
    assert run._nudge_state in ("queued", "fired")   # a race with the fake client's own thread
    _settle_nudge(run)
    frame = run.frame()
    assert run._nudge_state == "fired"
    assert "Try the arrows!" in frame.toast.body[0].text
    assert client.calls == 2                         # the original toast, then the nudge


def test_nudge_never_fires_once_the_learner_has_moved():
    client = FakeClient(reply="Try the arrows!")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()                                      # arms the nudge
    run._nudge_deadline -= 999
    run.turn = 1                                      # the learner moved before the deadline
    run.frame()
    assert run._nudge_state == "cancelled"
    assert client.calls == 1                          # no second call was ever queued


def test_nudge_never_fires_twice():
    client = FakeClient(reply="Try the arrows!")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()
    run._nudge_deadline -= 999
    run.frame()
    _settle_nudge(run)
    run.frame()
    assert run._nudge_state == "fired"
    calls_after_firing = client.calls
    for _ in range(5):
        run.frame()
    assert client.calls == calls_after_firing


def test_no_nudge_with_no_grader_model_configured():
    run = new_run(seed=1, cols=100, rows=30)          # default InlineGrader: no client at all
    for _ in range(5):
        run.frame()
    assert run._nudge_state == "unarmed"


def test_nudge_never_arms_on_a_run_already_past_its_first_move():
    """A resumed run's snapshot restores `turn` before `frame()` is ever called for the first
    time, so `_poll_toast` never sees `self.turn == 0` and the nudge never arms, the same as any
    run genuinely past its first move."""
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.turn = 5                                      # simulates a restored, already-moved run
    run.frame()
    assert run._nudge_state == "unarmed"


def test_toast_ages_out_on_its_own():
    # DELVE-0070: the TTL is frozen until the learner moves at least once since the toast
    # appeared, so this now needs one move to start the clock before the remaining TTL turns.
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    frame = run.frame()
    assert frame.toast is not None
    run.turn += 1                              # the first move since the toast appeared
    frame = run.frame()
    assert frame.toast is not None             # the clock has only just started
    run.turn += _TOAST_TTL
    frame = run.frame()
    assert frame.toast is None


def test_toast_stays_up_across_many_idle_polls_with_no_move():
    """DELVE-0070: a learner who stops to read a toast and never moves again must never see it age
    out, no matter how many times the frame is rebuilt while `self.turn` stays put."""
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    frame = run.frame()
    assert frame.toast is not None
    for _ in range(50):                        # far more than _TOAST_TTL polls, turn never moves
        frame = run.frame()
    assert frame.toast is not None


def test_toast_countdown_only_starts_once_the_learner_moves():
    """The TTL is measured from the first move *after* the toast appeared, not from its own
    creation turn: moving once should not, by itself, already have used up most of the budget."""
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()
    run.turn += 5                              # idled a while, then finally took one turn
    frame = run.frame()
    assert frame.toast is not None
    run.turn += _TOAST_TTL - 1                 # one short of a full TTL since that first move
    frame = run.frame()
    assert frame.toast is not None
    run.turn += 1
    frame = run.frame()
    assert frame.toast is None


# -- firm length cap (DELVE-0070) ------------------------------------------------------------------


def test_an_overlong_ambient_reply_is_trimmed_to_the_cap_at_a_sentence_boundary():
    from delve.session.run import _TOAST_TEXT_CAP

    sentence = "This is one plain sentence of ambient dungeon flavour text. "
    long_reply = sentence * 20                 # comfortably past the cap
    assert len(long_reply) > _TOAST_TEXT_CAP
    client = FakeClient(reply=long_reply)
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    frame = run.frame()
    shown = frame.toast.body[0].text
    assert len(shown) <= _TOAST_TEXT_CAP
    assert shown.endswith(".")                 # cut at a sentence boundary, not mid-word
    assert long_reply.startswith(shown)         # a clean prefix, nothing rewritten mid-passage


def test_a_reply_within_the_cap_is_shown_unchanged():
    client = FakeClient(reply="A short passage, well within any reasonable cap.")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    frame = run.frame()
    assert frame.toast.body[0].text == "A short passage, well within any reasonable cap."


def test_cap_helper_falls_back_to_a_word_boundary_with_no_sentence_punctuation():
    import textwrap

    from delve.session.run import _cap_toast_text

    words = "one two three four five six seven eight nine ten " * 20
    capped = _cap_toast_text(words, limit=40)
    assert capped == textwrap.shorten(words, width=40, placeholder="…", break_on_hyphens=False)
    # Every word in the trimmed text (bar a trailing placeholder) is one of the whole words offered.
    assert all(w.rstrip("…") in ("one", "two", "three", "four", "five", "six", "seven", "eight",
                                 "nine", "ten", "") for w in capped.split())


def test_toast_is_dropped_if_the_learner_already_left_the_chapter():
    """Regression guard: a room's call can resolve turns after it was queued. If the learner has
    since moved to a different chapter (taken the stairs) before it lands, showing a passage
    labelled for a keeper or floor already left behind reads as a flat mismatch (confirmed in
    play: a tutorial keeper's toast appeared while already on Dlvl 1, next to a different keeper
    entirely), not just mild lateness the way a still-lingering toast for an earlier room on the
    *same* floor is; it must be dropped instead of shown."""
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    run.chapters.append(run.chapters[0])   # a second slot is enough for idx to move into
    _settle(run)
    run.idx = 1                            # simulate having since taken the stairs
    frame = run.frame()
    assert frame.toast is None


def test_toast_is_cleared_once_a_panel_opens_and_stays_cleared_after_it_closes():
    """Regression guard (a play-testing report): a keeper's lesson finished and the *same* ambient
    toast reappeared, having outlived its moment. Opening any overlay clears it outright, not just
    hides it, so closing that overlay again never brings it back."""
    from delve.session.commands import Dismiss, Inventory

    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    frame = run.frame()
    assert frame.toast is not None
    frame = run.apply(Inventory())
    assert frame.overlay is not None
    assert frame.toast is None                # cleared the instant the panel opened
    frame = run.apply(Dismiss())
    assert frame.overlay is None
    assert frame.toast is None                 # stays cleared, does not reappear


def test_toast_is_cleared_the_moment_a_keeper_conversation_starts():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert run.frame().toast is not None
    _approach(run, run.gates["phishing"].keeper.pos)
    frame = run.apply(Talk())
    assert frame.overlay is not None            # the lesson panel
    assert frame.toast is None


# -- toast_pending: appears without a keypress, ui/app.py's own follow-up ------------------------


def test_frame_reports_pending_while_a_call_is_queued_or_in_flight():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    frame = run.frame()
    # A race with the daemon thread either way, but immediately after construction the call can't
    # have both started and been delivered yet, so pending must be true at least once here.
    assert frame.toast_pending or frame.toast is not None


def test_pending_stays_true_while_the_idle_nudge_still_might_fire():
    """Since DELVE-0061, delivering the very first toast on turn 0 arms the idle-nudge timer, so
    `toast_pending` intentionally stays true afterwards (ui/app.py must keep polling to catch the
    nudge firing later); it only clears once a move cancels the nudge (a separate test)."""
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    frame = run.frame()                            # delivers the resolved toast, arms the nudge
    assert frame.toast is not None
    assert frame.toast_pending is True              # the nudge timer is now armed and waiting


def test_pending_clears_once_a_move_cancels_the_idle_nudge():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()                                     # delivers the toast, arms the nudge
    run.turn = 1                                    # simulate having moved
    frame = run.frame()
    assert frame.toast_pending is False              # nudge cancelled, nothing left to wait for


def test_pending_is_false_with_no_grader_model_configured():
    run = new_run(seed=1, cols=100, rows=30)       # default InlineGrader: submit is a no-op
    frame = run.frame()
    assert frame.toast_pending is False


def test_pending_stays_true_across_frames_until_the_call_actually_resolves():
    """The regression this issue is about: before `toast_pending` existed, nothing rebuilt the
    `Frame` between the call being submitted and the learner's next keypress, so a toast that
    finished while they stood still only appeared once they happened to move."""
    import time

    class SlowClient(FakeClient):
        def chat(self, prompt, *, json_mode=True, temperature=0, model=None):
            time.sleep(0.2)
            return super().chat(prompt, json_mode=json_mode, temperature=temperature, model=model)

    client = SlowClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    assert run.frame().toast_pending is True       # the call is still in flight, unsettled
    _settle(run)
    assert run.frame().toast is not None           # delivered on the very next frame(), no
    # command needed in between: `ui/app.py`'s poll loop is what makes this happen in the real
    # app without a keypress; this asserts the session half of that contract.


# -- fallback: no model, unreachable model, or an incompatible test double ----------------------


def test_no_toast_ever_with_no_grader_model_configured():
    run = new_run(seed=1, cols=100, rows=30)      # default InlineGrader: no client at all
    assert run._room_backstory.client is None
    frame = run.frame()
    assert frame.toast is None


def test_no_toast_when_the_model_is_unreachable():
    run = new_run(seed=1, cols=100, rows=30,
                  grader_runner=ThreadedGrader(LLMGrader(FakeClient(raises=True))))
    _settle(run)
    frame = run.frame()
    assert frame.toast is None


def test_a_client_missing_chat_entirely_never_crashes_the_background_thread():
    """Regression guard: many existing tests build a minimal fake client (just `model`/`host`,
    for the Grader tab's display) that was never meant to be called. DELVE-0060 makes every
    configured client reachable from room entry too, so `RoomBackstoryRunner._work` must survive a
    client shaped nothing like `OllamaClient`, not just an `LLMUnavailable`-raising one."""
    class BareClient:
        model = "m"
        host = "h"

    run = new_run(seed=1, cols=100, rows=30,
                  grader_runner=ThreadedGrader(LLMGrader(BareClient())))
    _settle(run)
    frame = run.frame()
    assert frame.toast is None


# -- the prompt: pack/chapter facts, keeper clause only for a gated room, locale -----------------


def test_room_prompt_states_no_keeper_for_an_ungated_room():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()
    _pass_room(run, run.gates["phishing"])
    _enter_room(run, "sorting-2")
    _settle(run)
    assert "about to face" not in client.last_prompt
    assert "No keeper is present" in client.last_prompt
    assert "The Sorting Office" in client.last_prompt


def test_room_prompt_includes_the_keeper_clause_for_a_gated_room():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert "Ada" in client.last_prompt
    assert "about to face" in client.last_prompt


# -- the learner's own backpack, offered as optional context --------------------------------------


def test_room_prompt_describes_the_backpack_when_carrying_something():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)                                 # the starting room's own call, gold still 0
    run.player.gold = 70
    _pass_room(run, run.gates["phishing"])
    _enter_room(run, "sorting-2")                # a fresh room's prompt, built with gold now set
    _settle(run)
    assert "The learner is carrying" in client.last_prompt
    assert "70 coins" in client.last_prompt


def test_room_prompt_omits_the_carrying_clause_for_an_empty_backpack():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert "The learner is carrying" not in client.last_prompt


def test_backpack_description_matches_the_pack_panels_own_wording():
    run = new_run(seed=1, cols=100, rows=30)
    run.player.gold = 70
    assert run._coins(70) in run._backpack_description()


def test_pet_description_is_locale_aware_not_hardcoded_english():
    # Used to hardcode "named" regardless of locale, so a Dutch run's ambient prompt said "hond
    # named Rex" instead of "hond genaamd Rex", the one fact fed into the otherwise fully-localized
    # prompt that wasn't actually localized.
    en = new_run(seed=1, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    assert en._pet_description() == "dog named Rex"
    nl = new_run(seed=1, cols=100, rows=30, pet_species="dog", pet_name="Rex",
                 strings=load_strings("nl"))
    assert nl._pet_description() == "hond genaamd Rex"
    assert "named" not in nl._pet_description()


# -- the random focus: room / keeper / objects --------------------------------------------------


def test_build_prompt_includes_every_fact_at_once_not_a_random_one():
    """Since a play-feedback request replaced the random single focus with comprehensive context:
    lesson topic, keeper, room objects (mandatory, even "bare"), backpack, and companion should
    all appear in the same prompt whenever given, never gated behind a coin flip."""
    prompt = backstory.build_prompt(
        pack="p", dlvl=1, chapter_title="c", language="English",
        keeper="Ada", requirement="70%", lesson_topic="Recognising phishing emails",
        room_objects="a rusted lockbox", carrying="70 coins", pet="cat named Whiskers")
    assert "Recognising phishing emails" in prompt
    assert "Ada" in prompt and "about to face" in prompt
    assert "a rusted lockbox" in prompt
    assert "70 coins" in prompt
    assert "cat named Whiskers" in prompt


def test_build_prompt_states_a_bare_floor_truthfully():
    prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="English")
    assert "floor of this room is bare" in prompt.lower()


def test_build_prompt_states_no_keeper_present_for_an_ungated_room():
    """A verification run against real models showed both qwen3.5:9b and gemma3:12b would
    sometimes invent a keeper for an ungated room when the clause was simply omitted; the prompt
    now says so explicitly, the same way `room_objects` states a bare floor rather than leaving
    the model to guess."""
    prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="English")
    assert "This room teaches" not in prompt
    assert "about to face" not in prompt
    assert "No keeper is present" in prompt


def test_build_prompt_permits_markdown_bold_for_emphasis():
    prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="English")
    assert "**" in prompt


def test_build_prompt_and_nudge_prompt_require_tutoyeer_dutch():
    """Regression guard (a play-feedback correction): STYLE.md's 'je', never 'u', was never
    actually stated in either prompt, and a comparison run showed a capable model drift to 'u'
    unprompted once nothing said otherwise."""
    prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="Dutch")
    nudge = backstory.build_nudge_prompt(pack="p", dlvl=1, chapter_title="c", language="Dutch")
    assert "'je'" in prompt and "'u'" in prompt
    assert "'je'" in nudge and "'u'" in nudge


def test_build_prompt_bans_sunlight_and_names_the_dungeon_setting():
    """Regression guard (a play-feedback correction): real replies kept describing sunlight
    slanting through windows, which cannot be true underground. The prompt itself must rule that
    out and name the dungeon's own atmosphere (torchlight, cold, damp, somber), tying depth to
    temperature via the real dlvl."""
    prompt = backstory.build_prompt(pack="p", dlvl=4, chapter_title="c", language="English")
    assert "no sunlight" in prompt.lower()
    assert "torchlight" in prompt.lower()
    assert "chapter 4" in prompt.lower()
    assert "colder" in prompt.lower()
    assert "happiness" in prompt.lower()


def test_build_nudge_prompt_also_bans_sunlight():
    prompt = backstory.build_nudge_prompt(pack="p", dlvl=1, chapter_title="c", language="English")
    assert "no sunlight" in prompt.lower()
    assert "torchlight" in prompt.lower()


# -- an explicit character budget, on top of "very short" (DELVE-0080) ----------------------------


def test_build_prompt_states_an_explicit_character_budget():
    prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="English")
    assert f"under {backstory._PASSAGE_CHAR_BUDGET} characters" in prompt


def test_build_nudge_prompt_states_its_own_smaller_character_budget():
    prompt = backstory.build_nudge_prompt(pack="p", dlvl=1, chapter_title="c", language="English")
    assert f"under {backstory._NUDGE_CHAR_BUDGET} characters" in prompt
    assert backstory._NUDGE_CHAR_BUDGET < backstory._PASSAGE_CHAR_BUDGET


def test_the_passage_budget_leaves_margin_under_the_hard_cap():
    from delve.session.run import _TOAST_TEXT_CAP

    assert backstory._PASSAGE_CHAR_BUDGET < _TOAST_TEXT_CAP


def test_room_prompt_includes_the_lesson_topic_for_a_gated_room():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert run.gates["phishing"].lesson.title in client.last_prompt


def test_room_prompt_describes_real_floor_items_not_invented_ones():
    from delve.engine.items import MONEY, Stack

    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()
    _pass_room(run, run.gates["phishing"])
    room = next(r for r in run.chapter.rooms if r.id == "sorting-2")
    pos = next(p for p in room.interior())
    run.items[pos] = [Stack(MONEY, 12)]
    _enter_room(run, "sorting-2")
    _settle(run)
    assert "12 coins" in client.last_prompt


def test_room_prompt_names_the_companion_when_one_is_along():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, pet_species="dog", pet_name="Rex",
                  grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert "dog named Rex" in client.last_prompt


def test_room_prompt_omits_the_companion_for_a_soloist():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, pet_species="none",
                  grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert "follows the learner" not in client.last_prompt


def test_room_backstory_asks_for_the_dedicated_backstory_model_not_the_graders():
    """The play-feedback decision: qwen3.5:9b for ambient prose, distinct from whatever the
    grader is configured with, via OllamaClient.chat's own model override rather than a second
    client (which would lose this fake's test-double identity)."""
    from delve.session.run import _BACKSTORY_MODEL

    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert client.last_model == _BACKSTORY_MODEL


def test_dutch_room_prompt_asks_for_dutch():
    client = FakeClient(reply="tekst")
    run = new_run(seed=1, cols=100, rows=30, strings=load_strings("nl"),
                  grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert "Dutch" in client.last_prompt


def test_toast_asks_for_prose_not_a_verdict():
    """Regression guard: DELVE-0057's fix (no forced JSON mode, non-zero temperature) must keep
    holding for the per-room call this issue replaced the per-run one with."""
    client = FakeClient(reply="A quiet corridor.")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    assert client.last_json_mode is False
    assert client.last_temperature != 0


def test_toast_title_is_the_keeper_name_for_a_gated_room_and_the_chapter_title_otherwise():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    frame = run.frame()
    assert frame.toast.title == run.gates["phishing"].keeper.name

    _pass_room(run, run.gates["phishing"])
    _enter_room(run, "sorting-2")
    _settle(run)
    frame = run.frame()
    assert frame.toast.title == run.cur.title


def test_daypart_buckets_the_day():
    assert backstory.daypart(3) == "night"
    assert backstory.daypart(8) == "morning"
    assert backstory.daypart(14) == "afternoon"
    assert backstory.daypart(19) == "evening"
    assert backstory.daypart(23) == "night"


def test_weekday_name_is_english_regardless_of_the_process_locale():
    """Regression guard: `build_prompt` used to embed `now.strftime('%A')`, which reads the
    process/OS locale (CLAUDE.md's own documented `strftime('%B')` gotcha, just as true of `%A`).
    On a host whose locale is Dutch, an English prompt would get a bare 'donderdag' spliced into
    it, and a model with no reason to think it wasn't an ordinary word would parrot it straight
    into an otherwise-English passage. Skipped if the Dutch locale isn't installed on this host."""
    import datetime as datetime_mod
    import locale

    try:
        locale.setlocale(locale.LC_TIME, "nl_NL.UTF-8")
    except locale.Error:
        import pytest
        pytest.skip("nl_NL.UTF-8 locale not installed on this host")
    try:
        thursday = datetime_mod.datetime(2026, 7, 30)   # a real Thursday
        assert thursday.strftime("%A") == "donderdag"   # the locale really is in effect
        prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="English",
                                        now=thursday)
        assert "Thursday" in prompt
        assert "donderdag" not in prompt
    finally:
        locale.setlocale(locale.LC_TIME, "C")


# -- visited_rooms survives a snapshot round trip, so resume never re-triggers a toast -----------


def test_visited_rooms_survive_a_snapshot_round_trip():
    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    _pass_room(run, run.gates["phishing"])
    _enter_room(run, "sorting-2")
    _settle(run)
    assert run.cur.visited_rooms == {"phishing", "sorting-2"}

    data = to_dict(run)
    fresh = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    apply_dict(fresh, data)
    assert fresh.cur.visited_rooms == {"phishing", "sorting-2"}

    calls_before = client.calls
    fresh._observe()                              # re-checking the same spot re-triggers nothing
    assert client.calls == calls_before


# -- items-first prompt rework (DELVE-0064) ------------------------------------------------------


def test_item_bullet_includes_the_items_own_description():
    from delve.engine.items import ItemDef

    run = new_run(seed=1, cols=100, rows=30)
    memo = ItemDef(id="urgent-memo", glyph="?", name="urgent memo", colour="bright_red",
                   look="A printed email that wants you hurried.")
    bullet = run._item_bullet(memo, 1)
    assert bullet.startswith("- **a urgent memo**:")
    assert "A printed email that wants you hurried." in bullet


def test_item_bullet_falls_back_to_the_bare_phrase_with_no_look():
    from delve.engine.items import MONEY

    run = new_run(seed=1, cols=100, rows=30)
    assert run._item_bullet(MONEY, 12) == "- **12 coins**"


def test_item_bullet_collapses_a_hard_wrapped_look_onto_one_line():
    """Regression guard: an item's `look` is pack-authored prose, not one of the project's own
    bookkeeping docs, so it is not bound by CLAUDE.md's single-line rule and may genuinely be
    hard-wrapped across several source lines (`urgent-memo.md`'s is). Splicing that raw text into
    a bullet used to embed a mid-sentence newline straight into the prompt."""
    from delve.engine.items import ItemDef

    run = new_run(seed=1, cols=100, rows=30)
    memo = ItemDef(id="urgent-memo", glyph="?", name="urgent memo", colour="bright_red",
                   look="A printed email that wants you hurried. The sender almost looks right, "
                        "the link\nalmost looks right, and the deadline is always one hour from "
                        "whenever you found\nit. Ada would not open it.")
    bullet = run._item_bullet(memo, 1)
    assert "\n" not in bullet
    assert "the link almost looks right" in bullet


def test_room_prompt_includes_a_floor_items_own_description_not_just_its_name():
    """DELVE-0064: the prompt now carries each floor object's own authored description (its
    `items/*.md` body, `ItemDef.look`), not just its bare noun phrase, so the model has real
    material to draw on."""
    from delve.engine.items import ItemDef, Stack

    client = FakeClient(reply="text")
    run = new_run(seed=1, cols=100, rows=30, grader_runner=ThreadedGrader(LLMGrader(client)))
    _settle(run)
    run.frame()
    _pass_room(run, run.gates["phishing"])
    room = next(r for r in run.chapter.rooms if r.id == "sorting-2")
    pos = next(p for p in room.interior())
    memo = ItemDef(id="urgent-memo", glyph="?", name="urgent memo", colour="bright_red",
                   look="A printed email that wants you hurried.")
    run.items[pos] = [Stack(memo, 1)]
    _enter_room(run, "sorting-2")
    _settle(run)
    assert "a urgent memo" in client.last_prompt
    assert "A printed email that wants you hurried." in client.last_prompt


def test_build_prompt_asks_the_model_to_give_floor_items_the_bulk_of_the_passage():
    prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="English",
                                    room_objects="- **a spear letter**: a forged tone.")
    assert "bulk of the passage" in prompt


def test_build_prompt_frames_carrying_as_a_brief_secondary_nod():
    prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="English",
                                    carrying="- **70 coins**")
    assert "brief, secondary nod" in prompt.lower()


def test_build_prompt_forbids_describing_the_rooms_shape_or_opening_on_it():
    prompt = backstory.build_prompt(pack="p", dlvl=1, chapter_title="c", language="English")
    assert "do not describe the room's shape" in prompt.lower()
    assert "do not open the passage with a scene-setting description" in prompt.lower()


def test_build_prompt_still_names_the_dungeon_setting_after_the_rework():
    """Regression guard: DELVE-0064 moved the atmosphere framing from the opening paragraph to a
    trailing, compressed reminder; every fact it states must still reach the model, just later in
    the text, not dropped."""
    prompt = backstory.build_prompt(pack="p", dlvl=4, chapter_title="c", language="English")
    low = prompt.lower()
    assert "no sunlight" in low
    assert "torchlight" in low
    assert "colder" in low
    assert "happiness" in low
    assert prompt.index("no sunlight") > prompt.index("bulk of the passage")
