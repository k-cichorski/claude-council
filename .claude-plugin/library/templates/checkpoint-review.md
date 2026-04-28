You are reviewing an implementation phase against the council's VERDICT.

# What Was Agreed

{{verdict_relevant_sections}}

# What Was Implemented

**Diff summary:**
{{diff_summary}}

**Test output:**
{{test_output}}

**Deviation log (if any):**
{{deviation_log_or_none}}

# Your Task

Produce a verdict at: `{{artifact_path}}`

Format (strict — sections must be present, in this order):

## Compliance
{Does the implementation match the design? Cite specific decisions from
VERDICT.md by number. Be concrete: "Decision #4 said X, code does Y."}

## Concerns
{Skeptic's lens (always include this section, even for non-skeptic members):
what could break, what was skipped, what regressed?}

## Verdict

One of: **APPROVE** | **REQUEST_CHANGES** | **ESCALATE**

Followed by a one-paragraph reason.

# Constraints

- **Aim for ≤300 words total.** Soft target — the leader does not truncate your verdict. Stay close to the budget; only stretch up to ~600 words when a specific concern genuinely needs the room.
- **Project files are read-only.** Codebase exploration via Read/Grep/Glob/Bash (read-only); `WebSearch`/`WebFetch` are permitted when an external source materially affects the verdict.
- **Write only to** `{{artifact_path}}`.
- **Do not spawn subagents.**
