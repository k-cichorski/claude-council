"""Validates plugin.json manifest is well-formed and has required keys."""
import json
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parent.parent / ".claude-plugin"
MANIFEST = PLUGIN_ROOT / "plugin.json"


def test_manifest_exists():
    assert MANIFEST.is_file(), f"manifest missing: {MANIFEST}"


def test_manifest_parses_as_json():
    with MANIFEST.open() as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_manifest_required_fields():
    with MANIFEST.open() as f:
        data = json.load(f)
    for key in ("name", "version", "description", "author"):
        assert key in data, f"missing required key: {key}"
    assert data["name"] == "council"
    assert data["version"].count(".") == 2
    # author must be an object per Claude Code marketplace schema
    assert isinstance(data["author"], dict), "author must be object {name: ...}"
    assert "name" in data["author"]


def test_marketplace_manifest():
    mkt = PLUGIN_ROOT / "marketplace.json"
    assert mkt.is_file()
    with mkt.open() as f:
        data = json.load(f)
    assert data["name"] == "council"
    assert isinstance(data["plugins"], list) and len(data["plugins"]) >= 1
    council_plugin = next((p for p in data["plugins"] if p["name"] == "council"), None)
    assert council_plugin is not None
    assert council_plugin["source"] == "./.claude-plugin"


def test_readme_exists():
    readme = PLUGIN_ROOT / "README.md"
    assert readme.is_file()
    body = readme.read_text()
    assert "council" in body.lower()
    assert "install" in body.lower()
