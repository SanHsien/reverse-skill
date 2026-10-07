"""Contract tests for the dependency freshness check."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_dependency_freshness as checker  # noqa: E402


def test_comparison_uses_the_precision_the_declaration_states() -> None:
    assert not checker.is_newer_version("7.4.0", "7")
    assert checker.is_newer_version("8.0.0", "7")
    assert checker.is_newer_version("7.4.0", "7.3")
    assert not checker.is_newer_version("7.3.2", "7.3")


def test_prerelease_suffix_does_not_count_as_newer() -> None:
    assert not checker.is_newer_version("7.0.0rc1", "7.0.0")


def test_leading_v_is_stripped_for_github_action_tags() -> None:
    assert checker.is_newer_version("v7.1.0", "7.0.1")
    assert not checker.is_newer_version("v7.0.1", "7.0.1")


def test_hold_marker_is_read_off_the_declaring_line() -> None:
    text = "pytest>=9.1  # freshness-hold: pinned for stability\nruff>=0.16\n"
    packages = checker.parse_requirements(text, "requirements-dev.txt")

    assert len(packages) == 2
    assert packages[0]["hold"] == "pinned for stability"
    assert packages[1]["hold"] == ""


def test_deferral_expires_when_upstream_passes_reviewed_version() -> None:
    deferrals = {"pkg": ("1.0.0", "not now")}
    packages = [
        {
            "name": "pkg",
            "minimum": "0.9.0",
            "requirement": "pkg>=0.9.0",
            "source": "requirements-dev.txt",
            "hold": "",
        }
    ]

    status_same = checker.collect_status(packages, lambda _: "1.0.0", deferrals)
    assert not checker.needs_review(status_same[0])

    status_newer = checker.collect_status(packages, lambda _: "1.1.0", deferrals)
    assert checker.needs_review(status_newer[0])


def test_action_pin_with_subdirectory_is_parsed() -> None:
    text = (
        "- uses: github/codeql-action/init@3d3c42e5aac5ba805825da76410c181273ba90b1"
        " # v4.37.4\n"
    )
    packages = checker.parse_workflow_actions(text, "ci.yml")

    assert len(packages) == 1
    assert packages[0]["name"] == "github/codeql-action/init"
    assert packages[0]["minimum"] == "4.37.4"
    assert checker.action_repository("github/codeql-action/init") == "github/codeql-action"
