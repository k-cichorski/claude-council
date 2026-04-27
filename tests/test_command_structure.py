"""Command markdown has frontmatter and points to the using-council skill."""
from pathlib import Path

CMD = Path(__file__).parent.parent / ".claude-plugin" / "commands" / "council.md"


def test_command_exists():
    assert CMD.is_file()


def test_command_has_frontmatter():
    text = CMD.read_text()
    assert text.startswith("---\n"), "missing YAML frontmatter"
    end = text.find("\n---\n", 4)
    assert end > 0, "frontmatter not closed"


def test_command_describes_args():
    text = CMD.read_text().lower()
    assert "brief" in text
    assert "--resume" in text


def test_command_invokes_skill():
    text = CMD.read_text()
    assert "using-council" in text
