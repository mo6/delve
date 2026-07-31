"""progress: persistence. Users, runs, room results, scrolls.

SQLite from day one so the Phase 3 hall of fame is a view, not a migration. A run is
regenerable tile-for-tile from (seed, cols, rows); only the learner's mark is stored. `models.py`
is the rows, `store.py` the SQLiteStore, `scrolls.py` the award and its formatting (M5). The
session-side `Recorder` (`session/launch.py`) is what writes here, so `ui` never imports this
package (PLAN.md section 4, rule 2). See PLAN.md section 10.
"""
