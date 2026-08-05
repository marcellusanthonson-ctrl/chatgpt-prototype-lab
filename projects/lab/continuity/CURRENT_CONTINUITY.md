# LAB continuity — README authorization 195 and Product Leadership handoff

Canonical repository: `marcellusanthonson-ctrl/chatgpt-prototype-lab`  
Branch: `main`  
Entrypoint: `project-sources/chatgpt/START_HERE.md`  
HEAD policy: `VERIFY_LIVE_AT_USE`

## Estado alcanzado

Authorization 194 published `CODEX-DESKTOP-CONTEXT-OPTIMIZATION-001` and was consumed with no residual authority. The LAB now has a short root `AGENTS.md`, four lightweight role profiles, execution envelopes, context manifests, risk-based routing, controlled parallelism and measurement contracts.

No operational speed improvement has been established yet.

## Autorización documental activa

`AUTHORIZATION_LAB_README_CODEX_DESKTOP_OPTIMIZATION_DOCUMENTATION_195`

Status:

`GRANTED_AWAITING_EXECUTION`

It authorizes only a concise README section titled **“Ejecución optimizada con Codex Desktop”**, placed after **“Entrada para un nuevo piloto”** and before **“Orden canónico de lectura”**.

The exact execution gate is the current `README.md` blob:

`9968ae258b2bdf3cb6c3c800434914f06052e7cd`

The new conversation must verify live `main` and stop if the README blob differs. The continuity publication itself may advance `main` without invalidating this authorization.

Use:

- `AGENTS.md`
- `projects/lab/execution-envelopes/README_CODEX_DESKTOP_OPTIMIZATION_195_001.json`
- `projects/lab/context-manifests/README_CODEX_DESKTOP_OPTIMIZATION_195_001.json`
- profile `LAB_IMPLEMENTATION`

The README must not contain a fixed HEAD, current authorization state, pending items, Product Leadership status or an unmeasured speed claim.

## Product Leadership

Product Leadership remains:

`CANDIDATE_NOT_ACTIVE_NOT_INTEGRATED`

Readiness remains:

`NOT_READY_FOR_FRESH_RETEST_REISSUE`

Execution 005 / ATTEMPT-004 was published as `BLOCKED_BEFORE_MODEL_REQUESTS` with zero model requests and zero retries. Codex CLI was not logged in, and all 13 governed redesign files failed the worktree raw-byte gate because Windows materialized CRLF while the Git blobs remained LF. No instrument, package or `INT-LAB-004` mutation occurred.

After authorization 195 is consumed, the next Product Leadership step is a **separately authorized zero-model local readiness probe**, not a retest.

The probe must:

1. create a fresh Windows worktree from the live verified `main`;
2. prove 13/13 raw-byte Git-blob/worktree matches;
3. verify `codex login status` for a preexisting ChatGPT session without performing login;
4. verify Codex CLI `0.146.0` and SHA-256 `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb`;
5. verify the requested `gpt-5.6-sol`, `medium` reasoning and read-only sandbox surface through non-generative checks, or return `INSUFFICIENT_EVIDENCE`;
6. run deterministic validators without modifying governed Product Leadership artifacts;
7. emit `READY_FOR_SEPARATE_FRESH_RETEST_REISSUE_AUTHORIZATION`, `NOT_READY_WITH_EXACT_BLOCKERS` or `INSUFFICIENT_EVIDENCE`;
8. capture the first operational Codex Desktop context and latency metrics.

The probe, retest, model requests, login, audit, adjudication, promotion, activation and integration are not authorized by this continuity package.

## Sequence

1. Execute and consume authorization 195.
2. Separately prepare or grant the Product Leadership zero-model readiness probe.
3. Only after a readiness PASS, decide whether to grant a new fresh retest authorization.
4. Any retest result still requires separate external audit and human promotion decisions.

## Single next action

Execute authorization 195 using the published execution envelope and context manifest.
