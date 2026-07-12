# Symphonie — Project State

Project-ID: `symphonie`
Status: `KNOWN_AND_SYNCED`
Last-Updated: `2026-07-11`
Repository: `marcellusanthonson-ctrl/symphonie-codex-lab`

## Role

Symphonie is an eight-phase workflow that creates and develops applications and
websites from beginning to end. It coordinates project-specific work across
ChatGPT, Claude, and Codex. Skills are instruments used by particular phases;
they are not the purpose of Symphonie and Symphonie is not the canonical source
of reusable skills.

## Operating model

- Jonathan Martínez approves.
- ChatGPT coordinates, validates, audits, and issues bounded orders.
- Claude performs explicitly assigned discovery and definition phases.
- Codex performs bounded technical execution without autonomous authority.

## Structural relationship with MammothSkills

Symphonie and MammothSkills remain independent projects, but may establish an
explicit producer-consumer relationship when a Symphonie phase requires a
skill.

Symphonie may provide MammothSkills with:

- the target phase;
- the runtime agent, Claude or Codex;
- the available inputs;
- the required output structure;
- compatibility and handoff requirements;
- examples and failure cases;
- consumer-specific validation feedback.

MammothSkills may then create or adapt a skill for the declared target platform.
This includes adapting an existing Claude skill for a Claude-operated Symphonie
phase, or creating/adapting a skill for a Codex phase.

```text
Symphonie -> requirements and feedback -> MammothSkills
MammothSkills -> approved skill artifact/release -> Symphonie
Runtime -> Claude or Codex according to target_platform
```

Symphonie may consume the approved skill directly from MammothSkills as the
canonical skill source. Direct consumption must preserve artifact identity,
version or artifact ID, target platform, source commit, checksum when
applicable, configuration, and validation evidence.

Symphonie must not rely on an untracked copy or an unidentified mutable working
tree. MammothSkills must not autonomously modify the Symphonie repository.

Canonical decisions: `DEC-LAB-005`, `DEC-LAB-006`.

## Claude-operated early phases

The MammothSkills corpus currently includes:

- `intake-brief`;
- `project-scoping`;
- `project-status`.

These are not yet registered as installed operational Symphonie releases. Before
they can be assigned to Claude-operated Intake, Briefing, Scoping, or status
phases, their current state must be audited in MammothSkills, validated in the
Claude runtime, versioned and identified, explicitly approved, and separately
integrated into Symphonie.

## Historical Codex skill candidates

The following two Codex skill candidates were created or adapted inside
`symphonie-codex-lab` before MammothSkills existed:

- `symphonie-ux-ui-architect`;
- `symphonie-ui-implementer`.

They cover different Codex-operated phases:

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

This baseline is already closed. Its next useful validation is not another
isolated regression run, but participation in the real architect-to-implementer
handoff.

### `symphonie-ui-implementer 0.1.0-alpha.3`

```text
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

The completed runtime order reported:

- `IMP-REG-01` through `IMP-REG-12`: `PASS`;
- identical HEAD before and after;
- no tracked repository source changes;
- no Git configuration change;
- no commit, push, pull request, MammothSkills write, migration, or integration.

The prepared `IMP-REG-07` fixture contained only its authorized fixture copies
of `src/components/TicketBoard.tsx` and `src/components/TicketRow.tsx`; these
were not tracked source changes in the main repository.

Technical validation is complete, but promotion has not been approved. Runtime
success does not itself create an approved baseline.

## Immediate operational sequence

The next recommended transition is:

```text
1. Consolidate and review promotion evidence for
   symphonie-ui-implementer 0.1.0-alpha.3
2. Obtain an explicit approval or rejection from Jonathan Martínez
3. If approved, record alpha.3 as a closed immutable baseline
4. Validate architect -> Phase 3A contracts -> implementer handoff
5. Execute a real design through the chained flow
6. Repeat the flow to prove reproducibility
```

Each numbered transition requires its own explicit bounded authorization where
it involves execution, repository writing, promotion, release, migration, or
integration.

## Initial Symphonie Codex skill cycle

The immediate operational objective is to prove that Codex can:

1. discover and interpret both skills;
2. execute each skill under its phase contract;
3. produce the required design artifacts;
4. hand those artifacts from the architecture phase to the implementation phase;
5. create a real design through the Symphonie workflow;
6. repeat the flow with reproducible results.

Current completion state:

```text
SKILL_1_RUNTIME = PASS
SKILL_2_RUNTIME = PASS
HANDOFF_COMPATIBILITY = NOT_YET_VALIDATED
CODEX_DISCOVERY_AND_INTERPRETATION_AS_CHAIN = NOT_YET_VALIDATED
REAL_DESIGN_EXECUTION = NOT_YET_VALIDATED
REPEATABILITY = NOT_YET_VALIDATED
```

## Post-validation migration strategy

After the initial Symphonie Codex skill cycle is closed, reusable assets and
process knowledge may be migrated or extracted into MammothSkills under separate
authorization.

MammothSkills may receive:

- canonical skill sources;
- generic schemas, templates, and validators;
- reusable regression cases;
- audit and adaptation methods;
- Git and non-Git snapshot techniques;
- report parsing and fail-closed validation patterns;
- version, checksum, changelog, and source provenance.

Symphonie will retain:

- phase placement and activation rules;
- phase-specific input and output contracts;
- handoff requirements;
- workflow-specific fixtures and expected results;
- installed release identity and configuration;
- consumer-fit and integration evidence.

Historical copies must not be silently deleted. After canonical migration they
must be marked `legacy`, `superseded`, or `evidence-only` as appropriate.

Future skill flow:

```text
Symphonie declares phase requirements
-> MammothSkills creates or adapts
-> MammothSkills audits, tests, versions, and publishes
-> Jonathan approves the release
-> Symphonie consumes a fixed identified release
-> Symphonie validates consumer fit inside the workflow
```

## Skill relationship

- Skills for Claude live in Claude.
- Skills for Codex live in Codex.
- MammothSkills produces and maintains canonical skill artifacts.
- Symphonie specifies consumer requirements and validates consumer fit.
- Consumer feedback may result in a new MammothSkills revision.
- Technical adaptability, runtime compatibility, promotion, release, and
  Symphonie consumer fit are separate validations and permissions.

## Authorization state

```text
PRODUCT_CHANGE = NOT_AUTHORIZED
SKILL_PROMOTION = NOT_AUTHORIZED
SKILL_INTEGRATION = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
MAMMOTHSKILLS_MIGRATION = NOT_AUTHORIZED
MAMMOTHSKILLS_RELEASE = NOT_AUTHORIZED
```

This update records validated runtime evidence and the recommended sequence. It
does not authorize promotion, runtime execution, creation, adaptation, release,
installation, repository changes outside LAB, migration, or integration.

## Next authorized action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`

Recommended transition:

`REVIEW_AND_EXPLICITLY_APPROVE_OR_REJECT_PROMOTION_OF_SYMPHONIE_UI_IMPLEMENTER_0.1.0_ALPHA.3`
