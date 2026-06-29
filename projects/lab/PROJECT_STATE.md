# LAB — Project State

Project-ID: `lab`
Status: `ACTIVE`
Last-Updated: `2026-06-28`

## Purpose

Govern the laboratory method and preserve approved decisions, project states,
errors, evidence, reusable audit patterns, and continuity knowledge.

## Current phase

`KNOWLEDGE_BASE_OPERATIONAL_V1`

`METHODOLOGY.md` version `1.0.0` is approved and frozen.

## Operational state

```text
Status: ACTIVE
Current phase: KNOWLEDGE_BASE_OPERATIONAL_V1
Bootstrap: COMPLETED
Knowledge base: OPERATIONAL
Previous bounded order: CONSUMED
Current execution authorization: NONE
```

The bootstrap implementation commit
`5fe7effeb7b9896461b15f2b207fbcffe3897a1f` was validated and its remote
publication was verified. The completed order is consumed.

## Infrastructure

- `CURRENT_STATE.json` is the structured canonical current-state record.
- Project, decision, error, and pattern registries provide indexed records.
- Draft 2020-12 schemas document the JSON structures used by the repository.
- `scripts/validate_repository.py` performs read-only repository validation.
- `tests/expected_repository_state.json` fixes the expected governance state.

## Decisions in force

- Git is the canonical external decision and audit memory.
- JSON is structured truth; Markdown is the human-readable view.
- Incorrect decisions are superseded rather than silently removed.
- Missing authority or evidence produces a fail-closed `BLOCKED` state.

## Authority

- Jonathan Martínez: sole approver.
- ChatGPT: coordinator, validator, auditor, and bounded-order issuer.
- Claude: discovery and definition only when explicitly assigned.
- Codex: bounded technical executor with no autonomous authority.

## Authorization

No current execution authorization exists. The consumed bootstrap order does
not authorize additional documentation, implementation, release, product
change, or consumer integration.

## Next authorized action

A new direct approval and bounded order are required before any additional
repository work. No product action is authorized by this file.
