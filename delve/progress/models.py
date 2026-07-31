"""The rows of the progress store, one dataclass per table (PLAN.md section 10).

Plain data, no behaviour. A run is regenerable tile-for-tile from (seed, map_cols, map_rows,
pack_id, pack_version), so `Run` stores those inputs plus the learner's mark as a snapshot blob;
the grid itself is never persisted. `RoomResult.passed_at` is write-once (passing is final,
CLAUDE.md rule 3), and every completion writes its own `Scroll` row, kept forever, because a
learner's history is their collection (PLAN.md section 10; re-taking keeps both).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    name: str
    created_at: str


@dataclass(frozen=True)
class Run:
    id: int
    user_id: int
    pack_id: str
    pack_version: str
    seed: int
    map_cols: int
    map_rows: int
    snapshot: str | None      # JSON of the learner's mark, or None before the first save
    started_at: str
    finished_at: str | None   # None while the run is still in progress (resumable)
    outcome: str | None       # 'completed' when the scroll is taken; None otherwise


@dataclass(frozen=True)
class RoomResult:
    id: int
    run_id: int
    chapter_id: str
    room_id: str
    attempts: int
    score: float
    hints_used: int
    passed_at: str


@dataclass(frozen=True)
class Scroll:
    id: int
    user_id: int
    pack_id: str
    run_id: int
    score: float
    awarded_at: str
