# Council Plugin

Multi-perspective deliberation for Claude Code. Wrap any non-trivial design or
implementation task in a leader-orchestrated council of parallel-subagent
members — research, critique, consensus, then drive implementation through
`superpowers:writing-plans` + `executing-plans` with per-phase checkpoints.

> **Status:** v0.1.

## What it does

You hand the council a brief — anything from a single feature decision to a whole project. The council:

1. **Intake** — leader explores the codebase, asks clarifying questions until it has full context, picks 2–4 task-specific specialists from a curated library of 29 personas (or invents one), scans prior verdicts.
2. **Research** — three core members (Architect, Skeptic, User Advocate) plus the picked specialists each produce independent research in parallel.
3. **Synthesis** — leader writes a draft design with explicit agreement and disagreement maps.
4. **Critique** — every member critiques the draft in parallel.
5. **Final design** — leader writes `VERDICT.md`. Material disagreements are escalated to you; small ones become named dissents.
6. **Execution** — leader drives implementation via `superpowers:writing-plans` + `executing-plans`. After each implementation phase, the Skeptic plus one relevant specialist review the diff. Before merge, the full council reconvenes for a final review.

All artifacts persist under `.council/<slug>/` and are auto-committed at two points: when `VERDICT.md` is finalized, and when `final-review.md` is written.

## Install

### Option 1 — global plugin (recommended)

```bash
cp -r plugins/council ~/.claude/plugins/council
```

Restart Claude Code (or run `/plugins reload`). The `/council` slash command and the `council-architect` / `council-skeptic` / `council-user-advocate` agent types should appear.

### Option 2 — per-project plugin

Keep the `plugins/council/` directory in the repo (where it already is). Add to your project's `.claude/settings.json`:

```json
{
  "plugins": ["plugins/council"]
}
```

### Option 3 — separate repo (for distribution)

Move `plugins/council/` into its own git repo, then install via your preferred plugin manager.

## Usage

```
/council <brief>            # start a new deliberation
/council                    # interactive: leader prompts for brief
/council --resume <slug>    # resume an interrupted council
/council --list             # show .council/INDEX.md
```

### Worked example

```
/council add OAuth login to the web app
```

The leader will:
- explore your repo (auth module if any, user store, sessions)
- ask you about: OAuth provider choice, identity merging policy, session storage, success criteria
- pick specialists like `auth-protocol`, `secrets-management`, maybe `database-schema` if user identity changes
- run the council through phases 1–4 → produce `VERDICT.md`
- ask whether to proceed to plan + execution, then drive the implementation with checkpoints

## Repository layout

```
plugins/council/
  plugin.json
  README.md                        # this file
  commands/council.md              # /council slash command
  skills/using-council/
    SKILL.md                       # the leader's orchestration logic
    scripts/{slug,state,index}.py  # deterministic helpers
  agents/
    council-architect.md           # 3 fixed-core member personas
    council-skeptic.md
    council-user-advocate.md
  library/
    specialists/                   # 29 curated dynamic-specialist personas
    templates/                     # 6 prompt/output templates
  tests/                           # pytest suite for helpers + structural validators
```

## .gitignore guidance

The audit trail is the value — **commit `.council/`** unless you have a specific reason not to. If you do want to ignore it:

```
.council/
```

## Smoke-test runbook

After install, run this once to verify the plugin works end-to-end. The council itself is the test.

### Smoke 1 — `/council --list` on an empty project

1. In a clean repo with no `.council/` directory: run `/council --list`.
2. Expected: leader reports "no councils yet" or shows an empty INDEX. No errors.

### Smoke 2 — Trivial design-only council

1. Run `/council pick a logging library for this Python service`.
2. Expected: leader asks 2–5 clarifying questions, then picks ~3 specialists (e.g., `observability`, `error-handling-strategy`, `documentation-strategy`).
3. Watch for: parallel Task dispatches in Phase 1 (multiple subagents in one message), consolidated `discussion/round1-positions.md`, draft design in Phase 2, parallel critique in Phase 3.
4. At Phase 5 prompt, choose **DESIGN-ONLY**. VERDICT.md should be auto-committed; INDEX.md should show one entry with status `DESIGN-ONLY`.

### Smoke 3 — Resume

1. Start a council. After Phase 1 completes, kill the session (close terminal or `/clear`).
2. Reopen and run `/council --resume <slug>`.
3. Expected: leader reads STATE.json, reports "resuming at Phase 2 — Synthesis," skips Phase 1 (members already done), proceeds.

### Smoke 4 — Member failure recovery

1. Start a council. (Hard to simulate intentionally — trust the retry logic in the SKILL.md Phase 1 step 3.)
2. Confirm via inspection: SKILL.md Phase 1 step 3 documents the retry-once-then-mark-unavailable policy.

### Smoke 5 — Escalation

1. Hand the council a brief with a deliberately split decision (e.g., "design pricing plan storage — single source-of-truth or eventually-consistent caches?").
2. Expected: in Phase 4, leader detects a structural disagreement between specialists, renders `escalation-prompt.md` with both positions, asks the user to pick.

### Tests

Run the helper + structural test suite:

```bash
venv/bin/pytest plugins/council/tests/ -v
```

All tests should PASS.

## Limits (v1)

- Cross-project memory is not implemented — each project has its own `.council/`.
- Auto-promotion of invented specialists into the library is manual (see "Promotion path" in the design spec).
- Councils are flat — no recursion (sub-councils mid-flow). Re-invoke `/council` for sub-questions.
- No token-cost telemetry per deliberation.

## Contributing

The library specialists are data-driven — add new ones by dropping a markdown file into `library/specialists/` following the schema in `plugins/council/library/specialists/database-schema.md`. The structural test (`tests/test_specialist_library.py`) validates additions automatically — extend `EXPECTED_NAMES` in that test to include the new persona.

## License

MIT.
