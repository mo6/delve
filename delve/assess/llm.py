"""The one outward edge: an HTTP client to a locally hosted model (PHASE2.md section 3).

This is the **only** module in the core that opens a socket, the same discipline as `ui/` being
the only module that imports curses. `LLMGrader` is handed a client through this seam; everything
else in `assess` stays pure, and a test swaps in a fake with no network. Ollama's local API
(`/api/chat`) is the default runtime (PHASE2.md section 7); stdlib `urllib` only, no third-party
client, keeping the stdlib-only line for the core. Importing this module opens nothing; a socket is
opened only when `chat`/`available` is called.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlparse

# The recommended default of PHASE2.md section 7.2: a small, permissive (Apache-2.0) short-answer
# judge, validated by the spike. An operator may pin another with --grader-model.
DEFAULT_MODEL = "qwen2.5:3b"
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_TIMEOUT = 60          # a cold model load can be slow; grading itself is far quicker

_ALLOWED_SCHEMES = frozenset({"http", "https"})


@dataclass(frozen=True)
class ChatMetrics:
    """The reply fields Ollama returns beyond the message text, kept instead of discarded
    (DELVE-0053, INFOSCREEN.md section 7). Durations are converted from Ollama's nanoseconds to
    whole milliseconds; any field absent from the reply is `None`, never `0`, so "unknown" is
    never confused with "instant" or "zero tokens" by a later consumer."""

    total_duration_ms: int | None
    load_duration_ms: int | None
    prompt_tokens: int | None
    completion_tokens: int | None

    @property
    def warm(self) -> bool | None:
        """False when this call's reply reports it loaded the model (a real, non-zero
        `load_duration`); True when it reports no load; None when the reply didn't say."""
        if self.load_duration_ms is None:
            return None
        return self.load_duration_ms == 0


@dataclass(frozen=True)
class ChatReply:
    """`OllamaClient.chat`'s full result: the text a grader parses, plus the metrics beside it."""

    text: str
    metrics: ChatMetrics


def _ns_to_ms(value: object) -> int | None:
    return int(value) // 1_000_000 if isinstance(value, (int, float)) else None


def _as_int(value: object) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


class LLMUnavailable(Exception):
    """The model could not be reached, timed out, or returned nothing usable. `LLMGrader` catches
    this and falls to the keyword floor (PHASE2.md section 8), so a missing or sleeping model never
    blocks a room; it only lowers grading quality."""


def _http_url(url: str) -> str:
    """Reject anything that is not http(s). The host is operator-configured (default localhost),
    but a typo or a `file:` value must not reach urlopen."""
    scheme = urlparse(url).scheme.lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise LLMUnavailable(f"refusing non-http URL scheme: {scheme!r}")
    return url


class OllamaClient:
    """A thin client over Ollama's local chat API. Constrains the reply to JSON and pins the
    temperature to 0 (grading is judgement, not generation), the two settings the spike found make
    the reply robust to parse. `think: false` is also unconditional (DELVE-0052): a thinking
    model's reasoning trace is pure overhead here, since `LLMGrader` only reads the JSON verdict,
    and it can eat the whole `DEFAULT_TIMEOUT` before any content comes back. Any transport or
    protocol error becomes `LLMUnavailable`."""

    def __init__(self, model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST,
                 timeout: int = DEFAULT_TIMEOUT):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def chat(self, prompt: str, *, json_mode: bool = True, temperature: float = 0,
             model: str | None = None) -> ChatReply:
        """Send one prompt, return the model's raw text reply plus the reply's timing/token fields
        (DELVE-0053). Raises `LLMUnavailable` on any transport or protocol failure, or when the
        reply carries no usable text, so the grader falls back rather than crashing; a reply
        missing only the optional metrics fields still succeeds, with those fields `None`.

        `json_mode`/`temperature` default to exactly what `LLMGrader` has always sent (constrained
        JSON, temperature 0, the two settings the spike found make a verdict robust to parse), so
        that call site needs no change. A caller asking for prose rather than a verdict (the
        ambient toast, DELVE-0028/DELVE-0057/DELVE-0060) passes `json_mode=False` and a non-zero
        temperature: Ollama's `format: json` is a structural constraint on the *output*, not a
        suggestion, so a model asked for atmospheric prose while forced into JSON mode has no legal
        move but to emit the smallest valid document it can, `{}`, regardless of the prompt.

        `model` overrides `self.model` for this one call, defaulting to it when omitted: a caller
        can ask a client already configured for one model (the grader's own) to use a different
        one for a specific call (the ambient toast deliberately uses a different, more capable
        model, `RunState._BACKSTORY_MODEL`) without constructing a second client, which would lose
        whatever host/timeout/test-double the first one was already carrying."""
        payload = {
            "model": model or self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": False,
            "options": {"temperature": temperature},
        }
        if json_mode:
            payload["format"] = "json"
        req = urllib.request.Request(
            _http_url(f"{self.host}/api/chat"),
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read())
            text = body["message"]["content"]
        except (urllib.error.URLError, TimeoutError, OSError, KeyError,
                json.JSONDecodeError) as exc:
            raise LLMUnavailable(str(exc)) from exc
        metrics = ChatMetrics(
            total_duration_ms=_ns_to_ms(body.get("total_duration")),
            load_duration_ms=_ns_to_ms(body.get("load_duration")),
            prompt_tokens=_as_int(body.get("prompt_eval_count")),
            completion_tokens=_as_int(body.get("eval_count")),
        )
        return ChatReply(text=text, metrics=metrics)

    def available(self) -> bool:
        """A cheap reachability check: is the Ollama service up? For choosing the grader at startup
        and for `delve doctor` (step 3). Never raises."""
        try:
            req = urllib.request.Request(_http_url(f"{self.host}/api/tags"))
            with urllib.request.urlopen(req, timeout=5):
                return True
        except (OSError, LLMUnavailable):
            return False

    def list_models(self) -> list[str]:
        """The names of the models the local service has pulled (from `/api/tags`), so `delve
        doctor`/`setup` can tell whether the grader model is present. Raises `LLMUnavailable` on a
        transport error, the same as `chat`; callers guard with `available` first."""
        req = urllib.request.Request(_http_url(f"{self.host}/api/tags"))
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read())
            return [m["name"] for m in body.get("models", [])]
        except (urllib.error.URLError, TimeoutError, OSError, KeyError,
                json.JSONDecodeError) as exc:
            raise LLMUnavailable(str(exc)) from exc
