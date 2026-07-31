"""PoC (DELVE-0048): generate ambient one-liners along a simulated game path, using the local LLM.

A throwaway spike, in the shape of ../llm-grader: it deliberately reaches into engine/session
internals a real feature never would, and opens a socket directly from a script. Nothing here is
wired into the shipping engine or the pack format.

It drives a real pack through the same headless `RunState.apply(Command) -> Frame` harness the
project's own tests use to play a whole run (see tests/test_dungeon.py's `_path`/`_walk`/
`_pass_room`, copied and trimmed here rather than imported, since tests/ is not a package this
lives outside of), collecting a rolling log of what actually happened along the way: message
lines, item pickups, pet events. At each room, that dynamic log is combined with the room's (and
its chapter's, and its pack's) own authored prose into one prompt, asking the model for a batch of
short ambient one-liners that could plausibly appear at that exact point in that specific run.

This answers a narrower question than "can an LLM write flavour text": can it write flavour text
that visibly differs depending on what already happened on the way there. See DELVE-0048's
acceptance criteria for how to judge a run's output.
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

from delve.content.parser import load_pack  # noqa: E402
from delve.engine.world import Direction, Point, TileKind  # noqa: E402
from delve.session.commands import (  # noqa: E402
    Answer,
    AnswerText,
    Confirm,
    Descend,
    Move,
    Pickup,
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


def _step(run, events: list[str], cmd):
    """Apply one command and fold any freshly shown message line into the running event log,
    the same lines a player would actually see (pickups, pet fetches, pass/fail feedback)."""
    frame = run.apply(cmd)
    for m in frame.messages:
        if m and (not events or events[-1] != m):
            events.append(m)
    return frame


def _walk(run, events, path):
    for a, b in zip(path, path[1:], strict=False):
        _step(run, events, Move(_CARD[Point(b.x - a.x, b.y - a.y)]))


def _approach(run, events, keeper_pos):
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
    _walk(run, events, best)


def _correct_index(gate):
    q = gate.current_question()
    return gate.display_options().index(q.options[q.answer_index].text)


def _pass_room(run, events, gate):
    """Walk to the keeper, sit the examination answering everything correctly, and along the way
    try picking something up once: best-effort ambient colour, harmless ('nothing here') when the
    room has nothing placed."""
    _approach(run, events, gate.keeper.pos)
    _step(run, events, Pickup())
    frame = _step(run, events, Talk())
    frame = _step(run, events, Confirm(True))
    while isinstance(frame.overlay, (MenuView, PromptView, FreeTextView)):
        if isinstance(frame.overlay, FreeTextView):
            _step(run, events, AnswerText(run.active.current_question().accept[0]))
        else:
            _step(run, events, Answer(_correct_index(run.active)))
        frame = _step(run, events, Confirm(True))
    return frame


def _stand_on(run, events, kind):
    tile = next(p for p in _all_points(run.chapter.grid)
                if run.chapter.grid.at(p.x, p.y).kind is kind)
    path = _bfs_path(run.chapter.grid, run.player.pos, tile, blocked=set(run.keepers))
    assert path is not None, f"cannot reach {kind}"
    _walk(run, events, path)
    return tile


# -- prose context, from the pack itself, no invented flavour --------------------------------


def _lesson_prose(lesson, max_blocks: int = 6) -> str:
    """The room's authored body, joined plainly; capped so the prompt stays a reasonable size."""
    return "\n".join(b.text for b in lesson.blocks[:max_blocks])


def _static_context(pack, chapter, room) -> str:
    return (
        f"Dungeon: {pack.title}\n{pack.intro.strip()}\n\n"
        f"Floor: {chapter.title}\n{chapter.intro.strip()}\n\n"
        f"Room: {room.lesson.title}, kept by {room.keeper_name}\n{_lesson_prose(room.lesson)}"
    )


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
incidental sensory details a player might notice while exploring, not a recap.

Setting:
{static_context}

Recent events on this playthrough, oldest first, most recent last:
{event_lines}

Write {count} short ambient one-liners (each under about 15 words, no numbering, no quotation \
marks) describing incidental detail happening in this specific room right now. Ground them in the \
setting above; where it fits naturally, let a line react to one of the recent events, but not \
every line needs to. Do not repeat a line. Reply with ONLY a JSON object of this shape: \
{{"lines": ["...", "..."]}}."""


def _build_prompt(pack, chapter, room, events: list[str], window: int, count: int) -> str:
    recent = events[-window:] if window else events
    event_lines = "\n".join(f"- {e}" for e in recent) if recent else "(none yet)"
    return _PROMPT.format(
        static_context=_static_context(pack, chapter, room),
        event_lines=event_lines,
        count=count,
    )


def _generate(host, model, temperature, pack, chapter, room, events, window, count):
    prompt = _build_prompt(pack, chapter, room, events, window, count)
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
    p.add_argument("--room", default=None, help="only generate for this room id; the path still "
                   "walks the whole pack up to and including it")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--pet", default="dog", choices=["cat", "dog", "none"],
                   help="dog fetches placed items on its own, giving more spontaneous events")
    p.add_argument("--count", type=int, default=15, help="one-liners requested per room (10-20)")
    p.add_argument("--window", type=int, default=8, help="how many recent events to feed back; "
                   "0 means the whole log so far")
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--grader-model", default=DEFAULT_MODEL)
    p.add_argument("--grader-host", default=DEFAULT_HOST)
    args = p.parse_args(argv)

    pack = load_pack(Path(args.pack), args.lang)
    run = new_game(pack, seed=args.seed, cols=100, rows=30, pet_species=args.pet)
    events: list[str] = []

    target = args.room
    found = False
    for i, chapter_content in enumerate(pack.chapters):
        assert run.chapter.dlvl == i + 1
        for room in chapter_content.rooms:
            gate = run.gates[room.id]
            if not gate.passed:
                _pass_room(run, events, gate)
            if target is None or room.id == target:
                found = found or room.id == target
                lines, elapsed, err = _generate(
                    args.grader_host, args.grader_model, args.temperature,
                    pack, chapter_content, room, events, args.window, args.count,
                )
                print(f"\n=== {chapter_content.id}/{room.id} ({elapsed:.1f}s) ===")
                print(f"[event log so far: {len(events)} lines, feeding last "
                      f"{args.window or len(events)}]")
                if err:
                    print(err)
                else:
                    for line in lines:
                        print(f"  - {line}")
        if i < len(pack.chapters) - 1:
            _stand_on(run, events, TileKind.STAIRS_DOWN)
            _step(run, events, Descend())

    if target and not found:
        print(f"delve-ambient: room {target!r} not found in this pack", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
