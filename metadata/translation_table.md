# Data Dictionary: `metadata/translation_table.tsv`

| Column Name  | Description                                                          |
| ------------ | -------------------------------------------------------------------- |
| Page in 1991 | The page number in the 1991 edition. '-' if not in the 1991 edition. |
| Page in 2025 | The page number in the 2025 edition.                                 |
| Action       | What "happened" to the song. See below for values                    |

## Action Values

| Value           | Description                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------------- |
| `keep`          | The song is in both the 1991 and 2025 editions, with the same page number.                           |
| `replace`       | The song on the page in the 1991 edition is replaced by the song(s) on the page in the 2025 edition. |
| `replace-inner` | Subsequent songs replacing the song on this page in the 1991 edition.                                |
| `renumber`      | The song in the 1991 edition has been kept, but has been moved or renumbered.                        |
| `insert`        | A new song was inserted at this page location because of new space available.                        |
| `new`           | A new page was added to the 2025 edition.                                                            |
| `remove`        | The page was removed (as a song) in the 2025 edition.                                                |

For example, AFRICA occupies half a page in the 2025 edition, but an entire page in the 1991 edition. A new song, GAINES is on the bottom half. So AFRICA is listed as a `renumber` from 178 to 178t, and GAINES is listed as an `insert` at 178b.

For example, the removal of ROSE OF SHARON (254 in the 1991 edition) provided space for six songs, which are listed as `replace` or `replace-inner`.

For example, FAREWELL ANTHEM starts on page 260 in both the 1991 and 2025 edition.

Two pages of songs were added to the 2025 Edtion: 574 THOMASTON and 575 LISBON. These are listed as `new` pages.

## Usage

This translation table can be used to ask:

## Questions about the 1991 edition

Is this song from the 1991 edition in the 2025 edition? The answer is `yes` if the Action value is `keep` or `renumber`.

What number in the 2025 edition is this song from the 1991 edition? If the Action column vaue is `keep` or `renumber`, then it is the `Page in 2025` value.

What song or songs replaced this song in the 1991 edition? Look for all values of `replace` or `replace-inner` from looking up the son in the `Page in 1991` column.

Was this song in the 1991 edition left out of the 2025 edition? Yes, if the value is `replace`, `replace-inner`, or `remove`.

## Questions about the 2025 edition

Is this song in the 2025 edition also in the 1991 edition? The answer is `yes` if the Action value is `keep` or `renumber`.

What number in the 2025 edition is this song from the 1991 edition? If the Action column vaue is `keep` or `renumber`, then it is the `Page in 1991` value.

Is this a new song in the 2025 edition? Yes, if the Action value is `new`, `replace`, `replace-inner`, or `insert`

What song (or partial song) in the 1991 edition did this song replace? Look for the `Page in 1991` value, if the Action is `replace` or `replace-inner`. (Note that if the replaced song appears multiple times in the `Page in 1991` column, it partially replaced the song in the 1991 edition).
