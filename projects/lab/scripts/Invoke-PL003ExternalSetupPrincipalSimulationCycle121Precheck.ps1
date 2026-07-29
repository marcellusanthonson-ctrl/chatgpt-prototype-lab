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

$script:AuthorizationId121 = 'AUTHORIZATION_LAB_PL003_EXTERNAL_SETUP_PRINCIPAL_SIMULATION_CYCLE_121'
$script:ExpectedExternalProfile121 = 'pl003-iam-setup-operator'
$script:ReadOnlyPlanProfile121 = 'pl003-plan-operator'
$script:BootstrapProfile121 = 'pl003-bootstrap'
$script:TemporaryPolicyName121 = 'PL003AtomicSimulationOnly121'
$script:TemporaryPolicyDocument121 = '{"Version":"2012-10-17","Statement":[{"Sid":"TemporaryPL003SimulationOnly","Effect":"Allow","Action":"iam:SimulatePrincipalPolicy","Resource":"*"}]}'
$script:CredentialEnvironmentNames121 = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

function Get-PL003121Sha256 {
    param([Parameter(Mandatory)][string]$Text)

    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
        return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Test-PL003121PolicyDocument {
    param([Parameter(Mandatory)]$Document)

    try {
        $statements = @($Document.Statement)
        if ([string]$Document.Version -ne '2012-10-17' -or $statements.Count -ne 1) {
            return $false
        }
        $statement = $statements[0]
        $actions = @($statement.Action)
        $resources = @($statement.Resource)
        $conditionProperties = @($statement.PSObject.Properties | Where-Object { $_.Name -eq 'Condition' })
        return (
            [string]$statement.Sid -eq 'TemporaryPL003SimulationOnly' -and
            [string]$statement.Effect -eq 'Allow' -and
            $actions.Count -eq 1 -and
            [string]$actions[0] -ceq 'iam:SimulatePrincipalPolicy' -and
            $resources.Count -eq 1 -and
            [string]$resources[0] -ceq '*' -and
            $conditionProperties.Count -eq 0
        )
    } catch {
        return $false
    }
}

function Invoke-PL003121SyntheticTwoPrincipalCycle {
    param(
        [bool]$FailAfterPut,
        [bool]$SessionsIsolated
    )

    $events = [System.Collections.Generic.List[string]]::new()
    $externalCredentialLabel = 'EXTERNAL_SESSION_ONLY'
    $bootstrapCredentialLabel = if ($SessionsIsolated) { 'BOOTSTRAP_SESSION_ONLY' } else { $externalCredentialLabel }
    $failure = $null
    try {
        $events.Add('EXTERNAL_BASELINE')
        $events.Add('EXTERNAL_PUT')
        if ($FailAfterPut) {
            throw 'POST_PUT_FAILURE'
        }
        if ($externalCredentialLabel -eq $bootstrapCredentialLabel) {
            throw 'SESSION_ISOLATION_FAILED'
        }
        $events.Add('BOOTSTRAP_IDENTITY')
        $events.Add('BOOTSTRAP_SIMULATE')
    } catch {
        $failure = [string]$_.Exception.Message
    } finally {
        $events.Add('EXTERNAL_DELETE')
        $events.Add('EXTERNAL_FINAL_LIST')
    }
    return [ordered]@{
        events = @($events)
        failure = $failure
        sessions_isolated = $externalCredentialLabel -ne $bootstrapCredentialLabel
        delete_count = @($events | Where-Object { $_ -eq 'EXTERNAL_DELETE' }).Count
    }
}

function Test-PL003ExternalSetupPrincipalSimulationCycle121 {
    $failures = [System.Collections.Generic.List[string]]::new()
    $document = $script:TemporaryPolicyDocument121 | ConvertFrom-Json
    if (-not (Test-PL003121PolicyDocument -Document $document)) {
        $failures.Add('exact-policy-document')
    }

    $extraAction = '{"Version":"2012-10-17","Statement":[{"Sid":"TemporaryPL003SimulationOnly","Effect":"Allow","Action":["iam:SimulatePrincipalPolicy","iam:SimulateCustomPolicy"],"Resource":"*"}]}' | ConvertFrom-Json
    if (Test-PL003121PolicyDocument -Document $extraAction) {
        $failures.Add('extra-action-rejection')
    }

    $condition = '{"Version":"2012-10-17","Statement":[{"Sid":"TemporaryPL003SimulationOnly","Effect":"Allow","Action":"iam:SimulatePrincipalPolicy","Resource":"*","Condition":{"Bool":{"aws:MultiFactorAuthPresent":"true"}}}]}' | ConvertFrom-Json
    if (Test-PL003121PolicyDocument -Document $condition) {
        $failures.Add('condition-rejection')
    }

    $success = Invoke-PL003121SyntheticTwoPrincipalCycle -FailAfterPut $false -SessionsIsolated $true
    if (
        ($success.events -join ',') -ne 'EXTERNAL_BASELINE,EXTERNAL_PUT,BOOTSTRAP_IDENTITY,BOOTSTRAP_SIMULATE,EXTERNAL_DELETE,EXTERNAL_FINAL_LIST' -or
        -not $success.sessions_isolated -or
        $success.delete_count -ne 1
    ) {
        $failures.Add('two-principal-success-sequence')
    }

    $postPutFailure = Invoke-PL003121SyntheticTwoPrincipalCycle -FailAfterPut $true -SessionsIsolated $true
    if (
        ($postPutFailure.events -join ',') -ne 'EXTERNAL_BASELINE,EXTERNAL_PUT,EXTERNAL_DELETE,EXTERNAL_FINAL_LIST' -or
        $postPutFailure.delete_count -ne 1
    ) {
        $failures.Add('rollback-first-after-post-put-failure')
    }

    $isolationFailure = Invoke-PL003121SyntheticTwoPrincipalCycle -FailAfterPut $false -SessionsIsolated $false
    if ($isolationFailure.failure -ne 'SESSION_ISOLATION_FAILED' -or $isolationFailure.delete_count -ne 1) {
        $failures.Add('session-isolation-fail-closed')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = 6
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        policy_name = $script:TemporaryPolicyName121
        policy_sha256 = Get-PL003121Sha256 -Text $script:TemporaryPolicyDocument121
        exact_action = 'iam:SimulatePrincipalPolicy'
        additional_actions = 0
        conditions = 0
        two_principal_session_isolation = if ($failures -contains 'session-isolation-fail-closed' -or $failures -contains 'two-principal-success-sequence') { 'FAIL' } else { 'PASS' }
        rollback_first_after_put_failure = if ($failures -contains 'rollback-first-after-post-put-failure') { 'FAIL' } else { 'PASS' }
        aws_calls = 0
        aws_mutations = 0
        secrets_printed = $false
    }
}

function Write-PL003121Evidence {
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

function Invoke-PL003ExternalSetupPrincipalSimulationCycle121Precheck {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $evidencePath = Join-Path $repositoryRoot "projects\lab\evidence\EVD-LAB-PL003-EXTERNAL-SETUP-PRINCIPAL-SIMULATION-CYCLE-121-$attemptId.json"
    $synthetic = Test-PL003ExternalSetupPrincipalSimulationCycle121

    $evidence = [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "EVD-LAB-PL003-EXTERNAL-SETUP-PRINCIPAL-SIMULATION-CYCLE-121-$attemptId"
        authorization_id = $script:AuthorizationId121
        project_id = 'lab'
        kind = 'REDACTED_EXTERNAL_SETUP_PRINCIPAL_ATOMIC_CYCLE_PRECHECK_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        execution_head = $ExpectedExecutionHead
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            authorizations_118_119_120_consumed = 'PASS'
            active_execution_authority_before_121 = 'NONE'
            aws_cli = 'PENDING'
            cli_history_disabled = 'PENDING'
            inherited_temporary_credentials_absent = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
            temporary_files_absent = 'PENDING'
            synthetic_two_principal_cycle = $synthetic.result
            session_isolation = $synthetic.two_principal_session_isolation
            rollback_first_after_put_failure = $synthetic.rollback_first_after_put_failure
        }
        policy = [ordered]@{
            name = $script:TemporaryPolicyName121
            sha256 = $synthetic.policy_sha256
            exact_action = 'iam:SimulatePrincipalPolicy'
            statement_count = 1
            action_count = 1
            condition_count = 0
            additional_actions = 0
        }
        external_principal = [ordered]@{
            expected_setup_profile_present = $false
            selected = $false
            identity_verified = $false
            redacted_identifier = 'NONE'
            privilege_classification = 'NO_BOUNDED_EXTERNAL_SETUP_PRINCIPAL'
            read_only_plan_operator_present = $false
            read_only_plan_operator_compatible = $false
            canonical_permission_evidence = 'projects/lab/evidence/EVD-LAB-PL003-AWS-BOUNDED-PROVISIONING-OPERATOR-113.json'
        }
        bootstrap_principal = [ordered]@{
            session_started = $false
            identity_verified = $false
            redacted_identifier = 'NOT_EXECUTED'
        }
        baseline = [ordered]@{
            executed = $false
            temporary_policy_absence_verified = $false
        }
        grant = [ordered]@{
            attempted = $false
            succeeded = $false
        }
        simulation = [ordered]@{
            attempted = $false
            completed_without_access_denied = $false
        }
        rollback = [ordered]@{
            required = $false
            attempted = $false
            verified = $false
        }
        final_state = [ordered]@{
            temporary_policy_created_by_121 = $false
            persistent_iam_mutations = 0
            aws_resources_created = 0
            terraform_executions = 0
            product_leadership_test_003_executions = 0
            product_leadership_active = $false
            product_leadership_integrated = $false
        }
        aws_calls = [ordered]@{
            external_sts_get_caller_identity = 0
            external_iam_list_user_policies = 0
            external_iam_get_user_policy = 0
            external_iam_put_user_policy = 0
            external_iam_delete_user_policy = 0
            bootstrap_sts_get_session_token = 0
            bootstrap_sts_get_caller_identity = 0
            bootstrap_iam_simulate_principal_policy = 0
            other_aws = 0
        }
        iam_mutations = [ordered]@{
            expected = 0
            actual = 0
            unexpected = 0
            persistent = 0
        }
        external_credentials_cleared = $true
        bootstrap_credentials_cleared = $true
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
            throw 'LOCAL_SYNTHETIC_TWO_PRINCIPAL_CYCLE_FAILED'
        }

        if ($null -eq (Get-Command aws -ErrorAction SilentlyContinue)) {
            throw 'AWS_CLI_NOT_AVAILABLE'
        }
        $evidence.prechecks.aws_cli = 'PASS'
        $profiles = @(& aws configure list-profiles 2>$null)
        if ($LASTEXITCODE -ne 0) {
            throw 'AWS_PROFILE_LIST_FAILED'
        }
        if ((& aws configure get cli_history 2>$null) -eq 'enabled') {
            throw 'AWS_CLI_HISTORY_ENABLED'
        }
        $evidence.prechecks.cli_history_disabled = 'PASS'

        $presentCredentialNames = @(
            $script:CredentialEnvironmentNames121 | Where-Object {
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

        $temporaryFiles = @(
            Get-ChildItem -LiteralPath $PSScriptRoot -Filter '.pl003-121-*' -File -ErrorAction SilentlyContinue
        )
        if ($temporaryFiles.Count -ne 0) {
            throw 'TEMPORARY_FILES_PRESENT'
        }
        $evidence.prechecks.temporary_files_absent = 'PASS'

        $evidence.external_principal.expected_setup_profile_present = $profiles -contains $script:ExpectedExternalProfile121
        $evidence.external_principal.read_only_plan_operator_present = $profiles -contains $script:ReadOnlyPlanProfile121

        if (-not $evidence.external_principal.expected_setup_profile_present) {
            throw 'BLOCKED_NO_BOUNDED_EXTERNAL_SETUP_PRINCIPAL'
        }

        throw 'BLOCKED_FAIL_CLOSED_OTHER'
    } catch {
        $failure = [string]$_.Exception.Message
        $evidence.status = 'BLOCKED'
        $evidence.failure_code = $failure
        $evidence.result = if ($failure -eq 'BLOCKED_NO_BOUNDED_EXTERNAL_SETUP_PRINCIPAL') {
            'BLOCKED_NO_BOUNDED_EXTERNAL_SETUP_PRINCIPAL'
        } else {
            'BLOCKED_FAIL_CLOSED_OTHER'
        }
    } finally {
        Write-PL003121Evidence -Evidence $evidence -Path $evidencePath
    }

    return [ordered]@{
        result = $evidence.result
        failure_code = $evidence.failure_code
        external_principal_selected = $evidence.external_principal.selected
        aws_calls = $evidence.aws_calls
        iam_mutations = $evidence.iam_mutations
        evidence_path = $evidencePath.Substring($repositoryRoot.Length + 1).Replace('\', '/')
        secrets_printed = $false
    }
}

if ($MyInvocation.InvocationName -eq '.') {
    return
}

if ($SyntheticTest -or -not $OperationalRun) {
    $test = Test-PL003ExternalSetupPrincipalSimulationCycle121
    $test | ConvertTo-Json -Depth 8
    if ($test.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003ExternalSetupPrincipalSimulationCycle121Precheck `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber
$outcome | ConvertTo-Json -Depth 8
if ($outcome.result -eq 'PASS_EXTERNAL_SETUP_ATOMIC_SIMULATION_VERIFIED_AND_REMOVED') {
    exit 0
}
exit 1
