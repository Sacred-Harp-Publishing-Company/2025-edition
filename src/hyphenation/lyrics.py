import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

WORD_PATTERN = re.compile(
    r"[’']?[^\W\d_]+(?:[’'][^\W\d_]+)*(?:-[^\W\d_]+(?:[’'][^\W\d_]+)*)*",
    re.UNICODE,
)


@dataclass(frozen=True)
class LyricWord:
    text: str
    occurrence: int
    start: int
    end: int


def is_annotation(line: str) -> bool:
    return line.strip().startswith("[") and line.strip().endswith("]")


def tokenize_line(line: str, occurrence_start: int = 1) -> tuple[list[LyricWord], int]:
    words = []
    occurrence = occurrence_start
    for match in WORD_PATTERN.finditer(line):
        words.append(LyricWord(match.group(), occurrence, match.start(), match.end()))
        occurrence += 1
    return words, occurrence


def iter_lyric_words(lines: Iterable[str]) -> Iterator[LyricWord]:
    occurrences: dict[str, int] = {}
    for line_number, line in enumerate(lines):
        if line_number == 0 or is_annotation(line):
            continue
        words, _ = tokenize_line(line)
        for word in words:
            occurrence = occurrences.get(word.text, 0) + 1
            occurrences[word.text] = occurrence
            yield LyricWord(word.text, occurrence, word.start, word.end)


def replace_words(
    lines: Iterable[str], replacements: dict[tuple[int, int], str]
) -> list[str]:
    output = []
    for line_number, line in enumerate(lines):
        if line_number == 0 or is_annotation(line):
            output.append(line)
            continue
        words, _ = tokenize_line(line)
        pieces = []
        cursor = 0
        for word in words:
            pieces.append(line[cursor : word.start])
            pieces.append(replacements.get((line_number, word.occurrence), word.text))
            cursor = word.end
        pieces.append(line[cursor:])
        output.append("".join(pieces))
    return output
