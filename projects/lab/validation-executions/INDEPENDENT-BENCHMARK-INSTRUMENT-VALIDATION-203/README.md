# Independent benchmark instrument validation 203

This directory is the only authorized output surface for authorization 203.

Execution order:

1. Codex Desktop A writes only under `codex-a/`.
2. ChatGPT publishes the mandatory post-test report.
3. Claude returns a read-only audit for `claude/`; Claude must not modify the repository.
4. ChatGPT publishes the mandatory post-test report.
5. Codex Desktop B writes only under `codex-b/` from a fresh session and worktree.
6. ChatGPT reconciles under `adjudication/`.

The benchmark package is immutable. All tests are currently `NOT_RUN`.
