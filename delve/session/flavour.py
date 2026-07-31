"""Question-text flavour: sprinkle a single emoji onto a keyword, sparsely and deterministically.

An author writes plain question prose; the engine garnishes it when it builds the view (rule 2:
`session` shapes the words, `ui` only paints). We prepend one emoji from a global per-locale table
(`[flavour_emoji]` in the strings catalogue) to at most one keyword in a prompt, so `email` shows
as `📧 email`. The author never inserts an emoji themselves.

Two disciplines make this safe here:

- **Deterministic, and off every seeded stream.** The choice is a stable CRC of the prompt, never
  `self.rng` (which shuffles the exam options, CLAUDE.md 'RNG streams') nor the snapshotted streams.
  So it holds identical across every redraw of the panel and every regeneration of the run, and it
  touches nothing the grader reads (the prompt is display-only; grading is on the options/answer).
- **Single-codepoint only.** The table holds only lone emoji, because the panel measures display
  columns and cannot size a joined sequence (a test asserts it; DISPLAY.md section 4).

Skipped when the prompt already carries an emoji (the author got there first) or holds no keyword.
"""

import re
import unicodedata
import zlib

# Share of keyword-bearing prompts that actually get an emoji; the rest stay plain, so the garnish
# reads as an occasional sprinkle rather than a rule. Deterministic per prompt, not a live coin.
AUGMENT_PERCENT = 55


def _has_emoji(text: str) -> bool:
    """True if the text already shows a wide glyph (an emoji). Latin, `é`, `€`, `→` and box-drawing
    are all narrow or ambiguous, so only a real emoji trips this in an en/nl prompt."""
    return any(unicodedata.east_asian_width(c) in ("W", "F") for c in text)


def augment(prompt: str, table: dict) -> str:
    """`prompt` with one keyword garnished by its emoji, or unchanged. Pure and deterministic."""
    if not table or _has_emoji(prompt):
        return prompt
    matches = [(m.start(), kw)
               for kw in table
               for m in re.finditer(rf"\b{re.escape(kw)}\b", prompt, re.IGNORECASE)]
    if not matches:
        return prompt
    h = zlib.crc32(prompt.encode("utf-8"))
    if h % 100 >= AUGMENT_PERCENT:                     # sparse: leave most eligible prompts plain
        return prompt
    matches.sort()                                     # stable order, independent of dict iteration
    start, kw = matches[(h // 100) % len(matches)]
    return f"{prompt[:start]}{table[kw]} {prompt[start:]}"
