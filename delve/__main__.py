"""Entry point: `python -m delve`.

Kept thin on purpose. It parses arguments and hands off to a package below; anything that isn't
argument handling belongs there, not here.

- `delve` (or `delve play`) opens the curses frontend. `--seed` makes a run reproducible
  tile-for-tile (PLAN.md section 7), which is what makes a bug reportable.
- `delve validate <pack>` walks a Markdown pack and prints every author-facing issue as
  `file:line: level: message` (AUTHORING.md section 12). It imports no curses, so it runs in CI
  and on a headless box.
"""

import argparse
import os
import random
import sys

from delve import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="delve", description="Descend a dungeon; learn a topic.")
    parser.add_argument("--version", action="version", version=f"delve {__version__}")
    # Root-level play flags, so `delve --seed 42` keeps working with no subcommand.
    _play_args(parser)
    sub = parser.add_subparsers(dest="command")

    _play_args(sub.add_parser("play", help="play a run (the default)"))
    check = sub.add_parser("validate", help="check a Markdown pack and report author-facing issues")
    check.add_argument("pack", help="path to a pack directory (the one holding en/ and nl/)")

    doctor = sub.add_parser("doctor", help="report the free-text grader's health (Phase 2)")
    doctor.add_argument("--fix", action="store_true", help="also fix what can be fixed safely "
                        "(the same as 'delve setup')")
    _grader_args(doctor)
    setup = sub.add_parser("setup", help="prepare the local free-text grader (pull the model, "
                           "warm it up)")
    _grader_args(setup)

    args = parser.parse_args(argv)
    if args.command == "validate":
        return _validate(args.pack)
    if args.command == "setup":
        return _setup(args)
    if args.command == "doctor":
        return _setup(args) if args.fix else _doctor(args)
    return _play(args)


def _grader_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--grader-model", default=None,
                   help="local model to prepare/check; defaults to the recommended small model")
    p.add_argument("--grader-host", default=None,
                   help="base URL of the local model service; defaults to Ollama on localhost")


def _doctor(args) -> int:
    from delve.assess.llm import DEFAULT_HOST, DEFAULT_MODEL
    from delve.doctor import run_doctor
    return run_doctor(args.grader_model or DEFAULT_MODEL, args.grader_host or DEFAULT_HOST)


def _setup(args) -> int:
    from delve.assess.llm import DEFAULT_HOST, DEFAULT_MODEL
    from delve.doctor import run_setup
    return run_setup(args.grader_model or DEFAULT_MODEL, args.grader_host or DEFAULT_HOST)


def _play_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--seed", type=int, default=None, help="layout seed; omit for a random floor")
    p.add_argument("--name", default=None,
                   help="the learner's name; omit to be asked 'Who are you?' at the start "
                        "($DELVE_NAME pre-fills that prompt)")
    p.add_argument("--pack", default=None,
                   help="path to a pack directory (the folder holding en/ and nl/); "
                        "defaults to the bundled security-onboarding pilot")
    p.add_argument("--lang", default=None,
                   help="locale to play in (en or nl); omit to follow the system locale, "
                        "falling back to en")
    p.add_argument("--pet", default=None, choices=["cat", "dog", "none"],
                   help="the companion that comes with you; omit to be asked at the start")
    p.add_argument("--pet-name", default=None,
                   help="the companion's name; omit to be asked (or to take a species default). "
                        "$DELVE_CAT_NAME/$DELVE_DOG_NAME pre-fill that prompt")
    p.add_argument("--grader-model", default=None,
                   help="local model to grade free-text answers (e.g. qwen2.5:3b); omit to use "
                        "the recommended default model. Reachable Ollama is required to play "
                        "(Phase 2); run 'delve doctor' to check")
    p.add_argument("--grader-host", default=None,
                   help="base URL of the local model service; defaults to Ollama on localhost")


def _env_default(key: str) -> str | None:
    """A per-user startup default read from the environment, mirroring the locale detection in
    delve.strings: read the env at the edge, never a process-global. A blank var counts as unset."""
    return (os.environ.get(key) or "").strip() or None


def _play(args) -> int:
    # Game seed only (dungeon regen); not a crypto source. noqa: S311
    seed = args.seed if args.seed is not None else random.randrange(2**31)  # noqa: S311
    # One locale drives both the pack content and the engine strings: --lang, else the system
    # locale, else English (PLAN.md section 8). Resolved here so a bad --lang can't reach curses.
    from delve import strings as strings_pkg
    lang = strings_pkg.normalise(args.lang)
    engine_strings = strings_pkg.load(lang)
    # The pack (and the tutorial floor) are loaded here, at the top level, so a malformed or
    # missing pack prints a clean message and never reaches curses; it also keeps PackError out
    # of ui/ (PLAN section 4, rule 2).
    from delve.content.errors import PackError
    from delve.session import launch
    try:
        pack = (launch.load_pilot(lang) if args.pack is None
                else launch.load_pack_dir(args.pack, lang))
        tutorial = launch.load_tutorial(lang)
    except PackError as e:
        print(f"delve: cannot load pack: {e}", file=sys.stderr)
        return 1
    # The LLM grader is required to play (DELVE-0033): resolve the model/host, then check it's
    # reachable here at the edge (network I/O belongs at the edge, not in ui) before curses ever
    # starts. Not ready -> print the same diagnosis 'delve doctor' would and stop; no silent
    # keyword-floor session.
    from delve.assess.llm import DEFAULT_HOST, DEFAULT_MODEL
    from delve.doctor import ensure_ready
    model = args.grader_model or DEFAULT_MODEL
    host = args.grader_host or DEFAULT_HOST
    if not ensure_ready(model, host, out=lambda line: print(line, file=sys.stderr)):
        return 1
    # Built here at the edge so the assess.llm socket seam is only touched from the CLI entry
    # point; the runner rides into the UI opaquely, like the pack (rule 2).
    from delve.session.grading import make_grader_runner
    grader_runner = make_grader_runner(model, host)
    # Imported here, not at module top, so --version/--help and `validate` work without a terminal
    # and without importing curses (which windows-curses only provides on Windows).
    from delve.ui.app import main as ui_main
    # Per-user startup defaults from the environment: $DELVE_NAME pre-fills "Who are you?", and
    # $DELVE_CAT_NAME/$DELVE_DOG_NAME pre-fill the companion's name once its species is chosen. Each
    # pre-fills the prompt as an editable value (still asked); an explicit --name/--pet-name flag
    # skips the prompt and so takes precedence over its env default.
    name_default = _env_default("DELVE_NAME")
    pet_name_defaults = {"cat": _env_default("DELVE_CAT_NAME"),
                         "dog": _env_default("DELVE_DOG_NAME")}
    return ui_main(seed=seed, name=args.name, pack=pack, strings=engine_strings, tutorial=tutorial,
                   pet_species=args.pet, pet_name=args.pet_name, grader_runner=grader_runner,
                   name_default=name_default, pet_name_defaults=pet_name_defaults)


def _validate(pack: str) -> int:
    from delve.content.schema import validate_pack
    issues = validate_pack(pack)
    for issue in sorted(issues, key=lambda i: (i.path, i.line or 0, i.level)):
        print(issue)
    errors = sum(1 for i in issues if i.is_error)
    warnings = len(issues) - errors
    print(f"{pack}: ok" if not issues else f"{pack}: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
