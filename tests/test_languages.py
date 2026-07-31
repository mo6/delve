"""M6: the tutorial floor and languages.

Two things this milestone adds, both driven headlessly like every other run test (PLAN.md
section 4): the engine's Dlvl 0 orientation floor, and a full locale (strings catalogue, Dutch
number/date formatting) so the pilot plays in Dutch end to end. The play-through helpers are the
ones the M5 dungeon test already uses; this file only adds the tutorial floor above the pack and
asserts on the Dutch surface.
"""

from datetime import datetime
from pathlib import Path

from test_dungeon import _all_points, _clear_chapter, _stand_on

from delve import strings as strings_pkg
from delve.assess.grader import KeywordGrader
from delve.content.parser import load_pack
from delve.engine.items import MONEY
from delve.engine.world import TileKind
from delve.progress.scrolls import format_date, format_score
from delve.session.commands import Descend
from delve.session.launch import load_tutorial
from delve.session.run import new_game
from delve.session.views import TextView

PILOT = Path(__file__).resolve().parent.parent / "packs" / "security-onboarding"


# -- the strings catalogue ------------------------------------------------------------------


def test_both_locales_load_and_differ():
    en, nl = strings_pkg.load("en"), strings_pkg.load("nl")
    assert en("msg.cant_go") == "You can't go that way."
    assert nl("msg.cant_go") == "Die kant kun je niet op."
    assert en("status.rooms") == "Rooms" and nl("status.rooms") == "Kamers"
    assert en.keeper_kind("wizard") == "wizard" and nl.keeper_kind("wizard") == "tovenaar"


def test_info_panel_tab_strings_exist_in_both_locales():
    # DELVE-0040/0041: the i panel's title, tab labels and hint line, so a fresh locale can never
    # ship the tab strip half-translated.
    en, nl = strings_pkg.load("en"), strings_pkg.load("nl")
    assert en("item.info_title") == "Info" and nl("item.info_title") == "Info"
    assert en("item.tab_pack") == "Pack" and nl("item.tab_pack") == "Rugzak"
    assert en("item.tab_scoring") and nl("item.tab_scoring")
    assert en("item.tab_grader") and nl("item.tab_grader")
    assert en("item.tab_soon") and nl("item.tab_soon")
    assert "Tab" in en("hint.inventory") and "Tab" in nl("hint.inventory")


def test_status_tab_strings_exist_in_both_locales_and_differ():
    # DELVE-0044: the Status tab's label and its row labels, so a fresh locale can't ship it
    # half-translated. Labels differ per locale; values (a version, a model name, a size) don't.
    en, nl = strings_pkg.load("en"), strings_pkg.load("nl")
    assert en("item.tab_status") == "Status" and nl("item.tab_status") == "Status"
    assert en("item.status_version", version="1.0.0") != nl("item.status_version", version="1.0.0")
    assert en("item.status_pack", pack="X") and nl("item.status_pack", pack="X")   # "Pack" is a
    # vocabulary term (CLAUDE.md), untranslated in either locale; only checked for presence here.
    assert en("item.status_locale", locale="en") != nl("item.status_locale", locale="en")
    assert en("item.status_size") and nl("item.status_size")
    assert en("item.status_grader", model="m", host="h") != \
        nl("item.status_grader", model="m", host="h")


def test_scoring_sub_tab_strings_exist_in_both_locales():
    # DELVE-0055: the Now/Rooms sub-tab labels, the pass-map legend and its own hint variant, so a
    # fresh locale can't ship the sub-tab strip half-translated. The legend's glyphs never
    # translate; only its words do (checked by presence, not equality, since nl is free to reword).
    en, nl = strings_pkg.load("en"), strings_pkg.load("nl")
    assert en("item.tab_now") and nl("item.tab_now")
    assert en("item.tab_rooms") and nl("item.tab_rooms")
    assert en("item.rooms_legend") and nl("item.rooms_legend")
    for legend in (en("item.rooms_legend"), nl("item.rooms_legend")):
        assert "·" in legend and "░" in legend and "▒" in legend and "█" in legend
    # DELVE-0056: the wording names both row-switch (up/down) and cycle (left/right) keys.
    assert "up" in en("hint.inventory_sub") and "down" in en("hint.inventory_sub")
    assert "omhoog" in nl("hint.inventory_sub") and "omlaag" in nl("hint.inventory_sub")


def test_carrying_hint_names_the_info_key_not_inventory():
    # DELVE-0043: `i` opens the tabbed Info panel, not a flat inventory list, since DELVE-0040;
    # the walking hint had been left saying "Inventory: i" until this fix.
    en, nl = strings_pkg.load("en"), strings_pkg.load("nl")
    assert "Info: i" in en("hint.carrying") and "Inventory" not in en("hint.carrying")
    assert "Info: i" in nl("hint.carrying")


def test_interpolation_and_list_values():
    nl = strings_pkg.load("nl")
    assert nl("msg.descend", title="De kluis") == "Je daalt de trap af. De kluis."
    body = nl("overlay.repelled_body", name="Alwin", first="Alwin")
    assert isinstance(body, list) and len(body) == 3 and "Alwin" in body[0]


def test_unknown_keeper_kind_falls_back_to_the_slug():
    assert strings_pkg.load("nl").keeper_kind("necromancer") == "necromancer"


def test_locale_normalisation():
    assert strings_pkg.normalise("nl_NL") == "nl"
    assert strings_pkg.normalise("NL-be") == "nl"
    assert strings_pkg.normalise("fr_FR") == "en"      # unsupported -> English
    assert strings_pkg.normalise("") == "en"


# -- formatting is locale data, not translation (PLAN.md section 8) --------------------------


def test_dutch_number_and_date_formatting():
    nl = strings_pkg.load("nl").fmt
    assert format_score(0.9166, nl) == "91,7%"          # decimal comma
    assert format_date(datetime(2026, 7, 18), nl) == "18 juli 2026"   # lower-case month
    # English is unchanged and is the default when no table is passed.
    assert format_score(0.9166) == "91.7%"
    assert format_date(datetime(2026, 7, 18)) == "18 July 2026"


# -- the tutorial floor (PLAN.md section 9) --------------------------------------------------


def _game_with_tutorial(locale="en", seed=99, **kw):
    pack = load_pack(PILOT, locale)
    tutorial = load_tutorial(locale)
    strings = strings_pkg.load(locale)
    run = new_game(pack, seed=seed, cols=100, rows=30, name="Ada",
                   strings=strings, tutorial=tutorial, **kw)
    return pack, tutorial, run


def test_tutorial_is_dlvl_zero_unscored_and_above_the_pack():
    pack, tutorial, run = _game_with_tutorial()
    assert len(run.chapters) == len(tutorial.chapters) + len(pack.chapters)
    assert run.idx == 0
    assert run.chapter.dlvl == 0
    assert run.cur.scored is False
    # The pack's first floor now sits below a tutorial, so it grows stairs up to climb back.
    assert run.chapters[len(tutorial.chapters)].chapter.dlvl == 1
    assert run.chapters[len(tutorial.chapters)].chapter.stairs_up is not None


def test_tutorial_stairs_stand_open_from_the_start():
    _, _, run = _game_with_tutorial()
    grid = run.chapter.grid
    # Unlike every other floor, the tutorial's stairs down are painted before any keeper is
    # passed: they are a door standing open, not earned (PLAN.md section 9).
    assert any(grid.at(p.x, p.y).kind is TileKind.STAIRS_DOWN for p in _all_points(grid))


def test_tutorial_floor_is_seeded_with_coins():
    _, tutorial, run = _game_with_tutorial()
    tut = run.chapters[0]
    assert tut.scored is False
    coins = sum(s.count for pile in tut.items.values()
                for s in pile if s.defn.id == MONEY.id)
    assert coins > 0                         # a small award for following the Porter's directions
    # The pack's first floor has no scattered *coins*; its money comes from the on-pass reward. A
    # placed pack object (e.g. the urgent memo) may sit on it, so this checks money, not emptiness.
    first_pack_floor = run.chapters[len(tutorial.chapters)]
    assert not any(s.defn.id == MONEY.id
                   for pile in first_pack_floor.items.values() for s in pile)


def test_walking_over_a_tutorial_coin_auto_collects_it():
    from test_dungeon import _path, _walk

    # Soloist, so no companion races the player to the coin the test walks onto.
    _, _, run = _game_with_tutorial(pet_species="none")
    tut = run.chapters[0]
    reachable = ((pos, pile, _path(run.chapter.grid, run.player.pos, pos, blocked=set(run.keepers)))
                 for pos, pile in tut.items.items())
    pos, pile, path = next((r for r in reachable if r[2]), (None, None, None))
    assert path is not None, "no scattered coin is reachable from the start"
    before = run.player.gold
    _walk(run, path)                             # steps onto the coin, which auto-collects
    assert run.player.gold >= before + pile[0].count
    assert pos not in run.items


def test_clearing_the_tutorial_adds_nothing_to_the_pack_score():
    _, _, run = _game_with_tutorial()
    _clear_chapter(run)                      # pass every tutorial keeper
    assert all(g.passed for g in run.gates.values())
    assert run.pack_score() == 0.0           # unscored: no pack room has been passed yet
    # Only an explicit room reward pays on Dlvl 0 (Merryn's purse); others stay unpaid.
    rewarded = [g for g in run.gates.values() if g.rewarded]
    assert len(rewarded) == 1
    assert rewarded[0].content.id == "tutorial-purse"


def test_tutorial_purse_pays_one_hundred_on_a_perfect_pass():
    _, _, run = _game_with_tutorial(pet_species="none")
    gate = next(g for g in run.gates.values() if g.content.id == "tutorial-purse")
    _clear_chapter(run)                      # reaches Merryn in room order, passing everyone
    assert gate.rewarded and gate.passed_score == 1.0
    coins = [s for pile in run.items.values() for s in pile if s.defn.id == MONEY.id]
    # Scattered orientation coins may still sit on the floor; the on-pass pile is the 100.
    assert any(s.count == 100 for s in coins)


def test_purse_room_rejects_an_unrelated_answer_that_merely_contains_a_keyword():
    """DELVE-0032: the second question's accept list used to include the bare word "drop" (en) /
    "neerleggen" (nl), which `KeywordGrader`'s substring match would accept inside any unrelated
    sentence that happened to contain it. Both are gone from the accept list now; prove a sentence
    that still contains the word fails."""
    grader = KeywordGrader()
    cases = (
        ("en", "I'm not sure, let's just drop this idea for now"),
        ("nl", "ik wil deze klacht neerleggen bij het bestuur"),
    )
    for locale, sentence in cases:
        tutorial = load_tutorial(locale)
        room = next(r for c in tutorial.chapters for r in c.rooms if r.id == "tutorial-purse")
        question = room.questions[1]
        assert grader.grade_text(question, sentence).correct is False


def test_skip_tutorial_starts_on_the_pack_first_floor():
    pack, tutorial, run = _game_with_tutorial(skip_tutorial=True)
    assert run.idx == len(tutorial.chapters)
    assert run.chapter.dlvl == 1
    assert run.chapters[0].scored is False   # the tutorial is still built in, just started below


# -- play the pilot in Dutch, end to end -----------------------------------------------------


def test_pilot_plays_in_dutch_to_the_scroll():
    pack, tutorial, run = _game_with_tutorial(locale="nl", seed=7)

    # The status line reads in Dutch: 'Kamers', and the euro for gold (PLAN.md section 9's
    # exact bug: a Dutch learner taught to read a screen they never see).
    status = run.frame().status
    assert status.rooms_label == "Kamers"
    assert status.gold_symbol == "€"

    # Descend the orientation floor, then clear every pack floor to the pedestal.
    _clear_chapter(run)
    _stand_on(run, TileKind.STAIRS_DOWN)
    run.apply(Descend())
    assert run.chapter.dlvl == 1
    for i in range(len(pack.chapters)):
        _clear_chapter(run)
        if i < len(pack.chapters) - 1:
            _stand_on(run, TileKind.STAIRS_DOWN)
            run.apply(Descend())

    _stand_on(run, TileKind.PEDESTAL)
    assert run.finished
    overlay = run.frame().overlay
    assert isinstance(overlay, TextView)
    text = " ".join(b.text for b in overlay.body)
    assert "100,0%" in text                  # score with a Dutch decimal comma
    # The date is Dutch-formatted (lower-case month), robust to whatever day the test runs.
    assert format_date(datetime.now(), strings_pkg.load("nl").fmt) in text
