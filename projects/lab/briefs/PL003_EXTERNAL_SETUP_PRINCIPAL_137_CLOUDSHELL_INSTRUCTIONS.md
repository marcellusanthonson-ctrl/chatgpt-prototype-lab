# PL003 external setup principal — CloudShell instructions

Document role: OPERATOR_INSTRUCTIONS
Authority effect: NONE
Execution authority: `AUTHORIZATION_LAB_PL003_TEMPORARY_SETUP_PRINCIPAL_EXTERNAL_CREATION_137`

## Purpose

Run the canonical script manually from AWS CloudShell using an already authorized human administrative session or an external security custodian. The script creates or verifies only:

- `PL003TemporaryGateOperatorSetupBoundary`
- `PL003TemporaryGateOperatorSetup`
- `PL003TemporaryGateOperatorSetupExactMutation`
- `PL003AssumeTemporaryGateOperatorSetup`

It does not assume the setup role, create the final gate operator, simulate permissions, run Terraform, provision resources, or execute Product Leadership Test 003.

## Preconditions

1. Verify the live `main` HEAD and read `project-sources/chatgpt/START_HERE.md` in canonical order.
2. Confirm authorization 137 is `GRANTED` and unconsumed.
3. Use AWS CloudShell from the intended AWS account.
4. The active AWS identity must be a human-authorized administrative session or external custodian session.
5. Do not use root, `pl003-bootstrap-operator` directly, Codex, or a general administrative credential exposed to automation.
6. Do not paste account IDs, ARNs, credentials, tokens, or MFA codes into GitHub or ChatGPT.

## Execution

From a clean checkout of the repository at the verified live HEAD:

```bash
chmod 700 projects/lab/scripts/Invoke-PL003ExternalSetupPrincipal137CloudShell.sh
projects/lab/scripts/Invoke-PL003ExternalSetupPrincipal137CloudShell.sh
```

The script performs one STS identity read, verifies the exact bootstrap user, generates account-scoped IAM documents locally, displays a redacted caller identity, and requires this exact confirmation phrase:

```text
CREATE-PL003-TEMPORARY-SETUP
```

Before any mutation it reads collision baselines. Existing objects are preserved only when semantically exact. Any mismatch blocks without modification.

## Expected terminal outputs

Success:

```text
PASS_SETUP_PRINCIPAL_CREATED_AND_VERIFIED_NOT_USED
```

Allowed blocked outcomes include:

- `BLOCKED_EXISTING_RESOURCE_MISMATCH`
- `BLOCKED_NO_AUTHORIZED_EXTERNAL_CREATOR`
- `BLOCKED_BOOTSTRAP_ASSUME_SCOPE_CANNOT_BE_SAFELY_BOUNDED`
- `BLOCKED_ROLLBACK_NOT_PROVABLE`
- `BLOCKED_FAIL_CLOSED_OTHER`

## Rollback

After the first mutation, any subsequent error triggers reverse-order rollback. The script deletes only objects or inline policies created by the same attempt. It does not modify or delete preexisting matching resources.

## Evidence to retain

Retain the redacted terminal result, semantic SHA-256 values, the creator class, whether each resource was created or preserved, AWS read and mutation counts, rollback status, and explicit zero counts for setup-role assumption, final gate-operator mutation, simulation, Terraform, provisioning, and Test 003.

Do not treat a PASS as authority for Codex to use the setup role. A separate authorization is required.
