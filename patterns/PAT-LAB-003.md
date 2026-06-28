# PAT-LAB-003 — Reconstruct context using a fixed reading order

Status: `VALIDATED`
Scope: `LAB`, `MammothSkills`, `Symphonie`
Updated-At: `2026-06-28`

## Intent

Restore context from versioned evidence rather than relying exclusively on
conversational memory.

## Procedure

1. Read `LAB_CONTRACT.md` and `METHODOLOGY.md`.
2. Read `CURRENT_STATE.json` and its Markdown view.
3. Read the project registry and active project state.
4. Read decisions in force, open errors, and applicable patterns.
5. Stop when canonical records conflict or required evidence is missing.

## Anti-patterns

- beginning execution from remembered context alone;
- skipping authority or project-state records;
- treating an old session summary as higher authority than current state.

## Evidence

- `LAB_CONTRACT.md`, section 9;
- `METHODOLOGY.md`, section 10;
- `DEC-LAB-003`;
- legacy `patterns/integration/PAT-LAB-003-fixed-continuity-order.md`.
