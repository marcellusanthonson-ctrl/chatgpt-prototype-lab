[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot '..\Invoke-PL003ExternalSetupPrincipalSimulationCycle121Precheck.ps1'
. $scriptPath

$result = Test-PL003ExternalSetupPrincipalSimulationCycle121
$result | ConvertTo-Json -Depth 8
if ($result.result -ne 'PASS') {
    exit 1
}
exit 0
