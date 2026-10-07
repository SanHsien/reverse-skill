# 維護決策

## 2026-10-03：建立 Windows-first 維護型 fork

**決定**：fork `zhaoxuya520/reverse-skill`，保留 MIT License 與完整 Git 歷史，預設分支維持 `main` 以降低與上游同步摩擦。本線聚焦繁中公開入口、Windows 開發 gate、Windows CI，以及逐筆審查的上游追蹤。

**理由**：
- 現在很多原本不會寫程式的人，能靠 Codex、Claude Code、Cursor 把網站、App、會員系統做出來。畫面正常、功能能跑，很容易讓人覺得可以直接部署上線。
- 但 API Key 是否外洩、會員權限越權（BOLA/IDOR）、後端授權是否確實、測試帳號與 Debug 資料是否殘留正式環境，AI 寫完常會自信宣稱「已修復可以部署」。
- `reverse-skill` 作為資安 Skill 路由包，適合放在「AI 開發完成」與「正式上線」中間：先檢查、修正、再驗證，最後才上線。
- 原倉庫已提供 44 條路由規則、178 個回歸案例與 45 個核心 Skill 模組，但在 Windows 11 + PowerShell 環境下缺乏本機一鍵驗證 gate 與繁中入口。授權為 MIT，fork 修改同樣採用 MIT。

**限制**：
- 不把 fork 包裝成原創專案，保留原作者 zhaoxuya520 與 MIT 標示。
- 嚴格遵守授權邊界（`RULES.md` / `scope.md`），不進行未經授權的掃描或攻擊。
- 不覆寫或隨意變動產品目錄中的漏洞研究語料與各 Skill 本體。
- 不回貢上游，除非維護者在當次對話明確同意。

## 2026-10-03：維護線直接推 main

**決定**：fork 維護不開功能分支。改完在本機跑 gate，通過後直接推 `origin/main`。遠端只留 `main`；`upstream/main` 只追蹤。

**理由**：單人維護 fork，分支與 PR 沒有第二審查者，只增加同步成本。

**限制**：
- Dependabot 與外部 fork 仍可能開 PR，讀 diff 後再合併，不自動合併。
- 不推 `upstream`，不 force-push `main`，不刪 `upstream` remote。

## 2026-10-03：整合 AGENTS.md 並移除獨立 CLAUDE.md

**決定**：將原 `CLAUDE.md` 內容併入 `AGENTS.md`，並刪除 `CLAUDE.md`。同時在 `AGENTS.md` 中完整保留上游 `verify-repository-security.py` 強制要求的 3 個授權同意邊界標記。

**理由**：
- 依據主人跨 repo 統一標準（2026-09-21 指示），各 repo 只留 `AGENTS.md` 作為單一真相源。
- 完整保留 3 項同意邊界字串，確保上游安全檢驗腳本維持綠燈。

## 2026-10-03：依賴新鮮度檢查涵蓋 GitHub Actions 與 Python dev 依賴

**決定**：`tools/check_dependency_freshness.py` 同時檢查 `requirements-dev.txt`（PyPI）與 `.github/workflows/*.yml` 裡釘選 SHA 的 Actions（GitHub Releases API）。

**理由**：確保 CI 依賴與本機維護工具的版本漂移具備可見性與可查證性。
