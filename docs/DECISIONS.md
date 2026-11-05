# 維護決策

## 2026-11-06：保留維護工具下限，以常態政策記錄 freshness-hold

**決定**：保留 `pytest>=9.1` 與 `ruff>=0.16`，在各宣告行加入具體的 `freshness-hold` 理由；移除被此常態政策取代的 Ruff 0.17.2 暫緩紀錄。這不是精確釘版，安裝仍允許最新版。

**理由**：本次 PyPI 回報 pytest 9.2.0 與 Ruff 0.17.3。維護測試沒有要求 pytest 9.2 專屬功能，Ruff gate 僅使用 E9、F；沒有相容性需求足以提高下限。已閱讀 [pytest 9.2 變更紀錄](https://docs.pytest.org/en/stable/changelog.html#pytest-9-2-0-2026-10-27) 與 [Ruff 0.17.3 發佈說明](https://github.com/astral-sh/ruff/releases/tag/0.17.3)。常態下限政策應使用行末 hold，而非每次新版發佈便延長暫緩紀錄。

**限制與重審條件**：hold 表達下限政策，不代表驗證所有支援版本；若測試或規則實際依賴新版功能，再調整下限並記錄相容性證據。本次未修改 Actions 釘選或 workflow；本機 GitHub API 回傳 HTTP 403 rate limit exceeded，Actions latest 尚無法完成查證，不以 hold 掩蓋查詢失敗。

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
- #182：R7 (radare2) 中文情境基準案例（3 個案例、15 行，純測試）。
- #179（只取 `skills/config/routing.json` 與 `skills/tests/routing-benchmark.json`）：`\b` 在 .NET／JS 把 CJK 視為 `\w`，「分析这个APK」緊貼 ASCII 關鍵字時沒有詞界而退回 R0，對繁中／簡中為主的使用者是真缺陷；改用 ASCII 專用的 lookaround 邊界，並含其 R3 簽名參數關鍵字與 19 個基準案例。
- issue #180（上游無對應 PR）：`bootstrap-reverse.ps1` 在 `Set-StrictMode -Version Latest` 下對單一子項目呼叫 `.Count` 會丟例外，本 fork 同一行存在；改成 `@(Get-ChildItem ...)`。

**略過**：
- #171、#172、#178（field-journal 新文章）、#183（iOS fairplay-decrypt 文件與一行路由）：第三方投稿，上游尚未合併。這類內容會被 skill 載入當作操作指引，未經上游審過不收。觸發條件：上游合併後經 commit 軸抵達，再逐項審。
- #179 內七篇 field-journal 文件：同上。
- #174：上游已關閉未合併，內容是 field-journal 文章，同上不收。
- issue #173（Cursor 用戶端被 Request blocked）：用戶端環境問題，非本 repo 程式缺陷。
- issue #177（要求把 `reverse-skill.png` 轉成 jpg）：不適用；本 fork 公開入口圖維持 png。

水位：`reviewed_pr_through` 170 → 183、`reviewed_issue_through` 166 → 180、`reviewed_date` 2026-10-25。

## 2026-10-31：依賴新鮮度檢查中 `# freshness-hold` 蓋過「抓不到 latest」與版本不可比失敗

**決定**：`tools/check_dependency_freshness.py` 的 `# freshness-hold: <理由>` 標記除清空 minimum 檢查外，亦蓋過 `latest is None`（Releases/tags 查無版本或 API 失敗）與 `incomparable`（標籤非數字版本無法比較）之 `check_failed` 判定。

**理由**：
- `AGENTS.md` 明確規定依賴新鮮度檢查紅燈的正當出口為「維持宣告：在宣告那一行加 `# freshness-hold: <理由>`」。
- 若 Action pin 來源在 GitHub Releases/tags 皆未發布版本（例如純以 commit SHA 釘選的內部或第三方 Action），或上游 tag 未遵循數字版本規則，過去 `check_failed` 仍會被判定為真，導致即使維護者已審查並依規定加註 hold，`--strict` 仍持續報錯。
- 維護者在宣告行留下 hold 標記與具體理由，已構成對該依賴凍結的顯式決策；此時不再讓已知並獲批的凍結宣告造成 check 失敗。但 `fetch` 回 None 同時代表「查無版本」與「API 失敗」，「查不到」不等於「沒有」，所以報表對這類列不能只寫 `HELD: <理由>`：latest 為 `unknown`，或不是可比較的版本時，狀態欄顯示 `HELD (latest not checked): <理由>`，明講最新版本沒有被檢查；latest 可比較時維持 `HELD: <理由>`。這是顯示層的區分，不改變是否紅燈。
- 未標記 hold 的依賴仍維持最嚴格的完整檢查（查無版本或解析失敗依舊報 `CHECK FAILED` 並讓 `--strict` 報警）。

**限制**：
- 僅限明確標記 `# freshness-hold:` 的項目放行；未標記 hold 者若抓不到 latest 仍視為 check 失敗。


## 2026-11-02：上游 PR #184–#186 與 issue #187

commit 軸無新增（仍是 `cab634b`）。三個 PR 取目前 head 讀完 diff，並用 `grep -nE '\S\s{40,}\S|eval\(|new Function|globalThis|[A-Za-z0-9+/]{120,}'` 掃隱藏內容，皆無命中。

**採用**：
- #186（`3500e59`，open，+35／-0，只動 `skills/tests/routing-benchmark.json`）：為 R33 的 `must` 正則補 7 個 `quick:false` 案例。純測試、只加不改；套用後完整 routing benchmark `TOTAL=207 PASS=207 FAIL=0`（原 200），`tools\dev_check.ps1` 綠。

**略過**：
- #184（`a852b05`，open，+127／-3）：field-journal 新文章，第三方投稿、上游尚未合併；這類內容會被 skill 載入當操作指引，未經上游審過不收（同 2026-10-25 的 #171／#172／#178）。觸發條件：上游合併後經 commit 軸抵達再逐項審。
- #185（`4090cac`，CLOSED，+528／-5，10 檔）：提交者在 2026-11-01 留言「誤操作開出的 PR，已撤回」，上游沒有收。內容為脫殼工具進 catalog 與 manifest，屬提交者自己的工具鏈擴充，非缺陷修正。其中 `test-routing.sh` 寫死裸 `bash`（本 fork 同樣，`skills/scripts/test-routing.sh:46`）在 Windows 會命中 WSL 空殼，但本 fork 的 Windows 閘門跑的是 `test-routing.ps1`，不經過該行，故不單獨摘取。觸發條件：若將來把 `test-routing.sh` 納入 Windows 閘門就回來修。
- issue #187（標題「Electrical Circuit Institute」，內文空、無留言、無對應 PR）：與本專案無關，不處理。

水位：`reviewed_pr_through` 183 → 186、`reviewed_issue_through` 180 → 187、`reviewed_date` 2026-11-02。
