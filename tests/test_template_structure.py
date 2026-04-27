"""Templates must contain required placeholders and section markers."""
from pathlib import Path

TPL_DIR = Path(__file__).parent.parent / ".claude-plugin" / "library" / "templates"

REQUIRED = {
    "brief.md": ["{{slug}}", "## Problem", "## Success Criteria", "## Scope and Non-Goals", "## Constraints", "## Roster", "## Related Prior Verdicts", "## Open Questions Resolved With User"],
    "verdict.md": ["{{slug}}", "## Design", "## Decisions", "## Dissents", "## Success Criteria", "## Out of Scope", "## Risks and Mitigations", "## Implementation Pointer", "## Decomposition Proposal"],
    "research-prompt.md": ["{{display_name}}", "{{brief_full_text}}", "{{persona_full_text}}", "{{artifact_path}}", "## Findings", "## Tensions", "## Initial Recommendation", "## Open Questions"],
    "critique-prompt.md": ["{{display_name}}", "{{brief_full_text}}", "{{persona_full_text}}", "{{draft_design_full_text}}", "{{artifact_path}}", "## Agree", "## Reject", "## Missing"],
    "escalation-prompt.md": ["{{question_one_sentence}}", "{{member_a}}", "{{member_b}}", "{{leader_lean_with_caveat}}"],
    "checkpoint-review.md": ["{{verdict_relevant_sections}}", "{{diff_summary}}", "{{test_output}}", "{{artifact_path}}", "## Compliance", "## Concerns", "## Verdict", "APPROVE", "REQUEST_CHANGES", "ESCALATE"],
}


def test_all_templates_present():
    for name in REQUIRED:
        assert (TPL_DIR / name).is_file(), f"missing template: {name}"


def test_each_template_has_required_tokens():
    for name, tokens in REQUIRED.items():
        body = (TPL_DIR / name).read_text()
        missing = [t for t in tokens if t not in body]
        assert not missing, f"{name} missing tokens: {missing}"
