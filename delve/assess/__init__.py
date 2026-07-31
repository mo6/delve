"""assess: the examination. Questions, graders, scoring, attempts, penalties.

Knows nothing about doors. `Grader` is a protocol from day one so the Phase 2 LLM grader
slots in without touching the engine or the format. It grades an examination; the gate
decides what a result means. Fills in from M2. See CLAUDE.md 'Question format'.
"""
