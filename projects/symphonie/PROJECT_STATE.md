# Symphonie — Project State

Project-ID: `symphonie`
Status: `KNOWN_AND_SYNCED`
Last-Updated: `2026-07-16`
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

## Dedicated repository architecture

`DEC-LAB-010` approves the architecture for a dedicated private canonical workflow repository:

```text
TARGET_REPOSITORY = marcellusanthonson-ctrl/symphonie
VISIBILITY = PRIVATE
CANONICAL_BRANCH = main
ARCHITECTURE = APPROVED
REPOSITORY_CREATED = NO
REPOSITORY_CREATION = NOT_AUTHORIZED
BOOTSTRAP = NOT_AUTHORIZED
```

Until a separate creation order is completed and later registered, this project record continues to identify `marcellusanthonson-ctrl/symphonie-codex-lab` as the existing repository holding historical Symphonie Codex evidence. The historical repository must not be deleted or silently transformed.

Responsibility separation:

```text
chatgpt-prototype-lab = governance, decisions, errors, patterns, registry, continuity
future symphonie repository = canonical workflow, phase contracts, gates, schemas, identified integrations
MammothSkills = reusable skill production, adaptation, audit, versioning, releases
symphonie-codex-lab = historical Codex skill evidence and temporary laboratory
```

Local governance files in the future Symphonie repository will bind to or mirror LAB authority; they will not create independent approval authority. `CURRENT_STATE.json` will be the structured local source of truth and `CURRENT_STATE.md` its human-readable view.

## Phase 0 experimental baseline

`DEC-LAB-011` approves Phase 0 v0.1 as an experimental baseline:

```text
MODEL = 0A_CAPTURE -> 0B_ANALYZE_AND_CLASSIFY -> 0C_HUMAN_DECISION
STATUS = APPROVED_EXPERIMENTAL_BASELINE
STABLE_CONTRACT = NO
RUNTIME_VALIDATED = NO
REAL_CLIENT_USE = NOT_AUTHORIZED
```

### 0A — Capture

Records declarations, supplied documents, participants, provenance, privacy classification, and source conflicts. It does not interpret viability or approve progression.

Expected outputs:

- `client-intake-submission.json`
- `source-register.json`
- `privacy-screening.json`

### 0B — Analyze and classify

May be assigned to Claude only under an explicit bounded order. It analyzes already supplied sources, separates `CLIENT_DECLARED`, `DOCUMENT_EXTRACTED`, `INFERRED`, `UNKNOWN`, and `CONTRADICTORY`, identifies gaps and risks, and recommends without approving.

Expected outputs:

- `intake-analysis.json`
- `follow-up-question-set.json`
- `quotation-readiness-assessment.json`
- `intake-decision-recommendation.json`

It must not assume software, select a stack, design a solution, produce code or a quotation, estimate price or effort, import unrelated context, or issue unsupported professional conclusions.

### 0C — Human decision

Jonathan Martínez is the exclusive approver. Agents have no approval authority.

Allowed decisions:

- `APPROVE_DISCOVERY`
- `RETURN_FOR_CLARIFICATION`
- `REJECT_OR_ARCHIVE`
- `REFER_TO_QUALIFIED_REVIEW`
- `CLASSIFY_AS_NON_SOFTWARE_INTERVENTION`

Expected output: `phase-0-decision-record.json`.

Intake analyzes declarations and sources already supplied. Discovery creates new evidence through direct-user interaction, observation, research, and hypothesis validation. Intake cannot claim that the problem is validated or justify a quotation.

Privacy defaults to synthetic or anonymized data. `SENSITIVE_RESTRICTED` processing is blocked by default. Runtime, real-client data, Discovery, quotation, implementation, and integration remain not authorized.

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

The future evidence plan is `PLANNED_NOT_AUTHORIZED`.

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
1. DEC-LAB-010 approves the dedicated repository architecture, but creation remains not authorized.
2. DEC-LAB-011 approves Phase 0 v0.1 as an experimental baseline, but runtime remains not authorized.
3. Obtain a separate bounded authorization to create the empty private repository.
4. Verify repository identity and state.
5. Obtain a separate bounded authorization for the documentary bootstrap.
6. Validate schemas and execute only separately authorized synthetic tests.
7. Continue real-design, repeatability, historical-evidence, and migration work only through independent authorizations.
```

## Authorization state

```text
DEC_LAB_010_011_DOCUMENTATION = APPROVED_RECORDED_AUTHORIZATION_CONSUMED
SYMPHONIE_REPOSITORY_CREATION = NOT_AUTHORIZED
SYMPHONIE_BOOTSTRAP = NOT_AUTHORIZED
PHASE_0_RUNTIME = NOT_AUTHORIZED
PHASE_0_REAL_CLIENT_USE = NOT_AUTHORIZED
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

`SEPARATELY_AUTHORIZE_EMPTY_PRIVATE_SYMPHONIE_REPOSITORY_CREATION_THEN_BOOTSTRAP`
