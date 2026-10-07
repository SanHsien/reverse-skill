# 上游維護

## Remote

- Fork：`origin` → `https://github.com/SanHsien/reverse-skill.git`
- 原作者：`upstream` → `https://github.com/zhaoxuya520/reverse-skill.git`
- 追蹤分支：`main`

## 檢查新提交

```powershell
git fetch upstream main
python tools\check_upstream_updates.py --strict
```

工具以 `tools/upstream_baseline.json` 的 `reviewed_through` 為起點，列出所有未審查提交；
`reviewed_pr_through` 與 `reviewed_issue_through` 是另外兩個獨立水位，涵蓋 PR 與 issue
（用 `--state all`，已關閉但未合併的項目也算未審查）。有新項目或檢查失敗時，`--strict`
回傳非零；排程 workflow 也會因此明確失敗。

## 審查清冊

每次進行批次審查：

1. 讀 commit 主旨與變更檔案（open PR 必須讀 diff，禁止只憑標題結案）。
2. 判斷是否與繁中 README、Windows gate 或測試衝突。
3. 可直接同步的提交用 merge；只需要部分修正時 cherry-pick 或最小重做。
4. 跑 `pwsh -NoProfile -File tools\dev_check.ps1`。
5. 在 [`docs/DECISIONS.md`](DECISIONS.md) 記錄採用／略過理由（須引用具體檔案與衝突點）。
6. 驗證完成後才把 baseline 推進到已審查的完整 40 字元 SHA，以及對應的 PR／issue 水位。

Baseline 代表「已審查」，不代表「全部已合併」。

## 2026-10-03：fork 起點

本 fork 自上游 `main` `cab634bd855fc287f6e420c1f36fd1a6b9245960`（`fix: scope pwntools version probe environment`）建立。
此 SHA 設為第一個 `reviewed_through`。之後的上游 commit 才需要進入審查清冊。

水位：

- PR：已檢視至 **#170**（`reviewed_pr_through`）
- issue：已檢視至 **#166**（`reviewed_issue_through`）
- commit baseline：`cab634b`（完整 SHA 見 `tools/upstream_baseline.json`）
- 下次只看編號更大的項目，或已評估項目是否出現新 commit／新 head
