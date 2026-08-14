# Hyphenation

## General description of the problem

Hyphenation of _The Sacred Harp: 2025 Edition_ is slightly different than what is required for standard book publishing. In particular, we need to actually define the syllables of a word, not just meet the requirements of justification algorithms. When musically typeset, most hyphens are optional; it's useful for a singer to see the syllable boundaries, but sometimes the constraints of typesetting force the typesetter to remove these discretionary hyphens. Some hyphens are obligatory, however, being part of the word form. The editors decided to adopt the hyphenation decisions of _The American Heritage Dictionary_ (AHD) as part of their style guide. Practically, this was because the programmer assigned the task of hyphenation had API access to AHD's hyphenation decisions. Of course, some words present in the 2025 edition's lyric texts were missing from AHD, so we needed to make additional editorial decisions.

Some examples may be helpful:

Consider the third verse to ORTONVILLE (68b):

> Dear name! the rock on which I build,
> My shield and hiding place,
> My never-failing treasury filled
> With boundless stores of grace.

The hyphenated text version of this is:

> Dear name! the rock on which I build,  
> My shield and hid-ing place,  
> My nev-er-fail-ing trea-sury filled  
> With bound-less stores of grace.

The text as it appears in the first printing of the 2025 edition is:

> Dear name! the rock on which I build,  
> My shield and hid-ing place,  
> My nev-er-fail-ing treasury filled  
> With boundless stores of grace.

The first thing to notice is that the typesetters chose to leave some hyphenation out (in _treasury_ and _boundless_). The second is that _never-failing_ has one obligatory hyphen, and two discretionary hyphens. Thirdly, not as obvious is that the hyphenation of _treasury_ is non-standard. In AHD, the hyphenation is given as `treas·ur·y`, and we use this hyphenation in BENEFICENCE (486) (_His house a seat of wealth shall be, An un-ex-haust-ed treas-ur-y_). So, we need some way to express exceptions to the standard hyphenation. Fourthly, and perhaps somewhat surprisingly, there is no AHD entry for _Jesus_, which, of course, appears in first verse, and many other songs. So, we need to add this to our data. In fact, AHD is missing many proper names, plurals, and other derived forms.

Sometimes the same word form needs to be hyphenated differently within the same lyric. _Blessed_ is particularly thorny, since we decided to spell this as `blessed` when used as a verb or when it's used as a two-syllable adjective, but `blest` when used as a single-syllable adjective. (_Hail the blest morn_, but _The meek he blessed with righteousness_ and _Blessed are the pure in heart_). Note that the later two both appear in SERMON ON THE MOUNT (508).

## Data

We wanted to hyphenate texts semi-automatically, meaning that we would process texts using an algorithm drawing on a data set with hyphenation entries for each word in the lyrics of the 2025 edition, accounting for all of the various tricky bits.

In order to achieve this, we have created two data files in the `data/hyphenation` directory:

- `standard_hyphenation.tsv`: contains standard AHD for words found in the lyrics
- `master_exceptions.tsv`: contains all exceptions to standard use.

Note that the Unicode codepoint U+00B7 (MIDDLE DOT) is used to indicate the discretionary hyphen: for example, _Bar·ti·meus_. Obligatory hyphens use standard Unicode codepoint U+002D (HYPHEN-MINUS).

The format of these files is the same. They are tab-separated files with a header. The columns are:

- `word`: the word as found in the lyrics. For standard entries, these are not case-sensitive. For exceptions, these are case-sensitive.
- `hyphenated`: the hyphenated form to use.
- `song`: the song it occurs in or `*` to indicate all songs.
- `occurrence`: the occurrence in the lyric, starting from 1, or `*` to indicate all occurrences.
- `syllables`: the number of syllables this represents, which should just be the number of discretionary hyphens + 1. A simple data check.
- `context`: contextual notes about this entry.

The standard hyphenation file uses only the first two entries, effectively.

## The master algorithm

Basically, the algorithm looks at each word in the lyrics (knowing which file it is in and which occurrence of the word in that file: the first, second, etc.). It checks the master exceptions file, and if it matches one of its entries, it replaces the word with its given hyphenation. Otherwise, it checks the standard hyphenation file and does the same. If the word is not in either file, that's a problem, and an error is signaled.

Of course, the algorithm doesn't hyphenate titles (the first line in a lyric file), or annotations like `[chorus]` which describe the lyrics, but are not part of them.

For example, the hyphenated verse from our example from before should look like this:

> Dear name! the rock on which I build,  
> My shield and hid·ing place,  
> My nev·er-fail·ing trea·sury filled  
> With bound·less stores of grace.

## Data checks

There are several data integrity checks:

1. Checks that every word in the lyrics has at least one matching entry in the hyphenation data.
2. Checks that every entry in the hyphenation data matches at least one lyric word. This is useful to remove "cruft" from the data.
3. Checks that every entry in the hyphenation data has a correct syllable count.
4. Checks that every entry has all the fields aside from the optional `context`; that all song entries are either `*` or a proper song number, which occurs in the `metadata/topmatter.tsv` `sort` column; that every occurrence is either `*` or an integer; that no integer occurrence appears if the song is given as `*`.
5. Checks that every lyric file has a matching hyphenated lyric file, and that (once the discretionary hyphens are removed) the files are the same.

## Rule checks

To make this system more maintainable, exactly one rule should apply to every word found in the lyrics files. That is, at most one entry in the exceptions file should apply, and, failing its presence there, exactly one in the standard hyphenation file.
