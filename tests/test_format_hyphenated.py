from pathlib import Path

from scripts.format_hyphenated import format_file, format_single_file


def test_format_file_creates_hyphenated_and_source_sections(tmp_path: Path):
    hyphenated = tmp_path / "26.txt"
    source = tmp_path / "26-source.txt"
    hyphenated.write_text("# TITLE\nMy spir·it looks al·one,\n", encoding="utf-8")
    source.write_text("# TITLE\nMy spirit looks alone,\n", encoding="utf-8")

    assert format_file(hyphenated, source) == (
        "# TITLE\n"
        "My spir-it looks al-one,\n"
        "\n"
        "------\n"
        "\n"
        "# TITLE\n"
        "My spirit looks alone,\n"
    )


def test_format_single_file_writes_output(tmp_path: Path):
    hyphenated = tmp_path / "26.txt"
    source = tmp_path / "26-source.txt"
    output = tmp_path / "formatted" / "26.txt"
    hyphenated.write_text("# TITLE\nspir·it\n", encoding="utf-8")
    source.write_text("# TITLE\nspirit\n", encoding="utf-8")

    format_single_file(hyphenated, source, output)

    assert output.read_text(encoding="utf-8") == (
        "# TITLE\nspir-it\n\n------\n\n# TITLE\nspirit\n"
    )
