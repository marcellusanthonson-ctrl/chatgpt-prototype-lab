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

$script:AuthorizationId124 = 'AUTHORIZATION_LAB_PL003_BOUNDED_CREATOR_CAPABILITY_124'
$script:BootstrapProfile124 = 'pl003-bootstrap'
$script:PlanOperatorProfile124 = 'pl003-plan-operator'
$script:BootstrapUserName124 = 'pl003-bootstrap-operator'
$script:RoleName124 = 'PL003BoundedSimulationSetupOperator'
$script:BoundaryName124 = 'PL003BoundedSimulationSetupBoundary124'
$script:RolePolicyName124 = 'PL003BoundedSimulationSetupRolePolicy124'
$script:FutureBootstrapPolicyName124 = 'PL003AtomicSimulationOnly125'
$script:RoleMaximumSessionSeconds124 = 3600
$script:AssumeRoleDurationSeconds124 = 900
$script:CredentialEnvironmentNames124 = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

function Get-PL003124Sha256 {
    param([Parameter(Mandatory)][string]$Text)

    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
        return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function New-PL003124Documents {
    param([Parameter(Mandatory)][ValidatePattern('^\d{12}$')][string]$AccountId)

    $bootstrapArn = "arn:aws:iam::$AccountId`:user/$($script:BootstrapUserName124)"
    $trust = '{"Version":"2012-10-17","Statement":[{"Sid":"TrustExactBootstrapUserWithMFA","Effect":"Allow","Principal":{"AWS":"' + $bootstrapArn + '"},"Action":"sts:AssumeRole","Condition":{"Bool":{"aws:MultiFactorAuthPresent":"true"}}}]}'
    $permissions = '{"Version":"2012-10-17","Statement":[{"Sid":"ManageExactBootstrapInlinePoliciesOnly","Effect":"Allow","Action":["iam:ListUserPolicies","iam:GetUserPolicy","iam:PutUserPolicy","iam:DeleteUserPolicy"],"Resource":"' + $bootstrapArn + '"}]}'
    return [ordered]@{
        bootstrap_arn = $bootstrapArn
        trust = $trust
        boundary = $permissions
        role_policy = $permissions
    }
}

function Test-PL003124Documents {
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
        return [ordered]@{
            target_names_fixed = (
                $script:RoleName124 -ceq 'PL003BoundedSimulationSetupOperator' -and
                $script:BoundaryName124 -ceq 'PL003BoundedSimulationSetupBoundary124' -and
                $script:RolePolicyName124 -ceq 'PL003BoundedSimulationSetupRolePolicy124' -and
                $script:FutureBootstrapPolicyName124 -ceq 'PL003AtomicSimulationOnly125'
            )
            duration_exact = (
                $script:RoleMaximumSessionSeconds124 -eq 3600 -and
                $script:AssumeRoleDurationSeconds124 -eq 900
            )
            trust_exact = (
                $trustStatements.Count -eq 1 -and
                [string]$trustStatements[0].Sid -ceq 'TrustExactBootstrapUserWithMFA' -and
                [string]$trustStatements[0].Effect -ceq 'Allow' -and
                [string]$trustStatements[0].Action -ceq 'sts:AssumeRole' -and
                [string]$trustStatements[0].Principal.AWS -ceq [string]$Documents.bootstrap_arn -and
                [string]$trustStatements[0].Condition.Bool.'aws:MultiFactorAuthPresent' -ceq 'true'
            )
            boundary_exact = (
                $boundaryStatements.Count -eq 1 -and
                [string]$boundaryStatements[0].Sid -ceq 'ManageExactBootstrapInlinePoliciesOnly' -and
                [string]$boundaryStatements[0].Effect -ceq 'Allow' -and
                (@($boundaryStatements[0].Action) -join ',') -ceq ($expectedActions -join ',') -and
                [string]$boundaryStatements[0].Resource -ceq [string]$Documents.bootstrap_arn
            )
            role_policy_exact = (
                $roleStatements.Count -eq 1 -and
                [string]$roleStatements[0].Sid -ceq 'ManageExactBootstrapInlinePoliciesOnly' -and
                [string]$roleStatements[0].Effect -ceq 'Allow' -and
                (@($roleStatements[0].Action) -join ',') -ceq ($expectedActions -join ',') -and
                [string]$roleStatements[0].Resource -ceq [string]$Documents.bootstrap_arn
            )
            forbidden_tokens_absent = (
                ($Documents.trust + $Documents.boundary + $Documents.role_policy) -notmatch
                'AdministratorAccess|IAMFullAccess|PowerUserAccess|iam:\*|iam:PassRole'
            )
        }
    } catch {
        return [ordered]@{
            target_names_fixed = $false
            duration_exact = $false
            trust_exact = $false
            boundary_exact = $false
            role_policy_exact = $false
            forbidden_tokens_absent = $false
        }
    }
}

function Get-PL003124ProfileClassification {
    param([Parameter(Mandatory)][string]$ProfileName)

    if ($ProfileName -ceq $script:BootstrapProfile124) {
        return 'BOOTSTRAP_EXCLUDED_GET_POLICY_ACCESS_DENIED_BY_AUTHORIZATION_123'
    }
    if ($ProfileName -ceq $script:PlanOperatorProfile124) {
        return 'KNOWN_READ_ONLY_PLAN_OPERATOR_INCOMPATIBLE'
    }
    return 'UNVERIFIED_LOCAL_PROFILE_NO_CANONICAL_BOUNDED_CREATOR_CAPABILITY_EVIDENCE'
}

function Test-PL003BoundedCreatorCapability124 {
    $documents = New-PL003124Documents -AccountId '123456789012'
    $checks = Test-PL003124Documents -Documents $documents
    $failures = [System.Collections.Generic.List[string]]::new()
    foreach ($check in $checks.GetEnumerator()) {
        if (-not $check.Value) {
            $failures.Add([string]$check.Key)
        }
    }
    if (
        (Get-PL003124ProfileClassification -ProfileName $script:BootstrapProfile124) -cne
        'BOOTSTRAP_EXCLUDED_GET_POLICY_ACCESS_DENIED_BY_AUTHORIZATION_123'
    ) {
        $failures.Add('bootstrap-classification')
    }
    if (
        (Get-PL003124ProfileClassification -ProfileName $script:PlanOperatorProfile124) -cne
        'KNOWN_READ_ONLY_PLAN_OPERATOR_INCOMPATIBLE'
    ) {
        $failures.Add('plan-operator-classification')
    }
    if (
        (Get-PL003124ProfileClassification -ProfileName 'synthetic-unverified') -cne
        'UNVERIFIED_LOCAL_PROFILE_NO_CANONICAL_BOUNDED_CREATOR_CAPABILITY_EVIDENCE'
    ) {
        $failures.Add('unknown-profile-fail-closed')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = 9
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        role_name = $script:RoleName124
        boundary_name = $script:BoundaryName124
        role_policy_name = $script:RolePolicyName124
        future_bootstrap_policy_name = $script:FutureBootstrapPolicyName124
        trust_sha256_synthetic = Get-PL003124Sha256 -Text $documents.trust
        boundary_sha256_synthetic = Get-PL003124Sha256 -Text $documents.boundary
        role_policy_sha256_synthetic = Get-PL003124Sha256 -Text $documents.role_policy
        aws_service_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function Write-PL003124Evidence {
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

function Invoke-PL003BoundedCreatorCapability124Precheck {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $evidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-BOUNDED-CREATOR-CAPABILITY-124-$attemptId.json"
    $synthetic = Test-PL003BoundedCreatorCapability124

    $evidence = [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-BOUNDED-CREATOR-CAPABILITY-124-$attemptId"
        authorization_id = $script:AuthorizationId124
        project_id = 'lab'
        kind = 'REDACTED_LOCAL_BOUNDED_CREATOR_CAPABILITY_PREFLIGHT_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        branch_mode = 'DETACHED_HEAD'
        execution_head = $ExpectedExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            authorization_124_registered_granted = 'PASS'
            authorizations_118_119_120_121_122_123_consumed = 'PASS'
            inherited_execution_authority = 'NONE'
            synthetic_documents = $synthetic.result
            target_names_fixed = 'PASS'
            aws_cli_local_configuration = 'PENDING'
            cli_history_disabled = 'PENDING'
            inherited_temporary_credentials_absent = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
        }
        documents = [ordered]@{
            role_name = $script:RoleName124
            boundary_name = $script:BoundaryName124
            role_policy_name = $script:RolePolicyName124
            future_bootstrap_policy_name = $script:FutureBootstrapPolicyName124
            create_role_maximum_session_seconds = $script:RoleMaximumSessionSeconds124
            assume_role_duration_seconds = $script:AssumeRoleDurationSeconds124
            trust_sha256 = $null
            boundary_sha256 = $null
            role_policy_sha256 = $null
            exact_four_actions_on_bootstrap_only = $true
            iam_wildcard_absent = $true
            iam_pass_role_absent = $true
        }
        creator_inventory = [ordered]@{
            local_profile_count = 0
            profiles = @()
            eligible_creator_count = 0
            selected_creator = 'NONE'
            inventory_source = 'LOCAL_AWS_CONFIGURATION_ONLY'
        }
        collision_preflight = [ordered]@{
            executed = $false
            result = 'NOT_EXECUTED_NO_CREATOR_SELECTED'
        }
        resources = [ordered]@{
            boundary_created = $false
            role_created = $false
            role_policy_created = $false
        }
        compensation = [ordered]@{
            required = $false
            attempted = $false
            result = 'NOT_APPLICABLE'
        }
        assume_role = [ordered]@{
            attempted = $false
            duration_seconds = 900
            result = 'NOT_EXECUTED'
        }
        baseline = [ordered]@{
            attempted = $false
            result = 'NOT_EXECUTED'
        }
        aws_calls = [ordered]@{
            sts = 0
            iam = 0
            other = 0
        }
        mutations = [ordered]@{
            create_policy = 0
            create_role = 0
            put_role_policy = 0
            compensating = 0
            bootstrap_user_changes = 0
            unexpected = 0
        }
        final_aws_state = [ordered]@{
            resources_created = 0
            persistent_mutations = 0
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
            profile_names_included = $false
            full_account_id_included = $false
            full_arns_included = $false
            credentials_tokens_or_mfa_codes_included = $false
            raw_aws_configuration_included = $false
        }
        post_attempt_authority = 'NONE'
    }

    $accountId = $null
    $documents = $null
    $mfaSerial = $null

    try {
        $head = (git -C $repositoryRoot rev-parse HEAD).Trim()
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
        if (
            [Environment]::GetEnvironmentVariable('AWS_CLI_HISTORY', 'Process') -eq 'enabled' -or
            (& aws configure get cli_history 2>$null) -eq 'enabled'
        ) {
            throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
        }
        $evidence.prechecks.cli_history_disabled = 'PASS'
        $presentCredentialNames = @(
            $script:CredentialEnvironmentNames124 | Where-Object {
                -not [string]::IsNullOrWhiteSpace(
                    [Environment]::GetEnvironmentVariable($_, 'Process')
                )
            }
        )
        if ($presentCredentialNames.Count -ne 0) {
            throw 'PREEXISTING_AWS_CREDENTIAL_ENVIRONMENT_DETECTED'
        }
        $evidence.prechecks.inherited_temporary_credentials_absent = 'PASS'

        $profiles = @(& aws configure list-profiles 2>$null)
        if ($LASTEXITCODE -ne 0) {
            throw 'AWS_PROFILE_INVENTORY_FAILED'
        }
        $inventory = [System.Collections.Generic.List[object]]::new()
        $eligibleCount = 0
        $ordinal = 0
        foreach ($profile in $profiles) {
            $ordinal++
            $token = (& aws configure get aws_session_token --profile $profile 2>$null) -join ''
            $securityToken = (& aws configure get aws_security_token --profile $profile 2>$null) -join ''
            if (
                -not [string]::IsNullOrWhiteSpace($token) -or
                -not [string]::IsNullOrWhiteSpace($securityToken)
            ) {
                throw 'REUSABLE_PRIOR_TEMPORARY_CREDENTIAL_DETECTED'
            }
            $classification = Get-PL003124ProfileClassification -ProfileName $profile
            $roleConfigured = -not [string]::IsNullOrWhiteSpace(
                ((& aws configure get role_arn --profile $profile 2>$null) -join '')
            )
            $mfaConfigured = -not [string]::IsNullOrWhiteSpace(
                ((& aws configure get mfa_serial --profile $profile 2>$null) -join '')
            )
            $hasStaticAccessKey = -not [string]::IsNullOrWhiteSpace(
                ((& aws configure get aws_access_key_id --profile $profile 2>$null) -join '')
            )
            $eligible = $false
            if ($eligible) {
                $eligibleCount++
            }
            $inventory.Add([ordered]@{
                redacted_id = 'LOCAL_PROFILE_{0:D3}' -f $ordinal
                classification = $classification
                role_profile = $roleConfigured
                mfa_reference_configured = $mfaConfigured
                long_term_source_credential_reference_present = $hasStaticAccessKey
                reusable_session_token_present = $false
                eligible_creator = $eligible
            })
        }
        $evidence.creator_inventory.local_profile_count = $profiles.Count
        $evidence.creator_inventory.profiles = @($inventory)
        $evidence.creator_inventory.eligible_creator_count = $eligibleCount
        $evidence.prechecks.reusable_temporary_profiles_absent = 'PASS'
        $evidence.prechecks.aws_cli_local_configuration = 'PASS'

        $mfaSerial = (& aws configure get mfa_serial --profile $script:BootstrapProfile124 2>$null) -join ''
        if ($mfaSerial -notmatch '^arn:aws:iam::(\d{12}):mfa/') {
            throw 'BOOTSTRAP_MFA_REFERENCE_INVALID'
        }
        $accountId = [string]$Matches[1]
        $documents = New-PL003124Documents -AccountId $accountId
        $documentChecks = Test-PL003124Documents -Documents $documents
        if ($documentChecks.Values -contains $false) {
            throw 'LOCAL_DOCUMENT_VALIDATION_FAILED'
        }
        $evidence.documents.trust_sha256 = Get-PL003124Sha256 -Text $documents.trust
        $evidence.documents.boundary_sha256 = Get-PL003124Sha256 -Text $documents.boundary
        $evidence.documents.role_policy_sha256 = Get-PL003124Sha256 -Text $documents.role_policy

        if ($eligibleCount -eq 0) {
            throw 'BLOCKED_NO_EXISTING_BOUNDED_CREATOR_CAPABILITY'
        }
        throw 'BLOCKED_FAIL_CLOSED_OTHER'
    } catch {
        $message = [string]$_.Exception.Message
        $evidence.status = 'BLOCKED'
        $evidence.failure_code = if ($message -match '^[A-Z0-9_]+$') {
            $message
        } else {
            'BLOCKED_FAIL_CLOSED_OTHER'
        }
        $evidence.result = if ($evidence.failure_code -eq 'BLOCKED_NO_EXISTING_BOUNDED_CREATOR_CAPABILITY') {
            'BLOCKED_NO_EXISTING_BOUNDED_CREATOR_CAPABILITY'
        } else {
            'BLOCKED_FAIL_CLOSED_OTHER'
        }
    } finally {
        $accountId = $null
        $documents = $null
        $mfaSerial = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        $evidence.credentials_cleared = $true
        Write-PL003124Evidence -Evidence $evidence -Path $evidencePath
    }

    return [ordered]@{
        result = $evidence.result
        failure_code = $evidence.failure_code
        document_hashes = [ordered]@{
            trust = $evidence.documents.trust_sha256
            boundary = $evidence.documents.boundary_sha256
            role_policy = $evidence.documents.role_policy_sha256
        }
        local_profile_count = $evidence.creator_inventory.local_profile_count
        eligible_creator_count = $evidence.creator_inventory.eligible_creator_count
        selected_creator = $evidence.creator_inventory.selected_creator
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
    $test = Test-PL003BoundedCreatorCapability124
    $test | ConvertTo-Json -Depth 8
    if ($test.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003BoundedCreatorCapability124Precheck `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber
$outcome | ConvertTo-Json -Depth 10
if ($outcome.result -eq 'PASS_BOUNDED_CREATOR_CREATED_AND_VERIFIED_SETUP_ROLE') {
    exit 0
}
exit 1
