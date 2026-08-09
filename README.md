# Texts and Metadata for the 2025 Edition of The Sacred Harp

[![Tests](https://github.com/Sacred-Harp-Publishing-Company/2025-edition/actions/workflows/test.yml/badge.svg)](https://github.com/Sacred-Harp-Publishing-Company/2025-edition/actions/workflows/test.yml) [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/) [![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-3776AB.svg)](https://www.python.org/) [![Ruff](https://img.shields.io/badge/linted%20with-Ruff-D7FF64.svg)](https://docs.astral.sh/ruff/)

This repository contains texts and metadata for the 2025 edition of The Sacred Harp.

This is organized in the following way:

- `lyrics` contains lyrics for the 2025 edition, with one file per song
- `hyphenated-lyrics` is generated output and mirrors the files in `lyrics`
- `metadata` contains metadata for the 2025 edition

Other directories are:

- `data/hyphenation` contains the standard and exception TSV data used to hyphenate lyrics
- `src/hyphenation` contains the hyphenation package and command-line interface
- `tests` contains unit tests and integrity checks for the repository data

## Development (Currently, for hyphenation)

Run the test suite with:

```sh
python -m pytest
```

Hyphenated lyrics are checked and generated from the repository root with:

```sh
PYTHONPATH=src python -m hyphenation check
PYTHONPATH=src python -m hyphenation check --fix-syllables
PYTHONPATH=src python -m hyphenation generate
PYTHONPATH=src python -m hyphenation generate --allow-missing --log-file hyphenation.log
PYTHONPATH=src python -m hyphenation generate --allow-missing --song 27.2
PYTHONPATH=src python -m hyphenation generate --allow-missing --song 27.1 --song 27.2
```

The `check` command validates lyric coverage, entry integrity, and syllable counts. The `generate` command applies song- and occurrence-specific exceptions before standard hyphenation and writes files to `hyphenated-lyrics`. By default, generation processes every lyric file and stops when a word is missing. Use `--song SONG` one or more times to generate only selected files; the `.txt` suffix is optional. Use `--allow-missing` to preserve missing words unchanged and log warnings; `--log-file PATH` also writes the generation log to a file. Use `--root PATH` to run either command against another repository root.

When `check` finds an incorrect syllable count, it reports the computed count. Use `check --fix-syllables` to apply those corrections automatically.

## Copyright information

This collection of lyrics from _The Sacred Harp_ © 2025 by [Sacred Harp Publishing Company](https://sacredharp.com/) is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

Other data and code © 2026 by [Sacred Harp Publishing Company](https://sacredharp.com/) is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).
