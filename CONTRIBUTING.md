# 貢獻指南

## 開始前

1. 先讀 [`AGENTS.md`](AGENTS.md)、[`FORK.md`](FORK.md)、[`README.md`](README.md) 與 [`REVIEW.md`](REVIEW.md)。
2. 確認問題在最新 `main` 仍可重現，並查過既有 Issues 與 PRs。
3. 產品核心路由（`skills/config/routing.json`）、Skill 模組或工具清單的跨平台實質變更，優先考慮回報 [`zhaoxuya520/reverse-skill`](https://github.com/zhaoxuya520/reverse-skill)。
4. 嚴格遵守授權邊界：不要提交真實目標資料、私鑰、API key、未授權滲透測試產物或 `.env`。

## 本機開發與驗證

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
pwsh -NoProfile -File tools\dev_check.ps1
```

## 提交規範

本 fork 由維護者直接推 `origin/main`，不開短期功能分支。改動前先通過 Windows gate。

- 一次提交聚焦一個問題。
- Bug 修正先附可重現失敗測試；新行為需涵蓋成功、邊界與錯誤路徑。
- 修改使用方式時同步更新 `README.md` 與 `README.en.md`。
- 提交訊息採用 Conventional Commits（`fix:`、`feat:`、`docs:`、`test:`、`chore:`）。
- 對上游開 PR 需要維護者在當次對話明確同意回貢；平常 PR、push、release 一律指向 `SanHsien/reverse-skill`。
