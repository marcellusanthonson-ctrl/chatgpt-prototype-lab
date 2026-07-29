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
    [int]$AttemptNumber = 1,

    [Parameter(ParameterSetName = 'Operational')]
    [string]$EvidencePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$requestedOperationalRun120 = [bool]$OperationalRun
$requestedSyntheticTest120 = [bool]$SyntheticTest
$requestedExpectedHead120 = $ExpectedHead
$requestedAttemptNumber120 = $AttemptNumber
$requestedEvidencePath120 = $EvidencePath

$permission119Script = Join-Path $PSScriptRoot 'Invoke-PL003TemporarySimulationPermission119.ps1'
. $permission119Script

$OperationalRun = $requestedOperationalRun120
$SyntheticTest = $requestedSyntheticTest120
$ExpectedHead = $requestedExpectedHead120
$AttemptNumber = $requestedAttemptNumber120
$EvidencePath = $requestedEvidencePath120

$script:AuthorizationId120 = 'AUTHORIZATION_LAB_PL003_ATOMIC_SIMULATION_PERMISSION_CYCLE_120'
$script:TemporaryPolicyName120 = 'PL003AtomicSimulationOnly120'
$script:TemporaryPolicyDocument120 = '{"Version":"2012-10-17","Statement":[{"Sid":"AtomicPL003SimulationOnly","Effect":"Allow","Action":"iam:SimulatePrincipalPolicy","Resource":"*"}]}'

function Test-PL003AuthorizedPolicyDocument120 {
    param([Parameter(Mandatory)]$PolicyDocument)

    try {
        $statements = @($PolicyDocument.Statement)
        if ([string]$PolicyDocument.Version -ne '2012-10-17' -or $statements.Count -ne 1) {
            return $false
        }
        $statement = $statements[0]
        $actions = @($statement.Action)
        $resources = @($statement.Resource)
        return (
            [string]$statement.Sid -eq 'AtomicPL003SimulationOnly' -and
            [string]$statement.Effect -eq 'Allow' -and
            $actions.Count -eq 1 -and
            [string]$actions[0] -ceq 'iam:SimulatePrincipalPolicy' -and
            $resources.Count -eq 1 -and
            [string]$resources[0] -ceq '*'
        )
    } catch {
        return $false
    }
}

function Invoke-PL003120SyntheticAtomicCycle {
    param(
        [bool]$PutAttempted,
        [bool]$PutSucceeded,
        [bool]$PostPutStepFails,
        [bool]$DeleteSucceeds,
        [bool]$FinalAbsent
    )

    $events = [System.Collections.Generic.List[string]]::new()
    $failure = $null
    try {
        $events.Add('BASELINE')
        if ($PutAttempted) {
            $events.Add('PUT')
            if (-not $PutSucceeded) {
                throw 'PUT_FAILED'
            }
            if ($PostPutStepFails) {
                throw 'POST_PUT_FAILURE'
            }
            $events.Add('SIMULATE')
        }
    } catch {
        $failure = [string]$_.Exception.Message
    } finally {
        if ($PutAttempted) {
            $events.Add('DELETE')
            if (-not $DeleteSucceeds) {
                $failure = 'ROLLBACK_FAILED'
            }
        }
        $events.Add('FINAL_ABSENCE_CHECK')
        if (-not $FinalAbsent) {
            $failure = 'ROLLBACK_FAILED'
        }
    }
    return [ordered]@{
        events = @($events)
        failure = $failure
        delete_count = @($events | Where-Object { $_ -eq 'DELETE' }).Count
        final_absence = $FinalAbsent
    }
}

function Test-PL003AtomicSimulationPermissionCycle120 {
    $failures = [System.Collections.Generic.List[string]]::new()
    $base = Test-PL003TemporarySimulationPermission119
    if ($base.result -ne 'PASS') {
        $failures.Add('base-sanitization-and-rollback')
    }

    $document = $script:TemporaryPolicyDocument120 | ConvertFrom-Json
    if (-not (Test-PL003AuthorizedPolicyDocument120 -PolicyDocument $document)) {
        $failures.Add('exact-document')
    }
    $extra = '{"Version":"2012-10-17","Statement":[{"Sid":"AtomicPL003SimulationOnly","Effect":"Allow","Action":["iam:SimulatePrincipalPolicy","iam:GetUserPolicy"],"Resource":"*"}]}' | ConvertFrom-Json
    if (Test-PL003AuthorizedPolicyDocument120 -PolicyDocument $extra) {
        $failures.Add('extra-action-rejection')
    }

    $postPutFailure = Invoke-PL003120SyntheticAtomicCycle -PutAttempted $true -PutSucceeded $true -PostPutStepFails $true -DeleteSucceeds $true -FinalAbsent $true
    if (
        $postPutFailure.delete_count -ne 1 -or
        $postPutFailure.events[2] -ne 'DELETE' -or
        $postPutFailure.events[3] -ne 'FINAL_ABSENCE_CHECK'
    ) {
        $failures.Add('immediate-finally-delete')
    }

    $putFailure = Invoke-PL003120SyntheticAtomicCycle -PutAttempted $true -PutSucceeded $false -PostPutStepFails $false -DeleteSucceeds $true -FinalAbsent $true
    if ($putFailure.delete_count -ne 1 -or $putFailure.events[2] -ne 'DELETE') {
        $failures.Add('delete-after-uncertain-put')
    }

    $success = Invoke-PL003120SyntheticAtomicCycle -PutAttempted $true -PutSucceeded $true -PostPutStepFails $false -DeleteSucceeds $true -FinalAbsent $true
    if (
        ($success.events -join ',') -ne 'BASELINE,PUT,SIMULATE,DELETE,FINAL_ABSENCE_CHECK' -or
        $success.delete_count -ne 1 -or
        -not $success.final_absence
    ) {
        $failures.Add('successful-atomic-cycle')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = $base.case_count + 5
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        authorized_policy_sha256 = Get-PL003Sha256Text -Text $script:TemporaryPolicyDocument120
        exact_action = 'iam:SimulatePrincipalPolicy'
        additional_actions = 0
        delete_is_first_finally_aws_operation = if ($failures -contains 'immediate-finally-delete') { 'FAIL' } else { 'PASS' }
        delete_after_any_put_attempt = if ($failures -contains 'delete-after-uncertain-put') { 'FAIL' } else { 'PASS' }
        aws_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function New-PL003120Evidence {
    param(
        [Parameter(Mandatory)][string]$ExecutionHead,
        [Parameter(Mandatory)][string]$AttemptId,
        [Parameter(Mandatory)]$SyntheticResult
    )

    return [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-ATOMIC-SIMULATION-PERMISSION-CYCLE-120-$AttemptId"
        attempt_id = $AttemptId
        authorization_id = $script:AuthorizationId120
        project_id = 'lab'
        kind = 'REDACTED_ATOMIC_TEMPORARY_IAM_PERMISSION_CYCLE_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        execution_head = $ExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            authorization_119_consumed = 'PASS'
            active_execution_authority_before_120 = 'NONE'
            aws_cli = 'PENDING'
            cli_history_disabled = 'PENDING'
            inherited_temporary_credentials_absent = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
            bootstrap_profile = 'PENDING'
            region = 'PENDING'
            mfa_reference = 'PENDING'
            synthetic_atomic_cycle = $SyntheticResult.result
            delete_is_first_finally_aws_operation = $SyntheticResult.delete_is_first_finally_aws_operation
        }
        principal = [ordered]@{
            expected_bootstrap_principal_match = $false
            principal_type = 'IAM_USER'
            principal_identifier = 'REDACTED'
            full_arn_included = $false
            full_account_id_included = $false
        }
        baseline = [ordered]@{
            mechanism = 'GetUserPolicy_EXACT_NAME'
            temporary_policy_absent = $false
            sanitized_call_metadata = $null
        }
        grant = [ordered]@{
            mechanism = 'INLINE_USER_POLICY'
            policy_name = $script:TemporaryPolicyName120
            policy_document_sha256 = Get-PL003Sha256Text -Text $script:TemporaryPolicyDocument120
            authorized_action = 'iam:SimulatePrincipalPolicy'
            additional_actions = 0
            mutation_attempted = $false
            mutation_succeeded = $false
            effective_document_verified = $false
            sanitized_put_metadata = $null
            sanitized_get_metadata = $null
        }
        simulation = [ordered]@{
            tested_action = 'iam:CreatePolicy'
            tested_resource_shape = 'IAM_POLICY_PL003_SETUP_BOUNDARY'
            call_attempted = $false
            call_without_access_denied = $false
            evaluation_decision = $null
            sanitized_call_metadata = $null
        }
        rollback = [ordered]@{
            removal_attempted = $false
            removal_succeeded = $false
            removal_was_first_finally_aws_operation = $false
            final_absence_check_attempted = $false
            temporary_policy_absent = $false
            sanitized_delete_metadata = $null
            sanitized_final_get_metadata = $null
        }
        aws_calls = [ordered]@{
            sts_get_session_token = 0
            sts_get_caller_identity = 0
            iam_get_user_policy = 0
            iam_put_user_policy = 0
            iam_simulate_principal_policy = 0
            iam_delete_user_policy = 0
            other_aws = 0
        }
        iam_mutations = [ordered]@{
            grant_attempts = 0
            grant_successes = 0
            removal_attempts = 0
            removal_successes = 0
            unexpected = 0
        }
        zero_out_of_scope_effects = [ordered]@{
            persistent_iam_mutations = 0
            aws_infrastructure_mutations = 0
            aws_resources_created = 0
            terraform_executions = 0
            product_leadership_test_003_executions = 0
            product_leadership_active = $false
            product_leadership_integrated = $false
        }
        ephemeral_credentials_cleared = $false
        temporary_policy_file_removed = $false
        failure_code = $null
        result = 'IN_PROGRESS'
        redaction = [ordered]@{
            full_account_id_included = $false
            full_principal_arns_included = $false
            access_keys_included = $false
            secret_access_keys_included = $false
            session_tokens_included = $false
            mfa_codes_included = $false
            request_ids_included = $false
            raw_stdout_or_stderr_persisted = $false
        }
        post_attempt_authority = 'NONE'
    }
}

function Invoke-PL003AtomicSimulationPermissionCycle120 {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber,
        [AllowNull()][string]$RequestedEvidencePath
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $defaultEvidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-ATOMIC-SIMULATION-PERMISSION-CYCLE-120-$attemptId.json"
    $targetEvidencePath = if ([string]::IsNullOrWhiteSpace($RequestedEvidencePath)) {
        $defaultEvidencePath
    } else {
        [IO.Path]::GetFullPath($RequestedEvidencePath)
    }
    $authorizedEvidenceRoot = Join-Path $repositoryRoot 'projects\lab\evidence'
    if (-not $targetEvidencePath.StartsWith($authorizedEvidenceRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'EVIDENCE_PATH_OUTSIDE_AUTHORIZED_DIRECTORY'
    }

    $syntheticResult = Test-PL003AtomicSimulationPermissionCycle120
    $result = New-PL003120Evidence -ExecutionHead $ExpectedExecutionHead -AttemptId $attemptId -SyntheticResult $syntheticResult
    $temporaryPolicyPath = Join-Path $PSScriptRoot ('.pl003-120-policy-{0}.json' -f $PID)

    $secureMfa = $null
    $mfaPointer = [IntPtr]::Zero
    $mfaCode = $null
    $credentials = $null
    $sessionCall = $null
    $identityCall = $null
    $baselineCall = $null
    $putCall = $null
    $effectiveCall = $null
    $simulationCall = $null
    $deleteCall = $null
    $finalGetCall = $null
    $putAttempted = $false
    $putSucceeded = $false
    $operationFailure = $null
    $accountId = $null
    $principalArn = $null
    $simulationArguments = $null

    try {
        $head = git -C $repositoryRoot rev-parse HEAD
        if ($LASTEXITCODE -ne 0 -or $head -ne $ExpectedExecutionHead) {
            throw 'HEAD_MISMATCH'
        }
        $result.prechecks.head = 'PASS'

        $worktreeEntries = @(git -C $repositoryRoot status --porcelain=v1 --untracked-files=all)
        if ($LASTEXITCODE -ne 0 -or $worktreeEntries.Count -ne 0) {
            throw 'WORKTREE_NOT_CLEAN'
        }
        $result.prechecks.worktree = 'PASS'
        if ($syntheticResult.result -ne 'PASS' -or $syntheticResult.delete_is_first_finally_aws_operation -ne 'PASS') {
            throw 'LOCAL_ATOMIC_CYCLE_TEST_FAILED'
        }

        if ($null -eq (Get-Command aws -ErrorAction SilentlyContinue)) {
            throw 'AWS_CLI_NOT_AVAILABLE'
        }
        $result.prechecks.aws_cli = 'PASS'
        if ([Environment]::GetEnvironmentVariable('AWS_CLI_HISTORY', 'Process') -eq 'enabled') {
            throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
        }
        $profiles = @(& aws configure list-profiles 2>$null)
        if ($LASTEXITCODE -ne 0 -or (& aws configure get cli_history 2>$null) -eq 'enabled') {
            throw 'AWS_CLI_CONFIGURATION_INVALID'
        }
        $result.prechecks.cli_history_disabled = 'PASS'

        $presentCredentialNames = @(
            $script:CredentialEnvironmentNames | Where-Object {
                -not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($_, 'Process'))
            }
        )
        if ($presentCredentialNames.Count -ne 0) {
            throw 'PREEXISTING_AWS_CREDENTIAL_ENVIRONMENT_DETECTED'
        }
        $result.prechecks.inherited_temporary_credentials_absent = 'PASS'

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
        $result.prechecks.reusable_temporary_profiles_absent = 'PASS'
        if ($profiles -notcontains $script:SourceProfile) {
            throw 'BOOTSTRAP_PROFILE_NOT_FOUND'
        }
        $result.prechecks.bootstrap_profile = 'PASS'

        $configuredRegion = & aws configure get region --profile $script:SourceProfile 2>$null
        if ([string]::IsNullOrWhiteSpace(($configuredRegion -join ''))) {
            $configuredRegion = $script:ExpectedRegion
        }
        if (($configuredRegion -join '') -ne $script:ExpectedRegion) {
            throw 'BOOTSTRAP_REGION_MISMATCH'
        }
        $result.prechecks.region = 'PASS'

        $mfaSerial = & aws configure get mfa_serial --profile $script:SourceProfile 2>$null
        if ([string]::IsNullOrWhiteSpace(($mfaSerial -join ''))) {
            $mfaSerial = & aws configure get mfa_serial --profile $script:MfaReferenceProfile 2>$null
        }
        if ([string]::IsNullOrWhiteSpace(($mfaSerial -join ''))) {
            throw 'MFA_REFERENCE_NOT_CONFIGURED'
        }
        $mfaSerial = ($mfaSerial -join '')
        $result.prechecks.mfa_reference = 'PASS'

        $secureMfa = Read-Host -Prompt 'MFA token code' -AsSecureString
        $mfaPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureMfa)
        $mfaCode = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($mfaPointer)
        if ($mfaCode -notmatch '^\d{6}$') {
            throw 'INVALID_MFA_CODE_FORMAT'
        }

        $result.aws_calls.sts_get_session_token = 1
        $sessionCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'get-session-token',
            '--profile', $script:SourceProfile,
            '--region', $script:ExpectedRegion,
            '--serial-number', $mfaSerial,
            '--token-code', $mfaCode,
            '--duration-seconds', [string]$script:DurationSeconds,
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
            throw 'MFA_SESSION_ESTABLISHMENT_FAILED'
        }
        $sessionDocument = $sessionCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $credentials = $sessionDocument.Credentials
        if (
            [string]::IsNullOrWhiteSpace([string]$credentials.AccessKeyId) -or
            [string]::IsNullOrWhiteSpace([string]$credentials.SecretAccessKey) -or
            [string]::IsNullOrWhiteSpace([string]$credentials.SessionToken)
        ) {
            throw 'TEMPORARY_CREDENTIAL_SHAPE_INVALID'
        }

        $result.aws_calls.sts_get_caller_identity = 1
        $identityCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'sts', 'get-caller-identity',
            '--region', $script:ExpectedRegion,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $credentials
        if ($identityCall.ExitCode -ne 0) {
            throw 'BOOTSTRAP_IDENTITY_RESOLUTION_FAILED'
        }
        $identityDocument = $identityCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $accountId = [string]$identityDocument.Account
        $principalArn = [string]$identityDocument.Arn
        if ($accountId -notmatch '^\d{12}$') {
            throw 'STS_ACCOUNT_SHAPE_INVALID'
        }
        if ($principalArn -notmatch ('^arn:aws:iam::\d{12}:user/' + [regex]::Escape($script:ExpectedBootstrapPrincipal) + '$')) {
            throw 'BLOCKED_PRINCIPAL_MISMATCH'
        }
        $result.principal.expected_bootstrap_principal_match = $true

        $result.aws_calls.iam_get_user_policy++
        $baselineCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-user-policy',
            '--user-name', $script:ExpectedBootstrapPrincipal,
            '--policy-name', $script:TemporaryPolicyName120,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $credentials
        $result.baseline.sanitized_call_metadata = Get-PL003SanitizedCallMetadata -ExitCode $baselineCall.ExitCode -StdErr $baselineCall.RawStdErr -Service 'iam' -Operation 'GetUserPolicy'
        if ($baselineCall.ExitCode -eq 0) {
            throw 'BLOCKED_EXISTING_POLICY_COLLISION'
        }
        $baselineError = Get-PL003AwsErrorCode -StdErr $baselineCall.RawStdErr
        if ($baselineError -notmatch 'NoSuchEntity') {
            throw 'BLOCKED_BASELINE_EXACT_POLICY_READ_FAILED'
        }
        $result.baseline.temporary_policy_absent = $true

        $policyBytes = [Text.UTF8Encoding]::new($false).GetBytes($script:TemporaryPolicyDocument120)
        $policyStream = [IO.File]::Open($temporaryPolicyPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try {
            $policyStream.Write($policyBytes, 0, $policyBytes.Length)
        } finally {
            $policyStream.Dispose()
        }

        $putAttempted = $true
        $result.grant.mutation_attempted = $true
        $result.aws_calls.iam_put_user_policy = 1
        $result.iam_mutations.grant_attempts = 1
        $putCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'put-user-policy',
            '--user-name', $script:ExpectedBootstrapPrincipal,
            '--policy-name', $script:TemporaryPolicyName120,
            '--policy-document', ('file://' + $temporaryPolicyPath),
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $credentials
        $result.grant.sanitized_put_metadata = Get-PL003SanitizedCallMetadata -ExitCode $putCall.ExitCode -StdErr $putCall.RawStdErr -Service 'iam' -Operation 'PutUserPolicy'
        if ($putCall.ExitCode -ne 0) {
            if ((Get-PL003AwsErrorCode -StdErr $putCall.RawStdErr) -match 'AccessDenied|Unauthorized') {
                throw 'BLOCKED_PERMISSION_GRANT_NOT_AUTHORIZED'
            }
            throw 'TEMPORARY_PERMISSION_PUT_FAILED'
        }
        $putSucceeded = $true
        $result.grant.mutation_succeeded = $true
        $result.iam_mutations.grant_successes = 1

        $result.aws_calls.iam_get_user_policy++
        $effectiveCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-user-policy',
            '--user-name', $script:ExpectedBootstrapPrincipal,
            '--policy-name', $script:TemporaryPolicyName120,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $credentials
        $result.grant.sanitized_get_metadata = Get-PL003SanitizedCallMetadata -ExitCode $effectiveCall.ExitCode -StdErr $effectiveCall.RawStdErr -Service 'iam' -Operation 'GetUserPolicy'
        if ($effectiveCall.ExitCode -ne 0) {
            throw 'EFFECTIVE_POLICY_READ_FAILED'
        }
        $effectiveDocument = $effectiveCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        if (-not (Test-PL003AuthorizedPolicyDocument120 -PolicyDocument $effectiveDocument.PolicyDocument)) {
            throw 'EFFECTIVE_POLICY_DOCUMENT_MISMATCH'
        }
        $result.grant.effective_document_verified = $true

        $resourceArn = "arn:aws:iam::$accountId`:policy/PL003IAMSetupBoundary114"
        $contextEntries = @(
            'ContextKeyName=aws:MultiFactorAuthPresent,ContextKeyValues=true,ContextKeyType=boolean',
            'ContextKeyName=aws:RequestTag/Project,ContextKeyValues=PRODUCT-LEADERSHIP-TEST-003,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Authorization,ContextKeyValues=120,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Temporary,ContextKeyValues=true,ContextKeyType=string'
        )
        $simulationArguments = @(
            'iam', 'simulate-principal-policy',
            '--policy-source-arn', $principalArn,
            '--action-names', 'iam:CreatePolicy',
            '--resource-arns', $resourceArn,
            '--context-entries'
        ) + $contextEntries + @(
            '--no-cli-pager',
            '--output', 'json'
        )

        $result.simulation.call_attempted = $true
        $result.aws_calls.iam_simulate_principal_policy = 1
        $simulationCall = Invoke-PL003AwsCliCaptured -Arguments $simulationArguments -Credentials $credentials
        $result.simulation.sanitized_call_metadata = Get-PL003SanitizedCallMetadata -ExitCode $simulationCall.ExitCode -StdErr $simulationCall.RawStdErr -Service 'iam' -Operation 'SimulatePrincipalPolicy'
        if ($simulationCall.ExitCode -ne 0) {
            if ((Get-PL003AwsErrorCode -StdErr $simulationCall.RawStdErr) -match 'AccessDenied|Unauthorized') {
                throw 'BLOCKED_SIMULATION_STILL_ACCESS_DENIED'
            }
            throw 'READ_ONLY_SIMULATION_FAILED_OTHER'
        }
        $simulationDocument = $simulationCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $decision = [string]$simulationDocument.EvaluationResults[0].EvalDecision
        if ($decision -notin @('allowed', 'implicitDeny', 'explicitDeny')) {
            throw 'SIMULATION_DECISION_INVALID'
        }
        $result.simulation.call_without_access_denied = $true
        $result.simulation.evaluation_decision = $decision
    } catch {
        $operationFailure = [string]$_.Exception.Message
    } finally {
        # This deletion is deliberately the first AWS operation in finally after any PutUserPolicy attempt.
        if ($putAttempted -and $null -ne $credentials) {
            $result.rollback.removal_attempted = $true
            $result.rollback.removal_was_first_finally_aws_operation = $true
            $result.aws_calls.iam_delete_user_policy = 1
            $result.iam_mutations.removal_attempts = 1
            $deleteCall = Invoke-PL003AwsCliCaptured -Arguments @(
                'iam', 'delete-user-policy',
                '--user-name', $script:ExpectedBootstrapPrincipal,
                '--policy-name', $script:TemporaryPolicyName120,
                '--no-cli-pager',
                '--output', 'json'
            ) -Credentials $credentials
            $result.rollback.sanitized_delete_metadata = Get-PL003SanitizedCallMetadata -ExitCode $deleteCall.ExitCode -StdErr $deleteCall.RawStdErr -Service 'iam' -Operation 'DeleteUserPolicy'
            if ($deleteCall.ExitCode -eq 0) {
                $result.rollback.removal_succeeded = $true
                $result.iam_mutations.removal_successes = 1
            } elseif (
                -not $putSucceeded -and
                (Get-PL003AwsErrorCode -StdErr $deleteCall.RawStdErr) -match 'NoSuchEntity'
            ) {
                $result.rollback.removal_succeeded = $true
            } else {
                $operationFailure = 'BLOCKED_ROLLBACK_NOT_VERIFIED'
            }
        }

        if ($null -ne $credentials -and $result.baseline.temporary_policy_absent) {
            $result.rollback.final_absence_check_attempted = $true
            $result.aws_calls.iam_get_user_policy++
            $finalGetCall = Invoke-PL003AwsCliCaptured -Arguments @(
                'iam', 'get-user-policy',
                '--user-name', $script:ExpectedBootstrapPrincipal,
                '--policy-name', $script:TemporaryPolicyName120,
                '--no-cli-pager',
                '--output', 'json'
            ) -Credentials $credentials
            $result.rollback.sanitized_final_get_metadata = Get-PL003SanitizedCallMetadata -ExitCode $finalGetCall.ExitCode -StdErr $finalGetCall.RawStdErr -Service 'iam' -Operation 'GetUserPolicy'
            $finalError = Get-PL003AwsErrorCode -StdErr $finalGetCall.RawStdErr
            if ($finalGetCall.ExitCode -ne 0 -and $finalError -match 'NoSuchEntity') {
                $result.rollback.temporary_policy_absent = $true
            } else {
                $operationFailure = 'BLOCKED_ROLLBACK_NOT_VERIFIED'
            }
        }

        if ($mfaPointer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($mfaPointer)
        }
        $secureMfa = $null
        $mfaCode = $null
        if (Test-Path -LiteralPath $temporaryPolicyPath -PathType Leaf) {
            Remove-Item -LiteralPath $temporaryPolicyPath -Force
        }
        $result.temporary_policy_file_removed = -not (Test-Path -LiteralPath $temporaryPolicyPath)

        $credentials = $null
        $sessionCall = $null
        $identityCall = $null
        $baselineCall = $null
        $putCall = $null
        $effectiveCall = $null
        $simulationCall = $null
        $deleteCall = $null
        $finalGetCall = $null
        $accountId = $null
        $principalArn = $null
        $simulationArguments = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        $result.ephemeral_credentials_cleared = $true

        if (
            $null -eq $operationFailure -and
            $result.baseline.temporary_policy_absent -and
            $result.grant.effective_document_verified -and
            $result.simulation.call_without_access_denied -and
            $result.rollback.removal_succeeded -and
            $result.rollback.temporary_policy_absent
        ) {
            $result.status = 'COMPLETE'
            $result.result = 'PASS_ATOMIC_SIMULATION_PERMISSION_VERIFIED_AND_REMOVED'
        } else {
            $result.status = 'BLOCKED'
            $result.failure_code = $operationFailure
            $result.result = if ($operationFailure -match '^BLOCKED_') { $operationFailure } else { 'BLOCKED_FAIL_CLOSED_OTHER' }
        }
        Write-PL003Evidence -Evidence $result -TargetPath $targetEvidencePath
    }

    return [pscustomobject]@{
        ExitCode = if ($result.result -eq 'PASS_ATOMIC_SIMULATION_PERMISSION_VERIFIED_AND_REMOVED') { 0 } else { 1 }
        Summary = [ordered]@{
            result = $result.result
            failure_code = $result.failure_code
            principal_verified_redacted = $result.principal.expected_bootstrap_principal_match
            baseline_absent = $result.baseline.temporary_policy_absent
            grant_verified = $result.grant.effective_document_verified
            simulation_without_access_denied = $result.simulation.call_without_access_denied
            rollback_verified = $result.rollback.temporary_policy_absent
            aws_calls = $result.aws_calls
            iam_mutations = $result.iam_mutations
            credentials_cleared = $result.ephemeral_credentials_cleared
            evidence_path = $targetEvidencePath.Substring($repositoryRoot.Length + 1).Replace('\', '/')
            secrets_printed = $false
        }
    }
}

if ($MyInvocation.InvocationName -eq '.') {
    return
}

if ($SyntheticTest -or -not $OperationalRun) {
    $testResult = Test-PL003AtomicSimulationPermissionCycle120
    $testResult | ConvertTo-Json -Depth 8
    if ($testResult.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003AtomicSimulationPermissionCycle120 `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber `
    -RequestedEvidencePath $EvidencePath
$outcome.Summary | ConvertTo-Json -Depth 8
exit $outcome.ExitCode
