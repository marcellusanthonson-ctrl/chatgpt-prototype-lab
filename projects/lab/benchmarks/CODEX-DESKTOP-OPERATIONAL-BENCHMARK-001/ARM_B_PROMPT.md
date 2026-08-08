# CODEX DESKTOP 216 — ARM B OPTIMIZED

Execute `CODEX_DESKTOP_216_ARM_B_PROGRESSIVE_CONTEXT_OPTIMIZED` only after ChatGPT has delivered the mandatory Arm A post-test report and confirms the lifecycle gate permits Arm B.

Use a **fresh independent Windows Codex Desktop thread** and branch `benchmark/codex-desktop-216-arm-b`. Do not reuse Arm A conversation context.

ChatGPT will provide the exact `COMMON_EXECUTION_BASELINE_SHA`. Before analysis run `git rev-parse HEAD` and require exact equality with that same SHA. Stop on mismatch.

Load `AGENTS.md`, then `projects/lab/execution-envelopes/CODEX_DESKTOP_OPERATIONAL_BENCHMARK_216_001.json` and its referenced context manifest. Follow progressive disclosure exactly. Do not eagerly load ON_TRIGGER, HISTORICAL_REFERENCE or AUDIT_ONLY sources.

Execute the same `TASK.json` and `QUALITY_ORACLE.json` as Arm A. Write only under `projects/lab/benchmark-executions/CODEX-DESKTOP-OPERATIONAL-BENCHMARK-001/ARM_B/`:
- `RESULT.json`
- `CONTEXT_BUDGET_REPORT.json`
- `LEARNING_APPLICATION_REPORT.json`
- `SURFACE.json`

`SURFACE.json` must match Arm A's observed Codex model, reasoning configuration and sandbox configuration. If the configuration differs or cannot be established, stop and report insufficient evidence. Record Codex version, OS, common baseline SHA and observability.

Record all metrics required by the measurement protocol. Initial ALWAYS+REQUIRED sources must be <= 8 and duplicate stable rules must be zero.

The same forbidden actions and Product Leadership state-preservation boundaries as Arm A apply. Do not edit Product Leadership owner artifacts in this arm.

Commit and push only the four Arm B outputs. Do not merge any PR and do not push to main. Stop so ChatGPT can verify, report Arm B, compare both arms and perform the separately authorized canonical reconciliation.
