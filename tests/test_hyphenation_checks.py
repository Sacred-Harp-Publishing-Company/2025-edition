from pathlib import Path

from hyphenation.checks import (
    invalid_syllable_entries,
    lyric_files,
    missing_lyric_entries,
    output_mismatches,
    unused_entries,
)
from hyphenation.models import HyphenationEntry


def test_missing_entries_reports_song_word_and_occurrence(tmp_path: Path):
    lyric_file = tmp_path / "1.txt"
    lyric_file.write_text("# Title\nKnown unknown known\n", encoding="utf-8")
    missing = missing_lyric_entries(
        tmp_path,
        [],
        [HyphenationEntry("known", "known")],
    )
    assert missing == [("1", "unknown", 1)]


def test_lyric_files_are_sorted_numerically(tmp_path: Path):
    for name in ("100.txt", "26.txt", "27.2.txt", "27.1.txt"):
        (tmp_path / name).write_text("# Title\n", encoding="utf-8")

    assert [path.name for path in lyric_files(tmp_path)] == [
        "26.txt",
        "27.1.txt",
        "27.2.txt",
        "100.txt",
    ]


def test_invalid_syllables_includes_wildcards():
    entries = [HyphenationEntry("word", "wo·rd", syllables=None)]
    assert invalid_syllable_entries(entries) == entries


def test_unused_entries_respects_song_and_occurrence(tmp_path: Path):
    (tmp_path / "1.txt").write_text("# Title\nword word\n", encoding="utf-8")
    used = HyphenationEntry("word", "word", "1", "2")
    unused = HyphenationEntry("other", "other", "1", "*")
    assert unused_entries([used, unused], tmp_path) == [unused]


def test_output_mismatches_ignores_discretionary_middle_dots(tmp_path: Path):
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    output.mkdir()
    (source / "1.txt").write_text("# Title\nwo-rd\n", encoding="utf-8")
    (output / "1.txt").write_text("# Title\nwo·-rd\n", encoding="utf-8")
    assert output_mismatches(source, output) == []


def test_output_mismatches_can_limit_files(tmp_path: Path):
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    output.mkdir()
    for name in ("1.txt", "2.txt"):
        (source / name).write_text("# Title\nword\n", encoding="utf-8")
    (output / "1.txt").write_text("# Title\nword\n", encoding="utf-8")

    assert output_mismatches(source, output, ["1"]) == []
