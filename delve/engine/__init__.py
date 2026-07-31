"""engine: the roguelike. Dungeon, movement, vision, HP, doors.

Knows nothing about training. It imports nothing from content, assess, session, or ui
(PLAN.md section 4, rule 1). SealedWall becoming Door is the whole progression mechanic,
and it lives here with no knowledge of why it opened. Fills in from M1.
"""
