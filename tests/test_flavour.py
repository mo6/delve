"""The question-text emoji garnish (session/flavour.py): one single-codepoint emoji prepended to at
most one keyword per prompt, sparsely and deterministically, never touching what the grader reads.
"""

from test_render import _open_lesson  # navigates a run to an open lesson

from delve.session import flavour
from delve.session.commands import Confirm
from delve.session.views import MenuView, PromptView
from delve.strings import load

EN = load("en").flavour_emoji()


def _wide(text: str) -> int:
    return sum(flavour._has_emoji(c) for c in text)


# -- the pure function -------------------------------------------------------------------------


def test_a_keyword_gets_exactly_its_emoji_prepended():
    # This prompt's CRC passes the sparse gate; the garnish is stable, so we can assert it exactly.
    out = flavour.augment("Should you reuse your password across sites?", EN)
    assert out == "Should you reuse your 🔑 password across sites?"


def test_at_most_one_keyword_is_garnished_even_with_several():
    out = flavour.augment("You receive a link in an email. What do you do first?", EN)
    assert _wide(out) == 1                                  # one emoji, though link and email match


def test_a_prompt_that_already_has_an_emoji_is_left_alone():
    text = "Spot the 🎣 in this email before you click."      # author got there first
    assert flavour.augment(text, EN) == text


def test_a_prompt_with_no_keyword_is_unchanged():
    assert flavour.augment("Which of these is the safer habit here?", EN) == "Which of these is " \
        "the safer habit here?"


def test_the_garnish_is_deterministic():
    text = "How can you tell a phishing email from a real one?"
    assert flavour.augment(text, EN) == flavour.augment(text, EN)


def test_it_is_sparse_not_every_eligible_prompt():
    # Many synthetic keyword-bearing prompts: some get an emoji, some don't (the sparse gate), so
    # the fraction lands strictly between none and all.
    prompts = [f"About your password number {i}, what is true?" for i in range(60)]
    augmented = sum(flavour.augment(p, EN) != p for p in prompts)
    assert 0 < augmented < len(prompts)


def test_no_table_is_a_no_op():
    assert flavour.augment("A password question.", {}) == "A password question."


# -- the tables --------------------------------------------------------------------------------


def test_both_locales_use_single_codepoint_emoji_only():
    # The panel measures display columns and cannot size a joined sequence, so every value must be
    # one codepoint that actually reads as an emoji.
    for lang in ("en", "nl"):
        for kw, em in load(lang).flavour_emoji().items():
            assert len(em) == 1, f"{lang}:{kw} -> {em!r} is multi-codepoint"
            assert flavour._has_emoji(em), f"{lang}:{kw} -> {em!r} is not an emoji"


# -- wired into the session --------------------------------------------------------------------


def test_the_session_garnishes_the_question_prompt_it_shows():
    run, _ = _open_lesson(100, 30)
    frame = run.apply(Confirm(True))                       # dismiss the lesson -> first question
    assert isinstance(frame.overlay, (MenuView, PromptView))
    shown = frame.overlay.prompt if isinstance(frame.overlay, MenuView) else frame.overlay.text
    original = run.active.current_question().prompt
    # The shown prompt is exactly what the garnish makes of the original (which may be a no-op),
    # proving the prompt flows through flavour.augment and nothing else rewrote it.
    assert shown == flavour.augment(original, run.strings.flavour_emoji())
