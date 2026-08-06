# Benchmark 198 artifact forensic recovery

Authorization: `AUTHORIZATION_LAB_BENCHMARK_198_ARTIFACT_FORENSIC_RECOVERY_AND_CONDITIONAL_VERIFIABLE_REISSUANCE_200`

Terminal result: `PARTIAL_ARTIFACT_RECOVERY_INSUFFICIENT_FOR_RETEST`

## Finding

The historical package supports an exact recovery of the private oracle only. The task corpus and benchmark runner were published as malformed UTF-8 representations of packed 16-bit byte pairs and contain `U+FFFD` replacement characters. Those replacement characters erase the original byte pairs and prevent exact reconstruction.

- corpus: 3454 ASCII bytes are recoverable before the first irreversible loss;
- runner: 526 ASCII bytes are recoverable before the first irreversible loss;
- runner: canonical inventory declares 7093 bytes while GitHub records 7092 bytes;
- oracle: exact recovery passes byte count, SHA-256, Git blob SHA, base64, gzip, JSON and 21-task count.

No independent source contains the original task prompts or the complete runner/scorer implementation. Therefore a source-complete semantic reissue is not allowed.

## Non-effects

No resolver was modified or executed. No retest, model call, Codex scoring call, integration, runtime, product or architecture selection occurred.
