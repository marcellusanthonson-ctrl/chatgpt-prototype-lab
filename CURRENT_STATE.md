# LAB Current State

Document-ID: `lab.current-state`
Version: `1.0.4`
Status: `ACTIVE`
Last-Updated: `2026-07-11`

`CURRENT_STATE.json` is the structured source of truth. This file is its
human-readable view.

## Active project and phase

- Active project: `lab`
- Current phase: `KNOWLEDGE_BASE_OPERATIONAL_V1`
- Methodology: version `1.0.0`, status `APPROVED`
- Canonical methodology: `METHODOLOGY.md`

LAB is active and its knowledge base is operational. The approved methodology
remains frozen and in force until an explicitly approved decision supersedes
it.

## Project boundaries

### LAB

LAB is the starting laboratory for viability, feasibility, risk analysis,
experiments, integrations, and project initiation. It preserves validated
cross-project knowledge and does not contain or authorize product execution.

### MammothSkills

MammothSkills creates, adapts, audits, tests, repairs, versions, and publishes
skills for declared agent platforms and consumer contracts. It may create new
skills or adapt existing skills for Claude or Codex.

Current state:

```text
STATUS = ACTIVE_PIPELINE_VALIDATED_PHASE_A
WORKING_BRANCH = audit/ms-001
CURRENT_HEAD = 034910e9fec4c0f0b97fe06ee94554bda289a1b6
MS_001 = MAMMOTHSKILLS_PIPELINE_VALIDATION
RUNTIME_VALIDATION = DEFERRED_TO_NEXT_SESSION
RELEASE = NOT_AUTHORIZED
CONSUMER_INTEGRATION = NOT_AUTHORIZED
```

The three MS-001 skills remain a MammothSkills validation corpus:

- `intake-brief`
- `project-scoping`
- `project-status`

Their future use in Claude-operated Symphonie phases requires an audit of their
current state, Claude runtime validation, an identified release, and a separate
consumer-integration authorization.

### Symphonie

Symphonie is an eight-phase workflow that creates and develops applications and
websites from beginning to end. It coordinates project-specific work across
ChatGPT, Claude, and Codex. Skills are instruments used by particular phases;
they are not the purpose of Symphonie.

Current operational objective:

```text
Complete formal promotion review of symphonie-ui-implementer 0.1.0-alpha.3,
then prove direct architect-to-implementer handoff, real design execution, and
repeatability before any separately authorized migration to MammothSkills.
```

## Current Symphonie Codex skill state

### `symphonie-ux-ui-architect`

```text
VERSION = 0.1.0-alpha.5
PHASE = 3A
CAPABILITY = DOCUMENT_WRITE
STATUS = APPROVED_BASELINE_CLOSED_IMMUTABLE
STATIC_VALIDATION = PASS
RUNTIME_VALIDATION = PASS
PROMOTION_GATE = PASS
```

This skill defines and writes the approved Phase 3A design documents. It does
not write application source code.

### `symphonie-ui-implementer`

```text
VERSION = 0.1.0-alpha.3
PHASE = 4A
CAPABILITY = SOURCE_WRITE
STATUS = TECHNICALLY_VALIDATED_PROMOTION_PENDING
STATIC_VALIDATION = PASS
RUNTIME_SUITE = IMP-REG-01 THROUGH IMP-REG-12
RUNTIME_VALIDATION = PASS
VALIDATED_LOCAL_HEAD = 73c0448dfb99e04a943a8e75704f14daef2c2631
RUNTIME_ORDER = SYM-UI-IMPLEMENTER-RUNTIME-009
RUNTIME_ORDER_STATE = CONSUMED
PROMOTION = NOT_AUTHORIZED
RELEASE = NOT_AUTHORIZED
```

The runtime suite was completed without changing the validated HEAD, tracked
repository source, Git configuration, or another repository. This technical
success does not itself create promotion approval.

The next recommended transition is a bounded promotion review for
`symphonie-ui-implementer 0.1.0-alpha.3`. Only after a separate explicit
approval may it be recorded as an immutable approved baseline.

## Initial Symphonie Codex skill cycle

The two historical candidates were created or adapted inside
`symphonie-codex-lab` before MammothSkills existed. Their audit and operational
validation are completed there to preserve continuity, fixtures, regression
evidence, and source history.

Current completion state:

```text
SKILL_1_RUNTIME = PASS
SKILL_2_RUNTIME = PASS
HANDOFF_COMPATIBILITY = NOT_YET_VALIDATED
CODEX_DISCOVERY_AND_INTERPRETATION_AS_CHAIN = NOT_YET_VALIDATED
REAL_DESIGN_EXECUTION = NOT_YET_VALIDATED
REPEATABILITY = NOT_YET_VALIDATED
```

The correct remaining sequence is:

```text
1. Review promotion evidence for symphonie-ui-implementer 0.1.0-alpha.3
2. Obtain explicit approval or rejection from Jonathan Martínez
3. If approved, record the immutable implementer baseline
4. Execute architect -> Phase 3A contracts -> implementer handoff validation
5. Execute a real design implementation
6. Repeat the flow to validate reproducibility
7. Only then consider migration to MammothSkills under separate authorization
```

## Approved structural relationship model

Independent projects may establish explicit structural relationships when a
workflow requires them. Project independence does not mean absence of
interaction.

Canonical decisions: `DEC-LAB-005`, `DEC-LAB-006`.

```text
Symphonie -> requirements and feedback -> MammothSkills
MammothSkills -> approved skill artifact/release -> Symphonie
Skill runtime -> Claude or Codex according to target_platform
```

Symphonie may consume an approved skill directly from MammothSkills only as an
identified artifact or release with target platform, source commit, version or
artifact ID, checksum when applicable, configuration, and validation evidence.
Technical adaptation, runtime compatibility, consumer fit, release, and
integration remain separate validations and permissions.

## Post-validation migration strategy

After the initial Symphonie Codex skill cycle is closed, reusable skill assets,
generic tests, audit methods, adaptation methods, and regression techniques may
be migrated or extracted into MammothSkills under separate authorization.

Symphonie retains phase placement, input/output contracts, handoff rules,
consumer-specific fixtures, installed release identity, and integration
evidence. Historical copies must be marked `legacy`, `superseded`, or
`evidence-only`; they must not be silently deleted.

## Authority

- Jonathan Martínez: sole approver.
- ChatGPT: coordinator, validator, auditor, and bounded-order issuer.
- Claude: discovery and definition only when explicitly assigned.
- Codex: bounded technical executor only.
- Codex autonomous authority: `NO`.

A commit records a transition but does not create approval.

## Decisions in force

- `DEC-LAB-001`: approve the LAB repository structure.
- `DEC-LAB-002`: use GitHub as the external laboratory memory.
- `DEC-LAB-003`: adopt the fixed continuity read protocol.
- `DEC-LAB-004`: freeze methodology v1.0 and use Git as structured memory.
- `DEC-LAB-005`: permit explicit structural producer-consumer relationships
  between independent projects.
- `DEC-LAB-006`: complete the initial Symphonie Codex skill cycle before
  canonical migration to MammothSkills.

## Open or contained errors

- `ERR-LAB-001`: executor confused with target platform — `CONTAINED`.
- `ERR-LAB-002`: overcomplicated correction — `CONTAINED`.

`ERR-TOOLING-001` is `CORRECTED`, not verified or closed.

## Authorization state

```text
lab_documentation = NOT_AUTHORIZED
mammothskills_implementation = NOT_AUTHORIZED
mammothskills_migration = NOT_AUTHORIZED
mammothskills_release = NOT_AUTHORIZED
symphonie_runtime = NOT_AUTHORIZED
symphonie_integration = NOT_AUTHORIZED
product_changes = NOT_AUTHORIZED
codex_autonomous_authority = NO
```

This documentation records the runtime milestone and recommended sequence. It
does not authorize promotion, runtime execution, migration, release,
installation, consumer integration, product change, or repository modification
outside LAB.

## Next authorized action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`

Recommended transition:

`REVIEW_AND_EXPLICITLY_APPROVE_OR_REJECT_PROMOTION_OF_SYMPHONIE_UI_IMPLEMENTER_0.1.0_ALPHA.3`

## Continuity read order

1. `LAB_CONTRACT.md`
2. `METHODOLOGY.md`
3. `CURRENT_STATE.json`
4. `CURRENT_STATE.md`
5. `registry/projects.json`
6. active project state
7. decisions in force
8. open errors
9. applicable patterns
