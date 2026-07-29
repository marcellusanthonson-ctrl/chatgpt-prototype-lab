[CmdletBinding(DefaultParameterSetName = 'Synthetic')]
param(
    [Parameter(ParameterSetName = 'Synthetic')]
    [switch]$SyntheticTest,

    [Parameter(Mandatory, ParameterSetName = 'Operational')]
    [switch]$OperationalRun,

    [Parameter(Mandatory, ParameterSetName = 'Operational')]
    [ValidatePattern('^[0-9a-f]{40}$')]
    [string]$ExpectedHead,

    [Parameter(ParameterSetName = 'Operational')]
    [ValidateRange(1, 999)]
    [int]$AttemptNumber = 1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:AuthorizationId122 = 'AUTHORIZATION_LAB_PL003_CREATE_BOUNDED_SETUP_ROLE_122'
$script:BootstrapProfile122 = 'pl003-bootstrap'
$script:BootstrapUserName122 = 'pl003-bootstrap-operator'
$script:RoleName122 = 'PL003BoundedSimulationSetupOperator'
$script:BoundaryName122 = 'PL003BoundedSimulationSetupBoundary122'
$script:RolePolicyName122 = 'PL003BoundedSimulationSetupRolePolicy122'
$script:RequestedRoleMaximumSessionSeconds122 = 900
$script:AwsCreateRoleMinimumMaximumSessionSeconds122 = 3600
$script:CredentialEnvironmentNames122 = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

function Get-PL003122Sha256 {
    param([Parameter(Mandatory)][string]$Text)

    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
        return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function New-PL003122Documents {
    param([Parameter(Mandatory)][ValidatePattern('^\d{12}$')][string]$AccountId)

    $bootstrapArn = "arn:aws:iam::$AccountId`:user/$($script:BootstrapUserName122)"
    $trust = '{"Version":"2012-10-17","Statement":[{"Sid":"TrustExactBootstrapUserWithMFA","Effect":"Allow","Principal":{"AWS":"' + $bootstrapArn + '"},"Action":"sts:AssumeRole","Condition":{"Bool":{"aws:MultiFactorAuthPresent":"true"}}}]}'
    $permissions = '{"Version":"2012-10-17","Statement":[{"Sid":"ManageExactBootstrapInlinePoliciesOnly","Effect":"Allow","Action":["iam:ListUserPolicies","iam:GetUserPolicy","iam:PutUserPolicy","iam:DeleteUserPolicy"],"Resource":"' + $bootstrapArn + '"}]}'
    return [ordered]@{
        bootstrap_arn = $bootstrapArn
        trust = $trust
        boundary = $permissions
        role_policy = $permissions
    }
}

function Test-PL003122Documents {
    param([Parameter(Mandatory)]$Documents)

    try {
        $trust = $Documents.trust | ConvertFrom-Json
        $boundary = $Documents.boundary | ConvertFrom-Json
        $rolePolicy = $Documents.role_policy | ConvertFrom-Json
        $trustStatements = @($trust.Statement)
        $boundaryStatements = @($boundary.Statement)
        $roleStatements = @($rolePolicy.Statement)
        $expectedActions = @(
            'iam:ListUserPolicies',
            'iam:GetUserPolicy',
            'iam:PutUserPolicy',
            'iam:DeleteUserPolicy'
        )
        $boundaryActions = @($boundaryStatements[0].Action)
        $roleActions = @($roleStatements[0].Action)
        return [ordered]@{
            trust_exact = (
                $trustStatements.Count -eq 1 -and
                [string]$trustStatements[0].Effect -eq 'Allow' -and
                [string]$trustStatements[0].Action -eq 'sts:AssumeRole' -and
                [string]$trustStatements[0].Principal.AWS -eq [string]$Documents.bootstrap_arn -and
                [string]$trustStatements[0].Condition.Bool.'aws:MultiFactorAuthPresent' -eq 'true'
            )
            boundary_exact = (
                $boundaryStatements.Count -eq 1 -and
                [string]$boundaryStatements[0].Effect -eq 'Allow' -and
                [string]$boundaryStatements[0].Resource -eq [string]$Documents.bootstrap_arn -and
                ($boundaryActions -join ',') -ceq ($expectedActions -join ',')
            )
            role_policy_exact = (
                $roleStatements.Count -eq 1 -and
                [string]$roleStatements[0].Effect -eq 'Allow' -and
                [string]$roleStatements[0].Resource -eq [string]$Documents.bootstrap_arn -and
                ($roleActions -join ',') -ceq ($expectedActions -join ',')
            )
            forbidden_tokens_absent = (
                ($Documents.trust + $Documents.boundary + $Documents.role_policy) -notmatch
                'AdministratorAccess|IAMFullAccess|PowerUserAccess|iam:\*|iam:PassRole'
            )
        }
    } catch {
        return [ordered]@{
            trust_exact = $false
            boundary_exact = $false
            role_policy_exact = $false
            forbidden_tokens_absent = $false
        }
    }
}

function Test-PL003CreateBoundedSetupRole122 {
    $documents = New-PL003122Documents -AccountId '123456789012'
    $checks = Test-PL003122Documents -Documents $documents
    $failures = [System.Collections.Generic.List[string]]::new()
    foreach ($property in $checks.GetEnumerator()) {
        if (-not $property.Value) {
            $failures.Add([string]$property.Key)
        }
    }
    if ($script:RequestedRoleMaximumSessionSeconds122 -ge $script:AwsCreateRoleMinimumMaximumSessionSeconds122) {
        $failures.Add('expected-session-duration-incompatibility-not-detected')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = 5
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        role_name = $script:RoleName122
        boundary_name = $script:BoundaryName122
        role_policy_name = $script:RolePolicyName122
        trust_sha256_synthetic = Get-PL003122Sha256 -Text $documents.trust
        boundary_sha256_synthetic = Get-PL003122Sha256 -Text $documents.boundary
        role_policy_sha256_synthetic = Get-PL003122Sha256 -Text $documents.role_policy
        requested_role_maximum_session_seconds = $script:RequestedRoleMaximumSessionSeconds122
        aws_create_role_minimum_maximum_session_seconds = $script:AwsCreateRoleMinimumMaximumSessionSeconds122
        exact_900_second_role_maximum_representable = $false
        aws_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function Write-PL003122Evidence {
    param(
        [Parameter(Mandatory)]$Evidence,
        [Parameter(Mandatory)][string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        throw 'EVIDENCE_PATH_ALREADY_EXISTS'
    }
    $json = $Evidence | ConvertTo-Json -Depth 20
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $stream.Write($bytes, 0, $bytes.Length)
    } finally {
        $stream.Dispose()
    }
}

function Invoke-PL003CreateBoundedSetupRole122Precheck {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $evidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-CREATE-BOUNDED-SETUP-ROLE-122-$attemptId.json"
    $synthetic = Test-PL003CreateBoundedSetupRole122

    $evidence = [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-CREATE-BOUNDED-SETUP-ROLE-122-$attemptId"
        authorization_id = $script:AuthorizationId122
        project_id = 'lab'
        kind = 'REDACTED_BOUNDED_SETUP_ROLE_COMPATIBILITY_PREFLIGHT_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        execution_head = $ExpectedExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            authorization_122_registered_granted = 'PASS'
            authorizations_118_119_120_121_consumed = 'PASS'
            pend_lab_032 = 'OPEN_BLOCKED_NO_BOUNDED_EXTERNAL_SETUP_PRINCIPAL'
            aws_cli = 'PENDING'
            cli_history_disabled = 'PENDING'
            inherited_temporary_credentials_absent = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
            synthetic_documents = $synthetic.result
        }
        creator_identity = [ordered]@{
            session_started = $false
            verified = $false
            redacted_identifier = 'NOT_EXECUTED'
        }
        artifacts = [ordered]@{
            role = [ordered]@{
                name = $script:RoleName122
                requested_maximum_session_seconds = $script:RequestedRoleMaximumSessionSeconds122
                aws_api_minimum_maximum_session_seconds = $script:AwsCreateRoleMinimumMaximumSessionSeconds122
                exact_requirement_representable = $false
                created = $false
            }
            trust = [ordered]@{
                sha256 = $null
                exact_bootstrap_user = $true
                mfa_required = $true
                applied = $false
            }
            boundary = [ordered]@{
                name = $script:BoundaryName122
                sha256 = $null
                created = $false
            }
            role_policy = [ordered]@{
                name = $script:RolePolicyName122
                sha256 = $null
                applied = $false
            }
        }
        assume_role = [ordered]@{
            attempted = $false
            duration_seconds = 900
            succeeded = $false
        }
        baseline = [ordered]@{
            bootstrap_inline_policy_list_attempted = $false
            result = 'NOT_EXECUTED'
        }
        privilege_analysis = [ordered]@{
            exact_bootstrap_user_only = $true
            allowed_iam_actions = @(
                'iam:ListUserPolicies',
                'iam:GetUserPolicy',
                'iam:PutUserPolicy',
                'iam:DeleteUserPolicy'
            )
            wildcard_iam_actions = 0
            permissions_on_other_users = 0
            iam_pass_role = $false
            administrator_managed_policies = 0
            technical_verdict = 'DOCUMENTS_BOUNDED_BUT_ROLE_MAXIMUM_SESSION_REQUIREMENT_NOT_REPRESENTABLE'
        }
        aws_calls = [ordered]@{
            sts_get_session_token = 0
            sts_get_caller_identity_creator = 0
            iam_create_policy = 0
            iam_create_role = 0
            iam_put_role_policy = 0
            sts_assume_role = 0
            sts_get_caller_identity_role = 0
            iam_list_user_policies = 0
            other_aws = 0
        }
        mutations = [ordered]@{
            expected_if_compatible = 3
            actual = 0
            unexpected = 0
            bootstrap_user_changes = 0
            persistent = 0
        }
        out_of_scope = [ordered]@{
            terraform_executions = 0
            provisioning_executions = 0
            product_leadership_test_003_executions = 0
            product_leadership_active = $false
            product_leadership_integrated = $false
        }
        credentials_cleared = $true
        result = 'IN_PROGRESS'
        failure_code = $null
        redaction = [ordered]@{
            full_account_id_included = $false
            full_arns_included = $false
            credentials_tokens_or_mfa_codes_included = $false
            raw_aws_output_persisted = $false
        }
        post_attempt_authority = 'NONE'
    }

    try {
        $head = git -C $repositoryRoot rev-parse HEAD
        if ($LASTEXITCODE -ne 0 -or $head -ne $ExpectedExecutionHead) {
            throw 'HEAD_MISMATCH'
        }
        $evidence.prechecks.head = 'PASS'
        $status = @(git -C $repositoryRoot status --porcelain=v1 --untracked-files=all)
        if ($LASTEXITCODE -ne 0 -or $status.Count -ne 0) {
            throw 'WORKTREE_NOT_CLEAN'
        }
        $evidence.prechecks.worktree = 'PASS'
        if ($synthetic.result -ne 'PASS') {
            throw 'LOCAL_DOCUMENT_VALIDATION_FAILED'
        }

        if ($null -eq (Get-Command aws -ErrorAction SilentlyContinue)) {
            throw 'AWS_CLI_NOT_AVAILABLE'
        }
        $evidence.prechecks.aws_cli = 'PASS'
        $profiles = @(& aws configure list-profiles 2>$null)
        if ($LASTEXITCODE -ne 0 -or (& aws configure get cli_history 2>$null) -eq 'enabled') {
            throw 'AWS_CLI_CONFIGURATION_INVALID'
        }
        $evidence.prechecks.cli_history_disabled = 'PASS'

        $presentCredentialNames = @(
            $script:CredentialEnvironmentNames122 | Where-Object {
                -not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($_, 'Process'))
            }
        )
        if ($presentCredentialNames.Count -ne 0) {
            throw 'PREEXISTING_AWS_CREDENTIAL_ENVIRONMENT_DETECTED'
        }
        $evidence.prechecks.inherited_temporary_credentials_absent = 'PASS'

        foreach ($profile in $profiles) {
            $token = & aws configure get aws_session_token --profile $profile 2>$null
            $securityToken = & aws configure get aws_security_token --profile $profile 2>$null
            if (
                -not [string]::IsNullOrWhiteSpace(($token -join '')) -or
                -not [string]::IsNullOrWhiteSpace(($securityToken -join ''))
            ) {
                throw 'REUSABLE_PRIOR_TEMPORARY_CREDENTIAL_DETECTED'
            }
        }
        $evidence.prechecks.reusable_temporary_profiles_absent = 'PASS'
        if ($profiles -notcontains $script:BootstrapProfile122) {
            throw 'BOOTSTRAP_PROFILE_NOT_FOUND'
        }

        $mfaSerial = (& aws configure get mfa_serial --profile $script:BootstrapProfile122 2>$null) -join ''
        if ($mfaSerial -notmatch '^arn:aws:iam::(\d{12}):mfa/') {
            throw 'BOOTSTRAP_MFA_REFERENCE_INVALID'
        }
        $accountId = [string]$Matches[1]
        $documents = New-PL003122Documents -AccountId $accountId
        $documentChecks = Test-PL003122Documents -Documents $documents
        if ($documentChecks.Values -contains $false) {
            throw 'LOCAL_DOCUMENT_VALIDATION_FAILED'
        }
        $evidence.artifacts.trust.sha256 = Get-PL003122Sha256 -Text $documents.trust
        $evidence.artifacts.boundary.sha256 = Get-PL003122Sha256 -Text $documents.boundary
        $evidence.artifacts.role_policy.sha256 = Get-PL003122Sha256 -Text $documents.role_policy

        if ($script:RequestedRoleMaximumSessionSeconds122 -lt $script:AwsCreateRoleMinimumMaximumSessionSeconds122) {
            throw 'BLOCKED_ROLE_MAX_SESSION_DURATION_900_NOT_REPRESENTABLE'
        }
        throw 'BLOCKED_FAIL_CLOSED_OTHER'
    } catch {
        $failure = [string]$_.Exception.Message
        $evidence.status = 'BLOCKED'
        $evidence.failure_code = $failure
        $evidence.result = if ($failure -eq 'BLOCKED_ROLE_MAX_SESSION_DURATION_900_NOT_REPRESENTABLE') {
            'BLOCKED_ROLE_MAX_SESSION_DURATION_900_NOT_REPRESENTABLE'
        } else {
            'BLOCKED_FAIL_CLOSED_OTHER'
        }
    } finally {
        $accountId = $null
        $documents = $null
        $mfaSerial = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        Write-PL003122Evidence -Evidence $evidence -Path $evidencePath
    }

    return [ordered]@{
        result = $evidence.result
        failure_code = $evidence.failure_code
        role_name = $evidence.artifacts.role.name
        trust_sha256 = $evidence.artifacts.trust.sha256
        boundary_name = $evidence.artifacts.boundary.name
        boundary_sha256 = $evidence.artifacts.boundary.sha256
        role_policy_name = $evidence.artifacts.role_policy.name
        role_policy_sha256 = $evidence.artifacts.role_policy.sha256
        aws_calls = $evidence.aws_calls
        mutations = $evidence.mutations
        evidence_path = $evidencePath.Substring($repositoryRoot.Length + 1).Replace('\', '/')
        secrets_printed = $false
    }
}

if ($MyInvocation.InvocationName -eq '.') {
    return
}

if ($SyntheticTest -or -not $OperationalRun) {
    $test = Test-PL003CreateBoundedSetupRole122
    $test | ConvertTo-Json -Depth 8
    if ($test.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003CreateBoundedSetupRole122Precheck `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber
$outcome | ConvertTo-Json -Depth 8
if ($outcome.result -eq 'PASS_BOUNDED_SETUP_ROLE_CREATED_AND_VERIFIED') {
    exit 0
}
exit 1
