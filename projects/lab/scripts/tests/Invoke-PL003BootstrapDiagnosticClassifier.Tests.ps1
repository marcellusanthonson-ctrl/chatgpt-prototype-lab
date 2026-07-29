[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot '..\Invoke-PL003BootstrapDiagnosticPreflight.ps1'
. $scriptPath

$result = Test-PL003BootstrapDiagnosticClassifier
$result | ConvertTo-Json -Depth 6
if ($result.result -ne 'PASS') {
    exit 1
}
exit 0
