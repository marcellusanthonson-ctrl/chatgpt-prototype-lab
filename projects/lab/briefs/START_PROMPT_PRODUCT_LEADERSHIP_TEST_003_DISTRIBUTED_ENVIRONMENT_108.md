# Start prompt — Product Leadership Test 003 distributed environment

Continue from `marcellusanthonson-ctrl/chatgpt-prototype-lab`, branch `main`.

Verify the live remote HEAD and read `project-sources/chatgpt/START_HERE.md`, following its full order.

Then read:

1. `projects/lab/test-designs/PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003/DISTRIBUTED_EXECUTION_PROTOCOL.json`
2. `projects/lab/briefs/BRIEF_PRODUCT_LEADERSHIP_TEST_003_DISTRIBUTED_EXECUTION_IMPLEMENTATION_108.json`
3. `projects/lab/test-designs/PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003/EXECUTION_CONTRACT.json`
4. `projects/lab/test-executions/PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003/PREFLIGHT_STOP_106.json`
5. `projects/lab/test-executions/PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003/PREFLIGHT_STOP_107.json`

Mode: `DISTRIBUTED_ENVIRONMENT_IMPLEMENTATION_FAIL_CLOSED`.

Do not execute Test 003 and do not generate fixture content, outputs, scores, oracles, mappings, or case material.

Your task is only to provision or describe the provisioned eight-role environment and publish a verifiable preflight package proving:

- distinct principals and environments;
- deny policies across incompatible roles;
- custodian-only mapping secret access;
- auditor read-only access;
- append-only logs and immutable externally timestamped checkpoints;
- canonical UTF-8/LF/no-BOM SHA-256 artifact exchange.

Multiple processes, worktrees, or sessions under shared principals, filesystem, credentials, or permissions do not satisfy isolation.

If any mandatory requirement cannot be demonstrated, publish a fail-closed stop package and stop before fixture generation.

Do not activate or integrate Product Leadership.
