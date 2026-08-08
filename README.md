# Texts and Metadata for the 2025 Edition of The Sacred Harp

This repository contains texts and metadata for the 2025 edition of The Sacred Harp.

This is organized in the following way:

- `lyrics` contains lyrics for the 2025 edition, with one file per song.
- `metadata` contains metadata for the 2025 edition.
- `data/hyphenation` contains the standard and exception TSV data used to hyphenate lyrics.
- `src/hyphenation` contains the hyphenation package and command-line interface.
- `tests` contains unit tests and integrity checks for the repository data.
- `hyphenated-lyrics` is generated output and mirrors the files in `lyrics`.

Run the test suite with:

```sh
python -m pytest
```

Hyphenated lyrics are checked and generated from the repository root with:

```sh
PYTHONPATH=src python -m hyphenation check
PYTHONPATH=src python -m hyphenation generate
PYTHONPATH=src python -m hyphenation generate --allow-missing --log-file hyphenation.log
PYTHONPATH=src python -m hyphenation generate --allow-missing --song 27.2
PYTHONPATH=src python -m hyphenation generate --allow-missing --song 27.1 --song 27.2
```

The `check` command validates lyric coverage, entry integrity, and syllable counts. The `generate` command applies song- and occurrence-specific exceptions before standard hyphenation and writes files to `hyphenated-lyrics`. By default, generation processes every lyric file and stops when a word is missing. Use `--song SONG` one or more times to generate only selected files; the `.txt` suffix is optional. Use `--allow-missing` to preserve missing words unchanged and log warnings; `--log-file PATH` also writes the generation log to a file. Use `--root PATH` to run either command against another repository root.

To compare generated files with another system's two-part output, run:

```sh
python scripts/compare_hyphenated.py hyphenated-lyrics /path/to/other/hyphenated-lyrics
```

The comparison uses only the part above the dash separator, treats middle dots and hyphens as equivalent, and reports differing files and line numbers. It exits with status 1 when differences are found.

This collection of lyrics from _The Sacred Harp_ © 2025 by [Sacred Harp Publishing Company](https://sacredharp.com/) is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).
