"""Slug generation: {date}-{kebab-headline}, deterministic and sortable."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude-plugin" / "skills" / "using-council" / "scripts"))
from slug import make_slug


def test_basic_slug():
    assert make_slug("Add auth to CLI", date="2026-04-26") == "2026-04-26-add-auth-to-cli"


def test_strips_punctuation():
    assert make_slug("What's the deal with X?!", date="2026-04-26") == "2026-04-26-whats-the-deal-with-x"


def test_collapses_whitespace_and_dashes():
    assert make_slug("foo  --  bar", date="2026-04-26") == "2026-04-26-foo-bar"


def test_lowercases():
    assert make_slug("HELLO WORLD", date="2026-04-26") == "2026-04-26-hello-world"


def test_truncates_long_headlines():
    long = "a" * 200
    result = make_slug(long, date="2026-04-26")
    assert len(result) <= 11 + 60
    assert result.startswith("2026-04-26-")


def test_unicode_stripped():
    assert make_slug("café résumé", date="2026-04-26") == "2026-04-26-cafe-resume"


def test_uses_today_when_date_omitted(monkeypatch):
    import datetime
    class FakeDate(datetime.date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 26)
    monkeypatch.setattr(datetime, "date", FakeDate)
    assert make_slug("hello").startswith("2026-04-26-")


def test_empty_headline_raises():
    with pytest.raises(ValueError):
        make_slug("")
    with pytest.raises(ValueError):
        make_slug("!!!")
