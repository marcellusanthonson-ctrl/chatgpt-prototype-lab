# LAB — Project State

Project-ID: `lab`
Status: `ACTIVE`
Last-Updated: `2026-06-28`

## Purpose

Govern the method used across the laboratory, preserve external memory, and
maintain approved decisions, project states, errors, evidence, and reusable
audit patterns.

## Current phase

`METHODOLOGY_FROZEN_V1`

## Decisions in force

- Git is the canonical external decision and audit memory.
- `METHODOLOGY.md` v1.0 is approved and effective.
- JSON is structured truth; Markdown is the human-readable view.
- Incorrect decisions are superseded rather than silently removed.
- Missing authority or evidence produces a fail-closed `BLOCKED` state.

## Authority

- Jonathan Martínez: sole approver.
- ChatGPT: coordinator, validator, auditor, and bounded-order issuer.
- Claude: discovery and definition when explicitly assigned.
- Codex: technical executor only under a direct, explicit, bounded order.

## Open work

- Add schemas and automated validators for decision, error, project-state, and
  pattern records.
- Continue incorporating verified knowledge without duplicating product code.

## Next authorized action

Maintain the repository as the cross-project knowledge base. No product or
consumer-repository modification is authorized by this file.
