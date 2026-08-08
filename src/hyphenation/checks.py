from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import shlex

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

    def has_entry(word: str, song: str, occurrence: int) -> bool:
        return (
            any(
                exception_word_matches(word, entry)
                and entry.song in ("*", song)
                and entry.occurrence in ("*", str(occurrence))
                for entry in exceptions
            )
            or word.casefold() in standard_words
        )

    missing = []
    for lyric_file in lyric_files(lyrics_directory):
        lines = lyric_file.read_text(encoding="utf-8").splitlines(keepends=True)
        occurrences: dict[str, int] = {}
        for word in iter_lyric_words(lines):
            parts = word.text.split("-")
            parts_have_entries = True
            for part in parts:
                occurrence = occurrences.get(part, 0) + 1
                occurrences[part] = occurrence
                if not has_entry(part, lyric_file.stem, occurrence):
                    parts_have_entries = False
            if not parts_have_entries:
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


def syllable_fix_expression(entry: HyphenationEntry) -> tuple[int, str]:
    correct_count = count_syllables(entry.hyphenated)
    fields = (entry.word, entry.hyphenated, entry.song, entry.occurrence)
    tab = "\t"
    pattern = "^" + tab.join(re.escape(field) for field in fields)
    pattern += tab + "[^" + tab + "]*"
    replacement = tab.join(fields + (str(correct_count),))
    return correct_count, f"s/{pattern}/{replacement}/"


def syllable_fix_command(entry: HyphenationEntry, data_path: Path) -> tuple[int, str]:
    correct_count, expression = syllable_fix_expression(entry)
    command = f"sed -i '' -E {shlex.quote(expression)} {shlex.quote(str(data_path))}"
    return correct_count, command


def apply_syllable_fix(entry: HyphenationEntry, data_path: Path) -> None:
    correct_count = count_syllables(entry.hyphenated)
    lines = data_path.read_text(encoding="utf-8").splitlines(keepends=True)
    expected_fields = [entry.word, entry.hyphenated, entry.song, entry.occurrence]
    updated_lines = []
    matches = 0
    for line in lines:
        line_body = line.rstrip("\r\n")
        line_ending = line[len(line_body) :]
        fields = line_body.split("\t")
        if fields[:4] == expected_fields and len(fields) >= 5:
            fields[4] = str(correct_count)
            matches += 1
            line_body = "\t".join(fields)
        updated_lines.append(line_body + line_ending)
    if matches != 1:
        raise ValueError(
            f"Expected one TSV row for {entry.word!r}, found {matches} in {data_path}"
        )
    data_path.write_text("".join(updated_lines), encoding="utf-8")


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
