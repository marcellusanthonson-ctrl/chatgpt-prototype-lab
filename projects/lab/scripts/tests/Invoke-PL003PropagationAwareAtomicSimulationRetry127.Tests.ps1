[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot '..\Invoke-PL003PropagationAwareAtomicSimulationRetry127.ps1'
. $scriptPath

$result = Test-PL003PropagationAwareAtomicSimulationRetry127
$result | ConvertTo-Json -Depth 12
if (
    $result.result -ne 'PASS' -or
    $result.case_count -lt 27 -or
    $result.monotonic_wait_seconds -ne 120 -or
    $result.aws_calls_during_wait -ne 0 -or
    $result.interruption_during_stabilization -ne 'PASS' -or
    $result.rollback -ne 'PASS' -or
    -not $result.one_simulation -or
    -not $result.baseline_and_final_identical
) {
    exit 1
}
exit 0
