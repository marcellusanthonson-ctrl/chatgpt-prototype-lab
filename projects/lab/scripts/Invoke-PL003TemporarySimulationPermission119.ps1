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

$requestedOperationalRun119 = [bool]$OperationalRun
$requestedSyntheticTest119 = [bool]$SyntheticTest
$requestedExpectedHead119 = $ExpectedHead
$requestedAttemptNumber119 = $AttemptNumber
$requestedEvidencePath119 = $EvidencePath

$diagnosticScript = Join-Path $PSScriptRoot 'Invoke-PL003BootstrapDiagnosticPreflight.ps1'
. $diagnosticScript

$OperationalRun = $requestedOperationalRun119
$SyntheticTest = $requestedSyntheticTest119
$ExpectedHead = $requestedExpectedHead119
$AttemptNumber = $requestedAttemptNumber119
$EvidencePath = $requestedEvidencePath119

$script:AuthorizationId119 = 'AUTHORIZATION_LAB_PL003_TEMPORARY_SIMULATION_PERMISSION_119'
$script:TemporaryPolicyName119 = 'PL003TemporarySimulationOnly119'
$script:TemporaryPolicyDocument119 = '{"Version":"2012-10-17","Statement":[{"Sid":"TemporaryPL003SimulationOnly","Effect":"Allow","Action":"iam:SimulatePrincipalPolicy","Resource":"*"}]}'

function Get-PL003Sha256Text {
    param([Parameter(Mandatory)][string]$Text)

    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
        return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Get-PL003InlinePolicySetFingerprint {
    param([Parameter(Mandatory)][object[]]$PolicyNames)

    $ordered = @($PolicyNames | ForEach-Object { [string]$_ } | Sort-Object -CaseSensitive)
    return [ordered]@{
        count = $ordered.Count
        sha256 = Get-PL003Sha256Text -Text ($ordered -join "`n")
        temporary_policy_present = $ordered -contains $script:TemporaryPolicyName119
    }
}

function Test-PL003AuthorizedPolicyDocument {
    param([Parameter(Mandatory)]$PolicyDocument)

    try {
        $version = [string]$PolicyDocument.Version
        $statements = @($PolicyDocument.Statement)
        if ($version -ne '2012-10-17' -or $statements.Count -ne 1) {
            return $false
        }
        $statement = $statements[0]
        $actions = @($statement.Action)
        $resources = @($statement.Resource)
        return (
            [string]$statement.Sid -eq 'TemporaryPL003SimulationOnly' -and
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

function Invoke-PL003119SyntheticLifecycle {
    param(
        [bool]$GrantSucceeds,
        [bool]$EffectiveDocumentMatches,
        [bool]$SimulationSucceeds
    )

    $grantAttempts = 0
    $grantSuccesses = 0
    $deleteAttempts = 0
    $deleteSuccesses = 0
    $created = $false
    try {
        $grantAttempts++
        if (-not $GrantSucceeds) {
            throw 'GRANT_FAILED'
        }
        $grantSuccesses++
        $created = $true
        if (-not $EffectiveDocumentMatches) {
            throw 'EFFECTIVE_DOCUMENT_MISMATCH'
        }
        if (-not $SimulationSucceeds) {
            throw 'SIMULATION_FAILED'
        }
    } catch {
        # Synthetic failures are expected inputs to the rollback-state test.
    } finally {
        if ($created) {
            $deleteAttempts++
            $deleteSuccesses++
            $created = $false
        }
    }
    return [ordered]@{
        grant_attempts = $grantAttempts
        grant_successes = $grantSuccesses
        delete_attempts = $deleteAttempts
        delete_successes = $deleteSuccesses
        temporary_policy_present = $created
    }
}

function Test-PL003TemporarySimulationPermission119 {
    $failures = [System.Collections.Generic.List[string]]::new()
    $baseClassifier = Test-PL003BootstrapDiagnosticClassifier
    if ($baseClassifier.result -ne 'PASS') {
        $failures.Add('sanitized-classifier')
    }

    $expectedDocument = $script:TemporaryPolicyDocument119 | ConvertFrom-Json
    if (-not (Test-PL003AuthorizedPolicyDocument -PolicyDocument $expectedDocument)) {
        $failures.Add('authorized-document')
    }
    $extraActionDocument = '{"Version":"2012-10-17","Statement":[{"Sid":"TemporaryPL003SimulationOnly","Effect":"Allow","Action":["iam:SimulatePrincipalPolicy","iam:SimulateCustomPolicy"],"Resource":"*"}]}' | ConvertFrom-Json
    if (Test-PL003AuthorizedPolicyDocument -PolicyDocument $extraActionDocument) {
        $failures.Add('extra-action-rejection')
    }

    $grantFailure = Invoke-PL003119SyntheticLifecycle -GrantSucceeds $false -EffectiveDocumentMatches $false -SimulationSucceeds $false
    if ($grantFailure.delete_attempts -ne 0 -or $grantFailure.temporary_policy_present) {
        $failures.Add('grant-failure-state')
    }

    $documentFailure = Invoke-PL003119SyntheticLifecycle -GrantSucceeds $true -EffectiveDocumentMatches $false -SimulationSucceeds $false
    if ($documentFailure.delete_attempts -ne 1 -or $documentFailure.delete_successes -ne 1 -or $documentFailure.temporary_policy_present) {
        $failures.Add('document-failure-rollback')
    }

    $simulationFailure = Invoke-PL003119SyntheticLifecycle -GrantSucceeds $true -EffectiveDocumentMatches $true -SimulationSucceeds $false
    if ($simulationFailure.delete_attempts -ne 1 -or $simulationFailure.delete_successes -ne 1 -or $simulationFailure.temporary_policy_present) {
        $failures.Add('simulation-failure-rollback')
    }

    $success = Invoke-PL003119SyntheticLifecycle -GrantSucceeds $true -EffectiveDocumentMatches $true -SimulationSucceeds $true
    if (
        $success.grant_attempts -ne 1 -or
        $success.grant_successes -ne 1 -or
        $success.delete_attempts -ne 1 -or
        $success.delete_successes -ne 1 -or
        $success.temporary_policy_present
    ) {
        $failures.Add('successful-lifecycle')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = $baseClassifier.case_count + 5
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        authorized_policy_sha256 = Get-PL003Sha256Text -Text $script:TemporaryPolicyDocument119
        exact_action = 'iam:SimulatePrincipalPolicy'
        additional_actions = 0
        rollback_after_successful_grant = if ($failures -contains 'document-failure-rollback' -or $failures -contains 'simulation-failure-rollback' -or $failures -contains 'successful-lifecycle') { 'FAIL' } else { 'PASS' }
        aws_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function New-PL003119Evidence {
    param(
        [Parameter(Mandatory)][string]$ExecutionHead,
        [Parameter(Mandatory)][string]$AttemptId,
        [Parameter(Mandatory)]$SyntheticResult
    )

    return [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-TEMPORARY-SIMULATION-PERMISSION-119-$AttemptId"
        attempt_id = $AttemptId
        authorization_id = $script:AuthorizationId119
        project_id = 'lab'
        kind = 'REDACTED_TEMPORARY_IAM_PERMISSION_LIFECYCLE_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        branch_mode = 'DETACHED_HEAD'
        execution_head = $ExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            authorization_118_consumed = 'PASS'
            active_execution_authority_before_119 = 'NONE'
            aws_cli = 'PENDING'
            cli_history_disabled = 'PENDING'
            inherited_temporary_credentials_absent = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
            bootstrap_profile = 'PENDING'
            region = 'PENDING'
            mfa_reference = 'PENDING'
            synthetic_classifier_and_lifecycle = $SyntheticResult.result
            rollback_implementation = $SyntheticResult.rollback_after_successful_grant
        }
        principal = [ordered]@{
            expected_bootstrap_principal_match = $false
            principal_type = 'IAM_USER'
            principal_identifier = 'REDACTED'
            full_arn_included = $false
            full_account_id_included = $false
        }
        baseline = [ordered]@{
            source_denial_evidence = 'projects/lab/evidence/EVD-LAB-PL003-AWS-DIAGNOSTIC-PREFLIGHT-118-ATTEMPT-003.json'
            prior_simulation_classification = 'SIMULATION_ACTION_NOT_AUTHORIZED'
            inline_policy_set = $null
            temporary_policy_absent = $false
        }
        grant = [ordered]@{
            mechanism = 'INLINE_USER_POLICY'
            policy_name = $script:TemporaryPolicyName119
            policy_document_sha256 = Get-PL003Sha256Text -Text $script:TemporaryPolicyDocument119
            authorized_action = 'iam:SimulatePrincipalPolicy'
            additional_actions = 0
            mutation_attempted = $false
            mutation_succeeded = $false
            effective_document_verified = $false
            sanitized_call_metadata = $null
        }
        simulation = [ordered]@{
            tested_action = 'iam:CreatePolicy'
            tested_resource_shape = 'IAM_POLICY_PL003_SETUP_BOUNDARY'
            positive_call_attempted = $false
            positive_call_without_access_denied = $false
            evaluation_decision = $null
            sanitized_call_metadata = $null
        }
        rollback = [ordered]@{
            removal_attempted = $false
            removal_succeeded = $false
            temporary_policy_absent = $false
            final_inline_policy_set = $null
            final_configuration_matches_baseline = $false
            negative_call_attempted = $false
            negative_call_access_denied = $false
            sanitized_removal_metadata = $null
            sanitized_negative_call_metadata = $null
        }
        aws_calls = [ordered]@{
            sts_get_session_token = 0
            sts_get_caller_identity = 0
            iam_list_user_policies = 0
            iam_get_user_policy = 0
            iam_simulate_principal_policy = 0
            other_iam_reads = 0
            other_aws = 0
        }
        iam_mutations = [ordered]@{
            grant_attempts = 0
            grant_successes = 0
            removal_attempts = 0
            removal_successes = 0
            unexpected = 0
        }
        zero_other_mutation_attestation = [ordered]@{
            aws_infrastructure_mutations = 0
            terraform_executions = 0
            product_leadership_test_003_executions = 0
            product_leadership_active = $false
            product_leadership_integrated = $false
            aws_resources_created = 0
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

function Invoke-PL003TemporarySimulationPermission119 {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber,
        [AllowNull()][string]$RequestedEvidencePath
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $defaultEvidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-TEMPORARY-SIMULATION-PERMISSION-119-$attemptId.json"
    $targetEvidencePath = if ([string]::IsNullOrWhiteSpace($RequestedEvidencePath)) {
        $defaultEvidencePath
    } else {
        [IO.Path]::GetFullPath($RequestedEvidencePath)
    }
    $authorizedEvidenceRoot = Join-Path $repositoryRoot 'projects\lab\evidence'
    if (-not $targetEvidencePath.StartsWith($authorizedEvidenceRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'EVIDENCE_PATH_OUTSIDE_AUTHORIZED_DIRECTORY'
    }

    $syntheticResult = Test-PL003TemporarySimulationPermission119
    $result = New-PL003119Evidence -ExecutionHead $ExpectedExecutionHead -AttemptId $attemptId -SyntheticResult $syntheticResult
    $temporaryPolicyPath = Join-Path $PSScriptRoot ('.pl003-119-policy-{0}.json' -f $PID)

    $secureMfa = $null
    $mfaPointer = [IntPtr]::Zero
    $mfaCode = $null
    $sessionCall = $null
    $sessionDocument = $null
    $credentials = $null
    $identityCall = $null
    $identityDocument = $null
    $baselineCall = $null
    $baselineDocument = $null
    $grantCall = $null
    $effectiveCall = $null
    $effectiveDocument = $null
    $positiveCall = $null
    $removalCall = $null
    $finalCall = $null
    $finalDocument = $null
    $negativeCall = $null
    $policyCreated = $false
    $accountId = $null
    $principalArn = $null
    $resourceArn = $null
    $operationFailure = $null

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

        if ($syntheticResult.result -ne 'PASS' -or $syntheticResult.rollback_after_successful_grant -ne 'PASS') {
            throw 'LOCAL_SYNTHETIC_OR_ROLLBACK_TEST_FAILED'
        }

        if ($null -eq (Get-Command aws -ErrorAction SilentlyContinue)) {
            throw 'AWS_CLI_NOT_AVAILABLE'
        }
        $result.prechecks.aws_cli = 'PASS'

        if ([Environment]::GetEnvironmentVariable('AWS_CLI_HISTORY', 'Process') -eq 'enabled') {
            throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
        }
        $profiles = @(& aws configure list-profiles 2>$null)
        if ($LASTEXITCODE -ne 0) {
            throw 'AWS_PROFILE_LIST_FAILED'
        }
        if ((& aws configure get cli_history 2>$null) -eq 'enabled') {
            throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
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
            $result.grant.sanitized_call_metadata = Get-PL003SanitizedCallMetadata -ExitCode $sessionCall.ExitCode -StdErr $sessionCall.RawStdErr -Service 'sts' -Operation 'GetSessionToken'
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

        $result.aws_calls.iam_list_user_policies++
        $baselineCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'list-user-policies',
            '--user-name', $script:ExpectedBootstrapPrincipal,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $credentials
        if ($baselineCall.ExitCode -ne 0) {
            throw 'BASELINE_INLINE_POLICY_LIST_FAILED'
        }
        $baselineDocument = $baselineCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $baselineFingerprint = Get-PL003InlinePolicySetFingerprint -PolicyNames @($baselineDocument.PolicyNames)
        $result.baseline.inline_policy_set = $baselineFingerprint
        if ($baselineFingerprint.temporary_policy_present) {
            throw 'BLOCKED_EXISTING_POLICY_COLLISION'
        }
        $result.baseline.temporary_policy_absent = $true

        $policyBytes = [Text.UTF8Encoding]::new($false).GetBytes($script:TemporaryPolicyDocument119)
        $policyStream = [IO.File]::Open($temporaryPolicyPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try {
            $policyStream.Write($policyBytes, 0, $policyBytes.Length)
        } finally {
            $policyStream.Dispose()
        }

        $result.grant.mutation_attempted = $true
        $result.iam_mutations.grant_attempts = 1
        $grantCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'put-user-policy',
            '--user-name', $script:ExpectedBootstrapPrincipal,
            '--policy-name', $script:TemporaryPolicyName119,
            '--policy-document', ('file://' + $temporaryPolicyPath),
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $credentials
        $result.grant.sanitized_call_metadata = Get-PL003SanitizedCallMetadata -ExitCode $grantCall.ExitCode -StdErr $grantCall.RawStdErr -Service 'iam' -Operation 'PutUserPolicy'
        if ($grantCall.ExitCode -ne 0) {
            if ((Get-PL003AwsErrorCode -StdErr $grantCall.RawStdErr) -match 'AccessDenied|Unauthorized') {
                throw 'BLOCKED_PERMISSION_GRANT_NOT_AUTHORIZED'
            }
            throw 'TEMPORARY_PERMISSION_GRANT_FAILED'
        }
        $policyCreated = $true
        $result.grant.mutation_succeeded = $true
        $result.iam_mutations.grant_successes = 1

        $result.aws_calls.iam_get_user_policy = 1
        $effectiveCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'get-user-policy',
            '--user-name', $script:ExpectedBootstrapPrincipal,
            '--policy-name', $script:TemporaryPolicyName119,
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $credentials
        if ($effectiveCall.ExitCode -ne 0) {
            throw 'TEMPORARY_POLICY_EFFECTIVE_DOCUMENT_READ_FAILED'
        }
        $effectiveDocument = $effectiveCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        if (-not (Test-PL003AuthorizedPolicyDocument -PolicyDocument $effectiveDocument.PolicyDocument)) {
            throw 'EFFECTIVE_POLICY_DOCUMENT_MISMATCH'
        }
        $result.grant.effective_document_verified = $true

        $resourceArn = "arn:aws:iam::$accountId`:policy/PL003IAMSetupBoundary114"
        $contextEntries = @(
            'ContextKeyName=aws:MultiFactorAuthPresent,ContextKeyValues=true,ContextKeyType=boolean',
            'ContextKeyName=aws:RequestTag/Project,ContextKeyValues=PRODUCT-LEADERSHIP-TEST-003,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Authorization,ContextKeyValues=119,ContextKeyType=string',
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

        $result.simulation.positive_call_attempted = $true
        $result.aws_calls.iam_simulate_principal_policy++
        $positiveCall = Invoke-PL003AwsCliCaptured -Arguments $simulationArguments -Credentials $credentials
        $result.simulation.sanitized_call_metadata = Get-PL003SanitizedCallMetadata -ExitCode $positiveCall.ExitCode -StdErr $positiveCall.RawStdErr -Service 'iam' -Operation 'SimulatePrincipalPolicy'
        if ($positiveCall.ExitCode -ne 0) {
            if ((Get-PL003AwsErrorCode -StdErr $positiveCall.RawStdErr) -match 'AccessDenied|Unauthorized') {
                throw 'BLOCKED_SIMULATION_STILL_ACCESS_DENIED'
            }
            throw 'POSITIVE_SIMULATION_FAILED_OTHER'
        }
        $positiveDocument = $positiveCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $decision = [string]$positiveDocument.EvaluationResults[0].EvalDecision
        if ($decision -notin @('allowed', 'implicitDeny', 'explicitDeny')) {
            throw 'POSITIVE_SIMULATION_DECISION_INVALID'
        }
        $result.simulation.positive_call_without_access_denied = $true
        $result.simulation.evaluation_decision = $decision
    } catch {
        $operationFailure = [string]$_.Exception.Message
    } finally {
        if ($policyCreated -and $null -ne $credentials) {
            $result.rollback.removal_attempted = $true
            $result.iam_mutations.removal_attempts = 1
            $removalCall = Invoke-PL003AwsCliCaptured -Arguments @(
                'iam', 'delete-user-policy',
                '--user-name', $script:ExpectedBootstrapPrincipal,
                '--policy-name', $script:TemporaryPolicyName119,
                '--no-cli-pager',
                '--output', 'json'
            ) -Credentials $credentials
            $result.rollback.sanitized_removal_metadata = Get-PL003SanitizedCallMetadata -ExitCode $removalCall.ExitCode -StdErr $removalCall.RawStdErr -Service 'iam' -Operation 'DeleteUserPolicy'
            if ($removalCall.ExitCode -eq 0) {
                $policyCreated = $false
                $result.rollback.removal_succeeded = $true
                $result.iam_mutations.removal_successes = 1
            } else {
                $operationFailure = 'BLOCKED_ROLLBACK_NOT_VERIFIED'
            }
        }

        if ($null -ne $credentials -and $null -ne $baselineDocument) {
            $result.aws_calls.iam_list_user_policies++
            $finalCall = Invoke-PL003AwsCliCaptured -Arguments @(
                'iam', 'list-user-policies',
                '--user-name', $script:ExpectedBootstrapPrincipal,
                '--no-cli-pager',
                '--output', 'json'
            ) -Credentials $credentials
            if ($finalCall.ExitCode -eq 0) {
                $finalDocument = $finalCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
                $finalFingerprint = Get-PL003InlinePolicySetFingerprint -PolicyNames @($finalDocument.PolicyNames)
                $result.rollback.final_inline_policy_set = $finalFingerprint
                $result.rollback.temporary_policy_absent = -not $finalFingerprint.temporary_policy_present
                $result.rollback.final_configuration_matches_baseline = (
                    $result.baseline.inline_policy_set.count -eq $finalFingerprint.count -and
                    $result.baseline.inline_policy_set.sha256 -eq $finalFingerprint.sha256 -and
                    -not $finalFingerprint.temporary_policy_present
                )
                if (-not $result.rollback.final_configuration_matches_baseline) {
                    $operationFailure = 'BLOCKED_ROLLBACK_NOT_VERIFIED'
                }
            } else {
                $operationFailure = 'BLOCKED_ROLLBACK_NOT_VERIFIED'
            }
        }

        if (
            $null -eq $operationFailure -and
            $result.simulation.positive_call_without_access_denied -and
            $result.rollback.final_configuration_matches_baseline
        ) {
            $result.rollback.negative_call_attempted = $true
            $result.aws_calls.iam_simulate_principal_policy++
            $negativeCall = Invoke-PL003AwsCliCaptured -Arguments $simulationArguments -Credentials $credentials
            $result.rollback.sanitized_negative_call_metadata = Get-PL003SanitizedCallMetadata -ExitCode $negativeCall.ExitCode -StdErr $negativeCall.RawStdErr -Service 'iam' -Operation 'SimulatePrincipalPolicy'
            $negativeError = Get-PL003AwsErrorCode -StdErr $negativeCall.RawStdErr
            if ($negativeCall.ExitCode -ne 0 -and $negativeError -match 'AccessDenied|Unauthorized') {
                $result.rollback.negative_call_access_denied = $true
            } else {
                $operationFailure = 'BLOCKED_ROLLBACK_NOT_VERIFIED'
            }
        }

        if ($mfaPointer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($mfaPointer)
            $mfaPointer = [IntPtr]::Zero
        }
        $secureMfa = $null
        $mfaCode = $null

        if (Test-Path -LiteralPath $temporaryPolicyPath -PathType Leaf) {
            Remove-Item -LiteralPath $temporaryPolicyPath -Force
        }
        $result.temporary_policy_file_removed = -not (Test-Path -LiteralPath $temporaryPolicyPath)

        $sessionCall = $null
        $sessionDocument = $null
        $credentials = $null
        $identityCall = $null
        $identityDocument = $null
        $baselineCall = $null
        $baselineDocument = $null
        $grantCall = $null
        $effectiveCall = $null
        $effectiveDocument = $null
        $positiveCall = $null
        $removalCall = $null
        $finalCall = $null
        $finalDocument = $null
        $negativeCall = $null
        $accountId = $null
        $principalArn = $null
        $resourceArn = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        $result.ephemeral_credentials_cleared = $true

        if ($null -eq $operationFailure) {
            $result.status = 'COMPLETE'
            $result.result = 'PASS_TEMPORARY_SIMULATION_PERMISSION_VERIFIED_AND_REMOVED'
        } else {
            if ($operationFailure -in @(
                'BLOCKED_PERMISSION_GRANT_NOT_AUTHORIZED',
                'BLOCKED_PRINCIPAL_MISMATCH',
                'BLOCKED_EXISTING_POLICY_COLLISION',
                'BLOCKED_SIMULATION_STILL_ACCESS_DENIED',
                'BLOCKED_ROLLBACK_NOT_VERIFIED'
            )) {
                $result.result = $operationFailure
            } else {
                $result.result = 'BLOCKED_FAIL_CLOSED_OTHER'
            }
            $result.failure_code = $operationFailure
            $result.status = 'BLOCKED'
        }

        Write-PL003Evidence -Evidence $result -TargetPath $targetEvidencePath
    }

    $summary = [ordered]@{
        result = $result.result
        failure_code = $result.failure_code
        principal_verified_redacted = $result.principal.expected_bootstrap_principal_match
        positive_simulation_without_access_denied = $result.simulation.positive_call_without_access_denied
        rollback_verified = $result.rollback.final_configuration_matches_baseline
        aws_calls = $result.aws_calls
        iam_mutations = $result.iam_mutations
        ephemeral_credentials_cleared = $result.ephemeral_credentials_cleared
        evidence_path = $targetEvidencePath.Substring($repositoryRoot.Length + 1).Replace('\', '/')
        secrets_printed = $false
    }
    return [pscustomobject]@{
        ExitCode = if ($result.result -eq 'PASS_TEMPORARY_SIMULATION_PERMISSION_VERIFIED_AND_REMOVED') { 0 } else { 1 }
        Summary = $summary
    }
}

if ($MyInvocation.InvocationName -eq '.') {
    return
}

if ($SyntheticTest -or -not $OperationalRun) {
    $testResult = Test-PL003TemporarySimulationPermission119
    $testResult | ConvertTo-Json -Depth 8
    if ($testResult.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003TemporarySimulationPermission119 `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber `
    -RequestedEvidencePath $EvidencePath
$outcome.Summary | ConvertTo-Json -Depth 8
exit $outcome.ExitCode
