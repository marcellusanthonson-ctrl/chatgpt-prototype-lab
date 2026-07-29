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

$requestedOperationalRun123 = [bool]$OperationalRun
$requestedSyntheticTest123 = [bool]$SyntheticTest
$requestedExpectedHead123 = $ExpectedHead
$requestedAttemptNumber123 = $AttemptNumber

$diagnosticScript123 = Join-Path $PSScriptRoot 'Invoke-PL003BootstrapDiagnosticPreflight.ps1'
. $diagnosticScript123
$documentScript123 = Join-Path $PSScriptRoot 'Invoke-PL003CreateBoundedSetupRole122Precheck.ps1'
. $documentScript123

$OperationalRun = $requestedOperationalRun123
$SyntheticTest = $requestedSyntheticTest123
$ExpectedHead = $requestedExpectedHead123
$AttemptNumber = $requestedAttemptNumber123

$script:AuthorizationId123 = 'AUTHORIZATION_LAB_PL003_CREATE_BOUNDED_SETUP_ROLE_COMPATIBILITY_123'
$script:BootstrapProfile123 = 'pl003-bootstrap'
$script:BootstrapUserName123 = 'pl003-bootstrap-operator'
$script:RoleName123 = 'PL003BoundedSimulationSetupOperator'
$script:BoundaryName123 = 'PL003BoundedSimulationSetupBoundary122'
$script:RolePolicyName123 = 'PL003BoundedSimulationSetupRolePolicy122'
$script:CreateRoleMaximumSessionSeconds123 = 3600
$script:AssumeRoleDurationSeconds123 = 900
$script:RoleSessionName123 = 'PL003Authorization123'
$script:CredentialEnvironmentNames123 = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

function Test-PL003123PermissionDocument {
    param(
        [Parameter(Mandatory)]$Document,
        [Parameter(Mandatory)][string]$ExpectedBootstrapArn
    )

    try {
        $statements = @($Document.Statement)
        if ([string]$Document.Version -ne '2012-10-17' -or $statements.Count -ne 1) {
            return $false
        }
        $expectedActions = @(
            'iam:ListUserPolicies',
            'iam:GetUserPolicy',
            'iam:PutUserPolicy',
            'iam:DeleteUserPolicy'
        )
        $statement = $statements[0]
        return (
            [string]$statement.Sid -eq 'ManageExactBootstrapInlinePoliciesOnly' -and
            [string]$statement.Effect -eq 'Allow' -and
            (@($statement.Action) -join ',') -ceq ($expectedActions -join ',') -and
            @($statement.Resource).Count -eq 1 -and
            [string]@($statement.Resource)[0] -ceq $ExpectedBootstrapArn
        )
    } catch {
        return $false
    }
}

function Test-PL003123TrustDocument {
    param(
        [Parameter(Mandatory)]$Document,
        [Parameter(Mandatory)][string]$ExpectedBootstrapArn
    )

    try {
        $statements = @($Document.Statement)
        if ([string]$Document.Version -ne '2012-10-17' -or $statements.Count -ne 1) {
            return $false
        }
        $statement = $statements[0]
        return (
            [string]$statement.Sid -eq 'TrustExactBootstrapUserWithMFA' -and
            [string]$statement.Effect -eq 'Allow' -and
            [string]$statement.Action -eq 'sts:AssumeRole' -and
            [string]$statement.Principal.AWS -ceq $ExpectedBootstrapArn -and
            [string]$statement.Condition.Bool.'aws:MultiFactorAuthPresent' -ceq 'true'
        )
    } catch {
        return $false
    }
}

function Get-PL003123CompensationPlan {
    param(
        [bool]$BoundaryCreated,
        [bool]$RoleCreated,
        [bool]$RolePolicyCreated
    )

    $plan = [System.Collections.Generic.List[string]]::new()
    if ($RolePolicyCreated) {
        $plan.Add('DeleteRolePolicy')
    }
    if ($RoleCreated) {
        $plan.Add('DeleteRole')
    }
    if ($BoundaryCreated) {
        $plan.Add('DeletePolicy')
    }
    return @($plan)
}

function Test-PL003CreateBoundedSetupRoleCompatibility123 {
    $failures = [System.Collections.Generic.List[string]]::new()
    $documents = New-PL003122Documents -AccountId '123456789012'
    $documentChecks = Test-PL003122Documents -Documents $documents

    foreach ($check in $documentChecks.GetEnumerator()) {
        if (-not $check.Value) {
            $failures.Add("document-$($check.Key)")
        }
    }
    if (-not (Test-PL003123TrustDocument `
        -Document ($documents.trust | ConvertFrom-Json) `
        -ExpectedBootstrapArn $documents.bootstrap_arn)) {
        $failures.Add('effective-trust-validator')
    }
    if (-not (Test-PL003123PermissionDocument `
        -Document ($documents.boundary | ConvertFrom-Json) `
        -ExpectedBootstrapArn $documents.bootstrap_arn)) {
        $failures.Add('effective-boundary-validator')
    }
    if (-not (Test-PL003123PermissionDocument `
        -Document ($documents.role_policy | ConvertFrom-Json) `
        -ExpectedBootstrapArn $documents.bootstrap_arn)) {
        $failures.Add('effective-role-policy-validator')
    }
    if (
        $script:CreateRoleMaximumSessionSeconds123 -ne 3600 -or
        $script:AssumeRoleDurationSeconds123 -ne 900 -or
        $script:AssumeRoleDurationSeconds123 -gt $script:CreateRoleMaximumSessionSeconds123
    ) {
        $failures.Add('duration-compatibility')
    }

    $fullCompensation = @(
        Get-PL003123CompensationPlan `
            -BoundaryCreated $true `
            -RoleCreated $true `
            -RolePolicyCreated $true
    )
    if (($fullCompensation -join ',') -cne 'DeleteRolePolicy,DeleteRole,DeletePolicy') {
        $failures.Add('full-compensation-order')
    }
    $partialCompensation = @(
        Get-PL003123CompensationPlan `
            -BoundaryCreated $true `
            -RoleCreated $false `
            -RolePolicyCreated $false
    )
    if (($partialCompensation -join ',') -cne 'DeletePolicy') {
        $failures.Add('partial-compensation-order')
    }

    $classifier = Test-PL003BootstrapDiagnosticClassifier
    if ($classifier.result -ne 'PASS') {
        $failures.Add('sanitized-error-classifier')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = 10 + [int]$classifier.case_count
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        classifier_result = $classifier.result
        role_name = $script:RoleName123
        boundary_name = $script:BoundaryName123
        role_policy_name = $script:RolePolicyName123
        create_role_maximum_session_seconds = $script:CreateRoleMaximumSessionSeconds123
        assume_role_duration_seconds = $script:AssumeRoleDurationSeconds123
        trust_sha256_synthetic = Get-PL003122Sha256 -Text $documents.trust
        boundary_sha256_synthetic = Get-PL003122Sha256 -Text $documents.boundary
        role_policy_sha256_synthetic = Get-PL003122Sha256 -Text $documents.role_policy
        aws_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function New-PL003123CallCounter {
    return [ordered]@{
        sts_get_session_token = 0
        sts_get_caller_identity_creator = 0
        iam_get_policy_collision = 0
        iam_get_role_collision = 0
        iam_create_policy = 0
        iam_create_role = 0
        iam_put_role_policy = 0
        iam_get_policy_verification = 0
        iam_get_policy_version = 0
        iam_get_role_verification = 0
        iam_get_role_policy = 0
        sts_assume_role = 0
        sts_get_caller_identity_role = 0
        iam_list_user_policies = 0
        iam_delete_role_policy_compensation = 0
        iam_delete_role_compensation = 0
        iam_delete_policy_compensation = 0
        other_aws = 0
    }
}

function Set-PL003123FailureMetadata {
    param(
        [Parameter(Mandatory)]$Evidence,
        [Parameter(Mandatory)]$Call,
        [Parameter(Mandatory)][string]$Service,
        [Parameter(Mandatory)][string]$Operation
    )

    $Evidence.failure_metadata = Get-PL003SanitizedCallMetadata `
        -ExitCode $Call.ExitCode `
        -StdErr $Call.RawStdErr `
        -Service $Service `
        -Operation $Operation
}

function Invoke-PL003CreateBoundedSetupRoleCompatibility123 {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $evidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-CREATE-BOUNDED-SETUP-ROLE-COMPATIBILITY-123-$attemptId.json"
    $temporaryDocumentDirectory = Join-Path $repositoryRoot 'projects\lab\scripts\.pl003-auth123-tmp'
    $trustPath = Join-Path $temporaryDocumentDirectory 'trust.json'
    $boundaryPath = Join-Path $temporaryDocumentDirectory 'boundary.json'
    $rolePolicyPath = Join-Path $temporaryDocumentDirectory 'role-policy.json'
    $synthetic = Test-PL003CreateBoundedSetupRoleCompatibility123
    $calls = New-PL003123CallCounter

    $evidence = [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-CREATE-BOUNDED-SETUP-ROLE-COMPATIBILITY-123-$attemptId"
        authorization_id = $script:AuthorizationId123
        project_id = 'lab'
        kind = 'REDACTED_BOUNDED_SETUP_ROLE_COMPATIBILITY_EXECUTION_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        branch_mode = 'DETACHED_HEAD'
        execution_head = $ExpectedExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            authorization_123_registered_granted = 'PASS'
            authorizations_118_119_120_121_122_consumed = 'PASS'
            inherited_execution_authority = 'NONE'
            pend_lab_032_before_execution = 'OPEN_BLOCKED_ROLE_MAX_SESSION_DURATION_900_NOT_REPRESENTABLE_NO_ACTIVE_EXECUTION_AUTHORITY'
            synthetic_and_documents = $synthetic.result
            sanitized_error_classifier = $synthetic.classifier_result
            aws_cli = 'PENDING'
            cli_history_disabled = 'PENDING'
            inherited_temporary_credentials_absent = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
        }
        creator_identity = [ordered]@{
            verified = $false
            redacted_identifier = 'NOT_EXECUTED'
            mfa_session = 'NOT_EXECUTED'
        }
        collision_preflight = [ordered]@{
            boundary_absent = $false
            role_absent = $false
            result = 'NOT_EXECUTED'
        }
        artifacts = [ordered]@{
            role = [ordered]@{
                name = $script:RoleName123
                create_role_maximum_session_seconds = $script:CreateRoleMaximumSessionSeconds123
                created = $false
                verified = $false
            }
            trust = [ordered]@{
                sha256 = $null
                exact_bootstrap_user = $true
                mfa_required = $true
                verified = $false
            }
            boundary = [ordered]@{
                name = $script:BoundaryName123
                sha256 = $null
                created = $false
                verified = $false
            }
            role_policy = [ordered]@{
                name = $script:RolePolicyName123
                sha256 = $null
                applied = $false
                verified = $false
            }
        }
        assume_role = [ordered]@{
            attempted = $false
            duration_seconds = $script:AssumeRoleDurationSeconds123
            succeeded = $false
        }
        assumed_role_identity = [ordered]@{
            verified = $false
            redacted_identifier = 'NOT_EXECUTED'
        }
        baseline = [ordered]@{
            bootstrap_inline_policy_list_attempted = $false
            result = 'NOT_EXECUTED'
            policy_name_count = $null
            sorted_policy_names_sha256 = $null
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
            permissions_on_other_identities = 0
            iam_pass_role = $false
            attached_role_policies = 0
            technical_verdict = 'PENDING'
        }
        aws_calls = $calls
        mutations = [ordered]@{
            creation_attempts = 0
            creation_successes = 0
            compensation_attempts = 0
            compensation_successes = 0
            unexpected = 0
            bootstrap_user_changes = 0
            persistent_at_completion = 0
        }
        compensation = [ordered]@{
            required = $false
            attempted = $false
            succeeded = $null
            operations = @()
        }
        out_of_scope = [ordered]@{
            bootstrap_put_user_policy = 0
            bootstrap_delete_user_policy = 0
            iam_simulate_principal_policy = 0
            terraform_executions = 0
            provisioning_executions = 0
            product_leadership_test_003_executions = 0
            product_leadership_active = $false
            product_leadership_integrated = $false
        }
        credentials_cleared = $false
        failure_code = $null
        failure_metadata = $null
        result = 'IN_PROGRESS'
        redaction = [ordered]@{
            full_account_id_included = $false
            full_arns_included = $false
            credentials_tokens_or_mfa_codes_included = $false
            request_ids_included = $false
            raw_aws_output_persisted = $false
        }
        post_attempt_authority = 'NONE'
    }

    $secureMfa = $null
    $mfaPointer = [IntPtr]::Zero
    $mfaCode = $null
    $mfaSerial = $null
    $accountId = $null
    $documents = $null
    $boundaryArn = $null
    $roleArn = $null
    $creatorCredentials = $null
    $roleCredentials = $null
    $sessionDocument = $null
    $identityDocument = $null
    $roleSessionDocument = $null
    $boundaryCreated = $false
    $roleCreated = $false
    $rolePolicyCreated = $false
    $executionSucceeded = $false

    try {
        $head = (git -C $repositoryRoot rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0 -or $head -ne $ExpectedExecutionHead) {
            throw 'HEAD_MISMATCH'
        }
        $evidence.prechecks.head = 'PASS'

        $worktreeEntries = @(git -C $repositoryRoot status --porcelain=v1 --untracked-files=all)
        if ($LASTEXITCODE -ne 0 -or $worktreeEntries.Count -ne 0) {
            throw 'WORKTREE_NOT_CLEAN'
        }
        $evidence.prechecks.worktree = 'PASS'
        if ($synthetic.result -ne 'PASS') {
            throw 'LOCAL_VALIDATION_FAILED'
        }

        if ($null -eq (Get-Command aws -ErrorAction SilentlyContinue)) {
            throw 'AWS_CLI_NOT_AVAILABLE'
        }
        $evidence.prechecks.aws_cli = 'PASS'
        if ([Environment]::GetEnvironmentVariable('AWS_CLI_HISTORY', 'Process') -eq 'enabled') {
            throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
        }
        $profiles = @(& aws configure list-profiles 2>$null)
        if ($LASTEXITCODE -ne 0 -or (& aws configure get cli_history 2>$null) -eq 'enabled') {
            throw 'AWS_CLI_CONFIGURATION_INVALID'
        }
        $evidence.prechecks.cli_history_disabled = 'PASS'

        $presentCredentialNames = @(
            $script:CredentialEnvironmentNames123 | Where-Object {
                -not [string]::IsNullOrWhiteSpace(
                    [Environment]::GetEnvironmentVariable($_, 'Process')
                )
            }
        )
        if ($presentCredentialNames.Count -ne 0) {
            throw 'PREEXISTING_AWS_CREDENTIAL_ENVIRONMENT_DETECTED'
        }
        $evidence.prechecks.inherited_temporary_credentials_absent = 'PASS'

        foreach ($profile in $profiles) {
            $token = (& aws configure get aws_session_token --profile $profile 2>$null) -join ''
            $securityToken = (& aws configure get aws_security_token --profile $profile 2>$null) -join ''
            if (
                -not [string]::IsNullOrWhiteSpace($token) -or
                -not [string]::IsNullOrWhiteSpace($securityToken)
            ) {
                throw 'REUSABLE_PRIOR_TEMPORARY_CREDENTIAL_DETECTED'
            }
        }
        $evidence.prechecks.reusable_temporary_profiles_absent = 'PASS'
        if ($profiles -notcontains $script:BootstrapProfile123) {
            throw 'BOOTSTRAP_PROFILE_NOT_FOUND'
        }

        $mfaSerial = (& aws configure get mfa_serial --profile $script:BootstrapProfile123 2>$null) -join ''
        if ($mfaSerial -notmatch '^arn:aws:iam::(\d{12}):mfa/') {
            throw 'BOOTSTRAP_MFA_REFERENCE_INVALID'
        }
        $accountId = [string]$Matches[1]
        $documents = New-PL003122Documents -AccountId $accountId
        $checks = Test-PL003122Documents -Documents $documents
        if ($checks.Values -contains $false) {
            throw 'LOCAL_DOCUMENT_VALIDATION_FAILED'
        }
        $evidence.artifacts.trust.sha256 = Get-PL003122Sha256 -Text $documents.trust
        $evidence.artifacts.boundary.sha256 = Get-PL003122Sha256 -Text $documents.boundary
        $evidence.artifacts.role_policy.sha256 = Get-PL003122Sha256 -Text $documents.role_policy
        $boundaryArn = "arn:aws:iam::$accountId`:policy/$($script:BoundaryName123)"
        $roleArn = "arn:aws:iam::$accountId`:role/$($script:RoleName123)"

        [IO.Directory]::CreateDirectory($temporaryDocumentDirectory) | Out-Null
        [IO.File]::WriteAllText($trustPath, $documents.trust, [Text.UTF8Encoding]::new($false))
        [IO.File]::WriteAllText($boundaryPath, $documents.boundary, [Text.UTF8Encoding]::new($false))
        [IO.File]::WriteAllText($rolePolicyPath, $documents.role_policy, [Text.UTF8Encoding]::new($false))

        $secureMfa = Read-Host -Prompt 'MFA token code' -AsSecureString
        $mfaPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureMfa)
        $mfaCode = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($mfaPointer)
        if ($mfaCode -notmatch '^\d{6}$') {
            throw 'INVALID_MFA_CODE_FORMAT'
        }

        $calls.sts_get_session_token = 1
        $sessionCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'get-session-token',
            '--profile', $script:BootstrapProfile123,
            '--region', $script:ExpectedRegion,
            '--serial-number', $mfaSerial,
            '--token-code', $mfaCode,
            '--duration-seconds', '3600',
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $null
        if ($mfaPointer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($mfaPointer)
            $mfaPointer = [IntPtr]::Zero
        }
        $secureMfa = $null
        $mfaCode = $null
        if ($sessionCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $sessionCall -Service 'sts' -Operation 'GetSessionToken'
            throw 'MFA_SESSION_ESTABLISHMENT_FAILED'
        }
        $sessionDocument = $sessionCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $creatorCredentials = $sessionDocument.Credentials
        if (
            [string]::IsNullOrWhiteSpace([string]$creatorCredentials.AccessKeyId) -or
            [string]::IsNullOrWhiteSpace([string]$creatorCredentials.SecretAccessKey) -or
            [string]::IsNullOrWhiteSpace([string]$creatorCredentials.SessionToken)
        ) {
            throw 'TEMPORARY_CREATOR_CREDENTIAL_SHAPE_INVALID'
        }
        $evidence.creator_identity.mfa_session = 'PASS_EPHEMERAL_IN_MEMORY_ONLY'

        $calls.sts_get_caller_identity_creator = 1
        $creatorIdentityCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'get-caller-identity',
            '--region', $script:ExpectedRegion,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($creatorIdentityCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $creatorIdentityCall -Service 'sts' -Operation 'GetCallerIdentity'
            throw 'CREATOR_IDENTITY_RESOLUTION_FAILED'
        }
        $identityDocument = $creatorIdentityCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        if (
            [string]$identityDocument.Account -cne $accountId -or
            [string]$identityDocument.Arn -cne $documents.bootstrap_arn
        ) {
            throw 'CREATOR_PRINCIPAL_MISMATCH'
        }
        $evidence.creator_identity.verified = $true
        $evidence.creator_identity.redacted_identifier = 'IAM_USER:<REDACTED_ACCOUNT_ID>:pl003-bootstrap-operator'

        $calls.iam_get_policy_collision = 1
        $boundaryCollisionCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-policy',
            '--policy-arn', $boundaryArn,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        $boundaryCollisionCode = Get-PL003AwsErrorCode -StdErr $boundaryCollisionCall.RawStdErr
        if ($boundaryCollisionCall.ExitCode -eq 0) {
            throw 'BOUNDARY_COLLISION'
        }
        if ($boundaryCollisionCode -cne 'NoSuchEntity') {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $boundaryCollisionCall -Service 'iam' -Operation 'GetPolicy'
            throw 'BOUNDARY_COLLISION_PREFLIGHT_FAILED'
        }
        $evidence.collision_preflight.boundary_absent = $true

        $calls.iam_get_role_collision = 1
        $roleCollisionCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-role',
            '--role-name', $script:RoleName123,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        $roleCollisionCode = Get-PL003AwsErrorCode -StdErr $roleCollisionCall.RawStdErr
        if ($roleCollisionCall.ExitCode -eq 0) {
            throw 'ROLE_COLLISION'
        }
        if ($roleCollisionCode -cne 'NoSuchEntity') {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $roleCollisionCall -Service 'iam' -Operation 'GetRole'
            throw 'ROLE_COLLISION_PREFLIGHT_FAILED'
        }
        $evidence.collision_preflight.role_absent = $true
        $evidence.collision_preflight.result = 'PASS_BOTH_EXACT_NAMES_ABSENT'

        $calls.iam_create_policy = 1
        $evidence.mutations.creation_attempts++
        $createPolicyCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'create-policy',
            '--policy-name', $script:BoundaryName123,
            '--policy-document', ('file://' + $boundaryPath.Replace('\', '/')),
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($createPolicyCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $createPolicyCall -Service 'iam' -Operation 'CreatePolicy'
            throw 'CREATE_BOUNDARY_POLICY_FAILED'
        }
        $createPolicyDocument = $createPolicyCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        if ([string]$createPolicyDocument.Policy.Arn -cne $boundaryArn) {
            throw 'CREATED_BOUNDARY_ARN_MISMATCH'
        }
        $boundaryCreated = $true
        $evidence.mutations.creation_successes++
        $evidence.artifacts.boundary.created = $true

        $calls.iam_create_role = 1
        $evidence.mutations.creation_attempts++
        $createRoleCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'create-role',
            '--role-name', $script:RoleName123,
            '--assume-role-policy-document', ('file://' + $trustPath.Replace('\', '/')),
            '--permissions-boundary', $boundaryArn,
            '--max-session-duration', [string]$script:CreateRoleMaximumSessionSeconds123,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($createRoleCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $createRoleCall -Service 'iam' -Operation 'CreateRole'
            throw 'CREATE_ROLE_FAILED'
        }
        $createRoleDocument = $createRoleCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        if (
            [string]$createRoleDocument.Role.Arn -cne $roleArn -or
            [int]$createRoleDocument.Role.MaxSessionDuration -ne $script:CreateRoleMaximumSessionSeconds123
        ) {
            throw 'CREATED_ROLE_SHAPE_MISMATCH'
        }
        $roleCreated = $true
        $evidence.mutations.creation_successes++
        $evidence.artifacts.role.created = $true

        $calls.iam_put_role_policy = 1
        $evidence.mutations.creation_attempts++
        $putRolePolicyCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'put-role-policy',
            '--role-name', $script:RoleName123,
            '--policy-name', $script:RolePolicyName123,
            '--policy-document', ('file://' + $rolePolicyPath.Replace('\', '/')),
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($putRolePolicyCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $putRolePolicyCall -Service 'iam' -Operation 'PutRolePolicy'
            throw 'PUT_ROLE_POLICY_FAILED'
        }
        $rolePolicyCreated = $true
        $evidence.mutations.creation_successes++
        $evidence.artifacts.role_policy.applied = $true

        $calls.iam_get_policy_verification = 1
        $getPolicyCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-policy',
            '--policy-arn', $boundaryArn,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($getPolicyCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $getPolicyCall -Service 'iam' -Operation 'GetPolicy'
            throw 'VERIFY_BOUNDARY_METADATA_FAILED'
        }
        $getPolicyDocument = $getPolicyCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $policyVersionId = [string]$getPolicyDocument.Policy.DefaultVersionId
        if (
            [string]$getPolicyDocument.Policy.Arn -cne $boundaryArn -or
            [string]::IsNullOrWhiteSpace($policyVersionId)
        ) {
            throw 'VERIFY_BOUNDARY_METADATA_MISMATCH'
        }

        $calls.iam_get_policy_version = 1
        $getPolicyVersionCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-policy-version',
            '--policy-arn', $boundaryArn,
            '--version-id', $policyVersionId,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($getPolicyVersionCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $getPolicyVersionCall -Service 'iam' -Operation 'GetPolicyVersion'
            throw 'VERIFY_BOUNDARY_DOCUMENT_FAILED'
        }
        $effectiveBoundary = ($getPolicyVersionCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).PolicyVersion.Document
        if (-not (Test-PL003123PermissionDocument -Document $effectiveBoundary -ExpectedBootstrapArn $documents.bootstrap_arn)) {
            throw 'EFFECTIVE_BOUNDARY_DOCUMENT_MISMATCH'
        }
        $evidence.artifacts.boundary.verified = $true

        $calls.iam_get_role_verification = 1
        $getRoleCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-role',
            '--role-name', $script:RoleName123,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($getRoleCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $getRoleCall -Service 'iam' -Operation 'GetRole'
            throw 'VERIFY_ROLE_FAILED'
        }
        $effectiveRole = ($getRoleCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).Role
        if (
            [string]$effectiveRole.Arn -cne $roleArn -or
            [int]$effectiveRole.MaxSessionDuration -ne $script:CreateRoleMaximumSessionSeconds123 -or
            [string]$effectiveRole.PermissionsBoundary.PermissionsBoundaryArn -cne $boundaryArn -or
            -not (Test-PL003123TrustDocument `
                -Document $effectiveRole.AssumeRolePolicyDocument `
                -ExpectedBootstrapArn $documents.bootstrap_arn)
        ) {
            throw 'EFFECTIVE_ROLE_TRUST_BOUNDARY_OR_DURATION_MISMATCH'
        }
        $evidence.artifacts.role.verified = $true
        $evidence.artifacts.trust.verified = $true

        $calls.iam_get_role_policy = 1
        $getRolePolicyCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-role-policy',
            '--role-name', $script:RoleName123,
            '--policy-name', $script:RolePolicyName123,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($getRolePolicyCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $getRolePolicyCall -Service 'iam' -Operation 'GetRolePolicy'
            throw 'VERIFY_ROLE_POLICY_FAILED'
        }
        $effectiveRolePolicy = ($getRolePolicyCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).PolicyDocument
        if (-not (Test-PL003123PermissionDocument -Document $effectiveRolePolicy -ExpectedBootstrapArn $documents.bootstrap_arn)) {
            throw 'EFFECTIVE_ROLE_POLICY_DOCUMENT_MISMATCH'
        }
        $evidence.artifacts.role_policy.verified = $true
        $evidence.privilege_analysis.technical_verdict = 'PASS_EXACT_FOUR_ACTIONS_EXACT_BOOTSTRAP_USER_NO_WILDCARD_NO_PASSROLE'

        Start-Sleep -Seconds 10
        $calls.sts_assume_role = 1
        $evidence.assume_role.attempted = $true
        $assumeRoleCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'assume-role',
            '--role-arn', $roleArn,
            '--role-session-name', $script:RoleSessionName123,
            '--duration-seconds', [string]$script:AssumeRoleDurationSeconds123,
            '--region', $script:ExpectedRegion,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $creatorCredentials
        if ($assumeRoleCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $assumeRoleCall -Service 'sts' -Operation 'AssumeRole'
            throw 'ASSUME_ROLE_FAILED'
        }
        $roleSessionDocument = $assumeRoleCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $roleCredentials = $roleSessionDocument.Credentials
        if (
            [string]::IsNullOrWhiteSpace([string]$roleCredentials.AccessKeyId) -or
            [string]::IsNullOrWhiteSpace([string]$roleCredentials.SecretAccessKey) -or
            [string]::IsNullOrWhiteSpace([string]$roleCredentials.SessionToken)
        ) {
            throw 'TEMPORARY_ROLE_CREDENTIAL_SHAPE_INVALID'
        }
        $evidence.assume_role.succeeded = $true

        $calls.sts_get_caller_identity_role = 1
        $roleIdentityCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'get-caller-identity',
            '--region', $script:ExpectedRegion,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $roleCredentials
        if ($roleIdentityCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $roleIdentityCall -Service 'sts' -Operation 'GetCallerIdentity'
            throw 'ROLE_IDENTITY_RESOLUTION_FAILED'
        }
        $roleIdentityDocument = $roleIdentityCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $expectedRoleSessionArn = "arn:aws:sts::$accountId`:assumed-role/$($script:RoleName123)/$($script:RoleSessionName123)"
        if (
            [string]$roleIdentityDocument.Account -cne $accountId -or
            [string]$roleIdentityDocument.Arn -cne $expectedRoleSessionArn
        ) {
            throw 'ASSUMED_ROLE_IDENTITY_MISMATCH'
        }
        $evidence.assumed_role_identity.verified = $true
        $evidence.assumed_role_identity.redacted_identifier = 'ASSUMED_ROLE:<REDACTED_ACCOUNT_ID>:PL003BoundedSimulationSetupOperator/PL003Authorization123'

        $calls.iam_list_user_policies = 1
        $evidence.baseline.bootstrap_inline_policy_list_attempted = $true
        $listUserPoliciesCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'list-user-policies',
            '--user-name', $script:BootstrapUserName123,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $roleCredentials
        if ($listUserPoliciesCall.ExitCode -ne 0) {
            Set-PL003123FailureMetadata -Evidence $evidence -Call $listUserPoliciesCall -Service 'iam' -Operation 'ListUserPolicies'
            throw 'BOOTSTRAP_BASELINE_READ_FAILED'
        }
        $policyNames = @(
            ($listUserPoliciesCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).PolicyNames |
                ForEach-Object { [string]$_ } |
                Sort-Object
        )
        $evidence.baseline.result = 'PASS_READ_ONLY'
        $evidence.baseline.policy_name_count = $policyNames.Count
        $evidence.baseline.sorted_policy_names_sha256 = Get-PL003122Sha256 -Text ($policyNames -join "`n")

        $executionSucceeded = $true
        $evidence.status = 'COMPLETE'
        $evidence.result = 'PASS_BOUNDED_SETUP_ROLE_CREATED_AND_VERIFIED'
        $evidence.mutations.persistent_at_completion = 3
    } catch {
        $message = [string]$_.Exception.Message
        $evidence.failure_code = if ($message -match '^[A-Z0-9_]+$') {
            $message
        } else {
            'UNEXPECTED_EXECUTION_FAILURE'
        }
        $evidence.status = 'BLOCKED'
        $evidence.result = 'BLOCKED_FAIL_CLOSED'
    } finally {
        if ($mfaPointer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($mfaPointer)
            $mfaPointer = [IntPtr]::Zero
        }

        if (-not $executionSucceeded -and ($boundaryCreated -or $roleCreated -or $rolePolicyCreated)) {
            $evidence.compensation.required = $true
            $evidence.compensation.attempted = $true
            $compensationOperations = [System.Collections.Generic.List[object]]::new()
            $compensationSucceeded = $true

            if ($rolePolicyCreated) {
                $calls.iam_delete_role_policy_compensation++
                $evidence.mutations.compensation_attempts++
                $call = Invoke-PL003AwsCliCaptured -Arguments @(
                    'iam', 'delete-role-policy',
                    '--role-name', $script:RoleName123,
                    '--policy-name', $script:RolePolicyName123,
                    '--no-cli-pager',
                    '--output', 'json'
                ) -Credentials $creatorCredentials
                $ok = $call.ExitCode -eq 0
                if ($ok) {
                    $evidence.mutations.compensation_successes++
                    $rolePolicyCreated = $false
                } else {
                    $compensationSucceeded = $false
                }
                $compensationOperations.Add([ordered]@{ operation = 'DeleteRolePolicy'; succeeded = $ok })
            }
            if ($roleCreated) {
                $calls.iam_delete_role_compensation++
                $evidence.mutations.compensation_attempts++
                $call = Invoke-PL003AwsCliCaptured -Arguments @(
                    'iam', 'delete-role',
                    '--role-name', $script:RoleName123,
                    '--no-cli-pager',
                    '--output', 'json'
                ) -Credentials $creatorCredentials
                $ok = $call.ExitCode -eq 0
                if ($ok) {
                    $evidence.mutations.compensation_successes++
                    $roleCreated = $false
                } else {
                    $compensationSucceeded = $false
                }
                $compensationOperations.Add([ordered]@{ operation = 'DeleteRole'; succeeded = $ok })
            }
            if ($boundaryCreated) {
                $calls.iam_delete_policy_compensation++
                $evidence.mutations.compensation_attempts++
                $call = Invoke-PL003AwsCliCaptured -Arguments @(
                    'iam', 'delete-policy',
                    '--policy-arn', $boundaryArn,
                    '--no-cli-pager',
                    '--output', 'json'
                ) -Credentials $creatorCredentials
                $ok = $call.ExitCode -eq 0
                if ($ok) {
                    $evidence.mutations.compensation_successes++
                    $boundaryCreated = $false
                } else {
                    $compensationSucceeded = $false
                }
                $compensationOperations.Add([ordered]@{ operation = 'DeletePolicy'; succeeded = $ok })
            }
            $evidence.compensation.operations = @($compensationOperations)
            $evidence.compensation.succeeded = $compensationSucceeded
            if (-not $compensationSucceeded) {
                $evidence.status = 'ACTIVE_IAM_INCIDENT'
                $evidence.result = 'BLOCKED_PARTIAL_RESOURCE_CLEANUP_FAILED'
                $evidence.failure_code = 'PARTIAL_RESOURCE_CLEANUP_FAILED'
            } else {
                $evidence.mutations.persistent_at_completion = 0
            }
        }

        if (Test-Path -LiteralPath $temporaryDocumentDirectory) {
            foreach ($path in @($trustPath, $boundaryPath, $rolePolicyPath)) {
                if (Test-Path -LiteralPath $path) {
                    Remove-Item -LiteralPath $path -Force
                }
            }
            if (@(Get-ChildItem -LiteralPath $temporaryDocumentDirectory -Force).Count -eq 0) {
                Remove-Item -LiteralPath $temporaryDocumentDirectory -Force
            }
        }

        $secureMfa = $null
        $mfaCode = $null
        $mfaSerial = $null
        $sessionDocument = $null
        $identityDocument = $null
        $roleSessionDocument = $null
        $creatorCredentials = $null
        $roleCredentials = $null
        $accountId = $null
        $documents = $null
        $boundaryArn = $null
        $roleArn = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        $evidence.credentials_cleared = $true
        Write-PL003122Evidence -Evidence $evidence -Path $evidencePath
    }

    return [ordered]@{
        result = $evidence.result
        status = $evidence.status
        failure_code = $evidence.failure_code
        creator_identity = $evidence.creator_identity.redacted_identifier
        collision_preflight = $evidence.collision_preflight.result
        role_name = $evidence.artifacts.role.name
        trust_sha256 = $evidence.artifacts.trust.sha256
        boundary_name = $evidence.artifacts.boundary.name
        boundary_sha256 = $evidence.artifacts.boundary.sha256
        role_policy_name = $evidence.artifacts.role_policy.name
        role_policy_sha256 = $evidence.artifacts.role_policy.sha256
        assume_role = $evidence.assume_role
        role_identity = $evidence.assumed_role_identity.redacted_identifier
        baseline = $evidence.baseline
        aws_calls = $evidence.aws_calls
        mutations = $evidence.mutations
        compensation = $evidence.compensation
        evidence_path = $evidencePath.Substring($repositoryRoot.Length + 1).Replace('\', '/')
        secrets_printed = $false
    }
}

if ($MyInvocation.InvocationName -eq '.') {
    return
}

if ($SyntheticTest -or -not $OperationalRun) {
    $test = Test-PL003CreateBoundedSetupRoleCompatibility123
    $test | ConvertTo-Json -Depth 8
    if ($test.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003CreateBoundedSetupRoleCompatibility123 `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber
$outcome | ConvertTo-Json -Depth 10
if ($outcome.result -eq 'PASS_BOUNDED_SETUP_ROLE_CREATED_AND_VERIFIED') {
    exit 0
}
exit 1
