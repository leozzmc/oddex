# 方案 B：species 引用盤點與改寫策略

基準：develop a374eee3（expansion 1.17.2，Emerald build）。決策見 `docs/DECISIONS.md`（關掉原版各世代 species，原創角色全部新增在 custom 區段）。
分工：§1–§3 引用盤點與改寫策略由 Sonia 負責；§4 關掉原版世代後會壞在哪裡、YAML + 產生器的設計由 Mark 負責（待補）。
**本文只有盤點與提案，尚未修改任何內容。**

## 0. 範圍：只算 Emerald，FRLG 不在範圍內

expansion 同一份原始碼同時包含 Emerald 和 FRLG 的內容，但 Emerald build 會排除 FRLG：

- 訓練家：`src/data.c:233` 用 `#if IS_FRLG` 切換，只會使用 `trainers.party` 或 `trainers_frlg.party` 其中一份。
- 腳本：`data/event_scripts.s:603–1050` 用 `.if IS_FRLG` 包住 FRLG 的地圖腳本。
- 地圖：`mapjson` 依 `version`，只收對應 region 的地圖（emerald → `REGION_HOENN`）。
- 野生遭遇：`wild_encounters.json` 裡有 124 張 `REGION_KANTO` 的地圖，在 Emerald 用不到。

因此 `trainers_frlg.party`、`*_Frlg` 地圖、Kanto 野生遭遇、`trainer_tower_sets.c`、`credits_frlg.c`、`oak_speech.c` 都**不需要改寫**。

## 1. 盤點（Emerald）

計數方式：`trainers.party` 依格式解析（每個訓練家標頭區塊之後，每個以空行分隔的區塊算一隻）；`wild_encounters.json` 依各地圖 `map.json` 的 `region` 分類；腳本用 regex 抓 `SPECIES_*`（排除註解、`_Frlg` 和 `debug.inc`）；C 原始碼排除 `src/data/pokemon*`、`src/data/graphics*`，以及由 party/json 產生的 `trainers*.h`、`wild_encounters.h`。

| 類別 | 位置 | 規模 | 改寫方式 | 何時會碰到 |
|---|---|---|---|---|
| 訓練家隊伍 | `src/data/trainers.party` | 855 名訓練家、1,825 隻、208 種 | 資料替換 | 全程 |
| 野生遭遇 | `src/data/wild_encounters.json`（Hoenn） | 116 張地圖、655 張表（land 317 / water 153 / fishing 151 / rock smash 34）、1,975 格、132 種 | 資料替換或用產生器 | 全程 |
| 事件腳本 | `data/maps/*/scripts.inc`、`data/scripts/*.inc` | 58 個檔案、149 處：`playmoncry` 71、`setvar` 25、`setwildbattle` 14、`bufferspeciesname` 13、`givemon` 7、`seteventmon` 6… | 逐處修改 | 全程（大多在中後期） |
| 對話文字裡寫死的角色名 | `.string`（Emerald） | 約 186 處（全部 399 處，其中 213 處在 FRLG） | 逐處改文字，或改用 `bufferspeciesname` | 全程 |
| 寶可夢造型的地圖物件 | `map.json` 的 `OBJ_EVENT_GFX_*` | 147 個物件、65 種造型（Wingull 12、Kecleon 12、Poochyena 11…） | 美術替換（Mark） | 全程 |
| 寫死在 C 裡的劇情用角色 | 見 §2 | 約 10 處 | 修改 C 或改用代號 | 開場到 Petalburg |
| 對戰設施 | `src/data/battle_frontier/*.h` | frontier 882、trainer hill 204、tent 160、pyramid 320、apprentice 160 | 整批替換或停用 | 破關後 |
| 其他系統 | `trade.h` 31、`contest_opponents.h` 104、`easy_chat_group_pokemon*.h` 453、`bard_music/pokemon.h` 386、`daycare.c` 45、`battle_setup.c` 傳說寶可夢、`roamer`… | — | 依系統逐一評估 | 中期到破關後 |
| 機制用（形態變化、特性、Z 招式等） | `battle_util.c`、`battle_z_move.c`、`battle_dynamax.c`… | 約 150 處 | **不需要改**（是機制判斷，不是內容） | — |

## 2. 早期路線（未白鎮 → Petalburg）一定會碰到的引用

遊戲流程依序是：開場 → 未白鎮 → Route 101（救 Birch、選御三家）→ Oldale → Route 103（勁敵戰）→ 回研究所拿圖鑑 → Route 102 → Petalburg（Wally 抓寶可夢教學）。Petalburg 道館（Norman）是第 5 個徽章，**不算早期**。

### 2.1 寫死在 C 裡的部分（不改就會出錯或顯示原版角色）

| 用途 | 位置 | 目前 |
|---|---|---|
| Birch 開場展示的寶可夢 | `src/main_menu.c:1409`、`:1909` | `SPECIES_LOTAD` |
| 御三家 | `src/starter_choose.c:113–115` | Treecko（現在是 Mossprit）／Torchic／Mudkip |
| 追著 Birch 跑的野生寶可夢（Lv2） | `src/battle_controllers.c:163` | `SPECIES_ZIGZAGOON` |
| Wally 教學：要抓的寶可夢（Lv5） | `src/battle_setup.c:516` | `SPECIES_RALTS` |
| Wally 教學：借給 Wally 用的寶可夢（Lv7） | `src/field_specials.c:1531` | `SPECIES_ZIGZAGOON` |

### 2.2 資料

- **勁敵戰（Route 103）**：`TRAINER_{MAY,BRENDAN}_ROUTE_103_{TREECKO,TORCHIC,MUDKIP}`，共 6 組，各帶 1 隻剋制玩家的御三家。之後在 Route 104／Rustboro 還有 6 組（第二隻是 Lotad／Slugma／Torkoal／Wingull）。
- **野生（可以走到的陸地）**：Route 101：Poochyena、Wurmple、Zigzagoon；Route 103：Poochyena、Zigzagoon、Wingull；Route 102：Poochyena、Wurmple、Zigzagoon、Lotad、Seedot、Ralts。水上和釣魚（Magikarp、Tentacool、Wailmer、Marill、Goldeen、Corphish…）要有釣竿或衝浪才碰得到，不算早期。
- **訓練家**：Route 102：Calvin（Poochyena）、Rick（Wurmple×2）、Tiana（Zigzagoon、Shroomish）、Allen（Zigzagoon、Taillow）。Route 103 還有 Daisy、Isabelle、Marcos、Miguel、Rhett、Amy & Liv、Pete、Andrew（共 8 組）；其中哪些不需要衝浪就能遇到，**尚未確認**（要看各自的座標和地形）。
- **腳本與文字**：`PetalburgCity_PokemonCenter_1F` 的初始角色屬性說明（Treecko 那段已經改成 `bufferspeciesname`，Torchic／Mudkip 還寫死）；`PetalburgCity_Gym` 的 Wally 教學文字提到 ZIGZAGOON；研究所裡 Johto 御三家（Chikorita 等）的 `givemon` 是破關後才會出現。
- **地圖物件造型**：Route 101 追人的 Zigzagoon（`ZIGZAGOON_1`）、家裡搬家的 Vigoroth（4 個）、2F 的 Swablu／Pichu 娃娃。這些是獨立的物件圖，關掉 species 也不會壞，但畫面上仍然是原版的造型，需要美術替換。
- **圖鑑**：拿到圖鑑後，地區圖鑑的順序和內容（`pokedex_orders` 等）由 Mark 處理。

**早期最少需要的原創角色**：御三家 3 隻 ＋ 早期陸地野生大約 6–7 種（Poochyena、Wurmple、Zigzagoon、Wingull、Lotad、Seedot、Ralts 這幾個位置），開場展示、救 Birch、Wally 教學這三個劇情位置都可以重用野生角色。也就是**大約 10 隻原創角色**，就能撐起到 Petalburg 為止的路線。

## 3. 改寫策略（提案）

### 3.1 角色代號層（role alias）

新增一個 header（例如 `include/constants/oddex_species.h`），用「劇情或遊戲上的用途」來命名，而不是用特定角色：

```c
#define SPECIES_ODDEX_STARTER_GRASS   SPECIES_MOSSPRIT
#define SPECIES_ODDEX_STARTER_FIRE    SPECIES_xxx
#define SPECIES_ODDEX_STARTER_WATER   SPECIES_xxx
#define SPECIES_ODDEX_INTRO_MON       SPECIES_xxx   // main_menu.c 開場
#define SPECIES_ODDEX_RESCUE_WILD     SPECIES_xxx   // 救 Birch
#define SPECIES_ODDEX_TUTORIAL_CATCH  SPECIES_xxx   // Wally 要抓的
#define SPECIES_ODDEX_TUTORIAL_LENT   SPECIES_xxx   // 借給 Wally 的
```

§2.1 的 C 程式碼、§2.2 的勁敵隊伍、腳本裡的 `givemon`／`bufferspeciesname` 都改成引用代號。之後換角色、調整平衡，只要改這一個檔案。

可行性：trainerproc 會把物種名稱原樣轉成 `SPECIES_<名稱>` 寫進 `trainers.h`（`tools/trainerproc/main.c` `fprint_species`），而 `trainers.h` 是在 `src/data.c` 裡用 C 編譯的。所以 party 檔寫 `Oddex Starter Fire`，就會變成 `SPECIES_ODDEX_STARTER_FIRE`，只要編譯 `data.c` 時看得到這個 header 就能展開。腳本（經過 cpp）和 `wild_encounters.h`（同樣是生成後再用 C 編譯）也是同樣的道理。**我只確認了 trainerproc 的輸出規則；header 要從哪裡 include 才能三條路都看得到，需要實際編譯驗證**（建議由 Mark 在設計產生器時一起確認）。

### 3.2 大量資料：用「原版 → 原創」替換表加上產生器，保留原本的關卡曲線

訓練家（1,825 隻）和野生遭遇（1,975 格）**不要手改**。做一份替換表 `vanilla → oddex`（可以多對一，例如 Wurmple、Silcoon、Cascoon 都對應到同一條原創進化線的相應階段），由產生器套用到 `trainers.party` 和 `wild_encounters.json`：

- **優點**：原版的等級、遭遇率、表格結構、訓練家難度曲線全部保留，只換角色，平衡不會從零開始。可以逐步擴充：先把早期約 12 種原版角色對應好，後面再慢慢補。
- **前提**：替換表的 key 需要包含「進化階段」，才能讓原創角色的進化線和原版的位置對得上。這份角色清單（YAML）的欄位設計，跟 Mark 的產生器設計對齊。
- **未對應的角色**：原版世代關掉之後，沒有對應到的 species 就是無效引用。產生器遇到沒有對應的角色時要**直接失敗並列出清單**，不要靜默保留。早期開發階段可以提供 `--fallback SPECIES_xxx` 選項，先填一隻佔位角色，讓 ROM 能跑起來。
- 替代方案「依角色清單的棲息地／屬性重新產生遭遇表」比較自由，但要從零重新調整平衡。建議等原創角色超過大約 50 隻、需要真正的生態設計時再考慮。

### 3.3 不適合放進產生器、要逐處改的部分

腳本 149 處、文字約 186 處、地圖物件 147 個，大多跟劇情綁在一起（例如 `playmoncry` 配合特定 NPC），自動替換很容易出錯。依路線進度分批處理，**每一段都用無頭截圖驗證**（未白鎮那次就是靠截圖才抓到 NPC 被屋頂蓋住）。對戰設施和其他系統（§1 最後幾列）放到最後；破關後的內容可以先停用。

### 3.4 守門檢查

把本次盤點用的 script 整理成 `tools/oddex/check_species_refs.py`：列出所有引用到「已停用 species」的位置（party、json、腳本、C），放進 build 或 CI。這樣每批改寫都能看到剩下多少，也能防止新的原版引用混進來。

### 3.5 建議順序

1. 先對齊 YAML 欄位和替換表格式（Sonia × Mark）。
2. 建立代號層，改寫 §2.1 的 5 個 C 引用和 Route 103 勁敵隊伍。
3. 產生器套用早期約 12 種原版角色的替換，跑 `to_littleroot` 和 `to_starter`，再一路截圖到 Petalburg。
4. 依路線往後擴充替換表和逐處修改；設施類最後處理。

## 4. 關掉原版世代後會壞在哪裡、YAML + 產生器設計（Mark，待補）
