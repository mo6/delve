"""The Markdown parser (M3). Two things matter most here and both are load-bearing.

The golden test parses the pilot's real `01-phishing.md` and asserts it equals the `Room` the M2
slice hard-codes, byte for byte. That single assertion ties M3 to M2: the format is answerable to
content the engine already renders, not the reverse (CLAUDE.md 'The pilot pack').

The rest pin the format down where it's easy to get subtly wrong: inline flattening that must not
touch a domain, paragraph joining, quote paragraphs, fenced code kept verbatim, and question type
inferred from option count alone in either language.
"""

from pathlib import Path

import pytest

from delve.content.errors import PackError
from delve.content.markup import flatten_inline, inline_spans, tokenize
from delve.content.parser import load_pack, parse_room
from delve.content.pilot import PHISHING_ROOM

PILOT = Path("packs/security-onboarding")
PHISH = PILOT / "en" / "01-the-sorting-office" / "01-phishing.md"


# -- the golden test ---------------------------------------------------------------------------


def test_parsed_phishing_room_equals_the_hardcoded_slice():
    room = parse_room(str(PHISH), PHISH.read_text(encoding="utf-8"))
    assert room == PHISHING_ROOM


# -- inline flattening -------------------------------------------------------------------------


def test_flatten_strips_emphasis_and_code_but_keeps_the_text():
    assert flatten_inline("A **phishing** message wants your *click*.") == \
        "A phishing message wants your click."
    assert flatten_inline("nearly right. `micros0ft.com`. `yourcompany-hr.net`.") == \
        "nearly right. micros0ft.com. yourcompany-hr.net."


def test_flatten_leaves_underscores_and_domains_alone():
    # Underscore is not an emphasis marker here: it lives inside identifiers and the very domains
    # a security lesson teaches people to read.
    assert flatten_inline("check `first_last@corp.io` against the_real_domain") == \
        "check first_last@corp.io against the_real_domain"


def test_flatten_keeps_unpaired_markers_literal():
    assert flatten_inline("2 * 3 is 6") == "2 * 3 is 6"


# -- block tokenizing --------------------------------------------------------------------------


def test_paragraph_joins_wrapped_source_lines_with_a_space():
    toks = tokenize("Ada does not look up. She keeps\nholding it while she talks.")
    assert [t.kind for t in toks] == ["para"]
    assert toks[0].text == "Ada does not look up. She keeps holding it while she talks."


def test_quote_joins_paragraphs_with_a_blank_line():
    toks = tokenize("> first line\n> still first\n>\n> second para")
    assert toks[0].kind == "quote"
    assert toks[0].text == "first line still first\n\nsecond para"


def test_inline_spans_mark_bold_and_strip_the_rest():
    # **strong** survives as its own run; *emphasis* and `code` are stripped to plain, like flatten.
    assert inline_spans("a **b** c") == (("a ", False), ("b", True), (" c", False))
    assert inline_spans("plain *em* and `code`") == (("plain em and code", False),)
    # a paragraph token now carries both the flattened text and the styled runs.
    (tok,) = tokenize("A **phishing** message wants your click.")
    assert tok.text == "A phishing message wants your click."      # flattened, unchanged
    assert ("phishing", True) in tok.spans


def test_a_table_tokenises_into_a_styled_cell_grid():
    toks = tokenize("| Factor | Verdict |\n|---|---|\n| **Passkeys** | Strongest. |\n")
    assert [t.kind for t in toks] == ["table"]
    assert toks[0].rows == (
        ((("Factor", False),), (("Verdict", False),)),      # header row
        ((("Passkeys", True),), (("Strongest.", False),)),  # the |---| separator is dropped
    )


def test_a_table_between_paragraphs_is_its_own_block():
    toks = tokenize("Before.\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\nAfter.")
    assert [t.kind for t in toks] == ["para", "table", "para"]


def test_fenced_code_is_verbatim_and_never_flattened():
    toks = tokenize("```\n  P@ssw0rd!2024   *not italics*\n```")
    assert toks[0].kind == "code"
    assert toks[0].text == "P@ssw0rd!2024   *not italics*"


def test_options_and_headings_carry_their_state_and_line():
    toks = tokenize("### A question?\n\n- [ ] no\n- [x] yes", offset=4)
    assert toks[0].kind == "heading" and toks[0].level == 3 and toks[0].line == 5
    assert [(t.kind, t.checked) for t in toks[1:]] == [("option", False), ("option", True)]


# -- question type inference -------------------------------------------------------------------


def test_question_type_comes_from_option_count_in_any_language():
    room = load_pack(PILOT, "nl").chapters[0].rooms[0]
    kinds = [q.kind for q in room.questions]
    # The Dutch assertion uses Waar/Niet waar, which an earlier True/False rule broke; two options
    # is still an assertion (CLAUDE.md 'Question format').
    assert "assertion" in kinds and "mcq" in kinds
    for q in room.questions:
        assert q.kind == ("assertion" if len(q.options) == 2 else "mcq")


# -- structural errors raise with file:line ----------------------------------------------------

def _room(body: str) -> str:
    return "---\nid: r\nkeeper: wizard\nname: K\npass: 0.75\n---\n\n# T\n\ntext\n\n" + body


@pytest.mark.parametrize("text, needle", [
    ("no frontmatter here", "needs frontmatter"),
    ("---\nid: r\n\n# T", "never closed"),
    ("---\nkeeper: wizard\n---\n# T\n## Questions\n### q\n- [x] a\n- [ ] b\n> e",
     "missing required key 'id'"),
    ("---\nid: r\nkeeper: goblin\n---\n# T", "keeper must be one of"),
    ("---\nid: r\npass: 1.5\n---\n# T", "pass must be between 0 and 1"),
    ("---\nid: r\npass: soon\n---\n# T", "must be a number"),
    ("---\nid: r\n---\nno title\n## Questions\n### q\n- [x] a\n- [ ] b\n> e", "needs an H1 title"),
    ("---\nid: r\n---\n# T\n\nlesson only", "needs a '## Questions' section"),
])
def test_malformed_room_raises_packerror(text, needle):
    with pytest.raises(PackError) as e:
        parse_room("r.md", text)
    assert needle in str(e.value)


@pytest.mark.parametrize("q, needle", [
    ("### only one?\n- [x] a\n> e", "at least two options"),
    ("### none right?\n- [ ] a\n- [ ] b\n> e", "exactly one option marked"),
    ("### two right?\n- [x] a\n- [x] b\n> e", "exactly one option marked"),
    ("### no reason?\n- [x] a\n- [ ] b", "needs a '>' explanation"),
    ("### free?\n- ?answer: urgency", "needs a '>' explanation"),
    ("### free?\n- ?answer:\n> e", "at least one reference answer"),
    ("### both?\n- [x] a\n- [ ] b\n- ?answer: a\n> e", "and no checkbox options"),
])
def test_malformed_question_raises_at_the_heading_line(q, needle):
    with pytest.raises(PackError) as e:
        parse_room("r.md", _room("## Questions\n\n" + q))
    assert needle in str(e.value)


def test_error_points_at_the_offending_line():
    text = "---\nid: r\nkeeper: goblin\nname: K\npass: 0.75\n---\n# T"
    with pytest.raises(PackError) as e:
        parse_room("r.md", text)
    assert e.value.line == 3            # the keeper: line, not the top of the file
