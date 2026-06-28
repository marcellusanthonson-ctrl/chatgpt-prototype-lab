# ERR-TOOLING-001 — PowerShell and repository-script failures

Status: `CORRECTED`
Severity: `MEDIUM`
Detected: `2026-06-28`
Updated-At: `2026-06-28`
Projects: `LAB`

## Failures observed

- BOM and CRLF caused `git diff --check` failures;
- literal PowerShell escape text was inserted into JSON;
- positional array arguments were assembled incorrectly;
- restore behavior was invalid for paths unknown to Git;
- multiline text replacement was fragile.

## Correction

- write UTF-8 without BOM and normalize canonical Git content to LF;
- parse and serialize JSON as structured data;
- build argument arrays explicitly before wrapper invocation;
- distinguish tracked, staged-new, and untracked paths during recovery;
- limit recovery to an exact allowlist;
- use patch-based or structural editing instead of fragile text injection.

## Preventive rule

Repository scripts must be syntax-checked and exercised against expected
states. Structured formats must be modified structurally, and recovery must
stop on unrelated changes.

## Lifecycle note

The correction is recorded, but repository evidence does not yet justify
`VERIFIED` or `CLOSED`.
