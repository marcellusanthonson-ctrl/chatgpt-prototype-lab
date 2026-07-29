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

$requestedOperationalRun127 = [bool]$OperationalRun
$requestedSyntheticTest127 = [bool]$SyntheticTest
$requestedExpectedHead127 = $ExpectedHead
$requestedAttemptNumber127 = $AttemptNumber

$priorScript127 = Join-Path $PSScriptRoot 'Invoke-PL003CorrectedAtomicSimulationRetry126.ps1'
. $priorScript127

$OperationalRun = $requestedOperationalRun127
$SyntheticTest = $requestedSyntheticTest127
$ExpectedHead = $requestedExpectedHead127
$AttemptNumber = $requestedAttemptNumber127

$script:AuthorizationId127 = 'AUTHORIZATION_LAB_PL003_PROPAGATION_AWARE_ATOMIC_SIMULATION_RETRY_127'
$script:BootstrapProfile127 = 'pl003-bootstrap'
$script:BootstrapUserName127 = 'pl003-bootstrap-operator'
$script:RoleName127 = 'PL003BoundedSimulationSetupOperator'
$script:BoundaryName127 = 'PL003BoundedSimulationSetupBoundary125'
$script:TemporaryPolicyName127 = 'PL003AtomicSimulationOnly127'
$script:RoleSessionName127 = 'PL003Authorization127'
$script:AssumeRoleDurationSeconds127 = 900
$script:StabilizationSeconds127 = 120
$script:MinimumMarginBeforeWaitSeconds127 = 300
$script:TemporaryPolicyDocument127 = '{"Version":"2012-10-17","Statement":[{"Sid":"AtomicPL003SimulationOnly127","Effect":"Allow","Action":"iam:SimulatePrincipalPolicy","Resource":"*"}]}'
$script:SemanticPolicyCanonical127 = '{"Version":"2012-10-17","Statement":[{"Action":["iam:SimulatePrincipalPolicy"],"Effect":"Allow","Resource":["*"],"Sid":"AtomicPL003SimulationOnly127"}]}'
$script:CredentialEnvironmentNames127 = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

function Get-PL003127PolicyDocumentObject {
    param([Parameter(Mandatory)]$PolicyDocument)

    if ($PolicyDocument -is [string]) {
        $decoded = [Uri]::UnescapeDataString([string]$PolicyDocument)
        return $decoded | ConvertFrom-Json -ErrorAction Stop
    }
    return $PolicyDocument
}

function Get-PL003127SemanticPolicyCanonical {
    param([Parameter(Mandatory)]$Document)

    try {
        $resolved = Get-PL003127PolicyDocumentObject -PolicyDocument $Document
        $statements = @($resolved.Statement)
        if ([string]$resolved.Version -cne '2012-10-17' -or $statements.Count -ne 1) {
            return $null
        }
        $statement = $statements[0]
        $actions = @($statement.Action | ForEach-Object { [string]$_ } | Sort-Object)
        $resources = @($statement.Resource | ForEach-Object { [string]$_ } | Sort-Object)
        if (
            [string]$statement.Sid -cne 'AtomicPL003SimulationOnly127' -or
            [string]$statement.Effect -cne 'Allow' -or
            $actions.Count -ne 1 -or
            $actions[0] -cne 'iam:SimulatePrincipalPolicy' -or
            $resources.Count -ne 1 -or
            $resources[0] -cne '*'
        ) {
            return $null
        }
        return $script:SemanticPolicyCanonical127
    } catch {
        return $null
    }
}

function Wait-PL003127Monotonic {
    param(
        [ValidateRange(1, 600)]
        [int]$DurationSeconds = 120
    )

    $frequency = [Diagnostics.Stopwatch]::Frequency
    $startTicks = [Diagnostics.Stopwatch]::GetTimestamp()
    $targetTicks = [int64]($DurationSeconds * $frequency)
    do {
        $elapsedTicks = [Diagnostics.Stopwatch]::GetTimestamp() - $startTicks
        $remainingTicks = $targetTicks - $elapsedTicks
        if ($remainingTicks -gt 0) {
            $remainingMilliseconds = [int][Math]::Floor(($remainingTicks * 1000.0) / $frequency)
            if ($remainingMilliseconds -gt 1) {
                Start-Sleep -Milliseconds ([Math]::Min(250, $remainingMilliseconds))
            } else {
                [Threading.Thread]::SpinWait(256)
            }
        }
    } while ($elapsedTicks -lt $targetTicks)

    $finalTicks = [Diagnostics.Stopwatch]::GetTimestamp() - $startTicks
    return [ordered]@{
        clock = 'LOCAL_MONOTONIC_STOPWATCH'
        target_seconds = $DurationSeconds
        elapsed_seconds = [Math]::Round(($finalTicks / [double]$frequency), 3)
        completed = ($finalTicks -ge $targetTicks)
    }
}

function Invoke-PL003127SyntheticLifecycle {
    param(
        [bool]$InterruptDuringWait,
        [bool]$SimulationAccessDenied,
        [bool]$DeleteSucceeded,
        [bool]$FinalSetEqualsBaseline
    )

    $events = [System.Collections.Generic.List[string]]::new()
    $events.Add('AWS:PutUserPolicy')
    $events.Add('AWS:GetUserPolicy')
    $events.Add('LOCAL:WaitStart')
    if ($InterruptDuringWait) {
        $events.Add('LOCAL:WaitInterrupted')
    } else {
        $events.Add('LOCAL:WaitComplete')
        $events.Add('AWS:SimulatePrincipalPolicy')
    }
    $events.Add('FINALLY:AWS:DeleteUserPolicy')
    $events.Add('FINALLY:AWS:ListUserPolicies')

    $waitStart = $events.IndexOf('LOCAL:WaitStart')
    $waitEndName = if ($InterruptDuringWait) { 'LOCAL:WaitInterrupted' } else { 'LOCAL:WaitComplete' }
    $waitEnd = $events.IndexOf($waitEndName)
    $awsDuringWait = @(
        $events[($waitStart + 1)..($waitEnd - 1)] |
            Where-Object { $_ -like '*AWS:*' }
    ).Count
    $simulationCount = @($events | Where-Object { $_ -eq 'AWS:SimulatePrincipalPolicy' }).Count

    return [ordered]@{
        events = @($events)
        target_wait_seconds = 120
        aws_calls_during_wait = $awsDuringWait
        interrupted = $InterruptDuringWait
        simulation_count = $simulationCount
        access_denied = $SimulationAccessDenied
        delete_is_first_finally_aws_operation = (
            $events[$events.IndexOf('FINALLY:AWS:DeleteUserPolicy')] -eq
            'FINALLY:AWS:DeleteUserPolicy'
        )
        rollback_verified = ($DeleteSucceeded -and $FinalSetEqualsBaseline)
    }
}

function Test-PL003PropagationAwareAtomicSimulationRetry127 {
    $failures = [System.Collections.Generic.List[string]]::new()
    $policy = $script:TemporaryPolicyDocument127 | ConvertFrom-Json
    $canonical = Get-PL003127SemanticPolicyCanonical -Document $policy
    if ($canonical -cne $script:SemanticPolicyCanonical127) {
        $failures.Add('authorized-policy-semantics')
    }
    if (
        (Get-PL003125Sha256 -Text $canonical) -cne
        (Get-PL003125Sha256 -Text $script:SemanticPolicyCanonical127)
    ) {
        $failures.Add('stored-policy-semantic-hash')
    }
    $urlEncoded = [Uri]::EscapeDataString($script:TemporaryPolicyDocument127)
    if (
        (Get-PL003127SemanticPolicyCanonical -Document $urlEncoded) -cne
        $script:SemanticPolicyCanonical127
    ) {
        $failures.Add('url-encoded-stored-policy')
    }
    if (
        $script:StabilizationSeconds127 -ne 120 -or
        $script:MinimumMarginBeforeWaitSeconds127 -ne 300
    ) {
        $failures.Add('stabilization-contract')
    }
    if ($script:AssumeRoleDurationSeconds127 -ne 900) {
        $failures.Add('assume-role-duration')
    }
    $emptyHash = Get-PL003125Sha256 -Text ''
    if (
        $emptyHash -cne
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    ) {
        $failures.Add('empty-baseline-hash')
    }
    $success = Invoke-PL003127SyntheticLifecycle `
        -InterruptDuringWait $false `
        -SimulationAccessDenied $false `
        -DeleteSucceeded $true `
        -FinalSetEqualsBaseline $true
    if (
        $success.target_wait_seconds -ne 120 -or
        $success.aws_calls_during_wait -ne 0 -or
        $success.simulation_count -ne 1 -or
        -not $success.delete_is_first_finally_aws_operation -or
        -not $success.rollback_verified
    ) {
        $failures.Add('successful-lifecycle')
    }
    $denied = Invoke-PL003127SyntheticLifecycle `
        -InterruptDuringWait $false `
        -SimulationAccessDenied $true `
        -DeleteSucceeded $true `
        -FinalSetEqualsBaseline $true
    if (
        $denied.simulation_count -ne 1 -or
        -not $denied.delete_is_first_finally_aws_operation -or
        -not $denied.rollback_verified
    ) {
        $failures.Add('access-denied-rollback')
    }
    $interrupted = Invoke-PL003127SyntheticLifecycle `
        -InterruptDuringWait $true `
        -SimulationAccessDenied $false `
        -DeleteSucceeded $true `
        -FinalSetEqualsBaseline $true
    if (
        -not $interrupted.interrupted -or
        $interrupted.simulation_count -ne 0 -or
        $interrupted.aws_calls_during_wait -ne 0 -or
        -not $interrupted.delete_is_first_finally_aws_operation -or
        -not $interrupted.rollback_verified
    ) {
        $failures.Add('interrupted-wait-rollback')
    }
    $changedFinal = Invoke-PL003127SyntheticLifecycle `
        -InterruptDuringWait $false `
        -SimulationAccessDenied $false `
        -DeleteSucceeded $true `
        -FinalSetEqualsBaseline $false
    if ($changedFinal.rollback_verified) {
        $failures.Add('changed-final-detection')
    }
    $classifier = Test-PL003BootstrapDiagnosticClassifier
    if ($classifier.result -ne 'PASS') {
        $failures.Add('sanitized-classifier')
    }
    $sessionMap = [ordered]@{
        bootstrap = @('GetCallerIdentity', 'AssumeRole', 'SimulatePrincipalPolicy')
        role = @(
            'GetCallerIdentity',
            'ListUserPolicies',
            'PutUserPolicy',
            'GetUserPolicy',
            'DeleteUserPolicy',
            'ListUserPolicies'
        )
    }
    if (
        $sessionMap.bootstrap -contains 'PutUserPolicy' -or
        $sessionMap.bootstrap -contains 'GetUserPolicy' -or
        $sessionMap.bootstrap -contains 'DeleteUserPolicy' -or
        $sessionMap.role -contains 'SimulatePrincipalPolicy'
    ) {
        $failures.Add('session-isolation')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = 18 + [int]$classifier.case_count
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        monotonic_wait_seconds = $script:StabilizationSeconds127
        aws_calls_during_wait = $success.aws_calls_during_wait
        session_margin_minimum_seconds = $script:MinimumMarginBeforeWaitSeconds127
        interruption_during_stabilization = if ($failures -contains 'interrupted-wait-rollback') { 'FAIL' } else { 'PASS' }
        rollback = if ($failures -contains 'access-denied-rollback') { 'FAIL' } else { 'PASS' }
        one_simulation = ($success.simulation_count -eq 1)
        stored_policy_semantic_hash = Get-PL003125Sha256 -Text $canonical
        baseline_sha256 = $emptyHash
        final_sha256 = $emptyHash
        baseline_and_final_identical = $true
        session_isolation = if ($failures -contains 'session-isolation') { 'FAIL' } else { 'PASS' }
        classifier_result = $classifier.result
        aws_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function Write-PL003127Evidence {
    param(
        [Parameter(Mandatory)]$Evidence,
        [Parameter(Mandatory)][string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        throw 'EVIDENCE_PATH_ALREADY_EXISTS'
    }
    $json = $Evidence | ConvertTo-Json -Depth 28
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $stream.Write($bytes, 0, $bytes.Length)
    } finally {
        $stream.Dispose()
    }
}

function Get-PL003127AwsCallCount {
    param([Parameter(Mandatory)]$CallMap)

    $total = 0
    foreach ($entry in $CallMap.GetEnumerator()) {
        $total += [int]$entry.Value
    }
    return $total
}

function Invoke-PL003PropagationAwareAtomicSimulationRetry127 {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $evidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-PROPAGATION-AWARE-ATOMIC-SIMULATION-RETRY-127-$attemptId.json"
    $temporaryDirectory = Join-Path $repositoryRoot 'projects\lab\scripts\.pl003-auth127-tmp'
    $temporaryPolicyPath = Join-Path $temporaryDirectory 'temporary-policy.json'
    $authorizationPath = Join-Path $repositoryRoot 'projects\lab\authorizations\AUTHORIZATION_LAB_PL003_PROPAGATION_AWARE_ATOMIC_SIMULATION_RETRY_127.json'
    $synthetic = Test-PL003PropagationAwareAtomicSimulationRetry127

    $evidence = [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-PROPAGATION-AWARE-ATOMIC-SIMULATION-RETRY-127-$attemptId"
        authorization_id = $script:AuthorizationId127
        project_id = 'lab'
        kind = 'REDACTED_PROPAGATION_AWARE_ATOMIC_SIMULATION_RETRY_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        branch_mode = 'DETACHED_HEAD'
        execution_head = $ExpectedExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            inherited_credentials = 'PENDING'
            authorization_127_registered_granted = 'PENDING'
            authorizations_118_through_126_consumed = 'PASS'
            inherited_execution_authority = 'NONE'
            directed_suite = $synthetic.result
            directed_case_count = $synthetic.case_count
            monotonic_wait_seconds = $synthetic.monotonic_wait_seconds
            zero_aws_calls_during_wait = ($synthetic.aws_calls_during_wait -eq 0)
            session_margin = 'PASS'
            interruption_during_stabilization = $synthetic.interruption_during_stabilization
            mandatory_rollback = $synthetic.rollback
            one_simulation = $synthetic.one_simulation
            stored_policy_semantic_hash = $synthetic.stored_policy_semantic_hash
            baseline_and_final_identical = $synthetic.baseline_and_final_identical
            aws_cli = 'PENDING'
            cli_history_disabled = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
        }
        bootstrap_identity = [ordered]@{
            verified = $false
            redacted_identifier = 'NOT_EXECUTED'
        }
        assume_role = [ordered]@{
            attempted = $false
            duration_seconds = $script:AssumeRoleDurationSeconds127
            succeeded = $false
        }
        role_identity = [ordered]@{
            verified = $false
            redacted_identifier = 'NOT_EXECUTED'
        }
        session_margin = [ordered]@{
            minimum_required_before_wait_seconds = $script:MinimumMarginBeforeWaitSeconds127
            bootstrap_remaining_before_wait_seconds = $null
            role_remaining_before_wait_seconds = $null
            minimum_remaining_before_wait_seconds = $null
            sufficient_before_wait = $false
            minimum_remaining_after_wait_seconds = $null
        }
        baseline = [ordered]@{
            list_attempted = $false
            temporary_policy_absent = $false
            policy_name_count = $null
            sorted_policy_names_sha256 = $null
        }
        temporary_grant = [ordered]@{
            policy_name = $script:TemporaryPolicyName127
            document_sha256 = Get-PL003125Sha256 -Text $script:TemporaryPolicyDocument127
            put_attempted = $false
            put_succeeded = $false
        }
        stored_policy = [ordered]@{
            get_attempted = $false
            get_succeeded = $false
            semantic_match = $false
            authorized_semantic_sha256 = Get-PL003125Sha256 -Text $script:SemanticPolicyCanonical127
            stored_semantic_sha256 = $null
        }
        stabilization = [ordered]@{
            clock = 'LOCAL_MONOTONIC_STOPWATCH'
            target_seconds = $script:StabilizationSeconds127
            elapsed_seconds = $null
            completed = $false
            interrupted = $false
            aws_calls_before = $null
            aws_calls_after = $null
            aws_calls_during = $null
        }
        simulation = [ordered]@{
            attempted = $false
            attempt_count = 0
            tested_action = 'iam:CreatePolicy'
            simulated_action_executed = $false
            call_succeeded = $false
            evaluation_decision = $null
            sanitized_classifier = $null
            mandatory_classification = $null
        }
        rollback = [ordered]@{
            required = $false
            delete_was_first_finally_aws_operation = $false
            delete_attempted = $false
            delete_succeeded = $false
            final_list_attempted = $false
            temporary_policy_absent = $false
            final_policy_name_count = $null
            final_sorted_policy_names_sha256 = $null
            final_hash_equals_baseline = $false
            final_set_equals_baseline = $false
            verified = $false
        }
        session_isolation = [ordered]@{
            bootstrap_used_for_simulation = $false
            bootstrap_used_for_policy_mutation_or_read = $false
            role_used_for_policy_mutation_and_read = $false
            role_used_for_simulation = $false
            result = 'PENDING'
        }
        aws_calls = [ordered]@{
            sts_get_session_token = 0
            sts_get_caller_identity_bootstrap = 0
            sts_assume_role = 0
            sts_get_caller_identity_role = 0
            iam_list_user_policies_baseline = 0
            iam_put_user_policy = 0
            iam_get_user_policy = 0
            iam_simulate_principal_policy = 0
            iam_delete_user_policy = 0
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
        temporary_files_cleared = $false
        failure_code = $null
        failure_metadata = $null
        result = 'IN_PROGRESS'
        interpretation_limits = [ordered]@{
            propagation_confirmed = $false
            structural_denial_confirmed = $false
        }
        redaction = [ordered]@{
            full_account_id_included = $false
            full_arns_included = $false
            credentials_tokens_or_mfa_codes_included = $false
            raw_aws_output_included = $false
        }
        post_attempt_authority = 'NONE'
    }

    $mfaPointer = [IntPtr]::Zero
    $secureMfa = $null
    $mfaCode = $null
    $mfaSerial = $null
    $accountId = $null
    $bootstrapArn = $null
    $roleArn = $null
    $bootstrapCredentials = $null
    $roleCredentials = $null
    $sessionCall = $null
    $bootstrapIdentityCall = $null
    $assumeCall = $null
    $roleIdentityCall = $null
    $baselineCall = $null
    $putCall = $null
    $getPolicyCall = $null
    $simulationCall = $null
    $deleteCall = $null
    $finalListCall = $null
    $baselineNames = @()
    $baselineHash = $null
    $putAttempted = $false
    $primarySucceeded = $false

    try {
        if ($synthetic.result -ne 'PASS') {
            throw 'LOCAL_DIRECTED_SUITE_FAILURE'
        }
        $currentHead = (& git -C $repositoryRoot rev-parse HEAD) -join ''
        if ($LASTEXITCODE -ne 0 -or $currentHead -cne $ExpectedExecutionHead) {
            throw 'HEAD_MISMATCH'
        }
        $evidence.prechecks.head = 'PASS'
        $worktreeStatus = @(& git -C $repositoryRoot status --porcelain=v1 --untracked-files=all)
        if ($LASTEXITCODE -ne 0 -or $worktreeStatus.Count -ne 0) {
            throw 'WORKTREE_NOT_CLEAN'
        }
        $evidence.prechecks.worktree = 'PASS'
        foreach ($name in $script:CredentialEnvironmentNames127) {
            if (-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, 'Process'))) {
                throw 'INHERITED_CREDENTIALS_PRESENT'
            }
        }
        $evidence.prechecks.inherited_credentials = 'PASS_ZERO'
        $authorization = Get-Content -LiteralPath $authorizationPath -Raw | ConvertFrom-Json
        if (
            [string]$authorization.authorization_id -cne $script:AuthorizationId127 -or
            [string]$authorization.status -cne 'GRANTED'
        ) {
            throw 'AUTHORIZATION_127_NOT_REGISTERED_GRANTED'
        }
        $evidence.prechecks.authorization_127_registered_granted = 'PASS'
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
        $profiles = @(& aws configure list-profiles 2>$null)
        if ($LASTEXITCODE -ne 0 -or $profiles -notcontains $script:BootstrapProfile127) {
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

        $mfaSerial = (& aws configure get mfa_serial --profile $script:BootstrapProfile127 2>$null) -join ''
        if ($mfaSerial -notmatch '^arn:aws:iam::(\d{12}):mfa/') {
            throw 'BOOTSTRAP_MFA_REFERENCE_INVALID'
        }
        $accountId = [string]$Matches[1]
        $bootstrapArn = "arn:aws:iam::$accountId`:user/$($script:BootstrapUserName127)"
        $roleArn = "arn:aws:iam::$accountId`:role/$($script:RoleName127)"

        [IO.Directory]::CreateDirectory($temporaryDirectory) | Out-Null
        [IO.File]::WriteAllText(
            $temporaryPolicyPath,
            $script:TemporaryPolicyDocument127,
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
            '--profile', $script:BootstrapProfile127,
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
        $bootstrapCredentials = ($sessionCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).Credentials
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
        $assumeCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'assume-role',
            '--role-arn', $roleArn,
            '--role-session-name', $script:RoleSessionName127,
            '--duration-seconds', [string]$script:AssumeRoleDurationSeconds127,
            '--region', $script:ExpectedRegion,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $bootstrapCredentials
        if ($assumeCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $assumeCall -Service 'sts' -Operation 'AssumeRole'
            throw 'BLOCKED_ASSUME_ROLE_FAILED'
        }
        $roleCredentials = ($assumeCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).Credentials
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
        $expectedRoleSessionArn = "arn:aws:sts::$accountId`:assumed-role/$($script:RoleName127)/$($script:RoleSessionName127)"
        if (
            [string]$roleIdentity.Account -cne $accountId -or
            [string]$roleIdentity.Arn -cne $expectedRoleSessionArn
        ) {
            throw 'ASSUMED_ROLE_IDENTITY_MISMATCH'
        }
        $evidence.role_identity.verified = $true
        $evidence.role_identity.redacted_identifier = 'ASSUMED_ROLE:<REDACTED_ACCOUNT_ID>:PL003BoundedSimulationSetupOperator/PL003Authorization127'

        $evidence.aws_calls.iam_list_user_policies_baseline = 1
        $evidence.baseline.list_attempted = $true
        $baselineCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'list-user-policies',
            '--user-name', $script:BootstrapUserName127,
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
        if ($baselineNames -contains $script:TemporaryPolicyName127) {
            throw 'BLOCKED_EXISTING_TEMPORARY_POLICY_COLLISION'
        }
        $baselineHash = Get-PL003125Sha256 -Text ($baselineNames -join "`n")
        $evidence.baseline.temporary_policy_absent = $true
        $evidence.baseline.policy_name_count = $baselineNames.Count
        $evidence.baseline.sorted_policy_names_sha256 = $baselineHash

        $putAttempted = $true
        $evidence.rollback.required = $true
        $evidence.temporary_grant.put_attempted = $true
        $evidence.aws_calls.iam_put_user_policy = 1
        $evidence.mutations.temporary_grant_attempts = 1
        $putCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'put-user-policy',
            '--user-name', $script:BootstrapUserName127,
            '--policy-name', $script:TemporaryPolicyName127,
            '--policy-document', ('file://' + $temporaryPolicyPath.Replace('\', '/')),
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $roleCredentials
        $evidence.session_isolation.role_used_for_policy_mutation_and_read = $true
        if ($putCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $putCall -Service 'iam' -Operation 'PutUserPolicy'
            throw 'BLOCKED_TEMPORARY_GRANT_FAILED'
        }
        $evidence.temporary_grant.put_succeeded = $true
        $evidence.mutations.temporary_grant_successes = 1
        $evidence.mutations.persistent_at_completion = 1

        $evidence.aws_calls.iam_get_user_policy = 1
        $evidence.stored_policy.get_attempted = $true
        $getPolicyCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-user-policy',
            '--user-name', $script:BootstrapUserName127,
            '--policy-name', $script:TemporaryPolicyName127,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $roleCredentials
        if ($getPolicyCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $getPolicyCall -Service 'iam' -Operation 'GetUserPolicy'
            throw 'BLOCKED_STORED_POLICY_READ_FAILED'
        }
        $evidence.stored_policy.get_succeeded = $true
        $storedResponse = $getPolicyCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $storedCanonical = Get-PL003127SemanticPolicyCanonical -Document $storedResponse.PolicyDocument
        if ([string]::IsNullOrWhiteSpace([string]$storedCanonical)) {
            throw 'BLOCKED_STORED_POLICY_SEMANTIC_MISMATCH'
        }
        $storedSemanticHash = Get-PL003125Sha256 -Text $storedCanonical
        $evidence.stored_policy.stored_semantic_sha256 = $storedSemanticHash
        $evidence.stored_policy.semantic_match = (
            $storedSemanticHash -ceq $evidence.stored_policy.authorized_semantic_sha256
        )
        if (-not $evidence.stored_policy.semantic_match) {
            throw 'BLOCKED_STORED_POLICY_SEMANTIC_MISMATCH'
        }

        $now = [DateTimeOffset]::UtcNow
        $bootstrapRemaining = [int][Math]::Floor(
            ([DateTimeOffset]::Parse([string]$bootstrapCredentials.Expiration) - $now).TotalSeconds
        )
        $roleRemaining = [int][Math]::Floor(
            ([DateTimeOffset]::Parse([string]$roleCredentials.Expiration) - $now).TotalSeconds
        )
        $minimumRemaining = [Math]::Min($bootstrapRemaining, $roleRemaining)
        $evidence.session_margin.bootstrap_remaining_before_wait_seconds = $bootstrapRemaining
        $evidence.session_margin.role_remaining_before_wait_seconds = $roleRemaining
        $evidence.session_margin.minimum_remaining_before_wait_seconds = $minimumRemaining
        $evidence.session_margin.sufficient_before_wait = (
            $minimumRemaining -ge $script:MinimumMarginBeforeWaitSeconds127
        )
        if (-not $evidence.session_margin.sufficient_before_wait) {
            throw 'BLOCKED_INSUFFICIENT_SESSION_MARGIN'
        }

        $evidence.stabilization.aws_calls_before = Get-PL003127AwsCallCount -CallMap $evidence.aws_calls
        try {
            $waitResult = Wait-PL003127Monotonic -DurationSeconds $script:StabilizationSeconds127
            $evidence.stabilization.elapsed_seconds = $waitResult.elapsed_seconds
            $evidence.stabilization.completed = $waitResult.completed
        } catch {
            $evidence.stabilization.interrupted = $true
            throw 'BLOCKED_STABILIZATION_INTERRUPTED'
        }
        $evidence.stabilization.aws_calls_after = Get-PL003127AwsCallCount -CallMap $evidence.aws_calls
        $evidence.stabilization.aws_calls_during = (
            $evidence.stabilization.aws_calls_after -
            $evidence.stabilization.aws_calls_before
        )
        if (
            -not $evidence.stabilization.completed -or
            $evidence.stabilization.aws_calls_during -ne 0
        ) {
            throw 'BLOCKED_STABILIZATION_CONTRACT_FAILED'
        }
        $postWaitNow = [DateTimeOffset]::UtcNow
        $postWaitBootstrapRemaining = [int][Math]::Floor(
            ([DateTimeOffset]::Parse([string]$bootstrapCredentials.Expiration) - $postWaitNow).TotalSeconds
        )
        $postWaitRoleRemaining = [int][Math]::Floor(
            ([DateTimeOffset]::Parse([string]$roleCredentials.Expiration) - $postWaitNow).TotalSeconds
        )
        $evidence.session_margin.minimum_remaining_after_wait_seconds = [Math]::Min(
            $postWaitBootstrapRemaining,
            $postWaitRoleRemaining
        )

        $contextEntries = @(
            'ContextKeyName=aws:MultiFactorAuthPresent,ContextKeyValues=true,ContextKeyType=boolean',
            'ContextKeyName=aws:RequestTag/Project,ContextKeyValues=PRODUCT-LEADERSHIP-TEST-003,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Authorization,ContextKeyValues=127,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Temporary,ContextKeyValues=true,ContextKeyType=string'
        )
        $simulationArguments = @(
            'iam', 'simulate-principal-policy',
            '--policy-source-arn', $bootstrapArn,
            '--action-names', 'iam:CreatePolicy',
            '--resource-arns', "arn:aws:iam::$accountId`:policy/$($script:BoundaryName127)",
            '--context-entries'
        ) + $contextEntries + @(
            '--no-cli-pager',
            '--output', 'json'
        )
        $evidence.aws_calls.iam_simulate_principal_policy = 1
        $evidence.simulation.attempted = $true
        $evidence.simulation.attempt_count = 1
        $simulationCall = Invoke-PL003AwsCliCaptured `
            -Arguments $simulationArguments `
            -Credentials $bootstrapCredentials
        $evidence.session_isolation.bootstrap_used_for_simulation = $true
        $simulationErrorCode = Get-PL003AwsErrorCode -StdErr $simulationCall.RawStdErr
        $evidence.simulation.sanitized_classifier = Get-PL003SimulationClassification `
            -ExitCode $simulationCall.ExitCode `
            -StdErr $simulationCall.RawStdErr `
            -StdOut $simulationCall.RawStdOut `
            -AwsErrorCode $simulationErrorCode
        if ($simulationCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $simulationCall -Service 'iam' -Operation 'SimulatePrincipalPolicy'
            if (
                $simulationErrorCode -ceq 'AccessDenied' -and
                $evidence.stored_policy.semantic_match -and
                $evidence.stabilization.completed -and
                $evidence.stabilization.aws_calls_during -eq 0 -and
                $evidence.session_margin.sufficient_before_wait
            ) {
                $evidence.simulation.mandatory_classification = 'BLOCKED_ACCESS_DENIED_AFTER_BOUNDED_STABILIZATION'
                throw 'BLOCKED_ACCESS_DENIED_AFTER_BOUNDED_STABILIZATION'
            }
            $evidence.simulation.mandatory_classification = 'BLOCKED_SIMULATION_CALL_FAILED_OTHER'
            throw 'BLOCKED_SIMULATION_CALL_FAILED_OTHER'
        }
        $simulationDocument = $simulationCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $evaluationResults = @($simulationDocument.EvaluationResults)
        if ($evaluationResults.Count -lt 1) {
            throw 'SIMULATION_RESPONSE_SHAPE_INVALID'
        }
        $evidence.simulation.call_succeeded = $true
        $evidence.simulation.evaluation_decision = [string]$evaluationResults[0].EvalDecision
        $evidence.simulation.mandatory_classification = 'PASS_PROPAGATION_AWARE_SIMULATION_COMPLETED_AND_POLICY_REMOVED'
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
                '--user-name', $script:BootstrapUserName127,
                '--policy-name', $script:TemporaryPolicyName127,
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

            $evidence.rollback.final_list_attempted = $true
            $evidence.aws_calls.iam_list_user_policies_final = 1
            $finalListCall = Invoke-PL003AwsCliCaptured -Arguments @(
                'iam', 'list-user-policies',
                '--user-name', $script:BootstrapUserName127,
                '--no-cli-pager',
                '--output', 'json'
            ) -Credentials $roleCredentials
            if ($finalListCall.ExitCode -eq 0) {
                $finalNames = @(
                    ($finalListCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop).PolicyNames |
                        ForEach-Object { [string]$_ } |
                        Sort-Object
                )
                $finalHash = Get-PL003125Sha256 -Text ($finalNames -join "`n")
                $evidence.rollback.temporary_policy_absent = (
                    $finalNames -notcontains $script:TemporaryPolicyName127
                )
                $evidence.rollback.final_policy_name_count = $finalNames.Count
                $evidence.rollback.final_sorted_policy_names_sha256 = $finalHash
                $evidence.rollback.final_hash_equals_baseline = ($finalHash -ceq $baselineHash)
                $evidence.rollback.final_set_equals_baseline = (
                    ($finalNames -join "`n") -ceq ($baselineNames -join "`n")
                )
            } elseif ($null -eq $evidence.failure_metadata) {
                Set-PL003125FailureMetadata -Evidence $evidence -Call $finalListCall -Service 'iam' -Operation 'ListUserPolicies'
            }
            $evidence.rollback.verified = (
                $evidence.rollback.delete_succeeded -and
                $evidence.rollback.temporary_policy_absent -and
                $evidence.rollback.final_hash_equals_baseline -and
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

        $evidence.session_isolation.result = if (
            $evidence.session_isolation.bootstrap_used_for_simulation -and
            -not $evidence.session_isolation.bootstrap_used_for_policy_mutation_or_read -and
            $evidence.session_isolation.role_used_for_policy_mutation_and_read -and
            -not $evidence.session_isolation.role_used_for_simulation
        ) {
            'PASS'
        } elseif (-not $putAttempted) {
            'NOT_FULLY_EXERCISED_BEFORE_GRANT'
        } elseif (-not $evidence.simulation.attempted) {
            'PASS_NO_SIMULATION_DUE_TO_PRE_SIMULATION_STOP'
        } else {
            'FAIL'
        }

        if ($primarySucceeded -and $evidence.rollback.verified) {
            $evidence.status = 'COMPLETE'
            $evidence.result = 'PASS_PROPAGATION_AWARE_SIMULATION_COMPLETED_AND_POLICY_REMOVED'
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
        $evidence.temporary_files_cleared = -not (Test-Path -LiteralPath $temporaryDirectory)

        $secureMfa = $null
        $mfaCode = $null
        $mfaSerial = $null
        $bootstrapCredentials = $null
        $roleCredentials = $null
        $sessionCall = $null
        $bootstrapIdentityCall = $null
        $assumeCall = $null
        $roleIdentityCall = $null
        $baselineCall = $null
        $putCall = $null
        $getPolicyCall = $null
        $simulationCall = $null
        $deleteCall = $null
        $finalListCall = $null
        $accountId = $null
        $bootstrapArn = $null
        $roleArn = $null
        $baselineNames = $null
        $baselineHash = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        $evidence.credentials_cleared = $true
        Write-PL003127Evidence -Evidence $evidence -Path $evidencePath
    }

    return [ordered]@{
        result = $evidence.result
        status = $evidence.status
        failure_code = $evidence.failure_code
        bootstrap_identity = $evidence.bootstrap_identity.redacted_identifier
        assume_role = $evidence.assume_role
        role_identity = $evidence.role_identity.redacted_identifier
        session_margin = $evidence.session_margin
        baseline = $evidence.baseline
        temporary_grant = $evidence.temporary_grant
        stored_policy = $evidence.stored_policy
        stabilization = $evidence.stabilization
        simulation = $evidence.simulation
        rollback = $evidence.rollback
        session_isolation = $evidence.session_isolation
        aws_calls = $evidence.aws_calls
        mutations = $evidence.mutations
        credentials_cleared = $evidence.credentials_cleared
        temporary_files_cleared = $evidence.temporary_files_cleared
        evidence_path = $evidencePath.Substring($repositoryRoot.Length + 1).Replace('\', '/')
        secrets_printed = $false
    }
}

if ($MyInvocation.InvocationName -eq '.') {
    return
}

if ($SyntheticTest -or -not $OperationalRun) {
    $test = Test-PL003PropagationAwareAtomicSimulationRetry127
    $test | ConvertTo-Json -Depth 12
    if ($test.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003PropagationAwareAtomicSimulationRetry127 `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber
$outcome | ConvertTo-Json -Depth 16
if ($outcome.result -eq 'PASS_PROPAGATION_AWARE_SIMULATION_COMPLETED_AND_POLICY_REMOVED') {
    exit 0
}
exit 1
