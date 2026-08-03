"""Pack variables (DELVE-0020): declare `{{tokens}}` in a template, fill from variables.md, and
substitute at view-build. Built-ins (`{{player}}`, `{{pack_title}}`) come from run state.
"""

from collections import deque
from pathlib import Path

from delve.content.parser import load_pack
from delve.content.variables import (
    BUILTINS,
    load_variables,
    parse_variables_md,
    substitute,
)
from delve.engine.world import Direction, Point
from delve.session.commands import Answer, Confirm, Move, Talk
from delve.session.run import new_game
from delve.session.views import MenuView, TextView
from delve.strings import load

PILOT = Path("packs/security-onboarding")

_CARD = {Point(0, -1): Direction.N, Point(0, 1): Direction.S,
         Point(1, 0): Direction.E, Point(-1, 0): Direction.W}

_ROOM = (
    "---\nid: r\nkeeper: wizard\nname: K\npass: 0.75\n---\n\n"
    "# Room\n\n"
    "Mail {{security_email}} or ask in {{help_channel}}.\n\n"
    "A literal `{brace}` in a code span stays put.\n\n"
    "## Questions\n\n"
    "### Who do you mail, {{player}}?\n\n"
    "- [ ] nobody\n"
    "- [x] {{security_email}}\n"
    "- [ ] spam\n\n"
    "> Reach {{help_channel}} when unsure.\n"
)


def _write_locale(base: Path, *, template: str, filled: str | None) -> None:
    base.mkdir(parents=True)
    (base / "pack.md").write_text(
        "---\nid: p\ntitle: Pack Title\ndifficulty: standard\nscroll: S\n---\n\n"
        "Welcome to {{organisation}}, {{player}}.\n",
        encoding="utf-8")
    (base / "scroll.md").write_text(
        "# S\n\n{name} scored {score}. Team: {{team}}.\n", encoding="utf-8")
    (base / "variables.template.md").write_text(template, encoding="utf-8")
    if filled is not None:
        (base / "variables.md").write_text(filled, encoding="utf-8")
    cdir = base / "01-chapter"
    cdir.mkdir()
    (cdir / "chapter.md").write_text(
        "---\nid: c\ntitle: C\n---\n\nFloor intro for {{organisation}}.\n", encoding="utf-8")
    (cdir / "01-room.md").write_text(_ROOM, encoding="utf-8")


def _pack_root(tmp_path: Path, *, en_filled: str | None = None, nl_filled: str | None = None,
               en_template: str | None = None, nl_template: str | None = None) -> Path:
    en_t = en_template or (
        "# Variables\n\n"
        "- `{{organisation}}`: Example Org\n"
        "- `{{security_email}}`: security@example.com\n"
        "- `{{help_channel}}`: #security-help\n"
        "- `{{team}}`: Security\n"
    )
    nl_t = nl_template or (
        "# Variabelen\n\n"
        "- `{{organisation}}`: Voorbeeld Org\n"
        "- `{{security_email}}`: security@example.com\n"
        "- `{{help_channel}}`: #security-help\n"
        "- `{{team}}`: Beveiliging\n"
    )
    _write_locale(tmp_path / "en", template=en_t, filled=en_filled)
    _write_locale(tmp_path / "nl", template=nl_t, filled=nl_filled)
    return tmp_path


def _open_first_lesson(root: Path, *, locale: str = "en", name: str = "Robin"):
    pack = load_pack(root, locale)
    run = new_game(pack, seed=1, cols=100, rows=30, name=name, strings=load(locale),
                   pet_species="none", skip_tutorial=True)
    grid = run.chapter.grid
    keeper = next(iter(run.keepers))
    blocked = set(run.keepers)

    def path(a, b):
        prev = {a: None}
        q = deque([a])
        while q:
            c = q.popleft()
            if c == b:
                break
            for d in _CARD:
                n = Point(c.x + d.x, c.y + d.y)
                if n not in prev and n not in blocked and grid.walkable(n.x, n.y):
                    prev[n] = c
                    q.append(n)
        if b not in prev:
            return None
        out, c = [], b
        while c is not None:
            out.append(c)
            c = prev[c]
        return out[::-1]

    targets = [Point(keeper.x + dx, keeper.y + dy)
               for dx in (-1, 0, 1) for dy in (-1, 0, 1)
               if (dx or dy) and grid.walkable(keeper.x + dx, keeper.y + dy)
               and Point(keeper.x + dx, keeper.y + dy) not in blocked]
    best = min((p for t in targets if (p := path(run.player.pos, t))), key=len)
    for a, b in zip(best, best[1:], strict=False):
        run.apply(Move(_CARD[Point(b.x - a.x, b.y - a.y)]))
    frame = run.apply(Talk())
    assert isinstance(frame.overlay, TextView)
    return run, frame


# -- pure substitute ---------------------------------------------------------------------------


def test_substitute_replaces_declared_tokens_and_leaves_stray_braces():
    values = {"security_email": "sec@acme.test", "help_channel": "#sec"}
    text = "Mail {{security_email}} or `{raw}` and {single}."
    assert substitute(text, values) == "Mail sec@acme.test or `{raw}` and {single}."


def test_substitute_is_deterministic_and_a_no_op_on_plain_prose():
    values = {"team": "Watch"}
    plain = "No tokens here."
    assert substitute(plain, values) == plain
    once = substitute("Join {{team}}", values)
    assert once == "Join Watch"
    assert substitute(once, values) == once


def test_parse_skips_builtins_in_the_file():
    text = "# V\n\n- `{{player}}`: ShouldNotWin\n- `{{team}}`: Ops\n"
    assert parse_variables_md("v.md", text) == {"team": "Ops"}
    assert "player" in BUILTINS


# -- load_pack merge ---------------------------------------------------------------------------


def test_load_pack_merges_filled_over_template_and_falls_back(tmp_path):
    root = _pack_root(
        tmp_path,
        en_filled="# V\n\n- `{{security_email}}`: real@acme.test\n",
    )
    pack = load_pack(root, "en")
    assert pack.variables["security_email"] == "real@acme.test"
    assert pack.variables["help_channel"] == "#security-help"   # template default
    assert pack.variables["organisation"] == "Example Org"


def test_load_pack_without_variables_md_uses_template_defaults(tmp_path):
    root = _pack_root(tmp_path, en_filled=None)
    assert load_pack(root, "en").variables["organisation"] == "Example Org"


def test_load_pack_without_template_has_empty_variables(tmp_path):
    base = tmp_path / "en"
    base.mkdir()
    (base / "pack.md").write_text(
        "---\nid: p\ntitle: T\ndifficulty: standard\nscroll: S\n---\n\nHi.\n", encoding="utf-8")
    (base / "scroll.md").write_text("# S\n", encoding="utf-8")
    cdir = base / "01-c"
    cdir.mkdir()
    (cdir / "chapter.md").write_text("---\nid: c\ntitle: C\n---\n\nIntro.\n", encoding="utf-8")
    (cdir / "01-r.md").write_text(
        "---\nid: r\nkeeper: wizard\nname: K\npass: 0.75\n---\n\n# R\n\n"
        "text\n\n## Questions\n\n### q?\n\n- [x] yes\n- [ ] no\n\n> because.\n",
        encoding="utf-8")
    assert load_pack(tmp_path, "en").variables == {}


# -- session surfaces --------------------------------------------------------------------------


def test_filled_tokens_appear_on_lesson_option_explanation_and_welcome(tmp_path):
    root = _pack_root(
        tmp_path,
        en_filled=(
            "# V\n\n"
            "- `{{organisation}}`: Acme Corp\n"
            "- `{{security_email}}`: sec@acme.test\n"
            "- `{{help_channel}}`: #acme-sec\n"
            "- `{{team}}`: Watch\n"
        ),
    )
    run, frame = _open_first_lesson(root, name="Robin")
    assert "Acme Corp" in run.messages[0]
    body = " ".join(b.text for b in frame.overlay.body)
    assert "sec@acme.test" in body and "#acme-sec" in body
    assert "{{security_email}}" not in body
    assert "{brace}" in body

    frame = run.apply(Confirm(True))
    assert isinstance(frame.overlay, MenuView)
    assert "Robin" in frame.overlay.prompt
    assert any(i.text == "sec@acme.test" for i in frame.overlay.items)

    correct = next(i for i, item in enumerate(frame.overlay.items) if item.text == "sec@acme.test")
    frame = run.apply(Answer(correct))
    assert isinstance(frame.overlay, TextView)
    expl = " ".join(b.text for b in frame.overlay.body)
    assert "#acme-sec" in expl


def test_missing_variables_md_falls_back_to_template(tmp_path):
    root = _pack_root(tmp_path, en_filled=None)
    _, frame = _open_first_lesson(root)
    body = " ".join(b.text for b in frame.overlay.body)
    assert "security@example.com" in body
    assert "#security-help" in body


def test_locales_resolve_independently(tmp_path):
    root = _pack_root(tmp_path)
    en = load_pack(root, "en")
    nl = load_pack(root, "nl")
    assert en.variables["team"] == "Security"
    assert nl.variables["team"] == "Beveiliging"
    assert en.variables["organisation"] == "Example Org"
    assert nl.variables["organisation"] == "Voorbeeld Org"


def test_player_builtin_wins_over_a_file_declaration(tmp_path):
    root = _pack_root(
        tmp_path,
        en_filled="# V\n\n- `{{player}}`: Impostor\n- `{{organisation}}`: Acme\n"
                  "- `{{security_email}}`: a@b.c\n- `{{help_channel}}`: #x\n- `{{team}}`: T\n",
    )
    assert "player" not in load_variables(tmp_path / "en")
    run, _ = _open_first_lesson(root, name="Robin")
    run.apply(Confirm(True))
    shown = run.frame().overlay
    prompt = shown.prompt if isinstance(shown, MenuView) else shown.text
    assert "Robin" in prompt
    assert "Impostor" not in prompt


def test_pilot_ships_template_and_substitutes_defaults():
    pack = load_pack(PILOT, "en")
    assert pack.variables["security_email"] == "security@example.com"
    assert pack.variables["tier_public"] == "Public"
    nl = load_pack(PILOT, "nl")
    assert nl.variables["tier_public"] == "Openbaar"
    room = next(r for c in pack.chapters for r in c.rooms if r.id == "reporting")
    prose = " ".join(b.text for b in room.lesson.blocks)
    assert "{{security_email}}" in prose
