from dataclasses import dataclass


@dataclass(frozen=True)
class HyphenationEntry:
    word: str
    hyphenated: str
    song: str = "*"
    occurrence: str = "*"
    syllables: int | None = 1
    context: str = ""

    @property
    def is_standard(self) -> bool:
        return self.song == "*" and self.occurrence == "*"

    @property
    def occurrence_number(self) -> int | None:
        return None if self.occurrence == "*" else int(self.occurrence)
