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
This includes adapting an existing Claude skill for more precise results in a
Claude-operated Symphonie phase, or creating/adapting a skill for a Codex phase.

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

## Historical Codex skill candidates

The following two Codex skill candidates were created or adapted inside
`symphonie-codex-lab` before MammothSkills existed:

- `symphonie-ux-ui-architect`;
- `symphonie-ui-implementer`.

They are candidates for two Codex-operated phases of the Symphonie workflow.
Their current audit and runtime validation will be completed in
`symphonie-codex-lab` to preserve source history, fixtures, regression evidence,
and continuity.

The immediate operational objective is to prove that Codex can:

1. discover and interpret both skills;
2. execute each skill under its phase contract;
3. produce the required design artifacts;
4. hand those artifacts from the architecture phase to the implementation phase;
5. create a real design through the Symphonie workflow;
6. repeat the flow with reproducible results.

Completion criteria:

```text
SKILL_1_RUNTIME = PASS
SKILL_2_RUNTIME = PASS
HANDOFF_COMPATIBILITY = PASS
CODEX_DISCOVERY_AND_INTERPRETATION = PASS
REAL_DESIGN_EXECUTION = PASS
REPEATABILITY = PASS
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
- Technical adaptability, runtime compatibility, and Symphonie consumer fit are
  separate validations.

## Authorization state

```text
PRODUCT_CHANGE = NOT_AUTHORIZED
SKILL_INTEGRATION = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
MAMMOTHSKILLS_MIGRATION = NOT_AUTHORIZED
MAMMOTHSKILLS_RELEASE = NOT_AUTHORIZED
```

The approved structural relationship and migration sequence do not themselves
authorize runtime execution, creation, adaptation, release, installation,
repository changes outside LAB, or integration.

MS-001 remains a MammothSkills validation corpus and is not a current
operational candidate for Symphonie.

## Next authorized action

No runtime, migration, release, product, or skill-integration action is
authorized by this documentation update. Each transition requires a new,
explicit, bounded authorization.
