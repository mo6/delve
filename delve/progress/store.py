"""The progress store: users, runs, room results, scrolls (PLAN.md section 10).

SQLite from day one so the Phase 3 hall of fame is a view, not a migration. The schema is exactly
section 10's: a run records the layout inputs and a snapshot blob (the grid is never stored, only
regenerated); `room_results` is write-once per room in a run (passing is final, CLAUDE.md rule 3),
enforced by a UNIQUE constraint and INSERT OR IGNORE; every completion writes its own `scrolls`
row and none is ever updated, because re-taking a pack keeps both (a learner's history is their
collection, section 10).

`Store` is a Protocol so a test or a future backend can stand in; `SQLiteStore(":memory:")` is the
in-memory store the tests use. The store stamps its own timestamps in UTC ISO-8601.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Protocol

from delve.progress.models import Run, Scroll, User

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    id           INTEGER PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    pack_id      TEXT NOT NULL,
    pack_version TEXT NOT NULL,
    seed         INTEGER NOT NULL,
    map_cols     INTEGER NOT NULL,
    map_rows     INTEGER NOT NULL,
    snapshot     TEXT,
    started_at   TEXT NOT NULL,
    finished_at  TEXT,
    outcome      TEXT
);
CREATE TABLE IF NOT EXISTS room_results (
    id         INTEGER PRIMARY KEY,
    run_id     INTEGER NOT NULL REFERENCES runs(id),
    chapter_id TEXT NOT NULL,
    room_id    TEXT NOT NULL,
    attempts   INTEGER NOT NULL,
    score      REAL NOT NULL,
    hints_used INTEGER NOT NULL,
    passed_at  TEXT NOT NULL,
    UNIQUE (run_id, room_id)
);
CREATE TABLE IF NOT EXISTS scrolls (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    pack_id    TEXT NOT NULL,
    run_id     INTEGER NOT NULL REFERENCES runs(id),
    score      REAL NOT NULL,
    awarded_at TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(UTC).isoformat()


class Store(Protocol):
    def user_by_name(self, name: str) -> User: ...
    def create_run(self, user_id: int, pack_id: str, pack_version: str,
                   seed: int, cols: int, rows: int) -> Run: ...
    def unfinished_run(self, user_id: int, pack_id: str) -> Run | None: ...
    def save_snapshot(self, run_id: int, snapshot: str) -> None: ...
    def save_room_result(self, run_id: int, chapter_id: str, room_id: str,
                         attempts: int, score: float, hints_used: int) -> None: ...
    def finish_run(self, run_id: int, outcome: str) -> None: ...
    def award_scroll(self, user_id: int, pack_id: str, run_id: int, score: float) -> Scroll: ...
    def trophy_case(self, user_id: int) -> list[Scroll]: ...
    def close(self) -> None: ...


class SQLiteStore:
    """A SQLite-backed `Store`. Pass a file path to persist, or ':memory:' for a throwaway one."""

    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    # -- users ----------------------------------------------------------------------------

    def user_by_name(self, name: str) -> User:
        """Match an existing user case-insensitively, or create one. Identity is trust-based and a
        name is all it takes (PLAN.md section 10); the stored name keeps the first spelling seen."""
        row = self.conn.execute(
            "SELECT * FROM users WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
        if row is None:
            created = _now()
            cur = self.conn.execute(
                "INSERT INTO users (name, created_at) VALUES (?, ?)", (name, created))
            self.conn.commit()
            return User(id=cur.lastrowid, name=name, created_at=created)
        return User(**dict(row))

    # -- runs -----------------------------------------------------------------------------

    def create_run(self, user_id: int, pack_id: str, pack_version: str,
                   seed: int, cols: int, rows: int) -> Run:
        started = _now()
        cur = self.conn.execute(
            "INSERT INTO runs (user_id, pack_id, pack_version, seed, map_cols, map_rows, "
            "started_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, pack_id, pack_version, seed, cols, rows, started))
        self.conn.commit()
        return self._run(cur.lastrowid)

    def unfinished_run(self, user_id: int, pack_id: str) -> Run | None:
        """The learner's most recent run of this pack that was never finished, or None. This is
        the run the resume prompt offers to continue (PLAN.md section 10). An unfinished row older
        than a later completed run of the same pack is superseded and not offered (DELVE-0084)."""
        row = self.conn.execute(
            "SELECT * FROM runs WHERE user_id = ? AND pack_id = ? AND finished_at IS NULL "
            "AND id > COALESCE(("
            "  SELECT MAX(id) FROM runs "
            "  WHERE user_id = ? AND pack_id = ? AND finished_at IS NOT NULL"
            "), 0) "
            "ORDER BY id DESC LIMIT 1",
            (user_id, pack_id, user_id, pack_id)).fetchone()
        return Run(**dict(row)) if row else None

    def save_snapshot(self, run_id: int, snapshot: str) -> None:
        self.conn.execute("UPDATE runs SET snapshot = ? WHERE id = ?", (snapshot, run_id))
        self.conn.commit()

    def finish_run(self, run_id: int, outcome: str) -> None:
        self.conn.execute(
            "UPDATE runs SET finished_at = ?, outcome = ? WHERE id = ?",
            (_now(), outcome, run_id))
        self.conn.commit()

    def _run(self, run_id: int) -> Run:
        row = self.conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return Run(**dict(row))

    # -- room results ---------------------------------------------------------------------

    def save_room_result(self, run_id: int, chapter_id: str, room_id: str,
                         attempts: int, score: float, hints_used: int) -> None:
        """Record a passed room. Write-once per (run, room): a later re-read never overwrites the
        result, because passing is final (CLAUDE.md rule 3)."""
        self.conn.execute(
            "INSERT OR IGNORE INTO room_results (run_id, chapter_id, room_id, attempts, score, "
            "hints_used, passed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, chapter_id, room_id, attempts, score, hints_used, _now()))
        self.conn.commit()

    # -- scrolls --------------------------------------------------------------------------

    def award_scroll(self, user_id: int, pack_id: str, run_id: int, score: float) -> Scroll:
        awarded = _now()
        cur = self.conn.execute(
            "INSERT INTO scrolls (user_id, pack_id, run_id, score, awarded_at) "
            "VALUES (?, ?, ?, ?, ?)", (user_id, pack_id, run_id, score, awarded))
        self.conn.commit()
        return Scroll(id=cur.lastrowid, user_id=user_id, pack_id=pack_id, run_id=run_id,
                      score=score, awarded_at=awarded)

    def trophy_case(self, user_id: int) -> list[Scroll]:
        """Every scroll the learner has earned, newest first. Re-taking keeps both, so a pack the
        learner finished twice appears twice (PLAN.md section 10)."""
        rows = self.conn.execute(
            "SELECT * FROM scrolls WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
        return [Scroll(**dict(r)) for r in rows]

    def close(self) -> None:
        self.conn.close()
