#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "reportlab>=4.0",
# ]
# ///
"""Render a beautiful PDF songbook from metadata/topmatter.tsv and lyrics/*.txt.

Usage:
    uv run scripts/make_songbook_pdf.py
    uv run scripts/make_songbook_pdf.py --output songbook.pdf
    uv run scripts/make_songbook_pdf.py --song 27.1 --song 27.2
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

PAGE_WIDTH, PAGE_HEIGHT = 5.5 * inch, 8.5 * inch
MARGIN = 0.7 * inch

INK = "#1a1a1a"
MUTED = "#555555"
RULE = "#8a6d3b"


@dataclass
class Song:
    sort: str
    page: str
    title: str
    meter: str
    scripture: str
    key: str
    text_attribution: str
    tune_attribution: str
    copyright: str
    stanzas: list[
        tuple[str, list[str]]
    ]  # (kind, lines) kind is "verse:<n>" or "label:<text>"


def esc(s: str) -> str:
    return escape(s.strip())


def read_topmatter(tsv_path: Path) -> list[dict[str, str]]:
    with tsv_path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def parse_lyrics(path: Path) -> list[tuple[str, list[str]]]:
    """Split a lyrics file into stanzas, tagging chorus/labeled refrains."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^#.*\n+", "", text, count=1)  # drop the leading "# TITLE" line
    blocks = re.split(r"\n\s*\n", text.strip("\n"))

    stanzas: list[tuple[str, list[str]]] = []
    verse_num = 0
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip() != ""]
        if not lines:
            continue
        m = re.match(r"^\[(.+)\]$", lines[0].strip())
        if m:
            label = " ".join(
                w.capitalize() for w in re.split(r"[\s,]+", m.group(1)) if w
            )
            stanzas.append((f"label:{label}", lines[1:]))
        else:
            verse_num += 1
            stanzas.append((f"verse:{verse_num}", lines))
    return stanzas


class Ornament(Flowable):
    """A small decorative divider: a rule with a diamond at its center."""

    def __init__(self, width=2.2 * inch, height=10):
        super().__init__()
        self.width = width
        self.height = height
        self.hAlign = "CENTER"

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        mid = self.width / 2.0
        gap = 7
        c.line(0, self.height / 2, mid - gap, self.height / 2)
        c.line(mid + gap, self.height / 2, self.width, self.height / 2)
        c.setFillColor(RULE)
        d = 3.2
        p = c.beginPath()
        p.moveTo(mid, self.height / 2 + d)
        p.lineTo(mid + d, self.height / 2)
        p.lineTo(mid, self.height / 2 - d)
        p.lineTo(mid - d, self.height / 2)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.restoreState()


def styles() -> dict[str, ParagraphStyle]:
    return {
        "number": ParagraphStyle(
            "number",
            fontName="Times-Italic",
            fontSize=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "title": ParagraphStyle(
            "title",
            fontName="Times-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=2,
        ),
        "meter": ParagraphStyle(
            "meter",
            fontName="Times-Italic",
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceAfter=6,
        ),
        "scripture": ParagraphStyle(
            "scripture",
            fontName="Times-Italic",
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=INK,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=18,
            rightIndent=18,
        ),
        "attribution": ParagraphStyle(
            "attribution",
            fontName="Times-Roman",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceBefore=2,
            spaceAfter=10,
        ),
        "verse": ParagraphStyle(
            "verse",
            fontName="Times-Roman",
            fontSize=11.5,
            leading=16,
            alignment=TA_LEFT,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=0,
            leftIndent=20,
            firstLineIndent=-20,
        ),
        "chorus": ParagraphStyle(
            "chorus",
            fontName="Times-Italic",
            fontSize=11,
            leading=15,
            alignment=TA_LEFT,
            textColor=INK,
            spaceBefore=6,
            spaceAfter=0,
            leftIndent=38,
        ),
        "chorus_label": ParagraphStyle(
            "chorus_label",
            fontName="Times-BoldItalic",
            fontSize=9.5,
            alignment=TA_LEFT,
            textColor=MUTED,
            leftIndent=38,
            spaceBefore=6,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Times-Roman",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "index_title": ParagraphStyle(
            "index_title",
            fontName="Times-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=4,
        ),
        "index_group": ParagraphStyle(
            "index_group",
            fontName="Times-BoldItalic",
            fontSize=11,
            leading=14,
            textColor=RULE,
            spaceBefore=10,
            spaceAfter=3,
        ),
        "index_entry": ParagraphStyle(
            "index_entry",
            fontName="Times-Roman",
            fontSize=9.5,
            leading=13,
            textColor=INK,
        ),
        "index_page": ParagraphStyle(
            "index_page",
            fontName="Times-Roman",
            fontSize=9.5,
            leading=13,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "book_title": ParagraphStyle(
            "book_title",
            fontName="Times-Bold",
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=6,
        ),
        "book_subtitle": ParagraphStyle(
            "book_subtitle",
            fontName="Times-Italic",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceAfter=6,
        ),
        "colophon": ParagraphStyle(
            "colophon",
            fontName="Times-Roman",
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor=MUTED,
            leftIndent=24,
            rightIndent=24,
        ),
    }


def song_flowables(song: Song, sty: dict[str, ParagraphStyle]) -> list:
    story: list = []
    story.append(Paragraph(f"No. {esc(song.page)}", sty["number"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(esc(song.title), sty["title"]))
    if song.meter:
        story.append(Paragraph(esc(song.meter), sty["meter"]))
    story.append(Ornament())
    if song.scripture:
        story.append(Paragraph(f"\u201c{esc(song.scripture)}\u201d", sty["scripture"]))
    attrib_bits = []
    if song.text_attribution:
        attrib_bits.append(f"Words: {esc(song.text_attribution)}")
    if song.tune_attribution:
        attrib_bits.append(f"Music: {esc(song.tune_attribution)}")
    if attrib_bits:
        story.append(
            Paragraph(
                " &nbsp;&nbsp;\u2022&nbsp;&nbsp; ".join(attrib_bits), sty["attribution"]
            )
        )
    story.append(Spacer(1, 6))

    for kind, lines in song.stanzas:
        text = "<br/>".join(esc(ln) for ln in lines)
        if kind.startswith("verse:"):
            n = kind.split(":", 1)[1]
            story.append(Paragraph(f"<b>{n}.</b>&nbsp;&nbsp;{text}", sty["verse"]))
        else:
            label = kind.split(":", 1)[1]
            story.append(Paragraph(label, sty["chorus_label"]))
            story.append(Paragraph(text, sty["chorus"]))
    return story


def page_sort_key(song: Song) -> float:
    try:
        return float(song.sort)
    except ValueError:
        return 0.0


def entry_table(rows: list[tuple[str, str]], sty: dict[str, ParagraphStyle]) -> Table:
    data = [
        [
            Paragraph(esc(label), sty["index_entry"]),
            Paragraph(esc(page), sty["index_page"]),
        ]
        for label, page in rows
    ]
    t = Table(data, colWidths=[None, 0.55 * inch], hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#dddddd")),
            ]
        )
    )
    return t


ARTICLES = {"THE", "A", "AN"}


def invert_leading_article(text: str) -> str:
    """Move a leading article to the end of the primary clause for indexing:
    "THE DYING CHRISTIAN" -> "DYING CHRISTIAN, THE"
    "The Sacred Harp, 1844. Alto S. M. Denson, 1911." ->
        "Sacred Harp, The, 1844. Alto S. M. Denson, 1911."
    """
    first, sep, rest = text.partition(" ")
    if not sep or first.upper() not in ARTICLES:
        return text
    m = re.search(r"[,.]", rest)
    if m:
        name, tail = rest[: m.start()], rest[m.start() :]
        return f"{name}, {first}{tail}"
    return f"{rest}, {first}"


def flat_index(
    songs: list[Song],
    heading: str,
    extractor,
    sty: dict[str, ParagraphStyle],
) -> list:
    """A simple alphabetical "value — page" index (e.g. Index of Titles)."""
    rows = sorted(
        (
            (invert_leading_article(extractor(s)), s.page, page_sort_key(s))
            for s in songs
            if extractor(s)
        ),
        key=lambda r: (re.sub(r"[^A-Za-z0-9]", "", r[0]).upper(), r[2]),
    )
    if not rows:
        return []
    story: list = [
        PageBreak(),
        Paragraph(heading, sty["index_title"]),
        Ornament(),
        Spacer(1, 6),
    ]
    story.append(entry_table([(label, page) for label, page, _ in rows], sty))
    return story


def grouped_index(
    songs: list[Song],
    heading: str,
    extractor,
    sty: dict[str, ParagraphStyle],
) -> list:
    """A grouped index (e.g. Metrical Index, Index of Authors) keyed by a
    metadata value, with matching titles/pages listed underneath each group.
    """
    groups: dict[str, list[Song]] = {}
    for s in songs:
        value = extractor(s).strip()
        if not value:
            continue
        groups.setdefault(value, []).append(s)
    if not groups:
        return []

    story: list = [
        PageBreak(),
        Paragraph(heading, sty["index_title"]),
        Ornament(),
        Spacer(1, 6),
    ]
    for value in sorted(
        groups,
        key=lambda v: re.sub(r"[^A-Za-z0-9]", "", invert_leading_article(v)).upper(),
    ):
        members = sorted(
            groups[value],
            key=lambda s: (
                re.sub(r"[^A-Za-z0-9]", "", invert_leading_article(s.title)).upper(),
                page_sort_key(s),
            ),
        )
        story.append(Paragraph(esc(invert_leading_article(value)), sty["index_group"]))
        story.append(
            entry_table(
                [(invert_leading_article(s.title), s.page) for s in members], sty
            )
        )
    return story


def build_indexes(songs: list[Song], sty: dict[str, ParagraphStyle]) -> list:
    story: list = []
    story += flat_index(songs, "Index of Titles", lambda s: s.title, sty)
    story += grouped_index(songs, "Metrical Index", lambda s: s.meter, sty)
    story += grouped_index(
        songs, "Index of Scripture Texts", lambda s: s.scripture, sty
    )
    story += grouped_index(songs, "Index of Keys", lambda s: s.key, sty)
    story += grouped_index(
        songs, "Index of Text Authors", lambda s: s.text_attribution, sty
    )
    story += grouped_index(
        songs,
        "Index of Tune Composers and Arrangers",
        lambda s: s.tune_attribution,
        sty,
    )
    story += grouped_index(
        songs, "Index of Copyright Holders", lambda s: s.copyright, sty
    )
    return story


def title_page_flowables(sty: dict[str, ParagraphStyle]) -> list:
    story: list = [
        Spacer(1, 2.2 * inch),
        Paragraph("Lyrics from<br/><i>The Sacred Harp</i>", sty["book_title"]),
        Paragraph("2025 Edition", sty["book_subtitle"]),
        Spacer(1, 0.3 * inch),
        Ornament(width=2.6 * inch),
        PageBreak(),
    ]
    return story


def copyright_page_flowables(sty: dict[str, ParagraphStyle]) -> list:
    story: list = [
        Spacer(1, 3 * inch),
        Paragraph(
            "This edition (typesetting, layout, and indexes) "
            "\u00a9 2026 by Words &amp; Numbers, LLC, is licensed under a "
            "Creative Commons Attribution-NonCommercial 4.0 International "
            "License (CC BY-NC 4.0). To view a copy of this license, visit "
            "https://creativecommons.org/licenses/by-nc/4.0/.",
            sty["colophon"],
        ),
        Spacer(1, 10),
        Paragraph(
            "Lyric texts are reproduced, unmodified, from "
            "<i>The Sacred Harp: 2025 Edition</i>, \u00a9 2025 Sacred Harp "
            "Publishing Company (https://sacredharp.com/), likewise licensed "
            "under a Creative Commons Attribution-NonCommercial 4.0 "
            "International License (CC BY-NC 4.0). To view a copy of this "
            "license, visit https://creativecommons.org/licenses/by-nc/4.0/.",
            sty["colophon"],
        ),
    ]
    return story


def build_songs(
    rows: list[dict[str, str]], lyrics_dir: Path, only: set[str] | None
) -> list[Song]:
    songs = []
    for row in rows:
        sort = row["Sort"].strip()
        if only and sort not in only:
            continue
        path = lyrics_dir / f"{sort}.txt"
        if not path.exists():
            print(
                f"warning: no lyrics file for {sort!r} ({path}); skipping",
                file=sys.stderr,
            )
            continue
        stanzas = parse_lyrics(path)
        songs.append(
            Song(
                sort=sort,
                page=row.get("Page", sort).strip(),
                title=row.get("Title", "").strip(),
                meter=row.get("Text Meter", "").strip(),
                scripture=row.get("Scripture", "").strip(),
                key=row.get("Key", "").strip(),
                text_attribution=row.get("Text Attribution", "").strip(),
                tune_attribution=row.get("Tune Attribution", "").strip(),
                copyright=row.get("Copyright", "").strip(),
                stanzas=stanzas,
            )
        )
    return songs


def make_pdf(songs: list[Song], output: Path) -> None:
    sty = styles()
    front_matter_pages = 2  # title page + copyright page

    def blank_footer(canvas, doc):
        pass

    def numbered_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Times-Italic", 8)
        canvas.setFillColor(MUTED)
        page_num = doc.page - front_matter_pages
        canvas.drawCentredString(PAGE_WIDTH / 2, 0.4 * inch, str(page_num))
        canvas.restoreState()

    def make_frame():
        return Frame(
            MARGIN,
            MARGIN,
            PAGE_WIDTH - 2 * MARGIN,
            PAGE_HEIGHT - 2 * MARGIN,
            id="main",
        )

    doc = BaseDocTemplate(
        str(output),
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        title="The Sacred Harp: 2025 Edition",
        author="Sacred Harp Publishing Company",
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="front", frames=[make_frame()], onPage=blank_footer),
            PageTemplate(id="song", frames=[make_frame()], onPage=numbered_footer),
        ]
    )

    story: list = title_page_flowables(sty)
    story.extend(copyright_page_flowables(sty))
    story.append(NextPageTemplate("song"))
    story.append(PageBreak())
    for i, song in enumerate(songs):
        story.extend(song_flowables(song, sty))
        if i != len(songs) - 1:
            story.append(PageBreak())
    story.extend(build_indexes(songs, sty))
    doc.build(story)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=repo_root, help="repository root")
    parser.add_argument("--tsv", type=Path, default=None, help="path to topmatter.tsv")
    parser.add_argument(
        "--lyrics-dir", type=Path, default=None, help="path to lyrics directory"
    )
    parser.add_argument("--output", type=Path, default=None, help="output PDF path")
    parser.add_argument(
        "--song",
        action="append",
        default=None,
        help="only include this song (by Sort value, e.g. 27.1); may be repeated",
    )
    args = parser.parse_args()

    tsv_path = args.tsv or (args.root / "metadata" / "topmatter.tsv")
    lyrics_dir = args.lyrics_dir or (args.root / "lyrics")
    output = args.output or (args.root / "songbook.pdf")
    only = set(args.song) if args.song else None

    rows = read_topmatter(tsv_path)
    songs = build_songs(rows, lyrics_dir, only)
    if not songs:
        print("error: no songs to render", file=sys.stderr)
        raise SystemExit(1)
    make_pdf(songs, output)
    print(f"wrote {len(songs)} songs to {output}")


if __name__ == "__main__":
    main()
