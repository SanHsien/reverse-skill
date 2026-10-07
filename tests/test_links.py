from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_links  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def test_maintainer_markdown_links_resolve() -> None:
    failures = 0
    for path in check_links.iter_documents():
        problems = check_links.check_document(path)
        failures += len(problems)
        for problem in problems:
            print(f"{path}: {problem}")
    assert failures == 0


def test_check_links_rejects_path_outside_repo(tmp_path: Path) -> None:
    doc = tmp_path / "note.md"
    doc.write_text("[here](.)\n", encoding="utf-8")
    problems = check_links.check_document(doc)
    assert any("逃出" in item for item in problems)


def test_check_links_reports_a_missing_target(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.setattr(check_links, "ROOT", tmp_path)
    doc = tmp_path / "note.md"
    doc.write_text("[gone](./does-not-exist.md)\n", encoding="utf-8")
    problems = check_links.check_document(doc)
    assert any("找不到" in item for item in problems)


def test_check_links_ignores_external_and_anchor_links(tmp_path: Path) -> None:
    doc = tmp_path / "note.md"
    doc.write_text(
        "[web](https://example.com) [mail](mailto:a@example.com) [anchor](#section)\n",
        encoding="utf-8",
    )
    problems = check_links.check_document(doc)
    assert problems == []


def test_bilingual_readmes_cross_link_each_other() -> None:
    zh = (ROOT / "README.md").read_text(encoding="utf-8")
    en = (ROOT / "README.en.md").read_text(encoding="utf-8")

    assert "README.en.md" in zh
    assert "README.md" in en
