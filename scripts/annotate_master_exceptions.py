"""Create a copy of master_exceptions.tsv with an OK/reason status column."""

from __future__ import annotations

import argparse
from pathlib import Path

from hyphenation.data import load_entries, validate_entry
from hyphenation.checks import unused_entries
from hyphenation.models import HyphenationEntry


def entry_status(
    entry: HyphenationEntry,
    unused: set[HyphenationEntry],
    valid_songs: set[str],
) -> str:
    try:
        validate_entry(entry, valid_songs)
    except ValueError as error:
        return str(error)
    return "unused: no matching word found in lyrics" if entry in unused else "OK"


def annotate(source: Path, lyrics_directory: Path, destination: Path) -> None:
    entries = load_entries(source)
    valid_songs = {path.stem for path in lyrics_directory.glob("*.txt")}
    unused = set(unused_entries(entries, lyrics_directory))
    statuses = [entry_status(entry, unused, valid_songs) for entry in entries]

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
