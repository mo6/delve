"""The play entry point's grader gate (DELVE-0033): the LLM grader is required to play, not merely
the default, so `delve`/`delve play` must refuse to reach curses when it isn't reachable, printing
the same diagnosis `delve doctor` would. `delve.doctor.ensure_ready` is stubbed rather than driven
through a real Ollama socket, matching how `tests/test_doctor.py` covers the check itself.
"""

from delve.__main__ import main


def test_play_refuses_to_start_and_never_reaches_curses_when_the_grader_is_not_ready(
        monkeypatch, capsys):
    reported = []

    def fake_ensure_ready(model, host, out=print):
        out("delve: the free-text grader is required to play, and isn't ready:")
        out("  [XX ] Ollama installed: not found on PATH")
        reported.append((model, host))
        return False

    def fake_ui_main(**kwargs):
        raise AssertionError("curses should never start when the grader is not ready")

    monkeypatch.setattr("delve.doctor.ensure_ready", fake_ensure_ready)
    monkeypatch.setattr("delve.ui.app.main", fake_ui_main)

    assert main([]) == 1
    assert reported                                            # ensure_ready was actually called
    err = capsys.readouterr().err
    assert "required to play" in err and "Ollama installed" in err


def test_play_starts_normally_when_the_grader_is_ready(monkeypatch):
    captured = {}

    def fake_ui_main(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr("delve.doctor.ensure_ready", lambda *a, **k: True)
    monkeypatch.setattr("delve.ui.app.main", fake_ui_main)

    assert main([]) == 0
    assert captured["grader_runner"] is not None
    assert "grader_warning" not in captured                    # no longer a ui concern (DELVE-0033)


def test_grader_model_and_host_flags_reach_ensure_ready(monkeypatch):
    seen = {}

    def fake_ensure_ready(model, host, out=print):
        seen["model"] = model
        seen["host"] = host
        return True

    monkeypatch.setattr("delve.doctor.ensure_ready", fake_ensure_ready)
    monkeypatch.setattr("delve.ui.app.main", lambda **kwargs: 0)

    assert main(["--grader-model", "qwen2.5:3b", "--grader-host", "http://example:1234"]) == 0
    assert seen == {"model": "qwen2.5:3b", "host": "http://example:1234"}
