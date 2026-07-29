[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot '..\Invoke-PL003CreateBoundedSetupRoleCompatibility123.ps1'
. $scriptPath

$result = Test-PL003CreateBoundedSetupRoleCompatibility123
$result | ConvertTo-Json -Depth 8
if ($result.result -ne 'PASS') {
    exit 1
}
exit 0
