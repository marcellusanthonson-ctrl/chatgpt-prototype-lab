# Symphonie — Project State

Project-ID: `symphonie`
Status: `KNOWN_AND_SYNCED`
Last-Updated: `2026-07-14`
Repository: `marcellusanthonson-ctrl/symphonie-codex-lab`

## Role

Symphonie is an eight-phase workflow that creates and develops applications and websites from beginning to end. It coordinates project-specific work across ChatGPT, Claude, and Codex. Skills are instruments used by particular phases; Symphonie is not the canonical producer of reusable skills.

## Operating model

- Jonathan Martínez approves.
- ChatGPT coordinates, validates, audits, and issues bounded orders.
- Claude performs explicitly assigned discovery and definition phases.
- Codex performs bounded technical execution without autonomous authority.

## Structural relationship with MammothSkills

Symphonie and MammothSkills remain independent projects. Symphonie may provide requirements and consumer feedback; MammothSkills may later provide identified approved skill artifacts or releases. Release, installation, migration, consumer fit, runtime compatibility, and integration remain separate validations and permissions.

Canonical decisions: `DEC-LAB-005`, `DEC-LAB-006`.

## Current Phase 3A architect baseline

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
REG-08 = PASS
REG-09 = BLOCKED_AS_EXPECTED
REG-09_REASON = MIGRATION_TARGET_UNCONFIRMED
UNAUTHORIZED_WRITES = ZERO
NORMAL_EIGHT_OUTPUT_FLOW = PRESERVED
```

Alpha.6 conditionally adds `.project/phase-3/migration-handoff.json` when an authorized instruction declares a migration or another applicable fidelity condition. It preserves source identity, formulas, sensitive fidelity zones, runtime risks, navigation, asset provenance, observable acceptance criteria, and reference images.

### Accepted historical evidence limitation

```text
FULL_HISTORICAL_REGRESSION_PACK = NOT_REVALIDATED_IN_ALPHA6_EXECUTION
MISSING_RETAINED_ACTUAL_EVIDENCE = REG-02 THROUGH REG-07
LIMITATION = ACCEPTED_NON_BLOCKING_FOR_PROMOTION
```

The limitation does not invalidate REG-08 or REG-09 and does not block baseline approval. It prevents claiming that the complete historical pack was revalidated during the Alpha.6 run.

Required future tests are recorded in:

`projects/symphonie/reports/ALPHA6_HISTORICAL_EVIDENCE_TEST_PLAN.md`

The future evidence plan covers:

1. `REG-02`: block source-code paths and preserve the DOCUMENT_WRITE boundary;
2. `REG-03`: block an unconfirmed target stack;
3. `REG-04`: complete a valid Next.js Phase 3A documentation task and stop before implementation;
4. `REG-05`: preserve undefined button behavior without inventing routes or endpoints;
5. `REG-06`: reject generic visual direction and justify a product-specific direction;
6. `REG-07`: preserve an existing design system without creating unauthorized parallel tokens.

The plan is `PLANNED_NOT_AUTHORIZED`.

## Historical Phase 3A baseline

```text
VERSION = 0.1.0-alpha.5
STATUS = HISTORICAL_APPROVED_BASELINE_CLOSED_IMMUTABLE
```

Alpha.5 remains preserved as immutable historical evidence.

## Current Phase 4A implementer baseline

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

Its approval does not authorize release, installation, migration, or integration.

## Validated synthetic architect-to-implementer handoff

Project: `handoff-controlled-017`

```text
RESULT = PASS_WITH_FINDINGS
HANDOFF_COMPATIBILITY = PASS
CODEX_DISCOVERY_AND_INTERPRETATION_AS_CHAIN = PASS
VALIDATED_CHAIN = architect -> human gate -> implementer -> build -> manual browser validation
REAL_DESIGN_EXECUTION = NOT_YET_VALIDATED
REPEATABILITY = NOT_YET_VALIDATED
```

The synthetic exercise validated Phase 3A contract generation, preservation of the human design gate, Phase 4A consumption of canonical JSON contracts, bounded application-source changes, successful build, browser rendering, responsive behavior, keyboard and focus behavior, accessibility basics, action preservation, and boundary checks.

It does not establish execution on a real design, reproducibility, production readiness, release, migration, or integration.

## Canonical minimal handoff knowledge

The LAB records three verified generic controls:

- `knowledge/contracts/phase3-minimum-assertions.json`;
- `knowledge/contracts/action-preservation.json`;
- `knowledge/regressions/imp-reg-11.json`.

They provide minimum Phase 3A exit assertions, UI-action preservation, and fail-closed authorization checks before observable effects.

## Current operational sequence

```text
1. Alpha.6 promotion is approved and recorded under DEC-LAB-009.
2. Historical REG-02 through REG-07 evidence closure may be executed later under a separate bounded authorization.
3. Plan a real-design execution through the approved architect-to-implementer chain.
4. Obtain explicit bounded authorization for each runtime and repository-writing phase.
5. Execute and assess the real design without integration or release.
6. Repeat the flow before claiming reproducibility.
7. Only then consider migration or extraction into MammothSkills under separate authorization.
```

## Authorization state

```text
ALPHA6_BASELINE_PROMOTION = APPROVED_RECORDED_AUTHORIZATION_CONSUMED
HISTORICAL_EVIDENCE_EXECUTION = NOT_AUTHORIZED
PRODUCT_CHANGE = NOT_AUTHORIZED
REAL_DESIGN_EXECUTION = NOT_AUTHORIZED
REPEATABILITY_TEST = NOT_AUTHORIZED
SKILL_MERGE = NOT_AUTHORIZED
SKILL_RELEASE = NOT_AUTHORIZED
SKILL_INSTALLATION = NOT_AUTHORIZED
SKILL_INTEGRATION = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
MAMMOTHSKILLS_MIGRATION = NOT_AUTHORIZED
MAMMOTHSKILLS_RELEASE = NOT_AUTHORIZED
```

## Next action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`

Recommended transition:

`PLAN_REAL_DESIGN_EXECUTION_OR_SEPARATELY_AUTHORIZE_HISTORICAL_EVIDENCE_CLOSURE_WITHOUT_INTEGRATION`
