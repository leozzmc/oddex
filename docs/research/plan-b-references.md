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
- **訓練家**：Route 102：Calvin（Poochyena）、Rick（Wurmple×2）、Tiana（Zigzagoon、Shroomish）、Allen（Zigzagoon、Taillow）。Route 103 的 8 組訓練家，**早期一組都遇不到**。從 Oldale 進來的西側陸地（x 2–23）四面被水和樹包住，只有劇情的勁敵戰：

| 訓練家 | 座標 | 怎麼遇到 |
|---|---|---|
| Daisy、Amy & Liv、Andrew、Miguel | (71,11)、(64–65,12)、(50,8)、(56,13) | 從 Route 110 走陸路（中期，過了 Slateport 之後） |
| Rhett、Marcos | (67,5)、(67,9) | Route 110 加上居合斬（(67,7)、(72,8) 的 `CUTTABLE_TREE`） |
| Isabelle、Pete | (36,6)、(36,13) | 衝浪（站在 `MB_OCEAN_WATER` 上，elevation 1） |

判斷方式：讀 `map.bin`，依 tileset 的 `metatile_attributes.bin` 判斷 behavior，從地圖邊緣做 BFS。只走 collision 0 的非水面格子，遵守 elevation 規則（相同 elevation，或其中一邊是 0/15），平台（`MB_JUMP_*`）只能往跳下的方向通過，物件當成障礙。只要訓練家四周有一格走得到，就算遇得到。
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

### 3.4 守門檢查：`tools/oddex/check_species_refs.py`

只讀，不修改任何檔案。「原版」的定義是：定義在 `src/data/pokemon/species_info/gen_*_families.h` 裡的 species（會解析 `species.h` 的別名，例如 `SPECIES_CASTFORM`）。Mark 之後新增在其他檔案裡的原創角色，以及 `SPECIES_ODDEX_*` 代號，都不會被回報。FRLG 的內容和生成檔一律跳過。

```bash
python3 tools/oddex/check_species_refs.py --summary                    # 各類別的數量
python3 tools/oddex/check_species_refs.py --maps LittlerootTown,Route101,OldaleTown,Route103,Route102,PetalburgCity
python3 tools/oddex/check_species_refs.py --category c                 # 只看寫死在 C 裡的劇情或內容
python3 tools/oddex/check_species_refs.py --strict --summary           # 有引用就以 exit 1 結束（給 CI 用）
python3 tools/oddex/check_species_refs.py --json > refs.json
```

目前結果（develop 0885db43）：

| 類別 | 處數 | 檔案 | 說明 | `--strict` |
|---|---|---|---|---|
| party | 1,825 | 1 | `trainers.party` | 會擋 |
| wild | 2,107 | 1 | Hoenn 1,975 + pyramid 84 + pike 48 | 會擋 |
| script | 141 | 54 | 腳本裡的 `SPECIES_*` | 會擋 |
| c | 228 | 32 | 寫死在 C 裡的劇情或內容（contest 對手 104、交換 31、`battle_setup.c` 20…） | 會擋 |
| unknown | 0 | 0 | party／wild 裡無法辨識的名稱（打錯字，或解析器漏掉的） | 會擋 |
| text | 186 | 61 | `.string` 裡寫死的角色名 | 只回報 |
| gfx | 94 | 49 | 寶可夢造型的地圖物件 | 只回報 |
| facility | 1,809 | 10 | 對戰設施（遷移期間停用） | 只回報 |
| dictionary | 839 | 3 | easy chat 詞庫、吟遊詩人的發音表 | 只回報 |
| mechanics | 335 | 34 | 戰鬥、形態、動畫機制 | 只回報 |

`--maps` 會依地圖篩選：訓練家是看被哪張地圖的腳本引用，所以 `Route103` 也會列出中期才遇得到的訓練家（見 §2.2 的表）。`c`、`mechanics` 不屬於任何地圖，篩選時會被排除。
分類清單（`MECHANICS_C`、`FACILITY_C_PREFIXES`、`DICTIONARY_C_PREFIXES`）是人工整理的。如果某個檔案歸錯類別，直接修改腳本頂端的清單即可。

### 3.5 建議順序

已和 Mark 的版本合併，見 §5。

## 4. 關掉原版世代後會壞在哪裡、格式與產生器（Mark）

見 [`species-plan-b.md`](species-plan-b.md)（目前在 feat/species daec035c）：關掉原版的實驗結果、三種格式（角色資料 TOML、替換表、代號）、產生器 `gen_species.py`。

## 5. 格式定案與第二階段實作順序（Sonia × Mark 合併版）

### 5.1 格式

- **角色資料**：採用 Mark 的 `content/species/<id>.toml`。地圖和事件這邊**不需要新增 `[design]` 欄位**：劇情用途以 `content/roles.toml` 為準，出現位置以替換表為準，避免同一件事有兩份資料。只有一個要求：`habitat` 一律使用 `map.json` 的 `name`（例如 `Route101`，這也是 `check_species_refs.py --maps` 用的名稱），特殊用途用標籤（例如 `starter`）。
- **代號**：採用 Mark 的 `content/roles.toml` → `oddex_species.h`（四條路都已驗證）。早期需要的代號：

  | 代號 | 位置 | 目前（第 2 步先指向原版） |
  |---|---|---|
  | `STARTER_GRASS` / `STARTER_FIRE` / `STARTER_WATER` | `starter_choose.c:113–115`；Route 103 勁敵 6 組；`PetalburgCity_PokemonCenter_1F` 的 3 段屬性說明 | Treecko / Torchic / Mudkip |
  | `INTRO_MON` | `main_menu.c:1409`、`:1909` | Lotad |
  | `RESCUE_WILD` | `battle_controllers.c:163`；Route 101 追 Birch 的物件造型 | Zigzagoon |
  | `TUTORIAL_CATCH` | `battle_setup.c:516`（Wally 要抓的） | Ralts |
  | `TUTORIAL_LENT` | `field_specials.c:1531`；`PetalburgCity_Gym` 文字裡的 ZIGZAGOON | Zigzagoon |

  每個用途都給自己的代號，即使一開始指向同一隻角色，之後也能分開調整。
- **替換表**：採用 Mark 的 `content/replacements.toml`（key 是原版的每一隻，所以包含進化階段）。`trainers.party` 和 `wild_encounters.json` 由 Sonia 決定，**採就地改寫**：改寫後這兩個檔案就是原始資料，平衡調整直接改檔案，殘留的原版引用由 `check_species_refs.py --strict` 擋下。改寫工具的要求：
  1. **只替換 species 字樣、保持最小 diff**：party 只改每隻寶可夢的第一行；json 只改 `"species": "..."` 的值，不重新排版整個檔案。
  2. **可以依路線分段套用**：`--maps Route101,Route102,...`（party 依訓練家被哪張地圖引用來判斷，跟 `check_species_refs.py` 的規則相同）。
  3. **重複執行結果不變**：已經換成原創角色的地方不會再動。
  4. 替換表缺少原版角色時，失敗並列出全部；可選 `--fallback`。
  - 分工：進化階段的比對需要讀 TOML，由 Mark 提供（`gen_species.py` 的載入函式）；改寫 party 和 json 由 Sonia 實作（`tools/oddex/apply_replacements.py`）。

### 5.2 第二階段實作順序

| 步 | 內容 | 負責 | 依賴 | 驗證 |
|---|---|---|---|---|
| 0 | 使用者決定：原創角色的美術製作方式、叫聲、TOML 格式（Mark §5） | 使用者 | — | — |
| 1 | 產生地區圖鑑、修好 sprite 檢視器的起始編號 | Mark | — | 能力畫面不再顯示 No000 |
| 2a | 代號接上 C：開場 ×2、救 Birch、御三家 ×3 | Mark | — | `to_starter` 截圖逐像素不變 |
| 2b | 代號接上 C：Wally 教學 ×2；Route 103 勁敵 6 組；Petalburg 寶可夢中心 3 段、道館 1 段改用 `bufferspeciesname` 代號 | Sonia | — | `to_petalburg` 截圖不變 |
| 2c | 新增 `to_petalburg.txt`：接在 `to_starter` 之後 → Oldale → Route 103 勁敵 → 研究所拿圖鑑 → Route 102 → Petalburg Wally 教學。**先在原版上錄好基準截圖** | Sonia | — | 腳本可重現 |
| 3 | 早期約 10 隻原創角色的資料和圖像 | Mark | 0 | 產生器驗證、sprite 檢視器 |
| 4a | `apply_replacements.py`（§5.1 的要求） | Sonia（階段比對：Mark） | 3 | 單元測試：重複執行、最小 diff、缺漏時失敗 |
| 4b | 套用早期替換：Route 101/102/103 陸地野生 7 種、Route 102 訓練家 4 名；代號改指向原創角色；Route 101 追人的物件改用原創角色的 overworld 圖 | Sonia × Mark | 3、4a | `check_species_refs.py --strict --maps LittlerootTown,Route101,OldaleTown,Route103,Route102,PetalburgCity` 通過（`--maps` 會排除 C，C 的部分由 2a／2b 涵蓋） |
| 5 | 關掉原版世代（連同 forms／cross-evo 開關） | Mark | 1、4b | `to_littleroot`、`to_starter`、`to_petalburg` 截圖全程沒有 assert |
| 6 | 依路線往後擴充替換表、腳本和文字；美術（搬家的 Vigoroth、娃娃等）；最後是設施 stub | 兩人 | 5 | 每段都要跑 `--strict --maps` 和截圖 |

1、2a、2b、2c 彼此獨立，可以同時進行。第 3 步卡在第 0 步的美術決策。
