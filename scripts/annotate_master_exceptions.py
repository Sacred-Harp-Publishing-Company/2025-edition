"""Create a copy of master_exceptions.tsv with an OK/reason status column."""

from __future__ import annotations

import argparse
from pathlib import Path

from hyphenation.checks import lyric_files
from hyphenation.data import load_entries, validate_entry
from hyphenation.lookup import exception_word_matches
from hyphenation.lyrics import iter_lyric_words
from hyphenation.models import HyphenationEntry


def observed_words(lyrics_directory: Path) -> set[tuple[str, str, int]]:
    observed = set()
    for lyric_file in lyric_files(lyrics_directory):
        lines = lyric_file.read_text(encoding="utf-8").splitlines(keepends=True)
        for word in iter_lyric_words(lines):
            observed.add((lyric_file.stem, word.text, word.occurrence))
    return observed


def entry_status(
    entry: HyphenationEntry,
    observed: set[tuple[str, str, int]],
    valid_songs: set[str],
) -> str:
    try:
        validate_entry(entry, valid_songs)
    except ValueError as error:
        return str(error)
    used = any(
        exception_word_matches(word, entry)
        and (entry.song == "*" or song == entry.song)
        and (entry.occurrence == "*" or occurrence == int(entry.occurrence))
        for song, word, occurrence in observed
    )
    return "OK" if used else "unused: no matching word found in lyrics"


def annotate(source: Path, lyrics_directory: Path, destination: Path) -> None:
    entries = load_entries(source)
    valid_songs = {path.stem for path in lyrics_directory.glob("*.txt")}
    observed = observed_words(lyrics_directory)
    statuses = [entry_status(entry, observed, valid_songs) for entry in entries]

    header, *rows = source.read_text(encoding="utf-8").splitlines()
    if len(rows) != len(statuses):
        raise ValueError("Row count does not match parsed entry count")
    output_lines = [f"{header}\tstatus"]
    output_lines.extend(f"{row}\t{status}" for row, status in zip(rows, statuses))
    destination.write_text("\n".join(output_lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--destination",
        type=Path,
        default=None,
        help="Output path (default: master_exceptions_annotated.tsv next to the source).",
    )
    args = parser.parse_args()
    source = args.root / "data/hyphenation/master_exceptions.tsv"
    destination = args.destination or source.with_name(
        "master_exceptions_annotated.tsv"
    )
    annotate(source, args.root / "lyrics", destination)
    print(f"Wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
