# ERR-LAB-001 — Executor confused with target platform

Status: `CONTAINED`
Severity: `HIGH`
Detected: `2026-06-28`
Projects: `LAB`, `MammothSkills`, `Symphonie`

## Observed behavior

A Codex execution role was incorrectly treated as evidence that the audited
Claude skills should be implemented under `targets/codex/`.

## Expected behavior

The target platform is determined by the skill's intended runtime and approved
classification, not by the agent that edits the repository.

```text
Codex edits repository != artifact belongs to Codex
Claude skill -> Claude
Codex skill -> Codex
```

## Root cause

The workflow mixed two independent dimensions:

1. who performs a technical repository change;
2. where the produced skill is installed and executed.

## Impact

- incorrect `targets/codex/` architecture for MS-001;
- incorrect bounded fileset;
- an implementation order was issued against the wrong platform target;
- user confidence was damaged.

## Containment

- previous implementation order revoked;
- Codex implementation authorization removed;
- MammothSkills state marked blocked pending target-platform correction;
- no implementation or release was created from the invalid order.

## Preventive rule

Every skill audit must explicitly record these fields before target paths are
approved:

```text
source_platform
target_platform
runtime_owner
technical_executor
consumer_repository
```

`technical_executor` must never be used to infer `target_platform`.

## Verification required before closure

- approved superseding decision in MammothSkills;
- corrected Claude target paths;
- superseded fileset and execution order;
- remote verification that no invalid Codex target package was implemented.

---

# ERR-LAB-002 — Overcomplicated correction after conceptual error

Status: `CONTAINED`
Severity: `MEDIUM`
Detected: `2026-06-28`

## Observed behavior

After the first target-platform mistake, the correction introduced additional
classifications and split adaptations instead of applying the user's simple
rule: MammothSkills produces skills; each skill lives in its native platform.

## Root cause

The response attempted to redesign the architecture before restating and
locking the user's explicit model.

## Preventive rule

When the user supplies a simpler governing rule:

1. restate it literally;
2. compare current artifacts against it;
3. identify only the minimal correction;
4. do not introduce new architecture without explicit need and approval.

---

# ERR-TOOLING-001 — PowerShell approval script failures

Status: `CORRECTED`
Severity: `MEDIUM`
Detected: `2026-06-28`

## Failures observed

- BOM and CRLF caused `git diff --check` failures;
- literal PowerShell `` `n `` was inserted into JSON;
- array concatenation was passed incorrectly as a positional argument;
- `git restore --staged` was attempted on a path unknown to Git.

## Techniques that resolved them

- UTF-8 without BOM using `.NET UTF8Encoding(false)`;
- explicit LF normalization;
- parse and serialize JSON as an object instead of text replacement;
- build argument arrays before passing them to wrapper functions;
- distinguish tracked, staged-new, and untracked paths during recovery;
- restrict recovery to an exact allowlist and stop on unrelated changes.

## Preventive rule

Generated repository scripts must be syntax-checked and tested against the
expected recovery states before being given to the user. Structured formats
must be modified structurally, never by fragile multiline text injection.
