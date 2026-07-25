# Authority-first failure analysis and next discriminating test

Status: `DESIGN_READY_FOR_SEPARATE_EXECUTION_AUTHORIZATION`.

This is a documentary analysis of the frozen execution 071 artifacts. No runs were re-executed, no corpus was generated, and no historical harness, oracle, metric, gate or hash was changed.

## Exact failure profile

The authority-first arm produced 48 critical events across 252 fixture evaluations. All 48 came from eight fixtures and were stable across all six configurations:

- `BINDING_NEGATIVE_OMITTED`: 12 events from `FX-071-002` and `FX-071-027`, one per fixture in each configuration.
- `UNSUPPORTED_CONCLUSION`: 36 events from `FX-071-006`, `008`, `021`, `024`, `031` and `033`, one per fixture in each configuration.
- Other critical codes: zero.

The two omitted binding-support documents were at recorded base-query ranks 13 and 11. `budget_k=2` therefore contributed, but a modest increase to k would not have been sufficient. A large increase could recover them while also adding unrelated context, reducing precision and worsening the current selection-count safe-refusal rule.

## Causal boundary

The direct evidence supports three mechanisms:

1. Broad lexical retrieval admitted 31-36 candidates for each failing fixture because generic terms were shared across the corpus.
2. Authority-first ranking prevented authority inversions but placed unrelated authority-rank-100 documents ahead of required authority-rank-90 negative support.
3. Safe refusal was implemented as `selected.length == 0`; any unrelated eligible match therefore became a non-refusal and an unsupported conclusion.

The exact displacers were not the declared per-fixture decoy documents. They were canonical documents belonging to other fixtures. This modifies the external audit's shorthand attribution to "lexical decoys": lexical distraction was real, but the observed mechanism was cross-fixture canonical collision.

Dense semantic retrieval was not exercised (`embeddings=false`, `provider=NONE`). Its absence makes semantic limitation plausible, not causally proven. The next test therefore isolates representation, k, negative reservation, retrieval, ranking and refusal rather than assuming any one of them is the architectural answer.

## Claim limits

This analysis does not prove product viability, select an architecture, implementation or provider, or confirm or refute the entire authority-first RAG class. Execution of the proposed test requires a separate explicit authorization.
