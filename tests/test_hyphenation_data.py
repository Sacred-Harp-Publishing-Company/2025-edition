from pathlib import Path

import pytest

from hyphenation.data import count_syllables, load_entries, parse_entry, validate_entry
from hyphenation.lookup import MissingHyphenationError, resolve_hyphenation
from hyphenation.models import HyphenationEntry

ROOT = Path(__file__).parents[1]


def test_count_syllables_uses_discretionary_boundaries():
    assert count_syllables("nev·er-fail·ing") == 3
    assert count_syllables("blessed") == 1


def test_parse_entry_reads_optional_context_as_empty():
    entry = parse_entry(
        {
            "word": "Jesus",
            "hyphenated": "Je·sus",
            "song": "*",
            "occurrence": "*",
            "syllables": "2",
            "context": "",
        }
    )
    assert entry == HyphenationEntry("Jesus", "Je·sus", syllables=2)


def test_validate_entry_rejects_bad_syllables():
    entry = HyphenationEntry("word", "wo·rd", syllables=3)
    with pytest.raises(ValueError, match="Incorrect syllable"):
        validate_entry(entry)


def test_load_real_exception_data():
    entries = load_entries(ROOT / "data/hyphenation/master_exceptions.tsv")
    assert len(entries) >= 800
    assert any(entry.word == "Blessed" and entry.song == "508" for entry in entries)


def test_exception_lookup_prefers_exact_song_and_occurrence():
    exceptions = [
        HyphenationEntry("word", "global", "*", "*"),
        HyphenationEntry("word", "song", "10", "*"),
        HyphenationEntry("word", "exact", "10", "2"),
    ]
    assert resolve_hyphenation("word", "10", 2, exceptions, []) == "exact"
    assert resolve_hyphenation("word", "10", 3, exceptions, []) == "song"
    assert resolve_hyphenation("word", "11", 1, exceptions, []) == "global"


def test_global_exceptions_are_case_insensitive_but_specific_are_not():
    exceptions = [
        HyphenationEntry("mortals", "mor·tals"),
        HyphenationEntry("Blessed", "Bless·ed", "508", "1"),
    ]
    assert resolve_hyphenation("Mortals", "473", 1, exceptions, []) == "Mor·tals"
    assert resolve_hyphenation("Blessed", "508", 1, exceptions, []) == "Bless·ed"
    with pytest.raises(MissingHyphenationError):
        resolve_hyphenation("blessed", "508", 1, exceptions, [])


def test_global_exception_preserves_case_after_leading_apostrophe():
    exceptions = [HyphenationEntry("’tis", "’tis")]
    assert resolve_hyphenation("’Tis", "503", 1, exceptions, []) == "’Tis"


def test_global_exception_preserves_lowercase_source_case():
    exceptions = [HyphenationEntry("Chorus", "Chorus")]
    assert resolve_hyphenation("chorus", "46", 1, exceptions, []) == "chorus"


def test_standard_lookup_is_case_insensitive():
    standard = [HyphenationEntry("jesus", "Je·sus")]
    assert resolve_hyphenation("Jesus", "1", 1, [], standard) == "Je·sus"
    assert resolve_hyphenation("JESUS", "1", 1, [], standard) == "JE·SUS"


def test_missing_lookup_is_explicit():
    with pytest.raises(MissingHyphenationError):
        resolve_hyphenation("unknown", "1", 1, [], [])
