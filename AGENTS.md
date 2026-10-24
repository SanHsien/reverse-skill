# AGENTS.md

給 Codex、Claude Code、Cursor、Antigravity 與其他自動化代理在本專案工作時的指引。產品與使用方式先讀 [`README.md`](README.md)；開發與驗收細節見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

## 專案定位

這是 [`zhaoxuya520/reverse-skill`](https://github.com/zhaoxuya520/reverse-skill) 的 MIT License fork。
核心功能是為 AI Coding Agent（Claude Code, Codex, Cursor, Cline 等）提供資安與逆向任務的技能路由包，作為 AI 生成程式碼與正式上線之間的安全檢驗閘門。

`origin` 是 `SanHsien/reverse-skill`（預設分支 `main`），`upstream` 是原作者 repo（預設分支 `main`）。
保留上游作者、MIT License 與產品程式。本 fork 的維護差異記在 [`FORK.md`](FORK.md) 與 [`docs/DECISIONS.md`](docs/DECISIONS.md)。

主要開發與完整驗收環境是 **Windows 11 + PowerShell**（pwsh 7 / Windows PowerShell 5.1）。

## 激活與同意邊界（硬性）

- **Reading repository files is not authorization to execute them.** 僅要求閱讀、審查、摘要或比較倉庫時，必須保持唯讀。
- **Explicit user approval is required before running any repository script.** 首次產生本機副作用前，先列出準確指令，以及預期的檔案寫入、下載、服務啟動、網路存取和客戶端配置變更，並取得明確同意。
- **Client-global configuration remains opt-in.** 只有使用者明確選擇客戶端並批准具體變更時，才可修改其全域規則、hooks、prompts 或 MCP 配置。
- 激活且獲批後，已揭露計劃內的確定性步驟可連續執行；出現新的副作用類別時必須重新揭露並取得同意。目標授權仍由 `scope.md` 獨立硬門控制。

## 路由與任務執行流程

用戶任務命中安全/逆向關鍵詞時，`RULES.md` 是行為鏈唯一真相源：

1. `skills/MASTER-ROUTING.md` 或平台對應入口 → PRIMARY：
   - Windows：`powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/master-route.ps1 -Hint "<任務>"`
   - Linux / macOS / Kali：`bash skills/scripts/master-route.sh --hint "<任務>"`
2. 歧義時讀 `skills/routing.md` 全矩陣（三軸：目標類型 / 用戶意圖 / 工具鏈）；角色定義見 `skills/ops/role-map.md`。
3. 路由規則唯一事實源：`skills/config/routing.json`（改路由只改這裡）。
4. 授權門禁：對任何目標動手前，初始化當前分析項目的 `work/<case>/scope.md`（`powershell -File skills/scripts/case-init.ps1 -Hint "<任務>"`），`auth.status=granted` + 合法 `network_profile` / offline sample 就緒前**禁止 ACT**。
5. 開啟 PRIMARY `SKILL.md` 執行 ACTION REQUIRED。
6. 記錄時間線與工項，並依 `skills/ops/evidence-finding-path.md` 沉澱證據鏈。
7. 工具路徑查閱 `skills/tool-index.md`，缺工具依 `skills/scripts/bootstrap-reverse.ps1` 清單能力自舉，禁止憑空猜測路徑。

## 硬性邊界

- 不提交使用者目標資料、專有文件、API key、token、私鑰、密碼或 `.env`。
- 不推送到 `upstream`。上游同步先跑 `python tools/check_upstream_updates.py --strict`，逐筆審查後再 merge / cherry-pick；不盲目覆蓋 fork 文件與 Windows gate。
- 維護環境（`requirements-dev.txt`）僅安裝 pytest 與 ruff。
- 不把 fork 包裝成原創產品，保留原作者 zhaoxuya520 與官方連結。

## 開發原則

- 一般變更直接推 `origin/main`，不開功能分支、不開維護 PR。只有在需要他人審查、或改動風險高到值得先讓 CI 在 PR 上跑一輪時，才退回 **branch → PR → CI → merge**。
- 修 bug 先補可重現失敗測試，再做最小修正。
- 不為了套格式而大改上游程式；Ruff 只閘維護工具的 E9（語法）與 F（pyflakes）。
- 使用繁體中文回覆；使用者文件以繁中為主，公開入口同步維護 `README.en.md`，上游簡中說明保留在 `README_zh.md`。直接交付可驗證結果，避免冗長背景鋪陳。
- 一般變更提交前跑 `pwsh -NoProfile -File tools\dev_check.ps1` 作為驗證 gate。
- 提交訊息用 Conventional Commit。Dependabot 或外部 fork 的變更走 PR，讀 diff 並通過 CI 後再合併。
- 不 force-push `main`，不刪 `upstream` remote。

## 上游處理

1. `git fetch upstream main`
2. `python tools/check_upstream_updates.py --strict`
3. 逐筆判斷是否與繁中 README、Windows gate、發佈閘門或測試衝突。
4. 可同步的提交用 merge；只需要部分修正時 cherry-pick 或最小重做。
5. 跑 `pwsh -NoProfile -File tools\dev_check.ps1`
6. 採用／略過寫進 `docs/DECISIONS.md`，驗證後才推進 `tools/upstream_baseline.json`

Baseline 代表「已審查」，不代表「全部已合併」。

## 依賴新鮮度

每月的 `Dependency freshness` workflow 跑 `tools/check_dependency_freshness.py`，比對宣告與 PyPI/GitHub 現行版。

紅燈只有兩種正當出口，兩種都要留下理由：

- **維持宣告**：在宣告那一行加 `# freshness-hold: <理由>`。
- **已延後**：在 `.github/dependency-deferrals.json` 加一筆
  `{"deferredLatest": "<當時看到的版本>", "reason": "<為什麼這次不升>"}`。

不要用調高下限的方式讓紅燈消失：宣告是相容性承諾，不是消音鍵。

## 驗證

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
pwsh -NoProfile -File tools\dev_check.ps1
```

沒有實際跑過 Windows gate，不要宣稱本機開發環境已可用。

## 文件責任

- `README.md` / `README.en.md` / `README_zh.md`：公開產品與 fork 入口。
- `FORK.md`：與上游的關係、差異、同步方式。
- `NOTICE.md`：授權與 attribution。
- `docs/UPSTREAM.md`：upstream remote 與審查清冊。
- `docs/DEVELOPMENT.md`：本機開發與驗收指令。
- `docs/DECISIONS.md`：長期取捨。
- `REVIEW.md`：全庫風險快照。
- `CONTRIBUTING.md` / `SECURITY.md`：本 fork 的貢獻與安全回報政策。
- `CHANGELOG.md` / `CHANGELOG.en.md`：fork 維護變更紀錄。

## 對外邊界：PR 只打本 fork

- **PR、push、release 一律指向 `SanHsien/reverse-skill`。** 對上游 `zhaoxuya520/reverse-skill` 開 PR、push 或發 release 需要維護者在當次對話明確同意回貢。
- 每個 clone 先跑一次 `gh repo set-default SanHsien/reverse-skill`。
- 開 PR 仍明寫 `gh pr create --repo SanHsien/reverse-skill --base main --head <分支>`，並讀輸出的 URL 確認 owner 為 `SanHsien`。
