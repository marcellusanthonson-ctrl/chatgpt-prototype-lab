# ERR-LAB-002 — Overcomplicated correction after a simple governing rule

Status: `CONTAINED`
Severity: `MEDIUM`
Detected: `2026-06-28`
Updated-At: `2026-06-28`
Projects: `LAB`, `MammothSkills`

## Observed behavior

After the target-platform mistake, the attempted correction introduced extra
classifications and split adaptations instead of applying the user's simple
rule: MammothSkills produces skills and each skill lives in its native
platform.

## Root cause

The response tried to redesign the architecture before restating and locking
the explicit governing model.

## Impact and containment

The additional architecture was not approved or implemented. The simpler
platform rule is now explicit in the methodology and project state.

## Preventive rule

Restate the user's governing rule literally, compare current artifacts against
it, and apply the minimum correction before introducing new architecture.

This error remains contained, not verified or closed.
