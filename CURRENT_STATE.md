# LAB Current State

Document-ID: `lab.current-state`
Version: `1.0.1`
Status: `ACTIVE`
Last-Updated: `2026-07-07`

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

## Bootstrap closure

```text
Current phase: KNOWLEDGE_BASE_OPERATIONAL_V1
Bootstrap: COMPLETED
Implementation commit: 5fe7effeb7b9896461b15f2b207fbcffe3897a1f
Validation: PASS
Remote publication: VERIFIED
Previous execution order: CONSUMED
Next authorized action: NONE_UNTIL_NEW_EXPLICIT_APPROVAL
```

The completed bootstrap was validated, published, and accepted for closure.
Its bounded execution order is consumed and is not reusable permission.

## Project state

### LAB

LAB governs the method and preserves cross-project knowledge. This synchronization
records a current-state update only; it does not authorize product work,
consumer integration, releases, or implementation.

### MammothSkills

MammothSkills is `active_pipeline_validated_phase_a`.

It creates, audits, adapts, tests, versions, and publishes skills, but is not a
skill runtime. Skills for Codex live in Codex, and consumers may only consume
fixed approved releases through separate explicit integration orders.

Current operational evidence:

```text
Repository: marcellusanthonson-ctrl/MammothSkills
Working branch: audit/ms-001
Current head: 034910e9fec4c0f0b97fe06ee94554bda289a1b6
Phase A evidence commit: 55f66f4d9020ca93113aef61194141efdc3688cc
MS-001 state: MS_001_CLASSIFIED_AS_PIPELINE_VALIDATION
MS-001 purpose: MAMMOTHSKILLS_PIPELINE_VALIDATION
Codex adaptation: TEST_ARTIFACT
Runtime validation: DEFERRED_TO_NEXT_SESSION
Release: NOT_AUTHORIZED
Consumer integration: NOT_AUTHORIZED
```

MS-001 proves that MammothSkills can create curated Codex package artifacts,
manifests, static structure checks, contract cases, and a deferred runtime
validation plan. It is not a production release and does not authorize
Symphonie integration.

The three MS-001 skills `intake-brief`, `project-scoping`, and `project-status`
are not current candidates for operational use in Symphonie. In the current
conceptual Symphonie flow, these phases belong to the Claude/definition segment.
For MammothSkills they remain useful as a validation corpus.

```text
PIPELINE_PHASE_A = VALIDATED
CLASSIFICATION_GATE = PASS
RUNTIME_VALIDATION = DEFERRED / OPTIONAL_LAB_TEST
RELEASE_SYSTEM = NOT_YET_VALIDATED
CONSUMER_INTEGRATION = NOT_AUTHORIZED
```

### Symphonie

Symphonie is a consumer and coordinator of fixed approved releases. It is not
the canonical source of reusable skills.

```text
PRODUCT_CHANGE = NOT_AUTHORIZED
SKILL_INTEGRATION = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
```

## Authority

- Jonathan Martínez: sole approver.
- ChatGPT: coordinator, validator, auditor, and bounded-order issuer.
- Claude: discovery and definition only when explicitly assigned.
- Codex: bounded technical executor only.
- Codex autonomous authority: `NO`.

The technical executor never determines the target platform. A commit records
a transition but does not create approval.

## Decisions in force

- `DEC-LAB-001`: approve the LAB repository structure.
- `DEC-LAB-002`: use GitHub as the external laboratory memory.
- `DEC-LAB-003`: adopt the fixed continuity read protocol.
- `DEC-LAB-004`: freeze methodology v1.0 and use Git as structured memory.

## Open or contained errors

- `ERR-LAB-001`: executor confused with target platform — `CONTAINED`.
- `ERR-LAB-002`: overcomplicated correction — `CONTAINED`.

`ERR-TOOLING-001` is `CORRECTED`, not verified or closed.

## Validated patterns

- `PAT-LAB-001`: record events, not full transcripts.
- `PAT-LAB-002`: separate knowledge states.
- `PAT-LAB-003`: reconstruct context using a fixed reading order.
- `PAT-LAB-004`: bounded evidence-first audit.
- `PAT-MA-001`: Codex executes without autonomous authority.

## Authorization state

```text
lab_documentation = NOT_AUTHORIZED
mammothskills_implementation = NOT_AUTHORIZED
mammothskills_release = NOT_AUTHORIZED
symphonie_integration = NOT_AUTHORIZED
product_changes = NOT_AUTHORIZED
codex_autonomous_authority = NO
```

The current synchronization records the consumed documentation update. No
additional LAB documentation, implementation, release, product change, or
consumer integration is authorized by this state.

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
