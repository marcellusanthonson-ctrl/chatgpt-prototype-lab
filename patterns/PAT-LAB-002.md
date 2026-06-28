# PAT-LAB-002 — Separate observation, hypothesis, validation, approval, and resolution

Status: `VALIDATED`
Scope: `LAB`, `MammothSkills`, `Symphonie`
Updated-At: `2026-06-28`

## Intent

Prevent inference, technical success, or continuation from being mistaken for
approval or closure.

## Procedure

1. Label observations without interpreting them as decisions.
2. Mark hypotheses as unverified until evidence validates them.
3. Record validation separately from approval by the sole approver.
4. Track correction, verification, and resolution as distinct transitions.
5. Supersede incorrect records explicitly instead of erasing them.

## Anti-patterns

- converting silence or partial agreement into approval;
- closing an error when only a written correction exists;
- silently deleting an incorrect decision.

## Evidence

- `LAB_CONTRACT.md`, sections 4 and 10;
- `METHODOLOGY.md`, sections 5 and 6;
- legacy `patterns/integration/PAT-LAB-002-state-separation.md`.
