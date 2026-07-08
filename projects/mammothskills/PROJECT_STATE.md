# MammothSkills — Project State

Project-ID: `mammothskills`
Status: `ACTIVE_PIPELINE_VALIDATED_PHASE_A`
Last-Updated: `2026-07-07`
Repository: `marcellusanthonson-ctrl/MammothSkills`
Working-Branch: `audit/ms-001`
Current-HEAD: `034910e9fec4c0f0b97fe06ee94554bda289a1b6`

## Purpose

Create, audit, adapt, test, version, and publish skills. MammothSkills is the
producer and source of truth for skill artifacts, not the runtime where they
live.

## Platform rule

- Skills for Claude live in Claude.
- Skills for Codex live in Codex.
- The technical executor does not determine the target platform.
- MammothSkills must not write directly into Symphonie or any other consumer.
- Consumers may use only fixed approved releases through separate explicit
  integration orders.

## Current operational state

MammothSkills has validated its phase-A adaptation/audit pipeline using MS-001
as a controlled validation corpus.

```text
PIPELINE_PHASE_A = VALIDATED
CLASSIFICATION_GATE = PASS
RUNTIME_VALIDATION = DEFERRED_TO_NEXT_SESSION
RELEASE_SYSTEM = NOT_YET_VALIDATED
CONSUMER_INTEGRATION = NOT_AUTHORIZED
```

## MS-001 classification

MS-001 is classified as `MAMMOTHSKILLS_PIPELINE_VALIDATION`.

The following skills were used as a validation corpus:

- `intake-brief`
- `project-scoping`
- `project-status`

The Codex packages created under `targets/codex/**` in the MammothSkills repo
are test artifacts. They are not operational releases and are not approved for
Symphonie integration.

```text
MS_001_PURPOSE = MAMMOTHSKILLS_PIPELINE_VALIDATION
SOURCE_PLATFORM = Claude
TARGET_PLATFORM_TEST = Codex
CODEX_ADAPTATION = TEST_ARTIFACT
SYMPHONIE_OPERATIONAL_USE = NOT_APPLICABLE_NOW
SYMPHONIE_INTEGRATION = NOT_AUTHORIZED
RELEASE = NOT_AUTHORIZED
```

## Evidence

Phase-A implementation evidence:

```text
55f66f4d9020ca93113aef61194141efdc3688cc
```

Classification documentation evidence:

```text
034910e9fec4c0f0b97fe06ee94554bda289a1b6
```

MS-001 proves that MammothSkills can:

- preserve baseline/source/spec separation;
- create curated Codex package artifacts;
- create `SKILL.md` files;
- create `ADAPTATION_MANIFEST.json` files;
- create structural and contractual tests;
- document deferred runtime validation;
- distinguish technical adaptability from consumer fit.

## Current blockers and limits

There is no blocker against using MS-001 as MammothSkills pipeline evidence.

Remaining incomplete capabilities:

- real runtime validation in a fresh Codex session;
- a release/versioning workflow with checksums;
- installation from a fixed release artifact;
- a future MS-002 or equivalent skill that is a real operational candidate for
  Codex use.

The following remain not authorized:

```text
MAMMOTHSKILLS_RELEASE = NOT_AUTHORIZED
SYMPHONIE_INTEGRATION = NOT_AUTHORIZED
PRODUCT_CHANGE = NOT_AUTHORIZED
CODEX_AUTONOMOUS_AUTHORITY = NO
```

## Valid work retained

- immutable baselines and source fingerprints;
- source licensing and provenance;
- approved behavioral specifications and handoff contracts;
- audit gates and test concepts;
- producer, release, runtime, and consumer separation;
- MS-001 package/test/classification evidence.

## Authorization

This state file records the consumed synchronization. It does not authorize new
implementation, runtime validation, release, merge, product change, or consumer
integration.

## Next authorized action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`

Recommended future actions, each requiring a separate explicit order:

1. optional runtime validation of MS-001 as lab evidence;
2. MS-002 with a skill that is a real Codex operational candidate;
3. release workflow design and checksum validation.
