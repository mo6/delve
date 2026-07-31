"""`delve doctor` / `delve setup`: the free-text grader bootstrap (PHASE2.md section 7.4, step 3).

`doctor` is a read-only diagnostic: is Ollama installed, is its service up, is the grader model
pulled, does a warm-up grade come back from the model. It prints a copy-pasteable report and a
remedy for anything missing, so support is a screenshot. `setup` (also `doctor --fix`) additionally
performs the *safe, reversible* remedies: it pulls the model and runs the warm-up. Installing the
Ollama binary and starting its service touch the machine in ways that are not cleanly reversible, so
those follow the design's other branch, print the single command to run and stop, rather than piping
an installer to a shell unasked.

Nothing here is on the run's hot path, so it imports freely (subprocess, shutil, the `assess.llm`
seam); it is reached only from the CLI. `ensure_ready` is the exception: it is play's startup gate
(DELVE-0033), so `delve/__main__.py` calls it before curses starts and refuses to play when the
grader isn't ready, printing the same diagnosis `doctor` would. The keyword floor still exists as an
internal, mid-run fallback for a single garbled/low-confidence verdict (`assess.grader.LLMGrader`'s
`fallback`), but it is no longer a supported way to play with no model at all.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass

from delve.assess.llm import DEFAULT_HOST, DEFAULT_MODEL, LLMUnavailable, OllamaClient


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str
    remedy: str = ""       # what to do about it when not ok; shown by the report


def _install_hint() -> str:
    """The single command to install Ollama, per platform (PHASE2.md section 7.4)."""
    if sys.platform == "darwin":
        return "brew install ollama   (or download from https://ollama.com/download)"
    if sys.platform.startswith("linux"):
        return "curl -fsSL https://ollama.com/install.sh | sh"
    return "download the installer from https://ollama.com/download"


def _model_present(model: str, names: list[str]) -> bool:
    """Is `model` among the pulled `names`? Exact match, or a bare name (no tag) matching any tag of
    it, so `qwen2.5:3b` and a plain `qwen2.5` both resolve sensibly."""
    if model in names:
        return True
    if ":" not in model:
        return any(n.split(":")[0] == model for n in names)
    return False


def diagnose(model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST, *,
             client: OllamaClient | None = None, which=shutil.which) -> list[Check]:
    """The four checks, in dependency order: binary, service, model, (warm-up is separate because it
    costs a real grade). Each later check is skipped-as-failed when an earlier one fails, so the
    report always names the *first* thing to fix. Pure but for the injected `client`/`which`."""
    client = client or OllamaClient(model, host)
    checks: list[Check] = []

    binary = which("ollama")
    checks.append(Check("Ollama installed", bool(binary),
                        binary or "not found on PATH",
                        remedy=f"install it:  {_install_hint()}"))
    if not binary:
        return checks

    up = client.available()
    checks.append(Check("service running", up, host if up else f"{host} not answering",
                        remedy="start it:  ollama serve"))
    if not up:
        return checks

    try:
        names = client.list_models()
    except LLMUnavailable:
        names = []
    present = _model_present(model, names)
    checks.append(Check(f"model {model!r} pulled", present,
                        "present" if present else "not pulled",
                        remedy=f"pull it:  ollama pull {model}"))
    return checks


def ensure_ready(model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST, *,
                 client: OllamaClient | None = None, which=shutil.which, out=print) -> bool:
    """Play's startup gate (DELVE-0033): the LLM grader is required to play, not merely a default,
    so this runs the same structural checks `delve doctor` reports (binary, service, model pulled)
    and prints the same diagnosis when one fails, before curses ever starts. No warm-up grade here;
    that costs a real inference call on every launch, and the mid-run `KeywordGrader` fallback
    already covers a single garbled/low-confidence verdict, so a warm-up isn't needed just to decide
    whether play may start. Pure but for the injected `client`/`which`/`out`."""
    client = client or OllamaClient(model, host)
    checks = diagnose(model, host, client=client, which=which)
    ready = all(c.ok for c in checks)
    if not ready:
        out("delve: the free-text grader is required to play, and isn't ready:")
        _report(checks, out)
        out("run 'delve setup' to prepare it, or 'delve doctor' for the full report.")
    return ready


def warm_up(model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST, *,
            client: OllamaClient | None = None) -> Check:
    """One real grade through the production `LLMGrader`, so 'grader ready' means the whole path
    works, not just that the service answered. A verdict that fell to the keyword floor (source is
    not 'llm') means the model did not usably respond; free text will still play, on the floor."""
    from delve.assess.grader import LLMGrader
    from delve.assess.question import Question
    client = client or OllamaClient(model, host)
    q = Question(prompt="Name a primary colour.", explanation="",
                 accept=("red", "blue", "green", "yellow"))
    verdict = LLMGrader(client).grade_text(q, "blue")
    if verdict.source == "llm":
        return Check("warm-up grade", True, "grader ready")
    return Check("warm-up grade", False,
                 "no usable verdict from the model; free text will use the keyword fallback",
                 remedy="check that the model is pulled and the service is running")


def _report(checks: list[Check], out) -> None:
    for c in checks:
        out(f"  [{'ok ' if c.ok else 'XX '}] {c.name}: {c.detail}")
        if not c.ok and c.remedy:
            out(f"         {c.remedy}")


def run_doctor(model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST, *,
               client: OllamaClient | None = None, which=shutil.which, out=print) -> int:
    """Report the grader's health and stop; change nothing. Exit 0 when the whole path is ready
    (every check passes and a warm-up grade comes back from the model), 1 otherwise, so a script or
    a support flow can gate on it."""
    client = client or OllamaClient(model, host)
    out("delve grader doctor")
    checks = diagnose(model, host, client=client, which=which)
    if all(c.ok for c in checks):
        checks = [*checks, warm_up(model, host, client=client)]
    _report(checks, out)
    ready = all(c.ok for c in checks)
    out("grader ready: free-text answers will be graded on meaning." if ready else
        "grader not ready: delve requires it to play.\n"
        "run 'delve setup' to fix the first item above.")
    return 0 if ready else 1


def run_setup(model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST, *,
              client: OllamaClient | None = None, which=shutil.which,
              run_cmd=subprocess.run, out=print) -> int:
    """Fix what can be fixed safely, then warm up. Pulls the model (reversible: `ollama rm`) and
    runs a warm-up grade; for the binary and the service it prints the one command to run and
    stops, rather than installing or starting software unasked (PHASE2.md section 7.4)."""
    client = client or OllamaClient(model, host)
    out(f"delve setup: preparing the free-text grader ({model})")

    if not which("ollama"):
        out(f"Ollama is not installed. Install it, then run 'delve setup' again:\n  "
            f"{_install_hint()}")
        return 1
    if not client.available():
        out(f"Ollama is installed but its service is not running at {host}. Start it, then run "
            f"'delve setup' again:\n  ollama serve")
        return 1

    try:
        names = client.list_models()
    except LLMUnavailable:
        names = []
    if not _model_present(model, names):
        out(f"Pulling {model} (a one-time download of a couple of gigabytes)...")
        result = run_cmd(["ollama", "pull", model])
        if getattr(result, "returncode", 1) != 0:
            out(f"'ollama pull {model}' did not succeed; free text will use the keyword fallback.")
            return 1

    check = warm_up(model, host, client=client)
    out(f"  [{'ok ' if check.ok else 'XX '}] {check.detail}")
    return 0 if check.ok else 1
