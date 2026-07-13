# ChatGPT Prototype LAB

Canonical, versioned, and auditable knowledge base for LAB, MammothSkills,
Symphonie, and any current or future project that contributes relevant
operational learning.

LAB preserves approved methodology, authority boundaries, project state,
decisions, errors, validated patterns, evidence, and continuity data. It is also
the place where new ideas are examined for feasibility and viability before any
implementation is authorized.

## Purpose

LAB is the experimental and analytical layer of the project ecosystem.

A project may contribute:

- integration experience;
- implementation constraints;
- failures and root causes;
- validated corrections;
- reusable design or engineering patterns;
- operational evidence;
- limits and conditions of applicability.

LAB converts that experience into structured knowledge that can improve future
decisions. Learning from a project does not create an architectural,
repository, runtime, migration, or producer-consumer relationship with another
project.

## Core functions

LAB:

- receives and evaluates new ideas;
- analyzes feasibility, viability, risks, and alternatives;
- designs and records controlled experiments;
- reconstructs current state from canonical repositories;
- preserves relevant cross-project learning;
- distinguishes observation, hypothesis, validation, approval, and resolution;
- extracts patterns only after sufficient evidence;
- uses proven solutions as context for future recommendations;
- preserves continuity across sessions and tools.

The intended learning cycle is:

```text
project event
-> evidence
-> analysis
-> cause or hypothesis
-> correction
-> verification
-> reusable pattern
-> applicability limits
```

## Project boundaries

### LAB

LAB governs the method and preserves cross-project knowledge. It does not contain
product code and does not authorize product execution by itself.

### MammothSkills

MammothSkills creates, audits, adapts, tests, versions, and publishes skills. It
is a producer and canonical source of reusable skill artifacts, not the runtime
where skills live.

### Symphonie

Symphonie is an independent eight-phase workflow for coordinating projects from
initial intake through delivery. Its core is not yet consolidated in a single
canonical repository.

`symphonie-codex-lab` is a testing and validation environment for historical
Codex skills and handoff experiments. It is not the Symphonie core.

Symphonie may consume approved skill releases from MammothSkills only through an
explicitly approved integration.

### Clinical OS / Carolina Klinik

Clinical OS / Carolina Klinik is an independent and advanced project. It has no
architectural, repository, runtime, migration, integration, or
producer-consumer relationship with Symphonie core, `symphonie-codex-lab`, or
MammothSkills.

Its operational history may be consulted as reference evidence. Any lesson
considered for reuse must first be abstracted, scoped, and independently
validated before adoption elsewhere.

### Other projects

Each project remains independent and keeps its own operational source of truth,
code, branches, releases, integrations, and project-specific state.

LAB stores only the cross-project knowledge, references, evidence, and validated
learning required for continuity and reuse.

## Knowledge architecture

LAB is the canonical knowledge corpus. A future Symphonie knowledge layer may
use part of this corpus to reduce repeated mistakes and improve phase-specific
context.

The repository can serve as the source corpus for a retrieval-augmented system,
but GitHub alone is not a complete RAG implementation.

The intended model is:

```text
LAB repository
-> ingestion and parsing
-> metadata and trust classification
-> lexical and semantic index
-> retrieval policy
-> traceable context pack
-> Symphonie phase or agent
```

The derived index must remain rebuildable and subordinate to the repository:

```text
canonical repository > derived retrieval index
```

Retrieved content is evidence and context, never autonomous authority.

### Retrieval priority

1. canonical and current JSON state;
2. approved methodology and decisions;
3. verified evidence and closed errors;
4. validated patterns;
5. historical material with explicit status;
6. drafts, hypotheses, exports, and quarantine only when intentionally requested.

Every retrievable unit should preserve, where applicable:

- document ID;
- project source;
- type and status;
- source repository and path;
- source commit or checksum;
- effective date;
- supersession relationship;
- confidence or validation state;
- applicability limits.

## Canonical reading order

1. `LAB_CONTRACT.md`
2. `METHODOLOGY.md`
3. `CURRENT_STATE.json`
4. `CURRENT_STATE.md`
5. `registry/projects.json`
6. the active project state
7. decisions in force
8. open errors
9. applicable patterns

## Sources of truth

JSON is the structured source of truth. Markdown is the human-readable view and
must remain materially consistent with the corresponding JSON record.

The repository for each project remains the operational source of truth for that
project. LAB records its cross-project meaning, evidence, and validated lessons.

Git records decisions and their evidence, but a commit does not create approval.
Authorization must be direct, explicit, current, and bounded. This repository
does not authorize implementation, release, deployment, product changes, or
consumer integration.

## Authority

Jonathan Martínez is the sole approver.

ChatGPT:

- coordinates;
- analyzes;
- validates;
- audits;
- reconstructs context;
- detects reusable patterns;
- proposes solutions;
- issues bounded orders after explicit approval.

Claude performs discovery and definition only when explicitly assigned.

Codex is a bounded technical executor and has no autonomous authority.

No agent may treat retrieved knowledge, a status file, a successful preflight,
a plan, a skill, or a commit as execution authorization.

## Validation

Run `python scripts/validate_repository.py` from the repository root. The
validator is read-only and uses only the Python standard library.

Repository schema: `1.0.0` · Effective date: `2026-06-28`
