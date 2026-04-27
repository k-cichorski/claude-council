# Council Verdict — {{slug}}

> Status: IN-PROGRESS | DESIGN-ONLY | EXECUTED | ABANDONED | SCOPE-TOO-LARGE
>
> The canonical output of the council. Written at the end of Phase 4 (or Phase 4b
> if triggered). Auto-committed on completion. If status is SCOPE-TOO-LARGE,
> the Design and Decisions sections are omitted and a `## Decomposition Proposal`
> section is added instead.

## Design

{The agreed shape: architecture, components, interfaces, data flow.
Include diagrams (ASCII) if helpful. This is the *answer*.}

## Decisions

Numbered list. For each decision:
- the position chosen
- rationale (1–3 sentences)
- alternatives considered (with one-line reason for rejection)
- which member championed the chosen position

1. **{decision title}** — {chosen position}.
   - Rationale: {why}
   - Alternatives considered: {alt-1} (rejected: {reason}); {alt-2} (rejected: {reason})
   - Championed by: {member role}

2. …

## Dissents

For each disagreement that wasn't structural enough to escalate (those went
to the user during Phase 4 and are recorded in `## Decisions`):
- which member dissented
- their position (1–2 sentences)
- the leader's reason for not adopting it

(none if no dissents)

## Success Criteria

(Carry over from BRIEF.md, refined if the council narrowed them.)

- …

## Out of Scope

(Carry over from BRIEF.md non-goals plus any narrowing the council did.)

- …

## Risks and Mitigations

(Surfaced primarily by the Skeptic. Each risk paired with a mitigation or
an explicit "no mitigation, accepted because…")

| Risk | Mitigation |
|---|---|
| … | … |

## Implementation Pointer

Plan: `.council/{{slug}}/execution/plan.md` (filled in at Phase 5)

---

### For SCOPE-TOO-LARGE only

## Decomposition Proposal

This brief was too large for a single council (>4 specialists genuinely
required). The leader recommends splitting into:

1. **{sub-brief 1 headline}** — {1–2 sentences scoping it}
2. **{sub-brief 2 headline}** — …
3. …

Each sub-brief should be re-invoked via `/council <headline>` once the user
confirms decomposition.
