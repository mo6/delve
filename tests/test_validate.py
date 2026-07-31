"""`delve validate` (M3): the pack-policy checks that span files and are gathered, not raised.

The headline requirement is that the pilot pack passes clean on both locales, including the
identical-tree check (PLAN.md section 11, M3). The rest build small broken packs on disk and
assert the validator finds capacity overflow, a drifted locale tree, and per-file faults all in
one pass, and that the CLI's exit code follows whether any error survived.
"""

from pathlib import Path

from delve.__main__ import main
from delve.content.schema import validate_pack

PILOT = "packs/security-onboarding"

_ROOM = "---\nid: {id}\nkeeper: wizard\nname: K\npass: 0.75\n---\n\n# {id}\n\ntext\n\n" \
        "## Questions\n\n### q?\n\n- [x] yes\n- [ ] no\n\n> because.\n"


def _pack(root: Path, locale: str, rooms: int, *, chapters: int = 1, scroll: bool = True):
    """Write a minimal but valid pack tree under root/locale, so a test can then break one thing."""
    base = root / locale
    base.mkdir(parents=True, exist_ok=True)
    (base / "pack.md").write_text(
        "---\nid: p\ntitle: P\ndifficulty: standard\nscroll: S\n---\n\nIntro.\n", encoding="utf-8")
    if scroll:
        (base / "scroll.md").write_text("# S\n\n{name} scored {score} on {date}.\n",
                                        encoding="utf-8")
    for c in range(1, chapters + 1):
        cdir = base / f"{c:02d}-chapter"
        cdir.mkdir(exist_ok=True)
        (cdir / "chapter.md").write_text(f"---\nid: c{c}\ntitle: C{c}\n---\n\nIntro.\n",
                                         encoding="utf-8")
        for r in range(1, rooms + 1):
            (cdir / f"{r:02d}-room.md").write_text(_ROOM.format(id=f"c{c}r{r}"), encoding="utf-8")


# -- the headline ------------------------------------------------------------------------------


def test_pilot_pack_has_no_errors():
    # The pilot carries deliberate placeholder warnings (see below); it must have no *errors*.
    assert [i for i in validate_pack(PILOT) if i.is_error] == []


def test_pilot_validate_cli_exits_zero():
    assert main(["validate", PILOT]) == 0


def test_pilot_placeholders_warn():
    # Every author-marked spot that must be replaced before real use surfaces as a warning, in
    # both locales, so nobody ships the pilot as-is (CLAUDE.md 'The pilot pack').
    warns = [i for i in validate_pack(PILOT)
             if i.level == "warning" and "placeholder" in i.message]
    assert warns, "expected placeholder warnings in the pilot"
    paths = " ".join(i.path for i in warns)
    assert "classification.md" in paths and "reporting.md" in paths
    assert "/en/" in paths and "/nl/" in paths


# -- capacity ----------------------------------------------------------------------------------


def test_seven_rooms_warns(tmp_path):
    _pack(tmp_path, "en", rooms=7)
    issues = validate_pack(tmp_path)
    assert [i.level for i in issues] == ["warning"]
    assert "7 rooms" in issues[0].message


def test_nine_rooms_is_an_error(tmp_path):
    _pack(tmp_path, "en", rooms=9)
    errors = [i for i in validate_pack(tmp_path) if i.is_error]
    assert len(errors) == 1 and "nine is a lecture" in errors[0].message


# -- locale-tree parity ------------------------------------------------------------------------


def test_drifted_locale_tree_is_reported_both_ways(tmp_path):
    _pack(tmp_path, "en", rooms=2)
    _pack(tmp_path, "nl", rooms=2)
    (tmp_path / "en" / "01-chapter" / "03-extra.md").write_text(_ROOM.format(id="x"),
                                                                encoding="utf-8")
    messages = [i.message for i in validate_pack(tmp_path)]
    assert any("missing from nl/" in m for m in messages)


def test_identical_trees_raise_no_parity_issue(tmp_path):
    _pack(tmp_path, "en", rooms=2)
    _pack(tmp_path, "nl", rooms=2)
    assert validate_pack(tmp_path) == []


# -- gathering + exit codes --------------------------------------------------------------------


def test_a_broken_file_becomes_an_issue_and_the_walk_continues(tmp_path):
    _pack(tmp_path, "en", rooms=2)
    good = tmp_path / "en" / "01-chapter" / "01-room.md"
    good.write_text(good.read_text().replace("- [x] yes", "- [ ] yes"), encoding="utf-8")
    issues = validate_pack(tmp_path)
    assert any("exactly one option marked" in i.message for i in issues)
    # The second room still parsed, so the walk didn't stop at the first fault.
    assert sum(1 for i in issues if i.is_error) == 1


def test_missing_scroll_is_only_a_warning(tmp_path):
    _pack(tmp_path, "en", rooms=1, scroll=False)
    issues = validate_pack(tmp_path)
    assert [i.level for i in issues] == ["warning"]
    assert main(["validate", str(tmp_path)]) == 0        # warnings don't fail the build


def test_cli_returns_one_when_an_error_survives(tmp_path):
    _pack(tmp_path, "en", rooms=9)
    assert main(["validate", str(tmp_path)]) == 1


def test_no_locale_subtree_is_an_error(tmp_path):
    (tmp_path / "stray.md").write_text("# nope\n", encoding="utf-8")
    issues = validate_pack(tmp_path)
    assert len(issues) == 1 and "no locale subtree" in issues[0].message


def test_missing_pack_path_is_a_clean_error_not_a_traceback(tmp_path):
    # A path that does not exist reports one issue rather than raising FileNotFoundError, so the
    # CLI prints `path: error: ...` and exits 1 like any other validation failure.
    issues = validate_pack(tmp_path / "no-such-pack")
    assert len(issues) == 1 and "no such pack directory" in issues[0].message
    assert issues[0].is_error


def test_pack_path_that_is_a_file_is_a_clean_error(tmp_path):
    afile = tmp_path / "pack.md"
    afile.write_text("not a pack\n", encoding="utf-8")
    issues = validate_pack(afile)
    assert len(issues) == 1 and "not a directory" in issues[0].message
