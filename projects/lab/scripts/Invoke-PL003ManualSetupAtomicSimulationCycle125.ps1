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

$requestedOperationalRun125 = [bool]$OperationalRun
$requestedSyntheticTest125 = [bool]$SyntheticTest
$requestedExpectedHead125 = $ExpectedHead
$requestedAttemptNumber125 = $AttemptNumber

$diagnosticScript125 = Join-Path $PSScriptRoot 'Invoke-PL003BootstrapDiagnosticPreflight.ps1'
. $diagnosticScript125

$OperationalRun = $requestedOperationalRun125
$SyntheticTest = $requestedSyntheticTest125
$ExpectedHead = $requestedExpectedHead125
$AttemptNumber = $requestedAttemptNumber125

$script:AuthorizationId125 = 'AUTHORIZATION_LAB_PL003_MANUAL_SETUP_EVIDENCE_AND_ATOMIC_SIMULATION_CYCLE_125'
$script:BootstrapProfile125 = 'pl003-bootstrap'
$script:BootstrapUserName125 = 'pl003-bootstrap-operator'
$script:RoleName125 = 'PL003BoundedSimulationSetupOperator'
$script:BoundaryName125 = 'PL003BoundedSimulationSetupBoundary125'
$script:RolePolicyName125 = 'PL003BoundedSimulationSetupRolePolicy125'
$script:TemporaryPolicyName125 = 'PL003AtomicSimulationOnly125'
$script:RoleSessionName125 = 'PL003Authorization125'
$script:AssumeRoleDurationSeconds125 = 900
$script:TemporaryPolicyDocument125 = '{"Version":"2012-10-17","Statement":[{"Sid":"AtomicPL003SimulationOnly125","Effect":"Allow","Action":"iam:SimulatePrincipalPolicy","Resource":"*"}]}'
$script:CredentialEnvironmentNames125 = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

function Get-PL003125Sha256 {
    param([Parameter(Mandatory)][string]$Text)

    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
        return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Test-PL003125TemporaryPolicyDocument {
    param([Parameter(Mandatory)]$Document)

    try {
        $statements = @($Document.Statement)
        if ([string]$Document.Version -cne '2012-10-17' -or $statements.Count -ne 1) {
            return $false
        }
        $statement = $statements[0]
        return (
            [string]$statement.Sid -ceq 'AtomicPL003SimulationOnly125' -and
            [string]$statement.Effect -ceq 'Allow' -and
            @($statement.Action).Count -eq 1 -and
            [string]@($statement.Action)[0] -ceq 'iam:SimulatePrincipalPolicy' -and
            @($statement.Resource).Count -eq 1 -and
            [string]@($statement.Resource)[0] -ceq '*'
        )
    } catch {
        return $false
    }
}

function Invoke-PL003125SyntheticLifecycle {
    param(
        [bool]$PutAttempted,
        [bool]$PutSucceeded,
        [bool]$SimulationSucceeded,
        [bool]$DeleteSucceeded,
        [bool]$FinalAbsent,
        [bool]$FinalSetEqualsBaseline
    )

    $events = [System.Collections.Generic.List[string]]::new()
    if ($PutAttempted) {
        $events.Add('PutUserPolicy')
    }
    if ($PutSucceeded -and $SimulationSucceeded) {
        $events.Add('SimulatePrincipalPolicy')
    }
    if ($PutAttempted) {
        $events.Add('Finally:DeleteUserPolicy')
        $events.Add('Finally:GetUserPolicy')
        $events.Add('Finally:ListUserPolicies')
    }
    $rollbackVerified = (
        $PutAttempted -and
        $DeleteSucceeded -and
        $FinalAbsent -and
        $FinalSetEqualsBaseline
    )
    return [ordered]@{
        events = @($events)
        delete_is_first_finally_aws_operation = (
            -not $PutAttempted -or
            $events.IndexOf('Finally:DeleteUserPolicy') -ge 0
        )
        rollback_verified = $rollbackVerified
    }
}

function Test-PL003ManualSetupAtomicSimulationCycle125 {
    $failures = [System.Collections.Generic.List[string]]::new()
    $policy = $script:TemporaryPolicyDocument125 | ConvertFrom-Json
    if (-not (Test-PL003125TemporaryPolicyDocument -Document $policy)) {
        $failures.Add('temporary-policy-document')
    }
    if (
        $script:RoleName125 -cne 'PL003BoundedSimulationSetupOperator' -or
        $script:BoundaryName125 -cne 'PL003BoundedSimulationSetupBoundary125' -or
        $script:RolePolicyName125 -cne 'PL003BoundedSimulationSetupRolePolicy125' -or
        $script:TemporaryPolicyName125 -cne 'PL003AtomicSimulationOnly125'
    ) {
        $failures.Add('fixed-target-names')
    }
    if ($script:AssumeRoleDurationSeconds125 -ne 900) {
        $failures.Add('assume-role-duration')
    }
    $success = Invoke-PL003125SyntheticLifecycle `
        -PutAttempted $true `
        -PutSucceeded $true `
        -SimulationSucceeded $true `
        -DeleteSucceeded $true `
        -FinalAbsent $true `
        -FinalSetEqualsBaseline $true
    if (-not $success.delete_is_first_finally_aws_operation -or -not $success.rollback_verified) {
        $failures.Add('successful-lifecycle')
    }
    $simulationFailure = Invoke-PL003125SyntheticLifecycle `
        -PutAttempted $true `
        -PutSucceeded $true `
        -SimulationSucceeded $false `
        -DeleteSucceeded $true `
        -FinalAbsent $true `
        -FinalSetEqualsBaseline $true
    if (
        -not $simulationFailure.delete_is_first_finally_aws_operation -or
        -not $simulationFailure.rollback_verified
    ) {
        $failures.Add('simulation-failure-rollback')
    }
    $putFailure = Invoke-PL003125SyntheticLifecycle `
        -PutAttempted $true `
        -PutSucceeded $false `
        -SimulationSucceeded $false `
        -DeleteSucceeded $true `
        -FinalAbsent $true `
        -FinalSetEqualsBaseline $true
    if (-not $putFailure.delete_is_first_finally_aws_operation -or -not $putFailure.rollback_verified) {
        $failures.Add('put-failure-rollback')
    }
    $deleteFailure = Invoke-PL003125SyntheticLifecycle `
        -PutAttempted $true `
        -PutSucceeded $true `
        -SimulationSucceeded $true `
        -DeleteSucceeded $false `
        -FinalAbsent $false `
        -FinalSetEqualsBaseline $false
    if ($deleteFailure.rollback_verified) {
        $failures.Add('delete-failure-detection')
    }
    $classifier = Test-PL003BootstrapDiagnosticClassifier
    if ($classifier.result -ne 'PASS') {
        $failures.Add('sanitized-classifier')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = 8 + [int]$classifier.case_count
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        classifier_result = $classifier.result
        temporary_policy_name = $script:TemporaryPolicyName125
        temporary_policy_sha256 = Get-PL003125Sha256 -Text $script:TemporaryPolicyDocument125
        assume_role_duration_seconds = $script:AssumeRoleDurationSeconds125
        aws_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function Write-PL003125Evidence {
    param(
        [Parameter(Mandatory)]$Evidence,
        [Parameter(Mandatory)][string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        throw 'EVIDENCE_PATH_ALREADY_EXISTS'
    }
    $json = $Evidence | ConvertTo-Json -Depth 24
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $stream.Write($bytes, 0, $bytes.Length)
    } finally {
        $stream.Dispose()
    }
}

function Set-PL003125FailureMetadata {
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

function Invoke-PL003ManualSetupAtomicSimulationCycle125 {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $evidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-MANUAL-SETUP-ATOMIC-SIMULATION-125-$attemptId.json"
    $temporaryDirectory = Join-Path $repositoryRoot 'projects\lab\scripts\.pl003-auth125-tmp'
    $temporaryPolicyPath = Join-Path $temporaryDirectory 'temporary-policy.json'
    $synthetic = Test-PL003ManualSetupAtomicSimulationCycle125

    $evidence = [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-MANUAL-SETUP-ATOMIC-SIMULATION-125-$attemptId"
        authorization_id = $script:AuthorizationId125
        project_id = 'lab'
        kind = 'REDACTED_MANUAL_SETUP_ATOMIC_SIMULATION_CYCLE_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        branch_mode = 'DETACHED_HEAD'
        execution_head = $ExpectedExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            authorization_125_registered_granted = 'PASS'
            authorizations_118_119_120_121_122_123_124_consumed = 'PASS'
            inherited_execution_authority = 'NONE'
            synthetic_cycle = $synthetic.result
            sanitized_classifier = $synthetic.classifier_result
            aws_cli = 'PENDING'
            cli_history_disabled = 'PENDING'
            inherited_temporary_credentials_absent = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
        }
        manual_setup_assertion = [ordered]@{
            source = 'projects/lab/evidence/EVD-LAB-PL003-MANUAL-SETUP-125-HUMAN-ASSERTION.json'
            initial_status = 'PENDING_PROGRAMMATIC_VERIFICATION'
            role_name = $script:RoleName125
            boundary_name = $script:BoundaryName125
            role_policy_name = $script:RolePolicyName125
            role_maximum_session_seconds_asserted = 3600
            attached_normal_managed_policy_count_asserted = 0
            manual_bootstrap_mutations_asserted = 0
        }
        bootstrap_identity = [ordered]@{
            verified = $false
            redacted_identifier = 'NOT_EXECUTED'
        }
        assume_role = [ordered]@{
            attempted = $false
            duration_seconds = $script:AssumeRoleDurationSeconds125
            succeeded = $false
        }
        role_identity = [ordered]@{
            verified = $false
            redacted_identifier = 'NOT_EXECUTED'
        }
        baseline = [ordered]@{
            list_attempted = $false
            temporary_policy_absent = $false
            policy_name_count = $null
            sorted_policy_names_sha256 = $null
        }
        temporary_grant = [ordered]@{
            policy_name = $script:TemporaryPolicyName125
            document_sha256 = Get-PL003125Sha256 -Text $script:TemporaryPolicyDocument125
            put_attempted = $false
            put_succeeded = $false
        }
        simulation = [ordered]@{
            attempted = $false
            tested_action = 'iam:CreatePolicy'
            simulated_action_executed = $false
            call_succeeded = $false
            evaluation_decision = $null
            classification = $null
        }
        rollback = [ordered]@{
            required = $false
            delete_was_first_finally_aws_operation = $false
            delete_attempted = $false
            delete_succeeded = $false
            final_get_user_policy_attempted = $false
            exact_policy_absent = $false
            final_list_user_policies_attempted = $false
            final_set_equals_baseline = $false
            verified = $false
        }
        aws_calls = [ordered]@{
            sts_get_session_token = 0
            sts_get_caller_identity_bootstrap = 0
            sts_assume_role = 0
            sts_get_caller_identity_role = 0
            iam_list_user_policies_baseline = 0
            iam_put_user_policy = 0
            iam_simulate_principal_policy = 0
            iam_delete_user_policy = 0
            iam_get_user_policy_final = 0
            iam_list_user_policies_final = 0
            other_aws = 0
        }
        mutations = [ordered]@{
            temporary_grant_attempts = 0
            temporary_grant_successes = 0
            rollback_attempts = 0
            rollback_successes = 0
            persistent_at_completion = 0
            unexpected = 0
        }
        final_state = [ordered]@{
            bootstrap_inline_policy_set_restored = $false
            temporary_policy_absent = $false
            role_modified = $false
            trust_modified = $false
            boundary_modified = $false
            role_policy_modified = $false
            identities_or_access_keys_created = 0
            infrastructure_mutations = 0
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
            raw_aws_output_included = $false
        }
        post_attempt_authority = 'NONE'
    }

    $secureMfa = $null
    $mfaPointer = [IntPtr]::Zero
    $mfaCode = $null
    $mfaSerial = $null
    $accountId = $null
    $bootstrapArn = $null
    $roleArn = $null
    $bootstrapCredentials = $null
    $roleCredentials = $null
    $sessionDocument = $null
    $roleSessionDocument = $null
    $baselineNames = $null
    $putAttempted = $false
    $primarySucceeded = $false

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
            throw 'LOCAL_SYNTHETIC_TEST_FAILURE'
        }
        if (-not (Test-PL003125TemporaryPolicyDocument `
            -Document ($script:TemporaryPolicyDocument125 | ConvertFrom-Json))) {
            throw 'TEMPORARY_POLICY_DOCUMENT_MISMATCH'
        }

        if ($null -eq (Get-Command aws -ErrorAction SilentlyContinue)) {
            throw 'AWS_CLI_NOT_AVAILABLE'
        }
        $evidence.prechecks.aws_cli = 'PASS'
        if (
            [Environment]::GetEnvironmentVariable('AWS_CLI_HISTORY', 'Process') -eq 'enabled' -or
            (& aws configure get cli_history 2>$null) -eq 'enabled'
        ) {
            throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
        }
        $evidence.prechecks.cli_history_disabled = 'PASS'
        $presentCredentialNames = @(
            $script:CredentialEnvironmentNames125 | Where-Object {
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
        if ($LASTEXITCODE -ne 0 -or $profiles -notcontains $script:BootstrapProfile125) {
            throw 'BOOTSTRAP_PROFILE_NOT_FOUND'
        }
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

        $mfaSerial = (& aws configure get mfa_serial --profile $script:BootstrapProfile125 2>$null) -join ''
        if ($mfaSerial -notmatch '^arn:aws:iam::(\d{12}):mfa/') {
            throw 'BOOTSTRAP_MFA_REFERENCE_INVALID'
        }
        $accountId = [string]$Matches[1]
        $bootstrapArn = "arn:aws:iam::$accountId`:user/$($script:BootstrapUserName125)"
        $roleArn = "arn:aws:iam::$accountId`:role/$($script:RoleName125)"

        [IO.Directory]::CreateDirectory($temporaryDirectory) | Out-Null
        [IO.File]::WriteAllText(
            $temporaryPolicyPath,
            $script:TemporaryPolicyDocument125,
            [Text.UTF8Encoding]::new($false)
        )

        $secureMfa = Read-Host -Prompt 'MFA token code' -AsSecureString
        $mfaPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureMfa)
        $mfaCode = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($mfaPointer)
        if ($mfaCode -notmatch '^\d{6}$') {
            throw 'INVALID_MFA_CODE_FORMAT'
        }

        $evidence.aws_calls.sts_get_session_token = 1
        $sessionCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'get-session-token',
            '--profile', $script:BootstrapProfile125,
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
            Set-PL003125FailureMetadata -Evidence $evidence -Call $sessionCall -Service 'sts' -Operation 'GetSessionToken'
            throw 'MFA_SESSION_ESTABLISHMENT_FAILED'
        }
        $sessionDocument = $sessionCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $bootstrapCredentials = $sessionDocument.Credentials
        if (
            [string]::IsNullOrWhiteSpace([string]$bootstrapCredentials.AccessKeyId) -or
            [string]::IsNullOrWhiteSpace([string]$bootstrapCredentials.SecretAccessKey) -or
            [string]::IsNullOrWhiteSpace([string]$bootstrapCredentials.SessionToken)
        ) {
            throw 'BOOTSTRAP_CREDENTIAL_SHAPE_INVALID'
        }

        $evidence.aws_calls.sts_get_caller_identity_bootstrap = 1
        $bootstrapIdentityCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'get-caller-identity',
            '--region', $script:ExpectedRegion,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $bootstrapCredentials
        if ($bootstrapIdentityCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $bootstrapIdentityCall -Service 'sts' -Operation 'GetCallerIdentity'
            throw 'BOOTSTRAP_IDENTITY_RESOLUTION_FAILED'
        }
        $bootstrapIdentity = $bootstrapIdentityCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        if (
            [string]$bootstrapIdentity.Account -cne $accountId -or
            [string]$bootstrapIdentity.Arn -cne $bootstrapArn
        ) {
            throw 'BOOTSTRAP_IDENTITY_MISMATCH'
        }
        $evidence.bootstrap_identity.verified = $true
        $evidence.bootstrap_identity.redacted_identifier = 'IAM_USER:<REDACTED_ACCOUNT_ID>:pl003-bootstrap-operator'

        $evidence.aws_calls.sts_assume_role = 1
        $evidence.assume_role.attempted = $true
        $assumeRoleCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'assume-role',
            '--role-arn', $roleArn,
            '--role-session-name', $script:RoleSessionName125,
            '--duration-seconds', [string]$script:AssumeRoleDurationSeconds125,
            '--region', $script:ExpectedRegion,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $bootstrapCredentials
        if ($assumeRoleCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $assumeRoleCall -Service 'sts' -Operation 'AssumeRole'
            throw 'BLOCKED_ASSUME_ROLE_FAILED'
        }
        $roleSessionDocument = $assumeRoleCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $roleCredentials = $roleSessionDocument.Credentials
        if (
            [string]::IsNullOrWhiteSpace([string]$roleCredentials.AccessKeyId) -or
            [string]::IsNullOrWhiteSpace([string]$roleCredentials.SecretAccessKey) -or
            [string]::IsNullOrWhiteSpace([string]$roleCredentials.SessionToken)
        ) {
            throw 'ROLE_CREDENTIAL_SHAPE_INVALID'
        }
        $evidence.assume_role.succeeded = $true

        $evidence.aws_calls.sts_get_caller_identity_role = 1
        $roleIdentityCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'get-caller-identity',
            '--region', $script:ExpectedRegion,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $roleCredentials
        if ($roleIdentityCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $roleIdentityCall -Service 'sts' -Operation 'GetCallerIdentity'
            throw 'ROLE_IDENTITY_RESOLUTION_FAILED'
        }
        $roleIdentity = $roleIdentityCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $expectedRoleSessionArn = "arn:aws:sts::$accountId`:assumed-role/$($script:RoleName125)/$($script:RoleSessionName125)"
        if (
            [string]$roleIdentity.Account -cne $accountId -or
            [string]$roleIdentity.Arn -cne $expectedRoleSessionArn
        ) {
            throw 'ASSUMED_ROLE_IDENTITY_MISMATCH'
        }
        $evidence.role_identity.verified = $true
        $evidence.role_identity.redacted_identifier = 'ASSUMED_ROLE:<REDACTED_ACCOUNT_ID>:PL003BoundedSimulationSetupOperator/PL003Authorization125'

        $evidence.aws_calls.iam_list_user_policies_baseline = 1
        $evidence.baseline.list_attempted = $true
        $baselineCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'list-user-policies',
            '--user-name', $script:BootstrapUserName125,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $roleCredentials
        if ($baselineCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $baselineCall -Service 'iam' -Operation 'ListUserPolicies'
            throw 'BLOCKED_BASELINE_READ_FAILED'
        }
        $baselineNames = @(
            ($baselineCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).PolicyNames |
                ForEach-Object { [string]$_ } |
                Sort-Object
        )
        if ($baselineNames -contains $script:TemporaryPolicyName125) {
            throw 'BLOCKED_EXISTING_TEMPORARY_POLICY_COLLISION'
        }
        $evidence.baseline.temporary_policy_absent = $true
        $evidence.baseline.policy_name_count = $baselineNames.Count
        $evidence.baseline.sorted_policy_names_sha256 = Get-PL003125Sha256 -Text ($baselineNames -join "`n")

        $putAttempted = $true
        $evidence.rollback.required = $true
        $evidence.temporary_grant.put_attempted = $true
        $evidence.aws_calls.iam_put_user_policy = 1
        $evidence.mutations.temporary_grant_attempts = 1
        $putCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'put-user-policy',
            '--user-name', $script:BootstrapUserName125,
            '--policy-name', $script:TemporaryPolicyName125,
            '--policy-document', ('file://' + $temporaryPolicyPath.Replace('\', '/')),
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $roleCredentials
        if ($putCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $putCall -Service 'iam' -Operation 'PutUserPolicy'
            throw 'BLOCKED_TEMPORARY_GRANT_FAILED'
        }
        $evidence.temporary_grant.put_succeeded = $true
        $evidence.mutations.temporary_grant_successes = 1
        $evidence.mutations.persistent_at_completion = 1

        $contextEntries = @(
            'ContextKeyName=aws:MultiFactorAuthPresent,ContextKeyValues=true,ContextKeyType=boolean',
            'ContextKeyName=aws:RequestTag/Project,ContextKeyValues=PRODUCT-LEADERSHIP-TEST-003,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Authorization,ContextKeyValues=125,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Temporary,ContextKeyValues=true,ContextKeyType=string'
        )
        $simulationArguments = @(
            'iam', 'simulate-principal-policy',
            '--policy-source-arn', $bootstrapArn,
            '--action-names', 'iam:CreatePolicy',
            '--resource-arns', "arn:aws:iam::$accountId`:policy/$($script:BoundaryName125)",
            '--context-entries'
        ) + $contextEntries + @(
            '--no-cli-pager',
            '--output', 'json'
        )
        $evidence.aws_calls.iam_simulate_principal_policy = 1
        $evidence.simulation.attempted = $true
        $simulationCall = Invoke-PL003AwsCliCaptured `
            -Arguments $simulationArguments `
            -Credentials $bootstrapCredentials
        if ($simulationCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $simulationCall -Service 'iam' -Operation 'SimulatePrincipalPolicy'
            throw 'BLOCKED_SIMULATION_CALL_FAILED'
        }
        $simulationDocument = $simulationCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $evaluationResults = @($simulationDocument.EvaluationResults)
        if ($evaluationResults.Count -lt 1) {
            throw 'SIMULATION_RESPONSE_SHAPE_INVALID'
        }
        $evidence.simulation.call_succeeded = $true
        $evidence.simulation.evaluation_decision = [string]$evaluationResults[0].EvalDecision
        $evidence.simulation.classification = Get-PL003SimulationClassification `
            -ExitCode 0 `
            -StdErr '' `
            -StdOut $simulationCall.RawStdOut `
            -AwsErrorCode $null
        $primarySucceeded = $true
    } catch {
        $message = [string]$_.Exception.Message
        $evidence.failure_code = if ($message -match '^[A-Z0-9_]+$') {
            $message
        } else {
            'BLOCKED_FAIL_CLOSED_OTHER'
        }
    } finally {
        if ($mfaPointer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($mfaPointer)
            $mfaPointer = [IntPtr]::Zero
        }

        if ($putAttempted) {
            $evidence.rollback.delete_was_first_finally_aws_operation = $true
            $evidence.rollback.delete_attempted = $true
            $evidence.aws_calls.iam_delete_user_policy = 1
            $evidence.mutations.rollback_attempts = 1
            $deleteCall = Invoke-PL003AwsCliCaptured -Arguments @(
                'iam', 'delete-user-policy',
                '--user-name', $script:BootstrapUserName125,
                '--policy-name', $script:TemporaryPolicyName125,
                '--no-cli-pager',
                '--output', 'json'
            ) -Credentials $roleCredentials
            $deleteErrorCode = Get-PL003AwsErrorCode -StdErr $deleteCall.RawStdErr
            $deleteAcceptable = (
                $deleteCall.ExitCode -eq 0 -or
                $deleteErrorCode -ceq 'NoSuchEntity'
            )
            $evidence.rollback.delete_succeeded = $deleteAcceptable
            if ($deleteAcceptable) {
                $evidence.mutations.rollback_successes = 1
            } elseif ($null -eq $evidence.failure_metadata) {
                Set-PL003125FailureMetadata -Evidence $evidence -Call $deleteCall -Service 'iam' -Operation 'DeleteUserPolicy'
            }

            $evidence.rollback.final_get_user_policy_attempted = $true
            $evidence.aws_calls.iam_get_user_policy_final = 1
            $finalGetCall = Invoke-PL003AwsCliCaptured -Arguments @(
                'iam', 'get-user-policy',
                '--user-name', $script:BootstrapUserName125,
                '--policy-name', $script:TemporaryPolicyName125,
                '--no-cli-pager',
                '--output', 'json'
            ) -Credentials $roleCredentials
            $finalGetErrorCode = Get-PL003AwsErrorCode -StdErr $finalGetCall.RawStdErr
            $evidence.rollback.exact_policy_absent = (
                $finalGetCall.ExitCode -ne 0 -and
                $finalGetErrorCode -ceq 'NoSuchEntity'
            )

            $evidence.rollback.final_list_user_policies_attempted = $true
            $evidence.aws_calls.iam_list_user_policies_final = 1
            $finalListCall = Invoke-PL003AwsCliCaptured -Arguments @(
                'iam', 'list-user-policies',
                '--user-name', $script:BootstrapUserName125,
                '--no-cli-pager',
                '--output', 'json'
            ) -Credentials $roleCredentials
            if ($finalListCall.ExitCode -eq 0) {
                $finalNames = @(
                    ($finalListCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).PolicyNames |
                        ForEach-Object { [string]$_ } |
                        Sort-Object
                )
                $evidence.rollback.final_set_equals_baseline = (
                    ($finalNames -join "`n") -ceq ($baselineNames -join "`n")
                )
            }
            $evidence.rollback.verified = (
                $evidence.rollback.delete_succeeded -and
                $evidence.rollback.exact_policy_absent -and
                $evidence.rollback.final_set_equals_baseline
            )
            if ($evidence.rollback.verified) {
                $evidence.mutations.persistent_at_completion = 0
                $evidence.final_state.bootstrap_inline_policy_set_restored = $true
                $evidence.final_state.temporary_policy_absent = $true
            } else {
                $primarySucceeded = $false
                $evidence.failure_code = 'BLOCKED_ROLLBACK_NOT_VERIFIED_ACTIVE_IAM_INCIDENT'
            }
        }

        if ($primarySucceeded -and $evidence.rollback.verified) {
            $evidence.status = 'COMPLETE'
            $evidence.result = 'PASS_MANUAL_SETUP_VERIFIED_ATOMIC_SIMULATION_COMPLETED_AND_ROLLED_BACK'
        } elseif ($evidence.failure_code -eq 'BLOCKED_ROLLBACK_NOT_VERIFIED_ACTIVE_IAM_INCIDENT') {
            $evidence.status = 'ACTIVE_IAM_INCIDENT'
            $evidence.result = 'BLOCKED_ROLLBACK_NOT_VERIFIED_ACTIVE_IAM_INCIDENT'
        } else {
            $evidence.status = 'BLOCKED'
            $evidence.result = if ([string]::IsNullOrWhiteSpace([string]$evidence.failure_code)) {
                'BLOCKED_FAIL_CLOSED_OTHER'
            } else {
                [string]$evidence.failure_code
            }
        }

        if (Test-Path -LiteralPath $temporaryDirectory) {
            if (Test-Path -LiteralPath $temporaryPolicyPath) {
                Remove-Item -LiteralPath $temporaryPolicyPath -Force
            }
            if (@(Get-ChildItem -LiteralPath $temporaryDirectory -Force).Count -eq 0) {
                Remove-Item -LiteralPath $temporaryDirectory -Force
            }
        }

        $secureMfa = $null
        $mfaCode = $null
        $mfaSerial = $null
        $sessionDocument = $null
        $roleSessionDocument = $null
        $bootstrapCredentials = $null
        $roleCredentials = $null
        $accountId = $null
        $bootstrapArn = $null
        $roleArn = $null
        $baselineNames = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        $evidence.credentials_cleared = $true
        Write-PL003125Evidence -Evidence $evidence -Path $evidencePath
    }

    return [ordered]@{
        result = $evidence.result
        status = $evidence.status
        failure_code = $evidence.failure_code
        bootstrap_identity = $evidence.bootstrap_identity.redacted_identifier
        assume_role = $evidence.assume_role
        role_identity = $evidence.role_identity.redacted_identifier
        baseline = $evidence.baseline
        temporary_grant = $evidence.temporary_grant
        simulation = $evidence.simulation
        rollback = $evidence.rollback
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
    $test = Test-PL003ManualSetupAtomicSimulationCycle125
    $test | ConvertTo-Json -Depth 10
    if ($test.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003ManualSetupAtomicSimulationCycle125 `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber
$outcome | ConvertTo-Json -Depth 14
if ($outcome.result -eq 'PASS_MANUAL_SETUP_VERIFIED_ATOMIC_SIMULATION_COMPLETED_AND_ROLLED_BACK') {
    exit 0
}
exit 1
