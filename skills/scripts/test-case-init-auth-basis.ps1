#Requires -Version 5.1
# Regression: case-init must fail closed on an authorization basis outside the
# scope-contract allow-list (skills/ops/scope-contract.md). It must exit non-zero,
# say why, and leave no case directory behind -- never rewrite the basis to a
# valid-looking value such as own_system.
# Covers case-init.ps1 always, and case-init.sh when bash is available.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptDir = $PSScriptRoot
$ps1 = Join-Path $scriptDir 'case-init.ps1'
$sh = Join-Path $scriptDir 'case-init.sh'
$hostPwsh = Get-Command pwsh -ErrorAction SilentlyContinue
$shell = if ($hostPwsh) { $hostPwsh.Source } else { (Get-Command powershell -ErrorAction Stop).Source }
$bash = Get-Command bash -ErrorAction SilentlyContinue

$failures = New-Object System.Collections.Generic.List[string]
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("rs-basis-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $root | Out-Null

function Invoke-CaseInit {
    param([string]$Kind, [string]$CaseName, [string]$Basis)
    if ($Kind -eq 'ps1') {
        $out = & $shell -NoProfile -ExecutionPolicy Bypass -File $ps1 -Hint 'offline apk' -CaseName $CaseName `
            -ProjectRoot $root -AuthBasis $Basis 2>&1 | Out-String
    } else {
        $out = & $bash.Source $sh --hint 'offline apk' --case-name $CaseName --project-root $root --auth-basis $Basis 2>&1 | Out-String
    }
    [pscustomobject]@{ Code = $LASTEXITCODE; Output = $out; CaseRoot = (Join-Path (Join-Path $root 'work') $CaseName) }
}

$kinds = @('ps1')
if ($bash) { $kinds += 'sh' } else { Write-Host 'SKIP case-init.sh (bash not found)' }

try {
    foreach ($kind in $kinds) {
        $bad = Invoke-CaseInit -Kind $kind -CaseName "bad-basis-$kind" -Basis 'public_passive_observation'
        if ($bad.Code -eq 0) { $failures.Add("$kind accepted invalid basis (exit 0)") }
        if ($bad.Output -notmatch 'public_passive_observation') { $failures.Add("$kind error does not name the rejected basis") }
        if (Test-Path -LiteralPath $bad.CaseRoot) { $failures.Add("$kind created a case directory for an invalid basis") }

        $good = Invoke-CaseInit -Kind $kind -CaseName "good-basis-$kind" -Basis 'lab_only'
        $scope = Join-Path $good.CaseRoot 'scope.md'
        if ($good.Code -ne 0) { $failures.Add("$kind rejected allowed basis lab_only (exit $($good.Code)): $($good.Output)") }
        elseif (-not (Test-Path -LiteralPath $scope) -or ([System.IO.File]::ReadAllText($scope) -notmatch '(?m)^- basis: lab_only\s*$')) {
            $failures.Add("$kind did not record basis lab_only in scope.md")
        }
        Write-Host ("checked case-init.{0}" -f $kind)
    }
}
finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}

if ($failures.Count -gt 0) {
    Write-Host ("FAILED {0}" -f $failures.Count)
    $failures | ForEach-Object { Write-Host " - $_" }
    exit 1
}
Write-Host 'CASE-INIT AUTH BASIS FAILS CLOSED'
