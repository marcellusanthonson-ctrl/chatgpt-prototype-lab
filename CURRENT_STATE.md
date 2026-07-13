# LAB Current State

Document-ID: `lab.current-state`
Version: `1.0.6`
Status: `ACTIVE`
Last-Updated: `2026-07-12`

`CURRENT_STATE.json` is the structured source of truth. This file is its human-readable view.

## Active project and phase

- Active project: `lab`
- Current phase: `KNOWLEDGE_BASE_OPERATIONAL_V1`
- Methodology: version `1.0.0`, status `APPROVED`
- Canonical methodology: `METHODOLOGY.md`

LAB is active and its knowledge base is operational. The approved methodology remains frozen and in force until an explicitly approved decision supersedes it.

## Project boundaries

### LAB

LAB is the starting laboratory for viability, feasibility, risk analysis, experiments, integrations, and project initiation. It preserves validated cross-project knowledge and does not contain or authorize product execution.

### MammothSkills

MammothSkills creates, adapts, audits, tests, repairs, versions, and publishes skills for declared agent platforms and consumer contracts.

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

Their future use in Claude-operated Symphonie phases requires audit, Claude runtime validation, an identified release, explicit approval, and separate consumer-integration authorization.

### Symphonie

Symphonie is an eight-phase workflow that creates and develops applications and websites from beginning to end. It coordinates project-specific work across ChatGPT, Claude, and Codex. Skills are instruments used by particular phases; they are not the purpose of Symphonie.

Current operational objective:

```text
Plan and explicitly authorize a real-design execution through the validated
architect-to-implementer chain, then repeat the flow before any separately
authorized migration to MammothSkills.
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

This skill defines and writes the approved Phase 3A design documents. It does not write application source code.

### `symphonie-ui-implementer`

```text
VERSION = 0.1.0-alpha.3
PHASE = 4A
CAPABILITY = SOURCE_WRITE
STATUS = APPROVED_BASELINE_CLOSED_IMMUTABLE
STATIC_VALIDATION = PASS
RUNTIME_SUITE = IMP-REG-01 THROUGH IMP-REG-12
RUNTIME_VALIDATION = PASS
BASELINE_HEAD = c2f3159e754d356f23b6855f2aecf1a663209835
PROMOTION_REVIEW = SYM-UI-IMPLEMENTER-PROMOTION-REVIEW-013
PROMOTION_RECORD_ORDER = SYM-UI-IMPLEMENTER-PROMOTION-RECORD-014
PROMOTION_RECORD_COMMIT = 8f319aef3f328d22376fde42b4b0003601ffa670
HUMAN_APPROVAL = GRANTED
PROMOTION_GATE = PASS
RELEASE = NOT_AUTHORIZED
MIGRATION = NOT_AUTHORIZED
INTEGRATION = NOT_AUTHORIZED
```

The implementer baseline is approved, closed, and immutable. Any future functional change requires a new version, new validation evidence, and a new explicit human approval. This approval does not authorize release, installation, migration, or Symphonie integration.

## Initial Symphonie Codex skill cycle

The two historical candidates were created or adapted inside `symphonie-codex-lab` before MammothSkills existed. Their isolated audit and runtime validation remain preserved there.

```text
SKILL_1_RUNTIME = PASS
SKILL_1_PROMOTION = APPROVED_BASELINE_CLOSED_IMMUTABLE
SKILL_2_RUNTIME = PASS
SKILL_2_PROMOTION = APPROVED_BASELINE_CLOSED_IMMUTABLE
HANDOFF_COMPATIBILITY = PASS
CODEX_DISCOVERY_AND_INTERPRETATION_AS_CHAIN = PASS
REAL_DESIGN_EXECUTION = NOT_YET_VALIDATED
REPEATABILITY = NOT_YET_VALIDATED
```

## Validated synthetic handoff

Project: `handoff-controlled-017`

Terminal result:

```text
RESULT = PASS_WITH_FINDINGS
VALIDATED_CHAIN = architect -> human gate -> implementer -> build -> manual browser validation
CLOSED_AT = 2026-07-12
```

Orders recorded:

- `SYM-ARCH-IMPLEMENTER-HANDOFF-017`
- `SYM-ARCH-IMPLEMENTER-HANDOFF-018`
- `SYM-ARCH-IMPLEMENTER-HANDOFF-019`
- `SYM-ARCH-IMPLEMENTER-HANDOFF-RUNTIME-020`
- `SYM-ARCH-IMPLEMENTER-HANDOFF-MANUAL-VALIDATION-021`

The validated sequence established that Codex could discover and interpret both approved skills as a chain, produce the Phase 3A contracts, preserve the human approval gate, consume the canonical JSON contracts in Phase 4A, produce bounded source changes, build successfully, render in a browser, preserve unresolved actions, and pass the required responsive, keyboard, focus, accessibility-basic, Phase 3A conformance, and boundary checks.

The complete history remains material:

1. Phase 3A produced the approved `Evidence rail` design contracts.
2. Phase 4A consumed the four canonical JSON contracts and changed only the authorized application files.
3. The first build attempt was blocked because the synthetic fixture lacked Vite CSS Module declarations.
4. A separately authorized `src/vite-env.d.ts` correction resolved that build blocker.
5. Automated browser validation was blocked because the Playwright Chromium executable was unavailable and installation was prohibited.
6. Manual-assisted validation completed the remaining browser evidence and closed the synthetic handoff as `PASS_WITH_FINDINGS`.

Non-blocking findings:

- `favicon.ico` returned a local `404` without affecting the fixture.
- Contract-faithful `Prepared, not executed` and `Not yet executed` labels became semantically stale after experiment completion.

This validation is synthetic. It does not establish real-design execution, repeatability, production readiness, release, migration, or integration.

## Remaining sequence

```text
1. Plan a real-design execution through the validated chained flow
2. Obtain explicit bounded authorization
3. Execute and assess the real design
4. Repeat the flow to prove reproducibility
5. Only then consider migration to MammothSkills under separate authorization
```

## Approved structural relationship model

Independent projects may establish explicit structural relationships when a workflow requires them. Project independence does not mean absence of interaction.

Canonical decisions: `DEC-LAB-005`, `DEC-LAB-006`.

```text
Symphonie -> requirements and feedback -> MammothSkills
MammothSkills -> approved skill artifact/release -> Symphonie
Skill runtime -> Claude or Codex according to target_platform
```

Symphonie may consume an approved skill directly from MammothSkills only as an identified artifact or release with target platform, source commit, version or artifact ID, checksum when applicable, configuration, and validation evidence. Technical adaptation, runtime compatibility, consumer fit, release, and integration remain separate validations and permissions.

## Post-validation migration strategy

After the initial Symphonie Codex skill cycle is closed, reusable skill assets, generic tests, audit methods, adaptation methods, and regression techniques may be migrated or extracted into MammothSkills under separate authorization.

Symphonie retains phase placement, input/output contracts, handoff rules, consumer-specific fixtures, installed release identity, and integration evidence. Historical copies must be marked `legacy`, `superseded`, or `evidence-only`; they must not be silently deleted.

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
- `DEC-LAB-005`: permit explicit structural producer-consumer relationships between independent projects.
- `DEC-LAB-006`: complete the initial Symphonie Codex skill cycle before canonical migration to MammothSkills.

## Open or contained errors

- `ERR-LAB-001`: executor confused with target platform — `CONTAINED`.
- `ERR-LAB-002`: overcomplicated correction — `CONTAINED`.

`ERR-TOOLING-001` is `CORRECTED`, not verified or closed.

## Validated patterns

- `PAT-LAB-001`: Record events, not full transcripts.
- `PAT-LAB-002`: Separate observation, hypothesis, validation, approval, and resolution.
- `PAT-LAB-003`: Reconstruct context using a fixed reading order.
- `PAT-LAB-004`: Bounded evidence-first audit.
- `PAT-MA-001`: Codex executes without autonomous authority.

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

This documentation records the completed synthetic handoff validation. It does not authorize real-design execution, repeatability testing, runtime, release, installation, migration, integration, product change, or repository modification outside LAB.

## Next authorized action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`

Recommended transition:

`PLAN_AND_EXPLICITLY_AUTHORIZE_REAL_DESIGN_EXECUTION_THROUGH_VALIDATED_HANDOFF`

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
