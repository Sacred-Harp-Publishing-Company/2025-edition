import logging
from collections.abc import Callable, Iterable
from pathlib import Path

from .checks import lyric_files
from .lookup import MissingHyphenationError
from .lyrics import is_annotation, replace_words, tokenize_line

Resolver = Callable[[str, str, int], str]
logger = logging.getLogger(__name__)


def hyphenate_word(
    word: str,
    song: str,
    occurrences: dict[str, int],
    resolver: Resolver,
    allow_missing: bool,
    log: logging.Logger,
) -> str:
    parts = []
    for part in word.split("-"):
        occurrence = occurrences.get(part, 0) + 1
        occurrences[part] = occurrence
        try:
            replacement = resolver(part, song, occurrence)
        except MissingHyphenationError:
            if not allow_missing:
                raise
            log.warning(
                "Missing hyphenation: song=%s occurrence=%s word=%r; passing through",
                song,
                occurrence,
                part,
            )
            replacement = part
        parts.append(replacement)
    return "-".join(parts)


def hyphenate_lines(
    lines: Iterable[str],
    song: str,
    resolver: Resolver,
    allow_missing: bool = False,
    log: logging.Logger | None = None,
) -> list[str]:
    log = log or logger
    lines = list(lines)
    replacements = {}
    occurrences: dict[str, int] = {}
    for line_number, line in enumerate(lines):
        if line_number == 0 or is_annotation(line):
            continue
        words, _ = tokenize_line(line)
        for word in words:
            replacement = hyphenate_word(
                word.text, song, occurrences, resolver, allow_missing, log
            )
            replacements[(line_number, word.occurrence)] = replacement
    return replace_words(lines, replacements)


def hyphenate_file(
    source: Path,
    destination: Path,
    resolver: Resolver,
    allow_missing: bool = False,
    log: logging.Logger | None = None,
) -> None:
    (log or logger).info("Generating %s", destination)
    lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "".join(hyphenate_lines(lines, source.stem, resolver, allow_missing, log)),
        encoding="utf-8",
    )


def hyphenate_directory(
    source: Path,
    destination: Path,
    resolver: Resolver,
    allow_missing: bool = False,
    log: logging.Logger | None = None,
    songs: Iterable[str] | None = None,
) -> None:
    selected = None if songs is None else {song.removesuffix(".txt") for song in songs}
    for lyric_file in lyric_files(source):
        if selected is not None and lyric_file.stem not in selected:
            continue
        hyphenate_file(
            lyric_file,
            destination / lyric_file.name,
            resolver,
            allow_missing,
            log,
        )
