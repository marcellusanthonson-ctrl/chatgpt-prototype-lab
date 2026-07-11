# Symphonie — Project State

Project-ID: `symphonie`
Status: `KNOWN_AND_SYNCED`
Last-Updated: `2026-07-11`
Repository: `marcellusanthonson-ctrl/symphonie-codex-lab`

## Role

Symphonie is an eight-phase workflow for creating applications and websites. It
coordinates project-specific work across ChatGPT, Claude, and Codex. It is not
the canonical source of reusable skills.

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

Canonical decision: `DEC-LAB-005`.

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
MAMMOTHSKILLS_RELEASE = NOT_AUTHORIZED
```

The approved structural relationship does not itself authorize creation,
adaptation, release, installation, repository changes, or integration.

MS-001 remains a MammothSkills validation corpus and is not a current
operational candidate for Symphonie.

## Next authorized action

No product or skill integration action is authorized. A future skill request
must first declare its Symphonie phase, runtime agent, input/output contract,
and validation criteria, followed by separate bounded authorizations for
creation or adaptation and consumption.
