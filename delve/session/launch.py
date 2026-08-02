"""Starting and resuming a run against the store, kept on the session side so `ui` never imports
`progress` (PLAN.md section 4, rule 2): the shell asks the name, then hands it here.

`Recorder` is the object `RunState` calls on the transitions worth persisting, a room passed, a
chapter changed, the scroll taken; it turns those into store writes and a snapshot. `start` opens
a fresh run and takes its first snapshot; `resume` rebuilds the locked dungeon from the run's
stored (seed, cols, rows) and lays the snapshot back over it. The dungeon is never stored, only
regenerated (PLAN.md section 10), so resuming a run needs nothing but its record.
"""

import json
from datetime import datetime
from pathlib import Path

from delve.content.pack import Pack
from delve.content.parser import load_pack
from delve.progress.models import Run
from delve.progress.scrolls import format_date, format_money, format_score
from delve.progress.store import SQLiteStore, Store
from delve.session.run import RunState, new_game
from delve.session.snapshot import apply_dict, to_dict
from delve.strings import Strings
from delve.strings import load as load_strings

# The pilot ships in the repo; the installed layout can override this later. parents[2] is the
# repo root (delve/session/launch.py -> delve/ -> repo).
PILOT_PACK = Path(__file__).resolve().parents[2] / "packs" / "security-onboarding"

# The engine's own Dlvl 0 orientation floor, in the ordinary pack format so it translates and
# validates like anything else (PLAN.md section 9). It ships with the engine, not with each pack.
TUTORIAL_PACK = Path(__file__).resolve().parents[1] / "tutorial"

# The pack format carries no version field yet; recorded as a constant so runs.pack_version exists
# for the day a pack is edited (PLAN.md section 10). Bump when packs gain real versions.
PACK_VERSION = "1"


class Recorder:
    """Bridges a live RunState to the store. Held by the run and called on persist-worthy
    transitions; without one (tests, the M2 slice) the run simply persists nothing."""

    def __init__(self, store: Store, user_id: int, run_id: int, pack_id: str):
        self.store = store
        self.user_id = user_id
        self.run_id = run_id
        self.pack_id = pack_id

    def room_passed(self, chapter_id: str, gate) -> None:
        self.store.save_room_result(self.run_id, chapter_id, gate.content.id,
                                    gate.sittings, gate.passed_score, gate.hints_used)

    def save(self, run: RunState) -> None:
        self.store.save_snapshot(self.run_id, json.dumps(to_dict(run)))

    def finished(self, run: RunState, score: float) -> None:
        self.store.award_scroll(self.user_id, self.pack_id, self.run_id, score)
        self.store.finish_run(self.run_id, "completed")


def open_store(path: str | None = None) -> Store:
    """Open the progress store, defaulting to ~/.delve/progress.db. The parent directory is
    created if absent (for the default and any explicit file path alike)."""
    db = Path(path) if path is not None else Path.home() / ".delve" / "progress.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    return SQLiteStore(str(db))


def load_pilot(locale: str = "en") -> Pack:
    return load_pack(PILOT_PACK, locale)


def load_pack_dir(path: str, locale: str = "en") -> Pack:
    """Load an arbitrary pack directory (the folder holding en/ and nl/), for `delve --pack`.
    Raises `PackError` on a malformed or absent pack, which the CLI turns into a clean message."""
    return load_pack(Path(path), locale)


def load_tutorial(locale: str = "en") -> Pack:
    """The Dlvl 0 orientation floor for `locale`, as an ordinary parsed Pack (PLAN.md section 9)."""
    return load_pack(TUTORIAL_PACK, locale)


def default_strings() -> Strings:
    """The English catalogue, for a direct `ui.main` caller (a test) that passes no locale. Kept
    here so `ui` gets a Strings object without importing the strings package (rule 2)."""
    return load_strings("en")


def outcome_lines(run: RunState) -> list[str]:
    """The win screen as ready-to-print lines (M8), formatted and localised on the session side so
    `ui` never touches the strings catalogue or `scrolls` (rule 2). There is no losing outcome to
    render: REPELLED is not death and HP:0 respawns (CLAUDE.md rule 4)."""
    s = run.strings
    pack = run.pack.title if run.pack is not None else ""
    score = format_score(run.pack_score(), s.fmt)
    lines = [s("win.title"), "", s("win.body", pack=pack, score=score)]
    # Wealth earned along the way, shown only when a keeper actually paid (OBJECTS.md section 5).
    if run.player.gold > 0:
        lines.append(s("win.wealth", coins=format_money(run.player.gold, s.fmt)))
    lines += ["", s("ui.press_any")]
    return lines


def has_completed_run(store: Store, name: str) -> bool:
    """Whether this learner has ever finished a training. Used to default the tutorial skip to
    yes for a returning learner and to no for a newcomer (PLAN.md section 9)."""
    user = store.user_by_name(name)
    return bool(store.trophy_case(user.id))


def pending_run(store: Store, pack: Pack, name: str) -> Run | None:
    """The learner's unfinished run of this pack, if any, ready for the resume prompt. Resolves
    (and creates) the user by name as a side effect, which is what the fresh start needs too."""
    user = store.user_by_name(name)
    return store.unfinished_run(user.id, pack.id)


def trophies(store: Store, pack: Pack, name: str, strings: Strings | None = None) -> list[str]:
    """The learner's trophy case as ready-to-print lines, newest first, so the UI never touches a
    progress type (rule 2). Every completion is its own line; re-taking a pack shows both. Only
    the loaded pack's id resolves to a title (the others print their id) until packs are indexed.
    Score and date format in `strings`' locale (English if none is given)."""
    fmt = strings.fmt if strings is not None else None
    user = store.user_by_name(name)
    lines: list[str] = []
    for s in store.trophy_case(user.id):
        title = pack.title if s.pack_id == pack.id else s.pack_id
        try:
            when = format_date(datetime.fromisoformat(s.awarded_at), fmt)
        except ValueError:
            when = s.awarded_at
        lines.append(f"{format_score(s.score, fmt):>6}   {title}   {when}")
    return lines


def start(store: Store, pack: Pack, *, name: str, seed: int, cols: int, rows: int,
          strings: Strings | None = None, tutorial: Pack | None = None,
          skip_tutorial: bool = False, pet_species: str = "cat",
          pet_name: str | None = None, grader_runner=None) -> RunState:
    """Begin a fresh run: create its record, wire a recorder, and take the opening snapshot. The
    tutorial floor is built into the dungeon (Dlvl 0) unless absent; `skip_tutorial` only starts
    the learner below it. `pet_species`/`pet_name` are the companion choice (PETS.md), captured in
    the snapshot rather than the run record, so `resume` recovers them from there."""
    user = store.user_by_name(name)
    row = store.create_run(user.id, pack.id, PACK_VERSION, seed, cols, rows)
    recorder = Recorder(store, user.id, row.id, pack.id)
    run = new_game(pack, seed, cols, rows, name=name, recorder=recorder, strings=strings,
                   tutorial=tutorial, skip_tutorial=skip_tutorial, pet_species=pet_species,
                   pet_name=pet_name, grader_runner=grader_runner)
    recorder.save(run)
    return run


def resume(store: Store, pack: Pack, *, run_row: Run, name: str, strings: Strings | None = None,
           tutorial: Pack | None = None, grader_runner=None) -> RunState:
    """Continue an unfinished run from its snapshot, rebuilding the exact dungeon it was laid on
    (its stored seed and size), then re-opening every door the learner had earned. The `tutorial`
    is rebuilt in too, so the chapter list matches the snapshot it is laid back over. The
    `grader_runner` is rebuilt from config, not the snapshot: it is policy, not run state.

    Construction skips the constructor's `_observe` (DELVE-0094): a brand-new `RunState` would
    otherwise queue an ambient toast for the pack's spawn room before `apply_dict` moves the
    learner elsewhere, and that call's chapter almost never matches the restored one, so
    `_poll_toast` would silently drop it after the loading spinner had already promised it.
    `_observe` runs once below, against the restored position, so a genuinely unvisited restored
    room still gets its toast and an already-visited one queues nothing."""
    recorder = Recorder(store, run_row.user_id, run_row.id, pack.id)
    run = new_game(pack, run_row.seed, run_row.map_cols, run_row.map_rows,
                   name=name, recorder=recorder, strings=strings, tutorial=tutorial,
                   grader_runner=grader_runner, observe=False)
    if run_row.snapshot:
        apply_dict(run, json.loads(run_row.snapshot))
    run._observe()
    return run
