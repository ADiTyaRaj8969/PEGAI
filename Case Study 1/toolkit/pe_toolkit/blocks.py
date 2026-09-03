"""A minimal document model.

The report is emitted as Markdown and as DOCX. Rather than maintain two
templates that slowly diverge, both renderers walk the same list of blocks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import pandas as pd


@dataclass
class Heading:
    level: int
    text: str


@dataclass
class Para:
    text: str


@dataclass
class Bullets:
    items: Sequence[str]


@dataclass
class Table:
    frame: pd.DataFrame
    caption: str = ""
    widths: Sequence[float] | None = None  # relative column widths


@dataclass
class KeyValue:
    pairs: Sequence[tuple[str, str]]
    headers: tuple[str, str] = ("Field", "Details")
    caption: str = ""


@dataclass
class Figure:
    path: Path
    caption: str
    width_in: float = 6.1


@dataclass
class Code:
    text: str
    caption: str = ""


@dataclass
class PageBreak:
    pass


@dataclass
class Callout:
    """A short highlighted note - used for definitions and warnings."""

    title: str
    text: str


Block = (
    Heading | Para | Bullets | Table | KeyValue | Figure | Code | PageBreak | Callout
)


@dataclass
class Doc:
    blocks: list[Block] = field(default_factory=list)

    def add(self, block: Block) -> "Doc":
        self.blocks.append(block)
        return self

    def extend(self, blocks: Sequence[Block]) -> "Doc":
        self.blocks.extend(blocks)
        return self

    # convenience
    def h(self, level: int, text: str) -> "Doc":
        return self.add(Heading(level, text))

    def p(self, text: str) -> "Doc":
        return self.add(Para(text))

    def table(self, frame: pd.DataFrame, caption: str = "", widths=None) -> "Doc":
        return self.add(Table(frame, caption, widths))

    def kv(self, pairs, headers=("Field", "Details"), caption: str = "") -> "Doc":
        return self.add(KeyValue(list(pairs), headers, caption))

    def figure(self, path: Path, caption: str) -> "Doc":
        return self.add(Figure(path, caption))

    def code(self, text: str, caption: str = "") -> "Doc":
        return self.add(Code(text, caption))

    def brk(self) -> "Doc":
        return self.add(PageBreak())


_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)


def split_bold(text: str) -> list[tuple[str, bool]]:
    """Split `**bold**` markup into (run, is_bold) pairs for the DOCX writer."""
    parts: list[tuple[str, bool]] = []
    cursor = 0
    for match in _BOLD.finditer(text):
        if match.start() > cursor:
            parts.append((text[cursor : match.start()], False))
        parts.append((match.group(1), True))
        cursor = match.end()
    if cursor < len(text):
        parts.append((text[cursor:], False))
    return parts or [(text, False)]
