# Scripts

These utilities are run from the repository root with the project Python environment.

## Format hyphenated lyrics

Create the two-part lyric format for the complete corpus:

```sh
python scripts/format_hyphenated.py hyphenated-lyrics lyrics formatted-lyrics
```

The arguments are, in order:

1. The directory containing generated lyrics with middle-dot hyphenation.
2. The directory containing the original lyrics.
3. The output directory to create.

Each output file contains the generated hyphenated lyrics above a `------` separator and the original lyrics below it. Middle dots are converted to regular hyphens only in the upper section. The output directory is created automatically.

To format one file:

```sh
python scripts/format_hyphenated.py \
  hyphenated-lyrics/26.txt \
  lyrics/26.txt \
  formatted-lyrics/26.txt
```

The output file and its parent directories are created automatically.

## Compare hyphenated lyrics

Compare local generated lyrics with another system's two-part output:

```sh
python scripts/compare_hyphenated.py \
  hyphenated-lyrics \
  /path/to/other/hyphenated-lyrics
```

The comparison:

- Examines matching `.txt` files.
- Uses only the section above the dash separator in the other system's files.
- Treats middle dots and regular hyphens as equivalent.
- Ignores trailing blank lines.
- Reports missing files and differing line numbers.

It exits with status `1` when files differ or are missing, and status `0` when they match.
