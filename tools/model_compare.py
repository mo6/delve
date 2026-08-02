#!/usr/bin/env python3
"""Benchmark candidate Ollama models against Delve's real ambient/nudge prompts (DELVE-0047's
"a tools/ dev helper if judged worth keeping"). Not part of the delve package and not imported by
it, exactly like screenshot.py and issues.py; it opens a socket to a local Ollama, so it's a
dev tool, never run by run-tests.sh or the game itself.

    ./tools.sh model_compare                                  # default model set, JSON to stdout
    ./tools.sh model_compare gemma3:4b qwen3.5:9b qwen2.5:3b   # explicit models
    ./tools.sh model_compare --out results.json qwen3.5:9b

Builds the same prompts session/backstory.py sends in play (build_prompt for room/keeper/objects
ambient toasts, build_nudge_prompt for the nudge), across English and Dutch, and times each
model's real round trip through the same assess/llm.py:OllamaClient seam the game itself calls.
Prints per-scenario timings to stderr as it goes and writes the full results (text, token counts,
wall time, Ollama's own reported duration) as JSON, for turning into a report by hand.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from delve.assess.llm import OllamaClient  # noqa: E402  (path set up above)
from delve.session import backstory  # noqa: E402

DEFAULT_MODELS = ["qwen3.5:9b", "qwen2.5:3b"]

# Titles, chapter names, keeper names and lesson topics below are pulled verbatim from the four
# shipped packs (security-onboarding, holy-grail, friends-nap-partners, ethics-of-ai), both
# locales, via `load_pack`, so the scenarios exercise real pack variety rather than one invented
# dungeon repeated with different numbers.
SCENARIOS = [
    ("security-onboarding / lit / gated / bare floor / EN",
     dict(pack="The Caverns of Compliance", dlvl=1, chapter_title="The Sorting Office",
          keeper="Ada the Suspicious", requirement="70%",
          lesson_topic="Recognising a phish", has_light=True, language="English")),
    ("security-onboarding / unlit / gated / objects+cat / EN",
     dict(pack="The Caverns of Compliance", dlvl=3, chapter_title="The Archive",
          keeper="Marisol the Archivist", requirement="75%",
          lesson_topic="Knowing what you're holding",
          room_objects="a rusted lockbox, a stack of yellowed ledgers",
          carrying="70 coins, a coconut half", pet="cat named Whiskers",
          has_light=False, language="English")),
    ("security-onboarding / lit / ungated / objects, dog, no keeper / EN",
     dict(pack="The Caverns of Compliance", dlvl=2, chapter_title="The Vault",
          room_objects="scattered index cards, a broken quill", carrying="a torch",
          pet="dog named Rex", has_light=True, language="English")),
    ("security-onboarding / lit / gated / bare floor / NL",
     dict(pack="De grotten der naleving", dlvl=2, chapter_title="De kluis",
          keeper="Entropie, Hoedster der Sleutels", requirement="75%",
          lesson_topic="Lengte verslaat slimheid", has_light=True, language="Dutch")),
    ("security-onboarding / unlit / gated / objects+cat / NL",
     dict(pack="De grotten der naleving", dlvl=3, chapter_title="Het archief",
          keeper="Marisol de Archivaris", requirement="75%",
          lesson_topic="Weten wat je vasthoudt",
          room_objects="een verroeste kluis, een stapel vergeelde grootboeken",
          carrying="70 munten, een halve kokosnoot", pet="kat genaamd Whiskers",
          has_light=False, language="Dutch")),
    ("holy-grail / lit / gated / bare floor / EN",
     dict(pack="The Caverns of Camelot", dlvl=2, chapter_title="The Road",
          keeper="Dennis the Peasant", requirement="75%",
          lesson_topic="Strange women lying in ponds", has_light=True, language="English")),
    ("holy-grail / unlit / gated / objects, no keeper voice / EN",
     dict(pack="The Caverns of Camelot", dlvl=5, chapter_title="The Forest",
          keeper="Ni", requirement="75%", lesson_topic="We are the Knights Who Say Ni!",
          room_objects="a shrubbery, a felled tree blocking the path",
          has_light=False, language="English")),
    ("holy-grail / lit / gated / pet / NL",
     dict(pack="De grotten van Camelot", dlvl=6, chapter_title="Caerbannog",
          keeper="Tim de Tovenaar", requirement="75%",
          lesson_topic="Er zijn er die me… Tim noemen",
          carrying="een zwaard, een schild", pet="konijn genaamd Caerbannog",
          has_light=True, language="Dutch")),
    ("friends-nap-partners / lit / gated / objects / EN",
     dict(pack="The One Beneath the Apartment", dlvl=1, chapter_title="The Maid of Honor",
          keeper="Monica Geller", requirement="75%",
          lesson_topic="I can't decide, so you decide, then I decide everything",
          room_objects="a wedding dress on a hook, a clipboard of seating charts",
          has_light=True, language="English")),
    ("friends-nap-partners / unlit / gated / bare floor / NL",
     dict(pack="Die ene onder het appartement", dlvl=2, chapter_title="De bank en het kamp",
          keeper="Chandler Bing", requirement="75%", lesson_topic="Fa-aa-aw-ow",
          has_light=False, language="Dutch")),
    ("ethics-of-ai / lit / gated / objects+pet / EN",
     dict(pack="The Halls of Judgement", dlvl=3, chapter_title="The Ledger",
          keeper="Agentia", requirement="75%", lesson_topic="Moral agency",
          room_objects="a stack of incident reports, a dormant terminal",
          carrying="a notebook", pet="owl named Praxis",
          has_light=True, language="English")),
    ("ethics-of-ai / unlit / gated / bare floor / NL",
     dict(pack="De zalen van oordeel", dlvl=4, chapter_title="De glazen machine",
          keeper="Glas", requirement="75%", lesson_topic="Waarom transparantie",
          has_light=False, language="Dutch")),
    ("ethics-of-ai / lit / ungated / very deep, objects, no keeper / EN",
     dict(pack="The Halls of Judgement", dlvl=7, chapter_title="The Workshop",
          room_objects="a half-finished charter, scattered draft clauses",
          has_light=True, language="English")),
]

NUDGE_SCENARIOS = [
    ("security-onboarding / nudge / EN",
     dict(pack="The Caverns of Compliance", dlvl=1, chapter_title="The Sorting Office",
          keeper="Ada the Suspicious", language="English")),
    ("holy-grail / nudge / NL",
     dict(pack="De grotten van Camelot", dlvl=3, chapter_title="Het dorp",
          keeper="Bedevere de Wijze", language="Dutch")),
]


def _run(model: str, label: str, kind: str, prompt: str, client: OllamaClient) -> dict:
    t0 = time.monotonic()
    reply = client.chat(prompt, json_mode=False, temperature=backstory._TEMPERATURE)
    wall_s = time.monotonic() - t0
    print(f"  {label}: {wall_s:.2f}s wall, {reply.metrics.total_duration_ms}ms reported",
          file=sys.stderr)
    return {
        "model": model, "kind": kind, "label": label,
        "wall_s": round(wall_s, 2),
        "total_ms": reply.metrics.total_duration_ms,
        "load_ms": reply.metrics.load_duration_ms,
        "prompt_tokens": reply.metrics.prompt_tokens,
        "completion_tokens": reply.metrics.completion_tokens,
        "text": reply.text.strip(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("models", nargs="*", default=DEFAULT_MODELS,
                         help="Ollama model tags to compare (default: %(default)s)")
    parser.add_argument("--out", type=Path, default=None,
                         help="write results as JSON here (default: stdout)")
    parser.add_argument("--host", default="http://localhost:11434")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)

    results = []
    for model in args.models:
        client = OllamaClient(model=model, host=args.host, timeout=args.timeout)
        print(f"\n=== {model} ===", file=sys.stderr)
        for label, kwargs in SCENARIOS:
            prompt = backstory.build_prompt(**kwargs)
            results.append(_run(model, label, "ambient", prompt, client))
        for label, kwargs in NUDGE_SCENARIOS:
            prompt = backstory.build_nudge_prompt(**kwargs)
            results.append(_run(model, label, "nudge", prompt, client))

    payload = json.dumps(results, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(payload)
        print(f"\nDone. Results written to {args.out}", file=sys.stderr)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
