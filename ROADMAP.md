# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `30a3ed450320` 查的快照，開工前先重查 GitHub。

## 現況

這是 zhaoxuya520/reverse-skill（逆向／授權滲透測試 skill 路由包）的 Windows-first 維護 fork。維護面健康：`main` 上 CI、CodeQL、Dependency freshness、Upstream check 最近一次皆 success，open PR 0 筆、Dependabot 與 Code scanning 告警 0 筆；issue 功能已停用，issue 數「未查到」不是 0（2026-10-29 `gh` 查詢）。上游最後 push 2026-09-22，commit 水位 `cab634bd855f` 即上游最新；PR 審到 #183、issue 審到 #180，與上游最新編號一致（`tools/upstream_baseline.json`），無待審項目。卡住的只有一個安全設定決定：本機 Windows Defender 會隔離部分 playbook 檔（見近期第一列）。

## 近期：可以直接動手

| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 決定本機 clone 是否加入 Windows Defender 排除清單 | 深掃報告查明：`skills/pentest-tools/src-hunter/references/playbooks/rce.md` 在本機被 Defender 隔離（`Get-MpThreatDetection` 有兩次偵測），本機工作目錄因此一直顯示該檔被刪。遠端檔案完整；復原會被再次隔離；屬安全設定，agent 不自行改 | 維護者決定後在 `docs/DECISIONS.md` 記一則（排除或不排除，附理由）；若排除，本機 `git status` 不再顯示該檔被刪；若不排除，註明本機該檔缺失屬預期，且不得提交那筆刪除 | 維護者 | 接續開發報告（2026-10-25）「本機未提交變更」；`Get-MpThreatDetection` |
| 決定 `# freshness-hold` 是否也蓋過「抓不到 latest」的失敗 | 目前 hold 只清「因為 hold 而沒有 minimum」；帶 hold 但 repo 在 Releases／tags 都查無版本的 Action pin 仍是 `check_failed` 而讓 `--strict` 紅燈。這是 hold 語意取捨（「不管新舊」或「只不管版本比較」） | 在 `docs/DECISIONS.md` 記決定；若改為蓋過，`tools/check_dependency_freshness.py` 改動附重現測試（修前紅修後綠）、`pytest` 與 `tools\dev_check.ps1` 綠；若不改，DECISIONS 寫明理由 | Claude Opus | 深掃報告（2026-10-26）「已知但刻意不擴大修的邊角案例」；`tools/check_dependency_freshness.py:48`、`:301`、`:341`（hold 標記與 `check_failed` 判斷） |

## 中期：等條件成立再做

| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 審上游新 commit／PR／issue 並推進水位 | `Upstream check` workflow 轉 failure，或上游 `main` 出現 `cab634bd855f` 之後的 commit | 結論記入 `docs/DECISIONS.md`；`tools/upstream_baseline.json` 三個水位推進；`python tools/check_upstream_updates.py --strict` exit 0；`tools\dev_check.ps1` 綠 | Claude Sonnet | `tools/upstream_baseline.json`；`docs/DECISIONS.md:55-71` |
| 逐項審 field-journal 與 iOS 文件類投稿（上游 PR #171、#172、#178、#179、#183） | 上游合併這些 PR，內容經 commit 軸抵達 | 逐項審完並記入 `docs/DECISIONS.md`；採用的內容經 `skills/scripts/verify-repository-security.py` 與 routing 回歸（`tools\dev_check.ps1`）通過 | Claude Opus | `docs/DECISIONS.md:67-69`（這類內容會被 skill 載入當操作指引，未審過不收） |
| 修 `master-route.ps1` 只帶 `mustAll` 不帶 `must` 的規則永遠不命中 | 有人要在 `skills/config/routing.json` 新增只用 `mustAll` 的路由規則 | 新增含該規則的測試（修前不命中，修後命中）；routing 回歸全綠 | Codex | 深掃報告「觀察但目前無害」（`skills/scripts/master-route.ps1:39-51`） |

## 刻意不做

| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 擴充 payload／playbook 內容或新增繞過手法 | 本 fork 是維護線，不是內容生產線；資安內容只核對雜湊與路徑一致 | 維護者明確要求並限定授權測試範圍 |
| 收未經上游合併的第三方投稿 | 內容會被 skill 載入當操作指引（`docs/DECISIONS.md:67`） | 上游合併後依中期第二列審 |
| 把公開入口圖 `reverse-skill.png` 轉 jpg（上游 issue #177） | 不適用，本 fork 維持 png（`docs/DECISIONS.md:71`） | 圖檔體積造成載入或 clone 問題 |
| 替 `main` 設分支保護或改寫歷史 | 維護者既定：直接推 `main`；多數 fork 已壓成單一 commit，與上游無共同祖先是已知事實 | 出現第二位寫入者 |

## 維護方式

fork：以 `Upstream check` workflow 為訊號（failure＝上游有未審項目），審完在 `docs/DECISIONS.md` 記採用與否並推進水位。直接推 `main`；Dependabot 只開 PR，CI 綠且讀完 diff 才合併。`CI` workflow 只在 push／pull_request 觸發，沒有手動觸發。
