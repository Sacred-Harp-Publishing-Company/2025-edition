import argparse
import logging
import sys
from pathlib import Path

from .checks import (
    apply_syllable_fix,
    invalid_entries,
    invalid_syllable_entries,
    missing_lyric_entries,
    output_mismatches,
)
from .data import count_syllables, load_entries
from .generate import hyphenate_directory, hyphenate_file, hyphenate_lines
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
            correct_count = count_syllables(entry.hyphenated)
            failures.append(
                f"incorrect syllable count: {entry.word!r}; "
                f"correct count is {correct_count}"
            )
    for failure in failures:
        print(failure)
    return int(bool(failures))


def run_hyphenate(
    files: list[Path],
    root: Path,
    output_dir: Path | None = None,
    in_place: bool = False,
    allow_missing: bool = False,
) -> int:
    """Hyphenate one or more arbitrary text files."""
    exceptions = load_entries(root / "data/hyphenation/master_exceptions.tsv")
    standard = load_entries(root / "data/hyphenation/standard_hyphenation.tsv")
    resolver = build_resolver(exceptions, standard)

    for input_file in files:
        input_file = input_file.resolve()

        if not input_file.exists():
            logger.error(f"File not found: {input_file}")
            return 1

        # Determine output file
        if in_place:
            output_file = input_file
        elif output_dir:
            output_file = output_dir / input_file.name
        else:
            # Print to stdout
            output_file = None

        try:
            if output_file:
                logger.info(f"Processing {input_file} -> {output_file}")
                hyphenate_file(
                    input_file,
                    output_file,
                    resolver,
                    allow_missing=allow_missing,
                    log=logger,
                )
            else:
                # Read and hyphenate, print to stdout
                lines = input_file.read_text(encoding="utf-8").splitlines(keepends=True)
                hyphenated = hyphenate_lines(
                    lines,
                    input_file.stem,
                    resolver,
                    allow_missing=allow_missing,
                    log=logger,
                )
                sys.stdout.write("".join(hyphenated))

        except Exception as e:
            logger.error(f"Error processing {input_file}: {e}")
            if not allow_missing:
                return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and validate hyphenated lyrics."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_root_and_logging(p):
        p.add_argument(
            "--root", type=Path, default=Path("."), help="Repository root directory."
        )
        p.add_argument(
            "--log-file", type=Path, help="Also write log messages to this file."
        )

    # Check command
    check_parser = subparsers.add_parser("check", help="Validate hyphenation data.")
    add_root_and_logging(check_parser)
    check_parser.add_argument(
        "--fix-syllables",
        action="store_true",
        help="Apply incorrect syllable-count fixes while running check.",
    )

    # Generate command
    gen_parser = subparsers.add_parser(
        "generate", help="Generate hyphenated lyrics for all songs in lyrics/."
    )
    add_root_and_logging(gen_parser)
    gen_parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Pass through missing words and log warnings during generation.",
    )
    gen_parser.add_argument(
        "--song",
        action="append",
        help="Generate only this song number; repeat for multiple songs.",
    )

    # Hyphenate command
    hyph_parser = subparsers.add_parser(
        "hyphenate", help="Hyphenate one or more arbitrary text files."
    )
    add_root_and_logging(hyph_parser)
    hyph_parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="One or more text files to hyphenate.",
    )
    hyph_parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for output files (default: write to stdout).",
    )
    hyph_parser.add_argument(
        "--in-place",
        action="store_true",
        help="Modify files in place instead of writing to output directory.",
    )
    hyph_parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Preserve words not found in dictionaries with warnings.",
    )

    args = parser.parse_args()

    # Set up logging
    handlers = [logging.StreamHandler()]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )

    root = args.root
    if args.command == "check":
        return run_check(root, fix_syllables=args.fix_syllables)

    if args.command == "generate":
        exceptions = load_entries(root / "data/hyphenation/master_exceptions.tsv")
        standard = load_entries(root / "data/hyphenation/standard_hyphenation.tsv")
        resolver = build_resolver(exceptions, standard)
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

    if args.command == "hyphenate":
        return run_hyphenate(
            args.files,
            root,
            output_dir=args.output_dir,
            in_place=args.in_place,
            allow_missing=args.allow_missing,
        )

    return 1
