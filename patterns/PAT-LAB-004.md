# PAT-LAB-004 — Bounded evidence-first audit

Status: `VALIDATED`
Scope: `LAB`, `MammothSkills`, `Symphonie`
Updated-At: `2026-06-28`

## Intent

Audit real repositories and artifacts without confusing observation,
correction, approval, or execution authority.

## Procedure

1. Resolve the exact repository, branch, HEAD, scope, and authority.
2. Verify a clean working tree or record every pre-existing change.
3. Freeze baselines and calculate fingerprints before adaptation.
4. Inventory exact candidate files without modifying them.
5. Compare canonical artifacts before reports or conversational recollection.
6. Separate preflight, audit, correction, implementation, release, and
   consumer integration.
7. Run audit-only before correction unless correction is explicitly ordered.
8. Fail closed when evidence, path, platform, or authority is ambiguous.
9. Validate exact fileset, JSON, encoding, line limits, hashes, and tests.
10. Verify the resulting commit remotely against the intended branch head.
11. Record rollback, unresolved issues, and supersession relationships.

## Evidence hierarchy

1. current repository artifact;
2. executable code and validators;
3. schemas and versioned expected results;
4. original execution evidence;
5. manifests and approved plans;
6. derived reports;
7. conversational recollection.

## Validated techniques

- record revision, commit, and SHA-256 for a single-file fingerprint;
- hash an ordered manifest of normalized paths and file hashes for a directory;
- approve the complete fileset before implementation;
- parse and serialize structured formats instead of text injection;
- use UTF-8 without BOM and LF in canonical Git content;
- limit recovery to an exact allowlist and distinguish tracked states;
- diagnose EOL noise with logical content and normalized comparisons;
- verify the remote commit instead of trusting local console output.

## Anti-patterns

- infer target platform from the technical executor;
- treat a commit, status, preflight, or installed skill as authorization;
- mix audit and correction without an explicit correction order;
- delete an incorrect decision instead of superseding it;
- use broad destructive recovery;
- create a live consumer dependency on a producer working tree;
- approve architecture before exact platform and target paths are known;
- convert silence or partial agreement into approval.

## Evidence

- `METHODOLOGY.md`, sections 7 through 9;
- `errors/ERR-LAB-001.md`;
- `errors/ERR-TOOLING-001.md`;
- the pre-existing validated `PAT-LAB-004` record.

## Completion criteria

An audit is complete only when findings, evidence, scope, limitations, and the
single next authorized action are explicit. A correction is complete only
after independent verification.
