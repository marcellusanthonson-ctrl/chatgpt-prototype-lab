# Product Leadership Test 003 — static AWS preflight IaC

Status: `STATIC_DESIGN_ONLY_AWS_NOT_PROVISIONED`

This package expresses the approved disposable AWS security preflight as
Terraform. It does not authorize or perform provisioning, Test 003 execution,
secret creation, fixture generation, or Product Leadership activation.

## Technical choice

Terraform was selected because its native formatter and validator can check the
complete dependency graph locally after provider installation. The configuration:

- has no backend block and therefore defaults to local state if a future,
  separately authorized provisioning run is ever performed;
- has no provider credentials, profiles, assume-role configuration, or AWS data
  sources;
- creates no `aws_secretsmanager_secret_version`, Terraform output, test content,
  mapping, fixture, score, or oracle;
- requires placeholder account, region, principal ARNs, and external IDs only
  from a future bounded authorization;
- configures three disposable S3 buckets with versioning, SSE-KMS, public access
  block, ownership enforcement, and default Object Lock `GOVERNANCE` retention;
- separates artifact, immutable audit, and custody KMS keys;
- defines six distinct Codex task roles, a custodian role, a Claude read-only
  auditor role, and a bounded preflight controller role;
- applies a permission boundary and explicit deny policy to every role;
- sends CloudTrail management events and S3 object data events for all three
  buckets to the Object-Locked audit bucket.

## Static-only commands

The authorized validation sequence is:

```text
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

`init` downloads only the provider plugin and does not contact AWS. No `plan`,
`apply`, `destroy`, AWS CLI command, credential command, or CloudFormation
deployment belongs to this authorization.

## Future provisioning boundary

The future authorization brief is intentionally `DRAFT_NOT_AUTHORIZED`. It must
fix an isolated non-production account, region, retention period, budget alert,
nine distinct trust principals/external IDs, teardown handling, and evidence
release rules. A successful future preflight still must stop before Test 003.
