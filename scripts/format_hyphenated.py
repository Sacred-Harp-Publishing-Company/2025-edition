#!/usr/bin/env python3
"""Format generated hyphenated lyrics with an unhyphenated lower section."""

from __future__ import annotations

import argparse
from pathlib import Path

SEPARATOR = "------"


def format_file(hyphenated_path: Path, source_path: Path) -> str:
    hyphenated_lines = hyphenated_path.read_text(encoding="utf-8").splitlines()
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    upper_lines = [line.replace("·", "-") for line in hyphenated_lines]
    return "\n".join(upper_lines + ["", SEPARATOR, ""] + source_lines) + "\n"


def format_directory(
    hyphenated_directory: Path, source_directory: Path, output_directory: Path
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    for hyphenated_path in sorted(hyphenated_directory.glob("*.txt")):
        source_path = source_directory / hyphenated_path.name
        if not source_path.exists():
            raise FileNotFoundError(f"Missing source lyric: {source_path}")
        output_path = output_directory / hyphenated_path.name
        output_path.write_text(
            format_file(hyphenated_path, source_path), encoding="utf-8"
        )


def format_single_file(
    hyphenated_path: Path, source_path: Path, output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_file(hyphenated_path, source_path), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Format hyphenated lyrics with an unhyphenated lower section."
    )
    parser.add_argument("hyphenated_path", type=Path)
    parser.add_argument("source_path", type=Path)
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()
    paths_are_directories = args.hyphenated_path.is_dir() and args.source_path.is_dir()
    if paths_are_directories:
        if not args.output_path.exists() and args.output_path.suffix:
            parser.error("directory mode requires an output directory")
        format_directory(args.hyphenated_path, args.source_path, args.output_path)
    else:
        format_single_file(args.hyphenated_path, args.source_path, args.output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
