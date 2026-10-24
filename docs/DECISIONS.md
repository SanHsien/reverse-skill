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
- 依據維護者跨 repo 統一標準（2026-09-21 指示），各 repo 只留 `AGENTS.md` 作為單一真相源。
- 完整保留 3 項同意邊界字串，確保上游安全檢驗腳本維持綠燈。

## 2026-10-03：依賴新鮮度檢查涵蓋 GitHub Actions 與 Python dev 依賴

**決定**：`tools/check_dependency_freshness.py` 同時檢查 `requirements-dev.txt`（PyPI）與 `.github/workflows/*.yml` 裡釘選 SHA 的 Actions（GitHub Releases API）。

**理由**：確保 CI 依賴與本機維護工具的版本漂移具備可見性與可查證性。

## 2026-10-24：CodeQL `js/file-access-to-http`（alert #1，`burp-mcp-full/mcp-bridge.js:44`）判讀為設計如此

**決定**：不改程式碼；alert 保留，由維護者決定是否 dismiss。

**資料流證據**：
- 讀檔來源：`burp-mcp-full/mcp-bridge.js:30-31` 只讀固定路徑 `~/.burp-mcp-token`（`os.homedir()` 拼接常數檔名，無外部輸入影響路徑）；`BURP_MCP_TOKEN` 環境變數存在時連檔案都不讀（`:28`）。
- 檔案由誰寫：Burp 擴充自己產生隨機 token 並以 owner-only 權限原子寫入同一路徑（`burp-mcp-full/src/main/java/com/burpmcp/McpHttpServer.java:61-79`、`:81-95`）。檔案擁有者即執行 bridge 的使用者本人。
- 送出內容：檔案內容只進 `Authorization: Bearer` header（`mcp-bridge.js:37`），用在 `GET /tools`（`:44-46`）與 `POST /`（`:93-95`）。不會把任意檔案內容送出。
- 送往何處：`hostname`/`port` 只來自 `BURP_MCP_HOST`（預設 `127.0.0.1`）與 `BURP_MCP_PORT`（預設 `9876`）環境變數（`mcp-bridge.js:24-25`），與檔案內容無關；對端是只綁 `127.0.0.1` 的 Burp 擴充 HTTP API（`McpHttpServer.java:56`），正是驗這把 token 的服務。

**理由**：這是本機共享密鑰認證的標準做法：token 由服務端產生、寫入使用者家目錄，客戶端讀出後回送給同一個服務。目的地不受檔案內容左右，讀檔路徑固定，外送內容僅限該 token。唯一能把 token 送到別處的方式是使用者自行設定 `BURP_MCP_HOST`，屬使用者自身的設定權限，不構成攻擊面。

## 2026-10-25：上游審查（PR #171–#183、issue #173–#180；commit 水位不動，仍為 `cab634b`）

上游 commit 軸無新項目；PR／issue 軸有 9 個 PR、4 個 issue。`git apply --check` 全部可乾淨套用，因為本 fork 產品碼與上游一致。

**採用**（移植到 main，皆附回歸測試）：
- #176／issue #175：`skills/scripts/verify-doc-links.py` 補 percent-encoded 本機連結（本 fork 的 `tools/check_links.py` 早已 `unquote`，CI 的另一支驗證器沒有）。連同其測試與 CI 步驟。
- #181：case review 拒收重複 ID、懸空參照、不合規的 Finding 分類；`consolidate-evidence` 在寫入前拒絕路徑式 ID（例如 `../outside`）與重複 Finding。有路徑逃出 evidence 目錄的風險，所以採用。
- #182：R7 (radare2) 中文情境基準案例（15 行，純測試）。
- #179（只取 `skills/config/routing.json` 與 `skills/tests/routing-benchmark.json`）：`\b` 在 .NET／JS 把 CJK 視為 `\w`，「分析这个APK」緊貼 ASCII 關鍵字時沒有詞界而退回 R0，對繁中／簡中為主的使用者是真缺陷；改用 ASCII 專用的 lookaround 邊界，並含其 R3 簽名參數關鍵字與 19 個基準案例。
- issue #180（上游無對應 PR）：`bootstrap-reverse.ps1` 在 `Set-StrictMode -Version Latest` 下對單一子項目呼叫 `.Count` 會丟例外，本 fork 同一行存在；改成 `@(Get-ChildItem ...)`。

**略過**：
- #171、#172、#178（field-journal 新文章）、#183（iOS fairplay-decrypt 文件與一行路由）：第三方投稿，上游尚未合併。這類內容會被 skill 載入當作操作指引，未經上游審過不收。觸發條件：上游合併後經 commit 軸抵達，再逐項審。
- #179 內七篇 field-journal 文件：同上。
- #174：上游已關閉未合併，內容是 field-journal 文章，同上不收。
- issue #173（Cursor 用戶端被 Request blocked）：用戶端環境問題，非本 repo 程式缺陷。
- issue #177（要求把 `reverse-skill.png` 轉成 jpg）：不適用；本 fork 公開入口圖維持 png。

水位：`reviewed_pr_through` 170 → 183、`reviewed_issue_through` 166 → 180、`reviewed_date` 2026-10-25。
