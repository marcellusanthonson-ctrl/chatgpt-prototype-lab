[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot '..\Invoke-PL003ManualSetupAtomicSimulationCycle125.ps1'
. $scriptPath

$result = Test-PL003ManualSetupAtomicSimulationCycle125
$result | ConvertTo-Json -Depth 10
if ($result.result -ne 'PASS') {
    exit 1
}
exit 0
