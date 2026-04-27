"""INDEX.md maintenance: append + status update operations."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude-plugin" / "skills" / "using-council" / "scripts"))
from index import append_council, set_status, IndexEntry, read_index


def test_append_creates_file(tmp_path):
    idx = tmp_path / ".council" / "INDEX.md"
    append_council(idx, IndexEntry(slug="2026-04-26-test", date="2026-04-26", status="IN-PROGRESS", brief="Test brief"))
    assert idx.is_file()
    body = idx.read_text()
    assert "2026-04-26-test" in body
    assert "IN-PROGRESS" in body
    assert "Test brief" in body
    assert "# Council Index" in body


def test_append_preserves_existing(tmp_path):
    idx = tmp_path / "INDEX.md"
    append_council(idx, IndexEntry("a", "2026-04-26", "EXECUTED", "first"))
    append_council(idx, IndexEntry("b", "2026-04-27", "IN-PROGRESS", "second"))
    body = idx.read_text()
    assert body.find("a") < body.find("b")


def test_set_status_updates_existing(tmp_path):
    idx = tmp_path / "INDEX.md"
    append_council(idx, IndexEntry("a", "2026-04-26", "IN-PROGRESS", "test"))
    set_status(idx, "a", "EXECUTED")
    entries = read_index(idx)
    assert len(entries) == 1
    assert entries[0].status == "EXECUTED"


def test_set_status_unknown_slug_raises(tmp_path):
    idx = tmp_path / "INDEX.md"
    append_council(idx, IndexEntry("a", "2026-04-26", "IN-PROGRESS", "test"))
    with pytest.raises(KeyError):
        set_status(idx, "ghost", "EXECUTED")


def test_status_validation(tmp_path):
    idx = tmp_path / "INDEX.md"
    with pytest.raises(ValueError, match="status"):
        append_council(idx, IndexEntry("a", "2026-04-26", "BOGUS", "test"))


def test_brief_with_pipe_escaped(tmp_path):
    idx = tmp_path / "INDEX.md"
    append_council(idx, IndexEntry("a", "2026-04-26", "IN-PROGRESS", "with | pipes | here"))
    body = idx.read_text()
    assert r"\|" in body
    entries = read_index(idx)
    assert entries[0].brief == "with | pipes | here"


def test_read_empty_file(tmp_path):
    idx = tmp_path / "missing.md"
    assert read_index(idx) == []
