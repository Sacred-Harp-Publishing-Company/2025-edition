from pathlib import Path

from hyphenation.checks import (
    apply_syllable_fix,
    invalid_syllable_entries,
    lyric_files,
    missing_lyric_entries,
    output_mismatches,
    syllable_fix_command,
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


def test_missing_entries_checks_obligatory_hyphen_parts(tmp_path: Path):
    lyric_file = tmp_path / "1.txt"
    lyric_file.write_text("# Title\nnever-failing\n", encoding="utf-8")
    missing = missing_lyric_entries(
        tmp_path,
        [],
        [
            HyphenationEntry("never", "nev·er"),
            HyphenationEntry("failing", "fail·ing"),
        ],
    )
    assert missing == []


def test_missing_entries_counts_part_occurrences_independently(tmp_path: Path):
    lyric_file = tmp_path / "1.txt"
    lyric_file.write_text("# Title\nnever-failing never-failing\n", encoding="utf-8")
    missing = missing_lyric_entries(
        tmp_path,
        [],
        [
            HyphenationEntry("never", "nev·er"),
            HyphenationEntry("failing", "fail·ing"),
        ],
    )
    assert missing == []


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


def test_syllable_fix_command_reports_correct_count_and_sed_command(tmp_path: Path):
    entry = HyphenationEntry("word", "wo·rd", "1", "2", syllables=3)
    count, command = syllable_fix_command(entry, tmp_path / "exceptions.tsv")

    assert count == 2
    assert "sed -i '' -E" in command
    assert "wo·rd" in command
    assert "\t2" in command


def test_apply_syllable_fix_updates_tsv_row(tmp_path: Path):
    path = tmp_path / "exceptions.tsv"
    path.write_text(
        "word\thyphenated\tsong\toccurrence\tsyllables\tcontext\n"
        "word\two·rd\t1\t2\t3\t*\n",
        encoding="utf-8",
    )
    apply_syllable_fix(HyphenationEntry("word", "wo·rd", "1", "2", 3), path)

    assert "\t2\t*" in path.read_text(encoding="utf-8")


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
