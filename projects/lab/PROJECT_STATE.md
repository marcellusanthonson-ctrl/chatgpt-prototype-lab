# LAB — Project State

Project-ID: `lab`
Status: `ACTIVE`
Last-Updated: `2026-06-28`

## Purpose

Govern the laboratory method and preserve approved decisions, project states,
errors, evidence, reusable audit patterns, and continuity knowledge.

## Current phase

`METHODOLOGY_FROZEN_V1`

`METHODOLOGY.md` version `1.0.0` is approved and frozen.

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

The current bounded order authorizes LAB documentation completion, repository
validation, one commit, and one direct fast-forward push. It does not authorize
implementation, release, product change, or consumer integration.

## Next authorized action

Maintain this repository as the cross-project knowledge base under a new
direct, explicit, bounded order. No product action is authorized by this file.
