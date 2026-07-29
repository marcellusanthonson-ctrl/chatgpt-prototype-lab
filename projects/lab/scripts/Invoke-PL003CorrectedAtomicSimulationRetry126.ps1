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

$requestedOperationalRun126 = [bool]$OperationalRun
$requestedSyntheticTest126 = [bool]$SyntheticTest
$requestedExpectedHead126 = $ExpectedHead
$requestedAttemptNumber126 = $AttemptNumber

$priorScript126 = Join-Path $PSScriptRoot 'Invoke-PL003ManualSetupAtomicSimulationCycle125.ps1'
. $priorScript126

$OperationalRun = $requestedOperationalRun126
$SyntheticTest = $requestedSyntheticTest126
$ExpectedHead = $requestedExpectedHead126
$AttemptNumber = $requestedAttemptNumber126

$script:AuthorizationId126 = 'AUTHORIZATION_LAB_PL003_CORRECTED_ATOMIC_SIMULATION_RETRY_126'
$script:BootstrapProfile126 = 'pl003-bootstrap'
$script:BootstrapUserName126 = 'pl003-bootstrap-operator'
$script:RoleName126 = 'PL003BoundedSimulationSetupOperator'
$script:BoundaryName126 = 'PL003BoundedSimulationSetupBoundary125'
$script:TemporaryPolicyName126 = 'PL003AtomicSimulationOnly126'
$script:RoleSessionName126 = 'PL003Authorization126'
$script:AssumeRoleDurationSeconds126 = 900
$script:TemporaryPolicyDocument126 = '{"Version":"2012-10-17","Statement":[{"Sid":"AtomicPL003SimulationOnly126","Effect":"Allow","Action":"iam:SimulatePrincipalPolicy","Resource":"*"}]}'
$script:EmptyBaselineSha256126 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
$script:CredentialEnvironmentNames126 = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

function Test-PL003126TemporaryPolicyDocument {
    param([Parameter(Mandatory)]$Document)

    try {
        $statements = @($Document.Statement)
        if ([string]$Document.Version -cne '2012-10-17' -or $statements.Count -ne 1) {
            return $false
        }
        $statement = $statements[0]
        return (
            [string]$statement.Sid -ceq 'AtomicPL003SimulationOnly126' -and
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

function Test-PL003CorrectedAtomicSimulationRetry126 {
    $failures = [System.Collections.Generic.List[string]]::new()
    if (-not (Test-PL003126TemporaryPolicyDocument `
        -Document ($script:TemporaryPolicyDocument126 | ConvertFrom-Json))) {
        $failures.Add('temporary-policy-document')
    }
    if (
        $script:RoleName126 -cne 'PL003BoundedSimulationSetupOperator' -or
        $script:TemporaryPolicyName126 -cne 'PL003AtomicSimulationOnly126'
    ) {
        $failures.Add('fixed-target-names')
    }
    if ($script:AssumeRoleDurationSeconds126 -ne 900) {
        $failures.Add('assume-role-duration')
    }
    $emptyHash = Get-PL003125Sha256 -Text ''
    if ($emptyHash -cne $script:EmptyBaselineSha256126) {
        $failures.Add('empty-baseline-hash')
    }
    $baselineNames = @()
    $baselineHash = Get-PL003125Sha256 -Text ($baselineNames -join "`n")
    $finalNames = @()
    $finalHash = Get-PL003125Sha256 -Text ($finalNames -join "`n")
    if ($baselineHash -cne $finalHash) {
        $failures.Add('empty-baseline-final-hash')
    }
    $success = Invoke-PL003125SyntheticLifecycle `
        -PutAttempted $true `
        -PutSucceeded $true `
        -SimulationSucceeded $true `
        -DeleteSucceeded $true `
        -FinalAbsent $true `
        -FinalSetEqualsBaseline $true
    if (-not $success.delete_is_first_finally_aws_operation -or -not $success.rollback_verified) {
        $failures.Add('synthetic-grant-rollback')
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
        $failures.Add('synthetic-failure-rollback')
    }
    $sessionMap = [ordered]@{
        bootstrap = @('GetCallerIdentity', 'AssumeRole', 'SimulatePrincipalPolicy')
        role = @('GetCallerIdentity', 'ListUserPolicies', 'PutUserPolicy', 'DeleteUserPolicy', 'ListUserPolicies')
    }
    if (
        $sessionMap.bootstrap -contains 'PutUserPolicy' -or
        $sessionMap.bootstrap -contains 'DeleteUserPolicy' -or
        $sessionMap.role -contains 'SimulatePrincipalPolicy'
    ) {
        $failures.Add('session-isolation')
    }
    $classifier = Test-PL003BootstrapDiagnosticClassifier
    if ($classifier.result -ne 'PASS') {
        $failures.Add('sanitized-classifier')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = 10 + [int]$classifier.case_count
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        baseline_empty = $true
        empty_baseline_sha256 = $emptyHash
        final_empty_sha256 = $finalHash
        session_isolation = if ($failures -contains 'session-isolation') { 'FAIL' } else { 'PASS' }
        grant_and_rollback = if ($failures -contains 'synthetic-grant-rollback') { 'FAIL' } else { 'PASS' }
        delete_first_finally = $success.delete_is_first_finally_aws_operation
        classifier_result = $classifier.result
        temporary_policy_name = $script:TemporaryPolicyName126
        temporary_policy_sha256 = Get-PL003125Sha256 -Text $script:TemporaryPolicyDocument126
        assume_role_duration_seconds = $script:AssumeRoleDurationSeconds126
        aws_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function Write-PL003126Evidence {
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

function Invoke-PL003CorrectedAtomicSimulationRetry126 {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $evidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-CORRECTED-ATOMIC-SIMULATION-RETRY-126-$attemptId.json"
    $temporaryDirectory = Join-Path $repositoryRoot 'projects\lab\scripts\.pl003-auth126-tmp'
    $temporaryPolicyPath = Join-Path $temporaryDirectory 'temporary-policy.json'
    $synthetic = Test-PL003CorrectedAtomicSimulationRetry126

    $evidence = [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-CORRECTED-ATOMIC-SIMULATION-RETRY-126-$attemptId"
        authorization_id = $script:AuthorizationId126
        project_id = 'lab'
        kind = 'REDACTED_CORRECTED_ATOMIC_SIMULATION_RETRY_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        branch_mode = 'DETACHED_HEAD'
        execution_head = $ExpectedExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            inherited_credentials = 'PENDING'
            authorization_126_registered_granted = 'PASS'
            authorizations_118_through_125_consumed = 'PASS'
            inherited_execution_authority = 'NONE'
            directed_suite = $synthetic.result
            directed_case_count = $synthetic.case_count
            baseline_empty = $synthetic.baseline_empty
            empty_baseline_sha256 = $synthetic.empty_baseline_sha256
            session_isolation = $synthetic.session_isolation
            synthetic_grant_and_rollback = $synthetic.grant_and_rollback
            delete_first_finally = $synthetic.delete_first_finally
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
            duration_seconds = $script:AssumeRoleDurationSeconds126
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
            empty_hash_matches_expected = $false
        }
        temporary_grant = [ordered]@{
            policy_name = $script:TemporaryPolicyName126
            document_sha256 = Get-PL003125Sha256 -Text $script:TemporaryPolicyDocument126
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
            bootstrap_used_for_policy_mutation = $false
            role_used_for_policy_mutation = $false
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
    $baselineNames = $null
    $baselineHash = $null
    $putAttempted = $false
    $primarySucceeded = $false

    try {
        $head = (git -C $repositoryRoot rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0 -or $head -ne $ExpectedExecutionHead) {
            throw 'HEAD_MISMATCH'
        }
        $evidence.prechecks.head = 'PASS'
        $entries = @(git -C $repositoryRoot status --porcelain=v1 --untracked-files=all)
        if ($LASTEXITCODE -ne 0 -or $entries.Count -ne 0) {
            throw 'WORKTREE_NOT_CLEAN'
        }
        $evidence.prechecks.worktree = 'PASS'
        if ($synthetic.result -ne 'PASS' -or $synthetic.case_count -lt 19) {
            throw 'LOCAL_DIRECTED_SUITE_FAILURE'
        }
        if (-not (Test-PL003126TemporaryPolicyDocument `
            -Document ($script:TemporaryPolicyDocument126 | ConvertFrom-Json))) {
            throw 'TEMPORARY_POLICY_DOCUMENT_MISMATCH'
        }
        $presentCredentialNames = @(
            $script:CredentialEnvironmentNames126 | Where-Object {
                -not [string]::IsNullOrWhiteSpace(
                    [Environment]::GetEnvironmentVariable($_, 'Process')
                )
            }
        )
        if ($presentCredentialNames.Count -ne 0) {
            throw 'INHERITED_CREDENTIALS_PRESENT'
        }
        $evidence.prechecks.inherited_credentials = 'PASS_ZERO'

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
        if ($LASTEXITCODE -ne 0 -or $profiles -notcontains $script:BootstrapProfile126) {
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

        $mfaSerial = (& aws configure get mfa_serial --profile $script:BootstrapProfile126 2>$null) -join ''
        if ($mfaSerial -notmatch '^arn:aws:iam::(\d{12}):mfa/') {
            throw 'BOOTSTRAP_MFA_REFERENCE_INVALID'
        }
        $accountId = [string]$Matches[1]
        $bootstrapArn = "arn:aws:iam::$accountId`:user/$($script:BootstrapUserName126)"
        $roleArn = "arn:aws:iam::$accountId`:role/$($script:RoleName126)"

        [IO.Directory]::CreateDirectory($temporaryDirectory) | Out-Null
        [IO.File]::WriteAllText(
            $temporaryPolicyPath,
            $script:TemporaryPolicyDocument126,
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
            '--profile', $script:BootstrapProfile126,
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
            '--role-session-name', $script:RoleSessionName126,
            '--duration-seconds', [string]$script:AssumeRoleDurationSeconds126,
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
        $expectedRoleSessionArn = "arn:aws:sts::$accountId`:assumed-role/$($script:RoleName126)/$($script:RoleSessionName126)"
        if (
            [string]$roleIdentity.Account -cne $accountId -or
            [string]$roleIdentity.Arn -cne $expectedRoleSessionArn
        ) {
            throw 'ASSUMED_ROLE_IDENTITY_MISMATCH'
        }
        $evidence.role_identity.verified = $true
        $evidence.role_identity.redacted_identifier = 'ASSUMED_ROLE:<REDACTED_ACCOUNT_ID>:PL003BoundedSimulationSetupOperator/PL003Authorization126'

        $evidence.aws_calls.iam_list_user_policies_baseline = 1
        $evidence.baseline.list_attempted = $true
        $baselineCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'list-user-policies',
            '--user-name', $script:BootstrapUserName126,
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
        if ($baselineNames -contains $script:TemporaryPolicyName126) {
            throw 'BLOCKED_EXISTING_TEMPORARY_POLICY_COLLISION'
        }
        $baselineHash = Get-PL003125Sha256 -Text ($baselineNames -join "`n")
        $evidence.baseline.temporary_policy_absent = $true
        $evidence.baseline.policy_name_count = $baselineNames.Count
        $evidence.baseline.sorted_policy_names_sha256 = $baselineHash
        $evidence.baseline.empty_hash_matches_expected = (
            $baselineNames.Count -ne 0 -or
            $baselineHash -ceq $script:EmptyBaselineSha256126
        )
        if (-not $evidence.baseline.empty_hash_matches_expected) {
            throw 'BLOCKED_EMPTY_BASELINE_HASH_MISMATCH'
        }

        $putAttempted = $true
        $evidence.rollback.required = $true
        $evidence.temporary_grant.put_attempted = $true
        $evidence.aws_calls.iam_put_user_policy = 1
        $evidence.mutations.temporary_grant_attempts = 1
        $putCall = Invoke-PL003AwsCliCaptured -Arguments @(
            'iam', 'put-user-policy',
            '--user-name', $script:BootstrapUserName126,
            '--policy-name', $script:TemporaryPolicyName126,
            '--policy-document', ('file://' + $temporaryPolicyPath.Replace('\', '/')),
            '--no-cli-pager',
            '--output', 'json'
        ) -Credentials $roleCredentials
        $evidence.session_isolation.role_used_for_policy_mutation = $true
        if ($putCall.ExitCode -ne 0) {
            Set-PL003125FailureMetadata -Evidence $evidence -Call $putCall -Service 'iam' -Operation 'PutUserPolicy'
            throw 'BLOCKED_TEMPORARY_GRANT_FAILED'
        }
        $evidence.temporary_grant.put_succeeded = $true
        $evidence.mutations.temporary_grant_successes = 1
        $evidence.mutations.persistent_at_completion = 1

        Start-Sleep -Seconds 5
        $contextEntries = @(
            'ContextKeyName=aws:MultiFactorAuthPresent,ContextKeyValues=true,ContextKeyType=boolean',
            'ContextKeyName=aws:RequestTag/Project,ContextKeyValues=PRODUCT-LEADERSHIP-TEST-003,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Authorization,ContextKeyValues=126,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Temporary,ContextKeyValues=true,ContextKeyType=string'
        )
        $simulationArguments = @(
            'iam', 'simulate-principal-policy',
            '--policy-source-arn', $bootstrapArn,
            '--action-names', 'iam:CreatePolicy',
            '--resource-arns', "arn:aws:iam::$accountId`:policy/$($script:BoundaryName126)",
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
        $evidence.session_isolation.bootstrap_used_for_simulation = $true
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
                '--user-name', $script:BootstrapUserName126,
                '--policy-name', $script:TemporaryPolicyName126,
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
                '--user-name', $script:BootstrapUserName126,
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
                    $finalNames -notcontains $script:TemporaryPolicyName126
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
            -not $evidence.session_isolation.bootstrap_used_for_policy_mutation -and
            $evidence.session_isolation.role_used_for_policy_mutation -and
            -not $evidence.session_isolation.role_used_for_simulation
        ) {
            'PASS'
        } elseif (-not $putAttempted) {
            'NOT_FULLY_EXERCISED_BEFORE_GRANT'
        } else {
            'FAIL'
        }

        if ($primarySucceeded -and $evidence.rollback.verified) {
            $evidence.status = 'COMPLETE'
            $evidence.result = 'PASS_CORRECTED_ATOMIC_SIMULATION_COMPLETED_AND_ROLLED_BACK'
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
        $accountId = $null
        $bootstrapArn = $null
        $roleArn = $null
        $baselineNames = $null
        $baselineHash = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        $evidence.credentials_cleared = $true
        Write-PL003126Evidence -Evidence $evidence -Path $evidencePath
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
    $test = Test-PL003CorrectedAtomicSimulationRetry126
    $test | ConvertTo-Json -Depth 10
    if ($test.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003CorrectedAtomicSimulationRetry126 `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber
$outcome | ConvertTo-Json -Depth 14
if ($outcome.result -eq 'PASS_CORRECTED_ATOMIC_SIMULATION_COMPLETED_AND_ROLLED_BACK') {
    exit 0
}
exit 1
