# CONTEXTUAL_BOOTSTRAP_RESOLVER_001

Experimental, local, read-only prototype authorized by `AUTHORIZATION_197`.

## Purpose

Resolve a user task into a minimal, cited `ContextManifest` without loading every project or every historical record. The prototype implements only deterministic stages 1–4 and 7–8 of `RAG-FEDERATION-CONTRACT-001`:

1. resolve task scope;
2. select authorized namespaces;
3. verify active commits;
4. filter by authority and status;
7. detect cross-source conflicts;
8. return cited context.

Semantic retrieval and ranking are intentionally disabled. This package is not integrated into ChatGPT, Codex Desktop, Symphonie, any product, or any runtime.

## Runtime

- Node.js 22 or compatible;
- TypeScript compiler already available in the execution environment;
- no package installation;
- no external model calls;
- no embeddings or vector store;
- no persistent server.

## Commands

```bash
tsc -p tsconfig.json
node dist/validate.js
node dist/cli.js --input input.json --output context-manifest.json
```

## Validation result

`PROTOTYPE_VALIDATION_PASS_NO_INTEGRATION`

- 24 synthetic fixtures;
- 3 repetitions per fixture;
- 72 deterministic resolver runs;
- macro F1: 1.0;
- critical-constraint recall: 1.0;
- forbidden-path precision: 1.0;
- median byte reduction: 88.292%;
- zero authority bypasses;
- zero consumed authorizations activated;
- zero cross-project contamination;
- zero invented paths;
- zero automatically resolved conflicts.

The result is bounded to the synthetic corpus. It does not establish production readiness, generalization to the complete LAB, operational token savings, or approval for integration.

## Separation

`fixtures/public-fixtures.json.gz.b64` contains only selector-visible inputs. The runner completes all selector executions before loading `oracle/private-oracle.json`. Oracle hashes are checked before and after evaluation.

## Safety properties

- deny by default;
- authority is never inferred from the prompt;
- exact commit pinning;
- binding negative prohibitions;
- active authorization lifecycle checks;
- cross-project isolation;
- first-class conflicts;
- `RESOLUTION_REQUIRED` on conflicting or stale context;
- reason trace for every selected path.
