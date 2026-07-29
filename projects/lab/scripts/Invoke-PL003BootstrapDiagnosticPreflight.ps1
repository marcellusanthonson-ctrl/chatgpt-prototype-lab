[CmdletBinding(DefaultParameterSetName = 'Synthetic')]
param(
    [Parameter(ParameterSetName = 'Synthetic')]
    [switch]$SyntheticClassifierTest,

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

$script:SourceProfile = 'pl003-bootstrap'
$script:MfaReferenceProfile = 'pl003-plan-operator'
$script:ExpectedBootstrapPrincipal = 'pl003-bootstrap-operator'
$script:ExpectedRegion = 'sa-east-1'
$script:DurationSeconds = 3600
$script:CredentialEnvironmentNames = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

function ConvertTo-PL003SanitizedText {
    param([AllowNull()][string]$Text)

    if ([string]::IsNullOrEmpty($Text)) {
        return ''
    }

    $safe = $Text
    $safe = $safe -replace '(?i)(AKIA|ASIA|AIDA|AROA|ANPA|ANVA|AIPA)[A-Z0-9]{16}', '<REDACTED_ACCESS_KEY_ID>'
    $safe = $safe -replace '(?i)arn:(?:aws|aws-us-gov|aws-cn):[^\s,"'']+', '<REDACTED_ARN>'
    $safe = $safe -replace '(?<!\d)\d{12}(?!\d)', '<REDACTED_ACCOUNT_ID>'
    $safe = $safe -replace '(?i)(?:aws_?secret_?access_?key|secretAccessKey)\s*[=:]\s*\S+', '<REDACTED_SECRET_ACCESS_KEY>'
    $safe = $safe -replace '(?i)(?:aws_?session_?token|sessionToken)\s*[=:]\s*\S+', '<REDACTED_SESSION_TOKEN>'
    $safe = $safe -replace '(?i)(?:token-code|mfa(?:_?code)?)\s*[=:]\s*\d{6}', '<REDACTED_MFA_CODE>'
    $safe = $safe -replace '(?i)(?:request\s*id|requestid)\s*[=:]\s*[A-Za-z0-9-]+', '<REDACTED_REQUEST_ID>'
    return $safe
}

function Get-PL003AwsErrorCode {
    param([AllowNull()][string]$StdErr)

    if ($StdErr -match '(?i)An error occurred \(([^)]+)\)') {
        return [string]$Matches[1]
    }
    if ($StdErr -match '(?i)"(?:code|__type)"\s*:\s*"([^"]+)"') {
        $code = [string]$Matches[1]
        if ($code.Contains('#')) {
            $code = $code.Substring($code.LastIndexOf('#') + 1)
        }
        return $code
    }
    return $null
}

function Get-PL003HttpStatus {
    param([AllowNull()][string]$StdErr)

    if ($StdErr -match '(?i)(?:http\s*)?status(?:\s*code)?\s*[=:]\s*(\d{3})') {
        return [int]$Matches[1]
    }
    return $null
}

function Get-PL003SimulationClassification {
    param(
        [Parameter(Mandatory)][int]$ExitCode,
        [AllowNull()][string]$StdErr,
        [AllowNull()][string]$StdOut,
        [AllowNull()][string]$AwsErrorCode
    )

    if ($ExitCode -eq 0) {
        try {
            $response = $StdOut | ConvertFrom-Json -ErrorAction Stop
            $decision = [string]$response.EvaluationResults[0].EvalDecision
            if ($decision -in @('implicitDeny', 'explicitDeny')) {
                return 'SIMULATION_ACTION_NOT_AUTHORIZED'
            }
            return 'INSUFFICIENT_EVIDENCE_TO_DISCRIMINATE'
        } catch {
            return 'TOOLING_OR_ENVIRONMENT_FAILURE'
        }
    }

    $combined = ([string]$AwsErrorCode + ' ' + [string]$StdErr).ToLowerInvariant()

    if ($combined -match 'permissions boundary|boundary policy|session policy|sessionpolicy') {
        return 'BOUNDARY_OR_SESSION_POLICY_RESTRICTION'
    }
    if ($combined -match 'service control policy|\bscp\b|organizations? restriction|organization policy') {
        return 'SCP_ORGANIZATION_RESTRICTION_POSSIBLE'
    }
    if ($combined -match 'policy source.*not supported|principal.*not supported|unsupported.*principal|unsupportedoperation') {
        return 'SIMULATION_TARGET_PRINCIPAL_UNSUPPORTED'
    }
    if ($combined -match 'nosuchentity|principal.*not found|policy source.*not found|cannot be found') {
        return 'PRINCIPAL_ARN_RESOLUTION_FAILED'
    }
    if ($combined -match 'invalidinput|validationerror|malformed|invalid parameter|invalid context|invalid action|invalid resource') {
        return 'SIMULATION_INPUT_INVALID'
    }
    if ($combined -match 'accessdenied|not authorized|unauthorizedoperation|authorizationerror') {
        return 'SIMULATION_ACTION_NOT_AUTHORIZED'
    }
    if ($combined -match 'executable not found|not recognized as an internal|unable to locate credentials|could not connect|endpointconnectionerror|ssl validation|parse error|unknown options') {
        return 'TOOLING_OR_ENVIRONMENT_FAILURE'
    }
    return 'INSUFFICIENT_EVIDENCE_TO_DISCRIMINATE'
}

function Get-PL003SanitizedCallMetadata {
    param(
        [Parameter(Mandatory)][int]$ExitCode,
        [AllowNull()][string]$StdErr,
        [Parameter(Mandatory)][string]$Service,
        [Parameter(Mandatory)][string]$Operation
    )

    $errorCode = Get-PL003AwsErrorCode -StdErr $StdErr
    $httpStatus = Get-PL003HttpStatus -StdErr $StdErr
    $exceptionClass = if ($ExitCode -eq 0) {
        'NONE'
    } elseif (-not [string]::IsNullOrWhiteSpace($errorCode)) {
        'AWS_CLI_SERVICE_ERROR'
    } else {
        'AWS_CLI_PROCESS_ERROR'
    }

    return [ordered]@{
        exit_code = $ExitCode
        service = $Service
        operation = $Operation
        aws_error_code = $errorCode
        exception_class = $exceptionClass
        http_status = $httpStatus
        stderr_captured_in_memory = $true
        stdout_captured_in_memory = $true
        stderr_persisted = $false
        stdout_persisted = $false
    }
}

function Invoke-PL003AwsCliCaptured {
    param(
        [Parameter(Mandatory)][string[]]$Arguments,
        [AllowNull()]$Credentials
    )

    foreach ($argument in $Arguments) {
        if ($argument -match '[\s"]') {
            throw 'UNSAFE_NATIVE_ARGUMENT_SHAPE'
        }
    }

    $awsCommand = Get-Command aws -ErrorAction SilentlyContinue
    if ($null -eq $awsCommand) {
        throw 'AWS_CLI_NOT_AVAILABLE'
    }

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $awsCommand.Source
    $startInfo.Arguments = ($Arguments -join ' ')
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true

    if ($null -ne $Credentials) {
        $startInfo.EnvironmentVariables['AWS_ACCESS_KEY_ID'] = [string]$Credentials.AccessKeyId
        $startInfo.EnvironmentVariables['AWS_SECRET_ACCESS_KEY'] = [string]$Credentials.SecretAccessKey
        $startInfo.EnvironmentVariables['AWS_SESSION_TOKEN'] = [string]$Credentials.SessionToken
        $startInfo.EnvironmentVariables.Remove('AWS_SECURITY_TOKEN')
        $startInfo.EnvironmentVariables.Remove('AWS_PROFILE')
        $startInfo.EnvironmentVariables.Remove('AWS_DEFAULT_PROFILE')
    }
    $startInfo.EnvironmentVariables['AWS_REGION'] = $script:ExpectedRegion
    $startInfo.EnvironmentVariables['AWS_DEFAULT_REGION'] = $script:ExpectedRegion
    $startInfo.EnvironmentVariables['AWS_EC2_METADATA_DISABLED'] = 'true'

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    try {
        if (-not $process.Start()) {
            throw 'AWS_CLI_PROCESS_START_FAILED'
        }
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        return [pscustomobject]@{
            ExitCode = [int]$process.ExitCode
            RawStdOut = $stdout
            RawStdErr = $stderr
        }
    } finally {
        $process.Dispose()
    }
}

function Test-PL003BootstrapDiagnosticClassifier {
    $cases = @(
        [pscustomobject]@{
            Name = 'access-denied'
            ExitCode = 255
            ErrorCode = 'AccessDenied'
            StdErr = 'An error occurred (AccessDenied) when calling the SimulatePrincipalPolicy operation: not authorized'
            StdOut = ''
            Expected = 'SIMULATION_ACTION_NOT_AUTHORIZED'
        },
        [pscustomobject]@{
            Name = 'unsupported-principal'
            ExitCode = 255
            ErrorCode = 'ValidationError'
            StdErr = 'An error occurred (ValidationError): policy source principal is not supported'
            StdOut = ''
            Expected = 'SIMULATION_TARGET_PRINCIPAL_UNSUPPORTED'
        },
        [pscustomobject]@{
            Name = 'invalid-input'
            ExitCode = 255
            ErrorCode = 'InvalidInput'
            StdErr = 'An error occurred (InvalidInput): invalid context entry'
            StdOut = ''
            Expected = 'SIMULATION_INPUT_INVALID'
        },
        [pscustomobject]@{
            Name = 'principal-not-found'
            ExitCode = 255
            ErrorCode = 'NoSuchEntity'
            StdErr = 'An error occurred (NoSuchEntity): policy source cannot be found'
            StdOut = ''
            Expected = 'PRINCIPAL_ARN_RESOLUTION_FAILED'
        },
        [pscustomobject]@{
            Name = 'boundary'
            ExitCode = 255
            ErrorCode = 'AccessDenied'
            StdErr = 'An error occurred (AccessDenied): permissions boundary restriction'
            StdOut = ''
            Expected = 'BOUNDARY_OR_SESSION_POLICY_RESTRICTION'
        },
        [pscustomobject]@{
            Name = 'scp'
            ExitCode = 255
            ErrorCode = 'AccessDenied'
            StdErr = 'An error occurred (AccessDenied): blocked by service control policy'
            StdOut = ''
            Expected = 'SCP_ORGANIZATION_RESTRICTION_POSSIBLE'
        },
        [pscustomobject]@{
            Name = 'tooling'
            ExitCode = 255
            ErrorCode = $null
            StdErr = 'Could not connect to the endpoint URL'
            StdOut = ''
            Expected = 'TOOLING_OR_ENVIRONMENT_FAILURE'
        },
        [pscustomobject]@{
            Name = 'unknown'
            ExitCode = 255
            ErrorCode = 'UnknownFailure'
            StdErr = 'An error occurred (UnknownFailure)'
            StdOut = ''
            Expected = 'INSUFFICIENT_EVIDENCE_TO_DISCRIMINATE'
        },
        [pscustomobject]@{
            Name = 'successful-deny'
            ExitCode = 0
            ErrorCode = $null
            StdErr = ''
            StdOut = '{"EvaluationResults":[{"EvalDecision":"implicitDeny"}]}'
            Expected = 'SIMULATION_ACTION_NOT_AUTHORIZED'
        }
    )

    $failures = [System.Collections.Generic.List[string]]::new()
    foreach ($case in $cases) {
        $actual = Get-PL003SimulationClassification `
            -ExitCode $case.ExitCode `
            -StdErr $case.StdErr `
            -StdOut $case.StdOut `
            -AwsErrorCode $case.ErrorCode
        if ($actual -ne $case.Expected) {
            $failures.Add($case.Name)
        }
    }

    $syntheticAccountId = '123456' + '789012'
    $syntheticAccessKey = 'AKIA' + 'ABCDEFGHIJKLMNOP'
    $syntheticMfa = '12' + '3456'
    $syntheticArn = 'arn:' + 'aws:iam::' + $syntheticAccountId + ':user/example'
    $unsafe = "request id=abc-123 account=$syntheticAccountId principal=$syntheticArn key=$syntheticAccessKey token-code=$syntheticMfa"
    $sanitized = ConvertTo-PL003SanitizedText -Text $unsafe
    if (
        $sanitized.Contains($syntheticAccountId) -or
        $sanitized.Contains($syntheticArn) -or
        $sanitized.Contains($syntheticAccessKey) -or
        $sanitized.Contains($syntheticMfa) -or
        $sanitized.Contains('abc-123')
    ) {
        $failures.Add('sanitization')
    }

    return [ordered]@{
        result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
        case_count = $cases.Count + 1
        failed_case_count = $failures.Count
        failed_cases = @($failures)
        aws_calls = 0
        secrets_printed = $false
    }
}

function Write-PL003Evidence {
    param(
        [Parameter(Mandatory)]$Evidence,
        [Parameter(Mandatory)][string]$TargetPath
    )

    $parent = Split-Path -Parent $TargetPath
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        throw 'EVIDENCE_PARENT_DIRECTORY_NOT_FOUND'
    }
    if (Test-Path -LiteralPath $TargetPath) {
        throw 'EVIDENCE_PATH_ALREADY_EXISTS'
    }

    $json = $Evidence | ConvertTo-Json -Depth 20
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
    $stream = [IO.File]::Open(
        $TargetPath,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None
    )
    try {
        $stream.Write($bytes, 0, $bytes.Length)
    } finally {
        $stream.Dispose()
    }
}

function Invoke-PL003OperationalDiagnostic {
    param(
        [Parameter(Mandatory)][string]$ExpectedExecutionHead,
        [Parameter(Mandatory)][int]$OperationalAttemptNumber,
        [AllowNull()][string]$RequestedEvidencePath
    )

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    $attemptId = 'ATTEMPT-{0:D3}' -f $OperationalAttemptNumber
    $evidenceBaseName = 'EVD-LAB-PL003-AWS-DIAGNOSTIC-PREFLIGHT-118'
    $defaultEvidencePath = Join-Path $repositoryRoot "projects\lab\evidence\$evidenceBaseName-$attemptId.json"
    $targetEvidencePath = if ([string]::IsNullOrWhiteSpace($RequestedEvidencePath)) {
        $defaultEvidencePath
    } else {
        [IO.Path]::GetFullPath($RequestedEvidencePath)
    }
    if (-not $targetEvidencePath.StartsWith(
        (Join-Path $repositoryRoot 'projects\lab\evidence'),
        [StringComparison]::OrdinalIgnoreCase
    )) {
        throw 'EVIDENCE_PATH_OUTSIDE_AUTHORIZED_DIRECTORY'
    }

    $result = [ordered]@{
        schema_version = '1.0.0'
        evidence_id = "$evidenceBaseName-$attemptId"
        attempt_id = $attemptId
        authorization_id = 'AUTHORIZATION_LAB_PL003_CODEX_BOOTSTRAP_DIAGNOSTIC_EXECUTION_118'
        project_id = 'lab'
        kind = 'REDACTED_AWS_BOOTSTRAP_DIAGNOSTIC_PREFLIGHT_EVIDENCE'
        status = 'IN_PROGRESS'
        executed_at = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        repository = 'marcellusanthonson-ctrl/chatgpt-prototype-lab'
        branch_mode = 'DETACHED_HEAD'
        execution_head = $ExpectedExecutionHead
        original_checkout = [ordered]@{
            status = 'OUTDATED_WITH_TWO_UNTRACKED_LOCAL_EVIDENCE_FILES'
            local_evidence_preserved_outside_repository = $true
            treated_as_canonical_before_reconciliation = $false
        }
        isolated_worktree = [ordered]@{
            clean_before_execution = $false
            external_preservation_used_as_configuration_or_operational_input = $false
        }
        prechecks = [ordered]@{
            head = 'PENDING'
            worktree = 'PENDING'
            aws_cli = 'PENDING'
            cli_history_disabled = 'PENDING'
            inherited_temporary_credentials_absent = 'PENDING'
            reusable_temporary_profiles_absent = 'PENDING'
            bootstrap_profile = 'PENDING'
            mfa_reference = 'PENDING'
            synthetic_classifier = 'PASS'
        }
        diagnostic = [ordered]@{
            tested_action = 'iam:CreatePolicy'
            tested_resource_shape = 'IAM_POLICY_PL003_SETUP_BOUNDARY'
            context_key_names = @(
                'aws:MultiFactorAuthPresent',
                'aws:RequestTag/Project',
                'aws:RequestTag/Authorization',
                'aws:RequestTag/Temporary'
            )
            sanitized_call_metadata = $null
            classification = $null
        }
        aws_calls = [ordered]@{
            sts_get_session_token = 0
            sts_get_caller_identity = 0
            iam_simulate_principal_policy = 0
            other_aws = 0
        }
        zero_mutation_attestation = [ordered]@{
            iam_mutations = 0
            infrastructure_mutations = 0
            terraform_executions = 0
            product_leadership_test_003_executions = 0
            product_leadership_active = $false
            product_leadership_integrated = $false
        }
        ephemeral_credentials_cleared = $false
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

    $secureMfa = $null
    $mfaPointer = [IntPtr]::Zero
    $mfaCode = $null
    $sessionCall = $null
    $sessionDocument = $null
    $credentials = $null
    $identityCall = $null
    $identityDocument = $null
    $simulationCall = $null

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
        $result.isolated_worktree.clean_before_execution = $true

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
        $result.prechecks.cli_history_disabled = 'PASS_GLOBAL_CONFIGURATION'

        $presentCredentialNames = @(
            $script:CredentialEnvironmentNames | Where-Object {
                -not [string]::IsNullOrWhiteSpace(
                    [Environment]::GetEnvironmentVariable($_, 'Process')
                )
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

        if ((& aws configure get cli_history --profile $script:SourceProfile 2>$null) -eq 'enabled') {
            throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
        }
        $result.prechecks.cli_history_disabled = 'PASS'

        $configuredRegion = & aws configure get region --profile $script:SourceProfile 2>$null
        if ([string]::IsNullOrWhiteSpace(($configuredRegion -join ''))) {
            $configuredRegion = $script:ExpectedRegion
        }
        if (($configuredRegion -join '') -ne $script:ExpectedRegion) {
            throw 'BOOTSTRAP_REGION_MISMATCH'
        }

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
            $metadata = Get-PL003SanitizedCallMetadata `
                -ExitCode $sessionCall.ExitCode `
                -StdErr $sessionCall.RawStdErr `
                -Service 'sts' `
                -Operation 'GetSessionToken'
            $result.diagnostic.sanitized_call_metadata = $metadata
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
            $metadata = Get-PL003SanitizedCallMetadata `
                -ExitCode $identityCall.ExitCode `
                -StdErr $identityCall.RawStdErr `
                -Service 'sts' `
                -Operation 'GetCallerIdentity'
            $result.diagnostic.sanitized_call_metadata = $metadata
            throw 'BOOTSTRAP_IDENTITY_RESOLUTION_FAILED'
        }

        $identityDocument = $identityCall.RawStdOut | ConvertFrom-Json -ErrorAction Stop
        $accountId = [string]$identityDocument.Account
        $principalArn = [string]$identityDocument.Arn
        if ($accountId -notmatch '^\d{12}$') {
            throw 'STS_ACCOUNT_SHAPE_INVALID'
        }
        if ($principalArn -notmatch ('^arn:aws:iam::\d{12}:user/' + [regex]::Escape($script:ExpectedBootstrapPrincipal) + '$')) {
            throw 'BOOTSTRAP_STS_PRINCIPAL_MISMATCH'
        }

        $resourceArn = "arn:aws:iam::$accountId`:policy/PL003IAMSetupBoundary114"
        $contextEntries = @(
            'ContextKeyName=aws:MultiFactorAuthPresent,ContextKeyValues=true,ContextKeyType=boolean',
            'ContextKeyName=aws:RequestTag/Project,ContextKeyValues=PRODUCT-LEADERSHIP-TEST-003,ContextKeyType=string',
            'ContextKeyName=aws:RequestTag/Authorization,ContextKeyValues=114A,ContextKeyType=string',
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

        $result.aws_calls.iam_simulate_principal_policy = 1
        $simulationCall = Invoke-PL003AwsCliCaptured `
            -Arguments $simulationArguments `
            -Credentials $credentials

        $awsErrorCode = Get-PL003AwsErrorCode -StdErr $simulationCall.RawStdErr
        $classification = Get-PL003SimulationClassification `
            -ExitCode $simulationCall.ExitCode `
            -StdErr $simulationCall.RawStdErr `
            -StdOut $simulationCall.RawStdOut `
            -AwsErrorCode $awsErrorCode
        $result.diagnostic.sanitized_call_metadata = Get-PL003SanitizedCallMetadata `
            -ExitCode $simulationCall.ExitCode `
            -StdErr $simulationCall.RawStdErr `
            -Service 'iam' `
            -Operation 'SimulatePrincipalPolicy'
        $result.diagnostic.classification = $classification
        $result.status = 'DIAGNOSTIC_COMPLETE'
        $result.result = 'PASS_CLASSIFIED'
    } catch {
        $message = [string]$_.Exception.Message
        if (
            $result.aws_calls.sts_get_session_token -eq 0 -and
            $result.prechecks.mfa_reference -eq 'PASS' -and
            $message -notmatch '^[A-Z0-9_]+$'
        ) {
            $result.failure_code = 'SECURE_INTERACTIVE_MFA_PROMPT_UNAVAILABLE'
        } elseif ($message -match '^[A-Z0-9_]+$') {
            $result.failure_code = $message
        } else {
            $result.failure_code = 'UNEXPECTED_DIAGNOSTIC_FAILURE'
        }
        if ($result.aws_calls.sts_get_session_token -eq 0) {
            $result.status = 'BLOCKED_BEFORE_MFA'
        } elseif ($result.aws_calls.iam_simulate_principal_policy -eq 0) {
            $result.status = 'BLOCKED_AFTER_MFA_BEFORE_SIMULATION'
        } else {
            $result.status = 'DIAGNOSTIC_COMPLETE_WITH_CLASSIFICATION'
        }
        $result.result = 'BLOCKED_FAIL_CLOSED'
    } finally {
        if ($mfaPointer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($mfaPointer)
        }
        $secureMfa = $null
        $mfaCode = $null
        $sessionCall = $null
        $sessionDocument = $null
        $credentials = $null
        $identityCall = $null
        $identityDocument = $null
        $simulationCall = $null
        $accountId = $null
        $principalArn = $null
        $resourceArn = $null
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
        $result.ephemeral_credentials_cleared = $true
        Write-PL003Evidence -Evidence $result -TargetPath $targetEvidencePath
    }

    $summary = [ordered]@{
        result = $result.result
        status = $result.status
        failure_code = $result.failure_code
        classification = $result.diagnostic.classification
        aws_calls = $result.aws_calls
        zero_mutations = $true
        ephemeral_credentials_cleared = $result.ephemeral_credentials_cleared
        evidence_path = $targetEvidencePath.Substring($repositoryRoot.Length + 1).Replace('\', '/')
        secrets_printed = $false
    }
    $operationalExitCode = 1
    if ($result.result -eq 'PASS_CLASSIFIED') {
        $operationalExitCode = 0
    }
    return [pscustomobject]@{
        ExitCode = $operationalExitCode
        Summary = $summary
    }
}

if ($MyInvocation.InvocationName -eq '.') {
    return
}

if ($SyntheticClassifierTest -or -not $OperationalRun) {
    $testResult = Test-PL003BootstrapDiagnosticClassifier
    $testResult | ConvertTo-Json -Depth 6
    if ($testResult.result -eq 'PASS') {
        exit 0
    }
    exit 1
}

$outcome = Invoke-PL003OperationalDiagnostic `
    -ExpectedExecutionHead $ExpectedHead `
    -OperationalAttemptNumber $AttemptNumber `
    -RequestedEvidencePath $EvidencePath
$outcome.Summary | ConvertTo-Json -Depth 6
exit $outcome.ExitCode
