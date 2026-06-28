# Symphonie — Project State

Project-ID: `symphonie`
Status: `KNOWN_AND_SYNCED`
Last-Updated: `2026-06-28`
Repository: `marcellusanthonson-ctrl/symphonie-codex-lab`

## Role

Symphonie is a consumer and coordinator. It consumes fixed approved skill
releases and coordinates project-specific work across ChatGPT, Claude, and
Codex. It is not the canonical source of reusable skills.

## Operating model

- Jonathan Martínez approves.
- ChatGPT coordinates, validates, audits, and issues bounded orders.
- Claude performs explicitly assigned discovery and definition.
- Codex performs bounded technical execution without autonomous authority.

## Skill relationship

- Skills for Claude live in Claude.
- Skills for Codex live in Codex.
- MammothSkills produces and publishes versioned releases.
- Symphonie records the consumed version, source commit, checksum,
  configuration, and integration evidence.
- MammothSkills must not write directly into Symphonie.
- Symphonie must not depend live on a mutable MammothSkills working tree.

## Authorization state

```text
PRODUCT_CHANGE = NOT_AUTHORIZED
SKILL_INTEGRATION = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
```

The MS-001 target-platform error does not authorize installation, migration,
or product change in Symphonie. This LAB order does not modify the Symphonie
repository.

## Next authorized action

No product action is authorized. Future integration requires a validated fixed
release and a separate direct, explicit, bounded order.
