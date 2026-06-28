# PAT-LAB-004 — Bounded evidence-first audit

Status: `VALIDATED`
Applies-To: `LAB`, `MammothSkills`, `Symphonie`
Validated-On: `2026-06-28`

## Intent

Audit real repositories and artifacts without confusing observation,
correction, approval, or execution authority.

## Workflow

1. Resolve the exact repository, branch, HEAD, scope, and authority.
2. Verify a clean working tree or record every pre-existing change.
3. Freeze baselines and calculate fingerprints before adaptation.
4. Inventory exact candidate files without modifying them.
5. Compare canonical artifacts before relying on reports or conversation.
6. Separate preflight, audit, correction, implementation, release, and
   consumer integration into distinct steps.
7. Run audit-only before correction unless the correction order is explicit.
8. Fail closed when evidence, path, platform, or authority is ambiguous.
9. Validate exact fileset, JSON, encoding, line limits, hashes, and tests.
10. Verify the resulting commit remotely and compare it with the intended
    branch head.
11. Record rollback, unresolved issues, and supersession relationships.

## Evidence hierarchy

Use this order when sources conflict:

1. current repository artifact;
2. executable code and validators;
3. schemas and versioned expected results;
4. original execution evidence;
5. manifests and approved plans;
6. derived reports;
7. conversational recollection.

## Techniques that worked

### Fingerprints

For a single file, record revision, commit, and SHA-256.

For a directory:

1. enumerate files;
2. normalize paths;
3. sort paths;
4. calculate each SHA-256;
5. build an ordered manifest;
6. hash the manifest.

### Exact filesets

Approve the complete list of files that may be created or modified before an
implementation order is issued.

### Structured editing

Parse and serialize JSON as data. Do not inject multiline JSON through string
replacement.

### Encoding control

Use UTF-8 without BOM and LF endings. Run `git diff --check` before commit.

### Narrow recovery

Recovery scripts must use an exact allowlist, distinguish tracked from
untracked paths, and stop when unrelated changes appear.

### EOL-noise diagnosis

When a diff appears symmetric or unexpectedly large, compare logical content,
normalized hashes, and whitespace-insensitive diffs before claiming a real
change.

### Remote verification

After push, fetch the immutable commit and compare it with the intended branch.
Do not claim remote success from local console output alone.

## Anti-patterns

- infer target platform from the technical executor;
- treat a commit, status, preflight, or installed skill as authorization;
- mix audit and correction in the same pass;
- delete an incorrect decision instead of superseding it;
- use broad destructive recovery such as an unbounded hard reset;
- allow a live dependency from a consumer to a producer working tree;
- approve architecture before exact platform and target paths are known;
- convert silence or partial agreement into approval.

## Completion criteria

An audit is complete only when findings, evidence, scope, limitations, and the
single next authorized action are explicit. A correction is complete only after
independent verification.
