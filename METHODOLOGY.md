# LAB Methodology — Frozen v1.0

Document-ID: `lab.methodology`
Version: `1.0.0`
Status: `APPROVED`
Effective-Date: `2026-06-28`
Approver: Jonathan Martínez

## 1. Purpose

Git is the external, versioned, auditable memory for decisions, project state,
errors, evidence, and reusable practices across LAB, MammothSkills, and
Symphonie.

Git records a decision and its evidence. A commit does not create approval by
itself.

## 2. Project boundaries

### LAB

LAB governs the method and stores cross-project knowledge:

- authority and safety rules;
- decision and error taxonomy;
- audit methods;
- project registry;
- continuity state;
- reusable patterns.

LAB does not contain product code or authorize product execution.

### MammothSkills

MammothSkills creates, audits, adapts, tests, versions, and publishes skills.
It is a producer and source of truth, not the runtime where skills live.

- Skills for Claude live in Claude.
- Skills for Codex live in Codex.
- The agent that performs repository changes does not determine the target
  platform of the artifact.

### Symphonie

Symphonie consumes fixed releases and coordinates project execution. It records
which skill release is installed, its version, checksum, configuration, and
integration evidence.

MammothSkills must not write directly into Symphonie or another consumer.

## 3. Authority model

- Jonathan Martínez is the sole approver.
- ChatGPT coordinates, validates, audits, and issues bounded orders.
- Claude performs discovery and definition only when assigned.
- Codex performs technical execution only under a direct, explicit, bounded
  order.
- An installed skill, status report, preflight, plan, or commit is not an
  authorization.

Implementation, commit, push, pull request, merge, tag, release, deployment,
and consumer integration are separate permissions.

## 4. Canonical data

JSON is the structured source of truth. Markdown is the human-readable view.
Where both exist, Markdown must be generated from or verified against JSON.

Every approved artifact should record, when applicable:

- identifier and revision;
- status;
- approver and approval evidence;
- source commit;
- SHA-256 or directory digest;
- supersedes and superseded-by relationships.

## 5. Decision lifecycle

Valid states:

```text
DRAFT -> PROPOSED -> UNDER_REVIEW -> APPROVED
                     |               |
                     v               v
                  REJECTED       SUPERSEDED
```

Silence, continuation, partial agreement, or technical success do not equal
approval.

Incorrect decisions are not erased. A later decision explicitly supersedes
them and records the reason and consequences.

## 6. Error lifecycle

```text
OPEN -> CONTAINED -> CORRECTED -> VERIFIED -> CLOSED
```

A written correction is not enough to close an error. Verification evidence is
required.

## 7. Audit workflow

1. Establish exact repository, branch, commit, scope, and authority.
2. Verify a clean working tree or record all existing changes.
3. Freeze source baselines and calculate fingerprints.
4. Inventory exact candidate files without modifying them.
5. Compare implementation against approved contracts and real artifacts.
6. Separate observation, hypothesis, finding, correction, and approval.
7. Report findings before remediation unless a correction order is explicit.
8. Apply fail-closed behavior when evidence or authority is missing.
9. Validate exact changed files, line limits, JSON, encoding, tests, and hashes.
10. Record rollback and unresolved issues.

## 8. Techniques validated in practice

- immutable baselines and source registers;
- SHA-256 fingerprints for files and ordered directory manifests;
- exact filesets before implementation;
- preflight separated from execution;
- audit-only passes before correction;
- remote commit and branch comparison;
- JSON parsing instead of text replacement for structured documents;
- UTF-8 without BOM and LF normalization;
- narrow recovery limited to known generated files;
- `git diff --check`, logical diff, and normalized comparisons for EOL noise;
- one logical transition per commit;
- explicit stop conditions and rollback instructions.

## 9. Mandatory stop conditions

Stop and mark the action `BLOCKED` when any of the following is unresolved:

- repository, branch, or HEAD mismatch;
- dirty state outside the approved scope;
- missing approval or direct order;
- ambiguous target platform or target path;
- changed baseline or stale fingerprint;
- unapproved dependency, connector, or consumer write;
- file outside the exact fileset;
- inability to execute a critical validation;
- contradiction between canonical JSON and Markdown.

## 10. Continuity

A new conversation must reconstruct context from the repository rather than
relying on conversational memory. Read in this order:

1. `LAB_CONTRACT.md`
2. `METHODOLOGY.md`
3. `CURRENT_STATE.md`
4. `registry/projects.json`
5. active project state
6. decisions in force
7. open errors
8. applicable patterns

This methodology remains in force until an explicitly approved decision
supersedes it.
