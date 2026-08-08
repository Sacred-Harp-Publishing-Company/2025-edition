from collections.abc import Iterable

from .models import HyphenationEntry


class MissingHyphenationError(KeyError):
    pass


def exception_word_matches(word: str, entry: HyphenationEntry) -> bool:
    specific_occurrence = entry.song != "*" and entry.occurrence != "*"
    if specific_occurrence:
        return entry.word == word
    return entry.word.casefold() == word.casefold()


def _preserve_case(word: str, hyphenated: str) -> str:
    if word.isupper():
        return hyphenated.upper()
    if word.islower():
        return hyphenated.lower()
    first_cased = next((character for character in word if character.isalpha()), "")
    if first_cased.isupper():
        for index, character in enumerate(hyphenated):
            if character.isalpha():
                return hyphenated[:index] + character.upper() + hyphenated[index + 1 :]
    return hyphenated


def _specificity(
    entry: HyphenationEntry, song: str, occurrence: int
) -> tuple[int, int]:
    song_match = int(entry.song == song)
    occurrence_match = int(entry.occurrence == str(occurrence))
    return song_match, occurrence_match


def resolve_hyphenation(
    word: str,
    song: str,
    occurrence: int,
    exceptions: Iterable[HyphenationEntry],
    standard: Iterable[HyphenationEntry],
) -> str:
    matching_exceptions = [
        entry
        for entry in exceptions
        if exception_word_matches(word, entry)
        and entry.song in ("*", song)
        and entry.occurrence in ("*", str(occurrence))
    ]
    if matching_exceptions:
        ranked = sorted(
            matching_exceptions,
            key=lambda entry: _specificity(entry, song, occurrence),
            reverse=True,
        )
        best = _specificity(ranked[0], song, occurrence)
        if len(ranked) > 1 and _specificity(ranked[1], song, occurrence) == best:
            raise ValueError(f"Ambiguous exceptions for {word!r} in song {song}")
        entry = ranked[0]
        return (
            entry.hyphenated
            if entry.song != "*" and entry.occurrence != "*"
            else _preserve_case(word, entry.hyphenated)
        )

    normalized_word = word.casefold()
    for entry in standard:
        if entry.word.casefold() == normalized_word:
            return _preserve_case(word, entry.hyphenated)
    raise MissingHyphenationError(f"No hyphenation entry for {word!r} in song {song}")
