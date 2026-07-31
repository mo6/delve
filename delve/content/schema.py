"""Pack policy: the rules that span more than one file, gathered rather than raised.

parser.py raises on the first structural fault *within* a file. This module is the other half:
it walks a whole pack, turns each file's `PackError` into a gathered `Issue` so one run reports
every broken file at once, and adds the checks that no single file can answer on its own, chapter
capacity (a lecture is too many rooms, AUTHORING.md section 3) and locale-tree parity (a half-
translated dungeon is worse than a monolingual one, section 2). Warnings are advisory; errors
block the pack. The CLI prints them and picks an exit code from whether any error survived.
"""

import re
from pathlib import Path

from delve.content.errors import Issue, PackError
from delve.content.parser import (
    chapter_dirs,
    item_files,
    locale_dirs,
    parse_chapter_md,
    parse_item,
    parse_pack_md,
    parse_room,
    room_files,
)
from delve.engine.items import COLOURS, MONEY, OBJECT_GLYPHS

CAPACITY_WARN = 7          # AUTHORING.md section 3: 7-8 rooms warns, 9+ errors
CAPACITY_ERROR = 9
SCROLL_FIELDS = {"name", "score", "date", "pack"}
CLUTTER_WARN = 3           # more kinds than this in one room is a taste smell (OBJECTS.md sec. 9)
# An author marks a spot that must be replaced before real use with the word itself, in either
# locale (CLAUDE.md 'The pilot pack'). Keying off the marker, not off tokens like example.com,
# leaves teaching examples (`yourbank.example.com`) alone; those carry no marker.
PLACEHOLDER_MARKER = re.compile(r"\b(placeholder|plaatshouder)\b", re.IGNORECASE)


def validate_pack(root) -> list[Issue]:
    """Every issue in the pack, errors and warnings, ready to print. An empty list is a clean
    pack. Never raises: a `PackError` from any file becomes an `Issue` so the walk continues."""
    root = Path(root)
    if not root.exists():
        return [Issue(str(root), None, "no such pack directory")]
    if not root.is_dir():
        return [Issue(str(root), None, "not a directory; a pack is a folder holding en/ and/or "
                                       "nl/")]
    issues: list[Issue] = []
    locales = locale_dirs(root)
    if not locales:
        return [Issue(str(root), None, "no locale subtree found (expected en/ and/or nl/ with a "
                                       "pack.md)")]

    for base in locales:
        issues += _validate_locale(base)
    issues += _check_tree_parity(locales)
    return issues


def _validate_locale(base: Path) -> list[Issue]:
    issues: list[Issue] = []
    issues += _guard(base / "pack.md",
                     lambda p: parse_pack_md(str(p), p.read_text(encoding="utf-8")))

    chapters = chapter_dirs(base)
    if not chapters:
        issues.append(Issue(str(base), None, "a pack needs at least one chapter folder"))

    for cdir in chapters:
        issues += _guard(cdir / "chapter.md",
                         lambda p: parse_chapter_md(str(p), p.read_text(encoding="utf-8")))
        rooms = room_files(cdir)
        if not rooms:
            issues.append(Issue(str(cdir), None, "a chapter needs at least one room file"))
        issues += _check_capacity(cdir, len(rooms))
        for rf in rooms:
            issues += _guard(rf, lambda p: parse_room(str(p), p.read_text(encoding="utf-8")))

    issues += _check_scroll(base / "scroll.md")
    issues += _validate_items(base)
    issues += _check_freetext(base)
    issues += _check_placeholders(base)
    issues += _check_emoji(base)
    return issues


def _emoji_hazard(ch: str) -> bool:
    """A codepoint that only ever appears as part of a *multi*-codepoint emoji: a zero-width joiner,
    a variation selector, a skin-tone modifier, or a regional-indicator (flag) letter. Any of these
    means a single visible glyph is several codepoints, which the panel renders as one wide cell it
    cannot measure, so a line runs through the box border (DISPLAY.md section 1, SCREENS.md 9.4)."""
    return (ch in ("‍", "️", "︎")
            or "\U0001F3FB" <= ch <= "\U0001F3FF"        # skin-tone modifiers
            or "\U0001F1E6" <= ch <= "\U0001F1FF")        # regional indicators (flags)


def _check_emoji(base: Path) -> list[Issue]:
    """Pack prose may use emoji for flavour, but only *single-codepoint* ones: the panel's wrap
    counts display columns, which works for a lone wide glyph but not for a joined sequence. Flag
    every line carrying a multi-codepoint hazard so an author swaps it for a plain single emoji
    (a face, a key, a lock) before it renders broken. An error, because it does not just read
    oddly, it tears the panel frame."""
    issues: list[Issue] = []
    for f in sorted(base.rglob("*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            if any(_emoji_hazard(ch) for ch in line):
                issues.append(Issue(str(f), n, "multi-codepoint emoji (a joined, flag, skin-tone, "
                              "or variation-selector sequence); the panel can only render a "
                              "single-codepoint emoji, so use a plain one"))
    return issues


def _check_placeholders(base: Path) -> list[Issue]:
    """Warn on every line an author flagged as a placeholder (the pilot ships several: the
    classification tiers, `#security-help`, the reporting channels). Advisory, never blocking:
    the pack plays fine with them, but nobody should run it for real before replacing them
    (CLAUDE.md 'The pilot pack'). One warning per line, so a whole run lists every spot to fix."""
    issues: list[Issue] = []
    for f in sorted(base.rglob("*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            if PLACEHOLDER_MARKER.search(line):
                issues.append(Issue(str(f), n, "marks a placeholder; replace it with your "
                              "organisation's real value before running this for real.",
                              level="warning"))
    return issues


def _check_freetext(base: Path) -> list[Issue]:
    """A room using free-text questions needs the local LLM grader reachable, which `delve` now
    requires to play at all (DELVE-0033), not merely to grade at full quality. Warn here anyway,
    since `validate` runs fine with nothing installed (it never grades an examination) and this is
    the earliest point an author learns the room needs it; the warning never blocks validation."""
    issues: list[Issue] = []
    for cdir in chapter_dirs(base):
        for rf in room_files(cdir):
            try:
                room = parse_room(str(rf), rf.read_text(encoding="utf-8"))
            except PackError:
                continue                          # the room guard already reported this file
            if any(q.kind == "freetext" for q in room.questions):
                issues.append(Issue(str(rf), None, "uses free-text questions; the LLM grader "
                              "('delve setup' to prepare it) is required to play this pack, not "
                              "just for full-quality grading.", level="warning"))
    return issues


def _validate_items(base: Path) -> list[Issue]:
    """Pack-object policy that spans files (OBJECTS.md section 9): a glyph and colour from their
    closed sets, unique ids that never shadow money, and every room `place:` naming a kind some
    `items/*.md` actually defines. Item-tree parity (a kind translated in both locales) already
    falls out of `_check_tree_parity`, which globs every `*.md`."""
    issues: list[Issue] = []
    defined: dict[str, str] = {}
    for f in item_files(base):
        try:
            defn = parse_item(str(f), f.read_text(encoding="utf-8"))
        except PackError as e:
            issues.append(Issue(e.path, e.line, e.message))
            continue
        if defn.id == MONEY.id:
            issues.append(Issue(str(f), None, f"item id {MONEY.id!r} is reserved for the built-in "
                                              "currency; pick another"))
        if defn.id in defined:
            issues.append(Issue(str(f), None, f"duplicate item id {defn.id!r}; also defined in "
                                              f"{defined[defn.id]}"))
        defined.setdefault(defn.id, f.name)
        if defn.glyph not in OBJECT_GLYPHS:
            issues.append(Issue(str(f), None, f"glyph {defn.glyph!r} is not an object-class char; "
                                              f"use one of {' '.join(sorted(OBJECT_GLYPHS))}"))
        if defn.colour not in COLOURS:
            issues.append(Issue(str(f), None, f"unknown colour {defn.colour!r}; use one of the "
                                              "sixteen (e.g. yellow, bright_cyan)"))

    for cdir in chapter_dirs(base):
        for rf in room_files(cdir):
            try:
                room = parse_room(str(rf), rf.read_text(encoding="utf-8"))
            except PackError:
                continue                          # the room guard already reported this file
            for def_id, _ in room.placements:
                if def_id not in defined:
                    issues.append(Issue(str(rf), None, f"place names {def_id!r}, which no items/ "
                                                       "file in this locale defines"))
            if len(room.placements) > CLUTTER_WARN:
                issues.append(Issue(str(rf), None, f"{len(room.placements)} kinds placed in one "
                                    "room; objects are seasoning, not clutter (OBJECTS.md section "
                                    "13).", level="warning"))
    return issues


def _guard(path: Path, parse) -> list[Issue]:
    """Run a per-file parser, converting its `PackError` into a gathered `Issue`."""
    try:
        parse(path)
        return []
    except PackError as e:
        return [Issue(e.path, e.line, e.message)]


def _check_capacity(cdir: Path, n: int) -> list[Issue]:
    where = str(cdir)
    if n >= CAPACITY_ERROR:
        return [Issue(where, None, f"{n} rooms in one chapter; nine is a lecture, not a floor. "
                                   "Split it into two chapters (AUTHORING.md section 3).")]
    if n >= CAPACITY_WARN:
        return [Issue(where, None, f"{n} rooms in one chapter; the target is 3-4. Consider "
                                   "splitting it.", level="warning")]
    return []


def _check_scroll(path: Path) -> list[Issue]:
    if not path.is_file():
        # A warning, not an error: a pack is playable without one; the final chamber just has no
        # award. The tutorial floor has no scroll by design (never scored), yet still validates
        # like anything else (CLAUDE.md 'The tutorial floor').
        return [Issue(str(path), None, "no scroll.md; the final chamber will award nothing",
                      level="warning")]
    text = path.read_text(encoding="utf-8")
    issues: list[Issue] = []
    for m in re.finditer(r"\{([^}]*)\}", text):
        field = m.group(1)
        if field not in SCROLL_FIELDS:
            line = text.count("\n", 0, m.start()) + 1
            issues.append(Issue(str(path), line,
                                f"unknown scroll placeholder {{{field}}}; the engine only fills "
                                f"{{{'}, {'.join(sorted(SCROLL_FIELDS))}}}", level="warning"))
    return issues


def _check_tree_parity(locales: list[Path]) -> list[Issue]:
    """Every locale must carry the identical file tree; folder and file names are slugs and never
    translate (AUTHORING.md section 2). Diff each locale against the first and report both ways."""
    trees = {base.name: _relative_files(base) for base in locales}
    names = sorted(trees)
    if len(names) < 2:
        return []
    issues: list[Issue] = []
    reference = names[0]
    for other in names[1:]:
        for rel in sorted(trees[reference] - trees[other]):
            issues.append(Issue(f"{other}/{rel}", None,
                                f"present in {reference}/ but missing from {other}/"))
        for rel in sorted(trees[other] - trees[reference]):
            issues.append(Issue(f"{reference}/{rel}", None,
                                f"present in {other}/ but missing from {reference}/"))
    return issues


def _relative_files(base: Path) -> set[str]:
    return {str(p.relative_to(base)) for p in base.rglob("*.md")}
