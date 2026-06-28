# MammothSkills — Project State

Project-ID: `mammothskills`
Status: `ACTIVE_WITH_BLOCKER`
Last-Updated: `2026-06-28`
Repository: `marcellusanthonson-ctrl/MammothSkills`
Working-Branch: `audit/ms-001`

## Purpose

Create, audit, adapt, test, version, and publish skills. MammothSkills is the
producer and source of truth for skill artifacts, not the runtime where they
live.

## Platform rule

- Skills for Claude live in Claude.
- Skills for Codex live in Codex.
- The technical executor does not determine the target platform.
- MammothSkills must not write directly into Symphonie.

## MS-001 objective

The following three skills are Claude-targeted:

- `intake-brief`
- `project-scoping`
- `project-status`

Codex editing a repository does not assign these skills to Codex.

## Preserved gate states

```text
BASELINES_LOCKED = PASS
SOURCES_LOCKED = PASS
SPECS_APPROVED = PASS
TARGET_PLATFORM_CLASSIFICATION = REOPENED
PREVIOUS_CODEX_EXECUTION_ORDER = REVOKED
IMPLEMENTATION = NOT_AUTHORIZED
CODEX = NOT_AUTHORIZED
RELEASE = NOT_AUTHORIZED
```

## Current blocker

The former `targets/codex/` classification for these Claude skills is invalid
and revoked. A target-platform correction requires a separate approved
decision before any replacement implementation order may exist.

## Valid work retained

- immutable baselines and source fingerprints;
- source licensing and provenance;
- approved behavioral specifications and handoff contracts;
- audit gates and test concepts;
- producer, release, runtime, and consumer separation.

## Authorization

Implementation, Codex execution, and release are not authorized. This LAB
documentation order does not modify the MammothSkills repository and does not
create target paths or a replacement implementation order.

## Next authorized action

Document and approve the target-platform correction under a separate bounded
order. No implementation is authorized by this state file.
