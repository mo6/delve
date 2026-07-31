"""Markdown pack to content objects. This layer knows the *pack*: a room file is frontmatter,
an H1 title, a lesson, and a `## Questions` section; a question is an H3 and the options under it
(AUTHORING.md sections 6-10). It never sees a raw line; markup.py hands it tokens.

The split with schema.py is deliberate. The parser enforces the **format** and raises a
`PackError` (file:line) the moment a single file can't be a valid room. schema.py enforces the
**pack policy** that spans files, chapter capacity and locale-tree parity, and gathers those as
`Issue`s. So a broken file stops at its first structural error, while a whole-pack run still
reports every capacity and parity problem at once.

Question type is inferred from option count and never declared (CLAUDE.md 'Question format'), so
nothing here reads a label: two options is an assertion, three or more is multiple choice, in any
language. The parser produces the same `Room` object the M2 slice hard-codes, which is the pilot's
golden test.
"""

from pathlib import Path

from delve.assess.question import Option, Question
from delve.content.errors import PackError
from delve.content.lesson import Block, Lesson
from delve.content.markup import LESSON_KINDS, Token, tokenize
from delve.content.pack import Chapter, Pack, Room
from delve.engine.items import ItemDef

KEEPERS = ("wizard", "shopkeeper", "gatekeeper")
DIFFICULTIES = ("relaxed", "standard", "strict")
# The frontmatter keys an item file may set (OBJECTS.md section 9). The effect vocabulary is closed:
# an unknown key is a pack error, so a typo'd `on_moove` fails loudly rather than doing nothing.
ITEM_KEYS = {"id", "glyph", "colour", "name", "plural", "on_pickup", "on_pickup_plural",
             "on_move", "on_move_short", "on_move_min", "value", "bulky"}


# -- frontmatter --------------------------------------------------------------------------------


def split_frontmatter(text: str, path: str):
    """Return (values, key_lines, body, body_offset), or None when there's no frontmatter (the
    scroll has none). `body_offset` is the count of consumed lines, so tokenize points at the
    real file line. Frontmatter is flat `key: value` only, parsed by hand: it is metadata by
    design (CLAUDE.md rule 5), never nested, so it needs no YAML dependency."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    close = next((k for k in range(1, len(lines)) if lines[k].strip() == "---"), None)
    if close is None:
        raise PackError(path, 1, "frontmatter opened with '---' but is never closed")
    values: dict[str, str] = {}
    key_lines: dict[str, int] = {}
    for idx in range(1, close):
        raw = lines[idx]
        if not raw.strip():
            continue
        if ":" not in raw:
            raise PackError(path, idx + 1, f"frontmatter line is not 'key: value': {raw.strip()!r}")
        key, _, val = raw.partition(":")
        values[key.strip()] = val.strip()
        key_lines[key.strip()] = idx + 1
    return values, key_lines, "\n".join(lines[close + 1:]), close + 1


def _require(values, key_lines, keys, path):
    for key in keys:
        if not values.get(key):
            line = key_lines.get(key, 1)
            raise PackError(path, line, f"frontmatter is missing required key {key!r}")


def _float(values, key_lines, key, path, default):
    if key not in values:
        return default
    try:
        return float(values[key])
    except ValueError:
        raise PackError(path, key_lines[key], f"{key!r} must be a number, not {values[key]!r}") \
            from None


def _int(values, key_lines, key, path):
    if key not in values:
        return None
    try:
        return int(values[key])
    except ValueError:
        raise PackError(path, key_lines[key],
                        f"{key!r} must be a whole number, not {values[key]!r}") from None


def _reward(values, key_lines, path, default):
    """The `reward:` coins, validated non-negative. Absent means `default` (None for a room, so it
    inherits the pack; 0 for the pack). Negative coins are a pack error (OBJECTS.md)."""
    n = _int(values, key_lines, "reward", path)
    if n is None:
        return default
    if n < 0:
        raise PackError(path, key_lines["reward"], f"'reward' must be zero or more, not {n}")
    return n


def _bool(values, key_lines, key, path):
    if key not in values:
        return False
    v = values[key].strip().lower()
    if v in ("true", "yes", "1"):
        return True
    if v in ("false", "no", "0"):
        return False
    raise PackError(path, key_lines[key], f"{key!r} must be true or false, not {values[key]!r}")


def _placements(values, key_lines, path):
    """Parse a room's `place:` line into (def-id, count) pairs. `place: coconut-half x2, usb-stick`
    scatters a stack of two coconut halves and one USB stick. Count defaults to 1; a bad count or an
    empty id is a pack error. The def-id is *not* resolved here (schema.py checks it names a real,
    defined kind, gathering that with every other cross-file issue)."""
    raw = values.get("place")
    if not raw:
        return ()
    line = key_lines.get("place", 1)
    out: list[tuple[str, int]] = []
    for part in raw.split(","):
        token = part.strip()
        if not token:
            continue
        name, _, count = token.rpartition(" x")
        if name:                                  # matched '<id> xN'
            try:
                n = int(count)
            except ValueError:
                raise PackError(path, line,
                                f"place count must be a whole number, not {count!r}") from None
            if n < 1:
                raise PackError(path, line, f"place count must be one or more, not {n}")
            out.append((name.strip(), n))
        else:                                     # a bare id, count 1
            out.append((token, 1))
    return tuple(out)


# -- rooms --------------------------------------------------------------------------------------


def parse_room(path: str, text: str) -> Room:
    fm = split_frontmatter(text, path)
    if fm is None:
        raise PackError(path, 1, "a room file needs frontmatter with id, keeper, name and pass")
    values, key_lines, body, offset = fm
    _require(values, key_lines, ("id",), path)

    keeper = values.get("keeper", "gatekeeper")
    if keeper not in KEEPERS:
        raise PackError(path, key_lines.get("keeper", 1),
                        f"keeper must be one of {', '.join(KEEPERS)}, not {keeper!r}")
    pass_mark = _float(values, key_lines, "pass", path, 0.75)
    if not 0.0 <= pass_mark <= 1.0:
        raise PackError(path, key_lines.get("pass", 1),
                        f"pass must be between 0 and 1, not {pass_mark}")

    tokens = tokenize(body, offset)
    lesson, question_tokens = _lesson_and_questions(tokens, path)
    questions = _parse_questions(question_tokens, path)
    if not questions:
        raise PackError(path, 1, "a room needs at least one question after '## Questions'")

    return Room(
        id=values["id"],
        keeper_name=values.get("name", ""),
        keeper_kind=keeper,
        lesson=lesson,
        questions=tuple(questions),
        pass_mark=pass_mark,
        attempts=_int(values, key_lines, "attempts", path),
        penalty=_int(values, key_lines, "penalty", path),
        reward=_reward(values, key_lines, path, None),
        placements=_placements(values, key_lines, path),
    )


def _lesson_and_questions(tokens: list[Token], path: str) -> tuple[Lesson, list[Token]]:
    title = next((t.text for t in tokens if t.kind == "heading" and t.level == 1), None)
    if title is None:
        raise PackError(path, 1, "a room needs an H1 title above the lesson (e.g. '# Phishing')")

    split = next((i for i, t in enumerate(tokens)
                  if t.kind == "heading" and t.level == 2 and t.text == "Questions"), None)
    if split is None:
        raise PackError(path, 1, "a room needs a '## Questions' section")

    blocks: list[Block] = []
    for t in tokens[:split]:
        if t.kind in LESSON_KINDS:
            blocks.append(Block(t.kind, t.text, spans=t.spans, table=t.rows))
        elif t.kind == "heading" and t.level > 1:
            # a lesson subheading, folded to a paragraph (no heading style in the panel yet)
            blocks.append(Block("para", t.text))
    return Lesson(title=title, blocks=tuple(blocks)), tokens[split + 1:]


def _split_set(text: str) -> tuple[str, ...]:
    """A comma-separated rubric line (`?answer:` / `?reject:`) into a tuple of trimmed phrases,
    dropping the empties, so a trailing comma or extra spaces never produce a blank reference."""
    return tuple(p.strip() for p in text.split(",") if p.strip())


def _parse_questions(tokens: list[Token], path: str) -> list[Question]:
    questions: list[Question] = []
    prompt = prompt_line = None
    options: list[Option] = []
    accept: tuple[str, ...] | None = None    # None until a `?answer:` line marks this free text
    reject: tuple[str, ...] = ()
    explanation: str | None = None

    def flush():
        nonlocal prompt, options, accept, reject, explanation
        if prompt is None:
            return
        questions.append(
            _build_question(prompt, prompt_line, options, accept, reject, explanation, path))
        prompt, options, accept, reject, explanation = None, [], None, (), None

    for t in tokens:
        if t.kind == "heading" and t.level == 3:
            flush()
            prompt, prompt_line = t.text, t.line
        elif prompt is None:
            continue                                  # stray content before the first question
        elif t.kind == "option":
            options.append(Option(t.text, t.checked))
        elif t.kind == "freetext":
            accept = _split_set(t.text)
        elif t.kind == "reject":
            reject = _split_set(t.text)
        elif t.kind == "quote":
            explanation = t.text
    flush()
    return questions


def _build_question(prompt, line, options, accept, reject, explanation, path) -> Question:
    # A `?answer:` line makes this a free-text question (option count infers the others). It carries
    # a reference set and no checkboxes; grading is the LLM grader with a keyword floor (Phase 2).
    if accept is not None:
        if options:
            raise PackError(path, line, "a free-text question has a '- ?answer:' line and no "
                            "checkbox options; this one has both")
        if not accept:
            raise PackError(path, line, "a free-text question needs at least one reference answer "
                            "on its '- ?answer:' line")
        if not explanation:
            raise PackError(path, line, "a question needs a '>' explanation, shown after answering")
        return Question(prompt=prompt, explanation=explanation, accept=accept, reject=reject)
    if len(options) < 2:
        raise PackError(path, line, "a question needs at least two options")
    correct = [o for o in options if o.correct]
    if len(correct) != 1:
        raise PackError(path, line,
                        f"a question needs exactly one option marked [x], found {len(correct)}")
    if not explanation:
        raise PackError(path, line, "a question needs a '>' explanation, shown after answering")
    return Question(prompt=prompt, options=tuple(options), explanation=explanation)


# -- items --------------------------------------------------------------------------------------


def parse_item(path: str, text: str) -> ItemDef:
    """One `items/*.md` file into an engine `ItemDef` (OBJECTS.md section 9). Frontmatter carries
    the closed effect vocabulary; the body is the item's `look`, shown in the inventory panel. The
    parser enforces the *format* (required keys present, known keys only, a single-char glyph, a
    whole `value`); schema.py holds the cross-file policy (glyph and colour in their sets, ids
    unique, a `place:` naming a real kind). A `value` above zero makes a currency: it banks like
    money rather than filling an inventory slot."""
    fm = split_frontmatter(text, path)
    if fm is None:
        raise PackError(path, 1, "an item file needs frontmatter with id, glyph, colour and name")
    values, key_lines, body, _ = fm
    _require(values, key_lines, ("id", "glyph", "colour", "name"), path)
    for key in values:
        if key not in ITEM_KEYS:
            raise PackError(path, key_lines[key], f"unknown item key {key!r}; an item file may set "
                            f"{', '.join(sorted(ITEM_KEYS))}")
    glyph = values["glyph"]
    if len(glyph) != 1:
        raise PackError(path, key_lines["glyph"],
                        f"glyph must be a single character, not {glyph!r}")
    value = _int(values, key_lines, "value", path) or 0
    if value < 0:
        raise PackError(path, key_lines["value"], f"'value' must be zero or more, not {value}")
    on_move_min = _int(values, key_lines, "on_move_min", path)
    if on_move_min is not None and on_move_min < 1:
        raise PackError(path, key_lines["on_move_min"],
                        f"'on_move_min' must be one or more, not {on_move_min}")
    return ItemDef(
        id=values["id"],
        glyph=glyph,
        name=values["name"],
        colour=values["colour"],
        carriable=value == 0,          # a valued kind is currency: it banks, not an inventory slot
        value=value,
        bulky=_bool(values, key_lines, "bulky", path),
        look=body.strip(),
        on_pickup=values.get("on_pickup", ""),
        on_pickup_plural=values.get("on_pickup_plural", ""),
        on_move=values.get("on_move", ""),
        on_move_short=values.get("on_move_short", ""),
        on_move_min=on_move_min if on_move_min is not None else 1,
        plural=values.get("plural", ""),
    )


def item_files(locale: Path) -> list[Path]:
    """A locale's item definitions, `items/*.md`, sorted. Absent `items/` is fine: most packs
    define no objects."""
    items = locale / "items"
    if not items.is_dir():
        return []
    return sorted(items.glob("*.md"))


# -- chapter / pack / scroll --------------------------------------------------------------------


def _meta_body(text: str, path: str, required: tuple[str, ...]):
    fm = split_frontmatter(text, path)
    if fm is None:
        raise PackError(path, 1, f"this file needs frontmatter with {', '.join(required)}")
    values, key_lines, body, _ = fm
    _require(values, key_lines, required, path)
    return values, key_lines, body.strip()


def parse_pack_md(path: str, text: str):
    values, key_lines, intro = _meta_body(text, path, ("id", "title", "difficulty", "scroll"))
    difficulty = values["difficulty"]
    if difficulty not in DIFFICULTIES:
        raise PackError(path, key_lines["difficulty"],
                        f"difficulty must be one of {', '.join(DIFFICULTIES)}, not {difficulty!r}")
    reward = _reward(values, key_lines, path, 0)
    return values, intro, reward


def parse_chapter_md(path: str, text: str):
    values, _key_lines, intro = _meta_body(text, path, ("id", "title"))
    return values, intro


# -- walking a pack tree ------------------------------------------------------------------------


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def locale_dirs(root: Path) -> list[Path]:
    """Locale subtrees: a child directory that holds a pack.md. Sorted, so 'en' before 'nl'."""
    return sorted((d for d in root.iterdir() if d.is_dir() and (d / "pack.md").is_file()),
                  key=lambda d: d.name)


def chapter_dirs(locale: Path) -> list[Path]:
    return sorted((d for d in locale.iterdir() if d.is_dir() and (d / "chapter.md").is_file()),
                  key=lambda d: d.name)


def room_files(chapter: Path) -> list[Path]:
    return sorted(p for p in chapter.glob("*.md") if p.name != "chapter.md")


def load_pack(root: Path, locale: str) -> Pack:
    """Assemble one locale into a Pack, in filename order. Strict: raises on the first bad file.
    `validate_pack` (schema.py) is the lenient path that gathers every issue instead."""
    root = Path(root)
    base = root / locale
    if not (base / "pack.md").is_file():
        raise PackError(str(base / "pack.md"), None, f"no {locale!r} locale found under {root}")

    meta, intro, reward = parse_pack_md(str(base / "pack.md"), _read(base / "pack.md"))
    items = tuple(parse_item(str(f), _read(f)) for f in item_files(base))
    chapters: list[Chapter] = []
    for cdir in chapter_dirs(base):
        cmeta, cintro = parse_chapter_md(str(cdir / "chapter.md"), _read(cdir / "chapter.md"))
        rooms = tuple(parse_room(str(rf), _read(rf)) for rf in room_files(cdir))
        chapters.append(Chapter(id=cmeta["id"], title=cmeta["title"], intro=cintro,
                                rooms=rooms, slug=cdir.name))

    scroll_path = base / "scroll.md"
    scroll = _read(scroll_path).strip() if scroll_path.is_file() else ""
    return Pack(id=meta["id"], title=meta["title"], difficulty=meta["difficulty"],
                scroll_name=meta["scroll"], intro=intro, chapters=tuple(chapters),
                scroll=scroll, locale=locale, reward=reward, items=items)
