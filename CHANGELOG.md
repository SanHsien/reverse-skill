[English](CHANGELOG.en.md) | 中文版

# 變更紀錄

格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，新的在上面。
本檔只記錄**本 fork 的維護歷史**（2026-10-03 起）；上游
[`zhaoxuya520/reverse-skill`](https://github.com/zhaoxuya520/reverse-skill) 的產品演進見其自身歷史
與 [`docs/UPSTREAM.md`](docs/UPSTREAM.md) 的審查清冊。逐筆採用／略過的理由記在
[`docs/DECISIONS.md`](docs/DECISIONS.md)。

---

## [Unreleased]

## [1.0.1] - 2026-10-03

### 新增

- **Windows-first 維護骨架**：
  - 整合 `AGENTS.md` 作為單一代理規範入口（包含上游 3 項嚴格同意授權邊界），依政策移除獨立 `CLAUDE.md`。
  - 新增 `NOTICE.md`、`FORK.md`、`docs/DEVELOPMENT.md`、`docs/UPSTREAM.md`、`docs/DECISIONS.md` 與 `REVIEW.md`。
  - 新增維護工具集 `tools/`：
    - `dev_check.ps1`：Windows 本機一鍵驗證 gate（Python 語法編譯、Ruff E9+F、Pytest、文件相對連結、倉庫安全邊界、路由一致性、快速回歸測試）。
    - `check_upstream_updates.py`：上游 commit／PR／issue 三軸未審查追蹤器。
    - `check_dependency_freshness.py`：GitHub Actions 釘選 SHA 與 `requirements-dev.txt` 新鮮度稽核。
    - `check_links.py`：維護文件相對連結檢查器。
    - `upstream_baseline.json`：記錄上游 baseline（SHA `cab634b`、PR #170、Issue #166）。
  - 新增維護測試套件 `tests/`：
    - `test_upstream_check.py`：baseline 規格與 watermark 驗證。
    - `test_dependency_freshness.py`：依賴與 Actions 釘選比對契約測試。
    - `test_links.py`：文件相對連結與雙語 README 互指測試。
    - `test_fork_docs.py`：fork 維護文件契約測試。
  - 新增 `.cursor/rules/no-upstream-pr.mdc` 限制 PR 目標為 `SanHsien/reverse-skill`。
  - 新增 `.editorconfig` 規範縮排與換行。
  - 新增 GitHub Workflows：
    - `.github/workflows/upstream-check.yml`：每週自動檢查上游 commit／PR／issue。
    - `.github/workflows/dependency-freshness.yml`：每月依賴新鮮度追蹤。
- **公開入口繁中化**：
  - `README.md` 翻新為繁體中文主檔，強調作為「AI Coding 完成」與「正式上線」之間的安全檢驗閘門。
  - 原英文 README 鏡像保留為 `README.en.md`，並加上雙語切換導航。
