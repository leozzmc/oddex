# 地圖製作調查（工具、設計原則、參考作品、流程）

調查日期：2026-11-19。只查網頁資訊與本機原始碼，沒有安裝或下載任何工具與素材。
審稿：Sonia（地圖／事件線），2026-11-19。修正 §1 的最大尺寸、視野、connection 與 tileset 的說法、§3 第 8 點；新增 §1.1（新增地圖要登記的地方，包含 `region` 會被 mapjson 靜默排除的問題）、§2.4 的工具評估、§3 第 9 點。標示「本機確認」的數字都已經重新驗算過。
目的：評估社群常用的地圖製作方式，提出適合 oddex（pokeemerald-expansion 1.17.2、macOS arm64、Agent 直接改檔）的流程。
背景決策：MVP 階段不導入 Porymap 和 Poryscript（`docs/DECISIONS.md`）。本文件是第三階段以後「原創地區」的準備。

> 標示「本機確認」的數字是直接讀 `game/` 原始碼得到的；其餘依各來源頁面為準，採用前請再確認一次版本。

## 1. GBA 地圖的技術限制（本機確認）

| 項目 | 數值 | 來源 |
|---|---|---|
| 畫面大小 | 240×160 px ＝ **15×10 個 metatile**（每格 16×16） | GBA 規格 |
| 地圖資料格式 `map.bin` | 每格 1 個 u16：bit 0–9 metatile ID、bit 10–11 collision、bit 12–15 elevation | `include/global.fieldmap.h:7–12` |
| 地圖大小上限 | **(寬 + 15) × (高 + 14) ≤ 10,240**，超過的話地圖不會載入 | `include/fieldmap.h:15,23–25`、`src/fieldmap.c:170–174` |
| 例：最大正方形 | **86×86**（101×100 = 10,100；87×87 會變成 102×101 = 10,302，超過上限）。Petalburg 是 30×30，Hoenn 最大的道路 Route 119 是 40×140（8,470） | `data/layouts/layouts.json`（Sonia 審稿時計算） |
| metatile 數量 | primary 512 ＋ secondary 512 ＝ 1,024 | `include/fieldmap.h:9,12` |
| 8×8 tile 數量 | primary 512 ＋ secondary 512 | `include/fieldmap.h:8` |
| 調色盤 | primary 6 組 ＋ secondary 7 組 ＝ 13 組，每組 15 色 ＋ 透明 | `include/fieldmap.h:10,14` |
| 每個 metatile 的圖層 | 2 層（dual-layer，Emerald 預設）；可改成 3 層（triple-layer） | [Porytiles 文件](https://grunt-lucas.github.io/porytiles-user-docs/gba-decomp-tileset-system.html) |
| 現有內容 | 785 個 layout、939 個 `map.json`（含 FRLG；Emerald build 只會用到 `region` 是 `REGION_HOENN` 的地圖，見 §1.1） | 本機 |

設計上的意義：
- 玩家在畫面中央：**左右各看得到 7 格**（`MAP_OFFSET 7`，`include/fieldmap.h:19–23` 的註解），**上下只有大約 4–5 格**（畫面高 10 格）。所以垂直方向的路線，要更早讓重點物件（出口、道具、NPC、地標）進入畫面。
- 地圖比畫面小時，外圍會顯示 `border.bin` 的圖塊（`MAP_OFFSET 7`）。
- 高度（elevation）：玩家只能在相同高度之間移動，例外是任一邊為 0 或 15。高度 0 是「轉換格」（樓梯、梯子）；高度 15 用在橋這類多層結構；**高度 1 是水面**（衝浪時的高度，例如 Route 103 的游泳者）。看起來像山坡的地方，其實是靠 collision、elevation 和 metatile behavior（例如 `MB_JUMP_SOUTH` 單向跳台）做出來的，**沒有真正的 3D**。
- **可以走 ≠ 看得到**：metatile 的上層圖層會畫在 NPC 和玩家上面（屋頂邊緣、樹頂）。未白鎮的測試 NPC 就曾經放在研究所屋頂邊緣（metatile `0x20e`），結果能對話卻看不到人。放置物件時要看 metatile，不能只看 collision（`docs/research/maps-events.md` 坑 #9）。
- 相連的地圖（connections）是用**目前地圖的 tileset** 畫鄰居的圖塊。所以 **primary tileset 必須相同**。secondary 可以不同（原版 Petalburg 用 `gTileset_Petalburg`、Route 104 用 `gTileset_Rustboro`，兩張就是相連的），但交界處兩邊大約 7–8 格內，要只用 primary tileset 的 metatile（或兩邊 secondary 剛好相同的圖塊），否則從另一側看過去會顯示錯誤的圖塊。

### 1.1 新增一張地圖要登記的地方（本機確認）

| 項目 | 規則 | 不照做會怎樣 |
|---|---|---|
| `map.json` 的 `region` | Emerald build **必須是 `REGION_HOENN`**（或留空，留空時預設就是 Hoenn） | `mapjson` 會把其他 region 的地圖列進 `invalid_maps`，**靜默地不放進 map groups**（`tools/mapjson/mapjson.cpp:743–756`）。原創地區如果要用自己的 region 名稱，必須先改 mapjson |
| `data/maps/map_groups.json` | 地圖名稱要加進某個 group | 不會產生 `MAP_*` 常數 |
| `data/layouts/layouts.json` | 新增 layout（寬、高、tileset、`map.bin`、`border.bin` 路徑） | 編譯失敗 |
| connections | **兩張地圖都要寫**，方向相反、offset 互為相反數（Hoenn 的 134 條全部符合，例如 Petalburg `left -50` ↔ Route 104 `right 50`） | 只有一邊寫的話，從另一邊走過去會撞牆，或銜接位置錯開 |
| warps | `dest_warp_id` 是**目的地地圖 `warp_events` 陣列的索引** | 傳送到錯的門 |
| `region_map_section` | 地名提示框和地區地圖用的 `MAPSEC_*` | 地名顯示錯誤 |
| object events | 每張地圖最多 64 個 template、同時最多 16 個存在；新的 NPC 加在陣列最後，避免 `LOCALID_*` 偏移 | 編譯失敗，或腳本指到錯的 NPC |
| 野生遭遇 | 有草叢或水面的地圖，要在 `wild_encounters.json` 加對應的表 | 草叢踩了也不會遇到寶可夢 |

## 2. 工具

| 工具 | 版本 | macOS arm64 | 用途 | 對 oddex 的建議 |
|---|---|---|---|---|
| [Porymap](https://github.com/huderlem/porymap) | 6.3.1（2026-04-12） | 提供 `porymap-macos-latest.zip`（檔名沒寫架構；GitHub 的 macos-latest 目前是 Apple Silicon，**實際下載前要確認**）；另有 `macos-15-intel` 版 | 視覺化編輯地圖、碰撞、高度、事件、tileset 的 metatile | **使用者用 GUI 編排地形時再裝**。Agent 繼續直接改檔 |
| [Porytiles](https://github.com/grunt-lucas/porytiles) | 2.0.0（2026-08-27，MIT） | 有 `porytiles-macos-arm64.zip`，不需要 Homebrew | 把分層 PNG 編譯成 tileset（`metatiles.bin`、`metatile_attributes.bin`、`tiles.png`、調色盤） | **做原創 tileset 時導入**。純 CLI，Agent 可以自動執行 |
| [Poryscript](https://github.com/huderlem/poryscript) | 3.6.1（2026-05-31） | 只有 `poryscript-mac.zip`（沒寫架構，要確認） | 比組語腳本好寫的事件腳本語言 | 照原計畫，在第二階段只用在新寫的腳本 |

### 2.1 Porymap 會動到哪些檔案
依 [官方文件](https://huderlem.github.io/porymap/manual/project-files.html)：
- **讀寫**：`data/maps/map_groups.json`、每張地圖的 `map.json`、`data/layouts/layouts.json`、`map.bin`、`border.bin`、tileset 的 header（`src/data/tilesets/headers.h`、`graphics.h`、`metatiles.h`）與 `tiles.png`、`palettes/*.pal`、`metatiles.bin`、`metatile_attributes.bin`。
- **只附加**：`data/event_scripts.s`（新增腳本檔時加在最後）。
- **只讀**：腳本、constants、object event 和 species 的原始碼。
- **設定檔**：`porymap.project.cfg`（專案設定，可以 commit）、`porymap.user.cfg`（個人設定，應該忽略）、`prefabs.json`。我們的 `game/.gitignore` 已經忽略 `porymap.*.cfg` 和 `prefabs.json`。如果要讓團隊共用專案設定，要把 `porymap.project.cfg` 從忽略清單移除。
- **JSON 格式**：[6.0.0 更新紀錄](https://raw.githubusercontent.com/huderlem/porymap/master/CHANGELOG.md) 寫明「會保留 JSON 裡的自訂欄位」，也「減少存檔時的 diff 雜訊」。但**沒有文件說明 key 的順序是否保持不變**。導入前要做一次實驗：打開專案、不做任何修改就存檔，再看 `git diff`。
- 官方提醒：Porymap 會寫入的檔案，最好不要一邊用 Porymap 開著、一邊手動改。→ **同一張地圖不要同時由使用者（Porymap）和 Agent（直接改 JSON）修改。**
- 沒有 CLI 或 headless 模式。

### 2.2 Porymap 腳本 API
[腳本功能](https://huderlem.github.io/porymap/manual/scripting-capabilities.html)是在 GUI 裡執行的 JavaScript，可以 `map.setBlock(x, y, metatileId, collision, elevation)`、`setCollision`、`setElevation`、`bucketFill`、`setDimensions`，**但只作用在目前開著的地圖，沒有 headless 模式**。適合當使用者的輔助工具，不適合給 Agent 自動化。

### 2.3 Porytiles（[使用文件](https://grunt-lucas.github.io/porytiles-user-docs/quickstart.html)）
- 指令：`create-tileset`、`import-tileset`（把現有 tileset 納入管理）、`compile-tileset`、`decompile-tileset`、`list-tilesets`、`dump-attribute-schema`。
- 輸入：每個 tileset 的 `porytiles_src/` 裡放 `bottom.png`、`middle.png`、`top.png`（三個圖層）、`attributes.csv`（`id,behavior`，例如 `1,MB_TALL_GRASS`），選用 `anim/`（動畫）。
- 輸出：`porytiles_bin/`，也就是 Porymap 和遊戲讀的檔案。
- 依[文件](https://grunt-lucas.github.io/porytiles-user-docs/metatile-attributes.html)，用在 expansion 時要自己設定 `fieldmap.metatile_attribute_size: 2`（Emerald 格式）。
- collision 和 elevation 不是 tileset 的屬性，是每張地圖每一格的設定（在 Porymap 或 `map.bin` 裡）。
- 安裝不需要 Homebrew：下載 zip、把 `porytiles` 放進 PATH，第一次執行前 `xattr -d com.apple.quarantine`。

### 2.4 Agent 可以不用 GUI 做的事
`map.bin` 的格式很單純（見 §1），所以可以寫小工具讓 Agent 自動化：
- **graybox 工具**（提案）：用文字網格描述地形（例如 `.` 草地、`#` 樹、`~` 水、`=` 路），對應到現有 Emerald tileset 的 metatile ID 和 collision，輸出 `map.bin`、`border.bin`，再登記到 `layouts.json`。
- **地圖預覽工具**（提案）：把 `map.bin` ＋ tileset 畫成 PNG，在不開模擬器的情況下檢查整張地圖。
- 實際遊玩檢查繼續用 `tools/headless/oddex-run` 截圖，以及 `make check-oddex`。可以從開機走到指定地點的回歸腳本，用 `tools/headless/authoring/`（讀 savestate 的位置／戰鬥狀態、跨地圖找路、閉環產生路線）製作，`to_petalburg.txt` 就是這樣做的。

#### 評估（Sonia）：值得做，但分成三塊，順序是 預覽＋檢查 → graybox → 自動接邊

| 部分 | 內容 | 工作量（Agent） | 何時做 | 理由 |
|---|---|---|---|---|
| A. 預覽＋檢查 | 讀 `metatiles.bin`（每個 metatile 2 層 × 4 個 tile，含 palette／翻轉）、`tiles.png`、`palettes/*.pal`，把整張地圖畫成 PNG；疊上 collision／elevation、物件、warp、trigger、connection 的標記。同時做靜態檢查：可達性（`plan.py` 已經有 BFS／Dijkstra）、大小上限、connection 是否雙向對稱、warp 目的地是否存在、物件數量、**物件是否放在上層圖層會蓋住的格子**、交界處是否用了對方 tileset 沒有的 metatile | 約 1 天 | **現在就可以做** | 現有地圖也用得到：放 NPC、審 `map.json` 的修改、4b 之後的事件修改。未白鎮那個被屋頂蓋住的 NPC，用這個工具可以在編譯前就抓到。**狀態：已完成主要部分**，見 `tools/oddex/check_maps.py`（用法寫在 `maps-events.md`「地圖檢查與預覽」）。可達性和交界 tileset 檢查還沒做 |
| B. graybox 產生器 | 文字網格 → `map.bin`／`border.bin`／`layouts.json`／`map.json`／`map_groups.json`（region 設成 `REGION_HOENN`、connections 雙向寫入）。每個符號對應一個「功能正確」的 metatile（草地、草叢、樹、水、路、牆、單向跳台、門），collision、elevation、behavior 都正確，但不處理邊緣美觀 | 約 1 天（重用 A 的讀取和檢查） | 世界設計（§5 第 1 步）完成後 | 路線還沒定的時候，做出來也沒有東西可畫 |
| C. 自動接邊 | 樹叢 2×2 拼法、水岸、山壁、跳台兩端等「看起來對」的 metatile 選擇 | 2–4 天，而且每個 tileset 都要個別校準 | **建議不做**，交給使用者用 Porymap 修飾，或等原創 tileset（Porytiles）定案後再決定 | 成本高、跟特定 tileset 綁死；graybox 的目的本來就只是驗證路線 |

結論：先做 A（約 1 天，馬上有用），B 等世界設計完成後再做，C 不做。產出的 PNG 也可以直接放進 review 和基準比對。

## 3. 地圖設計原則

> PokéCommunity 的頁面在調查時回應 403，無法讀到全文。以下社群教學的內容是從搜尋摘要整理的，標題和連結可以給使用者直接閱讀；具體規則以 §1 的技術限制和原版地圖的實際做法為準。

| 教學 | 重點（摘要） |
|---|---|
| [Mini Gamemaking Tutorial Series: Compact Mapping](https://www.pokecommunity.com/showthread.php?p=10207185)（AenaonDusky） | 設計者看得到整張地圖，玩家看不到。地圖要依「玩家實際看到的範圍」來安排，用緊湊的配置營造距離感，而不是靠拉長空地 |
| [Neti's Natural Mapping Tutorial](https://www.pokecommunity.com/threads/netis-natural-mapping-tutorial.170454/)（另有較早的 [Neti's Mapping Tutorial](https://www.pokecommunity.com/threads/134658)） | 自然地形的擺法：樹、水、山。山要分層，上層的形狀不要和下層一樣，再點綴岩石 |
| [Fangame Tutorials: Mapping Routes](https://daily.pokecommunity.com/2017/09/14/fangame-tutorials-mapping-routes)、[Mapping Cities](https://daily.pokecommunity.com/2017/10/31/fangame-tutorials-mapping-cities/2) | Daily PokéCommunity 的道路和城市教學 |

注意：這些教學大多以 RPG Maker XP / Pokémon Essentials 為例，畫面大小和圖層規則跟 GBA 不同，**原則可以用，數字不能照搬**。

整理成 oddex 可以照做的規則：
1. **以 15×10 的視野設計**（左右各 7 格、上下約 4–5 格）：每走 7–10 格，畫面裡就要出現新東西（岔路、道具、訓練家、地標）。不要有超過一個畫面寬、卻什麼都沒有的空地。南北向的路線，看得到的距離比東西向短，所以要排得更密。
2. **主要道路 2–3 格寬**，讓玩家可以繞過 NPC，也讓訓練家的視線範圍有意義；支線和捷徑可以 1 格。
3. **地標**：每張地圖至少一個一眼就認得出來的東西（大樹、雕像、特殊建築），用來讓玩家記住位置。
4. **自然但不迷路**：河道、山壁、森林邊緣避免直線和左右對稱，但主要路線要清楚。
5. **單向跳台（ledge）**控制路線：回程走捷徑、去程繞遠路，是原版常見的節奏設計。
6. **草叢和訓練家**擺在玩家必經或「想去」的地方。原版也會讓玩家**必須**穿過一小段草叢（Route 101 的中段和北段之間只能走草叢），但必經的那段要短；大片草叢放在可以選擇繞開的支線上。訓練家的視線（sight 1–5 格）要能從路線上看出來，避免被看不到的訓練家攔下。
7. **地圖連接**：相連的地圖 primary tileset 要相同；secondary 不同時，交界處 7–8 格內只用 primary 的圖塊（見 §1）。交界處的地形要對齊，connections 兩邊都要寫（§1.1）。
8. **大小**：遵守 §1 的上限。原版的長路線是**單張的長地圖**（Route 110 是 40×100、Route 119 是 40×140），不是拆開的；只有超過上限，或想換 secondary tileset 時，才需要拆成多張相連的地圖。
9. **NPC 和物件的位置**：放在可以走、而且**沒有被上層圖層蓋住**的格子（§1）；擋路的 NPC 要有劇情理由，並用 flag 控制何時消失。

## 4. 參考作品

**研究它們的地圖配置和設計思路完全沒問題；直接複製它們的地圖或 tileset 不行**，除非作者明確授權。以下作品都沒有找到公開的素材授權。

| 作品 | 底層 | 適合參考什麼 | 素材可以用嗎 |
|---|---|---|---|
| Pokémon Gaia（Spherical Ice） | FireRed binary hack | 全新地區 Orbtus 的整體布局：城鎮、道路、洞穴、遺跡怎麼串成一個世界 | 不行。只做研究 |
| [Pokémon Unbound](https://www.pokecommunity.com/threads/pokemon-unbound-completed.382178/)（Skeli） | FireRed ＋ CFRU 引擎 | 原創地區 Borrius，地形和劇情、任務、探索的結合 | 不行。只做研究 |
| Emerald Seaglass | pokeemerald-expansion | 只換 tileset 和色調，就讓熟悉的地圖變成完全不同的氣氛 | 它的 overworld tile 大多是 [Zaebucca](https://zaebucca.itch.io/adventure-begins) 在 itch.io 販售的素材包。要採用的話，要**買下並讀過包內的授權檔**；社群回覆顯示它比 GPL 嚴格 |

可以考慮的**有授權** tileset（風格不一定是 GBA 寶可夢風，要先看過）：

| 來源 | 授權 | 注意 |
|---|---|---|
| [Tuxemon tileset](https://opengameart.org/content/tuxemon-tileset)（Buch，16×16） | CC-BY-SA 3.0 | 要標示作者；修改過的圖要用相同授權釋出。有人指出部分圖塊的來源有爭議 |
| [Overworld tiles](https://opengameart.org/content/overworld-tiles-0)（Buch） | CC-BY 3.0 | 只要標示作者 |
| [16x16 overworld tiles](https://opengameart.org/content/16x16-overworld-tiles)（Sharm） | CC-BY 4.0 / 3.0、OGA-BY 3.0 | 只要標示作者 |

套用到 GBA 時都需要重新量化到每組 15 色、並遵守 §1 的調色盤數量，這正是 Porytiles 處理的部分。

## 5. 建議流程

| 階段 | 內容 | 誰做 | 工具 |
|---|---|---|---|
| 1. 世界設計 | 地區概念、城鎮與道路的草圖、劇情推進順序、每個地點要傳達什麼 | **使用者**（Agent 協助整理成文件） | 紙筆或任何繪圖工具 |
| 2. Graybox | 用**現有 Emerald tileset** 畫出可以走的路線，先不管美術；確認出口、節奏、視野 | Agent（graybox 工具）或使用者（Porymap） | §2.4 的工具、Porymap |
| 3. 遊玩測試 | 從開機走一遍，截圖確認視野、碰撞、傳送點、高度 | Agent | `oddex-run`、`make check-oddex` |
| 4. 地形美術 | 原創或有授權的 tileset，分層 PNG → Porytiles 編譯 | 美術（使用者／外部）＋ Agent 編譯整合 | Porytiles、Aseprite |
| 5. NPC 與事件 | NPC、道具、隱藏事件、劇情腳本 | Agent（Sonia 那條線） | 直接改 `map.json`、Poryscript |
| 6. 回歸 | 每張完成的地圖加一支回歸腳本和基準截圖 | Agent | `tools/headless/authoring/`（產生路線）、`tools/headless/baselines/`、`make check-oddex` |

分工規則：
- **使用者用 Porymap 編排的地圖，Agent 在同一時間不碰那張地圖的檔案**；完成後由使用者 commit（或交給 Agent），再由 Agent 補事件和測試。
- 第 2 步先用現有 tileset，等路線確定了才做美術，避免畫好的圖因為改路線而白費。

## 6. 不要做的事

| 不要 | 原因 |
|---|---|
| 從其他 ROM hack 複製地圖、tileset、metatile | 沒有授權；研究配置可以，複製素材不行 |
| 使用社群「免費 tileset」但沒有確認來源 | 很多是從官方圖改的，或作者沒有給明確授權 |
| 同一張地圖讓 Porymap 和 Agent 同時修改 | Porymap 存檔會覆寫整個檔案，另一方的修改會遺失 |
| 先畫美術再決定路線 | 路線一改，美術就要重畫 |
| 做超過 (寬 + 15) × (高 + 14) ≤ 10,240 的地圖 | 地圖不會載入 |
| 相連的地圖用不同的 primary tileset，或交界處用了 secondary 專屬的圖塊 | 從另一側看過去，交界處會顯示錯誤的圖塊 |
| 新地圖的 `region` 設成 `REGION_HOENN` 以外的值 | Emerald build 會靜默排除這張地圖（§1.1） |
| connections 只寫一邊 | 從另一邊走不過去，或銜接位置錯開 |
| 照搬 RPG Maker 教學裡的數字 | 畫面大小和圖層規則不同 |
| 用 AI 圖片直接縮小當 tileset | 色數、8×8 對齊、調色盤數都不會符合，而且授權不清楚 |

## 7. 需要使用者決定的事

1. **要不要現在安裝 Porymap**：建議等到開始原創地區（第 1 步世界設計完成後）再裝。現階段 Agent 直接改 JSON 就夠了。裝的時候要下載 `porymap-macos-latest.zip`（約數十 MB），並先做一次「不修改就存檔」的 diff 實驗。
2. **原創地區的世界設計**：地區主題、城鎮數量、劇情順序是使用者的設計決定，Agent 可以協助整理成文件。
3. **地形美術的來源**：自己畫、用有授權的素材（§4），或購買素材包（例如 Zaebucca，要先讀授權）。
4. **要不要讓 Agent 做 graybox 工具和地圖預覽工具**（§2.4）：建議**預覽＋檢查現在就做**（約 1 天，現有地圖和事件修改馬上用得到）；graybox 產生器等第 1 步完成後再做；自動接邊不做。
