# ERR-LAB-001 — Executor confused with target platform

Status: `CONTAINED`
Severity: `HIGH`
Detected: `2026-06-28`
Updated-At: `2026-06-28`
Projects: `LAB`, `MammothSkills`, `Symphonie`

## Observed behavior

A Codex execution role was incorrectly treated as evidence that three audited
Claude skills should be implemented under `targets/codex/`.

## Expected behavior

The intended runtime and approved classification determine the target
platform. The agent editing a repository does not determine it.

```text
Codex edits repository != artifact belongs to Codex
Claude skill -> Claude
Codex skill -> Codex
```

## Root cause

The workflow mixed who performs a technical repository change with where the
produced skill is installed and executed.

## Impact and containment

- the incorrect `targets/codex/` architecture and fileset were revoked;
- Codex implementation authorization was removed;
- MammothSkills is blocked pending target-platform correction;
- no implementation or release was created from the invalid order.

## Required preventive fields

Every skill audit records these values before target paths are approved:

```text
source_platform
target_platform
runtime_owner
technical_executor
consumer_repository
```

Explicit rule: `technical_executor must never determine target_platform`.

## Verification required before closure

- an approved superseding decision in MammothSkills;
- corrected Claude target paths;
- a superseded fileset and execution order;
- remote evidence that no invalid Codex target package was implemented.

This error remains contained, not verified or closed.
