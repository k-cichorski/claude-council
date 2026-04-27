"""Each specialist file has well-formed frontmatter and required sections."""
from pathlib import Path

LIB = Path(__file__).parent.parent / ".claude-plugin" / "library" / "specialists"

EXPECTED_NAMES = {
    "database-schema", "database-performance", "caching-strategy", "data-migration", "event-sourcing",
    "api-design", "auth-protocol", "error-handling-strategy", "rate-limiting", "idempotency",
    "distributed-systems", "concurrency-control", "message-queue", "consistency-model",
    "ui-architecture", "accessibility", "state-management", "responsive-design",
    "testing-strategy", "security-auditor", "observability", "performance-budget",
    "deployment-strategy", "infrastructure-as-code", "secrets-management", "cost-optimization",
    "migration-strategy", "documentation-strategy", "release-engineering",
}

REQUIRED_SECTIONS = ["# Persona", "# Mandate (Phase 1 — Research)", "# Mandate (Phase 3 — Critique)", "# Constraints"]
REQUIRED_FRONTMATTER_KEYS = {"name", "display_name", "when_to_pick", "strengths", "out_of_scope"}


def _split_frontmatter(text: str) -> tuple[str, str]:
    assert text.startswith("---\n"), "missing frontmatter open"
    end = text.find("\n---\n", 4)
    assert end > 0, "missing frontmatter close"
    return text[4:end], text[end + 5 :]


def test_all_29_specialists_present():
    found = {p.stem for p in LIB.glob("*.md")}
    missing = EXPECTED_NAMES - found
    extra = found - EXPECTED_NAMES
    assert not missing, f"missing: {missing}"
    assert not extra, f"unexpected: {extra}"


def test_each_has_required_frontmatter_keys():
    for name in EXPECTED_NAMES:
        text = (LIB / f"{name}.md").read_text()
        fm, _ = _split_frontmatter(text)
        keys_present = {line.split(":", 1)[0].strip() for line in fm.splitlines() if ":" in line and not line.startswith("  ")}
        missing = REQUIRED_FRONTMATTER_KEYS - keys_present
        assert not missing, f"{name}: missing frontmatter keys {missing}"


def test_each_name_field_matches_filename():
    for name in EXPECTED_NAMES:
        text = (LIB / f"{name}.md").read_text()
        fm, _ = _split_frontmatter(text)
        for line in fm.splitlines():
            if line.startswith("name:"):
                assert line.split(":", 1)[1].strip() == name, f"{name}: name field mismatch"
                break
        else:
            raise AssertionError(f"{name}: no name field")


def test_each_has_required_sections():
    for name in EXPECTED_NAMES:
        body = (LIB / f"{name}.md").read_text()
        missing = [s for s in REQUIRED_SECTIONS if s not in body]
        assert not missing, f"{name}: missing sections {missing}"
