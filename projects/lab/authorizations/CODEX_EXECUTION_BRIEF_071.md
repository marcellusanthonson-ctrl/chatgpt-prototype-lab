# Codex Execution Brief — Authorization 071

## Mandatory authorization

`AUTHORIZATION_LAB_FULL_RAG_STAGES_5_AND_6_DISCRIMINATING_TEST_EXECUTION_071`

Approved by Jonathan Martínez for one bounded execution.

## Repository

- Repository: `marcellusanthonson-ctrl/chatgpt-prototype-lab`
- Branch: `main`
- Authorized baseline: `8653e1b9bed91a9ab460e66341623861c70fea76`
- Entrypoint: `project-sources/chatgpt/START_HERE.md`

## Required first actions

1. Fetch and verify the live remote HEAD of `main`.
2. Stop fail-closed unless the authorization remains applicable and the live state is compatible with its registered baseline and subsequent authorization-registration commits.
3. Read `START_HERE.md` and follow its required order.
4. Read the authorization JSON, `PEND-LAB-017`, and all 20 files of `FULL-RAG-STAGES-5-6-DISCRIMINATING-TEST-001`.
5. Validate JSON, references, boundaries and absence of pre-existing execution artifacts.

## Execution scope

Generate an independent synthetic corpus, private oracles and frozen scoring; validate leakage controls; implement only the local synthetic harness; execute at least 30 runs across the five specified arms and six configurations; evaluate with a separate process; calculate the pre-registered metrics and gates; publish the complete reproducible package.

## Required execution package

Create:

`projects/lab/test-executions/FULL-RAG-STAGES-5-6-DISCRIMINATING-TEST-EXECUTION-001/`

Include every deliverable required by authorization 071, including corpus, private oracles, freeze manifests and hashes, leakage reports, all run outputs, metrics, gate results, reproducibility report, summaries and `HASHES.json`.

## Mandatory boundaries

- No real data.
- No dependency installation.
- No external APIs or managed services.
- No production vector database.
- No production RAG implementation.
- No product or external-repository changes.
- No architecture selection.
- No implementation approval.
- No deployment or release.
- Selector cannot access private oracles, gold labels or private canary.
- Any post-freeze mutation invalidates the execution.

## Required stop states

Stop and report `BLOCKED_FAIL_CLOSED` or `EXPERIMENT_INVALID` for HEAD incompatibility, invalid design package, insufficient or non-independent corpus, leakage, canary exposure, failed controls, hash mutation after freeze, selector/evaluator isolation failure, required dependency installation, required external API, real-data detection, architecture decision requirement or non-reproducible runs.

## Completion

Authorization 071 is consumed only after verified remote publication of a complete reproducible execution package. Create a separate pending record for an independent external audit. Do not register an architectural decision.

Required closing fields:

```text
AUTHORIZATION_071_STATUS = CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION_OF_COMPLETE_REPRODUCIBLE_EXECUTION_PACKAGE
EXECUTOR = CODEX
CORPUS_STATUS = GENERATED_SYNTHETIC_AND_FROZEN
SCORING_STATUS = FROZEN_BEFORE_RUNS
LEAKAGE_CONTROL = PASS_OR_EXPERIMENT_INVALID
RUNS_EXPECTED_MINIMUM = 30
RUNS_EXECUTED = <artifact count>
CONTROL_STATUS = PASS_OR_EXPERIMENT_INVALID
EXPERIMENT_RESULT = <reported without automatic architecture selection>
ARCHITECTURE_SELECTED = NO
IMPLEMENTATION_SELECTED = NO
IMPLEMENTATION_APPROVED = NO
PRODUCT_IMPLEMENTATION = NONE
RUNTIME_PRODUCT_EFFECT = NONE
REAL_DATA_USED = NO
NEXT_AUTHORIZED_ACTION = NONE_AFTER_CONSUMPTION
```
