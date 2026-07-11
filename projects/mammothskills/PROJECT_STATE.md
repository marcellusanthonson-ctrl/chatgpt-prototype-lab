# MammothSkills — Project State

Project-ID: `mammothskills`
Status: `ACTIVE_PIPELINE_VALIDATED_PHASE_A`
Last-Updated: `2026-07-11`
Repository: `marcellusanthonson-ctrl/MammothSkills`
Working-Branch: `audit/ms-001`
Current-HEAD: `034910e9fec4c0f0b97fe06ee94554bda289a1b6`

## Purpose

Create, audit, adapt, test, repair, version, and publish skills for declared
agent platforms and consumer contracts. MammothSkills is the producer and
canonical source of skill artifacts, not the runtime where they live.

## Platform rule

- Skills for Claude live in Claude.
- Skills for Codex live in Codex.
- The technical executor does not determine the target platform.
- MammothSkills may create native skills or adapt existing skills for Claude or
  Codex according to the declared use case.
- MammothSkills must not autonomously write into a consumer repository.

## Consumer-driven intake

Before creating or adapting a skill, MammothSkills must establish:

```text
INTENDED_USE
CONSUMER_PROJECT
CONSUMER_PHASE
RUNTIME_AGENT
SOURCE_PLATFORM
TARGET_PLATFORM
INPUT_CONTRACT
OUTPUT_CONTRACT
CONSTRAINTS
VALIDATION_CRITERIA
```

A consumer may provide phase-specific requirements, examples, schemas,
compatibility constraints, expected handoffs, and integration feedback.

## Structural relationship with Symphonie

MammothSkills and Symphonie remain independent projects, but may operate through
an explicit producer-consumer relationship.

```text
Symphonie -> requirements and feedback -> MammothSkills
MammothSkills -> identified skill artifact/release -> Symphonie
Skill runtime -> Claude or Codex according to target_platform
```

When a skill is intended for Symphonie, MammothSkills may require details about:

- the Symphonie phase where it will be used;
- whether Claude or Codex will execute it;
- the inputs available to that phase;
- the exact output and handoff required by the next phase;
- consumer-specific quality and compatibility criteria.

Symphonie may consume the resulting approved skill directly from MammothSkills
as its canonical source. Direct consumption does not mean an untracked copy,
live dependency on a mutable working tree, or autonomous writes by MammothSkills
into Symphonie.

The consumed artifact must remain identifiable by version or artifact ID,
target platform, source commit, checksum when applicable, configuration, and
validation evidence.

Canonical decision: `DEC-LAB-005`.

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

- real runtime validation in a fresh target-agent session;
- a release/versioning workflow with checksums;
- installation or consumption from a fixed artifact;
- a future skill with a real operational consumer contract.

The following remain not authorized:

```text
MAMMOTHSKILLS_IMPLEMENTATION = NOT_AUTHORIZED
MAMMOTHSKILLS_RELEASE = NOT_AUTHORIZED
SYMPHONIE_INTEGRATION = NOT_AUTHORIZED
PRODUCT_CHANGE = NOT_AUTHORIZED
CODEX_AUTONOMOUS_AUTHORITY = NO
```

## Authorization

This state file records the approved structural model only. It does not
authorize a new skill, adaptation, runtime test, release, installation, product
change, or consumer integration.

## Next authorized action

`NONE_UNTIL_NEW_EXPLICIT_APPROVAL`
