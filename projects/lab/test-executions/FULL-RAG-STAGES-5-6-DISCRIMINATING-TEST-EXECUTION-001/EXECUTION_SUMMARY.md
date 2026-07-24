# Full RAG stages 5–6 discriminating test execution 001

Status: **COMPLETE_REPRODUCIBLE_EXECUTION_PACKAGE_READY_FOR_VERIFIED_REMOTE_PUBLICATION**.

The bounded synthetic execution generated 180 documents and 42 fixtures, froze public and private inputs before any run, executed 30 runs across five arms and six configurations, and evaluated outputs in a separate oracle-enabled process. Leakage controls, canary validation, post-freeze hashes, control discrimination and deterministic replay passed.

The authority-first full RAG simulation was viable under the bounded synthetic tested conditions. This result does not select an architecture, implementation, provider or production design. The relevance-first negative control discriminated unsafe ordering, and the evaluator-only positive control reached the expected ceiling.

No real data, external API, dependency installation, embeddings, vector database, product implementation, deployment or external repository modification was used.
