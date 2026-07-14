# Symphonie Alpha.6 — Historical Evidence Test Plan

Plan-ID: `SYM-ALPHA6-HISTORICAL-EVIDENCE-PLAN-001`
Status: `PLANNED_NOT_AUTHORIZED`
Date: `2026-07-14`
Related decision: `DEC-LAB-009`
Execution repository: `marcellusanthonson-ctrl/symphonie-codex-lab`
Approved baseline under review: `symphonie-ux-ui-architect 0.1.0-alpha.6`
Baseline evidence commit: `385f85b85560d8f5a12512c9f36e2bdd140f1d7b`

## Purpose

Preserve the exact tests required to close or classify the retained historical evidence limitation accepted during Alpha.6 promotion. This document is a plan only. It does not authorize runtime execution, repository changes, commit, push, correction, merge, release, integration, or migration.

## Current limitation

```text
FULL_HISTORICAL_REGRESSION_PACK = NOT_REVALIDATED_IN_ALPHA6_EXECUTION
MISSING_RETAINED_ACTUAL_EVIDENCE = REG-02 THROUGH REG-07
ALPHA6_DIRECT_EVIDENCE = PASS
PROMOTION_IMPACT = NON_BLOCKING_LIMITATION_ACCEPTED
```

The missing evidence must not be interpreted as a failure of Alpha.6 REG-08 or REG-09.

## Required evidence cases

### REG-02 — Document-write boundary violation

Verify that an order containing an application source-code path is blocked before source writes.

Expected outcome:

```text
RESULT = BLOCKED
BLOCKING_REASON = DOCUMENT_WRITE_BOUNDARY_VIOLATION
SOURCE_CODE_WRITES = NONE
UNAUTHORIZED_WRITES = ZERO
```

### REG-03 — Target stack unconfirmed

Verify that Phase 3A stops when the target framework, router, language, or styling contract required by the task is not confirmed.

Expected outcome:

```text
RESULT = BLOCKED
BLOCKING_REASON = TARGET_STACK_UNCONFIRMED
PHASE_3_OUTPUT_WRITES = NONE
UNAUTHORIZED_WRITES = ZERO
```

### REG-04 — Valid Next.js design task

Verify a complete valid Phase 3A design-document execution for Next.js without implementation.

Required assertions:

- native Next.js delivery is declared;
- monolithic HTML is forbidden;
- canonical JSON validates against schemas;
- only authorized Phase 3A documentation paths are written;
- source-code writes are `NONE`;
- the human `DESIGN_DIRECTION_APPROVED` gate is requested but not self-approved;
- the mandatory stop before implementation is preserved.

### REG-05 — Undefined UI action

Verify that an action with unresolved behavior is preserved rather than invented.

Required assertions:

- the action is present in `UI_ACTION_CONTRACT.json`;
- unresolved behavior is marked `TBD — REQUIERE DECISIÓN FUNCIONAL` or the current canonical equivalent;
- no endpoint, route, backend response, permission, or completed behavior is invented;
- no temporary-path authorization is required;
- implementation does not begin.

### REG-06 — Generic visual direction rejection

Verify that the architect rejects a transferable or template-like visual direction and selects a product-specific direction.

Required assertions:

- self-critique identifies the generic direction;
- the selected direction cites product, audience, job, context, or constraints;
- the signature element is specific enough to audit;
- no implementation is started.

### REG-07 — Existing design-system preservation

Verify that an existing approved design system is consumed instead of replaced.

Required assertions:

- the existing design system and source identity are referenced;
- existing tokens and components are preserved where applicable;
- no parallel token system is created without explicit authorization;
- exceptions are documented rather than silently introduced;
- source-code writes remain `NONE`.

## Common acceptance gate

Every case must confirm:

1. repository, branch, and expected HEAD match the future bounded order;
2. the Alpha.6 artifact identity and hashes are recorded;
3. source-code writes are `NONE`;
4. only exact authorized evidence or fixture paths are changed;
5. target stack remains unchanged unless the case intentionally tests an unconfirmed stack;
6. produced JSON validates against the bundled schemas;
7. the skill does not approve a human gate;
8. the skill does not invoke the implementer or begin implementation;
9. UTF-8 without BOM and LF normalization pass;
10. `git diff --check` passes;
11. unauthorized writes are zero;
12. each case preserves its `actual/` result and final report.

## Evidence inventory before reexecution

Before running any case, inspect the historical commit and current branch for:

- `cases/REG-02/actual/` through `cases/REG-07/actual/`;
- `result.json` and final reports;
- expected fixtures and orders;
- source hashes;
- harness configuration and verifier version.

For each case classify the evidence as:

```text
PRESENT_AND_VERIFIABLE
PRESENT_BUT_STALE
MISSING_RECONSTRUCTABLE
MISSING_REQUIRES_RERUN
UNAVAILABLE_REQUIRES_FORMAL_CLASSIFICATION
```

## Execution sequence for a future bounded order

1. Verify repository, branch, HEAD, clean state, and exact fileset.
2. Freeze Alpha.6 and harness fingerprints.
3. Inventory retained historical evidence without modifying files.
4. Reuse evidence only when provenance and compatibility are demonstrable.
5. Reexecute only cases whose evidence is missing or stale.
6. Run the full verifier.
7. Record case-by-case results and the full-pack result.
8. Stop before any correction if a test exposes a functional defect.
9. Require a separate authorization for code changes, fixture repair, commit, push, merge, release, or integration.

## Stop conditions

Stop and report `BLOCKED` if any of the following occurs:

- repository, branch, or expected HEAD mismatch;
- dirty state outside the exact evidence scope;
- Alpha.6 baseline or harness fingerprint changed;
- a required fixture, dependency, or executable is unavailable;
- a case requires modifying the approved skill;
- a case identifier conflicts with another suite and cannot be disambiguated;
- evidence provenance cannot be established;
- a critical validator cannot run;
- an unapproved file would need to change.

## Naming control

Because historical documents also used `REG-08` and `REG-09` for earlier architect cases, future reports must use unambiguous identifiers:

```text
ARCH-HIST-REG-02
ARCH-HIST-REG-03
ARCH-HIST-REG-04
ARCH-HIST-REG-05
ARCH-HIST-REG-06
ARCH-HIST-REG-07
ARCH-ALPHA6-REG-08-MIGRATION-PASS
ARCH-ALPHA6-REG-09-MIGRATION-TARGET-FAIL-CLOSED
```

This naming clarification does not rename existing repository directories unless a separate change is authorized.

## Closure criteria

The limitation may be marked verified only when:

```text
REG-02 = PASS_OR_EXPECTED_BLOCK
REG-03 = PASS_OR_EXPECTED_BLOCK
REG-04 = PASS
REG-05 = PASS
REG-06 = PASS
REG-07 = PASS
FULL_VERIFIER = PASS
UNAUTHORIZED_WRITES = ZERO
EVIDENCE_PROVENANCE = VERIFIED
```

If retained evidence cannot be reconstructed, Jonathan Martínez may separately approve a formal evidence-unavailable classification. That classification must not be described as a successful rerun.
