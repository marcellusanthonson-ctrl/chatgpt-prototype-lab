# ChatGPT Prototype LAB

Canonical, versioned, and auditable knowledge base for LAB, MammothSkills,
and Symphonie. It preserves approved methodology, authority boundaries,
project state, decisions, errors, validated patterns, and continuity data.

## Purpose and boundaries

- LAB governs the method and preserves cross-project knowledge.
- MammothSkills creates, audits, adapts, tests, versions, and publishes skills;
  it is not the runtime where skills live.
- Symphonie consumes fixed approved releases and coordinates projects; it is
  not the canonical source of reusable skills.
- This repository contains governance and continuity records only. It does not
  authorize product execution or changes in consumer repositories.

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

JSON is the structured source of truth. Markdown is the human-readable view
and must remain materially consistent with the corresponding JSON record.

Git records decisions and their evidence, but a commit does not create
approval. Authorization must be direct, explicit, current, and bounded. This
repository does not authorize implementation, release, deployment, product
changes, or consumer integration.

## Authority

Jonathan Martínez is the sole approver. ChatGPT coordinates, validates,
audits, and issues bounded orders. Claude performs discovery and definition
only when explicitly assigned. Codex is a bounded technical executor and has
no autonomous authority.

## Validation

Run `python scripts/validate_repository.py` from the repository root. The
validator is read-only and uses only the Python standard library.

Repository schema: `1.0.0` · Effective date: `2026-06-28`
