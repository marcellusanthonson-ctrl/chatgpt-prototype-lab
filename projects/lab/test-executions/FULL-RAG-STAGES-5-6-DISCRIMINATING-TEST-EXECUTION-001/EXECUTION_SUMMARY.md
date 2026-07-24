# Full RAG stages 5–6 discriminating test execution 001

Status: **COMPLETE_REPRODUCIBLE_EXECUTION_PACKAGE_READY_FOR_VERIFIED_REMOTE_PUBLICATION**.

The bounded synthetic execution generated 180 documents and 42 fixtures, froze public and private inputs before any run, executed 30 runs across five arms and six configurations, and evaluated outputs in a separate oracle-enabled process. Leakage controls, canary validation, post-freeze hashes, control discrimination and deterministic replay passed.

The authority-first full RAG simulation was **NON_VIABLE_UNDER_SYNTHETIC_TESTED_CONDITIONS**. It failed Gate B with 48 critical failures and Gate C with required-document recall 0.458333, precision 0.234127, macro F1 0.261243 and safe-failure F1 0.5. These values match `EXECUTION_SUMMARY.json`, `reports/METRICS.json` and `reports/GATE_RESULTS.json`.

The tested arm used `embeddings=false`, `provider=NONE`, `budget_k=2` and predominantly lexical retrieval with limited semantic contribution. The non-viability therefore applies to this frozen synthetic harness and its tested conditions. **THIS_RESULT_DOES_NOT_REFUTE_THE_ENTIRE_ARCHITECTURE_CLASS.** It does not select an architecture, implementation, provider or production design. The relevance-first negative control discriminated unsafe ordering, and the evaluator-only positive control reached the expected ceiling.

No real data, external API, dependency installation, embeddings, vector database, product implementation, deployment or external repository modification was used.
