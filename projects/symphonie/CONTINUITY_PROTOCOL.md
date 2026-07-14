# Symphonie — Cross-Conversation Continuity Protocol

Protocol-ID: `SYM-CONTINUITY-001`
Status: `ACTIVE_GUIDANCE`
Date: `2026-07-14`
Canonical repository: `marcellusanthonson-ctrl/chatgpt-prototype-lab`
Canonical branch: `main`

## 1. Purpose

This protocol defines how a new conversation must reconstruct the current Symphonie state before discussing status, decisions, authorizations, or the next action. It supplements the LAB continuity order; it does not replace `LAB_CONTRACT.md`, `METHODOLOGY.md`, or `CURRENT_STATE.json`.

## 2. Mandatory source-of-truth order

Read from `marcellusanthonson-ctrl/chatgpt-prototype-lab` on `main` in this exact order:

1. `LAB_CONTRACT.md`
2. `METHODOLOGY.md`
3. `CURRENT_STATE.json`
4. `CURRENT_STATE.md`
5. `registry/projects.json`
6. `projects/symphonie/PROJECT_STATE.md`
7. decisions in force referenced by `CURRENT_STATE.json`
8. open errors referenced by `CURRENT_STATE.json`
9. applicable validated patterns
10. `projects/symphonie/reports/SYMPHONIE_DESIGN_MIGRATION_INTEGRATION_REPORT.md`

`CURRENT_STATE.json` is the structured source of truth. Markdown files are human-readable views and must not override contradictory JSON.

## 3. Repositories and refs to verify

### LAB repository

```text
REPOSITORY = marcellusanthonson-ctrl/chatgpt-prototype-lab
BRANCH = main
KNOWN_HEAD_AT_PROTOCOL_CREATION = 4a0eb96890ef892d319ceedf494e94ee5a82dd74
```

The known HEAD is a checkpoint, not a permanent expected HEAD. A new conversation must resolve the current remote `main` and read the files from that current commit.

### Symphonie Codex Lab

```text
REPOSITORY = marcellusanthonson-ctrl/symphonie-codex-lab
CANDIDATE_BRANCH = feature/design-migration-handoff-alpha6
CANDIDATE_HEAD = 385f85b85560d8f5a12512c9f36e2bdd140f1d7b
IMPLEMENTATION_COMMIT = 22d63a901ec30221e7e8e7e944203eb2239598bd
```

Before relying on the candidate, verify that the remote branch still resolves to the recorded candidate HEAD or identify the newer authorized transition that superseded it.

## 4. State snapshot at protocol creation

```text
LAB_CURRENT_STATE_VERSION = 1.0.9
ARCHITECT_APPROVED_BASELINE = 0.1.0-alpha.5
ARCHITECT_ALPHA6_STATUS = PUBLISHED_CANDIDATE_WITH_RUNTIME_PASS_AND_HISTORICAL_EVIDENCE_FINDING
IMPLEMENTER_APPROVED_BASELINE = 0.1.0-alpha.3
REG-08 = PASS
REG-09 = BLOCKED_AS_EXPECTED
REG-09_REASON = MIGRATION_TARGET_UNCONFIRMED
REAL_DESIGN_EXECUTION = NOT_YET_VALIDATED
REPEATABILITY = NOT_YET_VALIDATED
```

This snapshot is historical context only. The new conversation must prefer the current repository state.

## 5. What Alpha.6 adds

Alpha.6 conditionally adds `.project/phase-3/migration-handoff.json` when an authorized Phase 3A instruction declares a technology migration or another qualifying fidelity condition.

The document preserves:

- source and target technology identity;
- source-of-truth precedence and immutable sources;
- visual formulas and recalculation behavior;
- sensitive fidelity zones;
- granular typography exceptions;
- SSR, hydration, client-boundary, observer, CSS, and font-loading risks;
- navigation and hash contracts;
- assets and hashes;
- observable visual acceptance criteria;
- visual references and approval state.

It is not required in ordinary Phase 3A work when activation conditions are absent.

## 6. Evidence and known finding

Alpha.6 direct evidence:

```text
STATIC_VALIDATION = PASS
REG-08_RUNTIME = PASS
REG-09_FAIL_CLOSED = PASS
UNAUTHORIZED_WRITES = ZERO
```

Known finding:

```text
FULL_HISTORICAL_REGRESSION_PACK = INCOMPLETE_EVIDENCE
MISSING_HISTORICAL_ACTUALS = REG-02_THROUGH_REG-07
```

Do not reinterpret the historical evidence gap as a failure of REG-08 or REG-09. Do not claim full-pack revalidation until the missing historical evidence is addressed or formally classified under a separate authorization.

## 7. Authorization reconstruction

At the start of a new conversation, assume no execution authorization unless `CURRENT_STATE.json` or a new explicit message from Jonathan Martínez states otherwise.

The following remain separate permissions:

- analysis;
- documentation write;
- implementation;
- commit;
- push;
- pull request;
- merge;
- tag;
- release;
- deployment;
- Symphonie integration;
- MammothSkills migration;
- product changes.

A previous commit, successful test, status file, continuation phrase, or prior authorization does not grant a new permission.

## 8. Required preflight before any technical order

Before issuing an executable order, establish:

```text
recipient:
executor:
repository:
branch:
expected_head:
authorized_files:
permitted_actions:
prohibited_actions:
validations:
stop_conditions:
commit_authorization:
push_authorization:
expected_result:
```

Mandatory stop conditions include:

- repository, branch, or HEAD mismatch;
- dirty state outside the authorized scope;
- ambiguous target technology or target path;
- need for an unapproved file or dependency;
- changed immutable baseline;
- inability to execute a critical validation;
- conflict between canonical JSON and Markdown;
- requirement for force push or autonomous scope expansion.

## 9. Recommended continuation sequence

No step below is pre-authorized.

### Path A — Candidate promotion review

1. Audit Alpha.6 at the published candidate commit.
2. Verify exact changed files and direct REG-08/09 evidence.
3. Decide how the historical REG-02–07 evidence gap affects promotion.
4. Produce a promotion recommendation.
5. Obtain Jonathan's explicit approval or rejection.
6. Record promotion separately from release or integration.

### Path B — Historical evidence closure

1. Inventory the expected `actual/` evidence for REG-02 through REG-07.
2. Determine whether evidence can be reconstructed, rerun, or formally classified as unavailable.
3. Issue a bounded evidence-only order.
4. Rerun the full verifier.
5. Record the result without changing Alpha.6 unless a separate correction is approved.

### Path C — Real-design execution

1. Select a real design and confirm its repository, branch, commit, target technology, and authorized files.
2. Decide whether migration-handoff activation conditions apply.
3. Run Phase 3A with the approved or explicitly selected architect version.
4. Preserve the human design-approval gate.
5. Run Phase 4A only under separate source-write authorization.
6. Build and validate responsive, keyboard, focus, accessibility, actions, fidelity zones, formulas, assets, and target-runtime risks.
7. Record findings and stop before integration or release.
8. Repeat the flow before claiming reproducibility.

## 10. Opening prompt for the next conversation

Use this message to start the next conversation:

> Consulta el repositorio canónico `marcellusanthonson-ctrl/chatgpt-prototype-lab` en `main` y reconstruye el estado siguiendo el orden de `LAB_CONTRACT.md`, `METHODOLOGY.md`, `CURRENT_STATE.json`, `CURRENT_STATE.md`, `registry/projects.json`, `projects/symphonie/PROJECT_STATE.md`, decisiones, errores, patrones y `projects/symphonie/reports/SYMPHONIE_DESIGN_MIGRATION_INTEGRATION_REPORT.md`. Después verifica la rama `feature/design-migration-handoff-alpha6` de `marcellusanthonson-ctrl/symphonie-codex-lab`. No asumas autorizaciones previas. Informa el estado vigente, las diferencias respecto de este protocolo y la siguiente transición recomendada, sin ejecutar cambios.

## 11. Expected first response in the new conversation

The first response should contain:

```text
LAB_REMOTE_HEAD:
CURRENT_STATE_VERSION:
SYMPHONIE_PROJECT_STATUS:
ALPHA5_STATUS:
ALPHA6_REMOTE_HEAD:
ALPHA6_STATUS:
REG08_STATUS:
REG09_STATUS:
HISTORICAL_EVIDENCE_FINDING:
CURRENT_AUTHORIZATION:
NEXT_RECOMMENDED_TRANSITION:
REPOSITORY_DIFFERENCES_FROM_PROTOCOL:
```

If the repository cannot be consulted, the response must state that explicitly and must not invent current state.
