# Contextual Bootstrap Resolver Operational Benchmark 001

Status: `REAL_REPOSITORY_BENCHMARK_FAIL_CRITICAL`

This package records authorization 198's shadow A/B benchmark of the unchanged resolver 197 baseline against real paths and GitHub metadata from the LAB snapshot `87b0ca32a8789f2a69ebfc2b3de67ff396b1bcb3`. No model was called and the resolver was not integrated.

## Result

- 21 tasks across seven routes.
- 63 canonical baseline loads and 63 resolver selections.
- 126 total iterations.
- Macro path F1: `0.925243`.
- Critical constraint recall: `0.935484`.
- Median represented-byte reduction: `70.045%`.
- Median source-count reduction: `75%`.
- Critical issues: `16`.

## Decisive failures

1. A small code-change request containing “estado” was routed as `STATUS_OR_AUTHORITY`, changing its authority semantics.
2. Status queries omitted current continuity and authorization lifecycle records.
3. Two material conflicts were returned as `READ_ONLY_READY` instead of `RESOLUTION_REQUIRED`.
4. Audit queries omitted required lifecycle or aggregate-state sources in targeted cases and over-selected unrelated evidence.
5. `STATUS_OR_AUTHORITY` achieved only `14.104%` median byte reduction, below the per-route gate.

## Boundaries

The local executor could not clone the private repository. The snapshot therefore uses a fixed GitHub commit/tree, real paths, GitHub source sizes/blob metadata and canonical content reads. Non-empty line counts, real tokenizer counts, model response quality and time-to-first-useful-code were not measured.

This FAIL does not authorize modifying, integrating or promoting the resolver.

## Reproduction

The frozen operational tasks, private oracle, final manifests, final results, snapshot metadata and benchmark runner are retained as gzip/base64 text artifacts. Decode with base64 and gzip before inspection or replay.
