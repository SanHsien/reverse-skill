[CmdletBinding()]
param(
    [switch]$FullRouting
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Invoke-Step {
    param(
        [Parameter(Mandatory)]
        [string]$Label,
        [Parameter(Mandatory)]
        [string]$Exe,
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    Write-Host "==> $Label"
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

$pythonTools = @(
    "tools\check_upstream_updates.py",
    "tools\check_dependency_freshness.py",
    "tools\check_links.py"
)

Invoke-Step -Label "Compile maintained Python" -Exe $pythonExe -Arguments (
    @("-m", "compileall", "-q", "tests") + $pythonTools
)

Invoke-Step -Label "Ruff (E9 + F)" -Exe $pythonExe -Arguments @(
    "-m", "ruff", "check", "--select", "E9,F", "--target-version", "py312",
    "tests", "tools\check_upstream_updates.py", "tools\check_dependency_freshness.py",
    "tools\check_links.py"
)

Invoke-Step -Label "Pytest maintenance suite" -Exe $pythonExe -Arguments @("-m", "pytest", "tests", "-q")

Invoke-Step -Label "Check Markdown links" -Exe $pythonExe -Arguments @(
    "tools\check_links.py"
)

Invoke-Step -Label "Repository security boundary" -Exe $pythonExe -Arguments @(
    "skills\scripts\verify-repository-security.py"
)

Invoke-Step -Label "Internal document links" -Exe $pythonExe -Arguments @(
    "skills\scripts\verify-doc-links.py"
)

$hostPwsh = (Get-Command pwsh -ErrorAction SilentlyContinue)
$pwshExe = if ($hostPwsh) { $hostPwsh.Source } else { (Get-Command powershell -ErrorAction Stop).Source }

Invoke-Step -Label "Routing coherence & supply-chain pin gate" -Exe $pwshExe -Arguments @(
    "-NoProfile", "-File", "skills\scripts\verify-routing-coherence.ps1"
)

if ($FullRouting) {
    Invoke-Step -Label "Routing regression (full benchmark)" -Exe $pwshExe -Arguments @(
        "-NoProfile", "-File", "skills\scripts\test-routing.ps1"
    )
} else {
    Invoke-Step -Label "Routing regression (quick benchmark)" -Exe $pwshExe -Arguments @(
        "-NoProfile", "-File", "skills\scripts\test-routing.ps1", "-Quick"
    )
}

Write-Host "WINDOWS DEV CHECK GREEN"
