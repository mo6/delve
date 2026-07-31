"""The curses bootstrap side effects in `delve/ui/app.py` that don't need a real terminal
(DELVE-0079): `_set_esc_delay` is the one piece of `_run`'s startup worth a direct test, since it
is a pure side effect on the `curses` module, easy to fake without a whole stdscr harness.
"""

from delve.ui import app


def test_set_esc_delay_calls_curses_set_escdelay(monkeypatch):
    calls = []
    monkeypatch.setattr(app.curses, "set_escdelay", lambda ms: calls.append(ms), raising=False)
    app._set_esc_delay()
    assert calls == [app._ESC_DELAY_MS]


def test_set_esc_delay_is_a_noop_on_a_curses_build_without_the_extension(monkeypatch):
    monkeypatch.delattr(app.curses, "set_escdelay", raising=False)
    app._set_esc_delay()   # must not raise
