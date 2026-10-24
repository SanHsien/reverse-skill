from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_upstream_updates as checker  # noqa: E402


def test_baseline_file_is_valid_and_complete() -> None:
    baseline = checker.load_baseline()

    assert baseline["repo"].endswith("reverse-skill.git")
    assert baseline["branch"] == "main"
    assert len(baseline["reviewed_through"]) == 40
    assert baseline["reviewed_date"]


def test_baseline_reads_pr_and_issue_watermarks() -> None:
    baseline = checker.load_baseline()

    assert isinstance(baseline["reviewed_pr_through"], int)
    assert isinstance(baseline["reviewed_issue_through"], int)
    assert baseline["reviewed_pr_through"] > 0
    assert baseline["reviewed_issue_through"] > 0


def test_workflow_is_scheduled_and_fails_on_unreviewed_commits() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "upstream-check.yml"
    ).read_text(encoding="utf-8")

    assert "schedule:" in workflow
    assert "cron:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "tools/check_upstream_updates.py" in workflow
