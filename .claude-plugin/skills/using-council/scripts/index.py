"""INDEX.md maintenance: a per-project audit table of councils."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

VALID_STATUSES = {"IN-PROGRESS", "DESIGN-ONLY", "EXECUTED", "ABANDONED", "SCOPE-TOO-LARGE"}

_HEADER = "# Council Index\n\n| Slug | Date | Status | Brief |\n|---|---|---|---|\n"


@dataclass
class IndexEntry:
    slug: str
    date: str
    status: str
    brief: str

    def __post_init__(self):
        if self.status not in VALID_STATUSES:
            raise ValueError(f"invalid status: {self.status!r}; valid: {sorted(VALID_STATUSES)}")


def _escape_cell(s: str) -> str:
    return s.replace("|", r"\|")


def _unescape_cell(s: str) -> str:
    return s.replace(r"\|", "|")


def _entry_to_row(e: IndexEntry) -> str:
    return f"| {e.slug} | {e.date} | {e.status} | {_escape_cell(e.brief)} |\n"


def append_council(index_path: Path, entry: IndexEntry) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if not index_path.is_file():
        index_path.write_text(_HEADER)
    with index_path.open("a") as f:
        f.write(_entry_to_row(entry))


def read_index(index_path: Path) -> list[IndexEntry]:
    if not index_path.is_file():
        return []
    text = index_path.read_text()
    entries: list[IndexEntry] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if "Slug" in line or "---" in line:
            continue
        if not line.endswith("|") or len(line) < 2:
            continue
        cells = re.split(r"(?<!\\)\|", line[1:-1])
        cells = [c.strip() for c in cells]
        if len(cells) != 4:
            continue
        slug, date, status, brief = cells
        entries.append(IndexEntry(slug=slug, date=date, status=status, brief=_unescape_cell(brief)))
    return entries


def set_status(index_path: Path, slug: str, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {new_status!r}")
    entries = read_index(index_path)
    for i, e in enumerate(entries):
        if e.slug == slug:
            entries[i] = IndexEntry(slug=e.slug, date=e.date, status=new_status, brief=e.brief)
            _rewrite(index_path, entries)
            return
    raise KeyError(f"slug not in index: {slug!r}")


def _rewrite(index_path: Path, entries: list[IndexEntry]) -> None:
    text = _HEADER
    for e in entries:
        text += _entry_to_row(e)
    index_path.write_text(text)
