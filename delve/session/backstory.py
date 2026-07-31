"""Optional ambient dungeon flavour prose, one short passage per room (DELVE-0060, replacing
DELVE-0028's single once-per-run passage on the Objectives tab, which DELVE-0057 fixed but which
stayed easy to miss buried behind a page flip).

Reuses `session/grading.py`'s `ThreadedGrader` shape (a blocking HTTP call run on a daemon thread
so `apply` stays non-blocking, PHASE2.md section 5.3), but deliberately does not go through
`assess.grader`/`LLMGrader`: this is descriptive scene-setting, not a verdict, and a failure here
must never touch `room_results`, HP, or grading quality (rule 1's spirit). `RunState` reuses
whichever `OllamaClient` the free-text grader is already configured with (if any); a run with no
model configured gets a client-less runner whose `submit` is forever a no-op, so entering a room
simply never grows a toast, with no error and no gating (unlike DELVE-0033's grader requirement).
"""

from __future__ import annotations

import threading
from collections import deque
from datetime import datetime

from delve.assess.llm import LLMUnavailable

_DAYPART_BOUNDARIES = ((5, "night"), (12, "morning"), (17, "afternoon"), (21, "evening"))

# Never `now.strftime("%A")`: that reads the process/OS locale (CLAUDE.md's own documented gotcha
# for `strftime('%B')`, and just as true of weekday names), so an English run on a host whose
# locale is set to Dutch would embed "donderdag" in an otherwise-English prompt, and the model,
# having no reason to think it's anything but an English word, would parrot it straight through.
# The prompt is always written in English (only the *requested reply* is localised via
# `{language}`), so the weekday name inside it must be a fixed English word regardless of the host.
_WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# Generation, not judgement (PHASE2.md's distinction, sharpened by DELVE-0057): 0 (the grader's
# floor) makes every passage a near-identical clone; this is high enough for real variety between
# rooms while staying coherent against the small models this project targets (tried informally
# against qwen2.5:3b and qwen3.5:9b).
_TEMPERATURE = 0.8

# The one constant across every passage, room or nudge (a play-feedback correction: real replies
# kept describing "the afternoon sun slanted through the dusty windows", which cannot be true
# underground). This is a dungeon, not a lit building with a view outside; {daypart}/{weekday} are
# still worth keeping (real variety, tied to real time), but they must be felt only through mood,
# torchlight, or the keeper's own rhythm, never through daylight or a window. {dlvl} feeds the
# "colder/damper the deeper" clause directly, so a chapter 1 room and a chapter 5 room read
# differently without a separate fact-gathering path.
_SETTING = (
    "This is a dungeon, deep underground: no sunlight or daylight ever reaches here; {light} "
    "This is chapter {dlvl}; the deeper that number, the colder the air, and the stone walls may "
    "be damp or wet. Even though it is {daypart} on a {weekday} outside, nothing here shows "
    "daylight, a window, or the outside world at all; if you nod to the time of day or day of "
    "week, do it only through mood, torchlight, or the keeper's own rhythm (a shift change, "
    "weariness, a habit). Keep the tone somber and a little foreboding: no sunlight, no "
    "cheerfulness, no happiness.{dutch_clause}"
)

# STYLE.md's tutoyeer rule (`je`, never `u`) and the pack's own torch vocabulary, both their own
# play-feedback corrections (a comparison run showed a capable model drift to `u` unprompted once
# nothing said otherwise; a later one showed English replies calling the torch a "fakkel").
# Appended only when Dutch is the requested reply language (a9a25bb tried scoping this with prose
# alone, "if replying in Dutch, ... In English, the word is simply 'torch'", but a wider three-model
# comparison run still showed every model occasionally parrot the literal token "fakkel" into an
# English passage regardless of the surrounding "if replying in Dutch" framing: a small model
# leans on words that are simply present in the prompt, whatever the conditioning sentence around
# them says. The only fix that actually holds is structural: the Dutch vocabulary words must not
# appear in the prompt text at all unless Dutch was actually requested.
_DUTCH_CLAUSE = (
    " If replying in Dutch, address the learner informally as 'je', never the formal 'u', and "
    "if you mention the torch itself, call it 'fakkel' (plural 'fakkels', its glow "
    "'fakkellicht'), never the word 'toorts' or 'toortslicht'."
)


def _language_setting(language: str, *, light: str, dlvl: int, daypart: str, weekday: str) -> str:
    dutch_clause = _DUTCH_CLAUSE if language.lower() == "dutch" else ""
    return _SETTING.format(light=light, dlvl=dlvl, daypart=daypart, weekday=weekday,
                           dutch_clause=dutch_clause)

# DELVE-0062: whether the learner currently has a working torch changes what they can actually see,
# so the prompt must say which is true rather than always assuming torchlight.
_LIGHT_ON = "only deep darkness beyond the reach of scarce, flickering torchlight."
_LIGHT_OFF = (
    "the learner has no working light of their own right now; only the few paces they can feel "
    "their way through are visible, everything beyond that is impenetrable black."
)

# DELVE-0064: the atmosphere framing (no sunlight, dlvl-scaled cold/damp, somber tone,
# daypart/weekday nod) used to open the whole prompt, which primed every reply to lead with room
# description; identical room to room, it stopped adding anything past a learner's first few
# rooms, while the one thing that *is* new each time, the room's own floor items, carried the
# least prompt weight and the least descriptive material (research: docs/research/
# ambient-toast-grigor.md, v1-v3 tried reordering only the closing ask and the model still opened
# on atmosphere regardless; only restructuring the whole prompt, items first, atmosphere pushed to
# a trailing single-touch reminder, actually moved it). `room_objects`/`carrying` are now expected
# to already be multi-line, per-item bullets (`RunState._item_bullet`) rather than a bare,
# comma-joined noun phrase, so the model has each object's own authored description to draw on.
PROMPT = (
    "You are writing a very short (2-3 sentence) scene-setting passage for a text-based dungeon "
    "training game. The learner is exploring a training pack called {pack!r}, currently on "
    "chapter {dlvl} ({chapter_title}).{lesson_clause}{keeper_clause}\n\n"
    "Focus mainly on what is newly in front of the learner in this room:\n\n"
    "{objects_clause}\n\n"
    "Give these floor items the bulk of the passage: what they look like, what is unsettling or "
    "telling about them, why they are here. You may also give a brief, secondary nod to what the "
    "learner is already carrying, without dwelling on it.{carrying_clause}{pet_clause}\n\n"
    "Do not describe the room's shape, walls, or layout, and do not open the passage with a "
    "scene-setting description of the space itself; start from the items instead. {setting} Keep "
    "any atmosphere to a brief, secondary touch; the items above are the subject, not the room.\n\n"
    "You may use **double asterisks** around a word or short phrase for emphasis, sparingly. "
    "Write a brief passage (no instructions, no meta-commentary, just narrative prose). Reply in "
    "{language}. Reply with ONLY the passage text, no preamble."
)


def daypart(hour: int) -> str:
    """Which part of the day `hour` (0-23) falls in, the coarse morning/afternoon/evening/night
    split the prompt asks the model to nod to."""
    for boundary, name in _DAYPART_BOUNDARIES:
        if hour < boundary:
            return name
    return "night"


def build_prompt(*, pack: str, dlvl: int, chapter_title: str, language: str, keeper: str = "",
                  requirement: str = "", lesson_topic: str = "", room_objects: str = "",
                  carrying: str = "", pet: str = "", has_light: bool = True,
                  now: datetime | None = None) -> str:
    """A room's prompt: every fact `RunState._room_prompt` can gather, always included, rather
    than picking one at random (a play-feedback request: comprehensive context beats a narrow,
    randomly chosen focus). `keeper`/`requirement` are blank for an ungated room (most of a
    chapter's rooms, since only a gated one has a lesson), and `lesson_topic` (the room's own
    `Lesson.title`) along with them; the lesson/requirement clauses are then omitted entirely
    rather than reading as 'about to face , whose room requires a score of  to pass', but the
    keeper clause instead states plainly that no keeper is present (a verification run showed
    both qwen3.5:9b and gemma3:12b would otherwise invent one from the surrounding dungeon
    framing roughly a third of the time, the same failure mode `room_objects` below was already
    guarding against). `room_objects` is what is really on the room's floor right now (mandatory
    context, per that same request: stated truthfully, including "the floor is bare", rather than
    inviting the model to invent generic clutter that may not be there); since DELVE-0064 it is
    expected to already be formatted as one Markdown bullet per item, each carrying that item's own
    authored description alongside its name (`RunState._item_bullet`), not a bare comma-joined
    noun phrase, so the model has real material to draw on rather than just an object's name.
    `carrying` is the same for the learner's own backpack, blank clause omitted the same way, but
    framed as a deliberately brief, secondary mention rather than a second item to dwell on. `pet`
    names the learner's companion (species and name), blank if they play solo. `has_light` is
    whether the learner currently has a working torch (DELVE-0062): true reads as the usual
    scarce-torchlight framing, false darkens it to only the few paces they can feel their way
    through."""
    now = now or datetime.now()
    lesson_clause = f" This room teaches: {lesson_topic}." if lesson_topic else ""
    keeper_clause = (f" They are about to face {keeper}, whose room requires a score of "
                     f"{requirement} to pass." if keeper
                     else " No keeper is present in this room; do not invent one.")
    objects_clause = (f"On the floor of this room:\n{room_objects}" if room_objects
                      else "The floor of this room is bare.")
    carrying_clause = f"\n\nThe learner is carrying:\n{carrying}" if carrying else ""
    pet_clause = f" A {pet} follows the learner." if pet else ""
    setting = _language_setting(language, light=_LIGHT_ON if has_light else _LIGHT_OFF, dlvl=dlvl,
                                daypart=daypart(now.hour), weekday=_WEEKDAYS[now.weekday()])
    return PROMPT.format(pack=pack, dlvl=dlvl, chapter_title=chapter_title,
                        lesson_clause=lesson_clause, keeper_clause=keeper_clause,
                        objects_clause=objects_clause, carrying_clause=carrying_clause,
                        pet_clause=pet_clause, setting=setting, language=language)


NUDGE_PROMPT = (
    "You are writing a very short (1-2 sentence) in-character line for a text-based dungeon "
    "training game. {setting} The learner is exploring a training pack called {pack!r}, currently "
    "on chapter {dlvl} ({chapter_title}), and has been standing still since arriving."
    "{keeper_clause} Write a brief, encouraging line, in character, that tells the learner to use "
    "the arrow keys to move. Your line MUST explicitly name 'the arrow keys' (or the equivalent "
    "words in the reply language); do not just hint at moving without naming them. No "
    "instructions outside the story, no meta-commentary. Reply in {language}. Reply with ONLY the "
    "line, no preamble."
)


def build_nudge_prompt(*, pack: str, dlvl: int, chapter_title: str, language: str,
                       keeper: str = "", now: datetime | None = None) -> str:
    """DELVE-0061: a first-time learner's one-shot idle nudge, in the same room's keeper voice
    (or none, for an ungated starting room), asking the model for an in-character line that leads
    naturally to trying the arrow keys, rather than the ambient scene-setting `build_prompt` asks
    for. `keeper` blank omits the clause entirely, the same convention `build_prompt` uses."""
    now = now or datetime.now()
    keeper_clause = f" {keeper} is waiting nearby." if keeper else ""
    # A nudge fires only when the learner has not yet moved since arriving, so their starting
    # torch is still lit; the darkened clause is only ever reached through `build_prompt`.
    setting = _language_setting(language, light=_LIGHT_ON, dlvl=dlvl, daypart=daypart(now.hour),
                                weekday=_WEEKDAYS[now.weekday()])
    return NUDGE_PROMPT.format(pack=pack, dlvl=dlvl, chapter_title=chapter_title,
                              keeper_clause=keeper_clause, setting=setting, language=language)


class RoomBackstoryRunner:
    """One short passage per room, at most one call in flight at a time (mirroring
    `ThreadedGrader`'s own simplicity, since a learner can only be entering one new room at a time
    in practice), any further room queued behind it. `poll` pumps the queue and hands back the
    next resolved `(room_id, context, text)` triple the caller has not seen yet, one at a time, or
    `None` if nothing is ready; a room whose call fails or returns nothing simply never appears, no
    error, no retry, no gating. A run with no client configured makes `submit` a permanent no-op.

    `context` is opaque here (`RunState._poll_toast` packs in the keeper/chapter title plus the
    chapter index the room belongs to) and is carried through the queue rather than re-derived at
    resolution time: a call can resolve turns after it was queued, by which point the learner may
    already be on a different chapter, so deriving anything fresh from then-current state could
    label the toast for the wrong room, or show one for a floor the learner has since left
    entirely (this module has no notion of "chapter" itself; that check is the caller's own)."""

    def __init__(self, client=None, model: str | None = None, metrics=None):
        self.client = client
        # Overrides whatever model `client` is itself configured with, for every call this runner
        # makes (`OllamaClient.chat`'s own `model` override), so `RunState` can point ambient
        # prose at a deliberately different, more capable model than the grader's without a
        # second client object, which would lose the grader's own host/timeout/test double.
        # `None` (the default) just uses whatever the client is already configured with.
        self.model = model
        # The same `GraderMetrics` instance the configured `LLMGrader` uses, if any (duck-typed:
        # only `.record_call`/`.ambient_calls` are read, no `assess.grader` import, rule 1). A
        # playtesting note: the Grader tab used to show no change at all after an ambient toast,
        # even though a real call had just happened, because this runner never touched it.
        self.metrics = metrics
        self._queue: deque[tuple[str, object, str]] = deque()   # (room_id, context, prompt)
        self._current: str | None = None                        # room_id whose call is in flight
        self._ready: deque[tuple[str, object, str]] = deque()    # (room_id, context, text), unread
        self._thread: threading.Thread | None = None

    def submit(self, room_id: str, context: object, prompt: str) -> None:
        if self.client is None or room_id == self._current:
            return
        if any(rid == room_id for rid, _, _ in self._queue):
            return
        self._queue.append((room_id, context, prompt))
        self._pump()

    def _pump(self) -> None:
        if self._current is not None or not self._queue:
            return
        room_id, context, prompt = self._queue.popleft()
        self._current = room_id
        self._thread = threading.Thread(
            target=self._work, args=(room_id, context, prompt), daemon=True)
        self._thread.start()

    def _work(self, room_id: str, context: object, prompt: str) -> None:
        try:
            # Prose, not a verdict: unlike LLMGrader's call, this must not force JSON-mode output
            # (DELVE-0057, otherwise the model's only legal reply is the smallest valid JSON
            # document, `{}`) and wants some variety rather than grading's deterministic floor.
            reply = self.client.chat(prompt, json_mode=False, temperature=_TEMPERATURE,
                                    model=self.model)
            text = reply.text.strip()
            if self.metrics is not None:
                self.metrics.record_call(reply.metrics)
                self.metrics.ambient_calls += 1
        except LLMUnavailable:
            text = ""
        except Exception:                     # deliberately broader than the client's own
            # documented failure mode: this call now fires on every room entered, far
            # more often and far more casually than a deliberate grade, so a client that is missing,
            # malformed, or simply not shaped the way this call expects (a test double built only
            # for the grader tab's display, say) must still never surface as a crashed background
            # thread over something this optional. `LLMGrader`'s own contract stays narrow
            # (`LLMUnavailable` only); this one is intentionally wider.
            text = ""
        if text:
            self._ready.append((room_id, context, text))
        self._current = None

    def poll(self) -> tuple[str, object, str] | None:
        """Called once per built `Frame`: advances the queue (starts the next call if the current
        one just finished) and returns one unread resolved room, FIFO, or `None`."""
        self._pump()
        return self._ready.popleft() if self._ready else None

    def pending(self) -> bool:
        """Whether a call is queued, in flight, or resolved but not yet delivered by `poll`
        (`ui/app.py` reads this, via `Frame.toast_pending`, to decide whether to keep waking on a
        short timeout rather than blocking on the next keypress, DELVE-0060's own follow-up: a
        toast that finishes resolving while the learner is standing still used to only appear once
        they next pressed a key, since nothing rebuilt the `Frame` until then)."""
        return self._current is not None or bool(self._queue) or bool(self._ready)
