"""Per-user startup defaults from the environment: $DELVE_NAME pre-fills "Who are you?", and
$DELVE_CAT_NAME/$DELVE_DOG_NAME pre-fill the companion's name once its species is chosen. They are
resolved at the edge (like the locale detection in delve.strings) and handed to the UI opaquely;
the prompt is still shown, so a set var is an editable default, not a skip. A --name/--pet-name flag
skips the prompt and so wins over its env default.
"""

from delve import __main__ as cli


def test_env_default_reads_and_treats_blank_as_unset(monkeypatch):
    monkeypatch.setenv("DELVE_NAME", "Alex")
    assert cli._env_default("DELVE_NAME") == "Alex"
    monkeypatch.setenv("DELVE_NAME", "  Ada Lovelace  ")             # trimmed
    assert cli._env_default("DELVE_NAME") == "Ada Lovelace"
    monkeypatch.setenv("DELVE_NAME", "   ")                          # blank counts as unset
    assert cli._env_default("DELVE_NAME") is None
    monkeypatch.delenv("DELVE_NAME", raising=False)
    assert cli._env_default("DELVE_NAME") is None


def _capture_ui_kwargs(monkeypatch):
    """Run the play path with the UI stubbed out, returning the kwargs it was called with. The
    grader-readiness gate (DELVE-0033) is stubbed too, so this stays offline regardless of whether
    Ollama is installed on the machine running the tests; that gate has its own tests."""
    captured = {}

    def fake_ui_main(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr("delve.doctor.ensure_ready", lambda *a, **k: True)
    monkeypatch.setattr("delve.ui.app.main", fake_ui_main)
    assert cli.main([]) == 0
    return captured


def test_env_names_propagate_to_the_ui_as_editable_defaults(monkeypatch):
    monkeypatch.setenv("DELVE_NAME", "Ada")
    monkeypatch.setenv("DELVE_CAT_NAME", "Grimalkin")
    monkeypatch.setenv("DELVE_DOG_NAME", "Idefix")
    kwargs = _capture_ui_kwargs(monkeypatch)
    assert kwargs["name_default"] == "Ada"
    assert kwargs["pet_name_defaults"] == {"cat": "Grimalkin", "dog": "Idefix"}
    # A pre-fill is not a skip: the name/pet flags stay None, so the prompt is still shown.
    assert kwargs["name"] is None
    assert kwargs["pet_name"] is None


def test_unset_env_leaves_the_builtin_defaults_untouched(monkeypatch):
    for var in ("DELVE_NAME", "DELVE_CAT_NAME", "DELVE_DOG_NAME"):
        monkeypatch.delenv(var, raising=False)
    kwargs = _capture_ui_kwargs(monkeypatch)
    assert kwargs["name_default"] is None
    assert kwargs["pet_name_defaults"] == {"cat": None, "dog": None}
