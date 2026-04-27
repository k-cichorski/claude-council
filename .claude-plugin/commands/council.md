---
name: council
description: Convene a council to deliberate on a project, feature, or design question. Leader gathers context, dispatches parallel-subagent members through structured research and critique rounds, produces a vetted VERDICT.md, and (optionally) drives implementation through writing-plans + executing-plans with per-phase checkpoints.
---

# /council

Invoke the council deliberation flow.

## Usage

- `/council <brief>` — start a new deliberation. The brief can be a one-liner ("add auth to the CLI") or a paragraph. The leader will ask follow-up questions until it has enough context.
- `/council` — interactive: leader prompts for the brief.
- `/council --resume <slug>` — resume an interrupted deliberation. The leader reads `.council/<slug>/STATE.json` and continues from the last incomplete phase.
- `/council --list` — list all councils in `.council/INDEX.md`.

## What happens

1. **Phase 0 — Intake**: leader explores the codebase, asks clarifying questions, picks specialists, scans prior verdicts.
2. **Phase 1 — Research**: members research in parallel.
3. **Phase 2 — Synthesis**: leader writes a draft design.
4. **Phase 3 — Critique**: members critique the draft in parallel.
5. **Phase 4 — Final design**: leader writes VERDICT.md (with optional Phase 4b sign-off).
6. **Phase 5 — Plan handoff**: leader invokes `superpowers:writing-plans` against the verdict.
7. **Phase 6 — Execution + checkpoints**: leader invokes `superpowers:executing-plans` with per-phase council checkpoints and a full-council pre-merge review.

Persisted artifacts live under `.council/<slug>/`. See the `using-council` skill for the full protocol.

## Implementation

When this command fires, invoke the **`using-council`** skill with the user-provided arguments forwarded as the brief (or as control flags `--resume <slug>`, `--list`).
