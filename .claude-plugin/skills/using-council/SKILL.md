---
name: using-council
description: Orchestrates a multi-perspective council deliberation. Use when invoked by the /council slash command, or when another skill explicitly requests a council. Drives the leader role through Phase 0 (intake) → Phase 6 (execution + checkpoints), persisting all artifacts under `.council/<slug>/` and reusing superpowers:writing-plans + executing-plans for implementation phases.
---

# Using the Council

You are the **leader** of a council deliberation. You run in the main session.
Members are subagents you dispatch via the Task tool.

**Announce at start:** "I'm using the using-council skill to run a council deliberation."

## Invocation

`/council <brief>` or `/council` (interactive) or `/council --resume <slug>` or `/council --list`.

- `--list`: open `.council/INDEX.md` and show it to the user; stop.
- `--resume <slug>`: read `.council/<slug>/STATE.json` (use `scripts/state.py:load_state`) and jump to the phase named in `state.phase`. Skip work already marked `done: true`.
- Otherwise: start at Phase 0.

## Helpers (Python scripts in this skill's `scripts/` directory)

- `scripts/slug.py` — `make_slug(headline, date=None)` produces `YYYY-MM-DD-kebab-headline`.
- `scripts/state.py` — `CouncilState`, `MemberRecord`, `load_state(path)`, `write_state(path, state)`.
- `scripts/index.py` — `IndexEntry`, `append_council(idx, entry)`, `set_status(idx, slug, new_status)`, `read_index(idx)`.

Run helpers via Bash. Resolve paths from the plugin's own install location (do not assume a `plugins/council/` prefix — this plugin is meant to be installed at `~/.claude/plugins/council/` or any standalone location). The skill knows its own root via `${CLAUDE_PLUGIN_ROOT}` (or compute it from this `SKILL.md`'s path). Example:
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/using-council/scripts/state.py"
```
Or import them inline in a small Bash heredoc when you need a one-shot.

## Plugin paths (relative to this skill)

- Templates: `../../library/templates/{brief,verdict,research-prompt,critique-prompt,escalation-prompt,checkpoint-review}.md`
- Specialists: `../../library/specialists/<name>.md`
- Core agents: `../../agents/council-{architect,skeptic,user-advocate}.md`

## Output paths (relative to project root)

- Per-deliberation directory: `.council/<slug>/`
- Index: `.council/INDEX.md`

---

## Phase 0 — Intake

**Goal:** produce a complete `BRIEF.md` and a roster.

### Steps

1. **Headline & slug.**
   - From the user's brief argument (or from an interactive prompt: "What does this council need to decide or design?"), distill a 3–8 word kebab headline.
   - Use `make_slug(headline)` to generate the slug.
   - Create the directory: `.council/<slug>/`.

2. **Context gathering (autonomous).**
   - Read `README.md`, `pyproject.toml`/`package.json`, top-level config files.
   - Glob the source tree to learn the layout.
   - Grep for terms in the brief to find existing structure that will collide or extend.
   - Use `WebSearch`/`WebFetch` when the brief depends on external knowledge — specs, framework docs, current state of the art, prior incidents, library versions. Cite sources you'll feed into BRIEF.md. Skip the web when the codebase or user can answer.
   - Spend whatever time it takes — this is cheaper than asking the user.

3. **Prior verdicts scan.**
   - If `.council/INDEX.md` exists, read it. Read `VERDICT.md` files whose briefs semantically overlap the new brief. Surface up to 2 strong matches.

4. **Clarifying questions (with the user).**
   - **Unbounded.** Ask one question at a time. Continue until you can write a complete BRIEF.md.
   - Reserve user attention for things only the user knows: intent, preferences, constraints, success criteria. Anything you can answer by reading the codebase, answer yourself.
   - Log every Q/A verbatim — they go in `BRIEF.md` `## Open Questions Resolved With User`.

5. **Roster selection.**
   - Always include 3 core members: architect, skeptic, user-advocate.
   - Pick 2–4 specialists. For each candidate `library/specialists/<name>.md`, read its `when_to_pick` and judge fit against the brief. Rank by fit; pick top 2–4.
   - If no library specialist is a strong fit for a needed role, **invent** one: write a fresh persona using the same schema as a library entry; save it under `.council/<slug>/research/_invented-<name>.md`; mark `invented: true` in BRIEF.md.
   - Hard cap: 7 total members. If you believe >4 specialists are genuinely required, instead emit a SCOPE-TOO-LARGE verdict (per `verdict.md` template) and ask the user to decompose.

6. **Write BRIEF.md.**
   - Render `library/templates/brief.md` with all sections filled in.

7. **Initialize STATE.json.**
   - Construct a `CouncilState` with `phase="phase-0-intake"` (about to advance) and one `MemberRecord` per roster member, all `done=false`.
   - Write to `.council/<slug>/STATE.json` via `write_state`.

8. **Append to INDEX.md.**
   - `append_council(.council/INDEX.md, IndexEntry(slug, date, "IN-PROGRESS", brief_headline))`.

9. **Advance phase to `phase-1-research` and persist STATE.**

### Exit condition

`BRIEF.md` is complete and `STATE.json` reflects the chosen roster.

---

## Phase 1 — Research

**Goal:** parallel research artifacts from every member.

### Steps

1. **Render member prompts.**
   For each member in the roster:
   - Load the persona body:
     - core: read `agents/council-<role>.md` (strip frontmatter; pass body as `persona_full_text`)
     - library specialist: read `library/specialists/<name>.md` (strip frontmatter; pass body as `persona_full_text`; record `display_name` from frontmatter)
     - invented: read `.council/<slug>/research/_invented-<name>.md`
   - Render `library/templates/research-prompt.md` with:
     - `{{display_name}}` — the member's display name (e.g., "Database Schema Specialist")
     - `{{brief_full_text}}` — full text of `.council/<slug>/BRIEF.md`
     - `{{persona_full_text}}` — the persona body
     - `{{artifact_path}}` — `.council/<slug>/research/<role>.md` (or `architect.md`/`skeptic.md`/`user-advocate.md` for core)
     - `{{related_verdicts_block}}` — paths and 1-line "why" for each related prior verdict (from BRIEF.md), or the literal string "(none)"

2. **Dispatch all members in parallel.**
   Send a single message containing one Task tool call per member. **All Task calls go in one message** so they execute concurrently.
   - For core members, set `subagent_type` to the matching custom type: `council-architect`, `council-skeptic`, `council-user-advocate`. (Plugin must be installed for these to resolve; otherwise fall back to `general-purpose`.)
   - For specialists (library or invented), use `subagent_type: general-purpose`.
   - For each Task call, the `prompt` field is the rendered research-prompt; `description` is `"<role> Phase 1 research"`.
   - Skeptic's prompt naturally includes the inverted-brief instruction (the template handles it).

3. **Collect & validate artifacts.**
   For each returned subagent, verify the artifact file exists at the expected path and contains the required `## Findings`, `## Tensions`, `## Initial Recommendation`, `## Open Questions` sections.
   - If missing or malformed: retry that member ONCE with a corrective prompt (point at the missing section). On second failure: leave the member's slot empty and add a `## Dissents` entry to VERDICT.md later (`{role}: research unavailable`).
   - **Word-budget policy.** The 500-word target is soft. **Never auto-truncate or summarize a member's artifact** — Phase 2 synthesis always uses the full content. If the artifact is >1000 words (i.e. >2× the target), append the role to `state.research_over_budget` so Phase 2 knows to read carefully. Below 1000 words: no warning, no action — modest overruns are expected when context is genuinely needed.

4. **Mark members done.**
   For each member with a valid artifact: `state.mark_done(role)`. Persist STATE.json.

5. **Advance phase to `phase-2-synthesis`** and persist STATE.

### Exit condition

For every roster member: either the artifact exists and is well-formed, or the member is marked unavailable in STATE.json.

---

## Phase 2 — Synthesis

**Goal:** produce a draft design that surfaces both agreement and disagreement.

This is the *only* phase where the leader writes substantive design content
without member input. It's also the most important phase to do honestly:
the draft must surface real disagreement between member positions, not
paper over it.

### Steps

1. **Read all member research artifacts** in `.council/<slug>/research/`.

2. **Write `discussion/round1-positions.md`.**
   For each member: 1-paragraph summary of their position (findings + recommendation), preserving who said what. This is the leader's record of "who came in with what."

3. **Construct the draft design.**
   Write `discussion/draft-design.md` with these sections (in this order):
   - `## Agreement Map` — bullet list of points where ≥2 members agreed (cite which members).
   - `## Disagreement Map` — for each material disagreement: name it, list the contesting positions and which members held them, do NOT resolve yet.
   - `## Draft Design` — the leader's best synthesis. Where members agreed, follow them. Where they disagreed, pick a position with a 1-line rationale (this is the *draft* — Phase 3 may overturn it).
   - `## Counter-Arguments` — for each chosen position, list the strongest counter you can construct. The Skeptic may not have caught everything.
   - `## Open Questions` — anything unresolved.

4. **Mark `state.draft_design_written = true`** and persist STATE.

5. **Advance phase to `phase-3-critique`** and persist STATE.

### Exit condition

`discussion/round1-positions.md` and `discussion/draft-design.md` both exist
and contain the required sections.

### Honesty check (leader rule)

Do not collapse disagreement into false consensus. If two members materially
disagree, they're in `## Disagreement Map` — period. The Skeptic's job in
Phase 3 is to verify the leader didn't paper over real splits in Phase 2.

---

## Phase 3 — Critique

**Goal:** every member critiques the leader's draft design.

### Steps

1. **Render critique prompts.**
   For each member (skip members marked unavailable in STATE):
   - Render `library/templates/critique-prompt.md` with:
     - `{{display_name}}`, `{{persona_full_text}}` — same as Phase 1
     - `{{brief_full_text}}` — full BRIEF.md
     - `{{draft_design_full_text}}` — full `discussion/draft-design.md`
     - `{{artifact_path}}` — `.council/<slug>/discussion/_critique-<role>.md` (per-member, will be consolidated)

2. **Dispatch all members in parallel** in one message (same pattern as Phase 1).
   - Skeptic gets the same template; the template's instructions already direct the Skeptic to hunt for hidden assumptions, premature commitments, etc.

3. **Collect & validate.** Each returned artifact must contain `## Agree`, `## Reject`, `## Missing`. Same retry/failure semantics as Phase 1.
   - **Word-budget policy.** The 300-word target is soft. **Never auto-truncate or summarize a member's critique** — Phase 4 reads the full text. If a critique is >600 words (i.e. >2× the target), append the role to `state.critique_over_budget`. Below 600 words: no warning, no action.

4. **Consolidate.**
   Write `discussion/round2-critique.md` by stitching all `_critique-<role>.md` files together with a `## {role}` header above each member's section. Keep raw text — do not summarize across members; that's the leader's Phase 4 job.

5. **Advance phase to `phase-4-final-design`** and persist STATE.

### Exit condition

`discussion/round2-critique.md` exists and contains a section per available member.

---

## Phase 4 — Final Design

**Goal:** resolve disagreements; produce VERDICT.md.

### Steps

1. **Read** `discussion/round2-critique.md` and `discussion/draft-design.md`.

2. **Classify each remaining disagreement** (decisions still contested after critique):
   - **Local/small** (e.g., "use a class vs a function"): leader breaks the tie with a one-sentence rationale. Loser's view goes in VERDICT's `## Dissents` (verbatim member's name + position).
   - **Structural/material** (e.g., "SQL vs document store", "monolith vs split"): **escalate to user.** Render `library/templates/escalation-prompt.md` with both positions, fill it in, and ask the user. The user's pick goes in VERDICT's `## Decisions` with `escalation_reason` recorded.
   - **Security/irreversible**: ALWAYS escalate (override the small/material distinction). Set `{{security_or_irreversible_flag_if_applicable}}` to a clear callout in the escalation prompt.

3. **Detect substantial change.**
   Compare the resulting design to `discussion/draft-design.md` `## Draft Design` section. If you changed:
   - any `## Decisions` outcome that was in the draft, OR
   - the architecture/component shape materially, OR
   - the success criteria,
   then **`state.phase_4b_triggered = true`**, **set `state.phase = "phase-4b-signoff"` and persist STATE before entering Phase 4b** (so a mid-4b interruption resumes correctly via `--resume`). Then proceed to Phase 4b.
   Otherwise skip Phase 4b.

4. **Write VERDICT.md** by rendering `library/templates/verdict.md`. All required sections must be filled. If status is `SCOPE-TOO-LARGE`, emit only the SCOPE-TOO-LARGE block (omit Design/Decisions/etc.).

5. **Auto-commit VERDICT.md** (first auto-commit of the flow):
   ```bash
   git add .council/<slug>/VERDICT.md
   git commit -m "council(<slug>): verdict — <brief headline>"
   ```
   Stage **only** the VERDICT.md path — do not `git add -A`. Set `state.verdict_committed = true`. Persist STATE.

6. **If status is `DESIGN-ONLY` (user opted out of execution) or `SCOPE-TOO-LARGE`:**
   - Update INDEX with `set_status(.council/INDEX.md, slug, "DESIGN-ONLY")` (or `"SCOPE-TOO-LARGE"`).
   - Set `state.phase = "complete"`. Stop.

7. Otherwise, advance phase to `phase-5-plan-handoff` and persist STATE.

### Exit condition

`VERDICT.md` exists, is committed, INDEX is updated. STATE reflects the next phase.

---

## Phase 4b — Sign-off

**Goal:** if Phase 4 changed substantially from the draft, get one more round of member sign-off before VERDICT lands.

### Steps

1. **Render a sign-off prompt for each available member.**
   This is a stripped critique-prompt variant focused on the *changes* from
   the draft. Build it inline:
   ```
   You are <display_name>. The council's draft has changed materially since
   your Phase 3 critique. Review the new VERDICT.md (full text below).

   <full VERDICT.md>

   Reply at <.council/<slug>/discussion/_signoff-<role>.md> with one of:
     APPROVE: <one-line reason>
     BLOCK: <what's wrong + what would unblock>

   Constraints: ≤100 words. Read-only project access. No subagents.
   ```

2. **Dispatch in parallel** (one message, one Task per member). All `general-purpose` is fine here — the persona has already been established earlier in the deliberation.

3. **Collect responses.**
   - If **all** APPROVE → advance to Phase 5 (or complete, per Phase 4 step 6).
   - If **any** BLOCK → treat as structural disagreement. Render the escalation prompt with the BLOCK reason verbatim and ask the user. User's pick + reason becomes a new entry in VERDICT's `## Decisions` (and the BLOCK is logged as a dissent). Then advance.

4. **Consolidate** all sign-off responses into `discussion/round3-signoff.md` (one section per member). Persist STATE.

5. **Advance state out of Phase 4b.** After consolidation completes, set `state.phase` to whatever Phase 4 step 6/7 dictates: `"complete"` if status is DESIGN-ONLY/SCOPE-TOO-LARGE, otherwise `"phase-5-plan-handoff"`. Persist STATE. (This closes the resumability gap — `--resume` after a Phase 4b interruption finds either `"phase-4b-signoff"` and re-runs only the dispatch, or this terminal value and skips to Phase 5.)

### Exit condition

Phase 4b is single-pass — never run a second 4b. The bound is: 2 critique rounds total (Phase 3 + this).

---

## Phase 5 — Plan Handoff

**Goal:** turn VERDICT.md into a concrete implementation plan.

### Steps

1. **Confirm with the user** that they want execution to proceed:
   ```
   VERDICT.md is committed at .council/<slug>/VERDICT.md.
   Proceed with Phase 5 (plan generation) and Phase 6 (execution with
   checkpoints), or stop here as DESIGN-ONLY?
   ```
   - If "stop": set INDEX status to `DESIGN-ONLY`, mark `state.phase = "complete"`, exit.
   - If "proceed": continue.

2. **Invoke `superpowers:writing-plans`** via the Skill tool. Pass an arg pointing at the verdict:
   ```
   Skill(skill="superpowers:writing-plans",
         args="Create an implementation plan for the council verdict at .council/<slug>/VERDICT.md. Save the plan to .council/<slug>/execution/plan.md.")
   ```
   The writing-plans skill will create the plan, possibly under `docs/superpowers/plans/...` by default — if so, **after it finishes, copy/move the resulting plan to `.council/<slug>/execution/plan.md`** so council artifacts stay co-located. Note both paths in STATE.

3. **Confirm plan exists** at `.council/<slug>/execution/plan.md`. If not, escalate to the user with the writing-plans output.

4. **Advance phase to `phase-6-execution`** and persist STATE.

### Exit condition

`.council/<slug>/execution/plan.md` exists and was generated by `superpowers:writing-plans`.

---

## Phase 6 — Execution with Checkpoints

**Goal:** drive implementation, with per-phase council checkpoints and a full-council pre-merge review.

### Steps

1. **Invoke `superpowers:executing-plans`** via the Skill tool with the plan path:
   ```
   Skill(skill="superpowers:executing-plans",
         args="Execute the plan at .council/<slug>/execution/plan.md. After each top-level task or phase boundary, return control to the council leader for a checkpoint review before proceeding.")
   ```
   `superpowers:executing-plans` typically runs tasks in batches; the goal here is to insert council review *between* batches.

2. **Per-phase checkpoint** — after each plan phase / batch:
   - **Pick the relevant specialist.** Re-run the Phase-0 selection algorithm against the diff summary of the just-completed batch. The Skeptic is *always* in the checkpoint; pick exactly 1 specialist.
   - **Render the checkpoint-review prompt** from `library/templates/checkpoint-review.md` with:
     - `{{verdict_relevant_sections}}` — the relevant `## Decisions` + `## Design` slices from VERDICT.md
     - `{{diff_summary}}` — `git diff --stat` for the batch + a short prose summary
     - `{{test_output}}` — output of the project's test suite for the batch
     - `{{deviation_log_or_none}}` — anything that diverged from the plan
     - `{{artifact_path}}` — `.council/<slug>/execution/checkpoint-<N>.md`
   - **Dispatch both members in parallel.** (Two Task calls in one message: Skeptic + the chosen specialist.)
   - **Read both verdicts.** Each returned `## Verdict` is one of `APPROVE | REQUEST_CHANGES | ESCALATE`.
     - All APPROVE → continue executing-plans.
     - Any REQUEST_CHANGES → return changes to the executor to apply, then re-run the checkpoint.
     - Any ESCALATE → escalate to the user with both verdicts shown.

3. **Pre-merge: full-council final review.**
   Once the plan is fully executed (and any requested changes applied):
   - **Dispatch all members** (full roster) in parallel using a final-review variant of the checkpoint prompt. Set `{{verdict_relevant_sections}}` to the *full* VERDICT.md and `{{diff_summary}}` to the *full* branch diff vs. the merge base.
   - **Read all verdicts.** Aggregation:
     - All APPROVE → write `execution/final-review.md` consolidating member sections; status = `READY`.
     - Any REQUEST_CHANGES → status = `CHANGES_REQUESTED`. Surface to user with details.
     - Any ESCALATE → status = `ESCALATED`. Surface to user.

4. **Auto-commit `final-review.md`** (second and final auto-commit of the flow):
   ```bash
   git add .council/<slug>/execution/final-review.md
   git commit -m "council(<slug>): final review — <READY|CHANGES_REQUESTED|ESCALATED>"
   ```
   Set `state.phase = "complete"`. Update INDEX: `set_status(.council/INDEX.md, slug, "EXECUTED")` (only when READY; otherwise leave `IN-PROGRESS` and surface to user). Persist STATE.

### Exit condition

`.council/<slug>/execution/final-review.md` exists, is committed, INDEX is updated, STATE is `complete`.

### Honesty check (leader rule)

Per-phase checkpoints are *checkpoints*, not theater. If the Skeptic
returns REQUEST_CHANGES, do not paper over it to keep things moving. The
council's value is exactly that it can pause execution mid-flight when
the design and the implementation drift apart.

---

## Resumability

A council deliberation may span multiple sessions, multi-hour gaps, or context resets. STATE.json is the source of truth.

### `/council --resume <slug>` semantics

1. **Read** `.council/<slug>/STATE.json` via `load_state`.
   - If missing or unreadable: walk the directory tree (`BRIEF.md`, `research/`, `discussion/`, `VERDICT.md`, `execution/`) to *reconstruct* a best-guess state. Show it to the user and ask "is this right?" before proceeding.

2. **Jump to the phase named in `state.phase`.**
   - For phases 1, 3, 6 (parallel-dispatch phases): re-render prompts only for members where `done == false`. Members with `done == true` are NOT re-run — their existing artifacts are reused.
   - For leader-only phases (0, 2, 4, 4b, 5): pick up where the artifact path indicates. (E.g., if `discussion/draft-design.md` exists, Phase 2 was at least partially done.)

3. **Idempotence:** writing an artifact that already exists must be safe (overwrite is fine; we're resuming the same role).

4. **Auto-commits don't re-fire.** If `state.verdict_committed == true`, do not re-commit VERDICT. Same for `final-review.md` (check git log).

### `/council --list` semantics

Read `.council/INDEX.md`. Show the table to the user. Stop.

### When STATE.json is missing entirely

Treat as a fresh start unless directory artifacts exist. If artifacts exist, see step 1 above (reconstruct + confirm).

---

## Invariants

(Stable across all phases — load-bearing rules of the council.)

- The leader always runs in the main session. Members are always subagents dispatched via the Task tool.
- Members never edit project code. Their only Write target is their assigned artifact path under `.council/<slug>/`.
- Hard caps: ≤7 members per council (3 core + ≤4 specialists), ≤2 critique rounds (Phase 3 + optional Phase 4b).
- Word budgets are **soft targets**, not hard caps: 500 words for research, 300 for critique/checkpoint. The leader **never** auto-truncates or summarizes a member's artifact — full content is always preserved for downstream phases. Going up to 2× the target is fine; beyond that, the role is logged to `state.research_over_budget` / `state.critique_over_budget` for awareness, but the artifact is still used in full.
- Auto-commit at exactly two points: end of Phase 4 (`VERDICT.md`), end of Phase 6 (`final-review.md`). All other artifacts are written but not auto-committed.
- Phase boundaries are commit-able; resumability via `STATE.json` is non-negotiable.
- Reuse, do not reinvent: Phase 5 calls `superpowers:writing-plans`; Phase 6 calls `superpowers:executing-plans`.
