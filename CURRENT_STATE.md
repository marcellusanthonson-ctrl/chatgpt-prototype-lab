# LAB Current State

Document-ID: `lab.current-state`
Version: `1.0.2`
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

### Symphonie

Symphonie is an eight-phase workflow for creating applications and websites. It
coordinates work across ChatGPT, Claude, and Codex. Claude performs assigned
discovery and definition phases; Codex performs bounded technical execution.

## Approved structural relationship model

Independent projects may establish explicit structural relationships when a
workflow requires them. Project independence does not mean absence of
interaction.

Canonical decision: `DEC-LAB-005`.

For MammothSkills and Symphonie:

```text
Symphonie -> requirements and feedback -> MammothSkills
MammothSkills -> approved skill artifact/release -> Symphonie
Skill runtime -> Claude or Codex according to target_platform
```

Before creating or adapting a skill, MammothSkills must determine:

```text
INTENDED_USE
CONSUMER_PROJECT
CONSUMER_PHASE
RUNTIME_AGENT
SOURCE_PLATFORM
TARGET_PLATFORM
INPUT_CONTRACT
OUTPUT_CONTRACT
CONSTRAINTS
VALIDATION_CRITERIA
```

When Symphonie is the consumer, it may provide phase-specific requirements,
examples, schemas, compatibility constraints, handoff requirements, and
validation feedback.

MammothSkills may then:

- create a new skill for Claude or Codex;
- adapt an existing Claude skill for a Claude-operated Symphonie phase;
- adapt a Claude or Codex skill for a Codex-operated Symphonie phase;
- revise and version the skill based on consumer feedback.

Symphonie may consume the approved skill directly from MammothSkills as the
canonical source. Direct consumption means using an identified artifact or
release with target platform, source commit, version or artifact ID, checksum
when applicable, configuration, and validation evidence.

Direct consumption does not authorize MammothSkills to write autonomously into
Symphonie and does not authorize Symphonie to depend on an unidentified mutable
working tree.

Technical adaptation, runtime compatibility, consumer fit, release, and
integration remain separate validations and permissions.

## MS-001

The three MS-001 skills remain a MammothSkills validation corpus:

- `intake-brief`
- `project-scoping`
- `project-status`

They are not current operational candidates for Symphonie. Their role is to
validate the MammothSkills adaptation, packaging, audit, and contract-test
pipeline.

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

## Open or contained errors

- `ERR-LAB-001`: executor confused with target platform — `CONTAINED`.
- `ERR-LAB-002`: overcomplicated correction — `CONTAINED`.

`ERR-TOOLING-001` is `CORRECTED`, not verified or closed.

## Authorization state

```text
lab_documentation = NOT_AUTHORIZED
mammothskills_implementation = NOT_AUTHORIZED
mammothskills_release = NOT_AUTHORIZED
symphonie_integration = NOT_AUTHORIZED
product_changes = NOT_AUTHORIZED
codex_autonomous_authority = NO
```

This documentation records the approved structural model. It does not authorize
a skill creation or adaptation, release, installation, consumer integration,
product change, or repository modification outside LAB.

## Next authorized action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`

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
