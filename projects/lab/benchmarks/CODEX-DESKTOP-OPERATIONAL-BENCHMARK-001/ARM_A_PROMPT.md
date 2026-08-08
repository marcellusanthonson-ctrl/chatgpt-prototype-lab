# CODEX DESKTOP 216 — ARM A CONTROL

Execute `CODEX_DESKTOP_216_ARM_A_EAGER_FULL_CONTEXT_CONTROL` for `CODEX-DESKTOP-OPERATIONAL-BENCHMARK-001` in a **fresh Windows Codex Desktop thread**.

Authorization: `AUTHORIZATION_LAB_CODEX_DESKTOP_OPERATIONAL_BENCHMARK_PRODUCT_LEADERSHIP_READINESS_RECONCILIATION_216`.
Branch: `benchmark/codex-desktop-216-arm-a`.

ChatGPT will provide the exact `COMMON_EXECUTION_BASELINE_SHA` after remote setup publication. Before analysis run `git rev-parse HEAD` and require exact equality with that SHA. Stop on mismatch. Record it in every arm output. Both arms must use this same baseline.

## Control loading
Read **every** file in `projects/lab/benchmarks/CODEX-DESKTOP-OPERATIONAL-BENCHMARK-001/EAGER_SOURCE_SET.json` before deciding relevance. This eager-loading exception is benchmark-only. Do not use the optimized execution envelope/context manifest to reduce Arm A initial sources.

Then read `TASK.json` and `QUALITY_ORACLE.json` and produce only a documentary reconciliation candidate. Do **not** edit Product Leadership owner artifacts.

Write only under `projects/lab/benchmark-executions/CODEX-DESKTOP-OPERATIONAL-BENCHMARK-001/ARM_A/`:
- `RESULT.json`
- `CONTEXT_BUDGET_REPORT.json`
- `LEARNING_APPLICATION_REPORT.json`
- `SURFACE.json`

`SURFACE.json` must record the observed Codex model, reasoning configuration, sandbox configuration, Codex version, OS, common baseline SHA and whether each value was directly observable. If model/reasoning/sandbox cannot be established, report that and stop with insufficient evidence rather than inventing it.

Record all metrics required by `CODEX-DESKTOP-CONTEXT-AND-LATENCY-MEASUREMENT-001`. A metric that is genuinely not observable must be explicit, never fabricated.

Permitted supplemental observations: OS, `codex --version`, and read-only preexisting Codex login-status observation if available without login/logout. Never access credentials or secrets.

Forbidden: Product Leadership zero-model readiness probe; fresh retest; model-subject/scoring/audit/adjudication/promotion/activation/integration; SSE; Contextual Bootstrap; rulesets/settings/workflows; credentials/secrets; runtime/product/external repo; direct push to main; PR merge.

Commit and push only the four Arm A outputs to this arm branch. Stop after Arm A. Arm B remains `NOT_RUN` until ChatGPT verifies these outputs and delivers the mandatory Arm A post-test report to Jonathan Martínez.
