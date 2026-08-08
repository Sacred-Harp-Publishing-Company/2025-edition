from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .data import count_syllables, validate_entry
from .lyrics import iter_lyric_words
from .lookup import exception_word_matches
from .models import HyphenationEntry


def lyric_files(directory: Path) -> list[Path]:
    def sort_key(path: Path) -> tuple[Decimal, str]:
        try:
            return Decimal(path.stem), path.name
        except InvalidOperation:
            return Decimal("Infinity"), path.name

    return sorted(directory.glob("*.txt"), key=sort_key)


def missing_lyric_entries(
    lyrics_directory: Path,
    exceptions: Iterable[HyphenationEntry],
    standard: Iterable[HyphenationEntry],
) -> list[tuple[str, str, int]]:
    exceptions = list(exceptions)
    standard_words = {entry.word.casefold() for entry in standard}
    missing = []
    for lyric_file in lyric_files(lyrics_directory):
        lines = lyric_file.read_text(encoding="utf-8").splitlines(keepends=True)
        for word in iter_lyric_words(lines):
            matches = [
                entry
                for entry in exceptions
                if exception_word_matches(word.text, entry)
                and entry.song in ("*", lyric_file.stem)
                and entry.occurrence in ("*", str(word.occurrence))
            ]
            if not matches and word.text.casefold() not in standard_words:
                missing.append((lyric_file.stem, word.text, word.occurrence))
    return missing


def invalid_syllable_entries(
    entries: Iterable[HyphenationEntry],
) -> list[HyphenationEntry]:
    return [
        entry
        for entry in entries
        if entry.syllables is None
        or entry.syllables != count_syllables(entry.hyphenated)
    ]


def invalid_entries(
    entries: Iterable[HyphenationEntry], valid_songs: Iterable[str]
) -> list[tuple[HyphenationEntry, str]]:
    errors = []
    for entry in entries:
        try:
            validate_entry(entry, valid_songs)
        except ValueError as error:
            errors.append((entry, str(error)))
    return errors


def unused_entries(
    entries: Iterable[HyphenationEntry], lyrics_directory: Path
) -> list[HyphenationEntry]:
    entries = list(entries)
    observed: set[tuple[str, str, int]] = set()
    for lyric_file in lyric_files(lyrics_directory):
        lines = lyric_file.read_text(encoding="utf-8").splitlines(keepends=True)
        for word in iter_lyric_words(lines):
            observed.add((lyric_file.stem, word.text, word.occurrence))
    unused = []
    for entry in entries:
        if any(
            word == entry.word
            and (entry.song == "*" or song == entry.song)
            and (entry.occurrence == "*" or occurrence == int(entry.occurrence))
            for song, word, occurrence in observed
        ):
            continue
        unused.append(entry)
    return unused


def output_mismatches(
    source_directory: Path,
    output_directory: Path,
    filenames: Iterable[str] | None = None,
) -> list[str]:
    mismatches = []
    source_files = (
        {path.name for path in lyric_files(source_directory)}
        if filenames is None
        else {filename.removesuffix(".txt") + ".txt" for filename in filenames}
    )
    output_files = (
        {path.name for path in lyric_files(output_directory)}
        if filenames is None
        else {filename.removesuffix(".txt") + ".txt" for filename in filenames}
    )
    for filename in sorted(source_files | output_files):
        source = source_directory / filename
        output = output_directory / filename
        if not source.exists() or not output.exists():
            mismatches.append(filename)
            continue
        original = source.read_text(encoding="utf-8")
        generated = output.read_text(encoding="utf-8").replace("·", "")
        if original != generated:
            mismatches.append(filename)
    return mismatches
