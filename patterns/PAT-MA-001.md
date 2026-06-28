# PAT-MA-001 — Codex executes without autonomous authority

Status: `VALIDATED`
Scope: `LAB`, `MammothSkills`, `Symphonie`
Updated-At: `2026-06-28`

## Intent

Keep technical execution separate from authority, approval, platform
classification, and scope selection.

## Procedure

1. Require a direct, explicit, bounded order before execution.
2. Verify repository, branch, HEAD, fileset, and permissions.
3. Stop when evidence or authority is absent or ambiguous.
4. Treat implementation, commit, push, release, and integration as separate
   permissions.
5. Never infer target platform from Codex being the technical executor.

## Anti-patterns

- starting from a plan, preflight, installed skill, or status report alone;
- expanding scope because a change appears useful;
- assigning Claude-targeted skills to Codex because Codex edits a repository;
- treating a successful commit as approval.

## Evidence

- `LAB_CONTRACT.md`, section 5;
- `METHODOLOGY.md`, sections 2 and 3;
- legacy `patterns/multi-agent/PAT-MA-001-codex-executor-only.md`.
