from pathlib import Path

from scripts.compare_hyphenated import compare_file, upper_part


def test_upper_part_stops_at_separator(tmp_path: Path):
    path = tmp_path / "1.txt"
    path.write_text("# TITLE\nwo-rd\n------\nword\n", encoding="utf-8")

    assert upper_part(path) == ["# TITLE", "wo-rd"]


def test_compare_file_ignores_middle_dot_vs_hyphen(tmp_path: Path):
    local = tmp_path / "local.txt"
    other = tmp_path / "other.txt"
    local.write_text("# TITLE\nnev·er-fail·ing\n", encoding="utf-8")
    other.write_text(
        "# TITLE\nnev-er-fail-ing\n------\nnever-failing\n", encoding="utf-8"
    )

    assert compare_file(local, other) == []


def test_compare_file_ignores_trailing_blank_lines(tmp_path: Path):
    local = tmp_path / "local.txt"
    other = tmp_path / "other.txt"
    local.write_text("# TITLE\nword\n", encoding="utf-8")
    other.write_text("# TITLE\nword\n\n------\nword\n", encoding="utf-8")

    assert compare_file(local, other) == []


def test_compare_file_reports_line_differences(tmp_path: Path):
    local = tmp_path / "local.txt"
    other = tmp_path / "other.txt"
    local.write_text("# TITLE\ncorrect\n", encoding="utf-8")
    other.write_text("# TITLE\nwrong\n------\ncorrect\n", encoding="utf-8")

    differences = compare_file(local, other)
    assert differences == ["  line 2:\n    local: correct\n    other: wrong"]
