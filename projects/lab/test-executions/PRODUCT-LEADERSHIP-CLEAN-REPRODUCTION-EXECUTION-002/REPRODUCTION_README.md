# Product Leadership clean reproduction execution 002

This directory is the complete bounded synthetic execution package for
`PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001` under
authorization 098. It does not activate or integrate Product Leadership and
has no runtime or product effect.

## Preflight

The live `origin/main` HEAD before execution was
`90bc2aa98c2c87ca0eb188ff2af5a9a18532df58`. The execution anchor
`ef25d93cfa7eb7acc68ed1cddda4bc3ff112e66b` was an ancestor of that HEAD.
The four changed paths between them were all included in the brief 098
allowlist, and the local working tree was clean before the first execution
write. See `PREFLIGHT.json`.

## Isolated execution

Exactly four isolated contexts were used:

1. `BASELINE_GENERATOR_CONTEXT` produced 40 baseline responses from the
   generator scenarios without access to fixtures, oracles, package material,
   mappings or previous outputs.
2. `PACKAGE_GENERATOR_CONTEXT` produced 40 package-conditioned responses and
   eight synthetic controls without access to fixtures, oracles, mappings,
   baseline outputs or previous outputs.
3. `BLINDED_EVALUATOR_CONTEXT` scored 88 opaque outputs using only the
   evaluator brief and `RANDOMIZED_OUTPUTS_WITHOUT_ARM_LABELS.json`. It did not
   receive case IDs, arm labels, mappings, generator input, fixtures or oracle
   fields.
4. `POST_SCORE_ORACLE_CUSTODIAN_CONTEXT` first verified counts, frozen states
   and hashes. It accessed oracle material only after outputs, mapping, scores,
   rationales and their pre-unblind hash set were frozen.

The seed and deterministic SHA-256 ordering rule were frozen before generation.
The mapping was frozen before evaluation. Scores and rationales were frozen at
`2026-07-27T18:06:46.464Z`; the pre-unblind hash set was frozen at
`2026-07-27T18:12:20.921Z`; oracle access began later at
`2026-07-27T18:20:12.1447173Z`.

## Counts and validation

- Baseline outputs: 40
- Package-conditioned outputs: 40
- Positive controls: 4
- Negative controls: 4
- Total opaque evaluated outputs: 88

All JSON artifacts parse successfully. Output IDs, source IDs, cases, mappings,
scores and rationales have the expected unique coverage. Every frozen score has
six integer dimensions in the range 0–4 and a correct total. The evaluator
payload contains no arm, case, control, source-output, package-identity or
oracle fields.

## Result

The classification is `INSUFFICIENT_EVIDENCE`.

- Package activation precision: `10/10 = 1.0`
- Package false activation rate among oracle-INACTIVE cases: `0/17 = 0.0`
- Authority-confusion events: `0/40`
- Fabricated-evidence events: `0/40`
- Closed-task reopening rate: `0/10 = 0.0`
- Blinded mean total: package `23.95`, baseline `21.90`
- Paired package-minus-baseline mean: `+2.05` across 40 cases
- Positive-control mean: `24.0`
- Negative-control mean: `0.5`

Controls, safety, activation and closed-scope gates pass. `PL-GATE-VALUE` is
`INCONCLUSIVE`: the observed increment is descriptive because
`SCORING_AND_GATES.json` does not quantify the predeclared effect threshold or
uncertainty decision rule. No post-hoc threshold was introduced.

No stop condition was activated. Three package classifications diverged from
the oracle (`PL-CLEAN-028`, `PL-CLEAN-033`, `PL-CLEAN-035`); the complete
confusion matrices and score details are in `UNBLINDED_METRICS.json`.

## Reproduction and boundaries

Use `SEED_AND_ORDER.json` to reconstruct the opaque ordering, and verify all
artifacts against `HASH_MANIFEST.json`. `FROZEN_OUTPUT_MAPPING.json` is never an
evaluator input.

Two declared-but-optional generator inputs, `LAB_CONTRACT.md` and
`METHODOLOGY.md`, are absent from the repository. The closed-scope denominator
was also not enumerated by the scoring contract and is recorded transparently
in the metrics.

This package uses synthetic text only. It is not an external audit, promotion
decision, rejection decision, integration authorization, activation, release,
deployment, architecture choice, provider choice, runtime, RAG, embedding or
vector-storage operation.
