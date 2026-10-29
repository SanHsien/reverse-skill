# 全庫風險快照

最後更新：2026-10-29。本檔記錄 fork 自 `zhaoxuya520/reverse-skill`（MIT）的全面審查結論、已知風險與維護邊界。

## 2026-10-29 PowerShell 逐行深審

- 完整讀過 `master-route.ps1`、`case-init.ps1`、`bootstrap-reverse.ps1`、`test-routing.ps1`、`verify-routing-coherence.ps1`；不宣稱 Kali／實際工具安裝路徑已驗證。
- 先寫失敗測試再修：同名 case 重跑覆寫 timeline／工項、空路由測試集假綠、未知 capability 假成功、npm post-install／setup 非零退出碼未傳遞。重跑另保留原 `created`、記錄 `updated` 並追加正確的 scope_update 事件。
- 產品候選 `fd7287e`：本機 `tools/dev_check.ps1` 通過（Python 3.12、33 pytest、44 Quick 路由、coherence、安全邊界、文件連結）；native Sol 獨立審查及修正後聚焦複審為 ship。新增測試只操作暫存 case／stub，未真的安裝工具。
- Defender 隔離 `waf-bypass.md`／`rce.md`，它們在本機呈未提交刪除；不還原、不停用防護、不把刪除提交，亦不把 gate 綠燈說成已驗證被隔離內容。用戶環境的安全設定決定仍保留於路線圖。
- 首次發布的 CI 揭露供應鏈測試以未知 capability 執行主流程來載入函式，正確的失敗退出碼因此污染測試結果。離線 probe 先重現 exit 1，再改為只用 AST 載入兩個待測函式，不清除或吞掉真實失敗；後續完整本機 gate 為 34 pytest、44/44 Quick、coherence／security／links 全綠。供應鏈測試的用戶目錄 fixture 未在本機執行，交由隔離 CI runner 驗證。

## 結論

- 授權合規：上游為 MIT License，本 fork 維持 MIT 授權與完整作者 attribution（見 `NOTICE.md`）。
- 邊界確認：對外一律只打本 fork（`SanHsien/reverse-skill`），不回貢上游（除非維護者在當次對話明確授權）。
- 開發環境：補齊 Windows 11 + PowerShell 本機一鍵驗證 gate（`tools/dev_check.ps1`）、三軸上游追蹤、依賴新鮮度稽核與相對連結檢查。
- 交付定位：作為 AI 生成程式碼到正式上線之間的安全檢驗閘門，要求具備授權契約（`scope.md`）與證據鏈。

## 已修 findings

- **AI 指引整合與單一真相源**：將原 `CLAUDE.md` 完整併入 `AGENTS.md`，依跨 repo 標準移除獨立 `CLAUDE.md`，並完整保留上游 `verify-repository-security.py` 強制檢驗的 3 項授權邊界標記。
- **公開入口繁中化與雙語導航**：建立繁體中文 `README.md`，將原英文 README 鏡像至 `README.en.md`，並在頂部加入雙向語言切換連結。
- **Windows 維護與測試骨架**：建立 `tools/dev_check.ps1`、`requirements-dev.txt` 與 `tests/` 測試套件，確保本地可重現驗證。

## 接受、不改契約

- **上游核心路由結構保持原狀**：`skills/config/routing.json`、`skills/MASTER-ROUTING.md`、`skills/routing.md` 與 45 個 Skill 模組維持與上游同步，不擅自修改其路由優先級或核心邏輯。
- **安全研究語料被防毒軟體隔離屬預期行為**：`skills/pentest-tools/src-hunter/references/payloader/` 中的語料可能觸發 Windows Defender 告警；上游腳本透過 Git index 讀取 blob 進行驗證，不強行關閉本機防毒軟體。
- **上游簡體中文說明保留**：`README_zh.md` 與 `RULES_zh.md` 維持原檔，不進行繁簡轉換，避免每次同步產生全檔衝突。

## 尚未宣稱範圍

- 尚未在 Kali Linux 實機環境完整驗證 Kali 專用 toolchain 腳本（`kali/scripts/`）。
- Burp MCP 橋接套件（`burp-mcp-full/`）之 Java 建置環境需另行配置 Gradle 與 Burp Suite Pro，本 fork 核心驗證聚焦於 Skill 路由與靜態合約。
- CTF 沙盒編排（`CTF-Sandbox-Orchestrator/`）涉及 Docker / K8s 多容器運行，不在日常本機單元測試範圍內。
