import csv
from pathlib import Path
from typing import Iterable

from .models import HyphenationEntry

REQUIRED_COLUMNS = {"word", "hyphenated", "song", "occurrence", "syllables", "context"}


def count_syllables(hyphenated: str) -> int:
    return hyphenated.count("·") + 1


def parse_entry(row: dict[str, str], line_number: int = 0) -> HyphenationEntry:
    missing = REQUIRED_COLUMNS - row.keys()
    if missing:
        raise ValueError(f"Missing columns at line {line_number}: {sorted(missing)}")
    try:
        syllables = None if row["syllables"] == "*" else int(row["syllables"])
    except ValueError as error:
        raise ValueError(f"Invalid syllable count at line {line_number}") from error
    return HyphenationEntry(
        word=row["word"],
        hyphenated=row["hyphenated"],
        song=row["song"],
        occurrence=row["occurrence"],
        syllables=syllables,
        context=row["context"] or "",
    )


def load_entries(path: str | Path) -> list[HyphenationEntry]:
    with Path(path).open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        return [parse_entry(row, reader.line_num) for row in reader]


def validate_entry(entry: HyphenationEntry, valid_songs: Iterable[str] = ()) -> None:
    valid_songs = set(valid_songs)
    if not entry.word or not entry.hyphenated:
        raise ValueError("word and hyphenated must not be empty")
    if entry.syllables is None:
        raise ValueError(f"Missing syllable count for {entry.word!r}")
    if entry.syllables != count_syllables(entry.hyphenated):
        raise ValueError(f"Incorrect syllable count for {entry.word!r}")
    if entry.song != "*" and entry.song not in valid_songs:
        raise ValueError(f"Unknown song {entry.song!r} for {entry.word!r}")
    if entry.occurrence != "*":
        try:
            occurrence = int(entry.occurrence)
        except ValueError as error:
            raise ValueError(f"Invalid occurrence for {entry.word!r}") from error
        if occurrence < 1:
            raise ValueError(f"Occurrence must be positive for {entry.word!r}")
    if entry.song == "*" and entry.occurrence != "*":
        raise ValueError(f"Global entry cannot have an occurrence for {entry.word!r}")
