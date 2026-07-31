"""ui: the curses frontend, and the ONLY package that imports curses.

Its whole job is to turn a keypress into a Command and paint a Frame. It imports
`session` and nothing else from the engine side (PLAN.md section 4, rule 2). At M0 there
is no session yet: this is just the curses bootstrap and the 100x30 size guard.

Nothing outside this package imports curses. That boundary exists so the game loop can be
tested without a terminal, and so PDCurses's drift from ncurses stays contained here.
"""
