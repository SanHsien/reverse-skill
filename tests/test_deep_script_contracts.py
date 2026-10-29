"""Offline regressions for the PowerShell entry points; never install tools."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "scripts"


def run_ps(*arguments: str) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("pwsh")
    assert executable, "PowerShell 7 is required by the maintenance gate"
    return subprocess.run(
        [executable, "-NoProfile", *arguments],
        cwd=ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )


@pytest.mark.parametrize("contract", ["history", "created", "update_event"])
def test_case_reinitialization_preserves_history_and_workitems(
    tmp_path: Path, contract: str,
) -> None:
    arguments = [
        "-File", str(SCRIPTS / "case-init.ps1"),
        "-Hint", "authorized web review", "-CaseName", "history-case",
        "-ProjectRoot", str(tmp_path),
    ]
    first = run_ps(*arguments)
    assert first.returncode == 0, first.stdout + first.stderr
    case = tmp_path / "work" / "history-case"
    scope = case / "scope.md"
    created = re.search(r"(?m)^- created: (.+)$", scope.read_text(encoding="utf-8-sig"))
    assert created
    timeline = case / "timeline.md"
    original = timeline.read_bytes() + b"\n\n## operator-event\n- evidence: E-123\n"
    timeline.write_bytes(original)
    workitems = case / "workitems.md"
    workitems.write_text("# Work Items\nWI-002 | done | E-123\n", encoding="utf-8")
    expected_items = workitems.read_bytes()

    second = run_ps(*arguments, "-AuthGranted", "-TargetUrl", "https://example.test/")
    assert second.returncode == 0, second.stdout + second.stderr
    assert timeline.read_bytes().startswith(original), "case-init erased prior events"
    assert workitems.read_bytes() == expected_items, "case-init reset existing work"
    scope_text = scope.read_text(encoding="utf-8-sig")
    assert "- status: granted" in scope_text
    if contract == "created":
        assert f"- created: {created[1]}" in scope_text, "creation time was reset"
        updated = re.search(r"(?m)^- updated: (.+)$", scope_text)
        assert updated and updated[1] != created[1]
    if contract == "update_event":
        suffix = timeline.read_bytes()[len(original):].decode("utf-8")
        assert suffix.count("| lead | scope_update") == 1
        assert "case scope updated" in suffix
        assert "case directory created" not in suffix


@pytest.mark.parametrize("quick", [False, True])
def test_empty_selected_routing_benchmark_is_not_green(
    tmp_path: Path, quick: bool,
) -> None:
    benchmark = tmp_path / "benchmark.json"
    cases = [{"hint": "apk", "expected": "apk", "quick": False}] if quick else []
    benchmark.write_text(json.dumps({"cases": cases}), encoding="utf-8")
    result = run_ps(
        "-File", str(SCRIPTS / "test-routing.ps1"),
        "-Benchmark", str(benchmark), "-LogDir", str(tmp_path / "logs"),
        *(["-Quick"] if quick else []),
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "0/0" not in result.stdout


def test_unknown_bootstrap_capability_has_failure_exit() -> None:
    result = run_ps(
        "-File", str(SCRIPTS / "bootstrap-reverse.ps1"),
        "-Capability", "deep-review-nonexistent-capability", "-SkipRefresh",
    )
    assert "missing-definition" in result.stdout, result.stdout + result.stderr
    assert result.returncode == 1, "unknown capability incorrectly reported success"


def test_supply_chain_function_loader_preserves_ci_exit(tmp_path: Path) -> None:
    """Run the real loader in a copied sandbox, not its user-profile fixtures."""
    driver = (SCRIPTS / "test-bootstrap-supply-chain.ps1").read_text(
        encoding="utf-8-sig",
    )
    loader = driver.split("# BEGIN offline bootstrap function loader", 1)[1].split(
        "# END offline bootstrap function loader", 1,
    )[0]
    scripts = tmp_path / "scripts"
    library = scripts / "lib"
    library.mkdir(parents=True)
    shutil.copy2(SCRIPTS / "bootstrap-reverse.ps1", scripts)
    for name in ("ToolDiscovery.ps1", "BootstrapSupplyChain.ps1"):
        shutil.copy2(SCRIPTS / "lib" / name, library)
    probe = scripts / "probe.ps1"
    probe.write_text(
        "$ErrorActionPreference = 'Stop'\n$global:LASTEXITCODE = 0\n"
        + loader
        + "\nGet-Command Ensure-Capability,Start-AnythingAnalyzerService "
        "-ErrorAction Stop | Out-Null\nWrite-Output 'loader completed'\n",
        encoding="utf-8-sig",
    )
    literal = str(probe).replace("'", "''")
    result = run_ps(
        "-Command", f". '{literal}'; if ($LASTEXITCODE) {{ exit $LASTEXITCODE }}",
    )
    assert "loader completed" in result.stdout, result.stdout + result.stderr
    assert result.returncode == 0, "function loading contaminated the CI exit status"


def load_capability_function() -> str:
    bootstrap = str(SCRIPTS / "bootstrap-reverse.ps1").replace("'", "''")
    # Parse and load just Ensure-Capability, as the repository's own bootstrap
    # tests do; never run the bootstrap installation entry point.
    return f"""
$ErrorActionPreference = 'Stop'
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    '{bootstrap}', [ref]$tokens, [ref]$errors)
if ($errors.Count) {{ throw 'Unexpected bootstrap parse errors' }}
$functionAst = $ast.Find({{
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $node.Name -eq 'Ensure-Capability'
}}, $true)
. ([scriptblock]::Create($functionAst.Extent.Text))
"""


@pytest.mark.parametrize("route", ["direct", "npx", "missing"])
def test_failed_npm_postinstall_is_not_reported_as_success(route: str) -> None:
    command_lookup = "'MockPost'" if route == "direct" else "$null"
    fallback_command = "'MockPost'" if route != "missing" else "$null"
    node_lookup = f"if ($Name -eq 'npm') {{ 'MockNpm' }} else {{ {fallback_command} }}"
    command = load_capability_function() + f"""
function Get-ReverseBootstrapDefinition {{
    [pscustomobject]@{{
        bootstrapKind = 'npm-global'; npmPackage = 'offline-stub-package'
        postInstall = 'mock-post chromium'
    }}
}}
function Get-ReverseCapabilityState {{ $null }}
function Ensure-NodeRuntime {{}}
function Get-NodeCommandPath {{ param($Name); {node_lookup} }}
function Get-FirstCommandPath {{ {command_lookup} }}
function MockNpm {{ $global:LASTEXITCODE = 0 }}
function MockPost {{ $global:LASTEXITCODE = 23 }}
Ensure-Capability -Name 'offline-stub'
"""
    result = run_ps("-Command", command)
    assert result.returncode != 0, "post-install exit 23 was silently accepted"
    assert "post-install" in result.stderr.lower(), result.stdout + result.stderr


def test_failed_npm_setup_is_not_reported_as_success(tmp_path: Path) -> None:
    setup = tmp_path / "setup.ps1"
    setup.write_text("exit 23\n", encoding="utf-8")
    setup_literal = str(setup).replace("'", "''")
    shell = str(shutil.which("pwsh")).replace("'", "''")
    command = load_capability_function() + f"""
function Get-ReverseBootstrapDefinition {{
    [pscustomobject]@{{
        bootstrapKind = 'npm-global'; npmPackage = 'offline-stub-package'
        setupScript = '{setup_literal}'
    }}
}}
function Get-ReverseCapabilityState {{ $null }}
function Ensure-NodeRuntime {{}}
function Get-NodeCommandPath {{ 'MockNpm' }}
function MockNpm {{ $global:LASTEXITCODE = 0 }}
function Get-PreferredPowerShellPath {{ '{shell}' }}
Ensure-Capability -Name 'offline-stub'
"""
    result = run_ps("-Command", command)
    assert result.returncode != 0, "setup script exit 23 was silently accepted"
    assert "setup" in result.stderr.lower(), result.stdout + result.stderr
