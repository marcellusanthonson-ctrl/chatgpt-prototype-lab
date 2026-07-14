# LAB Current State

Document-ID: `lab.current-state`
Version: `1.0.10`
Status: `ACTIVE`
Last-Updated: `2026-07-14`

`CURRENT_STATE.json` is the structured source of truth. This file is its human-readable view.

## Active project and phase

- Active project: `lab`
- Current phase: `KNOWLEDGE_BASE_OPERATIONAL_V1`
- Methodology: `1.0.0`, `APPROVED`

LAB remains the documentary and governance layer. It does not authorize product execution by itself.

## Authority

- Jonathan Martínez is the sole approver.
- ChatGPT coordinates, audits, validates, and issues bounded orders.
- Claude performs explicitly assigned discovery and definition.
- Codex is a bounded technical executor with no autonomous authority.
- A commit records a transition but does not create authorization.

## Symphonie state

Symphonie remains `KNOWN_AND_SYNCED` and coordinates an eight-phase workflow for creating applications and websites.

Current operational objective:

```text
Plan and explicitly authorize a real-design execution through the validated
architect-to-implementer chain, then repeat the flow before any separately
authorized migration to MammothSkills.
```

## Phase 3A architect baseline

### Approved current baseline

```text
SKILL = symphonie-ux-ui-architect
VERSION = 0.1.0-alpha.6
PHASE = 3A
CAPABILITY = DOCUMENT_WRITE
STATUS = APPROVED_BASELINE_WITH_RECORDED_HISTORICAL_EVIDENCE_LIMITATION
BRANCH = feature/design-migration-handoff-alpha6
IMPLEMENTATION_COMMIT = 22d63a901ec30221e7e8e7e944203eb2239598bd
RUNTIME_EVIDENCE_COMMIT = 385f85b85560d8f5a12512c9f36e2bdd140f1d7b
APPROVAL_DECISION = DEC-LAB-009
APPROVED_BY = Jonathan Martínez
APPROVED_AT = 2026-07-14
```

Direct evidence:

```text
STATIC_VALIDATION = PASS
REG-08_MIGRATION_PATH = PASS
REG-09_FAIL_CLOSED = PASS
REG-09_REASON = MIGRATION_TARGET_UNCONFIRMED
UNAUTHORIZED_WRITES = ZERO
NORMAL_EIGHT_OUTPUT_FLOW = PRESERVED
```

Alpha.6 conditionally adds:

```text
.project/phase-3/migration-handoff.json
```

The document is created only when an authorized order activates a relevant migration or fidelity condition. Ordinary Phase 3A work retains the original eight-output flow.

### Accepted historical evidence limitation

```text
FULL_HISTORICAL_REGRESSION_PACK = NOT_REVALIDATED_IN_ALPHA6_EXECUTION
MISSING_RETAINED_ACTUAL_EVIDENCE = REG-02 THROUGH REG-07
PROMOTION_EFFECT = NON_BLOCKING_LIMITATION_ACCEPTED
```

This limitation does not invalidate REG-08 or REG-09. It prevents claiming that the complete historical pack was revalidated in the same execution.

The required future evidence work is documented in:

`projects/symphonie/reports/ALPHA6_HISTORICAL_EVIDENCE_TEST_PLAN.md`

That plan covers:

- REG-02: document-write boundary violation;
- REG-03: target stack unconfirmed;
- REG-04: valid Next.js Phase 3A task;
- REG-05: undefined UI action preserved without invented behavior;
- REG-06: generic visual direction rejected;
- REG-07: existing design system preserved.

The plan is `PLANNED_NOT_AUTHORIZED`.

### Historical Alpha.5 baseline

```text
VERSION = 0.1.0-alpha.5
STATUS = HISTORICAL_APPROVED_BASELINE_CLOSED_IMMUTABLE
```

Alpha.5 remains preserved as historical evidence and must not be modified or silently deleted.

## Phase 4A implementer baseline

```text
SKILL = symphonie-ui-implementer
VERSION = 0.1.0-alpha.3
PHASE = 4A
CAPABILITY = SOURCE_WRITE
STATUS = APPROVED_BASELINE_CLOSED_IMMUTABLE
STATIC_VALIDATION = PASS
RUNTIME_VALIDATION = PASS
RUNTIME_SUITE = IMP-REG-01 THROUGH IMP-REG-12
BASELINE_HEAD = c2f3159e754d356f23b6855f2aecf1a663209835
```

Its approval does not authorize release, migration, installation, or integration.

## Validated chained handoff

Synthetic project: `handoff-controlled-017`

```text
RESULT = PASS_WITH_FINDINGS
VALIDATED_CHAIN = architect -> human gate -> implementer -> build -> manual browser validation
HANDOFF_COMPATIBILITY = PASS
CODEX_DISCOVERY_AND_INTERPRETATION = PASS_AS_CHAIN
REAL_DESIGN_EXECUTION = NOT_YET_VALIDATED
REPEATABILITY = NOT_YET_VALIDATED
```

The synthetic exercise validated contract generation, the human approval gate, bounded implementation, build, browser rendering, responsive behavior, keyboard and focus behavior, action preservation, Phase 3A conformance, and scope boundaries.

It did not establish production readiness, execution on a real design, reproducibility, release, migration, or integration.

## Canonical minimal handoff knowledge

The following documents remain canonical and published:

- `projects/symphonie/knowledge/contracts/phase3-minimum-assertions.json`
- `projects/symphonie/knowledge/contracts/action-preservation.json`
- `projects/symphonie/knowledge/regressions/imp-reg-11.json`

They provide minimum Phase 3A assertions, UI-action preservation, and fail-closed authorization checks.

## Decisions in force

- `DEC-LAB-001` through `DEC-LAB-008` remain approved.
- `DEC-LAB-009` approves Alpha.6 as the current Phase 3A baseline with the recorded REG-02–07 evidence limitation.

## Errors and patterns

Open or contained errors:

- `ERR-LAB-001`: executor confused with target platform — `CONTAINED`.
- `ERR-LAB-002`: overcomplicated correction — `CONTAINED`.
- `ERR-TOOLING-001`: `CORRECTED`, not verified or closed.

Validated patterns:

- `PAT-LAB-001`: record events, not full transcripts;
- `PAT-LAB-002`: separate observation, hypothesis, validation, approval, and resolution;
- `PAT-LAB-003`: reconstruct context using a fixed order;
- `PAT-LAB-004`: bounded evidence-first audit;
- `PAT-MA-001`: Codex executes without autonomous authority.

## Authorization state

```text
ALPHA6_BASELINE_PROMOTION = APPROVED_RECORDED_AUTHORIZATION_CONSUMED
LAB_DOCUMENTATION = NOT_AUTHORIZED
HISTORICAL_EVIDENCE_EXECUTION = NOT_AUTHORIZED
REAL_DESIGN_EXECUTION = NOT_AUTHORIZED
REPEATABILITY_TEST = NOT_AUTHORIZED
MERGE = NOT_AUTHORIZED
RELEASE = NOT_AUTHORIZED
SYMPHONIE_RUNTIME = NOT_AUTHORIZED
SYMPHONIE_INTEGRATION = NOT_AUTHORIZED
MAMMOTHSKILLS_MIGRATION = NOT_AUTHORIZED
PRODUCT_CHANGES = NOT_AUTHORIZED
CODEX_AUTONOMOUS_AUTHORITY = NO
```

Promotion approval is separate from merge, release, installation, integration, migration, runtime execution, and product changes.

## Next action

```text
NEXT_AUTHORIZED_ACTION = NONE_UNTIL_NEW_EXPLICIT_APPROVAL
NEXT_RECOMMENDED_TRANSITION =
PLAN_REAL_DESIGN_EXECUTION_OR_SEPARATELY_AUTHORIZE_HISTORICAL_EVIDENCE_CLOSURE_WITHOUT_INTEGRATION
```
