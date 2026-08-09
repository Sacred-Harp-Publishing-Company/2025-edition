"""Compare local hyphenated lyrics with another system's two-part output."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SEPARATOR = re.compile(r"^[\s\-‐‑‒–—]{6,}$")


def upper_part(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if SEPARATOR.fullmatch(line):
            return lines[:index]
    return lines


def normalize_hyphens(lines: list[str]) -> list[str]:
    return [line.replace("·", "-") for line in lines]


def trim_trailing_blank_lines(lines: list[str]) -> list[str]:
    last_content = len(lines)
    while last_content and not lines[last_content - 1].strip():
        last_content -= 1
    return lines[:last_content]


def compare_file(local_path: Path, other_path: Path) -> list[str]:
    local_lines = trim_trailing_blank_lines(
        normalize_hyphens(local_path.read_text(encoding="utf-8").splitlines())
    )
    other_lines = trim_trailing_blank_lines(normalize_hyphens(upper_part(other_path)))
    differences = []
    for line_number in range(1, max(len(local_lines), len(other_lines)) + 1):
        local_line = (
            local_lines[line_number - 1]
            if line_number <= len(local_lines)
            else "<missing>"
        )
        other_line = (
            other_lines[line_number - 1]
            if line_number <= len(other_lines)
            else "<missing>"
        )
        if local_line != other_line:
            differences.append(
                f"  line {line_number}:\n"
                f"    local: {local_line}\n"
                f"    other: {other_line}"
            )
    return differences


def compare_directories(local_directory: Path, other_directory: Path) -> int:
    local_files = {path.name for path in local_directory.glob("*.txt")}
    other_files = {path.name for path in other_directory.glob("*.txt")}
    exit_code = 0

    for filename in sorted(local_files | other_files):
        local_path = local_directory / filename
        other_path = other_directory / filename
        if not local_path.exists():
            print(f"{filename}: missing from local directory")
            exit_code = 1
            continue
        if not other_path.exists():
            print(f"{filename}: missing from other directory")
            exit_code = 1
            continue
        differences = compare_file(local_path, other_path)
        if differences:
            exit_code = 1
            print(f"{filename}:")
            print("\n".join(differences))
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare local hyphenated lyrics with another system's upper output."
    )
    parser.add_argument("local_directory", type=Path)
    parser.add_argument("other_directory", type=Path)
    args = parser.parse_args()
    return compare_directories(args.local_directory, args.other_directory)


if __name__ == "__main__":
    sys.exit(main())
