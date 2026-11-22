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
function Resolve-UsableBash {
    # On Windows, a bare `bash` on PATH is often C:\Windows\System32\bash.exe, the WSL
    # launcher, which fails when no distro is installed. Prefer Git Bash, located from
    # `git --exec-path` (works on windows-latest runners and local Git for Windows),
    # then any other bash outside System32/WindowsApps. Each candidate must actually run.
    $candidates = New-Object System.Collections.Generic.List[string]
    $isWin = [System.IO.Path]::DirectorySeparatorChar -eq '\'
    if ($isWin) {
        $git = Get-Command git -ErrorAction SilentlyContinue
        if ($git) {
            $exec = (& $git.Source --exec-path 2>$null | Select-Object -First 1)
            $dir = if ($exec) { $exec.Trim() -replace '/', '\' } else { '' }
            while ($dir) {
                $probe = Join-Path $dir 'bin\bash.exe'
                if (Test-Path -LiteralPath $probe) { $candidates.Add($probe); break }
                $parent = Split-Path -Parent $dir
                if (-not $parent -or $parent -eq $dir) { break }
                $dir = $parent
            }
        }
    }
    foreach ($cmd in @(Get-Command bash -All -CommandType Application -ErrorAction SilentlyContinue)) {
        if ($isWin -and $cmd.Source -match '\\(System32|SysWOW64|WindowsApps)\\') { continue }
        $candidates.Add($cmd.Source)
    }
    foreach ($candidate in $candidates) {
        $probeOut = & $candidate -c 'echo bash-ok' 2>$null
        if ($LASTEXITCODE -eq 0 -and "$probeOut" -match 'bash-ok') { return $candidate }
    }
    return $null
}

$bashPath = Resolve-UsableBash
$bash = if ($bashPath) { [pscustomobject]@{ Source = $bashPath } } else { $null }

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
if ($bash) {
    $kinds += 'sh'
    Write-Host ("using bash: {0}" -f $bash.Source)
} else {
    Write-Host 'SKIP case-init.sh: no usable bash found (Git Bash via git --exec-path, or bash outside System32/WindowsApps)'
}

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
