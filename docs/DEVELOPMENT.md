# 開發環境

維護者與 AI 接手用的開發文件。產品使用方式在 [`README.md`](../README.md)；上游同步在
[`UPSTREAM.md`](UPSTREAM.md)；決策在 [`DECISIONS.md`](DECISIONS.md)。

## 架構

```text
skills/                     核心安全技能模組（45 個 Skill 目錄）
  ├── config/routing.json   路由規則單一真相源（R0–R43）
  ├── MASTER-ROUTING.md     快速路由表與優先級
  ├── routing.md            完整三軸路由決策矩陣
  ├── ops/                  行為鏈契約（scope, evidence, roles, timeline）
  └── scripts/              路由執行、初始化與工具自舉腳本
      ├── master-route.ps1  Windows 路由執行器
      ├── case-init.ps1     案件工作區與授權合約初始化
      └── verify-*.ps1      路由一致性與契約驗證器

plugins/reverse-skill/      Codex / 宿主適配器插件
burp-mcp-full/              Burp Suite MCP 橋接套件（Java + MCP Server）
CTF-Sandbox-Orchestrator/   CTF 沙盒編排與評測環境
kali/                       Kali Linux 專用工具發現與 bootstrap 腳本
tools/                      Fork 維護工具集（dev_check, check_upstream, check_freshness, check_links）
tests/                      Fork 維護測試套件（pytest）
```

`skills/`、`plugins/`、`burp-mcp-full/`、`CTF-Sandbox-Orchestrator/`、`kali/` 是上游產品本體。
`tools/`、`tests/`、`FORK.md`、`NOTICE.md`、`AGENTS.md` 是本 fork 的開發與治理骨架。

## 本機開發（Windows）

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
$env:PYTHONUTF8 = "1"
pwsh -NoProfile -File tools\dev_check.ps1
```

先決條件：Python 3.12+、PowerShell 7（`pwsh`）或 Windows PowerShell 5.1。

## Canonical Gate

`tools\dev_check.ps1` 會依序執行：

1. `python -m compileall`（維護用 Python 腳本編譯）
2. `ruff check --select E9,F`（代碼語法與 pyflakes）
3. `pytest tests/ -q`（維護測試契約）
4. `python tools/check_links.py`（Markdown 相對連結）
5. `python skills/scripts/verify-repository-security.py`（倉庫安全邊界）
6. `python skills/scripts/verify-doc-links.py`（內部文件索引連結）
7. `pwsh skills/scripts/verify-routing-coherence.ps1`（路由規則一致性與供應鏈釘選）
8. `pwsh skills/scripts/test-routing.ps1 -Quick`（44 條基準快速回歸）

推送到 `origin/main` 前必須確保 `tools\dev_check.ps1` 綠燈。

## 工具設定

`pyproject.toml` **只放工具設定**，沒有 `[project]` 與 `[build-system]`：本 repo 是
Markdown Agent Skills、PowerShell 與 Python 路由套裝，不是 Python 發行套件。

## 依賴新鮮度

`tools/check_dependency_freshness.py` 檢查兩處宣告：`requirements-dev.txt` 的
`pytest`／`ruff` 對 PyPI，以及 `.github/workflows/*.yml` 裡每一個釘選 SHA 的 GitHub Action 對
GitHub Releases API。`.github/workflows/dependency-freshness.yml` 每月跑一次。紅燈出口為：
`# freshness-hold:`（寫在宣告那一行）或 `.github/dependency-deferrals.json` 的 `deferredLatest`。

## 不要做的事

- 不要直接 push 到 `upstream` remote。
- 不要把產品 `SKILL.md` 改寫成維護說明。
- 不要提交真實目標滲透資料、分析受害日誌或 API 憑證。
