"""STATE.json round-trip + schema validation + resumability semantics."""
import json
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude-plugin" / "skills" / "using-council" / "scripts"))
from state import CouncilState, MemberRecord, load_state, write_state, MissingStateError


def test_member_record_round_trip(tmp_path):
    m = MemberRecord(role="architect", type="core", artifact="research/architect.md", done=False)
    assert m.to_dict()["role"] == "architect"
    assert MemberRecord.from_dict(m.to_dict()) == m


def test_state_round_trip(tmp_path):
    s = CouncilState(
        slug="2026-04-26-test",
        phase="phase-1-research",
        members=[
            MemberRecord("architect", "core", "research/architect.md", True),
            MemberRecord("auth-protocol", "library:auth-protocol", "research/auth-protocol.md", False),
        ],
        draft_design_written=False,
        verdict_committed=False,
        phase_4b_triggered=False,
        started_at="2026-04-26T14:00:00Z",
        last_updated_at="2026-04-26T14:30:00Z",
    )
    state_path = tmp_path / "STATE.json"
    write_state(state_path, s)
    loaded = load_state(state_path)
    assert loaded == s


def test_load_state_missing_raises(tmp_path):
    with pytest.raises(MissingStateError):
        load_state(tmp_path / "STATE.json")


def test_state_json_is_human_readable(tmp_path):
    s = CouncilState(
        slug="t", phase="phase-0-intake", members=[],
        draft_design_written=False, verdict_committed=False, phase_4b_triggered=False,
        started_at="2026-04-26T14:00:00Z", last_updated_at="2026-04-26T14:00:00Z",
    )
    p = tmp_path / "STATE.json"
    write_state(p, s)
    text = p.read_text()
    assert text.count("\n") >= 5


def test_invalid_phase_rejected(tmp_path):
    bad = {
        "slug": "x", "phase": "phase-99-bogus", "members": [],
        "draft_design_written": False, "verdict_committed": False, "phase_4b_triggered": False,
        "started_at": "2026-04-26T14:00:00Z", "last_updated_at": "2026-04-26T14:00:00Z",
    }
    p = tmp_path / "STATE.json"
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="phase"):
        load_state(p)


def test_member_type_validation():
    with pytest.raises(ValueError, match="type"):
        MemberRecord("x", "garbage-type", "research/x.md", False)
    MemberRecord("x", "core", "research/x.md", False)
    MemberRecord("x", "library:auth-protocol", "research/x.md", False)
    MemberRecord("x", "invented", "research/x.md", False)


def test_mark_member_done(tmp_path):
    s = CouncilState(
        slug="t", phase="phase-1-research",
        members=[MemberRecord("architect", "core", "research/architect.md", False)],
        draft_design_written=False, verdict_committed=False, phase_4b_triggered=False,
        started_at="2026-04-26T14:00:00Z", last_updated_at="2026-04-26T14:00:00Z",
    )
    s.mark_done("architect")
    assert s.members[0].done is True


def test_mark_unknown_role_raises(tmp_path):
    s = CouncilState(
        slug="t", phase="phase-1-research", members=[],
        draft_design_written=False, verdict_committed=False, phase_4b_triggered=False,
        started_at="2026-04-26T14:00:00Z", last_updated_at="2026-04-26T14:00:00Z",
    )
    with pytest.raises(KeyError):
        s.mark_done("ghost")


def test_research_over_budget_round_trip(tmp_path):
    """Phase 1 over-budget warnings must persist across resume."""
    s = CouncilState(
        slug="t", phase="phase-2-synthesis",
        members=[MemberRecord("architect", "core", "research/architect.md", True)],
        draft_design_written=False, verdict_committed=False, phase_4b_triggered=False,
        started_at="2026-04-26T14:00:00Z", last_updated_at="2026-04-26T14:00:00Z",
    )
    s.research_over_budget.append("architect")
    s.research_over_budget.append("auth-protocol")
    s.critique_over_budget.append("skeptic")
    p = tmp_path / "STATE.json"
    write_state(p, s)
    loaded = load_state(p)
    assert loaded.research_over_budget == ["architect", "auth-protocol"]
    assert loaded.critique_over_budget == ["skeptic"]


def test_over_budget_defaults_empty(tmp_path):
    """Older STATE.json files (pre-over-budget fields) must still load."""
    legacy = {
        "slug": "t", "phase": "phase-1-research", "members": [],
        "draft_design_written": False, "verdict_committed": False, "phase_4b_triggered": False,
        "started_at": "2026-04-26T14:00:00Z", "last_updated_at": "2026-04-26T14:00:00Z",
    }
    p = tmp_path / "STATE.json"
    p.write_text(json.dumps(legacy))
    loaded = load_state(p)
    assert loaded.research_over_budget == []
    assert loaded.critique_over_budget == []


def test_legacy_research_truncated_field_is_read(tmp_path):
    """STATE.json written by an older council version uses `research_truncated`."""
    legacy = {
        "slug": "t", "phase": "phase-2-synthesis", "members": [],
        "draft_design_written": False, "verdict_committed": False, "phase_4b_triggered": False,
        "started_at": "2026-04-26T14:00:00Z", "last_updated_at": "2026-04-26T14:00:00Z",
        "research_truncated": ["architect", "skeptic"],
    }
    p = tmp_path / "STATE.json"
    p.write_text(json.dumps(legacy))
    loaded = load_state(p)
    assert loaded.research_over_budget == ["architect", "skeptic"]


def test_phase_4b_signoff_phase_valid():
    """Phase 4b must be a writable state.phase value (issue #2 in final review)."""
    s = CouncilState(
        slug="t", phase="phase-4b-signoff", members=[],
        draft_design_written=True, verdict_committed=False, phase_4b_triggered=True,
        started_at="2026-04-26T14:00:00Z", last_updated_at="2026-04-26T14:00:00Z",
    )
    assert s.phase == "phase-4b-signoff"
