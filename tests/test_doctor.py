"""Phase 2 step 3: the `delve doctor` / `delve setup` grader bootstrap (PHASE2.md section 7.4).

Every side effect is injected: a fake Ollama client (no socket), a fake `which` (no PATH lookup),
a fake `run_cmd` (no subprocess), and an `out` list instead of print. So the diagnostic order, the
remedies, the pull decision and the warm-up all run deterministically with nothing installed.
"""

import types

from delve.assess.llm import ChatMetrics, ChatReply, LLMUnavailable
from delve.doctor import (
    Check,
    _model_present,
    diagnose,
    ensure_ready,
    run_doctor,
    run_setup,
    warm_up,
)


class FakeClient:
    """Stands in for OllamaClient across all four checks: service reachability, the pulled-model
    list, and the warm-up grade's chat call."""

    def __init__(self, up=True, models=(), reply='{"verdict": "ACCEPT", "confidence": 0.9}',
                 chat_raises=False):
        self._up = up
        self._models = list(models)
        self._reply = reply
        self._chat_raises = chat_raises
        self.chats = 0

    def available(self):
        return self._up

    def list_models(self):
        if not self._up:
            raise LLMUnavailable("service down")
        return self._models

    def chat(self, prompt):
        self.chats += 1
        if self._chat_raises:
            raise LLMUnavailable("no model")
        return ChatReply(text=self._reply, metrics=ChatMetrics(None, None, None, None))


class FakeRun:
    """A subprocess.run stand-in that records the commands and returns a chosen exit code."""

    def __init__(self, returncode=0):
        self.returncode = returncode
        self.calls = []

    def __call__(self, cmd, *a, **k):
        self.calls.append(cmd)
        return types.SimpleNamespace(returncode=self.returncode)


def _present(_name):
    return "/usr/local/bin/ollama"


def _absent(_name):
    return None


# -- _model_present --------------------------------------------------------------------------------


def test_model_present_matches_exact_and_bare_name():
    assert _model_present("qwen2.5:3b", ["qwen2.5:3b", "llama3.2:1b"])
    assert _model_present("qwen2.5", ["qwen2.5:3b"])          # bare name matches a tag of it
    assert not _model_present("qwen2.5:7b", ["qwen2.5:3b"])
    assert not _model_present("mistral", ["qwen2.5:3b"])


# -- diagnose: reports the first thing to fix -----------------------------------------------------


def test_diagnose_binary_missing_stops_at_the_first_check():
    checks = diagnose(client=FakeClient(), which=_absent)
    assert len(checks) == 1
    assert checks[0].name == "Ollama installed" and not checks[0].ok
    assert "install it" in checks[0].remedy


def test_diagnose_service_down():
    checks = diagnose(client=FakeClient(up=False), which=_present)
    assert [c.ok for c in checks] == [True, False]           # installed, but service not running
    assert "ollama serve" in checks[-1].remedy


def test_diagnose_model_not_pulled():
    checks = diagnose("qwen2.5:3b", client=FakeClient(up=True, models=["llama3.2:1b"]),
                      which=_present)
    assert [c.ok for c in checks] == [True, True, False]
    assert "ollama pull qwen2.5:3b" in checks[-1].remedy


def test_diagnose_all_present():
    checks = diagnose("qwen2.5:3b", client=FakeClient(up=True, models=["qwen2.5:3b"]),
                      which=_present)
    assert all(c.ok for c in checks) and len(checks) == 3


# -- warm_up ---------------------------------------------------------------------------------------


def test_warm_up_ok_when_the_model_answers():
    check = warm_up(client=FakeClient())
    assert check.ok and check.detail == "grader ready"


def test_warm_up_fails_when_the_model_does_not_answer():
    # chat raises -> LLMGrader falls to the keyword floor -> source != "llm" -> warm-up not ok.
    check = warm_up(client=FakeClient(chat_raises=True))
    assert not check.ok


# -- run_doctor (read-only) ------------------------------------------------------------------------


def test_run_doctor_ready_returns_zero():
    out = []
    rc = run_doctor("qwen2.5:3b", client=FakeClient(up=True, models=["qwen2.5:3b"]),
                    which=_present, out=out.append)
    assert rc == 0
    assert any("grader ready" in line for line in out)


def test_run_doctor_not_ready_returns_one_and_says_play_needs_it():
    out = []
    rc = run_doctor(client=FakeClient(), which=_absent, out=out.append)
    assert rc == 1
    assert any("requires it to play" in line for line in out)
    assert any("install it" in line for line in out)         # the remedy for the first failure


def test_run_doctor_does_not_warm_up_when_a_check_fails():
    client = FakeClient(up=True, models=[])                  # model missing -> not ready
    run_doctor("qwen2.5:3b", client=client, which=_present, out=lambda _l: None)
    assert client.chats == 0                                  # no warm-up grade attempted


# -- run_setup (fixes what is safe) ----------------------------------------------------------------


def test_run_setup_pulls_a_missing_model_then_warms_up():
    out, run = [], FakeRun(returncode=0)
    client = FakeClient(up=True, models=[])                  # not pulled yet
    rc = run_setup("qwen2.5:3b", client=client, which=_present, run_cmd=run, out=out.append)
    assert run.calls == [["ollama", "pull", "qwen2.5:3b"]]    # it pulled
    assert rc == 0 and client.chats == 1                     # then warmed up


def test_run_setup_skips_the_pull_when_the_model_is_present():
    out, run = [], FakeRun()
    client = FakeClient(up=True, models=["qwen2.5:3b"])
    rc = run_setup("qwen2.5:3b", client=client, which=_present, run_cmd=run, out=out.append)
    assert run.calls == []                                    # nothing to pull
    assert rc == 0


def test_run_setup_prints_install_command_when_binary_missing():
    out, run = [], FakeRun()
    rc = run_setup(client=FakeClient(), which=_absent, run_cmd=run, out=out.append)
    assert rc == 1 and run.calls == []                       # never touched the shell
    assert any("not installed" in line for line in out)


def test_run_setup_tells_you_to_start_the_service_when_down():
    out, run = [], FakeRun()
    rc = run_setup(client=FakeClient(up=False), which=_present, run_cmd=run, out=out.append)
    assert rc == 1 and run.calls == []
    assert any("ollama serve" in line for line in out)


def test_run_setup_reports_a_failed_pull():
    out, run = [], FakeRun(returncode=1)                     # pull fails
    client = FakeClient(up=True, models=[])
    rc = run_setup("qwen2.5:3b", client=client, which=_present, run_cmd=run, out=out.append)
    assert rc == 1 and client.chats == 0                     # no warm-up after a failed pull
    assert any("did not succeed" in line for line in out)


def test_check_is_a_frozen_dataclass():
    c = Check("x", True, "d")
    assert c.ok and c.remedy == ""


# -- ensure_ready (play's startup gate, DELVE-0033) -----------------------------------------------


def test_ensure_ready_true_when_the_grader_is_ready():
    out = []
    assert ensure_ready("qwen2.5:3b", client=FakeClient(up=True, models=["qwen2.5:3b"]),
                        which=_present, out=out.append)
    assert out == []                                          # nothing printed on the happy path


def test_ensure_ready_false_and_prints_the_doctor_diagnosis_when_binary_missing():
    out = []
    ready = ensure_ready(client=FakeClient(), which=_absent, out=out.append)
    assert not ready
    assert any("required to play" in line for line in out)
    assert any("Ollama installed" in line for line in out)   # the same check doctor reports
    assert any("install it" in line for line in out)          # its remedy


def test_ensure_ready_false_when_service_down():
    out = []
    ready = ensure_ready(client=FakeClient(up=False), which=_present, out=out.append)
    assert not ready
    assert any("ollama serve" in line for line in out)


def test_ensure_ready_false_when_model_not_pulled():
    out = []
    ready = ensure_ready("qwen2.5:3b", client=FakeClient(up=True, models=[]),
                         which=_present, out=out.append)
    assert not ready
    assert any("ollama pull qwen2.5:3b" in line for line in out)


def test_ensure_ready_does_not_warm_up():
    client = FakeClient(up=True, models=["qwen2.5:3b"])
    ensure_ready("qwen2.5:3b", client=client, which=_present, out=lambda _l: None)
    assert client.chats == 0                                  # no inference call at startup
