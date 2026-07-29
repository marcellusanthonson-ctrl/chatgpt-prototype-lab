[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot '..\Invoke-PL003CorrectedAtomicSimulationRetry126.ps1'
. $scriptPath

$result = Test-PL003CorrectedAtomicSimulationRetry126
$result | ConvertTo-Json -Depth 10
if ($result.result -ne 'PASS' -or $result.case_count -lt 19) {
    exit 1
}
exit 0
