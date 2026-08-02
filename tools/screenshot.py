#!/usr/bin/env python3
"""Print a real Delve screen (ANSI colour) for a named scenario, driven by the live renderer.

    ./tools.sh screenshot                 # list scenarios
    ./tools.sh screenshot mcq             # one frame, colour on a tty
    ./tools.sh screenshot tutorial --plain

Drives a real RunState with real Commands to the named panel state, then paints through
`delve.ui.render.draw` onto the shared CursesEmu (tools/_fakescreen.py). No parallel mock
renderer: what you see is what the game draws. Colour comes from the same attrs.py pair map the
live terminal uses; set NO_COLOR or pipe to a file for plain characters.
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass, replace
from pathlib import Path

# tools/ is sys.path[0] when run as `python tools/screenshot.py` / via tools.sh.
from _fakescreen import (  # noqa: E402
    CursesEmu,
    ansi_render,
    colour_wanted,
    enable_fake_acs,
    enable_fake_colour,
)

from delve import strings as strings_pkg
from delve.content.parser import load_pack
from delve.content.pilot import PHISHING_ROOM
from delve.engine.world import Direction, Point
from delve.session.commands import (
    Answer,
    BuyRemoval,
    Confirm,
    Drop,
    Help,
    Inventory,
    Move,
    Select,
    TabCycle,
    Talk,
)
from delve.session.launch import load_tutorial
from delve.session.run import new_game, new_run
from delve.session.views import Frame, MenuView, PromptView, TextBlock, ToastView
from delve.ui import render

COLS, ROWS = 100, 30
ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "packs" / "security-onboarding"

_CARD = {
    Point(0, -1): Direction.N,
    Point(0, 1): Direction.S,
    Point(1, 0): Direction.E,
    Point(-1, 0): Direction.W,
}


@dataclass(frozen=True)
class Shot:
    """One captured frame ready to paint."""

    frame: Frame
    page: int = 1
    msg_page: int = 1


def _path(grid, start, goal, blocked):
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


def _approach(run):
    keeper = run.gates["phishing"].keeper.pos
    blocked = set(run.keepers)
    targets = [
        Point(keeper.x + dx, keeper.y + dy)
        for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        if (dx or dy) and run.chapter.grid.walkable(keeper.x + dx, keeper.y + dy)
        and Point(keeper.x + dx, keeper.y + dy) not in blocked
    ]
    best = min(
        (p for t in targets if (p := _path(run.chapter.grid, run.player.pos, t, blocked))),
        key=len,
    )
    for a, b in zip(best, best[1:], strict=False):
        run.apply(Move(_CARD[Point(b.x - a.x, b.y - a.y)]))


def _correct(run) -> int:
    g = run.active
    q = g.current_question()
    return g.display_options().index(q.options[q.answer_index].text)


def _wrong(run) -> int:
    g = run.active
    q = g.current_question()
    wrong = next(o for o in q.options if not o.correct)
    return g.display_options().index(wrong.text)


def _sit(run, choose):
    frame = run.apply(Confirm(True))
    while isinstance(frame.overlay, (MenuView, PromptView)):
        frame = run.apply(Answer(choose(run)))
        frame = run.apply(Confirm(True))
    return frame


def _exam_run(*, reward: int = 100, gold: int = 200, seed: int = 7, lang: str = "en"):
    strings = strings_pkg.load(lang)
    run = new_run(seed=seed, cols=COLS, rows=ROWS, pet_species="none",
                  strings=strings, name="Ada" if lang == "en" else "Ada")
    gate = run.gates["phishing"]
    gate.content = replace(PHISHING_ROOM, reward=reward)
    run.player.gold = gold
    return run


def _open_mcq(run):
    _approach(run)
    run.apply(Talk())
    frame = run.apply(Confirm(True))
    assert isinstance(frame.overlay, MenuView)
    return frame


# -- scenarios ---------------------------------------------------------------------------------


def sc_tutorial() -> Shot:
    """The tutorial floor's first screen (Dlvl 0), standing at the entrance."""
    tutorial = load_tutorial("en")
    pack = load_pack(PILOT, "en")
    strings = strings_pkg.load("en")
    run = new_game(pack, seed=7, cols=COLS, rows=ROWS, name="Ada", strings=strings,
                   tutorial=tutorial, skip_tutorial=False, pet_species="none")
    return Shot(run.frame())


def sc_arrival() -> Shot:
    """Arrival on the M2 slice (Dlvl 1), no panel open."""
    run = new_run(seed=99, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    return Shot(run.frame())


def sc_lesson() -> Shot:
    """Ada's lesson panel, page 1."""
    run = new_run(seed=99, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    _approach(run)
    return Shot(run.apply(Talk()), page=1)


def sc_mcq() -> Shot:
    """The first phishing MCQ, four options showing."""
    run = _exam_run()
    return Shot(_open_mcq(run))


def sc_mcq_eliminated() -> Shot:
    """The first phishing MCQ after one paid removal (the eliminated option is A_DIM)."""
    run = _exam_run()
    _open_mcq(run)
    return Shot(run.apply(BuyRemoval()))


def sc_assertion() -> Shot:
    """An assertion (two-option) question, English."""
    run = _exam_run()
    _approach(run)
    run.apply(Talk())
    run.apply(Confirm(True))
    run.apply(Answer(_correct(run)))
    frame = run.apply(Confirm(True))
    # Skip the explanation to land on Q2 (assertion).
    while not isinstance(frame.overlay, PromptView):
        frame = run.apply(Confirm(True))
    return Shot(frame)


def sc_assertion_nl() -> Shot:
    """An assertion in Dutch (Waar / Niet waar)."""
    run = _exam_run(lang="nl")
    # Dutch pack content for the slice still uses the English pilot room text; the PromptView
    # chrome (connector, footer, keys) comes from the Dutch strings catalogue.
    _approach(run)
    run.apply(Talk())
    run.apply(Confirm(True))
    run.apply(Answer(_correct(run)))
    frame = run.apply(Confirm(True))
    while not isinstance(frame.overlay, PromptView):
        frame = run.apply(Confirm(True))
    return Shot(frame)


def sc_explanation() -> Shot:
    """A right-answer explanation panel."""
    run = _exam_run()
    _open_mcq(run)
    run.apply(Answer(_correct(run)))
    return Shot(run.apply(Confirm(True)))


def sc_door() -> Shot:
    """The door appears after a clean pass; bare map, no panel."""
    run = _exam_run()
    _approach(run)
    run.apply(Talk())
    _sit(run, _correct)
    return Shot(run.frame())


def sc_repelled() -> Shot:
    """REPELLED after three failed sittings at standard stakes."""
    run = new_run(seed=99, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    _approach(run)
    frame = None
    for _ in range(3):
        run.apply(Talk())
        frame = _sit(run, _wrong)
    assert frame is not None and frame.overlay is not None
    return Shot(frame)


def sc_two_rooms() -> Shot:
    """Two rooms connected by a corridor after the first door is earned. Room 1 stays visible
    (dimmed, already `discovered`) once room 2 is lit; vision only reveals a room fully from
    inside it or a corridor tile-by-tile (`delve.engine.vision.lit_tiles`), so reaching the door
    is not enough, the walk has to continue into room 2 itself (playtesting note, DELVE-0092)."""
    run = _exam_run()
    _approach(run)
    run.apply(Talk())
    _sit(run, _correct)
    door = run.chapter.exits["phishing"]
    blocked = set(run.keepers)
    to_door = _path(run.chapter.grid, run.player.pos, door, blocked=blocked)
    assert to_door is not None
    next_room = next(r for r in run.chapter.rooms if r.id != "phishing")
    to_room2 = _path(run.chapter.grid, door, next_room.center, blocked=blocked)
    assert to_room2 is not None
    for a, b in zip(to_door + to_room2[1:], (to_door + to_room2[1:])[1:], strict=False):
        run.apply(Move(_CARD[Point(b.x - a.x, b.y - a.y)]))
    return Shot(run.frame())


def sc_scroll_en() -> Shot:
    """The award scroll (English fallback body on the M2 slice, which has no pack scroll.md)."""
    run = new_run(seed=1, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    run._overlay = run._scroll_overlay()
    run._overlay_kind = "scroll"
    return Shot(run.frame())


def sc_scroll_nl() -> Shot:
    """The award scroll in Dutch."""
    strings = strings_pkg.load("nl")
    run = new_run(seed=1, cols=COLS, rows=ROWS, pet_species="none", name="Ada", strings=strings)
    run._overlay = run._scroll_overlay()
    run._overlay_kind = "scroll"
    return Shot(run.frame())


def sc_reward() -> Shot:
    """A reward coin on the floor after a clean pass (random interior tile)."""
    run = _exam_run(reward=100)
    _approach(run)
    run.apply(Talk())
    _sit(run, _correct)
    return Shot(run.frame())


def sc_inventory() -> Shot:
    """The Info / Pack panel with some carried gold."""
    run = new_run(seed=99, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    run.player.gold = 70
    return Shot(run.apply(Inventory()))


def sc_drop_amount() -> Shot:
    """The drop-amount field over the pack."""
    run = new_run(seed=99, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    run.player.gold = 70
    frame = run.apply(Inventory())
    coin_label = run._coins(70)
    idx = next(i for i, label in enumerate(frame.overlay.pack_rows) if coin_label in label)
    while frame.overlay.pack_selected != idx:
        frame = run.apply(Select(1))
    return Shot(run.apply(Drop()))


def sc_help() -> Shot:
    """The ? help panel, Keys tab."""
    run = new_run(seed=1, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    return Shot(run.apply(Help()))


def sc_toast() -> Shot:
    """The ambient room-entry toast (synthetic text; no LLM call)."""
    run = new_run(seed=1, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    run._toast = ToastView(
        title="The Sorting Office",
        body=[TextBlock("para",
                        "Dust motes hang in the lamplight. Somewhere ahead, a keeper waits.")],
    )
    run._toast_turn = run.turn
    return Shot(run.frame())


def sc_grader() -> Shot:
    """Info / Grader tab with both model sections and at least one Latency sparkline."""
    from delve.assess.grader import LLMGrader
    from delve.assess.llm import ChatMetrics

    class FakeClient:
        model = "qwen2.5:3b"
        host = "http://localhost:11434"

    grader = LLMGrader(FakeClient())
    for ms in (200, 400, 350):
        grader.metrics.record_call(ChatMetrics(total_duration_ms=ms, load_duration_ms=0,
                                               prompt_tokens=180, completion_tokens=40))
    grader.metrics.llm_verdicts = 3
    run = new_run(seed=1, cols=COLS, rows=ROWS, pet_species="none", name="Ada")
    run._grader_runner = type("R", (), {"grader": grader})()
    for ms in (500, 800):
        run._ambient_metrics.record_call(ChatMetrics(total_duration_ms=ms, load_duration_ms=0,
                                                     prompt_tokens=50, completion_tokens=20))
    run._ambient_metrics.ambient_calls = 2
    run.apply(Inventory())
    return Shot(run.apply(TabCycle(2)))


SCENARIOS: dict[str, tuple[str, Callable[[], Shot]]] = {
    "tutorial": ("Tutorial floor (Dlvl 0), first screen", sc_tutorial),
    "arrival": ("Arrival on Dlvl 1, bare map", sc_arrival),
    "lesson": ("Keeper lesson panel (Ada, page 1)", sc_lesson),
    "mcq": ("Examination: four-option MCQ", sc_mcq),
    "mcq-eliminated": ("MCQ after one paid removal (dim option)", sc_mcq_eliminated),
    "assertion": ("Examination: assertion prompt", sc_assertion),
    "assertion-nl": ("Assertion chrome in Dutch", sc_assertion_nl),
    "explanation": ("Right-answer explanation panel", sc_explanation),
    "door": ("Door appears after a clean pass", sc_door),
    "repelled": ("REPELLED after three failed sittings", sc_repelled),
    "two-rooms": ("Two rooms and a corridor", sc_two_rooms),
    "scroll": ("Award scroll (English)", sc_scroll_en),
    "scroll-nl": ("Award scroll (Dutch)", sc_scroll_nl),
    "reward": ("On-pass reward coin on the floor", sc_reward),
    "inventory": ("Info / Pack panel", sc_inventory),
    "drop-amount": ("Drop-how-many amount field", sc_drop_amount),
    "help": ("Help panel, Keys tab", sc_help),
    "toast": ("Ambient room-entry toast", sc_toast),
    "grader": ("Info / Grader tab, two columns with sparklines", sc_grader),
}


def capture(name: str, *, ascii_walls: bool = False) -> CursesEmu:
    """Drive the named scenario and paint it onto a fresh CursesEmu. Public entry for tests.

    Rooms paint through box-drawing glyphs by default (`enable_fake_acs`), the same as a real
    terminal with a working alternate character set would show a learner; `ascii_walls=True` shows
    `walls.py`'s own ASCII stand-in instead (what an ACS-incapable terminal falls back to)."""
    if name not in SCENARIOS:
        raise KeyError(name)
    _summary, fn = SCENARIOS[name]
    shot = fn()
    scr = CursesEmu(ROWS, COLS)
    with ExitStack() as stack:
        stack.enter_context(enable_fake_colour())
        if not ascii_walls:
            stack.enter_context(enable_fake_acs())
        render.draw(scr, shot.frame, page=shot.page, msg_page=shot.msg_page)
    return scr


def render_scenario(name: str, *, colour: bool = False, ascii_walls: bool = False) -> str:
    """Paint a scenario and return the grid as a string (ANSI when colour=True)."""
    scr = capture(name, ascii_walls=ascii_walls)
    return ansi_render(scr, colour=colour)


def list_scenarios() -> str:
    lines = ["available scenarios:"]
    for name, (summary, _) in SCENARIOS.items():
        lines.append(f"  {name:<18} {summary}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Print a real Delve screen for a named scenario (live renderer, ANSI colour).",
    )
    ap.add_argument("scenario", nargs="?", help="scenario name; omit to list")
    ap.add_argument("--all", action="store_true",
                    help="print every scenario in turn (each headed by its name), to eyeball the "
                         "whole set in one pass; ignores a given scenario name")
    ap.add_argument("--plain", action="store_true",
                    help="force plain characters (also the default when not a tty / NO_COLOR)")
    ap.add_argument("--colour", "--color", action="store_true",
                    help="force ANSI colour even when stdout is not a tty")
    ap.add_argument("--ascii-walls", action="store_true",
                    help="show walls.py's own ASCII wall stand-in ('-'/'|') instead of the "
                         "box-drawing glyphs a real terminal's alternate character set draws "
                         "(the default)")
    args = ap.parse_args(argv)

    if not args.scenario and not args.all:
        print(list_scenarios())
        return 0

    if args.plain:
        use_colour = False
    elif args.colour:
        use_colour = True
    else:
        use_colour = colour_wanted()

    if args.all:
        for i, name in enumerate(SCENARIOS):
            if i:
                print()
            print(f"--- {name} {'-' * max(0, 76 - len(name))}")
            print(render_scenario(name, colour=use_colour, ascii_walls=args.ascii_walls))
        return 0

    if args.scenario not in SCENARIOS:
        print(f"screenshot: unknown scenario {args.scenario!r}", file=sys.stderr)
        print(list_scenarios(), file=sys.stderr)
        return 1

    print(render_scenario(args.scenario, colour=use_colour, ascii_walls=args.ascii_walls))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
