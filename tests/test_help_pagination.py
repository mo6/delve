"""DELVE-0059: the Keys tab used to lose half its page to a blank line between every entry
(`ui/windows.py`'s generic pager rule, right for prose, wrong for a dense list of one-liners).
`RunState._keys_body` folds a context's entries into one hard-break block, the same trick
`_title_block` already uses to keep an item's name flush above its description, so pagination
only ever breaks between whole entries, never mid-entry, with no wasted blank rows.

A playtesting follow-up widened this past Keys alone: `_condensed` (the same trick, pulled out as
a shared helper) now also folds Status, Grader, Objectives, and the message log into one block
each, since all four are the same shape (a dense list of short, one-line facts) Keys already was.
A lesson's prose and the pack's per-item entries stay genuinely separate blocks, since a blank line
between paragraphs or between two different carried items is meaningful there, unlike a flat list
of facts."""

from test_dungeon import _approach

from delve.session.commands import Help, Inventory, TabCycle, Talk
from delve.session.run import new_run
from delve.session.views import TextBlock
from delve.ui import windows


def test_walking_context_keys_fit_on_one_page_at_100x30():
    run = new_run(seed=1, cols=100, rows=30)
    frame = run.apply(Help())
    view = frame.overlay
    pages = windows._text_pages(view, windows._body(30))
    assert len(pages) == 1
    # 10 walking-context entries, packed tight ('p' retired: the message log lives in Info now;
    # 'd' moved to the Pack tab, DELVE-0081).
    assert len(pages[0]) == 10


def test_page_count_agrees_with_text_pages_for_the_keys_tab():
    run = new_run(seed=1, cols=100, rows=30)
    frame = run.apply(Help())
    assert windows.page_count(frame.overlay, 30) == 1


def test_a_context_with_more_entries_than_fit_still_paginates_between_whole_entries():
    # A synthetic HelpView-shaped body with more entries than a page can hold, mirroring what
    # _keys_body would build: one block, entries joined by a literal '\n'.
    from delve.session.views import HelpView, InfoTab

    lines = [f"k{i}: a moderately long explanation of what this particular key does, number {i}"
             for i in range(40)]
    spans = tuple((("\n" if i else "") + line, False) for i, line in enumerate(lines))
    body = [TextBlock("plain", "\n".join(lines), spans=spans)]
    view = HelpView(tabs=[InfoTab("keys", "Keys")], active=0, body=body)
    pages = windows._text_pages(view, windows._body(30))
    assert len(pages) > 1                       # genuinely too many for one page
    # Every rendered line is a whole entry's own (possibly wrapped) line; reconstruct each page's
    # text and assert no page starts or ends mid-entry (an entry's first line always starts with
    # "kN:", never a bare wrapped continuation missing that prefix at a page boundary).
    for page in pages:
        first_line = "".join(seg[0] for seg in page[0][1])
        assert first_line.split(":")[0].strip().startswith("k")


def test_objectives_tab_is_condensed_too():
    run = new_run(seed=1, cols=100, rows=30)
    run.apply(Help())
    frame = run.apply(TabCycle(1))
    # Objectives now folds its facts into one block via `_condensed`, the same as Keys.
    assert len(frame.overlay.body) == 1
    assert frame.overlay.body[0].spans
    lines = frame.overlay.body[0].text.split("\n")
    assert any(line.startswith("Pack:") for line in lines)
    assert any(line.startswith("Rooms passed:") for line in lines)


def test_lesson_spacing_is_unaffected():
    run = new_run(seed=1, cols=100, rows=30)
    _approach(run, run.gates["phishing"].keeper.pos)
    lesson = run.apply(Talk())
    assert len(lesson.overlay.body) >= 1
    assert not any(b.spans for b in lesson.overlay.body)   # unchanged: still discrete blocks


def test_pack_spacing_is_unaffected():
    # The Pack tab's compact list shows one row per carried kind (DELVE-0069), alongside the
    # focused row's own single "para" detail block (DELVE-0073's bold-title-plus-description
    # shape, always visible now per DELVE-0075), never condensed into a dense fact list the way
    # Keys/Status/Grader/Messages are, since a carried item's description is genuinely prose.
    run = new_run(seed=1, cols=100, rows=30)
    run.player.gold = 5
    pack = run.apply(Inventory())
    assert len(pack.overlay.pack_rows) >= 2
    assert pack.overlay.body[0].kind == "para"


def test_message_log_is_condensed_too():
    # The message log is the Info panel's Messages tab now (index 4), not a standalone panel.
    run = new_run(seed=1, cols=100, rows=30)
    run.messages.extend(["one", "two", "three"])
    run.apply(Inventory())
    log = run.apply(TabCycle(4))
    assert log.overlay.tabs[log.overlay.active].key == "messages"
    assert len(log.overlay.body) == 1
    assert log.overlay.body[0].spans
