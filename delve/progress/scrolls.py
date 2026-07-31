"""The award: turning a finished run into the scroll the learner carries out.

The scroll body is authored Markdown with `{name}`, `{score}`, `{date}` and `{pack}` left intact
(the validator checks no other placeholder appears); this fills them. Number and date formatting
is locale *data*, not translation (PLAN.md section 8), so it comes from a `[format]` table (the
locale's `delve/strings/<lang>.toml`) rather than `locale.setlocale`, which is process-global and
host-dependent. `fmt` defaults to English so callers with no locale in hand (older tests) keep
working; `--lang nl` passes `strings.fmt`, which spaces its currency, commas its decimals, and
lower-cases its months (all wrong by default, PLAN.md section 8).
"""

from datetime import datetime

# The English defaults, matching delve/strings/en.toml's [format] table. Kept here too so this
# module has no import dependency on the strings package: callers pass a table or take these.
_FMT_EN = {
    "currency": "$",
    "currency_sep": "",
    "thousands": ",",
    "decimal": ".",
    "date": "{d} {month} {y}",
    "months": ("January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"),
}


def format_score(score: float, fmt: dict | None = None) -> str:
    """A pack score as a percentage, e.g. 0.9166 -> '91.7%' (en) or '91,7%' (nl). The decimal
    mark is locale data, never a hard-coded dot (PLAN.md section 8)."""
    fmt = fmt or _FMT_EN
    return f"{score * 100:.1f}".replace(".", fmt["decimal"]) + "%"


def format_money(amount: int, fmt: dict | None = None) -> str:
    """An amount of gold with the locale's currency mark and thousands grouping: '$1,200' (en),
    '€ 1.200' (nl). The mark, the separator after it, and the grouping char are all locale data
    (the `[format]` table), never hard-coded (PLAN.md section 8)."""
    fmt = fmt or _FMT_EN
    digits = f"{amount:,}".replace(",", fmt["thousands"])
    return f"{fmt['currency']}{fmt.get('currency_sep', '')}{digits}"


def format_date(dt: datetime, fmt: dict | None = None) -> str:
    """A date the way the locale's scroll reads it: '18 July 2026' (en), '18 juli 2026' (nl).
    Month names come from the table, never `strftime('%B')`, which reads the process locale and
    would capitalise the Dutch months (PLAN.md section 8)."""
    fmt = fmt or _FMT_EN
    return fmt["date"].format(d=dt.day, month=fmt["months"][dt.month - 1], y=dt.year)


def render_scroll(template: str, *, name: str, score: float, date: datetime, pack: str,
                  fmt: dict | None = None) -> str:
    """Fill the four scroll placeholders. Plain string replacement, not `str.format`, so any stray
    brace in the prose is left untouched."""
    fills = {
        "{name}": name,
        "{score}": format_score(score, fmt),
        "{date}": format_date(date, fmt),
        "{pack}": pack,
    }
    text = template
    for key, value in fills.items():
        text = text.replace(key, value)
    return text
