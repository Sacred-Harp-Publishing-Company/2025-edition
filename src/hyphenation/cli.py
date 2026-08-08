import argparse
import logging
from pathlib import Path

from .checks import (
    invalid_entries,
    invalid_syllable_entries,
    missing_lyric_entries,
    output_mismatches,
    apply_syllable_fix,
    syllable_fix_command,
)
from .data import load_entries
from .generate import hyphenate_directory
from .lookup import resolve_hyphenation

logger = logging.getLogger(__name__)


def build_resolver(exceptions, standard):
    return lambda word, song, occurrence: resolve_hyphenation(
        word, song, occurrence, exceptions, standard
    )


def run_check(root: Path, fix_syllables: bool = False) -> int:
    exceptions = load_entries(root / "data/hyphenation/master_exceptions.tsv")
    standard = load_entries(root / "data/hyphenation/standard_hyphenation.tsv")
    songs = {path.stem for path in (root / "lyrics").glob("*.txt")}
    failures = []
    failures.extend(
        f"missing: {item}"
        for item in missing_lyric_entries(root / "lyrics", exceptions, standard)
    )
    failures.extend(
        f"invalid entry: {item}"
        for item in invalid_entries(exceptions + standard, songs)
    )
    for entries, path in (
        (
            exceptions,
            root / "data/hyphenation/master_exceptions.tsv",
        ),
        (
            standard,
            root / "data/hyphenation/standard_hyphenation.tsv",
        ),
    ):
        for entry in invalid_syllable_entries(entries):
            if fix_syllables:
                apply_syllable_fix(entry, path)
                continue
            correct_count, command = syllable_fix_command(entry, path)
            failures.append(
                f"incorrect syllable count: {entry.word!r}; "
                f"correct count is {correct_count}; fix with: {command}"
            )
    for failure in failures:
        print(failure)
    return int(bool(failures))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and validate hyphenated lyrics."
    )
    parser.add_argument("command", choices=("check", "generate"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Pass through missing words and log warnings during generation.",
    )
    parser.add_argument(
        "--log-file", type=Path, help="Also write log messages to this file."
    )
    parser.add_argument(
        "--song",
        action="append",
        help="Generate only this song number; repeat for multiple songs.",
    )
    parser.add_argument(
        "--fix-syllables",
        action="store_true",
        help="Apply incorrect syllable-count fixes while running check.",
    )
    args = parser.parse_args()
    handlers = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )
    root = args.root
    exceptions = load_entries(root / "data/hyphenation/master_exceptions.tsv")
    standard = load_entries(root / "data/hyphenation/standard_hyphenation.tsv")
    resolver = build_resolver(exceptions, standard)
    if args.command == "check":
        return run_check(root, fix_syllables=args.fix_syllables)
    hyphenate_directory(
        root / "lyrics",
        root / "hyphenated-lyrics",
        resolver,
        allow_missing=args.allow_missing,
        log=logger,
        songs=args.song,
    )
    mismatches = output_mismatches(
        root / "lyrics", root / "hyphenated-lyrics", args.song
    )
    for filename in mismatches:
        print(f"output mismatch: {filename}")
    return int(bool(mismatches))
