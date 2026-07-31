# M3 — Dual selector evaluation

Authorization 157 executed two operationally independent, read-only evaluators over exactly 420 deterministic synthetic cases.

- The static evaluator reads only the frozen `MODULE_SELECTOR.json` and the M3 corpus.
- The shadow evaluator reads only the frozen M2 shadow registry, its four adapters and the M3 corpus.
- The evaluators share no resolution function or implementation code.
- Both unchanged runs produced digest `9d9f48ab881ee0f604e70ae1d23887afe8c2a6bdfcf683b49e76b0a641935329` for each representation.
- Static and shadow behavior is exactly equivalent in 420 of 420 cases.
- Canonical fixture oracle pass rate is 12 of 13 for each representation.

`CRIT-FIX-008` expects `EVIDENCE_AND_CLAIMS` and `WEB_ACCESSIBILITY`, but its `TASK_WEB_INTERFACE` signal also activates `DESIGN_CRITERION` in both frozen representations. The same regression appears in its reversed-order case. Frozen inputs were not modified.

M3 result: `M3_BLOCKED_WITH_CLASSIFIED_DIVERGENCES`. M3 remediation, M4 and cutover require a separate human decision. No selector, runtime, integration or activation effect occurred.
