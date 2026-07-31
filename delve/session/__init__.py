"""session: the application loop. Headless: no curses, no HTTP, no I/O.

`apply(Command) -> Frame`, never blocking. This is where the loop lives so it can be
tested without a terminal (PLAN.md section 4): a test plays a whole run as a list of
Commands and asserts on the Frame. No display types cross this line. Fills in from M1/M2.
"""
