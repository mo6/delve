"""The progress store, the snapshot, and resume, exercised headlessly.

The store tests are direct (users, write-once room results, keep-both scrolls). The snapshot tests
drive a real run through `launch`, quit by throwing the RunState away, and resume from the stored
record alone, proving a run is regenerable from (seed, size, pack) plus the learner's mark
(PLAN.md section 10).
"""

from pathlib import Path

from test_dungeon import (
    PILOT,
    _all_points,
    _clear_chapter,
    _stand_on,
)

from delve.content.parser import load_pack
from delve.engine.world import TileKind
from delve.progress.store import SQLiteStore
from delve.session import launch
from delve.session.commands import Descend

# -- the store, directly --------------------------------------------------------------------


def test_user_is_matched_case_insensitively():
    store = SQLiteStore(":memory:")
    a = store.user_by_name("Ada")
    b = store.user_by_name("ada")
    assert a.id == b.id
    assert a.name == "Ada"        # the first spelling is kept


def test_room_result_is_write_once():
    store = SQLiteStore(":memory:")
    user = store.user_by_name("Ada")
    run = store.create_run(user.id, "p", "1", seed=1, cols=100, rows=30)
    store.save_room_result(run.id, "ch", "room", attempts=2, score=0.8, hints_used=0)
    store.save_room_result(run.id, "ch", "room", attempts=9, score=0.1, hints_used=3)
    row = store.conn.execute(
        "SELECT attempts, score FROM room_results WHERE run_id = ? AND room_id = ?",
        (run.id, "room")).fetchone()
    assert (row["attempts"], row["score"]) == (2, 0.8)   # the first result stands; passing is final


def test_scrolls_keep_both():
    store = SQLiteStore(":memory:")
    user = store.user_by_name("Ada")
    r1 = store.create_run(user.id, "p", "1", 1, 100, 30)
    r2 = store.create_run(user.id, "p", "1", 2, 100, 30)
    store.award_scroll(user.id, "p", r1.id, 0.8)
    store.award_scroll(user.id, "p", r2.id, 0.95)
    trophies = store.trophy_case(user.id)
    assert [s.score for s in trophies] == [0.95, 0.8]     # both kept, newest first


def test_unfinished_run_is_the_resume_candidate():
    store = SQLiteStore(":memory:")
    user = store.user_by_name("Ada")
    run = store.create_run(user.id, "p", "1", 1, 100, 30)
    assert store.unfinished_run(user.id, "p").id == run.id
    store.finish_run(run.id, "completed")
    assert store.unfinished_run(user.id, "p") is None


# -- launch: start, persist, resume ---------------------------------------------------------


def test_completing_a_run_writes_results_and_a_scroll():
    store = SQLiteStore(":memory:")
    pack = load_pack(PILOT, "en")
    run = launch.start(store, pack, name="Mara", seed=5, cols=100, rows=30)
    user = store.user_by_name("Mara")
    row = store.unfinished_run(user.id, pack.id)

    for i in range(len(pack.chapters)):
        _clear_chapter(run)
        if i < len(pack.chapters) - 1:
            _stand_on(run, TileKind.STAIRS_DOWN)
            run.apply(Descend())
    _stand_on(run, TileKind.PEDESTAL)
    assert run.finished

    n_rooms = sum(len(c.rooms) for c in pack.chapters)
    got = store.conn.execute(
        "SELECT COUNT(*) FROM room_results WHERE run_id = ?", (row.id,)).fetchone()[0]
    assert got == n_rooms == 12
    assert len(store.trophy_case(user.id)) == 1
    assert store.unfinished_run(user.id, pack.id) is None   # the run is finished, not resumable


def test_resume_rebuilds_the_run_from_its_record():
    store = SQLiteStore(":memory:")
    pack = load_pack(PILOT, "en")
    run = launch.start(store, pack, name="Mara", seed=8, cols=100, rows=30)

    _clear_chapter(run)                                     # finish floor 1
    _stand_on(run, TileKind.STAIRS_DOWN)
    run.apply(Descend())                                    # now on floor 2, snapshot written
    pos_before = run.player.pos

    # Quit: drop the RunState entirely and rebuild from the store record alone.
    user = store.user_by_name("Mara")
    row = store.unfinished_run(user.id, pack.id)
    resumed = launch.resume(store, pack, run_row=row, name="Mara")

    assert resumed.idx == 1
    assert resumed.player.pos == pos_before
    # Every door earned on floor 1 is open again in the rebuilt grid.
    assert all(g.passed for g in resumed.chapters[0].gates.values())
    grid0 = resumed.chapters[0].chapter.grid
    assert any(grid0.at(p.x, p.y).kind is TileKind.DOOR for p in _all_points(grid0))

    # And the resumed run plays through to the scroll.
    for i in range(1, len(pack.chapters)):
        _clear_chapter(resumed)
        if i < len(pack.chapters) - 1:
            _stand_on(resumed, TileKind.STAIRS_DOWN)
            resumed.apply(Descend())
    _stand_on(resumed, TileKind.PEDESTAL)
    assert resumed.finished


def test_trophies_list_every_completion_newest_first():
    store = SQLiteStore(":memory:")
    pack = load_pack(PILOT, "en")
    user = store.user_by_name("Ada")
    r1 = store.create_run(user.id, pack.id, "1", 1, 100, 30)
    r2 = store.create_run(user.id, pack.id, "1", 2, 100, 30)
    store.award_scroll(user.id, pack.id, r1.id, 0.80)
    store.award_scroll(user.id, pack.id, r2.id, 0.95)
    lines = launch.trophies(store, pack, "ada")     # case-insensitive resolve
    assert len(lines) == 2
    assert "95.0%" in lines[0] and pack.title in lines[0]   # newest first
    assert "80.0%" in lines[1]


def test_trophies_empty_for_a_new_learner():
    store = SQLiteStore(":memory:")
    pack = load_pack(PILOT, "en")
    assert launch.trophies(store, pack, "Nobody") == []


def test_default_db_path_is_created(tmp_path):
    db = tmp_path / "sub" / "progress.db"
    store = launch.open_store(str(db))
    store.user_by_name("Ada")
    store.close()
    assert Path(db).is_file()
