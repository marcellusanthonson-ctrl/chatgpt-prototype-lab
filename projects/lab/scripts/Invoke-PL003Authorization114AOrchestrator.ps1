[CmdletBinding()]
param(
    [switch]$LocalClosureTest,
    [switch]$LocalAttemptPathTest,
    [string]$EvidenceDirectoryOverride
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$canonicalEvidenceDirectory = Join-Path $repositoryRoot 'projects\lab\evidence'
$evidenceDirectory = if ([string]::IsNullOrWhiteSpace($EvidenceDirectoryOverride)) {
    $canonicalEvidenceDirectory
} else {
    $EvidenceDirectoryOverride
}
$evidenceBaseName = 'EVD-LAB-PL003-AWS-REPLACEMENT-SESSION-114A'
$legacyEvidencePath = Join-Path $evidenceDirectory "$evidenceBaseName.json"
$attemptNumber = 1
do {
    $attemptId = 'ATTEMPT-{0:D3}' -f $attemptNumber
    $attemptFileName = "$evidenceBaseName-$attemptId.json"
    $evidencePath = Join-Path $evidenceDirectory $attemptFileName
    if (-not (Test-Path -LiteralPath $evidencePath)) {
        break
    }
    $attemptNumber++
    if ($attemptNumber -gt 999) {
        throw 'ATTEMPT_PATH_SPACE_EXHAUSTED'
    }
} while ($true)

$predecessorFileName = if ($attemptNumber -gt 1) {
    "$evidenceBaseName-ATTEMPT-{0:D3}.json" -f ($attemptNumber - 1)
} elseif (Test-Path -LiteralPath $legacyEvidencePath) {
    "$evidenceBaseName.json"
} else {
    $null
}
$predecessorEvidence = if ($null -eq $predecessorFileName) {
    $null
} else {
    "projects/lab/evidence/$predecessorFileName"
}
$evidenceRelativePath = "projects/lab/evidence/$attemptFileName"
$isLocalTest = $LocalClosureTest -or $LocalAttemptPathTest
$sourceProfile = 'pl003-bootstrap'
$mfaReferenceProfile = 'pl003-plan-operator'
$expectedBootstrapPrincipal = 'pl003-bootstrap-operator'
$expectedRegion = 'sa-east-1'
$durationSeconds = 3600

$setupRoleName = 'PL003PreflightIAMSetupOperator'
$setupBoundaryName = 'PL003IAMSetupBoundary114'
$setupPolicyName = 'PL003IAMSetupExecution114'
$targetRoleName = 'PL003PreflightProvisioningOperator'
$targetBoundaryName = 'PL003PreflightProvisioningBoundary'
$targetPolicyName = 'PL003PreflightProvisioningExecution'
$planRoleName = 'PL003PreflightPlanOperator'
$provisioningProfileName = 'pl003-provisioning-operator'

$credentialEnvironmentNames = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)
$temporaryEnvironmentNames = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN',
    'AWS_PROFILE',
    'AWS_DEFAULT_PROFILE',
    'AWS_REGION',
    'AWS_DEFAULT_REGION',
    'AWS_EC2_METADATA_DISABLED'
)

$priorEnvironment = @{}
foreach ($name in $temporaryEnvironmentNames) {
    $priorEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}

$result = [ordered]@{
    schema_version = '1.0.0'
    evidence_id = "$evidenceBaseName-$attemptId"
    attempt_id = $attemptId
    predecessor_evidence = $predecessorEvidence
    evidence_path = $evidenceRelativePath
    project_id = 'lab'
    kind = 'REDACTED_AWS_REPLACEMENT_SESSION_AND_IAM_BOOTSTRAP_EXECUTION_EVIDENCE'
    status = 'IN_PROGRESS'
    authorization_id = 'AUTHORIZATION_LAB_PL003_AWS_ONE_TIME_IAM_BOOTSTRAP_114A'
    parent_authorization_id = 'AUTHORIZATION_LAB_PL003_AWS_ONE_TIME_IAM_BOOTSTRAP_114'
    related_authorization_id = 'AUTHORIZATION_LAB_PL003_AWS_BOUNDED_PROVISIONING_OPERATOR_113'
    executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
    branch = 'main'
    execution_head = $null
    replacement_session = [ordered]@{
        get_session_token_calls = 0
        mfa_backed = $false
        maximum_session_seconds = $durationSeconds
        storage = 'PROCESS_MEMORY_ONLY'
        temporary_credentials_printed = $false
        temporary_credentials_persisted = $false
        cleared_at_end = $false
    }
    bootstrap_identity = [ordered]@{
        expected = 'IAM_USER_SESSION_pl003-bootstrap-operator'
        sts_verified = $false
        full_account_id_recorded = $false
    }
    pre_mutation_gate = [ordered]@{
        bootstrap_simulation_completed = $false
        all_required_setup_and_teardown_actions_allowed = $false
        aws_mutations_before_gate = 0
    }
    setup_operator = [ordered]@{
        role_created = $false
        boundary_created = $false
        execution_policy_created = $false
        policy_attached = $false
        assumed_role_sts_verified = $false
        mfa_trust_verified = $false
        boundary_verified = $false
        maximum_session_seconds = $durationSeconds
    }
    authorization_113 = [ordered]@{
        status = 'NOT_STARTED'
        provisioning_role_created = $false
        boundary_created = $false
        execution_policy_created = $false
        assumed_role_sts_verified = $false
        effective_scope_tests = 'NOT_EXECUTED'
        plan_operator_unchanged = 'NOT_VERIFIED'
    }
    root_security_visibility = [ordered]@{
        get_account_summary = 'NOT_EXECUTED'
        root_mfa_enabled = 'NOT_VERIFIED'
        root_access_keys_absent = 'NOT_VERIFIED'
        root_identity_used = $false
    }
    teardown = [ordered]@{
        target_partial_artifacts_removed_if_required = $false
        setup_role_removed = $false
        setup_boundary_removed = $false
        setup_execution_policy_removed = $false
        setup_profile_present = $false
        complete = $false
    }
    aws_calls = [ordered]@{
        sts_get_session_token = 0
        sts_other = 0
        iam_read_or_simulation = 0
        iam_mutation = 0
        terraform = 0
        preflight_112_resource_mutation = 0
    }
    forbidden_effects = [ordered]@{
        plan_operator_modified = $false
        iam_users_created = 0
        access_keys_created = 0
        administrator_access_used = $false
        terraform_executed = $false
        product_leadership_test_003_executed = $false
        product_leadership_active = $false
        product_leadership_integrated = $false
    }
    failure_code = $null
    redaction = [ordered]@{
        full_account_id_included = $false
        full_principal_arns_included = $false
        credentials_tokens_or_mfa_codes_included = $false
    }
    result = 'IN_PROGRESS'
}

$secureTotp = $null
$totpBstr = [IntPtr]::Zero
$totp = $null
$sessionResponse = $null
$bootstrapCredentials = $null
$setupCredentials = $null
$targetCredentials = $null
$accountId = $null
$bootstrapUserArn = $null
$setupRoleArn = $null
$setupBoundaryArn = $null
$setupPolicyArn = $null
$targetRoleArn = $null
$targetBoundaryArn = $null
$targetPolicyArn = $null
$subjectBoundaryArn = $null
$setupBoundaryCreated = $false
$setupPolicyCreated = $false
$setupRoleCreated = $false
$setupAttached = $false
$targetBoundaryCreated = $false
$targetPolicyCreated = $false
$targetRoleCreated = $false
$targetAttached = $false
$targetVerified = $false
$planBaselineHash = $null
$teardownFailures = [System.Collections.Generic.List[string]]::new()
$writeEvidence = -not $isLocalTest

function ConvertTo-PolicyJson {
    param([Parameter(Mandatory)]$Document)
    return ($Document | ConvertTo-Json -Depth 30 -Compress)
}

function Invoke-AwsJson {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $output = aws @Arguments 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw ('AWS_CALL_FAILED_' + (($Arguments[0..1] -join '_').ToUpperInvariant().Replace('-', '_')))
    }
    if ([string]::IsNullOrWhiteSpace(($output -join ''))) {
        return $null
    }
    return (($output -join [Environment]::NewLine) | ConvertFrom-Json)
}

function Invoke-AwsNoOutput {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $null = aws @Arguments 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw ('AWS_CALL_FAILED_' + (($Arguments[0..1] -join '_').ToUpperInvariant().Replace('-', '_')))
    }
}

function Invoke-AwsBestEffort {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $null = aws @Arguments 2>$null
    return ($LASTEXITCODE -eq 0)
}

function Set-SessionEnvironment {
    param([Parameter(Mandatory)]$Credentials)
    $env:AWS_ACCESS_KEY_ID = [string]$Credentials.AccessKeyId
    $env:AWS_SECRET_ACCESS_KEY = [string]$Credentials.SecretAccessKey
    $env:AWS_SESSION_TOKEN = [string]$Credentials.SessionToken
    $env:AWS_SECURITY_TOKEN = $null
    $env:AWS_PROFILE = $null
    $env:AWS_DEFAULT_PROFILE = $null
    $env:AWS_REGION = $expectedRegion
    $env:AWS_DEFAULT_REGION = $expectedRegion
    $env:AWS_EC2_METADATA_DISABLED = 'true'
}

function Get-SimulationDecision {
    param(
        [Parameter(Mandatory)][string]$PolicySourceArn,
        [Parameter(Mandatory)][string]$Action,
        [Parameter(Mandatory)][string]$Resource,
        [string[]]$ContextEntries = @()
    )
    $arguments = @(
        'iam', 'simulate-principal-policy',
        '--policy-source-arn', $PolicySourceArn,
        '--action-names', $Action,
        '--resource-arns', $Resource,
        '--no-cli-pager',
        '--output', 'json'
    )
    if ($ContextEntries.Count -gt 0) {
        $arguments += '--context-entries'
        $arguments += $ContextEntries
    }
    $simulation = Invoke-AwsJson -Arguments $arguments
    $script:result.aws_calls.iam_read_or_simulation++
    return [string]$simulation.EvaluationResults[0].EvalDecision
}

function Get-PlanOperatorHash {
    $role = Invoke-AwsJson -Arguments @(
        'iam', 'get-role', '--role-name', $planRoleName, '--no-cli-pager', '--output', 'json'
    )
    $attached = Invoke-AwsJson -Arguments @(
        'iam', 'list-attached-role-policies', '--role-name', $planRoleName, '--no-cli-pager', '--output', 'json'
    )
    $inline = Invoke-AwsJson -Arguments @(
        'iam', 'list-role-policies', '--role-name', $planRoleName, '--no-cli-pager', '--output', 'json'
    )
    $script:result.aws_calls.iam_read_or_simulation += 3
    $shape = [ordered]@{
        role_name = [string]$role.Role.RoleName
        max_session_duration = [int]$role.Role.MaxSessionDuration
        permissions_boundary_arn = [string]$role.Role.PermissionsBoundary.PermissionsBoundaryArn
        attached_policy_arns = @($attached.AttachedPolicies | ForEach-Object { [string]$_.PolicyArn } | Sort-Object)
        inline_policy_names = @($inline.PolicyNames | Sort-Object)
    }
    $bytes = [Text.Encoding]::UTF8.GetBytes(($shape | ConvertTo-Json -Depth 5 -Compress))
    try {
        return ([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))).ToLowerInvariant()
    } catch {
        $sha = [Security.Cryptography.SHA256]::Create()
        try {
            return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
        } finally {
            $sha.Dispose()
        }
    }
}

function Remove-TargetPartialArtifacts {
    if ($null -eq $setupCredentials) {
        $teardownFailures.Add('TARGET_ROLLBACK_NO_SETUP_SESSION')
        return
    }
    Set-SessionEnvironment -Credentials $setupCredentials
    if ($targetAttached) {
        if (Invoke-AwsBestEffort -Arguments @('iam','detach-role-policy','--role-name',$targetRoleName,'--policy-arn',$targetPolicyArn,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
            $script:targetAttached = $false
        } else {
            $teardownFailures.Add('TARGET_POLICY_DETACH_FAILED')
        }
    }
    if ($targetRoleCreated) {
        if (Invoke-AwsBestEffort -Arguments @('iam','delete-role-permissions-boundary','--role-name',$targetRoleName,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
        }
        if (Invoke-AwsBestEffort -Arguments @('iam','delete-role','--role-name',$targetRoleName,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
            $script:targetRoleCreated = $false
        } else {
            $teardownFailures.Add('TARGET_ROLE_DELETE_FAILED')
        }
    }
    if ($targetPolicyCreated) {
        if (Invoke-AwsBestEffort -Arguments @('iam','delete-policy','--policy-arn',$targetPolicyArn,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
            $script:targetPolicyCreated = $false
        } else {
            $teardownFailures.Add('TARGET_POLICY_DELETE_FAILED')
        }
    }
    if ($targetBoundaryCreated) {
        if (Invoke-AwsBestEffort -Arguments @('iam','delete-policy','--policy-arn',$targetBoundaryArn,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
            $script:targetBoundaryCreated = $false
        } else {
            $teardownFailures.Add('TARGET_BOUNDARY_DELETE_FAILED')
        }
    }
    $script:result.teardown.target_partial_artifacts_removed_if_required = (
        -not $targetRoleCreated -and -not $targetPolicyCreated -and -not $targetBoundaryCreated
    )
}

function Remove-SetupArtifacts {
    if ($null -eq $bootstrapCredentials) {
        $teardownFailures.Add('SETUP_TEARDOWN_NO_BOOTSTRAP_SESSION')
        return
    }
    Set-SessionEnvironment -Credentials $bootstrapCredentials
    if ($setupAttached) {
        if (Invoke-AwsBestEffort -Arguments @('iam','detach-role-policy','--role-name',$setupRoleName,'--policy-arn',$setupPolicyArn,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
            $script:setupAttached = $false
        } else {
            $teardownFailures.Add('SETUP_POLICY_DETACH_FAILED')
        }
    }
    if ($setupRoleCreated) {
        if (Invoke-AwsBestEffort -Arguments @('iam','delete-role-permissions-boundary','--role-name',$setupRoleName,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
        }
        if (Invoke-AwsBestEffort -Arguments @('iam','delete-role','--role-name',$setupRoleName,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
            $script:setupRoleCreated = $false
            $script:result.teardown.setup_role_removed = $true
        } else {
            $teardownFailures.Add('SETUP_ROLE_DELETE_FAILED')
        }
    }
    if ($setupPolicyCreated) {
        if (Invoke-AwsBestEffort -Arguments @('iam','delete-policy','--policy-arn',$setupPolicyArn,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
            $script:setupPolicyCreated = $false
            $script:result.teardown.setup_execution_policy_removed = $true
        } else {
            $teardownFailures.Add('SETUP_POLICY_DELETE_FAILED')
        }
    }
    if ($setupBoundaryCreated) {
        if (Invoke-AwsBestEffort -Arguments @('iam','delete-policy','--policy-arn',$setupBoundaryArn,'--no-cli-pager')) {
            $script:result.aws_calls.iam_mutation++
            $script:setupBoundaryCreated = $false
            $script:result.teardown.setup_boundary_removed = $true
        } else {
            $teardownFailures.Add('SETUP_BOUNDARY_DELETE_FAILED')
        }
    }
    $script:result.aws_calls.iam_read_or_simulation += 3
    if (Invoke-AwsBestEffort -Arguments @('iam','get-role','--role-name',$setupRoleName,'--no-cli-pager','--output','json')) {
        $script:result.teardown.setup_role_removed = $false
        $teardownFailures.Add('SETUP_ROLE_STILL_PRESENT')
    }
    if (Invoke-AwsBestEffort -Arguments @('iam','get-policy','--policy-arn',$setupPolicyArn,'--no-cli-pager','--output','json')) {
        $script:result.teardown.setup_execution_policy_removed = $false
        $teardownFailures.Add('SETUP_POLICY_STILL_PRESENT')
    }
    if (Invoke-AwsBestEffort -Arguments @('iam','get-policy','--policy-arn',$setupBoundaryArn,'--no-cli-pager','--output','json')) {
        $script:result.teardown.setup_boundary_removed = $false
        $teardownFailures.Add('SETUP_BOUNDARY_STILL_PRESENT')
    }
}

try {
    if ($LocalClosureTest) {
        throw 'LOCAL_CLOSURE_TEST'
    }
    if ($LocalAttemptPathTest) {
        throw 'LOCAL_ATTEMPT_PATH_TEST'
    }
    if (-not [string]::IsNullOrWhiteSpace($EvidenceDirectoryOverride)) {
        throw 'EVIDENCE_DIRECTORY_OVERRIDE_FORBIDDEN_OPERATIONALLY'
    }
    if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
        throw 'AWS_CLI_NOT_AVAILABLE'
    }

    $result.execution_head = (git -C $repositoryRoot rev-parse HEAD)
    if ((git -C $repositoryRoot branch --show-current) -ne 'main') {
        throw 'BRANCH_MISMATCH'
    }
    if (@(git -C $repositoryRoot status --porcelain).Count -ne 0) {
        throw 'WORKTREE_NOT_CLEAN'
    }

    $profiles = @(aws configure list-profiles 2>$null)
    if ($profiles -notcontains $sourceProfile) {
        throw 'BOOTSTRAP_PROFILE_NOT_FOUND'
    }
    foreach ($profile in @(
        'pl003-bootstrap-mfa-114',
        'pl003-bootstrap-mfa-114-r2',
        'pl003-bootstrap-mfa-114-active',
        'pl003-iam-setup-operator'
    )) {
        if ($profiles -contains $profile) {
            foreach ($field in @('aws_access_key_id','aws_secret_access_key','aws_session_token')) {
                $value = aws configure get $field --profile $profile 2>$null
                if (-not [string]::IsNullOrWhiteSpace($value)) {
                    throw 'REUSABLE_PRIOR_TEMPORARY_CREDENTIAL_DETECTED'
                }
            }
        }
    }

    $presentCredentialEnvironmentNames = @(
        $credentialEnvironmentNames | Where-Object {
            -not [string]::IsNullOrWhiteSpace(
                [Environment]::GetEnvironmentVariable($_, 'Process')
            )
        }
    )
    if ($presentCredentialEnvironmentNames.Count -ne 0) {
        throw 'PREEXISTING_AWS_CREDENTIAL_ENVIRONMENT_DETECTED'
    }

    $configuredRegion = aws configure get region --profile $sourceProfile 2>$null
    if ([string]::IsNullOrWhiteSpace($configuredRegion)) {
        $configuredRegion = $expectedRegion
    }
    if ($configuredRegion -ne $expectedRegion) {
        throw 'BOOTSTRAP_REGION_MISMATCH'
    }
    if ((aws configure get cli_history --profile $sourceProfile 2>$null) -eq 'enabled') {
        throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
    }

    $mfaSerial = aws configure get mfa_serial --profile $sourceProfile 2>$null
    if ([string]::IsNullOrWhiteSpace($mfaSerial)) {
        $mfaSerial = aws configure get mfa_serial --profile $mfaReferenceProfile 2>$null
    }
    if ([string]::IsNullOrWhiteSpace($mfaSerial)) {
        throw 'MFA_REFERENCE_NOT_CONFIGURED'
    }

    $secureTotp = Read-Host -Prompt 'MFA token code' -AsSecureString
    $totpBstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureTotp)
    $totp = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($totpBstr)
    if ($totp -notmatch '^[0-9]{6}$') {
        throw 'INVALID_TOTP_FORMAT'
    }

    $result.replacement_session.get_session_token_calls = 1
    $result.aws_calls.sts_get_session_token = 1
    $sessionResponse = Invoke-AwsJson -Arguments @(
        'sts','get-session-token',
        '--profile',$sourceProfile,
        '--region',$expectedRegion,
        '--serial-number',$mfaSerial,
        '--token-code',$totp,
        '--duration-seconds',"$durationSeconds",
        '--no-cli-pager',
        '--output','json'
    )
    $bootstrapCredentials = $sessionResponse.Credentials
    $expiration = [DateTimeOffset]::Parse([string]$bootstrapCredentials.Expiration)
    $now = [DateTimeOffset]::UtcNow
    if ($expiration -le $now -or $expiration -gt $now.AddSeconds($durationSeconds + 120)) {
        throw 'REPLACEMENT_SESSION_EXPIRATION_INVALID'
    }
    Set-SessionEnvironment -Credentials $bootstrapCredentials

    $bootstrapIdentity = Invoke-AwsJson -Arguments @(
        'sts','get-caller-identity','--region',$expectedRegion,'--no-cli-pager','--output','json'
    )
    $result.aws_calls.sts_other++
    $accountId = [string]$bootstrapIdentity.Account
    $bootstrapUserArn = [string]$bootstrapIdentity.Arn
    if ($accountId -notmatch '^[0-9]{12}$') {
        throw 'STS_ACCOUNT_SHAPE_INVALID'
    }
    if ($bootstrapUserArn -notmatch ('^arn:aws:iam::[0-9]{12}:user/' + [regex]::Escape($expectedBootstrapPrincipal) + '$')) {
        throw 'BOOTSTRAP_STS_PRINCIPAL_MISMATCH'
    }
    $result.replacement_session.mfa_backed = $true
    $result.bootstrap_identity.sts_verified = $true

    $setupRoleArn = "arn:aws:iam::$accountId`:role/$setupRoleName"
    $setupBoundaryArn = "arn:aws:iam::$accountId`:policy/$setupBoundaryName"
    $setupPolicyArn = "arn:aws:iam::$accountId`:policy/$setupPolicyName"
    $targetRoleArn = "arn:aws:iam::$accountId`:role/$targetRoleName"
    $targetBoundaryArn = "arn:aws:iam::$accountId`:policy/$targetBoundaryName"
    $targetPolicyArn = "arn:aws:iam::$accountId`:policy/$targetPolicyName"
    $planRoleArn = "arn:aws:iam::$accountId`:role/$planRoleName"
    $subjectBoundaryArn = "arn:aws:iam::$accountId`:policy/pl003-preflight-subject-boundary"
    $subjectRoleArnPattern = "arn:aws:iam::$accountId`:role/pl003-preflight-*"
    $bucketArnPattern = 'arn:aws:s3:::pl003-preflight-*'
    $secretArnPattern = "arn:aws:secretsmanager:$expectedRegion`:$accountId`:secret:/pl003/preflight/*"
    $trailArnPattern = "arn:aws:cloudtrail:$expectedRegion`:$accountId`:trail/pl003-preflight-*"
    $budgetArnPattern = "arn:aws:budgets::$accountId`:budget/PL003*"

    $setupTrustJson = ConvertTo-PolicyJson -Document @{
        Version = '2012-10-17'
        Statement = @(@{
            Sid = 'ExactBootstrapMfaTrust'
            Effect = 'Allow'
            Principal = @{ AWS = $bootstrapUserArn }
            Action = 'sts:AssumeRole'
            Condition = @{ Bool = @{ 'aws:MultiFactorAuthPresent' = 'true' } }
        })
    }

    $setupPolicyDocument = @{
        Version = '2012-10-17'
        Statement = @(
            @{
                Sid = 'ReadAndSimulate'
                Effect = 'Allow'
                Action = @(
                    'iam:GetAccountSummary','iam:GetPolicy','iam:GetPolicyVersion',
                    'iam:GetRole','iam:ListAttachedRolePolicies','iam:ListPolicyVersions',
                    'iam:ListRolePolicies','iam:SimulatePrincipalPolicy'
                )
                Resource = '*'
            },
            @{
                Sid = 'CreateExactTargetPolicies'
                Effect = 'Allow'
                Action = @('iam:CreatePolicy','iam:DeletePolicy','iam:TagPolicy','iam:UntagPolicy')
                Resource = @($targetBoundaryArn,$targetPolicyArn)
            },
            @{
                Sid = 'CreateTargetRoleWithBoundary'
                Effect = 'Allow'
                Action = @('iam:CreateRole','iam:PutRolePermissionsBoundary')
                Resource = $targetRoleArn
                Condition = @{ StringEquals = @{ 'iam:PermissionsBoundary' = $targetBoundaryArn } }
            },
            @{
                Sid = 'ManageExactTargetRole'
                Effect = 'Allow'
                Action = @(
                    'iam:GetRole','iam:TagRole','iam:UntagRole','iam:UpdateAssumeRolePolicy',
                    'iam:DeleteRolePermissionsBoundary','iam:DeleteRole',
                    'iam:ListAttachedRolePolicies','iam:ListRolePolicies'
                )
                Resource = $targetRoleArn
            },
            @{
                Sid = 'AttachOnlyExactTargetPolicy'
                Effect = 'Allow'
                Action = @('iam:AttachRolePolicy','iam:DetachRolePolicy')
                Resource = $targetRoleArn
                Condition = @{ StringEquals = @{ 'iam:PolicyARN' = $targetPolicyArn } }
            },
            @{
                Sid = 'DenyCriticalEscalation'
                Effect = 'Deny'
                Action = @(
                    'iam:CreateUser','iam:DeleteUser','iam:CreateAccessKey','iam:UpdateAccessKey',
                    'iam:DeleteAccessKey','iam:CreateLoginProfile','iam:UpdateLoginProfile',
                    'iam:CreateGroup','iam:AddUserToGroup','iam:AttachUserPolicy','iam:PutUserPolicy',
                    'iam:AttachGroupPolicy','iam:PutGroupPolicy','iam:CreatePolicyVersion',
                    'iam:SetDefaultPolicyVersion','iam:PassRole'
                )
                Resource = '*'
            },
            @{
                Sid = 'DenyPlanOperatorMutation'
                Effect = 'Deny'
                Action = @(
                    'iam:AttachRolePolicy','iam:DetachRolePolicy','iam:PutRolePolicy','iam:DeleteRolePolicy',
                    'iam:PutRolePermissionsBoundary','iam:DeleteRolePermissionsBoundary',
                    'iam:UpdateAssumeRolePolicy','iam:UpdateRole','iam:DeleteRole','iam:TagRole','iam:UntagRole'
                )
                Resource = $planRoleArn
            }
        )
    }
    $setupPolicyJson = ConvertTo-PolicyJson -Document $setupPolicyDocument

    $targetTrustJson = ConvertTo-PolicyJson -Document @{
        Version = '2012-10-17'
        Statement = @(@{
            Sid = 'ExactBootstrapMfaTrust'
            Effect = 'Allow'
            Principal = @{ AWS = $bootstrapUserArn }
            Action = @('sts:AssumeRole','sts:TagSession')
            Condition = @{ Bool = @{ 'aws:MultiFactorAuthPresent' = 'true' } }
        })
    }

    $targetPolicyDocument = @{
        Version = '2012-10-17'
        Statement = @(
            @{
                Sid = 'ReadControlPlane'
                Effect = 'Allow'
                Action = @(
                    'iam:GetAccountSummary','iam:GetPolicy','iam:GetPolicyVersion','iam:GetRole',
                    'iam:ListAttachedRolePolicies','iam:ListPolicyVersions','iam:ListRolePolicies',
                    's3:ListAllMyBuckets','kms:ListAliases','cloudtrail:DescribeTrails',
                    'cloudtrail:GetEventSelectors','cloudtrail:GetTrailStatus','secretsmanager:ListSecrets',
                    'budgets:DescribeBudget','budgets:ViewBudget'
                )
                Resource = '*'
            },
            @{
                Sid = 'ManageSubjectBoundary'
                Effect = 'Allow'
                Action = @(
                    'iam:CreatePolicy','iam:GetPolicy','iam:GetPolicyVersion','iam:ListPolicyVersions',
                    'iam:DeletePolicy','iam:TagPolicy','iam:UntagPolicy'
                )
                Resource = $subjectBoundaryArn
            },
            @{
                Sid = 'CreateSubjectRolesWithBoundary'
                Effect = 'Allow'
                Action = @('iam:CreateRole','iam:PutRolePermissionsBoundary')
                Resource = $subjectRoleArnPattern
                Condition = @{ StringEquals = @{ 'iam:PermissionsBoundary' = $subjectBoundaryArn } }
            },
            @{
                Sid = 'ManageSubjectRoles'
                Effect = 'Allow'
                Action = @(
                    'iam:GetRole','iam:DeleteRole','iam:TagRole','iam:UntagRole',
                    'iam:UpdateAssumeRolePolicy','iam:PutRolePolicy','iam:GetRolePolicy',
                    'iam:DeleteRolePolicy','iam:ListRolePolicies','iam:ListAttachedRolePolicies',
                    'iam:DeleteRolePermissionsBoundary'
                )
                Resource = $subjectRoleArnPattern
            },
            @{
                Sid = 'ManagePrefixedBuckets'
                Effect = 'Allow'
                Action = @(
                    's3:CreateBucket','s3:DeleteBucket','s3:GetBucket*','s3:ListBucket*',
                    's3:PutBucketPolicy','s3:DeleteBucketPolicy','s3:PutBucketPublicAccessBlock',
                    's3:PutBucketVersioning','s3:PutBucketOwnershipControls',
                    's3:PutEncryptionConfiguration','s3:PutBucketTagging',
                    's3:PutBucketObjectLockConfiguration'
                )
                Resource = @($bucketArnPattern,"$bucketArnPattern/*")
            },
            @{
                Sid = 'CreateTaggedKeys'
                Effect = 'Allow'
                Action = 'kms:CreateKey'
                Resource = '*'
                Condition = @{ StringEquals = @{ 'aws:RequestTag/Project' = 'PRODUCT-LEADERSHIP-TEST-003' } }
            },
            @{
                Sid = 'ManageTaggedKeys'
                Effect = 'Allow'
                Action = @(
                    'kms:DescribeKey','kms:GetKeyPolicy','kms:GetKeyRotationStatus','kms:ListResourceTags',
                    'kms:PutKeyPolicy','kms:EnableKey','kms:DisableKey','kms:EnableKeyRotation',
                    'kms:ScheduleKeyDeletion','kms:CancelKeyDeletion','kms:TagResource',
                    'kms:UntagResource','kms:UpdateKeyDescription'
                )
                Resource = "arn:aws:kms:$expectedRegion`:$accountId`:key/*"
                Condition = @{ StringEquals = @{ 'aws:ResourceTag/Project' = 'PRODUCT-LEADERSHIP-TEST-003' } }
            },
            @{
                Sid = 'ManagePrefixedAliases'
                Effect = 'Allow'
                Action = @('kms:CreateAlias','kms:DeleteAlias','kms:UpdateAlias')
                Resource = "arn:aws:kms:$expectedRegion`:$accountId`:alias/pl003-preflight-*"
            },
            @{
                Sid = 'ManageEmptySecretContainer'
                Effect = 'Allow'
                Action = @(
                    'secretsmanager:CreateSecret','secretsmanager:DescribeSecret',
                    'secretsmanager:GetResourcePolicy','secretsmanager:PutResourcePolicy',
                    'secretsmanager:DeleteResourcePolicy','secretsmanager:TagResource',
                    'secretsmanager:UntagResource','secretsmanager:UpdateSecret',
                    'secretsmanager:DeleteSecret','secretsmanager:RestoreSecret'
                )
                Resource = $secretArnPattern
            },
            @{
                Sid = 'ManagePrefixedTrail'
                Effect = 'Allow'
                Action = @(
                    'cloudtrail:CreateTrail','cloudtrail:UpdateTrail','cloudtrail:StartLogging',
                    'cloudtrail:PutEventSelectors','cloudtrail:AddTags','cloudtrail:RemoveTags',
                    'cloudtrail:GetTrailStatus','cloudtrail:GetEventSelectors','cloudtrail:DeleteTrail',
                    'cloudtrail:StopLogging'
                )
                Resource = $trailArnPattern
            },
            @{
                Sid = 'ManageCostGuard'
                Effect = 'Allow'
                Action = @('budgets:CreateBudget','budgets:ModifyBudget','budgets:DescribeBudget','budgets:ViewBudget','budgets:DeleteBudget')
                Resource = $budgetArnPattern
            },
            @{
                Sid = 'DenyCriticalEscalation'
                Effect = 'Deny'
                Action = @(
                    'iam:CreateUser','iam:DeleteUser','iam:CreateAccessKey','iam:UpdateAccessKey',
                    'iam:DeleteAccessKey','iam:CreateLoginProfile','iam:CreateGroup',
                    'iam:AddUserToGroup','iam:AttachUserPolicy','iam:PutUserPolicy',
                    'iam:AttachGroupPolicy','iam:PutGroupPolicy','iam:CreatePolicyVersion',
                    'iam:SetDefaultPolicyVersion','iam:AttachRolePolicy','iam:PassRole'
                )
                Resource = '*'
            },
            @{
                Sid = 'DenyProtectedRoleMutation'
                Effect = 'Deny'
                Action = @(
                    'iam:DeleteRole','iam:UpdateAssumeRolePolicy','iam:PutRolePolicy',
                    'iam:DeleteRolePolicy','iam:PutRolePermissionsBoundary',
                    'iam:DeleteRolePermissionsBoundary','iam:AttachRolePolicy','iam:DetachRolePolicy',
                    'iam:TagRole','iam:UntagRole'
                )
                Resource = @($planRoleArn,$setupRoleArn,$targetRoleArn)
            },
            @{
                Sid = 'DenySubjectRoleChaining'
                Effect = 'Deny'
                Action = 'sts:AssumeRole'
                Resource = $subjectRoleArnPattern
            },
            @{
                Sid = 'DenyRetentionBypass'
                Effect = 'Deny'
                Action = @('s3:BypassGovernanceRetention','s3:PutObjectRetention','s3:PutObjectLegalHold')
                Resource = "$bucketArnPattern/*"
            },
            @{
                Sid = 'DenyTrailStopDeleteWithoutTeardownTag'
                Effect = 'Deny'
                Action = @('cloudtrail:StopLogging','cloudtrail:DeleteTrail')
                Resource = $trailArnPattern
                Condition = @{ StringNotEquals = @{ 'aws:PrincipalTag/PL003Teardown' = 'true' } }
            },
            @{
                Sid = 'DenyCostGuardDeleteWithoutTeardownTag'
                Effect = 'Deny'
                Action = 'budgets:DeleteBudget'
                Resource = $budgetArnPattern
                Condition = @{ StringNotEquals = @{ 'aws:PrincipalTag/PL003Teardown' = 'true' } }
            }
        )
    }
    $targetPolicyJson = ConvertTo-PolicyJson -Document $targetPolicyDocument

    if ($setupPolicyJson.Length -gt 6144 -or $targetPolicyJson.Length -gt 6144) {
        throw 'MANAGED_POLICY_SIZE_LIMIT_EXCEEDED'
    }

    $mfaContext = @('ContextKeyName=aws:MultiFactorAuthPresent,ContextKeyValues=true,ContextKeyType=boolean')
    $createTagsContext = @(
        'ContextKeyName=aws:RequestTag/Project,ContextKeyValues=PRODUCT-LEADERSHIP-TEST-003,ContextKeyType=string',
        'ContextKeyName=aws:RequestTag/Authorization,ContextKeyValues=114A,ContextKeyType=string',
        'ContextKeyName=aws:RequestTag/Temporary,ContextKeyValues=true,ContextKeyType=string'
    )
    $bootstrapChecks = @(
        [pscustomobject]@{ Action='iam:CreatePolicy'; Resource=$setupBoundaryArn; Context=$createTagsContext },
        [pscustomobject]@{ Action='iam:CreatePolicy'; Resource=$setupPolicyArn; Context=$createTagsContext },
        [pscustomobject]@{ Action='iam:TagPolicy'; Resource=$setupBoundaryArn; Context=$createTagsContext },
        [pscustomobject]@{ Action='iam:TagPolicy'; Resource=$setupPolicyArn; Context=$createTagsContext },
        [pscustomobject]@{ Action='iam:GetPolicy'; Resource=$setupBoundaryArn; Context=@() },
        [pscustomobject]@{ Action='iam:GetPolicy'; Resource=$setupPolicyArn; Context=@() },
        [pscustomobject]@{ Action='iam:DeletePolicy'; Resource=$setupBoundaryArn; Context=@() },
        [pscustomobject]@{ Action='iam:DeletePolicy'; Resource=$setupPolicyArn; Context=@() },
        [pscustomobject]@{
            Action='iam:CreateRole'
            Resource=$setupRoleArn
            Context=@("ContextKeyName=iam:PermissionsBoundary,ContextKeyValues=$setupBoundaryArn,ContextKeyType=string") + $createTagsContext
        },
        [pscustomobject]@{ Action='iam:TagRole'; Resource=$setupRoleArn; Context=$createTagsContext },
        [pscustomobject]@{
            Action='iam:AttachRolePolicy'
            Resource=$setupRoleArn
            Context=@("ContextKeyName=iam:PolicyARN,ContextKeyValues=$setupPolicyArn,ContextKeyType=string")
        },
        [pscustomobject]@{
            Action='iam:DetachRolePolicy'
            Resource=$setupRoleArn
            Context=@("ContextKeyName=iam:PolicyARN,ContextKeyValues=$setupPolicyArn,ContextKeyType=string")
        },
        [pscustomobject]@{ Action='iam:DeleteRolePermissionsBoundary'; Resource=$setupRoleArn; Context=@() },
        [pscustomobject]@{ Action='iam:DeleteRole'; Resource=$setupRoleArn; Context=@() },
        [pscustomobject]@{ Action='iam:GetRole'; Resource=$planRoleArn; Context=@() },
        [pscustomobject]@{ Action='sts:AssumeRole'; Resource=$setupRoleArn; Context=@() }
    )
    foreach ($check in $bootstrapChecks) {
        try {
            $decision = Get-SimulationDecision `
                -PolicySourceArn $bootstrapUserArn `
                -Action $check.Action `
                -Resource $check.Resource `
                -ContextEntries @($mfaContext + @($check.Context))
        } catch {
            throw 'BOOTSTRAP_SIMULATION_UNAVAILABLE_OR_DENIED'
        }
        if ($decision -ne 'allowed') {
            throw ('BOOTSTRAP_PERMISSION_GATE_DENIED_' + $check.Action.Replace(':','_').ToUpperInvariant())
        }
    }
    $result.pre_mutation_gate.bootstrap_simulation_completed = $true
    $result.pre_mutation_gate.all_required_setup_and_teardown_actions_allowed = $true
    $result.pre_mutation_gate.aws_mutations_before_gate = $result.aws_calls.iam_mutation

    $created = Invoke-AwsJson -Arguments @(
        'iam','create-policy','--policy-name',$setupBoundaryName,
        '--description','Temporary PL003 authorization 114 setup permissions boundary',
        '--policy-document',$setupPolicyJson,
        '--tags','Key=Project,Value=PRODUCT-LEADERSHIP-TEST-003','Key=Authorization,Value=114A','Key=Temporary,Value=true',
        '--no-cli-pager','--output','json'
    )
    $result.aws_calls.iam_mutation++
    $setupBoundaryCreated = $true
    if ([string]$created.Policy.Arn -ne $setupBoundaryArn) { throw 'SETUP_BOUNDARY_ARN_MISMATCH' }
    $result.setup_operator.boundary_created = $true

    $created = Invoke-AwsJson -Arguments @(
        'iam','create-policy','--policy-name',$setupPolicyName,
        '--description','Temporary PL003 authorization 114 setup execution policy',
        '--policy-document',$setupPolicyJson,
        '--tags','Key=Project,Value=PRODUCT-LEADERSHIP-TEST-003','Key=Authorization,Value=114A','Key=Temporary,Value=true',
        '--no-cli-pager','--output','json'
    )
    $result.aws_calls.iam_mutation++
    $setupPolicyCreated = $true
    if ([string]$created.Policy.Arn -ne $setupPolicyArn) { throw 'SETUP_POLICY_ARN_MISMATCH' }
    $result.setup_operator.execution_policy_created = $true

    $null = Invoke-AwsJson -Arguments @(
        'iam','create-role','--role-name',$setupRoleName,
        '--assume-role-policy-document',$setupTrustJson,
        '--permissions-boundary',$setupBoundaryArn,
        '--max-session-duration',"$durationSeconds",
        '--description','Temporary PL003 authorization 114 IAM setup operator',
        '--tags','Key=Project,Value=PRODUCT-LEADERSHIP-TEST-003','Key=Authorization,Value=114A','Key=Temporary,Value=true',
        '--no-cli-pager','--output','json'
    )
    $result.aws_calls.iam_mutation++
    $setupRoleCreated = $true
    $result.setup_operator.role_created = $true

    Invoke-AwsNoOutput -Arguments @(
        'iam','attach-role-policy','--role-name',$setupRoleName,'--policy-arn',$setupPolicyArn,'--no-cli-pager'
    )
    $result.aws_calls.iam_mutation++
    $setupAttached = $true
    $result.setup_operator.policy_attached = $true

    $assumed = Invoke-AwsJson -Arguments @(
        'sts','assume-role','--role-arn',$setupRoleArn,
        '--role-session-name','PL003Setup114A','--duration-seconds',"$durationSeconds",
        '--no-cli-pager','--output','json'
    )
    $result.aws_calls.sts_other++
    $setupCredentials = $assumed.Credentials
    Set-SessionEnvironment -Credentials $setupCredentials
    $setupIdentity = Invoke-AwsJson -Arguments @(
        'sts','get-caller-identity','--region',$expectedRegion,'--no-cli-pager','--output','json'
    )
    $result.aws_calls.sts_other++
    if ([string]$setupIdentity.Arn -notmatch ('^arn:aws:sts::[0-9]{12}:assumed-role/' + [regex]::Escape($setupRoleName) + '/')) {
        throw 'SETUP_STS_PRINCIPAL_MISMATCH'
    }
    $result.setup_operator.assumed_role_sts_verified = $true

    $setupRole = Invoke-AwsJson -Arguments @(
        'iam','get-role','--role-name',$setupRoleName,'--no-cli-pager','--output','json'
    )
    $result.aws_calls.iam_read_or_simulation++
    if ([string]$setupRole.Role.PermissionsBoundary.PermissionsBoundaryArn -ne $setupBoundaryArn) {
        throw 'SETUP_BOUNDARY_NOT_EFFECTIVE'
    }
    if ([int]$setupRole.Role.MaxSessionDuration -ne $durationSeconds) {
        throw 'SETUP_MAX_SESSION_MISMATCH'
    }
    $trust = $setupRole.Role.AssumeRolePolicyDocument
    $trustPrincipal = [string]$trust.Statement[0].Principal.AWS
    $trustMfa = [string]$trust.Statement[0].Condition.Bool.'aws:MultiFactorAuthPresent'
    if ($trustPrincipal -ne $bootstrapUserArn -or $trustMfa -ne 'true') {
        throw 'SETUP_TRUST_OR_MFA_MISMATCH'
    }
    $result.setup_operator.boundary_verified = $true
    $result.setup_operator.mfa_trust_verified = $true

    $planBaselineHash = Get-PlanOperatorHash

    $summary = Invoke-AwsJson -Arguments @(
        'iam','get-account-summary','--no-cli-pager','--output','json'
    )
    $result.aws_calls.iam_read_or_simulation++
    $result.root_security_visibility.get_account_summary = 'PASS'
    $result.root_security_visibility.root_mfa_enabled = ([int]$summary.SummaryMap.AccountMFAEnabled -eq 1)
    $result.root_security_visibility.root_access_keys_absent = ([int]$summary.SummaryMap.AccountAccessKeysPresent -eq 0)
    if (-not $result.root_security_visibility.root_mfa_enabled -or -not $result.root_security_visibility.root_access_keys_absent) {
        throw 'ROOT_SECURITY_GATE_FAILED'
    }

    $created = Invoke-AwsJson -Arguments @(
        'iam','create-policy','--policy-name',$targetBoundaryName,
        '--description','PL003 bounded provisioning operator permissions boundary',
        '--policy-document',$targetPolicyJson,
        '--tags','Key=Project,Value=PRODUCT-LEADERSHIP-TEST-003','Key=Authorization,Value=113',
        '--no-cli-pager','--output','json'
    )
    $result.aws_calls.iam_mutation++
    $targetBoundaryCreated = $true
    if ([string]$created.Policy.Arn -ne $targetBoundaryArn) { throw 'TARGET_BOUNDARY_ARN_MISMATCH' }
    $result.authorization_113.boundary_created = $true

    $created = Invoke-AwsJson -Arguments @(
        'iam','create-policy','--policy-name',$targetPolicyName,
        '--description','PL003 bounded provisioning operator execution policy',
        '--policy-document',$targetPolicyJson,
        '--tags','Key=Project,Value=PRODUCT-LEADERSHIP-TEST-003','Key=Authorization,Value=113',
        '--no-cli-pager','--output','json'
    )
    $result.aws_calls.iam_mutation++
    $targetPolicyCreated = $true
    if ([string]$created.Policy.Arn -ne $targetPolicyArn) { throw 'TARGET_POLICY_ARN_MISMATCH' }
    $result.authorization_113.execution_policy_created = $true

    $null = Invoke-AwsJson -Arguments @(
        'iam','create-role','--role-name',$targetRoleName,
        '--assume-role-policy-document',$targetTrustJson,
        '--permissions-boundary',$targetBoundaryArn,
        '--max-session-duration',"$durationSeconds",
        '--description','PL003 bounded provisioning operator for authorization 112',
        '--tags','Key=Project,Value=PRODUCT-LEADERSHIP-TEST-003','Key=Authorization,Value=113',
        '--no-cli-pager','--output','json'
    )
    $result.aws_calls.iam_mutation++
    $targetRoleCreated = $true
    $result.authorization_113.provisioning_role_created = $true

    Invoke-AwsNoOutput -Arguments @(
        'iam','attach-role-policy','--role-name',$targetRoleName,'--policy-arn',$targetPolicyArn,'--no-cli-pager'
    )
    $result.aws_calls.iam_mutation++
    $targetAttached = $true

    $positiveTests = @(
        @('iam:GetAccountSummary','*',@()),
        @('s3:CreateBucket','arn:aws:s3:::pl003-preflight-static-simulation',@()),
        @('secretsmanager:CreateSecret',"arn:aws:secretsmanager:$expectedRegion`:$accountId`:secret:/pl003/preflight/static-simulation",@()),
        @('cloudtrail:CreateTrail',"arn:aws:cloudtrail:$expectedRegion`:$accountId`:trail/pl003-preflight-static-simulation",@()),
        @('budgets:CreateBudget',"arn:aws:budgets::$accountId`:budget/PL003-static-simulation",@()),
        @('iam:CreateRole',"arn:aws:iam::$accountId`:role/pl003-preflight-static-simulation",@("ContextKeyName=iam:PermissionsBoundary,ContextKeyValues=$subjectBoundaryArn,ContextKeyType=string")),
        @('kms:CreateKey','*',@('ContextKeyName=aws:RequestTag/Project,ContextKeyValues=PRODUCT-LEADERSHIP-TEST-003,ContextKeyType=string'))
    )
    foreach ($test in $positiveTests) {
        $decision = Get-SimulationDecision -PolicySourceArn $targetRoleArn -Action $test[0] -Resource $test[1] -ContextEntries $test[2]
        if ($decision -ne 'allowed') {
            throw ('TARGET_POSITIVE_SIMULATION_FAILED_' + $test[0].Replace(':','_').ToUpperInvariant())
        }
    }

    $negativeTests = @(
        @('iam:CreateUser','*'),
        @('iam:CreateAccessKey',"arn:aws:iam::$accountId`:user/unauthorized"),
        @('iam:PassRole',$subjectRoleArnPattern),
        @('iam:UpdateAssumeRolePolicy',$planRoleArn),
        @('iam:DeleteRolePermissionsBoundary',$targetRoleArn),
        @('cloudtrail:StopLogging',"arn:aws:cloudtrail:$expectedRegion`:$accountId`:trail/pl003-preflight-static-simulation"),
        @('budgets:DeleteBudget',"arn:aws:budgets::$accountId`:budget/PL003-static-simulation"),
        @('s3:BypassGovernanceRetention','arn:aws:s3:::pl003-preflight-static-simulation/object'),
        @('sts:AssumeRole',"arn:aws:iam::$accountId`:role/pl003-preflight-static-simulation"),
        @('iam:AttachRolePolicy',"arn:aws:iam::$accountId`:role/pl003-preflight-static-simulation")
    )
    foreach ($test in $negativeTests) {
        $decision = Get-SimulationDecision -PolicySourceArn $targetRoleArn -Action $test[0] -Resource $test[1]
        if ($decision -ne 'explicitDeny') {
            throw ('TARGET_NEGATIVE_SIMULATION_FAILED_' + $test[0].Replace(':','_').ToUpperInvariant())
        }
    }
    $result.authorization_113.effective_scope_tests = 'PASS_7_POSITIVE_10_NEGATIVE_IAM_SIMULATIONS'

    $planFinalHash = Get-PlanOperatorHash
    if ($planFinalHash -ne $planBaselineHash) {
        throw 'PLAN_OPERATOR_CHANGED'
    }
    $result.authorization_113.plan_operator_unchanged = 'PASS_SAME_RUN_SHA256'

    Set-SessionEnvironment -Credentials $bootstrapCredentials
    $assumed = Invoke-AwsJson -Arguments @(
        'sts','assume-role','--role-arn',$targetRoleArn,
        '--role-session-name','PL003Provisioning113','--duration-seconds',"$durationSeconds",
        '--no-cli-pager','--output','json'
    )
    $result.aws_calls.sts_other++
    $targetCredentials = $assumed.Credentials
    Set-SessionEnvironment -Credentials $targetCredentials
    $targetIdentity = Invoke-AwsJson -Arguments @(
        'sts','get-caller-identity','--region',$expectedRegion,'--no-cli-pager','--output','json'
    )
    $result.aws_calls.sts_other++
    if ([string]$targetIdentity.Arn -notmatch ('^arn:aws:sts::[0-9]{12}:assumed-role/' + [regex]::Escape($targetRoleName) + '/')) {
        throw 'TARGET_STS_PRINCIPAL_MISMATCH'
    }
    $result.authorization_113.assumed_role_sts_verified = $true

    aws configure set role_arn $targetRoleArn --profile $provisioningProfileName
    aws configure set source_profile $sourceProfile --profile $provisioningProfileName
    aws configure set mfa_serial $mfaSerial --profile $provisioningProfileName
    aws configure set region $expectedRegion --profile $provisioningProfileName
    aws configure set duration_seconds $durationSeconds --profile $provisioningProfileName
    if ($LASTEXITCODE -ne 0) {
        throw 'PROVISIONING_PROFILE_CONFIGURATION_FAILED'
    }

    $targetVerified = $true
    $result.authorization_113.status = 'PASS_READY_FOR_CANONICAL_RECONCILIATION'
    $result.status = 'PASS_OPERATIONAL_SCOPE_COMPLETED'
    $result.result = 'PASS'
} catch {
    $message = [string]$_.Exception.Message
    if ($LocalClosureTest -and $message -eq 'LOCAL_CLOSURE_TEST') {
        $result.status = 'LOCAL_CLOSURE_PATH_COMPLETED'
        $result.result = 'LOCAL_TEST_PASS'
        $result.failure_code = $null
    }
    if ($LocalAttemptPathTest -and $message -eq 'LOCAL_ATTEMPT_PATH_TEST') {
        $result.status = 'LOCAL_ATTEMPT_PATH_SELECTION_COMPLETED'
        $result.result = 'LOCAL_TEST_PASS'
        $result.failure_code = $null
    }
    if ($message -match '^[A-Z0-9_:-]+$') {
        if (-not $isLocalTest) {
            $result.failure_code = $message.Replace(':','_').Replace('-','_')
        }
    } else {
        $result.failure_code = 'UNEXPECTED_ORCHESTRATOR_FAILURE'
    }
    if (-not $isLocalTest -and $result.replacement_session.get_session_token_calls -eq 0) {
        $result.status = 'BLOCKED_BEFORE_REPLACEMENT_SESSION'
    } elseif (-not $isLocalTest -and -not $result.pre_mutation_gate.all_required_setup_and_teardown_actions_allowed) {
        $result.status = 'BLOCKED_AFTER_MFA_BEFORE_AWS_MUTATION'
    } elseif (-not $isLocalTest -and -not $targetVerified) {
        $result.status = 'BLOCKED_FAIL_CLOSED_WITH_ROLLBACK_REQUIRED'
    }
    if (-not $isLocalTest) {
        $result.authorization_113.status = 'BLOCKED_FAIL_CLOSED'
        $result.result = 'BLOCKED'
    }
} finally {
    if (-not $targetVerified -and ($targetRoleCreated -or $targetPolicyCreated -or $targetBoundaryCreated)) {
        Remove-TargetPartialArtifacts
    }
    if ($setupRoleCreated -or $setupPolicyCreated -or $setupBoundaryCreated) {
        Remove-SetupArtifacts
    }

    $result.teardown.complete = (
        -not $setupRoleCreated -and
        -not $setupPolicyCreated -and
        -not $setupBoundaryCreated -and
        $teardownFailures.Count -eq 0
    )
    if (-not $result.teardown.complete) {
        $result.status = 'BLOCKED_TEARDOWN_INCOMPLETE'
        $result.failure_code = 'COMPLETE_TEMPORARY_ARTIFACT_CLEANUP_CANNOT_BE_GUARANTEED'
        $result.result = 'BLOCKED'
    }

    foreach ($name in $temporaryEnvironmentNames) {
        [Environment]::SetEnvironmentVariable($name, $priorEnvironment[$name], 'Process')
    }
    if ($totpBstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($totpBstr)
    }

    $secureTotp = $null
    $totp = $null
    $sessionResponse = $null
    $bootstrapCredentials = $null
    $setupCredentials = $null
    $targetCredentials = $null
    $accountId = $null
    $bootstrapUserArn = $null
    $setupRoleArn = $null
    $setupBoundaryArn = $null
    $setupPolicyArn = $null
    $targetRoleArn = $null
    $targetBoundaryArn = $null
    $targetPolicyArn = $null
    $subjectBoundaryArn = $null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    $result.replacement_session.cleared_at_end = $true

    if ($teardownFailures.Count -gt 0) {
        $result.teardown['failure_codes'] = @($teardownFailures)
    }

    if ($writeEvidence) {
        $evidenceJson = $result | ConvertTo-Json -Depth 20
        $evidenceBytes = [Text.UTF8Encoding]::new($false).GetBytes(
            $evidenceJson + [Environment]::NewLine
        )
        $evidenceStream = [IO.File]::Open(
            $evidencePath,
            [IO.FileMode]::CreateNew,
            [IO.FileAccess]::Write,
            [IO.FileShare]::None
        )
        try {
            $evidenceStream.Write($evidenceBytes, 0, $evidenceBytes.Length)
        } finally {
            $evidenceStream.Dispose()
        }
    }
}

$safeSummary = [ordered]@{
    result = $result.result
    status = $result.status
    replacement_session = if ($result.replacement_session.mfa_backed) { 'MFA_BACKED_AND_CLEARED' } else { 'NOT_ESTABLISHED' }
    setup_teardown = if ($result.teardown.complete) { 'COMPLETE' } else { 'INCOMPLETE' }
    authorization_113 = $result.authorization_113.status
    root_security = $result.root_security_visibility
    failure_code = $result.failure_code
    attempt_id = $result.attempt_id
    predecessor_evidence = $result.predecessor_evidence
    evidence_path = $result.evidence_path
    secrets_printed = $false
}
$safeSummary | ConvertTo-Json -Depth 6
if ($isLocalTest) {
    return
}
if ($result.result -in @('PASS','LOCAL_TEST_PASS')) {
    exit 0
}
exit 1
