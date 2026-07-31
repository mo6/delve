"""`OllamaClient.chat`'s `json_mode`/`temperature` parameters (DELVE-0057).

`LLMGrader` needs a strict, parseable verdict, so `chat` has always forced Ollama's `format: json`
and pinned `temperature` to 0. DELVE-0028's Objectives passage reused the same client for free-form
prose and got `{}` back every time: Ollama's `format` option is a structural constraint on the
model's *output*, not a hint, so a model told its reply must be JSON has no legal move but the
smallest valid document when the prompt actually asks for sentences. These tests drive `chat`
against a fake `urlopen` and inspect the exact payload sent, so a regression here (someone
re-hardcoding `format: json`) fails loudly rather than showing up as an empty passage in play.
"""

import json
from unittest.mock import patch

from delve.assess.llm import ChatReply, OllamaClient


class _FakeResponse:
    def __init__(self, body: dict):
        self._body = json.dumps(body).encode()

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _fake_urlopen(captured, reply_text="ok"):
    def _open(req, timeout=None):
        captured["payload"] = json.loads(req.data)
        return _FakeResponse({"message": {"content": reply_text}})
    return _open


def test_default_chat_call_forces_json_mode_and_zero_temperature():
    """LLMGrader's call site passes no extra arguments; this pins today's exact wire format."""
    captured: dict = {}
    client = OllamaClient(model="m")
    with patch("urllib.request.urlopen", _fake_urlopen(captured)):
        reply = client.chat("grade this")
    assert isinstance(reply, ChatReply)
    assert captured["payload"]["format"] == "json"
    assert captured["payload"]["options"]["temperature"] == 0


def test_prose_call_omits_json_mode_and_uses_the_given_temperature():
    captured: dict = {}
    client = OllamaClient(model="m")
    with patch("urllib.request.urlopen", _fake_urlopen(captured, reply_text="A quiet hall.")):
        reply = client.chat("write a scene", json_mode=False, temperature=0.8)
    assert reply.text == "A quiet hall."
    assert "format" not in captured["payload"]
    assert captured["payload"]["options"]["temperature"] == 0.8


def test_think_false_is_unconditional_either_way():
    for kwargs in ({}, {"json_mode": False, "temperature": 0.8}):
        captured: dict = {}
        client = OllamaClient(model="m")
        with patch("urllib.request.urlopen", _fake_urlopen(captured)):
            client.chat("x", **kwargs)
        assert captured["payload"]["think"] is False
