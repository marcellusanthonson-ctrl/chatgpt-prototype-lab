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
- Codex may execute repository changes without becoming the target platform of
  the skill being changed.

## MS-001 objective

Audit and adapt the Claude skills:

- `intake-brief`
- `project-scoping`
- `project-status`

These remain Claude-targeted skills unless a separate, explicitly approved
adaptation for another platform is created.

## Verified progress

- `BASELINES_LOCKED = PASS`
- `SOURCES_LOCKED = PASS`
- `SPECS_APPROVED = PASS`
- immutable baselines and source fingerprints recorded;
- iterative Claude brief workflow and ChatGPT handoff governance specified;
- implementation and test planning were previously approved against an
  incorrect Codex target path.

## Current blocker

The target-platform decision was misclassified. The former architecture using
`targets/codex/` for the three Claude skills is superseded conceptually and must
not be implemented.

```text
TARGET_PLATFORM_CLASSIFICATION = REOPENED
PREVIOUS_CODEX_EXECUTION_ORDER = REVOKED
IMPLEMENTATION = NOT AUTHORIZED
CODEX = NOT AUTHORIZED
RELEASE = NOT AUTHORIZED
```

## Valid work retained

The following remain useful:

- imported immutable baselines;
- source licensing and provenance;
- fingerprints;
- approved behavioral specifications;
- handoff contracts;
- audit gates and test concepts;
- producer/release/consumer separation.

## Required correction

Before implementation, create and approve a superseding decision that:

1. classifies the three MS-001 skills as Claude-targeted;
2. replaces `targets/codex/` with the correct Claude target paths;
3. supersedes the previous fileset and execution order;
4. issues a new bounded implementation order only after remote verification.

## Next authorized action

Document and approve the target-platform correction. No implementation is
authorized by this state file.
