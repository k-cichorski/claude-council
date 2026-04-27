"""All council agent files must declare valid frontmatter and tool policy."""
from pathlib import Path

AGENTS = Path(__file__).parent.parent / ".claude-plugin" / "agents"
EXPECTED = {"council-architect", "council-skeptic", "council-user-advocate"}
ALLOWED_TOOLS = {"Read", "Grep", "Glob", "Bash", "Write"}
FORBIDDEN_TOOLS = {"Edit", "Task", "NotebookEdit"}


def _parse_frontmatter(text: str) -> dict:
    assert text.startswith("---\n"), "missing frontmatter open"
    end = text.find("\n---\n", 4)
    assert end > 0, "missing frontmatter close"
    fm = text[4:end]
    out: dict = {}
    for line in fm.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def test_all_core_agents_present():
    found = {p.stem for p in AGENTS.glob("*.md")}
    assert EXPECTED <= found, f"missing core agents: {EXPECTED - found}"


def test_each_agent_frontmatter():
    for stem in EXPECTED:
        body = (AGENTS / f"{stem}.md").read_text()
        fm = _parse_frontmatter(body)
        assert fm.get("name") == stem
        assert fm.get("description"), f"{stem}: missing description"
        tools_str = fm.get("tools", "")
        tools = {t.strip() for t in tools_str.split(",") if t.strip()}
        assert tools, f"{stem}: missing tools"
        assert tools <= ALLOWED_TOOLS, f"{stem}: tools include disallowed: {tools - ALLOWED_TOOLS}"
        assert not (tools & FORBIDDEN_TOOLS), f"{stem}: tools include forbidden: {tools & FORBIDDEN_TOOLS}"
        assert "Edit" not in body or "Read-only" in body or "may NOT" in body, \
            f"{stem}: mentions Edit but doesn't disclaim it"
