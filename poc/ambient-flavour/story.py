"""PoC (DELVE-0049, DELVE-0050): a continuous ambient story built alongside a simulated playthrough.

Take 2 on `ambient.py` (DELVE-0048), kept unchanged as the earlier, simpler baseline; this is a
separate script rather than an edit to it, so the two can be compared side by side. Same standing
as `ambient.py` and `../llm-grader`: a throwaway spike that deliberately reaches into
engine/session internals a real feature never would, and opens a socket directly from a script.
Nothing here is wired into the shipping engine or the pack format.

It drives a real pack through the same headless `RunState.apply(Command) -> Frame` harness the
project's own tests use to play a whole run (the BFS walk/approach/pass-room helpers are a
trimmed copy of tests/test_dungeon.py's, same as in ambient.py): walking, talking to keepers,
sitting examinations, consulting the pet once, brushing off an already-passed keeper once,
resting once per chapter. Every message a player would actually see is folded into a running
gameplay log.

DELVE-0050 changed the generation cadence from a 10-20 line batch dumped once per room to
**exactly one line at a time**, at two triggers: on arriving at a room (grounded in that room
specifically), and every `--step-interval` simulated steps while walking between rooms (grounded
in the current floor generically, since there is no single room to ground it in between keepers).
A `Pacer` tracks the step count and current context and fires generation through the same prompt
machinery DELVE-0049 built.

Each generated line still combines the current context with **every ambient line generated so far
this run** (DELVE-0049's continuity mechanism, `ambient_log`/`--ambient-window`), so a detail
invented early can recur later, and the whole pack aims to read as one place accreting detail
rather than a series of disconnected vignettes, now delivered as a drip alongside play instead of
a paragraph dumped at each doorway.

Output is a single chronological trail for the whole pack, gameplay lines and generated ambient
lines interleaved in the order they actually happened, from the first room to the last.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from delve import strings as strings_pkg  # noqa: E402
from delve.content.parser import load_pack  # noqa: E402
from delve.engine.world import Direction, Point, TileKind  # noqa: E402
from delve.session.commands import (  # noqa: E402
    Answer,
    AnswerText,
    Confirm,
    Consult,
    Descend,
    Move,
    Pickup,
    Rest,
    Talk,
)
from delve.session.run import new_game  # noqa: E402
from delve.session.views import FreeTextView, MenuView, PromptView  # noqa: E402

DEFAULT_MODEL = "qwen2.5:3b"
DEFAULT_HOST = "http://localhost:11434"

_CARD = {
    Point(0, -1): Direction.N,
    Point(0, 1): Direction.S,
    Point(1, 0): Direction.E,
    Point(-1, 0): Direction.W,
}
_ALL_DIRS = {d.delta: d for d in Direction}


# -- the trail: one ordered log for the whole pack, gameplay and ambient interleaved --------------


class Trail:
    """Everything that happened, in order: real gameplay messages and generated ambient lines,
    tagged so the two can be told apart or not, per `--tag`. `ambient_log` is the subset the model
    gets to see again next time (DELVE-0049's continuity mechanism): every ambient line ever
    generated this run, fed back into every later prompt."""

    def __init__(self, tag: bool):
        self.tag = tag
        self.entries: list[tuple[str, str]] = []   # (kind, text), kind is 'game' or 'ambient'
        self.ambient_log: list[str] = []

    def game(self, text: str) -> None:
        self.entries.append(("game", text))
        self._print("game", text)

    def ambient_batch(self, lines: list[str]) -> None:
        for line in lines:
            self.entries.append(("ambient", line))
            self.ambient_log.append(line)
            self._print("ambient", line)

    def note(self, text: str) -> None:
        """A section marker (a room heading), never fed to the model, only for readability."""
        print(text)

    def _print(self, kind: str, text: str) -> None:
        print(f"[{kind}] {text}" if self.tag else text)

    def write(self, path: Path) -> None:
        path.write_text("\n".join(text for _kind, text in self.entries) + "\n")


class Pacer:
    """DELVE-0050's cadence: one line on entering a room, one every `interval` simulated steps
    while walking between rooms. `gen(chapter, room)` does the actual generation and trail
    append; `room` is None while walking a corridor, so the prompt falls back to floor-only
    grounding (`_static_context`'s corridor case)."""

    def __init__(self, interval: int, gen):
        self.interval = interval
        self.gen = gen
        self.count = 0
        self.chapter = None
        self.room = None

    def set_context(self, chapter, room=None) -> None:
        self.chapter = chapter
        self.room = room

    def moved(self) -> None:
        if self.chapter is None or self.interval <= 0:
            return
        self.count += 1
        if self.count >= self.interval:
            self.count = 0
            self.gen(self.chapter, self.room)

    def entered_room(self, chapter, room) -> None:
        self.set_context(chapter, room)
        self.count = 0
        self.gen(chapter, room)


# -- walking the run, same BFS shape as tests/test_dungeon.py -------------------------------------


def _bfs_path(grid, start, goal, blocked=frozenset()):
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for d in _CARD:
            nxt = Point(cur.x + d.x, cur.y + d.y)
            if nxt not in prev and nxt not in blocked and grid.walkable(nxt.x, nxt.y):
                prev[nxt] = cur
                q.append(nxt)
    if goal not in prev:
        return None
    out, cur = [], goal
    while cur is not None:
        out.append(cur)
        cur = prev[cur]
    return out[::-1]


def _all_points(grid):
    return [Point(x, y) for y in range(grid.height) for x in range(grid.width)]


def _step(run, trail: Trail, cmd):
    """Apply one command and fold any freshly shown message line into the trail, the same lines a
    player would actually see (pickups, pet fetches, a consult, a brush-off, pass/fail feedback)."""
    frame = run.apply(cmd)
    for m in frame.messages:
        if m and (not trail.entries or trail.entries[-1] != ("game", m)):
            trail.game(m)
    return frame


def _walk(run, trail, path, pacer: Pacer):
    for a, b in zip(path, path[1:], strict=False):
        _step(run, trail, Move(_CARD[Point(b.x - a.x, b.y - a.y)]))
        pacer.moved()


def _approach(run, trail, keeper_pos, pacer: Pacer):
    blocked = set(run.keepers)
    targets = [
        Point(keeper_pos.x + dx, keeper_pos.y + dy)
        for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        if (dx or dy) and run.chapter.grid.walkable(keeper_pos.x + dx, keeper_pos.y + dy)
        and Point(keeper_pos.x + dx, keeper_pos.y + dy) not in blocked
    ]
    best = None
    for t in targets:
        p = _bfs_path(run.chapter.grid, run.player.pos, t, blocked)
        if p and (best is None or len(p) < len(best)):
            best = p
    assert best is not None, f"cannot reach keeper at {keeper_pos}"
    _walk(run, trail, best, pacer)


def _correct_index(gate):
    q = gate.current_question()
    return gate.display_options().index(q.options[q.answer_index].text)


def _bump_direction(run, target_pos):
    """The Direction (any of the 8) from the player's current tile to an orthogonally-or-
    diagonally adjacent target, for a deliberate bump (a brush-off demo)."""
    d = Point(target_pos.x - run.player.pos.x, target_pos.y - run.player.pos.y)
    return _ALL_DIRS.get(d)


def _pass_room(run, trail, gate, demo, chapter_content, room, pacer: Pacer):
    """Walk to the keeper, sit the examination answering everything correctly. Along the way: try
    picking something up once (harmless 'nothing here' when the room has nothing placed), and, the
    very first time this run reaches an eligible question, demonstrate a pet consult (`demo` is a
    shared dict of one-shot flags so each demo interaction fires only once per whole run). Right on
    arrival, before anything else, fire the room-entry ambient line (DELVE-0050)."""
    _approach(run, trail, gate.keeper.pos, pacer)
    pacer.entered_room(chapter_content, room)
    _step(run, trail, Pickup())
    frame = _step(run, trail, Talk())
    frame = _step(run, trail, Confirm(True))
    while isinstance(frame.overlay, (MenuView, PromptView, FreeTextView)):
        if isinstance(frame.overlay, FreeTextView):
            _step(run, trail, AnswerText(run.active.current_question().accept[0]))
        else:
            if demo.get("consult") and not demo["consult_done"]:
                _step(run, trail, Consult())
                demo["consult_done"] = True
            _step(run, trail, Answer(_correct_index(run.active)))
        frame = _step(run, trail, Confirm(True))
    return frame


def _brush_off_demo(run, trail, gate, demo):
    """Right after passing the very first room this run, bump into that same keeper again: a
    real, already-tested interaction (test_bumping_a_passed_keeper_is_a_brush_off) worth showing
    the model once, so the ambient log has more than 'walk, read, answer, pass' in it."""
    if not demo.get("brushoff") or demo["brushoff_done"]:
        return
    d = _bump_direction(run, gate.keeper.pos)
    if d is not None:
        _step(run, trail, Move(d))
    demo["brushoff_done"] = True


def _rest_demo(run, trail, demo):
    if demo.get("rest"):
        _step(run, trail, Rest())


def _stand_on(run, trail, kind, pacer: Pacer):
    tile = next(p for p in _all_points(run.chapter.grid)
                if run.chapter.grid.at(p.x, p.y).kind is kind)
    path = _bfs_path(run.chapter.grid, run.player.pos, tile, blocked=set(run.keepers))
    assert path is not None, f"cannot reach {kind}"
    _walk(run, trail, path, pacer)
    return tile


# -- prose context, from the pack itself, no invented flavour --------------------------------


def _lesson_prose(lesson, max_blocks: int = 6) -> str:
    """The room's authored body, joined plainly; capped so the prompt stays a reasonable size."""
    return "\n".join(b.text for b in lesson.blocks[:max_blocks])


def _static_context(pack, chapter, room=None) -> str:
    base = (
        f"Dungeon: {pack.title}\n{pack.intro.strip()}\n\n"
        f"Floor: {chapter.title}\n{chapter.intro.strip()}"
    )
    if room is None:
        return base + ("\n\nYou are walking a corridor on this floor, between rooms; no keeper "
                        "or lesson is nearby right now.")
    return base + (f"\n\nRoom: {room.lesson.title}, kept by {room.keeper_name}\n"
                    f"{_lesson_prose(room.lesson)}")


_LOCALE_INSTRUCTION = {
    "en": "Reply entirely in English.",
    "nl": "Reply entirely in Dutch (informal 'je' address, never 'u'; sentence case in any "
          "heading-like phrase), matching how this pack's own Dutch prose is written.",
}


# -- the model call, own copy of the seam: format=json but free-form, not the grader's fixed --
# -- ACCEPT/REJECT+confidence shape, and a non-zero temperature since this is generation, --
# -- not judgement (assess/llm.py:OllamaClient pins temperature 0 for a reason that doesn't --
# -- apply here) --------------------------------------------------------------------------------


class LLMUnavailable(Exception):
    pass


def _chat(host: str, model: str, prompt: str, temperature: float, timeout: int = 120) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {"temperature": temperature},
    }
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - local Ollama only
            body = json.loads(resp.read())
        return body["message"]["content"]
    except (urllib.error.URLError, TimeoutError, OSError, KeyError, json.JSONDecodeError) as exc:
        raise LLMUnavailable(str(exc)) from exc


_PROMPT = """You are writing brief ambient flavour lines for a text-based dungeon-crawler training \
game, styled like NetHack. Stay strictly in the voice and setting given below. Do not restate or \
summarise the lesson content, and do not mention the keeper's teaching directly; these are \
incidental sensory details a player might notice while exploring, not a recap. {locale}

Setting:
{static_context}

Recent gameplay events, oldest first, most recent last:
{event_lines}

Ambient details already established earlier in this same playthrough (you may bring one back for \
continuity, e.g. a sound or object mentioned before recurring, but you don't have to force it):
{ambient_lines}

Write {count_phrase}, {length_clause}, no numbering, no quotation marks, describing incidental \
detail happening right here, right now. Do not repeat a line, including lines already listed \
above. Reply with ONLY a JSON object of this shape: {{"lines": ["...", "..."]}}."""


def _count_phrase(count: int) -> str:
    return ("one short ambient one-liner" if count == 1
            else f"{count} short ambient one-liners")


def _length_clause(count: int) -> str:
    return ("under about 15 words" if count == 1
            else "each under about 15 words")


def _build_prompt(pack, chapter, room, trail: Trail, lang: str, window: int, ambient_window: int,
                   count: int) -> str:
    game_events = [t for k, t in trail.entries if k == "game"]
    recent = game_events[-window:] if window else game_events
    event_lines = "\n".join(f"- {e}" for e in recent) if recent else "(none yet)"
    ambient = trail.ambient_log[-ambient_window:] if ambient_window else trail.ambient_log
    ambient_lines = ("\n".join(f"- {e}" for e in ambient) if ambient
                      else "(none yet, this is the start of the run)")
    return _PROMPT.format(
        locale=_LOCALE_INSTRUCTION[lang],
        static_context=_static_context(pack, chapter, room),
        event_lines=event_lines,
        ambient_lines=ambient_lines,
        count_phrase=_count_phrase(count),
        length_clause=_length_clause(count),
    )


def _generate(host, model, temperature, pack, chapter, room, trail, lang, window, ambient_window,
              count):
    prompt = _build_prompt(pack, chapter, room, trail, lang, window, ambient_window, count)
    start = time.monotonic()
    try:
        content = _chat(host, model, prompt, temperature)
    except LLMUnavailable as exc:
        return None, time.monotonic() - start, f"(LLM unavailable: {exc})"
    elapsed = time.monotonic() - start
    try:
        lines = json.loads(content)["lines"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None, elapsed, f"(could not parse model output; raw reply below)\n{content}"
    return lines, elapsed, None


# -- CLI --------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--pack", default=str(REPO_ROOT / "packs" / "security-onboarding"),
                   help="pack directory holding en/ and nl/ (default: the pilot)")
    p.add_argument("--lang", default="en", choices=["en", "nl"])
    p.add_argument("--room", default=None, help="stop the walk once this room id is reached "
                   "(passed, its entry line generated); omit to walk the whole pack")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--pet", default="dog", choices=["cat", "dog", "none"],
                   help="dog fetches placed items on its own, giving more spontaneous events")
    p.add_argument("--count", type=int, default=1, help="one-liners requested per generation call "
                   "(DELVE-0050 default: 1, fired on room entry and every --step-interval steps, "
                   "rather than a 10-20 line batch once per room)")
    p.add_argument("--step-interval", type=int, default=5, help="generate one ambient line every "
                   "this many simulated steps while walking between rooms; 0 disables the "
                   "walking-cadence trigger (room-entry lines still fire)")
    p.add_argument("--window", type=int, default=8, help="how many recent gameplay events to feed "
                   "back per generation call; 0 means the whole gameplay log so far")
    p.add_argument("--ambient-window", type=int, default=24, help="how many of the most recent "
                   "generated ambient lines to feed back for continuity; 0 means all of them, "
                   "the whole story so far, which was found to make the model drift into another "
                   "language over a full pack walk (see README's 'Early observations'); capped by "
                   "default so the prompt doesn't grow unbounded")
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--grader-model", default=DEFAULT_MODEL)
    p.add_argument("--grader-host", default=DEFAULT_HOST)
    p.add_argument("--tag", action=argparse.BooleanOptionalAction, default=True,
                   help="prefix each trail line with [game]/[ambient] (default: on)")
    p.add_argument("--consult-demo", action=argparse.BooleanOptionalAction, default=True,
                   help="demonstrate one pet consult on the run's first eligible question")
    p.add_argument("--brushoff-demo", action=argparse.BooleanOptionalAction, default=True,
                   help="demonstrate bumping the first room's keeper again after passing it")
    p.add_argument("--rest-demo", action=argparse.BooleanOptionalAction, default=True,
                   help="demonstrate one Rest() per chapter")
    p.add_argument("--out", default=None, help="also write the plain (untagged) trail to this "
                   "file")
    args = p.parse_args(argv)

    engine_strings = strings_pkg.load(args.lang)
    pack = load_pack(Path(args.pack), args.lang)
    run = new_game(pack, seed=args.seed, cols=100, rows=30, pet_species=args.pet,
                   strings=engine_strings)
    trail = Trail(tag=args.tag)
    demo = {
        "consult": args.consult_demo and args.pet != "none",
        "consult_done": False,
        "brushoff": args.brushoff_demo,
        "brushoff_done": False,
        "rest": args.rest_demo,
    }

    def _gen(chapter, room):
        lines, _elapsed, err = _generate(
            args.grader_host, args.grader_model, args.temperature,
            pack, chapter, room, trail, args.lang, args.window, args.ambient_window, args.count,
        )
        if err:
            trail.note(err)
        elif lines:
            trail.ambient_batch(lines)

    pacer = Pacer(interval=args.step_interval, gen=_gen)

    target = args.room
    found = False
    for i, chapter_content in enumerate(pack.chapters):
        assert run.chapter.dlvl == i + 1
        pacer.set_context(chapter_content, None)
        _rest_demo(run, trail, demo)
        for room in chapter_content.rooms:
            gate = run.gates[room.id]
            if not gate.passed:
                _pass_room(run, trail, gate, demo, chapter_content, room, pacer)
                _brush_off_demo(run, trail, gate, demo)
            pacer.set_context(chapter_content, None)   # back in the corridor after this room
            if target is not None and room.id == target:
                found = True
                break
        if found:
            break
        if i < len(pack.chapters) - 1:
            _stand_on(run, trail, TileKind.STAIRS_DOWN, pacer)
            _step(run, trail, Descend())

    if args.out:
        trail.write(Path(args.out))
        print(f"\n[wrote {len(trail.entries)} lines to {args.out}]")

    if target and not found:
        print(f"delve-ambient: room {target!r} not found in this pack", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
