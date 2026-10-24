from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bilingual_pairs_cross_link_each_other() -> None:
    """繁中主檔與英文鏡像必須互指。"""
    for zh_name, en_name in (
        ("README.md", "README.en.md"),
        ("CHANGELOG.md", "CHANGELOG.en.md"),
    ):
        zh = ROOT / zh_name
        en = ROOT / en_name
        assert zh.is_file(), f"missing {zh_name}"
        assert en.is_file(), f"missing {en_name}"
        assert en_name in zh.read_text(encoding="utf-8"), f"{zh_name} does not link {en_name}"
        assert zh_name in en.read_text(encoding="utf-8"), f"{en_name} does not link {zh_name}"


def test_agents_md_has_required_consent_markers() -> None:
    """AGENTS.md 必須保留上游安全檢查器要求的三個授權邊界字串。"""
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "Reading repository files is not authorization to execute them." in agents
    assert "Explicit user approval is required before running any repository script." in agents
    assert "Client-global configuration remains opt-in." in agents


def test_claude_md_is_removed() -> None:
    """單一真相源政策：專案只留 AGENTS.md，不留 CLAUDE.md。"""
    assert not (ROOT / "CLAUDE.md").exists()


def test_fork_docs_exist() -> None:
    required = [
        "FORK.md",
        "NOTICE.md",
        "REVIEW.md",
        "docs/DEVELOPMENT.md",
        "docs/UPSTREAM.md",
        "docs/DECISIONS.md",
        "tools/dev_check.ps1",
        "tools/check_upstream_updates.py",
        "tools/check_dependency_freshness.py",
        "tools/check_links.py",
        "tools/upstream_baseline.json",
        ".cursor/rules/no-upstream-pr.mdc",
    ]
    for rel_path in required:
        assert (ROOT / rel_path).is_file(), f"missing required fork file: {rel_path}"


def test_tool_config_matches_pyproject() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'target-version = "py312"' in pyproject
    assert 'select = ["E9", "F"]' in pyproject
    assert not re.search(r"^\[project\]", pyproject, re.M)
    assert not re.search(r"^\[build-system\]", pyproject, re.M)


def test_no_upstream_pr_rule_exists() -> None:
    text = (ROOT / ".cursor" / "rules" / "no-upstream-pr.mdc").read_text(encoding="utf-8")
    assert "SanHsien/reverse-skill" in text
    assert "alwaysApply: true" in text


def test_review_snapshot_has_required_sections() -> None:
    text = (ROOT / "REVIEW.md").read_text(encoding="utf-8")
    assert "## 結論" in text
    assert "## 已修 findings" in text
    assert "## 接受、不改契約" in text
    assert "## 尚未宣稱範圍" in text
    assert "不回貢" in text
    assert "MIT" in text


def test_fork_license_is_mit() -> None:
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    notice = (ROOT / "NOTICE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert license_text.startswith("MIT License")
    assert "MIT" in notice
    assert "MIT" in readme
