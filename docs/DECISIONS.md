# 決策紀錄

| 日期 | 決策 | 決定者 | 備註 |
|---|---|---|---|
| 2026-11-19 | 技術基礎採用 pokeemerald-expansion 1.17.2 | David | Emerald 為底、現代 GCC、相容 Porymap、species 與戰鬥擴充完整 |
| 2026-11-19 | 地圖與事件直接編輯 JSON/腳本；MVP 不導入 Porymap 與 Poryscript | David（Sonia 建議） | Porymap 等到要繪製原創地形時再導入，Poryscript 在第二階段只用於新寫的腳本 |
| 2026-11-19 | 上游測試不作為內容修改的門檻 | David | 因為內容被我們改掉而失敗的測試，之後再改寫或停用 |
| 2026-11-19 | **遊戲內文字使用英文** | 使用者 | 先不做中文化（中文化需要字型和編碼，可參考 rh-hideout-chinese fork） |
| 2026-11-19 | **大量替換角色採方案 B**：關閉原版各世代 species，原創角色全部新增在 custom 區段 | 使用者 | 訓練家、野生遭遇、腳本中引用的 species 都要改寫。MVP 的 Mossprit（原地替換 Treecko）之後要遷移到新的 slot |
| 2026-11-19 | 原創角色資料用 TOML（`content/species/*.toml`、`content/roles.toml`），由 `tools/oddex/gen_species.py` 產生程式碼 | David（Mark 建議） | Python 內建 tomllib，不需要第三方套件；要改回 YAML 只需換一個讀檔函式 |
| 2026-11-19 | 方案 B 遷移期間，先停用破關後的對戰設施（frontier、trainer hill、tent、pyramid、apprentice） | David（Sonia 建議） | 這些設施有約 1,700 處原版角色引用；等設計破關內容時再決定要替換還是重新設計。可以撤回 |
