"""A lesson as semantic blocks, not wrapped lines. The parser (M3) produces these from
Markdown; M2 hard-codes them. Keeping blocks semantic is what lets `ui` paginate on paragraph
boundaries and hold the panel height constant (PLAN.md section 7); the core never wraps text.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Block:
    kind: str   # 'para' | 'bullet' | 'quote' | 'code' | 'table'
    text: str   # 'code' keeps its newlines and is never wrapped; the rest are single paragraphs
    # Presentation hints derived from the same source as `text`: inline (text, strong) runs for
    # bold, and a table's cell grid. Excluded from equality (compare=False) so the M2 golden test
    # (a parsed Room equals the hard-coded pilot Room) still holds; styling is verified separately.
    spans: tuple = field(default=(), compare=False)
    table: tuple = field(default=(), compare=False)


@dataclass(frozen=True)
class Lesson:
    title: str
    blocks: tuple[Block, ...]
