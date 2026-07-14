# Symphonie — Project State

Project-ID: `symphonie`
Status: `KNOWN_AND_SYNCED`
Last-Updated: `2026-07-14`
Repository: `marcellusanthonson-ctrl/symphonie-codex-lab`

## Role

Symphonie is an eight-phase workflow that creates and develops applications and websites from beginning to end. It coordinates project-specific work across ChatGPT, Claude, and Codex. Skills are instruments used by particular phases; they are not the purpose of Symphonie and Symphonie is not the canonical source of reusable skills.

## Operating model

- Jonathan Martínez approves.
- ChatGPT coordinates, validates, audits, and issues bounded orders.
- Claude performs explicitly assigned discovery and definition phases.
- Codex performs bounded technical execution without autonomous authority.

## Structural relationship with MammothSkills

Symphonie and MammothSkills remain independent projects, but may establish an explicit producer-consumer relationship when a Symphonie phase requires a skill.

Symphonie may provide MammothSkills with phase, runtime-agent, input/output, compatibility, handoff, example, failure-case, and consumer-validation requirements. MammothSkills may then create or adapt a skill for the declared target platform.

```text
Symphonie -> requirements and feedback -> MammothSkills
MammothSkills -> approved skill artifact/release -> Symphonie
Runtime -> Claude or Codex according to target_platform
```

Direct consumption must preserve artifact identity, target platform, version or artifact ID, source commit, checksum when applicable, configuration, and validation evidence. MammothSkills must not autonomously modify the Symphonie repository.

Canonical decisions: `DEC-LAB-005`, `DEC-LAB-006`.

## Claude-operated early phases

The MammothSkills corpus currently includes:

- `intake-brief`;
- `project-scoping`;
- `project-status`.

These are not yet registered as installed operational Symphonie releases. Before assignment to Claude-operated phases, they require audit in MammothSkills, Claude runtime validation, versioned identity, explicit approval, and separate Symphonie integration.

## Historical Codex skill candidates

The following two Codex skills were created or adapted inside `symphonie-codex-lab` before MammothSkills existed:

- `symphonie-ux-ui-architect`;
- `symphonie-ui-implementer`.

```text
Phase 3A: symphonie-ux-ui-architect
Capability: DOCUMENT_WRITE
Purpose: define and write approved design contracts

Phase 4A: symphonie-ui-implementer
Capability: SOURCE_WRITE
Purpose: convert approved Phase 3A contracts into authorized UI source code
```

## Current skill validation state

### `symphonie-ux-ui-architect 0.1.0-alpha.5`

```text
STATUS = APPROVED_BASELINE_CLOSED_IMMUTABLE
STATIC_VALIDATION = PASS
RUNTIME_VALIDATION = PASS
PROMOTION_GATE = PASS
```

This baseline is closed and immutable.

### `symphonie-ui-implementer 0.1.0-alpha.3`

```text
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

Technical validation and human promotion are complete. This baseline is closed and immutable. Any future functional change requires a new version, new validation evidence, and a new explicit human approval.

The promotion does not authorize release, installation, migration to MammothSkills, or integration into Symphonie.

## Validated synthetic architect-to-implementer handoff

Project: `handoff-controlled-017`

```text
RESULT = PASS_WITH_FINDINGS
HANDOFF_COMPATIBILITY = PASS
CODEX_DISCOVERY_AND_INTERPRETATION_AS_CHAIN = PASS
REAL_DESIGN_EXECUTION = NOT_YET_VALIDATED
REPEATABILITY = NOT_YET_VALIDATED
CLOSED_AT = 2026-07-12
```

Orders included in the validated chain:

- `SYM-ARCH-IMPLEMENTER-HANDOFF-017`
- `SYM-ARCH-IMPLEMENTER-HANDOFF-018`
- `SYM-ARCH-IMPLEMENTER-HANDOFF-019`
- `SYM-ARCH-IMPLEMENTER-HANDOFF-RUNTIME-020`
- `SYM-ARCH-IMPLEMENTER-HANDOFF-MANUAL-VALIDATION-021`

The chain validated:

1. discovery and interpretation of both approved Codex skills;
2. Phase 3A generation of the canonical design contracts;
3. preservation of the human `DESIGN_DIRECTION_APPROVED` gate;
4. Phase 4A consumption of the four canonical JSON contracts;
5. bounded application-source generation;
6. successful TypeScript and Vite build;
7. real browser rendering;
8. console, six-viewport responsive, keyboard, focus, accessibility-basic, action-preservation, Phase 3A conformance, and boundary validation.

Historical blockers and corrections remain part of the evidence:

- The first build was blocked because the synthetic fixture lacked Vite CSS Module declarations.
- A separately authorized `src/vite-env.d.ts` correction resolved the build blocker.
- Automated browser validation was blocked because the Playwright Chromium executable was absent and browser installation was prohibited.
- Manual-assisted validation completed the remaining evidence and closed the synthetic handoff as `PASS_WITH_FINDINGS`.

Non-blocking findings:

- missing `favicon.ico` caused a local `404`;
- approved fixture labels `Prepared, not executed` and `Not yet executed` became semantically stale after the experiment was completed.

The synthetic result does not establish real-design execution, reproducibility, production readiness, release, migration, or integration.

## Canonical minimal handoff knowledge

The LAB now records three verified, generic knowledge documents:

- `knowledge/contracts/phase3-minimum-assertions.json`;
- `knowledge/contracts/action-preservation.json`;
- `knowledge/regressions/imp-reg-11.json`.

```text
SOURCE_AUDIT = SYM-LOCAL-EVIDENCE-AUDIT-005 / PASS_WITH_FINDINGS / CONSUMED
SOURCE_EXTRACTION = SYM-MINIMAL-KNOWLEDGE-EXTRACTION-006 / PASS / CONSUMED
CANONICALIZATION = SYM-LAB-CANONICALIZATION-007 / PASS / CONSUMED
PUBLICATION = SYM-LAB-PUSH-008 / PASS / CONSUMED
PUBLICATION_COMMIT = c478c5a4e290a10305e64c9ff8bf6eff4ead772a
MINIMAL_HANDOFF_KNOWLEDGE = CANONICALIZED_AND_PUBLISHED
VALIDATION = PASS
```

The documents add:

1. minimum, verifiable Phase 3A exit assertions for semantic order, declared responsive width, visible keyboard focus, text-labelled status, and reduced motion;
2. an action-preservation contract that prevents deletion, invention, or simulation of unauthorized behavior during the Phase 3A to Phase 4A handoff;
3. an `IMP_REG_11` fail-closed guard requiring authorization contradictions to be detected before any observable write or effect.

Operational boundary:

```text
CANONICAL_KNOWLEDGE = YES
AUTOMATIC_ENFORCEMENT = NOT_IMPLEMENTED
SKILL_MODIFICATION = NOT_PERFORMED
SYMPHONIE_RUNTIME_INTEGRATION = NOT_AUTHORIZED
PRODUCT_CHANGE = NOT_PERFORMED
```

The local audit also established that the exported UI implementer variant was superseded and that `SYMPHONIE_RECOVERY_QUARANTINE` remained unverified; neither was incorporated.

## Immediate operational sequence

The next recommended transition is:

```text
1. Plan a real-design execution through the validated chained flow
2. Apply the canonical minimal handoff knowledge as explicit test criteria
3. Obtain explicit bounded authorization for the real-design test
4. Execute and assess the real design
5. Repeat the flow to prove reproducibility
6. Only then consider migration to MammothSkills under separate authorization
```

Each transition requires its own explicit bounded authorization where it involves execution, repository writing, release, migration, or integration.

## Initial Symphonie Codex skill cycle

Current completion state:

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

## Post-validation migration strategy

After the initial Symphonie Codex skill cycle is closed, reusable assets and process knowledge may be migrated or extracted into MammothSkills under separate authorization.

MammothSkills may receive canonical skill sources, generic schemas, templates, validators, reusable regression cases, audit and adaptation methods, snapshot techniques, report parsing, fail-closed validation patterns, versioning, checksums, changelogs, and source provenance.

Symphonie retains phase placement, activation rules, phase-specific contracts, handoff requirements, workflow fixtures, installed release identity, configuration, consumer-fit evidence, and integration evidence.

Historical copies must not be silently deleted. After canonical migration they must be marked `legacy`, `superseded`, or `evidence-only` as appropriate.

## Skill relationship

- Skills for Claude live in Claude.
- Skills for Codex live in Codex.
- MammothSkills produces and maintains canonical reusable skill artifacts.
- Symphonie specifies consumer requirements and validates consumer fit.
- Consumer feedback may result in a new MammothSkills revision.
- Technical adaptability, runtime compatibility, promotion, release, and Symphonie consumer fit are separate validations and permissions.

## Authorization state

```text
PRODUCT_CHANGE = NOT_AUTHORIZED
REAL_DESIGN_EXECUTION = NOT_AUTHORIZED
REPEATABILITY_TEST = NOT_AUTHORIZED
SKILL_INTEGRATION = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
MAMMOTHSKILLS_MIGRATION = NOT_AUTHORIZED
MAMMOTHSKILLS_RELEASE = NOT_AUTHORIZED
```

This update records the completed audit, extraction, canonicalization, and publication of minimal Symphonie handoff knowledge. It does not authorize real-design execution, repeatability testing, release, installation, repository changes outside LAB, migration, runtime integration, or product changes.

## Next authorized action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`

Recommended transition:

`PLAN_AND_EXPLICITLY_AUTHORIZE_REAL_DESIGN_EXECUTION_THROUGH_VALIDATED_HANDOFF_USING_CANONICAL_MINIMAL_KNOWLEDGE`
