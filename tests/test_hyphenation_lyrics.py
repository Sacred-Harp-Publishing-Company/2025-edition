
import pytest

from hyphenation.generate import hyphenate_lines
from hyphenation.lookup import MissingHyphenationError
from hyphenation.lyrics import (
    is_annotation,
    iter_lyric_words,
    replace_words,
    tokenize_line,
)


def test_tokenize_line_preserves_internal_apostrophes_and_hyphens():
    words, next_occurrence = tokenize_line("My never-failing treasury, ev’ry day.")
    assert [word.text for word in words] == [
        "My",
        "never-failing",
        "treasury",
        "ev’ry",
        "day",
    ]
    assert next_occurrence == 6


def test_annotations_and_title_are_not_lyric_words():
    lines = ["# TITLE\n", "Jesus sings.\n", "[chorus]\n", "Jesus rests.\n"]
    assert [word.text for word in iter_lyric_words(lines)] == [
        "Jesus",
        "sings",
        "Jesus",
        "rests",
    ]
    assert is_annotation("  [chorus]\n")


def test_replace_words_preserves_punctuation_and_annotations():
    lines = ["# TITLE\n", "Dear name!\n", "[chorus]\n"]
    result = replace_words(lines, {(1, 1): "Dear", (1, 2): "na·me"})
    assert result == ["# TITLE\n", "Dear na·me!\n", "[chorus]\n"]


def test_hyphenate_lines_resolves_each_word_in_order():
    lines = ["# TITLE\n", "My name!\n"]
    result = hyphenate_lines(
        lines, "1", lambda word, song, occurrence: f"{word}:{occurrence}"
    )
    assert result == ["# TITLE\n", "My:1 name:1!\n"]


def test_obligatory_hyphen_parts_are_resolved_independently():
    lines = ["# TITLE\n", "My never-failing-all work.\n"]

    def resolve(word, song, occurrence):
        return {
            "never": "nev·er",
            "failing": "fail·ing",
            "all": "all",
        }.get(word, word)

    result = hyphenate_lines(
        lines,
        "1",
        resolve,
    )
    assert result == ["# TITLE\n", "My nev·er-fail·ing-all work.\n"]


def test_hyphenate_lines_passes_through_missing_words_and_logs(caplog):
    def resolve(word, song, occurrence):
        if word == "missing":
            raise MissingHyphenationError(word)
        return f"{word}:hyphenated"

    with caplog.at_level("WARNING"):
        result = hyphenate_lines(
            ["# TITLE\n", "Known missing.\n"],
            "1",
            resolve,
            allow_missing=True,
        )

    assert result == ["# TITLE\n", "Known:hyphenated missing.\n"]
    assert "song=1 occurrence=1 word='missing'" in caplog.text


def test_hyphenate_lines_is_strict_by_default():
    with pytest.raises(MissingHyphenationError):
        hyphenate_lines(
            ["# TITLE\n", "missing\n"],
            "1",
            lambda word, song, occurrence: (_ for _ in ()).throw(
                MissingHyphenationError(word)
            ),
        )
