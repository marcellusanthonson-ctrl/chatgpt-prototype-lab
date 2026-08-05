# LAB — Codex Desktop

Canonical entrypoint: `project-sources/chatgpt/START_HERE.md`
HEAD policy: `VERIFY_LIVE_AT_USE`
Sole approver: Jonathan Martínez

## Before acting

1. Verify the live remote `main` HEAD.
2. Read `project-sources/chatgpt/START_HERE.md`.
3. Load the assigned execution envelope, role profile, and context manifest.
4. Read only `ALWAYS` and `REQUIRED` sources initially.
5. Load `FILTERED` or `ON_TRIGGER` sources only when their selector or trigger matches.

## Boundaries

- Do not infer authorization from this file, a brief, a commit, or a PASS.
- Do not expand repositories, paths, credentials, runtime, product, or integration scope.
- Do not access another repository without explicit authorization.
- Apply `EXECUTION-LEARNING-FEEDBACK-LOOP-001` using only applicable incidents.
- Historical errors do not prove current recurrence.
- Role profiles define responsibility, not authority.
- Prefer deterministic validation over model self-assessment.
- Keep same-file edits, state changes, publication, and authorization consumption sequential.
- Parallelize only independent read or test work on disjoint surfaces.
- Do not expose or request private chain-of-thought.

## Close

Return the contract requested by the execution envelope and one next action.
