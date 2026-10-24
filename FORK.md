# Fork 維護說明

本 repo fork 自 [`zhaoxuya520/reverse-skill`](https://github.com/zhaoxuya520/reverse-skill)，
沿用 MIT License 與完整 Git 歷史。

## 為什麼維護 fork

- **定位為上線前的安全防線**：現在越來越多系統直接由 AI（Codex、Claude Code、Cursor）生成，畫面正常且功能能跑不代表能安全上線。reverse-skill 作為資安 Skill 路由包，放在「AI 開發完成」與「正式上線」中間：先檢查、修正、再驗證，最後才上線。
- **Windows-first 維護**：Windows 11 + PowerShell（pwsh 7 與 Windows PowerShell 5.1）是主要開發、除錯與完整驗收環境；Ubuntu CI 補充跨平台相容性。
- **公開入口以繁體中文為主**：主入口為繁體中文 `README.md`，英文原文鏡像保留在 `README.en.md`，簡體中文上游說明保留在 `README_zh.md`。
- **標準化維護鷹架**：建立 Windows 本機一鍵驗證 gate（`tools/dev_check.ps1`）、三軸上游追蹤（`tools/check_upstream_updates.py`）、依賴新鮮度稽核（`tools/check_dependency_freshness.py`）與文件相對連結檢查（`tools/check_links.py`）。

**回貢判準：修的是上游跨平台的 bug 或核心路由邏輯就送回去；這裡獨創的維護文件與 Windows 開發骨架留在這裡。**

## 與上游的差異

| 項目 | 說明 |
|---|---|
| `README.md` | 繁中主檔，定位 AI 安全交付閘門；標頭附雙語導航 |
| `README.en.md` | 英文原文鏡像 |
| `README_zh.md` | 保留上游簡體中文原檔 |
| `AGENTS.md` | 整合上游 `AGENTS.md` 與 `CLAUDE.md`，並加入 fork 維護與 Windows gate 規範 |
| `NOTICE.md` / `FORK.md` | 來源、授權與同步說明 |
| `tools/dev_check.ps1` | Windows 本機一鍵驗證 gate（Python 語法、Ruff、Pytest、文件連結、安全邊界、路由一致性） |
| `tools/check_upstream_updates.py` | 上游 commit、PR、issue 三軸未審查追蹤 |
| `tools/check_dependency_freshness.py` | GitHub Actions 釘選 SHA 與 `requirements-dev.txt` 新鮮度檢查 |
| `tools/check_links.py` | 維護文件之間的相對連結檢查 |
| `.cursor/rules/no-upstream-pr.mdc` | 限制 PR 與 push 目標為 `SanHsien/reverse-skill` 的編輯器防呆規則 |
| `.github/workflows/upstream-check.yml` | 每週自動檢查上游更新 |
| `.github/workflows/dependency-freshness.yml` | 每月自動檢查依賴新鮮度 |
| `docs/DECISIONS.md` / `docs/UPSTREAM.md` / `docs/DEVELOPMENT.md` | fork 維護決策、上游紀錄與本機開發指南 |

產品 `skills/`、`plugins/`、`kali/`、`burp-mcp-full/`、`CTF-Sandbox-Orchestrator/` 以上游為準。

## 分支與 remote

- `origin/main`：SanHsien 維護線，日常變更直接推此分支。
- `upstream/main`：上游原始倉庫，只追蹤、不推送。
- 同步方式見 [`docs/UPSTREAM.md`](docs/UPSTREAM.md)。

## 換一台電腦怎麼開發

```powershell
git clone https://github.com/SanHsien/reverse-skill.git
cd reverse-skill
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
pwsh -NoProfile -File tools\dev_check.ps1
```
