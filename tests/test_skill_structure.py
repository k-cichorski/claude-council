"""SKILL.md must contain a section per phase, plus invariants and resumability."""
from pathlib import Path

SKILL = Path(__file__).parent.parent / ".claude-plugin" / "skills" / "using-council" / "SKILL.md"

REQUIRED_SECTIONS = [
    "## Phase 0 — Intake",
    "## Phase 1 — Research",
    "## Phase 2 — Synthesis",
    "## Phase 3 — Critique",
    "## Phase 4 — Final Design",
    "## Phase 4b — Sign-off",
    "## Phase 5 — Plan Handoff",
    "## Phase 6 — Execution with Checkpoints",
    "## Resumability",
    "## Invariants",
]


def test_skill_exists():
    assert SKILL.is_file()


def test_skill_has_frontmatter():
    text = SKILL.read_text()
    assert text.startswith("---\n")
    assert "\n---\n" in text


def test_skill_has_all_phase_sections():
    body = SKILL.read_text()
    missing = [s for s in REQUIRED_SECTIONS if s not in body]
    assert not missing, f"SKILL.md missing sections: {missing}"


def test_skill_references_existing_skills():
    body = SKILL.read_text()
    assert "superpowers:writing-plans" in body
    assert "superpowers:executing-plans" in body


def test_skill_references_helpers():
    body = SKILL.read_text()
    assert "scripts/slug.py" in body
    assert "scripts/state.py" in body
    assert "scripts/index.py" in body
