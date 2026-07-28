[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$sourceProfile = 'pl003-bootstrap'
$mfaReferenceProfile = 'pl003-plan-operator'
$expectedPrincipalName = 'pl003-bootstrap-operator'
$expectedRegion = 'sa-east-1'
$durationSeconds = 3600

$credentialEnvironmentNames = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN'
)

$temporaryEnvironmentNames = @(
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_SECURITY_TOKEN',
    'AWS_PROFILE',
    'AWS_DEFAULT_PROFILE',
    'AWS_REGION',
    'AWS_DEFAULT_REGION',
    'AWS_EC2_METADATA_DISABLED'
)

$priorEnvironment = @{}
foreach ($name in $temporaryEnvironmentNames) {
    $priorEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}

$result = [ordered]@{
    result                              = 'FAIL'
    gate                                = 'AUTHORIZATION_114_MFA_GET_SESSION_TOKEN'
    source_profile                      = $sourceProfile
    region                              = $expectedRegion
    duration_seconds                    = $durationSeconds
    get_session_token                   = 'NOT_COMPLETED'
    redacted_sts_identity               = 'NOT_VERIFIED'
    temporary_credentials_storage       = 'PROCESS_MEMORY_ONLY'
    temporary_credentials_retained      = $false
    local_credential_profile_created    = $false
    aws_iam_mutations                   = 0
    full_account_id_included            = $false
    credentials_tokens_or_totp_included = $false
    cleanup                             = 'PENDING'
    failure_code                        = $null
    resume_instruction                  = $null
}

$secureTotp = $null
$totpBstr = [IntPtr]::Zero
$totp = $null
$sessionJson = $null
$sessionResponse = $null
$sessionCredentials = $null
$identityJson = $null
$identity = $null
$awsAccessKeyId = $null
$awsSecretAccessKey = $null
$awsSessionToken = $null

try {
    if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
        throw 'AWS_CLI_NOT_AVAILABLE'
    }

    $profiles = @(aws configure list-profiles 2>$null)
    if ($profiles -notcontains $sourceProfile) {
        throw 'BOOTSTRAP_PROFILE_NOT_FOUND'
    }

    $presentCredentialEnvironmentNames = @(
        $credentialEnvironmentNames | Where-Object {
            -not [string]::IsNullOrWhiteSpace(
                [Environment]::GetEnvironmentVariable($_, 'Process')
            )
        }
    )
    if ($presentCredentialEnvironmentNames.Count -ne 0) {
        throw 'PREEXISTING_AWS_CREDENTIAL_ENVIRONMENT_DETECTED'
    }

    $configuredRegion = aws configure get region --profile $sourceProfile 2>$null
    if ([string]::IsNullOrWhiteSpace($configuredRegion)) {
        $configuredRegion = $expectedRegion
    }
    if ($configuredRegion -ne $expectedRegion) {
        throw 'BOOTSTRAP_REGION_MISMATCH'
    }

    $cliHistory = aws configure get cli_history --profile $sourceProfile 2>$null
    if ($cliHistory -eq 'enabled') {
        throw 'AWS_CLI_HISTORY_MUST_BE_DISABLED'
    }

    $mfaSerial = aws configure get mfa_serial --profile $sourceProfile 2>$null
    if ([string]::IsNullOrWhiteSpace($mfaSerial)) {
        $mfaSerial = aws configure get mfa_serial --profile $mfaReferenceProfile 2>$null
    }
    if ([string]::IsNullOrWhiteSpace($mfaSerial)) {
        throw 'MFA_REFERENCE_NOT_CONFIGURED'
    }

    $secureTotp = Read-Host -Prompt 'MFA token code' -AsSecureString
    $totpBstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureTotp)
    $totp = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($totpBstr)
    if ($totp -notmatch '^[0-9]{6}$') {
        throw 'INVALID_TOTP_FORMAT'
    }

    $sessionJson = aws sts get-session-token `
        --profile $sourceProfile `
        --region $expectedRegion `
        --serial-number $mfaSerial `
        --token-code $totp `
        --duration-seconds $durationSeconds `
        --no-cli-pager `
        --output json 2>$null

    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($sessionJson -join ''))) {
        throw 'GET_SESSION_TOKEN_FAILED'
    }

    $sessionResponse = ($sessionJson -join [Environment]::NewLine) | ConvertFrom-Json
    $sessionCredentials = $sessionResponse.Credentials
    $awsAccessKeyId = [string]$sessionCredentials.AccessKeyId
    $awsSecretAccessKey = [string]$sessionCredentials.SecretAccessKey
    $awsSessionToken = [string]$sessionCredentials.SessionToken
    $expiration = [DateTimeOffset]::Parse([string]$sessionCredentials.Expiration)

    if (
        [string]::IsNullOrWhiteSpace($awsAccessKeyId) -or
        [string]::IsNullOrWhiteSpace($awsSecretAccessKey) -or
        [string]::IsNullOrWhiteSpace($awsSessionToken)
    ) {
        throw 'TEMPORARY_CREDENTIAL_SET_INCOMPLETE'
    }

    $now = [DateTimeOffset]::UtcNow
    if ($expiration -le $now -or $expiration -gt $now.AddSeconds($durationSeconds + 120)) {
        throw 'TEMPORARY_CREDENTIAL_EXPIRATION_INVALID'
    }

    $env:AWS_ACCESS_KEY_ID = $awsAccessKeyId
    $env:AWS_SECRET_ACCESS_KEY = $awsSecretAccessKey
    $env:AWS_SESSION_TOKEN = $awsSessionToken
    $env:AWS_SECURITY_TOKEN = $null
    $env:AWS_PROFILE = $null
    $env:AWS_DEFAULT_PROFILE = $null
    $env:AWS_REGION = $expectedRegion
    $env:AWS_DEFAULT_REGION = $expectedRegion
    $env:AWS_EC2_METADATA_DISABLED = 'true'

    $identityJson = aws sts get-caller-identity `
        --region $expectedRegion `
        --no-cli-pager `
        --output json 2>$null

    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($identityJson -join ''))) {
        throw 'REDACTED_STS_IDENTITY_VERIFICATION_FAILED'
    }

    $identity = ($identityJson -join [Environment]::NewLine) | ConvertFrom-Json
    $accountId = [string]$identity.Account
    $principalArn = [string]$identity.Arn

    if ($accountId -notmatch '^[0-9]{12}$') {
        throw 'STS_ACCOUNT_SHAPE_INVALID'
    }
    if ($principalArn -notmatch ('^arn:aws:iam::[0-9]{12}:user/' + [regex]::Escape($expectedPrincipalName) + '$')) {
        throw 'STS_PRINCIPAL_MISMATCH'
    }

    $result.result = 'PASS'
    $result.get_session_token = 'PASS_MFA_BACKED_TEMPORARY_SESSION'
    $result.redacted_sts_identity = "IAM_USER_SESSION_$expectedPrincipalName"
    $result.resume_instruction = 'Return to Codex and send exactly: RESUME_AUTHORIZATION_114_AFTER_MFA_GATE_PASS_NO_ACTIVE_SESSION_RETAINED'
} catch {
    $knownFailureCodes = @(
        'AWS_CLI_NOT_AVAILABLE',
        'BOOTSTRAP_PROFILE_NOT_FOUND',
        'PREEXISTING_AWS_CREDENTIAL_ENVIRONMENT_DETECTED',
        'BOOTSTRAP_REGION_MISMATCH',
        'AWS_CLI_HISTORY_MUST_BE_DISABLED',
        'MFA_REFERENCE_NOT_CONFIGURED',
        'INVALID_TOTP_FORMAT',
        'GET_SESSION_TOKEN_FAILED',
        'TEMPORARY_CREDENTIAL_SET_INCOMPLETE',
        'TEMPORARY_CREDENTIAL_EXPIRATION_INVALID',
        'REDACTED_STS_IDENTITY_VERIFICATION_FAILED',
        'STS_ACCOUNT_SHAPE_INVALID',
        'STS_PRINCIPAL_MISMATCH'
    )

    if ($knownFailureCodes -contains $_.Exception.Message) {
        $result.failure_code = $_.Exception.Message
    } else {
        $result.failure_code = 'UNEXPECTED_LOCAL_GATE_FAILURE'
    }
    $result.resume_instruction = 'Do not resume authorization 114; correct the reported gate failure without sharing credentials or the TOTP.'
} finally {
    foreach ($name in $temporaryEnvironmentNames) {
        [Environment]::SetEnvironmentVariable(
            $name,
            $priorEnvironment[$name],
            'Process'
        )
    }

    if ($totpBstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($totpBstr)
    }

    $secureTotp = $null
    $totp = $null
    $sessionJson = $null
    $sessionResponse = $null
    $sessionCredentials = $null
    $identityJson = $null
    $identity = $null
    $awsAccessKeyId = $null
    $awsSecretAccessKey = $null
    $awsSessionToken = $null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()

    $result.cleanup = 'PASS_PROCESS_ENVIRONMENT_RESTORED_AND_SENSITIVE_VARIABLES_RELEASED'
    $result.temporary_credentials_retained = $false
}

$result | ConvertTo-Json -Depth 4
if ($result.result -eq 'PASS') {
    exit 0
}
exit 1
