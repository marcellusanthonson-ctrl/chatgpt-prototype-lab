# CODEX_BOUNDED_RECOVERY_RESOLVER — Runbook

## Mission
Do not treat a reversible technical deviation as a terminal result. Diagnose the root cause, apply only reversible authorized repairs, revalidate every affected gate, and continue until the surface is eligible, one human action is required, a hard stop is proven, or the test mission completes.

## Recovery loop
1. Verify live `main` and authorization 188.
2. Observe without changing state.
3. Form one causal hypothesis.
4. Run the smallest discriminating diagnostic.
5. Apply one reversible fix if supported.
6. Revalidate all affected gates.
7. Record the cycle in `RECOVERY_JOURNAL.json`.
8. Continue within the five-cycle budget.

## Hash investigation
Hash canonical bytes from the Git blob at the verified HEAD. Hash the working-tree file separately. Never infer canonical corruption from a working-tree hash alone.

Interpretation:
- canonical expected + working tree different → recoverable checkout/EOL/encoding/filter issue;
- canonical different from expected → hard-stop canonical contradiction;
- both expected → pass;
- dirty working tree → isolate or restore before execution.

## Authentication
Read no secrets. Record only a boolean. When login is required, publish `WAITING_FOR_USER_ACTION_RESUMABLE` with exactly one user action. Do not consume authorization 188. Resume after the user completes the action.

## Model and runner
Require exact `gpt-5.6-sol`. Allowed recovery includes restart, catalog refresh, stable runner provenance checks, and official stable self-update within the existing installation. No prerelease runner and no model substitution.

## Conditional execution
After all eligibility gates pass:
1. perform one smoke request;
2. if PASS, run exactly two independent calibration-v2 scorers;
3. if calibration PASS, create Execution 004 / Attempt 003;
4. run 52 fixtures across four arms and produce at least 112 outputs;
5. blind-score and measure cost, negative transfer, and net decision value;
6. publish the exact result and consume authorization 188.

## Hard stops
Stop and consume only when a prohibited or irreversible action is required, the exact model remains unavailable after allowed recovery, the five-cycle budget is exhausted, frozen content would need mutation, or a downstream smoke/calibration/test integrity gate fails.
