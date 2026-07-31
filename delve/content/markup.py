"""Markdown to a flat token stream, with no display types in it (PLAN.md section 4).

This is the layer that knows Markdown; `parser.py` above it knows the *pack* (a lesson is the
blocks before `## Questions`, a question is an H3 and the options under it) and never touches a
raw line. Keeping the two apart is why a format change is a change here and nowhere else.

Two jobs. `flatten_inline` drops emphasis and code-span markers to plain text, because token
styling is a later polish (CLAUDE.md 'Question format' note) and the panel renders plain strings
today. `tokenize` walks the block level: paragraphs (wrapped source lines joined by a space),
bullets, `>` quotes (paragraphs joined by a blank line), fenced code (verbatim, never flattened),
H1-H3 headings, `- [ ]` / `- [x]` options, and the `- ?answer:` / `- ?reject:` free-text markers
(the accept and reject rubric sets, Phase 2). Every token carries its 1-based source line so an
error can say where.
"""

from dataclasses import dataclass

# Block kinds a lesson can hold. The panel renderer (ui/windows.py) knows these same five; adding
# another is a format change and touches both. Headings and options are question-side only.
LESSON_KINDS = frozenset({"para", "bullet", "quote", "code", "table"})


@dataclass(frozen=True)
class Token:
    kind: str            # heading para bullet quote code table option freetext reject
    line: int            # 1-based source line where the token starts
    text: str = ""       # flattened text (verbatim for 'code')
    level: int = 0       # heading depth
    checked: bool = False # option: was it marked [x]
    # Inline styling for para/quote/bullet: (text, strong) runs, so **bold** survives to the panel
    # while `text` above stays flattened for callers that want plain (headings, options, tests).
    spans: tuple = ()
    # A table's grid for kind 'table': rows -> cells -> (text, strong) runs. Layout (column widths,
    # cell wrapping) is the panel's job, so the token carries structure, not columns (rule 2).
    rows: tuple = ()


def flatten_inline(s: str) -> str:
    """Strip **strong**, *emphasis* and `code` markers, leaving the text. Backtick spans win over
    asterisks (so `*` inside code survives), unpaired markers stay literal, and nesting recurses.
    Underscore is deliberately not an emphasis marker here: it turns up inside identifiers and
    domains far more often than as italics, and misreading one would corrupt the very strings a
    security lesson is teaching people to look at."""
    out: list[str] = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "`":
            j = s.find("`", i + 1)
            if j == -1:
                out.append(c)
                i += 1
            else:
                out.append(s[i + 1:j])       # verbatim: no recursion inside code
                i = j + 1
        elif c == "*":
            marker = "**" if s.startswith("**", i) else "*"
            j = s.find(marker, i + len(marker))
            if j == -1:
                out.append(c)
                i += 1
            else:
                out.append(flatten_inline(s[i + len(marker):j]))
                i = j + len(marker)
        else:
            out.append(c)
            i += 1
    return "".join(out)


def inline_spans(s: str) -> tuple:
    """Parse inline markup into (text, strong) runs. `**strong**` becomes a strong run; `*emphasis*`
    and `` `code` `` are stripped to plain text, exactly as flatten_inline drops them; an unpaired
    marker stays literal. Adjacent runs of the same weight merge, so plain prose is a single run.
    This is the styled twin of flatten_inline: same text, but it remembers what was bold."""
    runs: list[list] = []

    def emit(text: str, strong: bool) -> None:
        if not text:
            return
        if runs and runs[-1][1] == strong:
            runs[-1][0] += text
        else:
            runs.append([text, strong])

    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "`":                                       # verbatim, no recursion inside code
            j = s.find("`", i + 1)
            if j == -1:
                emit(c, False)
                i += 1
            else:
                emit(s[i + 1:j], False)
                i = j + 1
        elif s.startswith("**", i):
            j = s.find("**", i + 2)
            if j == -1:
                emit(c, False)
                i += 1
            else:
                emit(flatten_inline(s[i + 2:j]), True)
                i = j + 2
        elif c == "*":
            j = s.find("*", i + 1)
            if j == -1:
                emit(c, False)
                i += 1
            else:
                emit(flatten_inline(s[i + 1:j]), False)
                i = j + 1
        else:
            emit(c, False)
            i += 1
    return tuple((t, strong) for t, strong in runs)


def _heading(line: str):
    n = len(line) - len(line.lstrip("#"))
    if 1 <= n <= 6 and line[n:n + 1] == " ":
        return n, line[n + 1:].strip()
    return None


def tokenize(body: str, offset: int = 0) -> list[Token]:
    """`offset` is added to every line number so tokens point at the real file line (the body
    starts below the frontmatter). Blank lines separate blocks; they carry no token."""
    lines = body.split("\n")
    tokens: list[Token] = []
    i, n = 0, len(lines)

    def lineno(idx: int) -> int:
        return offset + idx + 1

    while i < n:
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        if line.startswith("```"):                       # fenced code: verbatim to the close
            start = i
            i += 1
            buf: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1                                        # step over the closing fence
            tokens.append(Token("code", lineno(start), _dedent(buf)))
            continue

        head = _heading(line)
        if head:
            tokens.append(Token("heading", lineno(i), flatten_inline(head[1]), level=head[0]))
            i += 1
            continue

        if line.startswith("|"):                          # a Markdown table: rows of | cells |
            start = i
            raw_rows: list[str] = []
            while i < n and lines[i].strip().startswith("|"):
                raw_rows.append(lines[i].strip())
                i += 1
            tokens.append(Token("table", lineno(start), rows=_parse_table(raw_rows)))
            continue

        if line.startswith(">"):                          # quote: paragraphs split on a bare '>'
            start = i
            paras: list[list[str]] = [[]]
            while i < n and lines[i].strip().startswith(">"):
                inner = lines[i].strip()[1:].lstrip()
                if inner:
                    paras[-1].append(inner)
                elif paras[-1]:
                    paras.append([])
                i += 1
            text = "\n\n".join(" ".join(p) for p in paras if p)
            tokens.append(Token("quote", lineno(start), flatten_inline(text),
                                spans=inline_spans(text)))
            continue

        opt = _option(line)
        if opt is not None:
            tokens.append(Token("option", lineno(i), flatten_inline(opt[1]), checked=opt[0]))
            i += 1
            continue

        if line.startswith("- ?answer:"):
            tokens.append(Token("freetext", lineno(i), line[len("- ?answer:"):].strip()))
            i += 1
            continue

        if line.startswith("- ?reject:"):                # the optional deny-list twin of ?answer
            tokens.append(Token("reject", lineno(i), line[len("- ?reject:"):].strip()))
            i += 1
            continue

        if line.startswith(("- ", "* ")):                 # bullet, with indented continuations
            start = i
            buf = [line[2:]]
            i += 1
            while i < n and lines[i].strip() and not _breaks_bullet(lines[i]):
                buf.append(lines[i].strip())
                i += 1
            raw = " ".join(buf)
            tokens.append(Token("bullet", lineno(start), flatten_inline(raw),
                                spans=inline_spans(raw)))
            continue

        # plain paragraph: gather wrapped source lines until a blank or a block starter
        start = i
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not _starts_block(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        raw = " ".join(buf)
        tokens.append(Token("para", lineno(start), flatten_inline(raw), spans=inline_spans(raw)))

    return tokens


def _parse_table(raw_rows: list[str]) -> tuple:
    """A grid of styled cells from `| a | b |` rows: split each row on the pipes, drop the
    `|---|---|` separator, and parse each cell's inline markup so a **bold** label stays bold. The
    panel lays it out; this only recovers the structure."""
    grid: list[tuple] = []
    for raw in raw_rows:
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if cells and all(set(c) <= set("-: ") for c in cells):
            continue                                       # the header underline row
        grid.append(tuple(inline_spans(c) for c in cells))
    return tuple(grid)


def _option(line: str):
    if line[:3] in ("- [", "* [") and line[4:6] == "] ":
        mark = line[3]
        return (mark in "xX", line[6:].strip())
    return None


def _starts_block(raw: str) -> bool:
    s = raw.strip()
    return (
        s.startswith(("#", ">", "```", "- ", "* ", "|"))
        or _heading(s) is not None
    )


def _breaks_bullet(raw: str) -> bool:
    s = raw.strip()
    # A new bullet, an option, a table, or any other block starter ends the current bullet; a bare
    # indented line continues it.
    return s.startswith(("- ", "* ", "#", ">", "```", "|")) or _option(s) is not None


def _dedent(lines: list[str]) -> str:
    stripped = [ln for ln in lines if ln.strip()]
    if not stripped:
        return ""
    pad = min(len(ln) - len(ln.lstrip()) for ln in stripped)
    return "\n".join(ln[pad:] if ln.strip() else "" for ln in lines).strip("\n")
