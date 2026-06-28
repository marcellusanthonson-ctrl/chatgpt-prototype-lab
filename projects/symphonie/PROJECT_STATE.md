# Symphonie — Project State

Project-ID: `symphonie`
Status: `KNOWN_AND_SYNCED`
Last-Updated: `2026-06-28`
Repository: `marcellusanthonson-ctrl/symphonie-codex-lab`

## Purpose

Consume fixed, approved skill releases and coordinate project-specific work
across ChatGPT, Claude, and Codex.

## Operating model

- Jonathan Martínez approves.
- ChatGPT coordinates, validates, audits, and issues bounded orders.
- Claude performs discovery and definition through Claude-native skills.
- Codex performs bounded technical execution through Codex-native skills or
  explicit project instructions.

## Skill rule

- Skills for Claude live in Claude.
- Skills for Codex live in Codex.
- Symphonie consumes a fixed release; it is not the canonical source of the
  reusable skill.
- Every installed skill should record version, source commit, checksum,
  integration mode, and project-specific configuration.
- MammothSkills must not write directly into Symphonie.

## Repository relationship

```text
MammothSkills produces and publishes
-> ChatGPT validates compatibility and authorizes integration
-> Codex or the appropriate platform installs the fixed release
-> Symphonie records the exact consumed version
```

No project may depend live on a mutable MammothSkills working tree.

## Current state

Symphonie remains a consumer and coordinator. The MS-001 target-platform error
in MammothSkills does not authorize any installation or migration in Symphonie.

```text
PRODUCT_CHANGE = NOT AUTHORIZED
SKILL_INTEGRATION = NOT AUTHORIZED
CODEX_EXECUTION = NOT AUTHORIZED
```

## Next authorized action

No product action is authorized by this knowledge record. A future integration
requires a validated release and a separate explicit order.
