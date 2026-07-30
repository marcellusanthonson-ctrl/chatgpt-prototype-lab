#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# PL003 external setup principal creation for AUTHORIZATION 137.
# This script is intended for manual execution in AWS CloudShell by an already
# authorized human administrator or external security custodian.
# It MUST NOT be executed with root, the persistent bootstrap user credentials,
# or by Codex. It never assumes the role it creates.

readonly EXPECTED_REPOSITORY="marcellusanthonson-ctrl/chatgpt-prototype-lab"
readonly AUTHORIZATION_ID="AUTHORIZATION_LAB_PL003_TEMPORARY_SETUP_PRINCIPAL_EXTERNAL_CREATION_137"
readonly BOOTSTRAP_USER="pl003-bootstrap-operator"
readonly SETUP_BOUNDARY_NAME="PL003TemporaryGateOperatorSetupBoundary"
readonly SETUP_ROLE_NAME="PL003TemporaryGateOperatorSetup"
readonly SETUP_ROLE_POLICY_NAME="PL003TemporaryGateOperatorSetupExactMutation"
readonly BOOTSTRAP_GRANT_NAME="PL003AssumeTemporaryGateOperatorSetup"
readonly SOURCE_IDENTITY="pl003-temporary-gate-setup"
readonly MAX_SESSION_DURATION=3600

WORK_DIR="$(mktemp -d -t pl003-137-XXXXXXXX)"
CREATED_BOUNDARY=0
CREATED_ROLE=0
CREATED_ROLE_POLICY=0
CREATED_BOOTSTRAP_GRANT=0
ROLLBACK_REQUIRED=0
RESULT="BLOCKED_FAIL_CLOSED_OTHER"

cleanup_local() {
  rm -rf "$WORK_DIR"
}

canonical_json_file() {
  jq -S -c . "$1"
}

canonical_json_stream() {
  jq -S -c 'if type == "string" then fromjson else . end'
}

sha256_file_semantic() {
  canonical_json_file "$1" | sha256sum | awk '{print $1}'
}

redact_arn() {
  sed -E 's/[0-9]{12}/<REDACTED_ACCOUNT_ID>/g'
}

fail() {
  RESULT="$1"
  echo "ERROR: ${2:-$1}" >&2
  return 1
}

rollback() {
  local rollback_failed=0
  if [[ "$ROLLBACK_REQUIRED" -ne 1 ]]; then
    return 0
  fi

  echo "Executing mandatory rollback in reverse order..." >&2

  if [[ "$CREATED_BOOTSTRAP_GRANT" -eq 1 ]]; then
    aws iam delete-user-policy \
      --user-name "$BOOTSTRAP_USER" \
      --policy-name "$BOOTSTRAP_GRANT_NAME" >/dev/null || rollback_failed=1
  fi

  if [[ "$CREATED_ROLE_POLICY" -eq 1 ]]; then
    aws iam delete-role-policy \
      --role-name "$SETUP_ROLE_NAME" \
      --policy-name "$SETUP_ROLE_POLICY_NAME" >/dev/null || rollback_failed=1
  fi

  if [[ "$CREATED_ROLE" -eq 1 ]]; then
    aws iam delete-role \
      --role-name "$SETUP_ROLE_NAME" >/dev/null || rollback_failed=1
  fi

  if [[ "$CREATED_BOUNDARY" -eq 1 ]]; then
    aws iam delete-policy \
      --policy-arn "$SETUP_BOUNDARY_ARN" >/dev/null || rollback_failed=1
  fi

  if [[ "$rollback_failed" -ne 0 ]]; then
    RESULT="BLOCKED_ROLLBACK_NOT_PROVABLE"
    echo "Rollback could not be proven complete." >&2
    return 1
  fi

  echo "Rollback completed." >&2
}

on_exit() {
  local exit_code=$?
  if [[ "$exit_code" -ne 0 ]]; then
    rollback || true
  fi
  cleanup_local
  echo "FINAL_CLASSIFICATION=$RESULT"
  exit "$exit_code"
}
trap on_exit EXIT

command -v aws >/dev/null 2>&1 || fail "BLOCKED_FAIL_CLOSED_OTHER" "AWS CLI is required."
command -v jq >/dev/null 2>&1 || fail "BLOCKED_FAIL_CLOSED_OTHER" "jq is required."
command -v sha256sum >/dev/null 2>&1 || fail "BLOCKED_FAIL_CLOSED_OTHER" "sha256sum is required."

AWS_PAGER=""
export AWS_PAGER

CALLER_JSON="$(aws sts get-caller-identity --output json)" || fail "BLOCKED_NO_AUTHORIZED_EXTERNAL_CREATOR" "Unable to establish the external creator identity."
ACCOUNT_ID="$(jq -r '.Account' <<<"$CALLER_JSON")"
CALLER_ARN="$(jq -r '.Arn' <<<"$CALLER_JSON")"

[[ "$ACCOUNT_ID" =~ ^[0-9]{12}$ ]] || fail "BLOCKED_FAIL_CLOSED_OTHER" "Unexpected account identifier shape."
[[ "$CALLER_ARN" != *":root" ]] || fail "BLOCKED_NO_AUTHORIZED_EXTERNAL_CREATOR" "Root is prohibited."
[[ "$CALLER_ARN" != *":user/${BOOTSTRAP_USER}" ]] || fail "BLOCKED_NO_AUTHORIZED_EXTERNAL_CREATOR" "Direct mutation with the persistent bootstrap user is prohibited."

readonly SETUP_BOUNDARY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${SETUP_BOUNDARY_NAME}"
readonly SETUP_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${SETUP_ROLE_NAME}"
readonly BOOTSTRAP_USER_ARN="arn:aws:iam::${ACCOUNT_ID}:user/${BOOTSTRAP_USER}"
readonly GATE_BOUNDARY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/PL003EffectivePermissionGateOperatorBoundary"
readonly GATE_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/PL003EffectivePermissionGateOperator"

cat >"$WORK_DIR/setup-boundary.json" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CallerIdentity",
      "Effect": "Allow",
      "Action": "sts:GetCallerIdentity",
      "Resource": "*"
    },
    {
      "Sid": "ReadExactSetupAndTargetConfiguration",
      "Effect": "Allow",
      "Action": [
        "iam:GetPolicy",
        "iam:GetPolicyVersion",
        "iam:ListPolicyVersions",
        "iam:GetRole",
        "iam:ListRolePolicies",
        "iam:GetRolePolicy",
        "iam:ListAttachedRolePolicies",
        "iam:ListRoleTags",
        "iam:GetUserPolicy",
        "iam:ListUserPolicies"
      ],
      "Resource": [
        "$GATE_BOUNDARY_ARN",
        "$GATE_ROLE_ARN",
        "$BOOTSTRAP_USER_ARN"
      ]
    },
    {
      "Sid": "CreateAndRollbackExactGateBoundary",
      "Effect": "Allow",
      "Action": ["iam:CreatePolicy", "iam:DeletePolicy"],
      "Resource": "$GATE_BOUNDARY_ARN"
    },
    {
      "Sid": "CreateAndRollbackExactGateRole",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:PutRolePermissionsBoundary",
        "iam:DeleteRolePermissionsBoundary",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy"
      ],
      "Resource": "$GATE_ROLE_ARN"
    },
    {
      "Sid": "CreateAndRollbackExactBootstrapGrant",
      "Effect": "Allow",
      "Action": ["iam:PutUserPolicy", "iam:DeleteUserPolicy"],
      "Resource": "$BOOTSTRAP_USER_ARN"
    },
    {
      "Sid": "DenyUnsafeAdministration",
      "Effect": "Deny",
      "Action": [
        "iam:CreateUser", "iam:DeleteUser",
        "iam:CreateAccessKey", "iam:UpdateAccessKey", "iam:DeleteAccessKey",
        "iam:CreateLoginProfile", "iam:UpdateLoginProfile", "iam:DeleteLoginProfile",
        "iam:AttachRolePolicy", "iam:DetachRolePolicy",
        "iam:AttachUserPolicy", "iam:DetachUserPolicy",
        "iam:PassRole",
        "iam:UpdateAssumeRolePolicy",
        "iam:UpdateRole", "iam:UpdateRoleDescription",
        "iam:Tag*", "iam:Untag*",
        "sts:AssumeRole"
      ],
      "Resource": "*"
    }
  ]
}
JSON

# Boundary and identity policy intentionally share the same maximum surface.
cp "$WORK_DIR/setup-boundary.json" "$WORK_DIR/setup-identity-policy.json"

cat >"$WORK_DIR/setup-trust.json" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BootstrapAssumeTemporarySetupWithMFAOnly",
      "Effect": "Allow",
      "Principal": {"AWS": "$BOOTSTRAP_USER_ARN"},
      "Action": "sts:AssumeRole",
      "Condition": {
        "Bool": {"aws:MultiFactorAuthPresent": "true"},
        "NumericLessThanEquals": {"aws:MultiFactorAuthAge": "300"},
        "StringEquals": {"sts:SourceIdentity": "$SOURCE_IDENTITY"}
      }
    }
  ]
}
JSON

cat >"$WORK_DIR/bootstrap-grant.json" <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AssumeExactTemporarySetupWithMFAOnly",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "$SETUP_ROLE_ARN",
      "Condition": {
        "Bool": {"aws:MultiFactorAuthPresent": "true"},
        "NumericLessThanEquals": {"aws:MultiFactorAuthAge": "300"},
        "StringEquals": {"sts:SourceIdentity": "$SOURCE_IDENTITY"}
      }
    }
  ]
}
JSON

for file in setup-boundary.json setup-identity-policy.json setup-trust.json bootstrap-grant.json; do
  jq -e . "$WORK_DIR/$file" >/dev/null || fail "BLOCKED_FAIL_CLOSED_OTHER" "Invalid generated JSON: $file"
done

# Confirm the exact bootstrap principal exists before any mutation.
aws iam get-user --user-name "$BOOTSTRAP_USER" --output json >/dev/null \
  || fail "BLOCKED_BOOTSTRAP_ASSUME_SCOPE_CANNOT_BE_SAFELY_BOUNDED" "Exact bootstrap user not found or unreadable."

printf '\nAuthorization: %s\nRepository: %s\n' "$AUTHORIZATION_ID" "$EXPECTED_REPOSITORY"
printf 'External creator ARN: %s\n' "$(printf '%s' "$CALLER_ARN" | redact_arn)"
printf 'Target account: <REDACTED_ACCOUNT_ID>\n'
printf 'This creates ONLY the temporary setup boundary, role, inline role policy, and bootstrap grant.\n'
printf 'It DOES NOT assume the role or create the final gate operator.\n\n'
read -r -p 'Type exactly CREATE-PL003-TEMPORARY-SETUP to continue: ' CONFIRMATION
[[ "$CONFIRMATION" == "CREATE-PL003-TEMPORARY-SETUP" ]] \
  || fail "BLOCKED_FAIL_CLOSED_OTHER" "Human confirmation was not provided."

# Collision baseline: existing resources must be semantically exact or execution stops.
BOUNDARY_EXISTS=0
ROLE_EXISTS=0
ROLE_POLICY_EXISTS=0
BOOTSTRAP_GRANT_EXISTS=0

EXISTING_BOUNDARY_ARN="$(aws iam list-policies --scope Local --query "Policies[?PolicyName=='${SETUP_BOUNDARY_NAME}'].Arn | [0]" --output text)"
if [[ "$EXISTING_BOUNDARY_ARN" != "None" && -n "$EXISTING_BOUNDARY_ARN" ]]; then
  [[ "$EXISTING_BOUNDARY_ARN" == "$SETUP_BOUNDARY_ARN" ]] \
    || fail "BLOCKED_EXISTING_RESOURCE_MISMATCH" "Boundary name collision resolved to an unexpected ARN."
  BOUNDARY_EXISTS=1
  DEFAULT_VERSION="$(aws iam get-policy --policy-arn "$SETUP_BOUNDARY_ARN" --query 'Policy.DefaultVersionId' --output text)"
  aws iam get-policy-version --policy-arn "$SETUP_BOUNDARY_ARN" --version-id "$DEFAULT_VERSION" --query 'PolicyVersion.Document' --output json \
    | canonical_json_stream >"$WORK_DIR/observed-boundary.json"
  [[ "$(canonical_json_file "$WORK_DIR/setup-boundary.json")" == "$(cat "$WORK_DIR/observed-boundary.json")" ]] \
    || fail "BLOCKED_EXISTING_RESOURCE_MISMATCH" "Existing setup boundary is not semantically exact."
fi

if aws iam get-role --role-name "$SETUP_ROLE_NAME" --output json >"$WORK_DIR/observed-role-full.json" 2>/dev/null; then
  ROLE_EXISTS=1
  jq '.Role.AssumeRolePolicyDocument' "$WORK_DIR/observed-role-full.json" | canonical_json_stream >"$WORK_DIR/observed-trust.json"
  [[ "$(canonical_json_file "$WORK_DIR/setup-trust.json")" == "$(cat "$WORK_DIR/observed-trust.json")" ]] \
    || fail "BLOCKED_EXISTING_RESOURCE_MISMATCH" "Existing setup trust policy is not semantically exact."
  [[ "$(jq -r '.Role.MaxSessionDuration' "$WORK_DIR/observed-role-full.json")" == "$MAX_SESSION_DURATION" ]] \
    || fail "BLOCKED_EXISTING_RESOURCE_MISMATCH" "Existing setup role max session duration differs."
  [[ "$(jq -r '.Role.PermissionsBoundary.PermissionsBoundaryArn // empty' "$WORK_DIR/observed-role-full.json")" == "$SETUP_BOUNDARY_ARN" ]] \
    || fail "BLOCKED_EXISTING_RESOURCE_MISMATCH" "Existing setup role boundary differs."
fi

if aws iam get-role-policy --role-name "$SETUP_ROLE_NAME" --policy-name "$SETUP_ROLE_POLICY_NAME" --query 'PolicyDocument' --output json 2>/dev/null \
  | canonical_json_stream >"$WORK_DIR/observed-role-policy.json"; then
  ROLE_POLICY_EXISTS=1
  [[ "$(canonical_json_file "$WORK_DIR/setup-identity-policy.json")" == "$(cat "$WORK_DIR/observed-role-policy.json")" ]] \
    || fail "BLOCKED_EXISTING_RESOURCE_MISMATCH" "Existing setup inline role policy is not semantically exact."
fi

if aws iam get-user-policy --user-name "$BOOTSTRAP_USER" --policy-name "$BOOTSTRAP_GRANT_NAME" --query 'PolicyDocument' --output json 2>/dev/null \
  | canonical_json_stream >"$WORK_DIR/observed-bootstrap-grant.json"; then
  BOOTSTRAP_GRANT_EXISTS=1
  [[ "$(canonical_json_file "$WORK_DIR/bootstrap-grant.json")" == "$(cat "$WORK_DIR/observed-bootstrap-grant.json")" ]] \
    || fail "BLOCKED_EXISTING_RESOURCE_MISMATCH" "Existing bootstrap grant is not semantically exact."
fi

# A role policy cannot legitimately preexist without its role.
[[ "$ROLE_POLICY_EXISTS" -eq 0 || "$ROLE_EXISTS" -eq 1 ]] \
  || fail "BLOCKED_EXISTING_RESOURCE_MISMATCH" "Inline role policy state is inconsistent."

ROLLBACK_REQUIRED=1

if [[ "$BOUNDARY_EXISTS" -eq 0 ]]; then
  aws iam create-policy \
    --policy-name "$SETUP_BOUNDARY_NAME" \
    --description "Disposable PL003 setup-role permissions boundary; authorization 137." \
    --policy-document "file://$WORK_DIR/setup-boundary.json" >/dev/null
  CREATED_BOUNDARY=1
fi

if [[ "$ROLE_EXISTS" -eq 0 ]]; then
  aws iam create-role \
    --role-name "$SETUP_ROLE_NAME" \
    --path / \
    --assume-role-policy-document "file://$WORK_DIR/setup-trust.json" \
    --permissions-boundary "$SETUP_BOUNDARY_ARN" \
    --max-session-duration "$MAX_SESSION_DURATION" \
    --description "Disposable one-use PL003 gate-operator setup role; authorization 137." >/dev/null
  CREATED_ROLE=1
fi

if [[ "$ROLE_POLICY_EXISTS" -eq 0 ]]; then
  aws iam put-role-policy \
    --role-name "$SETUP_ROLE_NAME" \
    --policy-name "$SETUP_ROLE_POLICY_NAME" \
    --policy-document "file://$WORK_DIR/setup-identity-policy.json"
  CREATED_ROLE_POLICY=1
fi

if [[ "$BOOTSTRAP_GRANT_EXISTS" -eq 0 ]]; then
  aws iam put-user-policy \
    --user-name "$BOOTSTRAP_USER" \
    --policy-name "$BOOTSTRAP_GRANT_NAME" \
    --policy-document "file://$WORK_DIR/bootstrap-grant.json"
  CREATED_BOOTSTRAP_GRANT=1
fi

# Read-back verification. The setup role is deliberately NOT assumed.
aws iam get-role --role-name "$SETUP_ROLE_NAME" --output json >"$WORK_DIR/final-role.json"
jq '.Role.AssumeRolePolicyDocument' "$WORK_DIR/final-role.json" | canonical_json_stream >"$WORK_DIR/final-trust.json"
[[ "$(canonical_json_file "$WORK_DIR/setup-trust.json")" == "$(cat "$WORK_DIR/final-trust.json")" ]] \
  || fail "BLOCKED_FAIL_CLOSED_OTHER" "Final trust verification failed."
[[ "$(jq -r '.Role.MaxSessionDuration' "$WORK_DIR/final-role.json")" == "$MAX_SESSION_DURATION" ]] \
  || fail "BLOCKED_FAIL_CLOSED_OTHER" "Final max session duration verification failed."
[[ "$(jq -r '.Role.PermissionsBoundary.PermissionsBoundaryArn // empty' "$WORK_DIR/final-role.json")" == "$SETUP_BOUNDARY_ARN" ]] \
  || fail "BLOCKED_FAIL_CLOSED_OTHER" "Final boundary attachment verification failed."

FINAL_DEFAULT_VERSION="$(aws iam get-policy --policy-arn "$SETUP_BOUNDARY_ARN" --query 'Policy.DefaultVersionId' --output text)"
aws iam get-policy-version --policy-arn "$SETUP_BOUNDARY_ARN" --version-id "$FINAL_DEFAULT_VERSION" --query 'PolicyVersion.Document' --output json \
  | canonical_json_stream >"$WORK_DIR/final-boundary.json"
[[ "$(canonical_json_file "$WORK_DIR/setup-boundary.json")" == "$(cat "$WORK_DIR/final-boundary.json")" ]] \
  || fail "BLOCKED_FAIL_CLOSED_OTHER" "Final boundary document verification failed."

aws iam get-role-policy --role-name "$SETUP_ROLE_NAME" --policy-name "$SETUP_ROLE_POLICY_NAME" --query 'PolicyDocument' --output json \
  | canonical_json_stream >"$WORK_DIR/final-role-policy.json"
[[ "$(canonical_json_file "$WORK_DIR/setup-identity-policy.json")" == "$(cat "$WORK_DIR/final-role-policy.json")" ]] \
  || fail "BLOCKED_FAIL_CLOSED_OTHER" "Final inline role policy verification failed."

aws iam get-user-policy --user-name "$BOOTSTRAP_USER" --policy-name "$BOOTSTRAP_GRANT_NAME" --query 'PolicyDocument' --output json \
  | canonical_json_stream >"$WORK_DIR/final-bootstrap-grant.json"
[[ "$(canonical_json_file "$WORK_DIR/bootstrap-grant.json")" == "$(cat "$WORK_DIR/final-bootstrap-grant.json")" ]] \
  || fail "BLOCKED_FAIL_CLOSED_OTHER" "Final bootstrap grant verification failed."

RESULT="PASS_SETUP_PRINCIPAL_CREATED_AND_VERIFIED_NOT_USED"
ROLLBACK_REQUIRED=0

cat <<OUTPUT
RESULT=$RESULT
ACCOUNT=<REDACTED_ACCOUNT_ID>
EXTERNAL_CREATOR=$(printf '%s' "$CALLER_ARN" | redact_arn)
SETUP_BOUNDARY_NAME=$SETUP_BOUNDARY_NAME
SETUP_ROLE_NAME=$SETUP_ROLE_NAME
SETUP_ROLE_POLICY_NAME=$SETUP_ROLE_POLICY_NAME
BOOTSTRAP_GRANT_NAME=$BOOTSTRAP_GRANT_NAME
SETUP_ROLE_ASSUMED=0
GATE_OPERATOR_MUTATIONS=0
SIMULATION_CALLS=0
TERRAFORM_CALLS=0
PROVISIONING_CALLS=0
TEST_003_CALLS=0
TRUST_SEMANTIC_SHA256=$(sha256_file_semantic "$WORK_DIR/setup-trust.json")
BOUNDARY_SEMANTIC_SHA256=$(sha256_file_semantic "$WORK_DIR/setup-boundary.json")
IDENTITY_POLICY_SEMANTIC_SHA256=$(sha256_file_semantic "$WORK_DIR/setup-identity-policy.json")
BOOTSTRAP_GRANT_SEMANTIC_SHA256=$(sha256_file_semantic "$WORK_DIR/bootstrap-grant.json")
OUTPUT
