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

- **進化階段**：Mark 已經在 `tools/oddex/species_data.py` 提供 `load_species()`、`load_roles()`、`oddex_stages()`、`vanilla_stages()`（feat/species a1c3394f）。原版共 1,571 種：Wurmple 1 → Silcoon/Cascoon 2 → Beautifly/Dustox 3、Kirlia → Gardevoir/Gallade 都正確，Mega 等型態算第 1 階段。`apply_replacements.py` 直接 import 使用。

### 5.2 驗證：`make check-oddex`

下表「驗證」欄寫的 `make check-oddex`，是 Mark 實作的（feat/species a1c3394f，`game/oddex.mk` + `tools/oddex/check_oddex.sh`）。它會依序執行：

1. `gen_species.py --check`：產生檔是最新的。
2. `check_species_refs.py`：先回報全部的數量，再跑 `--strict-scopes`：`content/migration_scope.toml` 裡 `strict = true` 的範圍只要有原版引用就失敗（範圍檔見 §5.2.2）。
3. 用 runner 跑 `ODDEX_REGRESSION_SCRIPTS`（預設 `to_littleroot to_starter`）：只要出現 crash screen 就失敗。Mark 讓 `src/assertf.c` 在 debug build 的 CrashScreen 多輸出一行 `ODDEX_CRASH_SCREEN assert: <檔案:行號: 訊息>` 到 mGBA log，所以「全程沒有 assert」可以自動判定（已驗證：關掉第 3 世代時會抓到 `disabled species: 270`）。
4. 選用：`ODDEX_SHOTS_BASELINE=<dir>` 會拿 `<dir>/<腳本名>/*.png` 逐像素比對。

使用規則：
- **2c 完成時**，把 `to_petalburg` 加進 `check_oddex.sh` 預設的 `ODDEX_REGRESSION_SCRIPTS`，並把原版基準截圖放到 `ODDEX_SHOTS_BASELINE/to_petalburg/`。
- **4b 完成時**，把 `content/migration_scope.toml` 的 `[early]` 改成 `strict = true`；之後每遷移一段，就新增一個範圍並在完成時設成 strict。
- **回歸腳本必須能獨立執行**：`check_oddex.sh` 會讓每份腳本在自己全新的目錄裡、從開機開始跑，不能 `load` 其他腳本留下的 savestate。所以 `to_petalburg` 要從開機一路跑到 Petalburg（`littleroot_npcs` 目前依賴 `to_littleroot` 的存檔，因此沒放進回歸清單）。如果重複的開頭段落太多，可以請 David 在 runner 加一個 `include <script>` 指令。

### 5.2.1 4a：`tools/oddex/apply_replacements.py`（已完成，尚未套用）

```bash
python3 tools/oddex/apply_replacements.py --scope early --dry-run   # 先看會改什麼（目前：party 7 隻、wild 36 格）
python3 tools/oddex/apply_replacements.py --scope early             # 就地改寫
python3 tools/oddex/test_apply_replacements.py                       # 15 個單元測試，約 4 秒
```

- 替換表：`content/replacements.toml`（還沒建立，等 Mark 定案角色名字）。`[replace]` 的 key 是原版名稱（每個進化階段一行），value 是 `content/species/*.toml` 的 `id`；頂層可以寫 `stage_mismatch_ok = [...]`。
- 改寫規則：party 只改每隻寶可夢第一行裡的 species 那一段（暱稱、性別、持有物保留），原創角色寫成 trainerproc 會轉回 `SPECIES_<ID>` 的名字（`FOO_BAR` → `Foo Bar`）；原本是 `SPECIES_X` 寫法的就維持常數寫法。json 只替換 `"species"` 的值，不重新排版。已經是原創角色（含 `SPECIES_ODDEX_*` 代號）的不會再動，所以重複執行結果不變。
- 範圍：正式用法是 `--scope NAME`，讀 `content/migration_scope.toml`（§5.2.2），訓練家是明確清單、野生是地圖加表的種類。臨時用法 `--maps`／`--kinds` 依地圖推斷，兩種方式不能同時用。Kanto（FRLG）的表一律跳過。
- 失敗條件（什麼都不寫入）：表的 key 不是原版角色、value 不是現有的 id、進化階段不一致（除非列在 `stage_mismatch_ok`）、範圍內有表沒涵蓋的原版角色（全部列出；可以用 `--fallback ID` 先填佔位）。
- 測試（全部在暫存副本上跑，不會動到 repo 的檔案）：只改範圍內的 species 字樣且行數不變、重複執行沒有變化、缺漏時全部列出且不寫入、`--fallback`、範圍外不變、`--dry-run`、進化階段不一致、未知的 key／value、party 的各種寫法、名稱經 trainerproc 規則可以轉回 `SPECIES_<ID>`、`--scope early` 的數量、`--scope` 跟 `--maps` 互斥、`check_species_refs` 讀到同一個範圍、strict 範圍有原版引用時失敗、範圍檔打錯字時失敗。另外手動確認過：改寫後的副本經過 `cpp` + `trainerproc`，產生的是 `SPECIES_SHADEPUP` 這類常數。

### 5.2.2 遷移範圍：`content/migration_scope.toml`

David 的決定：「早期」不靠地圖前綴推斷，改用一份共用的範圍檔，由 `apply_replacements.py`（`--scope`：要改寫什麼）和 `check_species_refs.py`（`--scope`：只看範圍內的引用；`--strict-scopes`：所有 `strict = true` 的範圍不能有原版引用）一起讀，避免兩邊的規則漂移。`make check-oddex` 會跑 `--strict-scopes`，所以這份檔案也是**遷移進度表**：某段遷移完成，就把它設成 `strict = true`。

| 欄位 | 用途 |
|---|---|
| `wild_maps`、`wild_kinds` | 哪些地圖的哪些遭遇表（早期：Route 101/102/103 的 `land_mons`；水上和釣魚要有釣竿或衝浪） |
| `trainers` | 明確的訓練家清單，不依地圖推斷（早期：Route 102 的 4 名＋ Route 103 勁敵 6 組。Route 103 其他 8 組是中期才遇得到，Petalburg 道館的訓練家是第 5 個徽章，都不在範圍內） |
| `maps`、`exclude_maps` | 腳本、文字、寶可夢造型地圖物件的範圍，可以用萬用字元（早期：`LittlerootTown*`、`Route101`、`OldaleTown*`、`Route103`、`Route102`、`PetalburgCity*`） |
| `exclude_refs` | `"<檔案>:SPECIES_X"`，個別排除（早期：研究所裡破關後才給的 Johto 御三家） |
| `c_files` | 檔案內所有引用都要遷移完的 C 原始碼（早期：無；劇情角色在 2a／2b 已改成代號） |

載入時會驗證：未知欄位、不存在的地圖或萬用字元沒有對到任何地圖、不在 `trainers.party` 的訓練家、不存在的檔案，都會直接報錯，避免打錯字被靜默忽略。

`[early]` 目前的工作清單（`check_species_refs.py --scope early`）：訓練家 7 隻（Route 102）、野生 36 格、腳本 0、文字 0，以及**地圖造型 7 個**：未白鎮兩戶人家幫忙搬家的 Vigoroth ×4、2F 的 Swablu／Pichu 娃娃，以及 Route 101 追 Birch 的 Zigzagoon。4b 要嘛換成佔位的 overworld 圖，要嘛把它們列進 `exclude_refs` 並寫明理由，否則 `[early]` 設成 strict 之後檢查會失敗。

### 5.3 第二階段實作順序

| 步 | 內容 | 負責 | 依賴 | 驗證 |
|---|---|---|---|---|
| 0 | ~~使用者決策~~ **已決定**（`DECISIONS.md` 92cd562a）：原創角色先用程式產生的佔位圖，之後再統一設計；原版叫聲關掉後先無聲；資料格式採用 TOML（d0baa5b1） | 使用者 | — | — |
| 1 | 產生地區圖鑑、修好 sprite 檢視器的起始編號 | Mark | — | 能力畫面不再顯示 No000 |
| 2a | 代號接上 C：開場 ×2、救 Birch、御三家 ×3 | Mark | — | `make check-oddex` + `ODDEX_SHOTS_BASELINE`：`to_starter` 逐像素不變 |
| 2b | 代號接上 C：Wally 教學 ×2；Route 103 勁敵 6 組；Petalburg 寶可夢中心 3 段、道館 1 段改用 `bufferspeciesname` 代號 | Sonia | 2c | `make check-oddex` + `ODDEX_SHOTS_BASELINE`：`to_petalburg` 逐像素不變 |
| 2c | 新增 `to_petalburg.txt`：從開機開始，走 `to_starter` 的路線 → Oldale → Route 103 勁敵 → 研究所拿圖鑑 → Route 102 → Petalburg Wally 教學。**先在原版上錄好基準截圖**。必須能獨立執行（見 §5.2） | Sonia | — | 從開機跑兩次結果相同，並加進 `ODDEX_REGRESSION_SCRIPTS` |
| 3 | 早期約 10 隻原創角色的資料和圖像。依使用者決策，先把佔位圖產生器通用化：配色依屬性、幾種體型模板、屬性記號、同一條進化線共用配色，參數放在 TOML 的選填區段 `[graphics.placeholder]`（換正式美術時只要換圖檔、刪掉那一段）；圖檔匯入要能吃外部 PNG（自動量化成 15 色、對應共用 icon 調色盤）。詳見 Mark 的 `species-plan-b.md` §5.1 | Mark | 0 | 產生器驗證、sprite 檢視器、`make check-oddex` |
| 4a | `apply_replacements.py`（§5.1 的要求） | Sonia（階段比對：Mark） | 3 | 單元測試：重複執行、最小 diff、缺漏時失敗 |
| 4b | 套用早期替換：Route 101/102/103 陸地野生 7 種、Route 102 訓練家 4 名；代號改指向原創角色；Route 101 追人的物件改用原創角色的 overworld 圖 | Sonia × Mark | 3、4a | `[early]` 設成 `strict = true` 後，`make check-oddex` 通過（C 的部分由 2a／2b 的代號涵蓋） |
| 5 | 關掉原版世代（連同 forms／cross-evo 開關） | Mark | 1、4b | `make check-oddex`（含 strict 的 `[early]` 範圍，以及 `to_littleroot`、`to_starter`、`to_petalburg` 全程沒有 crash screen） |
| 6 | 依路線往後擴充。**每條路線的必要項目**：替換表套用（訓練家、野生）；腳本裡的 `SPECIES_*`，**包含 `playmoncry`**（原版角色的叫聲在 debug build 會 assert，見下方說明）；文字裡寫死的角色名；寶可夢造型的地圖物件改用佔位 overworld 圖。最後是設施 stub | 兩人 | 5 | `make check-oddex`：在 `migration_scope.toml` 新增該路線的範圍，完成時設成 strict，並加入或更新該路線的回歸腳本 |

1、2a、2c、3 彼此獨立，可以同時進行（第 0 步已決定，第 3 步用佔位圖就能開始）；2b 要等 2c 錄好基準截圖再改，才能證明改完遊戲內容不變。

**注意：「先無聲」不代表 `playmoncry` 可以不改。** `playmoncry` → `GetCryIdBySpecies` → `SanitizeSpeciesId`（`src/pokemon.c:6388`）。在 debug build 裡，播放已停用 species 的叫聲**一樣會跳出 `disabled species` 的 assert**（release build 會靜默變成 `SPECIES_NONE`）。所以腳本裡原版角色的 `playmoncry`（Emerald 共 71 處）還是要在第 6 步依路線改成原創角色或代號；原創角色本身的叫聲是 `CRY_NONE`，沒有問題。早期路線（到 Petalburg）沒有 `playmoncry`，所以不影響第 5 步的驗收。地圖上寶可夢造型的物件，依決策先換成原創角色的佔位 overworld 圖。

## 6. 第 6 步第一段的事前準備：Petalburg → Route 104 → Petalburg Woods → Rustboro（到 Roxanne）

### 6.1 範圍：`[rustboro]`（`content/migration_scope.toml`，`strict = false`）

- **野生**：Route 104、Petalburg Woods、Route 116 的 `land_mons`。Route 104 的水上和釣魚要衝浪或釣竿（舊釣竿在 Dewford），不在範圍內。Route 116 在拿第一個徽章前就能走，而且 `to_rustboro` 在那裡練等級（見 §6.4），所以納入範圍。
- **訓練家**：以「陸路可達性」確認（從 Petalburg 出發，可以跨 connection 和 warp，但不能衝浪、居合斬、碎岩、怪力；可砍的樹和可碎的岩石都當成障礙）：
  - Route 104：Haley、Ivan、Gina & Mia、Winston、Cindy、Billy、Darian（全部）。
  - Petalburg Woods：Lyle、James，以及 Devon 研究員事件中的 Aqua 手下（`TRAINER_GRUNT_PETALBURG_WOODS`）。
  - Route 116：Joey、Jose、Clark、Karen、Johnson、Devan。Janice、Jerry、Sarah、Dawson 要居合斬，不在範圍內。
  - Rustboro 道館：Josh、Tommy、Marc、Roxanne。
  - Route 104 的勁敵戰（`TRAINER_{MAY,BRENDAN}_RUSTBORO_*`）在 Devon 貨物事件之後，屬於下一段。
- **地圖**：`Route104*`、`PetalburgWoods`、`RustboroCity*`、`Route116`。例外：Devon 2F 用化石復活 Lileep／Anorith，化石要到 Route 111 的沙漠才拿得到，排除。

### 6.2 新的原創角色需求（給使用者：下一批面具要設計幾隻）

扣掉早期已經涵蓋的位置（Poochyena、Zigzagoon、Wurmple、Wingull、Lotad、Seedot、Ralts→Kirlia→Gardevoir/Gallade、Shroomish、Taillow、御三家），這一段還有 **12 個原版位置**沒有對應的原創角色（由 `check_species_refs.py --scope rustboro` 的訓練家和野生遭遇統計）：

| 原版 | 屬性 | 進化階段 | 訓練家隊伍 | 野生格數 | 出現在 | 說明 |
|---|---|---|---|---|---|---|
| Geodude | 岩石／地面 | 1 | 10 | 0 | Rustboro 道館（Josh、Marc、Tommy、Roxanne）、Route 116 的 Clark、Devan | **道館主題，必要** |
| Nosepass | 岩石 | 1 | 1 | 0 | Roxanne 的王牌 | 道館館主的招牌角色 |
| Nincada | 蟲／地面 | 1 | 3 | 2 | Woods 的 James、Route 116 的 Jose、Route 116 野生 | |
| Magikarp | 水 | 1 | 4 | 0 | Route 104 的釣魚人 Ivan、Darian | 只出現在訓練家隊伍 |
| Marill | 水／妖精 | 2（Azurill 是第 1 階段） | 0 | 2 | Route 104 野生 | 可以對到第 1 階段的原創角色，並列進 `stage_mismatch_ok` |
| Skitty | 一般 | 1 | 0 | 2 | Route 116 野生（也是 Rustboro 民宅 NPC 的寵物，見 §6.3） | |
| Slakoth | 一般 | 1 | 0 | 2 | Petalburg Woods 野生 | |
| Whismur | 一般 | 1 | 0 | 1 | Route 116 野生 | |
| Machop | 格鬥 | 1 | 1 | 0 | Route 116 的 Joey | |
| Abra | 超能力 | 1 | 0 | 1 | Route 116 野生 | |
| Silcoon | 蟲 | 2 | 0 | 1 | Petalburg Woods 野生 | Wurmple（早期的 Sproutworm）的第 2 階段 |
| Cascoon | 蟲 | 2 | 0 | 1 | Petalburg Woods 野生 | 同上，分支進化的另一邊 |

另外，**Pikachu（電）**不在訓練家和野生遭遇裡，但它是 Rustboro 民宅 NPC 的寵物（叫聲、文字、造型都有，見 §6.3），所以也需要一個角色。

**需要的數量**：一對一的話是 13 隻（上表 12 隻＋Pikachu）。替換表允許多對一，合併同一種角色後最少大約 **8 隻**：
- 一般：Skitty、Whismur、Slakoth 合成 1–2 隻。
- 水：Magikarp、Marill 合成 1 隻。
- 蟲繭：Silcoon、Cascoon 合成 1 隻，作為 Sproutworm 的第 2 階段。
- 岩石：Geodude、Nosepass 各 1 隻，因為道館要有代表性。
- Nincada、Machop、Abra、Pikachu：各 1 隻，或依面具設計併進現有的角色線（例如 Abra 可以併進小面那條超能力線，前提是屬性對得上）。

這是設計上的選擇，請使用者決定。

### 6.3 這段路線要逐處處理的腳本、文字、物件造型（`--scope rustboro`，訓練家和野生以外）

| 類別 | 位置 | 內容 | 處理方式 |
|---|---|---|---|
| `playmoncry` | `Route104_MrBrineysHouse/scripts.inc:91` | Mr. Briney 的 Wingull（Peeko）叫聲 | 改成 Wingull 的替代角色（Gullwisp），或新增一個代號 |
| `playmoncry` | `RustboroCity_Flat2_1F/scripts.inc:12` | NPC 的 Skitty 叫聲 | 改成 Skitty 的替代角色 |
| `playmoncry` | `RustboroCity_House3/scripts.inc:17` | NPC 的 Pikachu 叫聲 | 改成 Pikachu 的替代角色 |
| 文字 | `PetalburgWoods/scripts.inc:324` | 提到 SHROOMISH | `bufferspeciesname`，或改寫文字 |
| 文字 | `RustboroCity_Flat2_1F/scripts.inc:23` | SKITTY | 同上 |
| 文字 | `RustboroCity_House3/scripts.inc:31` | PIKACHU | 同上 |
| 文字 | `RustboroCity_Mart/scripts.inc:70` | SHROOMISH | 同上 |
| 文字 | `RustboroCity_PokemonSchool/scripts.inc:267` | SEEDOT | 同上 |
| 地圖造型 | `Route104_MrBrineysHouse` 物件 #2 | `OBJ_EVENT_GFX_WINGULL`（Peeko） | `OBJ_EVENT_GFX_SPECIES(...)` 換成替代角色 |
| 地圖造型 | `RustboroCity_Flat2_1F` 物件 #1 | `OBJ_EVENT_GFX_SKITTY` | 同上 |
| 地圖造型 | `RustboroCity_House3` 物件 #3 | `OBJ_EVENT_GFX_PIKACHU` | 同上 |
| 地圖造型 | `RustboroCity_Flat1_2F` 物件 #3–8 | Skitty、Treecko、Torchic、Mudkip、Pikachu 娃娃 | 跟 `[early]` 的娃娃一樣，先列進 `exclude_refs`，裝飾品統一處理 |

`playmoncry` 這 3 處在原版角色停用後會讓 debug build 跳出 assert，是 strict 之前一定要處理的。

### 6.4 `to_rustboro`（原版基準，4b 之後的 ROM）

`tools/headless/scripts/to_rustboro.txt` 接在 `to_petalburg` 後面：Petalburg 回血 → Route 104 → Petalburg Woods（Devon 研究員、Aqua 手下）→ Rustboro 回血 → Mart、學校、Flat2、House3 → Route 116 練到 Lv16（Lv15 學會 Bulldoze）→ 道館 → Roxanne → STONE BADGE。截圖 r01–r09 拍的是 §6.3 的各個位置和 Roxanne 的 Nosepass；Briney 家的 Peeko 要到 Dewford 之後才出現，這一段拍不到。單獨執行約 144 秒（345,802 幀），所以不在 `check-oddex` 的預設清單裡，交給 `make check-oddex-full`。

為了這一段，`autopilot.py` 新增了以下能力（也會用在 4b 的重新校準）：
- **戰鬥一次按一鍵**：從 RAM 讀 `gBattlescriptCurrInstr`。進入 `BattleScript_AskToLearnMove` 時，新招的「威力 × 本系加成 × 自己的攻擊或特攻」比最弱的現有招式高就按 A 學。比較時，某個屬性唯一的攻擊招（新招則是現有招式都沒有的屬性）價值乘 1.5，所以 Grinpack 會用 Aerial Ace（打格鬥系 2 倍）換掉和 Mega Drain 同屬性的 Razor Leaf；如果最弱那招是物理或特殊唯一的攻擊招，而新招是另一類，就改忘下一招，保留兩類（游標預設在 YES），在遺忘畫面把 `sMonSummaryScreen->firstMoveIndex`（偏移 16588）移到最弱那招再按 A；否則按 B 拒絕（`P_ASK_MOVE_CONFIRMATION` 是 FALSE，所以只有一個提示）。
- **野生戰逃跑**：對手的屬性剋我方、我方又沒有 2 倍以上的招式時（例如 Taillow 對草屬性），在行動選單選 Run。玩家的 `HandleInputChooseAction` 是 static，有三個同名函式，用 map 檔裡 `battle_controller_player.o` 的範圍找出正確的那個。
- **選招畫面**（`gBattlerControllerFuncs[0] == HandleInputChooseMove`）：把遊標移到「威力 × 屬性相剋 × 本系加成 × 攻防比」最高、還有 PP 的攻擊招式。攻防比是物理招用我方攻擊對對手防禦、特殊招用特攻對特防，套用能力階段（`statStages` 在 +24），分類從 `moves_info.h` 的 `.category` 解析。加入攻防比之前，Grinpack 一直拿物理招去撞 Iwadawn 135 的物防，要練到 Lv22 才打得贏 Roxanne；加入之後改用 Mega Drain，Lv16 就打得贏，`to_rustboro` 從約 400 秒縮短到 135 秒。雙方的招式、PP、屬性從 `gBattleMons[0]`／`gBattleMons[1]` 讀（`struct BattlePokemon` 大小 0x8C，招式在 +12、屬性在 +34、PP 在 +37）。相剋表從 ROM 的 `gTypeEffectivenessTable` 讀（`uq4_12_t` 是 u32），招式的威力和屬性從 `src/data/moves_info.h` 解析。換成原創角色後才需要這樣做：例如 Tackle 打一般／幽靈的 Kyokon 完全無效，Leafage 又被火屬性抵抗。
- **大地圖上換招式**：第一格是狀態招式，或 PP 低於 5 時，打開能力畫面把攻擊招式換到第一格。開始選單的遊標會記住位置而且會繞圈，所以從 `sCurrentStartMenuActions`／`sStartMenuCursorPos` 讀出來再計算按法；操作被腳本鎖住時（`sLockFieldControls`、`sGlobalScriptContextStatus`）不換。
- 同一步走不動兩次（已經按 B 排除對話框的可能）時，把那一格當成障礙並重新規劃。例如道館裡打完戰鬥、走過來擋在一格寬通道上的訓練家。
- `grind:Map:x1:y1:x2:y2:LV`：在兩格草叢之間來回走到指定等級；HP 低於 `GRIND_MIN_HP`%（預設 35，`to_rustboro` 用 60）或攻擊招式的 PP 總和低於 10 時暫停，讓呼叫者去回血。
- 戰鬥中按超過 600 次就直接報錯（避免像 PP 用完那次，無限產生存檔）。
- **進化畫面**（`gMain.callback2` 落在 `evolution_scene.o` 的範圍內）：一律按 A，因為 B 會中斷進化。只有在「Delete a move to make room for ...?」的 YES/NO 時，才依學招規則決定：`slot_to_forget` 找不到可以忘的招式就按 B。從 `gTasks` 找出 `Task_EvolutionScene`，讀 `tState`（data[0]）是不是 `EVOSTATE_REPLACE_MOVE`、`tLearnMoveState`（data[6]）是不是 `MVSTATE_HANDLE_YES_NO`，這兩個 enum 值從 `evolution_scene.c` 解析。`P_ASK_MOVE_CONFIRMATION` 是 FALSE，所以 NO 會直接放棄學招。這個判斷要放在戰鬥腳本的學招判斷之前：戰鬥結束後 `gBattlescriptCurrInstr` 可能還停在學招腳本裡，那時按 B 會中斷進化。
  - 驗證方式：用 Mark 在 trio-evo 建好的 ROM 重播 `to_rustboro` 到 Route 116，再練到 Lv17。Grinpack 在 Lv16 進化成 Grinvine，畫面依序是「What? Grinpack is evolving!」到「evolved into Grinvine!」，`tState` 從 1 走到 15（`EVOSTATE_TRY_LEARN_MOVE`）。
  - 進化畫面裡的學招提示（第 2 階段把 Night Slash 等招式改成 level 0 之後才會出現）：戰鬥結束後 `gBattleMons` 已經清空，原本每個招式的分數都是 0，所以一律拒絕學招。現在 `slot_to_forget` 在戰鬥外改讀隊伍第一隻：攻擊和特攻從 `struct Pokemon` 的 +90 和 +96 讀，屬性從 `where.lead_species` 解密出物種後查 ROM 的 `gSpeciesInfo`。`struct SpeciesInfo` 的大小不寫死（`pokemon.h` 註解寫的 0xC4 已經過時，這個 build 是 0x108），改成從建好的 ROM 量：`SPECIES_BULBASAUR` 是 1，所以它那一筆從 `gSpeciesInfo` 開頭算起的位移就是 struct 的大小。用 `gen_1_families.h` 裡 Bulbasaur 的種族值找出這個位置，必須剛好找到一個，而且要能整除 `nm -S` 量出的整張表的大小，否則就用 assert 擋下來。實測 Grinvine 會忘掉 Bite 來學 Night Slash。
- **跨地圖連接**：
  - `plan.step()` 跨過 connection 後，如果落在比較窄的鄰接地圖範圍外，就回傳 None。以前跳過崖時不會檢查，例如從 Route 110 往 Mauville 規劃時，就讀到地圖外而當掉。
  - 正在跨過 connection 的那幾格，玩家座標會在地圖邊界外一格，這時 `units()` 先 `wait 10`，等換完地圖再規劃。
- **`stepwalk.py`**：autopilot 的靜態規劃走不通時使用。它每走一段就重新規劃，戰鬥和對話交給 autopilot 處理，輸出格式跟 autopilot 一樣。
  - 預設：用地圖資料做 BFS，會跨 warp 和崖，例如 Lavaridge 道館的洞和間歇泉。只有地塊有 warp 行為的那一邊才能用，所以單向的 warp 也算得對。
  - `--live`：用執行中的地圖（`gBackupMapLayout`）和物件目前的位置規劃，例如已經藏起來的物件、`setmetatile` 改過的電閘、打完之後走過來擋路的訓練家。不想踩的格子（例如道館的開關）用 `--avoid x,y;...` 避開。
  - 用法：`stepwalk.py START.ss OUT_PREFIX MAP X Y [--live] [--avoid ...]`。
- **防止空轉**：總共執行超過 `AP_MAX_STEPS` 個單位（預設 20000），或在戰鬥外同一位置連續 100 次送出同一個指令，就印出原因、已執行的指令和最後的狀態，以 exit 3 結束（`AP_PARTIAL=1` 也一樣會失敗）。起因是 Mauville 練等時，練等格上跳出 Match Call 的訊息，`grind` 在練等格上遇到操作被鎖住只會 `wait 30`，而 B 只在「走一步沒動」時才按，結果空轉了 32 萬步（約 5 小時 40 分）都沒停；那時攻擊招式還剩 Aerial Ace 的 19 PP，高於暫停門檻 10，所以也沒有因為 PP 不足而暫停。現在練等格上連續 3 次操作被鎖住就按 B。
- `where.py` 會解密隊伍第一隻的招式和 PP（`EncryptBoxMon` 的 XOR 和 `personality % 24` 的子結構順序）。
- `stage_reach.py`：判斷這個階段走得到的訓練家（§6.1）。

## 7. 第 6 步第二段的事前準備：Devon 貨物 → Route 104 勁敵 → Dewford（到 Brawly）和 Granite Cave

### 7.1 範圍：`[dewford]`（`content/migration_scope.toml`，`strict = false`）

劇情順序：Roxanne 之後，Aqua 手下搶走 Devon 貨物，追到 Route 116 的 Rusturf Tunnel 打倒他，救回 Briney 的 Peeko → Devon 社長交代信件和貨物 → 離開 Rustboro 時在 Route 104 跟勁敵對戰 → Mr. Briney 開船送到 Dewford → 拿 Old Rod、打 Brawly、到 Granite Cave 把信交給 Steven。下一段從 Briney 開船到 Slateport（Route 109）開始。

- **訓練家**（`stage_reach.py`，從 Rustboro 和 Dewford 兩個起點，不能衝浪、居合斬、碎岩、怪力）：
  - Rusturf Tunnel 的 Aqua 手下（`TRAINER_GRUNT_RUSTURF_TUNNEL`，劇情戰）。同一條隧道的 Mike 要碎岩，不在範圍內。
  - Route 104 勁敵：6 種組合（`TRAINER_{MAY,BRENDAN}_RUSTBORO_{TREECKO,TORCHIC,MUDKIP}`）。
  - Dewford 道館：Takao、Jocelyn、Laura、Lilith、Cristian、Brenden、Brawly。
  - Route 106 沙灘的釣魚人 Elliot、Ned。Douglas、Kyla 和整條 Route 107 都是泳客，要衝浪。
- **野生**：Rusturf Tunnel 和 Granite Cave（1F、B1F、B2F、Steven 的房間）的 `land_mons`。Old Rod 拿到後，Briney 的船可以在 Dewford 和 Route 104 之間來回，所以 Dewford、Route 104、106、107 的 `fishing_mons` 也在範圍內。這個表同時包含 Good Rod 和 Super Rod 的格子，等於提早一起遷移；Route 104 的 `land_mons` 已經在 `[rustboro]`。Granite Cave 的 `rock_smash_mons` 要碎岩，不在範圍內。
- **地圖**：`RusturfTunnel`、`DewfordTown*`、`Route106`、`Route107`、`GraniteCave*`。Rustboro 市區、Devon 大樓和 Briney 的家已經在 `[rustboro]` 的 `RustboroCity*`、`Route104*` 裡。

`check_species_refs.py --scope dewford`：party 26、wild 112、script 3、text 1、gfx 2，共 24 種原版角色。

### 7.2 角色盤點：哪些位置可以用已經做好的角色填

「已有」指 `content/replacements.toml` 已經有對照（早期角色）；「Rustboro 批」指 `mask-designs.md` 裡 Rustboro 段的 9 隻設計（Mark 正在做）；「舊御三家」指換成三人組之後待重新安排的 Okinoir（草/地面）、Shishiblaze（火/格鬥）、Kamorai（水/電）。

| 原版 | 屬性 | 訓練家 | 野生格數 | 出現在 | 建議 | 依據 |
|---|---|---|---|---|---|---|
| Poochyena | 惡 | 1 | 3 | Rusturf 手下、Route 104 | **已有**：Shachound | |
| Wingull | 水/飛行 | 2 | 4 | 勁敵、Route 104 釣魚以外 | **已有**：Utoghast | Peeko 也是 Wingull（§7.3） |
| Lotad | 水/草 | 2 | 0 | 勁敵 | **已有**：Shojobob | |
| Taillow、Wurmple | | 0 | 3 | Route 104 | **已有**：Shawabolt、Usobuzz | |
| Treecko、Torchic、Mudkip | | 6 | 0 | 勁敵的御三家 | **代號**：`Oddex Starter Grass/Fire/Water`（跟 Route 103 勁敵一樣，2b 的做法） | 換成三人組後自動跟著改 |
| Magikarp | 水 | 2 | 16 | 各地釣魚、Elliot | **Rustboro 批**：Magatide | |
| Marill | 水/妖精 | 0 | 2 | Route 104 | **Rustboro 批**：Magatide | |
| Whismur | 一般 | 0 | 12 | Rusturf Tunnel | **Rustboro 批**：Mandalumb | |
| Geodude | 岩石/地面 | 0 | 4 | Granite Cave 1F | **Rustboro 批**：Komarock | |
| Abra | 超能力 | 0 | 4 | Granite Cave | **Rustboro 批**：Tsukuyume | |
| Machop | 格鬥 | 3 | 0 | Takao、Brenden、Brawly | **Rustboro 批**：Karuvajra | 道館主題 |
| Makuhita | 格鬥 | 2 | 12 | Brawly 的王牌、Cristian、洞窟 | **舊御三家**：Shishiblaze（火/格鬥） | 格鬥道館；1 階段、沒有進化，等級帶對得上 |
| Slugma、Torkoal | 火 | 2 | 0 | 勁敵 | **舊御三家**：Shishiblaze | 只在勁敵隊伍裡 |
| Wailmer | 水 | 0 | 18 | 釣魚（Good/Super Rod） | **舊御三家**：Kamorai（水/電） | 這段其實釣不到（Old Rod 只有 Magikarp/Tentacool） |
| Tentacool | 水/毒 | 2 | 6 | 釣魚、Elliot、Ned | **已有**：Shojobob（水/妖精），或新角色 | 有毒屬性的話比較合適 |
| Zubat | 毒/飛行 | 0 | 8 | Granite Cave 全層 | **已有**：Utoghast（飛行/幽靈），或新角色 | 洞窟的蝙蝠，最常遇到 |
| Sableye | 惡/幽靈 | 0 | 10 | Granite Cave B1F、B2F | **已有**：Kyokon（一般/幽靈），或新角色 | |
| Aron | 鋼/岩石 | 0 | 10 | Granite Cave B1F 以下 | **Rustboro 批**：Komarock，或新角色（鋼） | Aron 是 3 階段線的第 1 階段 |
| Meditite | 格鬥/超能力 | 4 | 0 | Brawly、Jocelyn、Laura、Lilith | **新角色**（格鬥/超能力） | 道館主題；也可以暫用 Karuvajra |

**結論**：全部用現有角色填，**新角色 0 隻**也做得到。比較理想的是 **1–4 隻**：
- Meditite：道館的第二主題，最需要新角色。
- Zubat、Sableye：Granite Cave 遇到最多的兩隻。
- Aron：要有鋼屬性。

先用上表的填法，之後再換成新角色，只要改 `replacements.toml`。這是設計上的選擇，請使用者決定。

### 7.3 逐處處理的腳本、文字、物件造型（`--scope dewford`，訓練家和野生以外）

| 類別 | 位置 | 內容 | 處理方式 |
|---|---|---|---|
| `playmoncry` ×2 | `RusturfTunnel/scripts.inc:293, 325` | 被搶走的 Peeko 叫聲 | 跟 Briney 家的 Peeko（§6.3）一樣改成 Utoghast；建議新增代號 `PEEKO`，三處共用 |
| 地圖造型 | `RusturfTunnel` 物件 #7 | `OBJ_EVENT_GFX_WINGULL`（Peeko） | `OBJ_EVENT_GFX_SPECIES(ODDEX_PEEKO)` |
| `playmoncry` | `DewfordTown_House1/scripts.inc:16` | NPC 的 Zigzagoon 叫聲 | 改成 Kyokon（對照表已有） |
| 文字 | `DewfordTown_House1/scripts.inc:35` | ZIGZAGOON | `bufferspeciesname` 或改寫句子 |
| 地圖造型 | `DewfordTown_House1` 物件 #3 | `OBJ_EVENT_GFX_ZIGZAGOON_2` | `OBJ_EVENT_GFX_SPECIES(KYOKON)` |

不算角色引用、但同一類的問題：`data/scripts/berry_tree.inc` 的道具名 **WAILMER PAIL**（Route 104 花店送的，在 `[rustboro]` 就拿得到）。道具改名留給第 6 步統一處理。

這一段的共用腳本（`data/scripts/*.inc`）裡沒有原版角色引用，所以不需要 `script_files`。

### 7.4 `to_dewford`：遷移之後才錄

`[dewford]` 已經遷移，`strict = true`：
- `apply_replacements`：party 20、wild 100。Route 104 的 land 已經在 `[rustboro]` 裡遷移過。
- 勁敵的御三家改成 `Oddex Starter *` 代號 ×6。
- Dewford House1 的寵物改成 Kyokon（叫聲、文字、造型）；Peeko 用 `PEEKO`。

這一段**沒有另外錄原版基準**，跟技能說明的第 2 步不同。原因有兩個：
- 這一晚御三家和角色數量換了好幾次，每次都讓經過戰鬥的路線整段作廢，原版基準錄好就會過期。
- 這段地圖不在任何現有回歸腳本的路線上。遷移後 `check-oddex-full` 只有 `to_rustboro` r02 一張不同，而且只是 Woods 手下 Shachound 的性別符號：訓練家資料一變動，訓練家寶可夢的性別就可能跟著改，畫面其他部分都沒變。

`to_dewford` 直接錄在遷移後的 ROM 上。預定接在 `to_rustboro` 後面：Devon 貨物事件（Rusturf 手下）→ Devon 社長 → Route 104 勁敵 → Briney 的船 → Dewford（Old Rod、House1 的 Zigzagoon）→ Granite Cave（Steven）→ Brawly。截圖要拍到 §7.3 的每一處、勁敵戰、Brawly 的王牌，以及一次 Old Rod 的釣魚戰鬥。執行時間會超過 `to_rustboro`（約 144 秒），所以放進 `check-oddex-full`。

可能遇到的問題：
- Dewford 道館很暗，要帶 Flash 或摸黑。stage_reach 走得到，但 autopilot 的路線規劃用的是地圖資料，不受亮度影響。
- Granite Cave B1F 的裂地板要 Mach Bike，不過 Steven 的房間從 1F 就走得到。


**錄製結果**：`tools/headless/scripts/to_dewford.txt`（在 `check-oddex-full` 裡）錄到 **KNUCKLE BADGE**。截圖 d01–d09 依序是：
- Rusturf Tunnel 的 Peeko 和 Aqua 手下、手下的 Shachound。
- Rustboro 的勁敵（Shojobob）。
- Briney 家的 Peeko、Dewford House1 的 Kyokon。
- Granite Cave 的野生戰。
- Brawly 的 Karuvajra、王牌 Komarock，以及徽章。

最早的版本停在 Brawly 的第一回合：當時 Lv17 的 Grinpack 被 Karuvajra 一下打掉 44/45。方案 F（見下）加上 Mark 讓 Grinpack 在 Lv15 學 Aerial Ace 之後，`to_rustboro` 在 Route 116 練到 Lv21。Lv19 時還打不贏：Karuvajra 要吃兩下 Aerial Ace，Brawly 又有兩瓶傷藥。練到 Lv21 之後，Roxanne 和 Brawly 都穩定打得贏（Brawly 那場結束時是 Lv22、剩 40/58）。Granite Cave 裡大多是剋 Grinpack 的格鬥系，在那裡練等多半在逃跑，效率很差，所以把練等集中在 Route 116。Old Rod 和 Steven 的信沒有涵蓋，因為跟角色遷移無關。

**Brawly 的平衡（2026-11-20，David 暫定採用方案 F，見 `DECISIONS.md` 和 `balance.md`）**：`TRAINER_BRAWLY_1` 的王牌從 Shishiblaze Lv19 改成 Komarock Lv17：
- 沿用原本王牌的 Sitrus 果和 24 的 IV。
- 招式是 Arm Thrust、Vital Throw、Rock Tomb、Bulk Up。
- Karuvajra 和 Gachirinza 降到 Lv14。

重戰的 `TRAINER_BRAWLY_2`–`5` 沒有改：它們在破關後，等級和隊伍的平衡要跟其他重戰一起看，不適合照第一戰的比例調整。

錄製時學到的事：
- Rustboro 南口的勁敵會問要不要對戰，用 B 推進等於回答 NO。
- Devon 社長之後的 PokéNav 教學，要選 POKéNAV → MATCH CALL → MR. STONE → CALL 才會結束。
- Briney 和 Peeko 繞著桌子走，要站在路線旁邊一直按 A 等他們經過。
- 路上的訓練家打完之後會站在路中間，autopilot 會判斷成走不過去。這時加上 `AP_PARTIAL=1`，讓 autopilot 交出已經走過的指令，再手動繞過去。
## 8. 第 6 步第三段：Route 109 → Slateport → Route 110 → Mauville（到 Wattson）

`[mauville]` 已設成 `strict = true`，由 `to_mauville` 驗證（`make check-oddex-full`）。理由都寫在範圍的註解裡。
- **已遷移**：
  - `apply_replacements`：
    - Route 110 的 land，加上 Route 109、Slateport、Route 110 的 fishing。
    - 訓練家（明確清單），包括 Route 110 勁敵 6 組：第 2 階段的御三家寫成 `STARTER_*_2` 代號（「Oddex Starter Fire 2」等），跟前面幾場勁敵戰用第 1 階段代號的做法一樣。
    - Edwin：Lombre → Shojomai、Nuzleaf → Karabeki。
  - 腳本、文字和造型：
    - Route 109 撿垃圾的 Kyokon。
    - Fan Club 的三隻寵物：Mandalumb、Kyokon，以及 Magatide。
    - Wally 那句「combine forces with ...」改用 `TUTORIAL_CATCH` 代號。
  - 範圍內的殘留是 0 筆。
- **Fan Club 的 Azumarill 對到 Magatide**：對照表沒有 Azumarill。它是 Marill 線的第 3 階段，而 Marill 對到 Magatide；這只是 NPC 的寵物，不牽涉進化。之後如果 Magatide 有了進化線，可以改成第 2 階段。
- **留在範圍外**：
  - 要衝浪才遇得到的水上野生。
  - 各訓練家的重戰（例如 EDWIN_2–5），要等之後的劇情階段才遇得到。
- **可達性**：`stage_reach.py` 從 Route 109 碼頭走得到海灘、Slateport、整條 Route 110（經過自行車道下方的木橋）和 Trick House 謎題 1 的第一個房間。之前的版本把木橋（`MB_BRIDGE_OVER_OCEAN`，名字裡有 OCEAN）當成水，誤判成只走得到 Route 110 南段；`plan.py` 和 `stage_reach.py` 現在共用 `is_water()`。修正後走得到的訓練家和明確清單相同。
- **`to_mauville`**：接在 `to_dewford` 後面。單獨執行約 530 秒，是 `check-oddex-full` 裡最長的一支。路線：
  1. Granite Cave（Steven 的信）。
  2. Briney 開船到 Route 109 → Fan Club → Stern 的船廠 → Museum 2F 打兩個 Aqua 手下 → 出 Museum 時 Scott 的劇情。
  3. Route 110：Birch 的劇情 → Kaleb、Isabel、Timmy → 勁敵 → Edwin → Alyssa、Edward。
  4. Mauville 跟 Wally 對戰。
  5. 在 Route 110 練到 Lv33 → 道館（Ben、開關 3）→ Wattson → DYNAMO BADGE。
  
  截圖 m01–m11：Kyokon、Magatide、Museum 的手下、勁敵和他的 Trekwheel、Edwin 的 Karabeki、Wally 的台詞和對戰、Wattson 的第一隻和王牌 Raijuoh、徽章。
  - 道館的電閘由 `setmetatile` 在執行時改變，而且 `FLAG_MAUVILLE_GYM_BARRIERS_STATE` 每次進地圖都會清掉，所以 `plan.py` 讀的靜態地圖不準。踩開關的路線要用執行中的地圖（`gBackupMapLayout`）規劃，也要避開不想踩的開關：已經按過的那個開關再踩沒有作用，踩到其他開關就會切換電閘。
  - 截圖不會讓遊戲多跑任何影格，但組合腳本時插入的 `wait` 會。曾經在 m03 前面多加了 `wait 20`，結果之後的戰鬥亂數全部錯開。截圖的時間點要在分段錄製時就做成一段，例如 `raw:wait 20`。
  - **平衡觀察（給使用者參考，未改動）**：隊伍只有御三家一隻時，Wattson 很難打。他有 Super Potion ×2，王牌帶 Sitrus Berry，還會用 Thunder Wave 和 Supersonic 讓我方空過回合。試錄時 Grinpack 的情況：
    - Lv25：打倒第 1、2 隻後輸掉。
    - Lv28（已學 Seed Bomb）：打倒 Suzurai 和 Kagurai。Kagurai 是鋼／電，只有 Crunch 有效，Crunch 只有 15 PP。之後只剩 19 HP，輸給 Raijuoh（電／惡，抵抗 Crunch），Raijumen 還沒出場。
    
    `damage_calc.py` 不算道具和異常狀態，所以會高估勝率。正式錄製時 Grinvine 在 Route 110 練到 Lv33 才打（Route 110 的野生只有 Lv12–13，經驗值又依等級差縮放，每場約 60–75 點），贏的時候還剩 77/92 HP。


## 9. 第 6 步第四段：Wattson 之後 → Flannery（第 4 個徽章）

`[lavaridge]` 的對照、方案 F 和手改都已經套用，回歸腳本是 `to_lavaridge`（§9.5）。等使用者核准新角色的美術後，再設成 `strict = true`。範圍的理由寫在 `content/migration_scope.toml` 的註解裡。

### 9.1 可達性

- 用 `stage_reach.py --rock-smash` 從 Mauville 出發判斷。拿到 Dynamo Badge 後，可以從 Mauville 的房子拿到 Rock Smash。Surf、Cut、Strength 都還不能用（Strength 要 Flannery 的徽章）。
- 另外從 Mt. Chimney 的纜車站跑一次：纜車是腳本 warp，BFS 看不到；Jagged Pass 往下走到 Lavaridge。
- **Route 111 的沙漠**要 Go-Goggles，在 Lavaridge 打完 Flannery 才拿到。沙漠入口是 `ViciousSandstorm` 的觸發格，把這些格子當成擋住再跑一次。
  - 沙漠裡的 8 名訓練家不列入：Heidi、Drew、Dusty、Beau、Becky、Bryan、Celia、Branden。
  - Route 111 的 land 野生全部在沙漠的沙地上（`MB_DEEP_SAND`），所以只列 fishing（路邊的池塘）和 rock smash。
- 劇情鎖：Route 112 的 Magma 手下和纜車要在 Meteor Falls 之後才放行，但這些都還在這一段裡。
- 野生表只列有格子走得到的種類（用 BFS 的結果數 land 格、岸邊、可碎的岩石）：
  - land：Route 112、113、114、117、Fiery Path、Jagged Pass、Meteor Falls 1F_1R。
  - fishing：Route 111（池塘）、114、115、117、118、Meteor Falls 1F_1R。
  - rock smash：Route 111、114、Granite Cave B2F（從 Dewford 起就走得到，有了 Rock Smash 就能碎岩）。
  - water_mons 要衝浪，不列入。
- 前面的範圍漏掉的訓練家，一起放在這裡：
  - Route 118 西岸的 4 名：從 Mauville 往東就走得到。
  - Route 115 南邊沙灘的 4 名：從 Rustboro 往北就走得到，現在也能從 Route 114 過去。
  - Rusturf Tunnel 東側的 Mike：用 Rock Smash 把隧道打通之後走得到。
- Flannery、Maxie、Winstrate 一家是腳本裡的戰鬥，不是地圖上的訓練家物件，所以手動加進清單。

為了這一段，工具做了三個修改：
- `stage_reach.py` 加上 `--rock-smash` 參數。
- `plan.py` 的 `load()`/`step()` 支援同一邊有好幾個 connection。例如 Route 111 的左邊是 Route 113（offset 0）和 Route 112（offset 20），以前後者會蓋掉前者，所以一直走不到 Route 113。這也影響 autopilot 的路線規劃。測試在 `tools/oddex/test_plan_step.py`。
- `migration_scope.toml` 的 `wild_maps` 可以寫成 `"Map:kind"`，只取那張地圖的某一種表，不受 `wild_kinds` 影響。例如 Route 111 只要 fishing，不要沙漠的 land。測試在 `test_apply_replacements.py`。

### 9.2 範圍內的原版角色

`check_species_refs.py --scope lavaridge`：340 筆、62 種。各類別的筆數：

| wild | party | script | text | gfx |
|---|---|---|---|---|
| 159 | 149 | 6 | 7 | 19 |

其中 27 種在 `replacements.toml` 還沒有對照。下表依進化線排列，「階段」是原版的進化階段，「目前對照」是 `replacements.toml` 現在的值：

| 進化線 | 物種 | 階段 | wild | party | script | text | gfx | 目前對照 |
|---|---|---|---|---|---|---|---|---|
| Aron | Aron | 1 |  | 6 |  |  |  | Bekurama |
| Azurill | Azurill | 1 |  |  | 1 | 2 | 1 | Shojobob |
| Azurill | Marill | 2 | 4 | 7 |  |  |  | Magatide |
| Azurill | Azumarill | 3 |  |  |  |  | 1 | **無** |
| Baltoy | Baltoy | 1 |  | 2 |  |  |  | **無** |
| Barboach | Barboach | 1 | 18 | 3 |  |  |  | **無** |
| Budew | Roselia | 2 |  | 8 |  |  |  | **無** |
| Carvanha | Carvanha | 1 | 5 |  |  |  |  | Kamorai |
| Carvanha | Sharpedo | 2 | 1 |  |  |  |  | **無** |
| Corphish | Corphish | 1 | 6 |  |  |  |  | **無** |
| Doduo | Doduo | 1 |  | 3 |  |  |  | **無** |
| Electrike | Electrike | 1 |  | 2 |  |  |  | Raijumen |
| Geodude | Geodude | 1 | 14 | 9 |  |  |  | Komarock |
| Geodude | Graveler | 2 |  | 1 |  |  |  | **無** |
| Goldeen | Goldeen | 1 | 8 | 2 |  |  |  | Kamorai |
| Grimer | Grimer | 1 | 2 |  |  |  |  | **無** |
| Illumise | Illumise | 1 | 4 |  |  |  |  | Torobi |
| Kecleon | Kecleon | 1 |  | 1 |  |  | 1 | **無** |
| Koffing | Koffing | 1 | 2 | 4 |  |  |  | **無** |
| Lotad | Lotad | 1 | 2 |  |  |  |  | Shojobob |
| Lotad | Lombre | 2 | 3 | 4 |  |  |  | Shojomai |
| Machop | Machop | 1 | 5 | 5 |  |  |  | Karuvajra |
| Magikarp | Magikarp | 1 | 12 | 1 |  |  |  | Magatide |
| Magnemite | Magnemite | 1 |  | 2 |  |  |  | Suzurai |
| Makuhita | Makuhita | 1 |  | 5 |  |  |  | Shishiblaze |
| Meditite | Meditite | 1 |  | 6 |  |  |  | Gachirinza |
| Nincada | Ninjask | 2 |  | 1 |  |  |  | **無** |
| Nosepass | Nosepass | 1 | 1 |  |  |  |  | Iwadawn |
| Numel | Numel | 1 | 16 | 15 |  |  |  | **無** |
| Numel | Camerupt | 2 |  | 2 |  |  |  | **無** |
| Oddish | Oddish | 1 | 3 | 1 |  |  |  | Okinoir |
| Pichu | Pikachu | 2 |  |  | 1 | 1 | 2 | Inarizuma |
| Poochyena | Poochyena | 1 | 2 | 2 | 1 |  | 11 | Shachound |
| Poochyena | Mightyena | 2 |  | 1 |  |  |  | Shachowl |
| Ralts | Ralts | 1 |  | 1 |  | 1 |  | Omotelle |
| Sandshrew | Sandshrew | 1 |  | 4 |  |  |  | **無** |
| Seedot | Seedot | 1 | 1 |  |  |  |  | Bekurama |
| Seedot | Nuzleaf | 2 | 1 | 3 |  |  |  | Karabeki |
| Seviper | Seviper | 1 | 3 | 1 |  |  |  | **無** |
| Shroomish | Shroomish | 1 |  | 9 |  |  |  | Yamambrr |
| Skarmory | Skarmory | 1 | 2 | 1 |  |  |  | **無** |
| Skitty | Skitty | 1 |  | 1 | 1 | 2 | 1 | Mandalumb |
| Slugma | Slugma | 1 | 4 | 7 |  |  |  | Shishiblaze |
| Solrock | Solrock | 1 | 3 |  |  |  |  | **無** |
| Spinda | Spinda | 1 | 7 | 2 |  |  |  | **無** |
| Spoink | Spoink | 1 | 4 | 1 |  |  |  | **無** |
| Swablu | Swablu | 1 | 3 | 1 |  |  |  | **無** |
| Taillow | Taillow | 1 |  | 4 |  |  |  | Shawabolt |
| Taillow | Swellow | 2 |  | 1 |  |  |  | **無** |
| Tentacool | Tentacool | 1 | 4 | 1 |  |  |  | Shojobob |
| Torkoal | Torkoal | 1 | 3 | 1 |  |  |  | Shishiblaze |
| Trapinch | Trapinch | 1 |  | 1 |  |  |  | **無** |
| Volbeat | Volbeat | 1 | 1 |  |  |  |  | Torobi |
| Wailmer | Wailmer | 1 | 6 | 1 |  |  |  | Kamorai |
| Whismur | Whismur | 1 |  | 2 |  |  |  | Mandalumb |
| Wingull | Wingull | 1 |  | 3 |  |  |  | Utoghast |
| Wurmple | Dustox | 3 |  | 1 |  |  |  | **無** |
| Wurmple | Beautifly | 3 |  | 1 |  |  |  | **無** |
| Wynaut | Wynaut | 1 |  |  | 1 |  |  | **無** |
| Zangoose | Zangoose | 1 |  | 1 |  |  |  | **無** |
| Zigzagoon | Zigzagoon | 1 |  | 5 | 1 | 1 | 2 | Kyokon |
| Zubat | Zubat | 1 | 9 | 3 |  |  |  | Komorimen |

script／text／gfx 的 32 筆要手改，不是 `apply_replacements` 會處理的：
- Mt. Chimney：10 個 Poochyena 物件（Aqua 和 Magma 兩邊手下的寵物，依 hide flag 分組）。
- Route 117 育幼屋院子裡的寵物：Azumarill、Kecleon、Pikachu、Zigzagoon。
- Verdanturf：Friendship Rater 的 Pikachu。
- Fallarbor：Azurill（造型、叫聲、2 句文字）；Mart 的 Skitty。
- Route 114：Poochyena。
- Lavaridge：民宅的 Zigzagoon；老婆婆送的 Wynaut 蛋（`giveegg`）。蛋是劇情送的角色，應該跟 `TUTORIAL_CATCH` 一樣用代號。
- Wanda 家的一句台詞提到 Ralts（Wally），改用 `TUTORIAL_CATCH` 代號。

### 9.3 回歸腳本的長度

`to_lavaridge` 要從開機接在 `to_mauville` 後面，而 `to_mauville` 單獨就約 530 秒。
- 以影格算，`to_mauville` 自己的部分約 72 萬格，其中 Route 110 練等（Lv24 → 33）就占了約 62 萬格（86%）。所以時間主要不是花在路線長度，而是花在單隻御三家為了打贏道館館主要大量練等。
- 把範圍在 Fallarbor 切成兩段，並不能讓任何一支腳本變短：每支都從開機跑，`to_lavaridge` 照樣包含前面所有的路。所以建議維持一個 `[lavaridge]` 範圍。
- 要控制時間，得處理練等，這三個方向要由使用者決定：
  1. Wattson／Flannery 的平衡（Mark 的分析）。草系的 Grinvine 打火系的 Flannery，練等只會比 Wattson 更多。
  2. 讓回歸路線抓第 2 隻角色當隊友（例如打 Flannery 用的水系）。
  3. 允許下一段的腳本從上一段在同一次檢查裡產生的 savestate 接著跑。這需要改 CLAUDE.md 的規則。
- 粗估：不練等的話 `to_lavaridge` 約 180 萬格（約 680 秒）；再加上打 Flannery 的練等，約 900 秒以上。
- 錄製要等 Mark 的新角色合併之後再做（角色數一改，長路線的 RNG 就會位移），之後一次重錄所有基準截圖。

### 9.4 不需要新角色、已經先做的手改

用 `replacements.toml` 現有的對照，跟 Rustboro、Dewford 那幾段一樣，改造型、叫聲和文字：
- Mt. Chimney 的 10 個 Poochyena 物件，以及 Route 114 的 Poochyena（造型、叫聲）→ Shachound。
- Fallarbor 的 Azurill（造型、叫聲、2 句文字）→ Shojobob。
- Fallarbor Mart 的 Skitty → Mandalumb。原本那句「用月之石讓 SKITTY 進化」改寫成「MANDALUMB 快到進化的等級了」，因為 Mandalumb 是 Lv20 升級進化。
- Lavaridge 民宅的 Zigzagoon，和 Route 117 育幼屋院子裡的 Zigzagoon → Kyokon。
- Verdanturf Friendship Rater 的 Pikachu，和 Route 117 育幼屋院子裡的 Pikachu → Inarizuma。
- Route 117 育幼屋院子裡的 Azumarill → Magatide（沿用 Mauville 段 Fan Club 的做法）。
- Wanda 家 Wally 的台詞：「my RALTS」改用 `bufferspeciesname` 加 `TUTORIAL_CATCH` 代號。
- Lavaridge 老婆婆送的蛋：`giveegg` 改用新代號 `EGG_GIFT`（名稱照 Mark 的提案），暫時指向 Wynaut。使用者核准的對照是 Gachirinza，Mark 那一批只要改 `roles.toml` 的值。
  - 為了不讓這個暫時的代號藏住原版角色，`check_species_refs.py` 現在也會解析 `oddex_species.h` 的代號：指向原版角色的代號，會被當成原版的引用回報。
- 還沒做：Route 117 育幼屋院子裡的 Kecleon，對照表沒有，要等 Mark。

### 9.5 `to_lavaridge`

接在 `to_mauville` 後面，單獨執行約 594 秒（方案 F 不用再練等）。路線：
1. 從 Mauville 的房子拿到 HM06，用背包教 Rock Smash（忘掉 Night Slash，Crunch 還在，惡系沒有少）。
2. 敲碎 Route 111 (19,100) 的岩石，經 Route 112 進 Fiery Path，從北邊出口到 Route 112 北段，再到 Route 113 → Fallarbor（截圖 Shojobob）→ Route 114 → Meteor Falls 的劇情 → 回 Fallarbor 回血。
3. 走回 Fiery Path（Route 112 北段到不了纜車）→ 搭纜車 → Mt. Chimney（截圖 Shachound）→ Tabitha、手下 → Maxie。
4. Jagged Pass → Lavaridge → 道館 → Flannery → HEAT BADGE。

截圖 v01–v06：Fallarbor 的 Shojobob、Mt. Chimney 的 Shachound、Maxie 的戰鬥（Shachowl）、Flannery 的戰鬥（Hifukko）、Kamadoro（方案 F，Lv24）、徽章。打 Flannery 時 Grinvine 在戰鬥中升到 Lv36，進化成 Grinarbor，最後剩 24/110 HP 贏了。

錄製時發現、已修正的問題：
- **HM 相容性**：Grinvine 原本學不了 Rock Smash，選草系或水系御三家的玩家會卡在 Mauville。David 決定每隻原創角色繼承它取代的原版角色的 HM 相容性；Mark 已經修好，並在 `gen_species` 加了檢查，任何一個 HM 沒有角色能學就會報錯。
- **autopilot 的轉向**：上一次 hold 剛結束就按另一個方向，遊戲會繼續走，所以原本只想轉向的輕按會多走一格（Route 113、Route 110 的來回衝過頭）。現在轉向前先放開 2 格影格。
- **autopilot 的忘招**：進化時學招（Horn Leech）的提示會選到 HM 招式 Rock Smash，遊戲拒絕忘掉 HM 後又重問，變成無限迴圈。現在 `slot_to_forget` 不會選 HM 招式（從 `tms_hms.h` 的 `FOREACH_HM` 解析）。測試在 `tools/oddex/test_autopilot.py`。
- **道館和隱藏物件**：Lavaridge 道館的洞和間歇泉是單向的 warp（只有一邊的地塊有 warp 行為），還有只能往下跳的崖，用 warp／崖的 BFS 一步一步走，遇到戰鬥就交給 autopilot。Route 112 纜車附近被藏起來的 Magma 手下，靜態地圖仍然會擋路，所以改用執行中的地圖規劃。這兩種走法現在都在 `tools/headless/authoring/stepwalk.py`（§6.4）：預設模式處理道館，`--live` 處理纜車附近。

只有在遊戲裡看過的手改：Fallarbor 的 Shojobob、Mt. Chimney 的 Shachound。Verdanturf、Route 117 育幼屋、Fallarbor Mart、Lavaridge 民宅和 Route 114 的手改，都不在這條路線上，只有 `check_maps` 和 `check_species_refs` 驗證過。Lavaridge 的蛋（`EGG_GIFT`）在畫面上看不出物種，只靠資料檢查。


## 10. 第 6 步第五段：Flannery 之後 → Norman（第 5 個徽章）

`[norman]`（`strict = false`）只定義了範圍，訓練家、野生資料和 ROM 都還沒動。範圍的理由寫在 `content/migration_scope.toml` 的註解裡。

### 10.1 可達性

- 用 `stage_reach.py --rock-smash --cut --strength` 判斷，從 Lavaridge 和 Dewford（Briney 的船是腳本，所以分開跑）各跑一次。這一段 Cut 和 Strength 都能用了（Cut 從 Rustboro 拿到，Strength 有 Flannery 的徽章就能用）。Surf 要打完 Norman 才由 Wally 的爸爸給，所以水上還是不算。Go-Goggles 讓 Route 111 的沙漠可以進去。
  - `stage_reach.py` 為此新增了 `--cut`、`--strength` 參數。shortcut：`--strength` 把所有大石頭都當成可以通過，石頭被推進死路的情況沒有模擬，石頭謎題要人工確認。
- 人工判斷、留在範圍外的劇情鎖：
  - Magma Hideout：要 Magma Emblem，之後才拿到。
  - Desert Ruins：點字封印，破關後才開。
  - Desert Underpass、Terra Cave：都是破關後才有。
- 留在範圍外的設施：Trainer Hill、各個 Battle Tent。
- 重戰（EDWIN_2 等）照舊不列入：它們的隊伍屬於觸發重戰時的徽章數。
- Trick House：謎題 2 要 3 個徽章，謎題 3 要 4 個（Flannery），謎題 4 要 Norman 的徽章，所以 1–3 在範圍內。謎題是腳本 warp 進去的，謎題 2 的門靠開關打開，BFS 看不到，所以謎題 2、3 的訓練家是人工判斷加入的。
- 新增 34 名訓練家：
  - 沙漠 8 名。
  - 要 Cut 才走得到的 12 名：Route 116 北側 4 名、Route 103 東側 6 名（從 Route 110 過去）、Trick House 謎題 1 剩下的 2 名。
  - Trick House 謎題 2、3 各 3 名。
  - Petalburg 道館 7 名和 Norman。
  - 以前提過 Route 116 的 Janice 這幾位要 Cut；現在都納入了。仍然要衝浪的有：Route 103 的 Isabelle、Pete，Route 106、107、109、115、118 的水上訓練家。
- 野生表：
  - Route 111 的 land：沙漠，要 Go-Goggles。
  - Mirage Tower 1F–4F 的 land。
  - Altering Cave 的 land：表 2–9（Mareep、Pineco 等 8 種）只會因為 Mystery Event（`VAR_ALTERING_CAVE_WILD_SET`）而切換，正常遊戲用不到，所以用 `exclude_refs` 排除，只保留表 1（Zubat）。
  - Petalburg、Route 102、103 的 fishing：從 Dewford 拿到 Old Rod 起就能釣，之前的範圍漏掉了。
- Devon 的化石復原：用 Mirage Tower 的 Root／Claw Fossil 復原。之前在 `[rustboro]` 用 `exclude_refs` 排除，現在走得到了，所以 `RustboroCity_DevonCorp_2F` 列進這個範圍的 `maps`。

工具修正：
- `exclude_refs` 以前只有 `check_species_refs` 在 script／text／gfx 時讀，`apply_replacements` 完全不讀。現在兩個工具在所有類別都會讀，排除的條目在套用時也會跳過。測試在 `test_apply_replacements.py`。

### 10.2 範圍內的原版角色

`check_species_refs.py --scope norman`：171 筆、47 種。各類別的筆數：

| wild | party | script |
|---|---|---|
| 102 | 59 | 10 |

其中 5 種還沒有對照。下表依進化線排列：

| 進化線 | 物種 | 階段 | wild | party | script | 出現 | 目前對照 |
|---|---|---|---|---|---|---|---|
| Anorith | Anorith | 1 |  |  | 5 | RustboroCity_DevonCorp_2F | **無** |
| Azurill | Marill | 2 |  | 4 |  | trainer | Magatide |
| Baltoy | Baltoy | 1 | 3 | 3 |  | Route111, trainer | Gachirinza |
| Budew | Roselia | 2 |  | 1 |  | trainer | Higanmen |
| Cacnea | Cacnea | 1 | 3 |  |  | Route111 | **無** |
| Carvanha | Sharpedo | 2 | 1 |  |  | Route103 | Raijuoh |
| Corphish | Corphish | 1 | 12 |  |  | PetalburgCity, Route102 | Namazura |
| Geodude | Geodude | 1 |  | 1 |  | trainer | Komarock |
| Geodude | Graveler | 2 |  | 1 |  | trainer | Mandaring |
| Goldeen | Goldeen | 1 | 4 |  |  | PetalburgCity, Route102 | Kamorai |
| Igglybuff | Wigglytuff | 3 |  | 1 |  | trainer | **無** |
| Kecleon | Kecleon | 1 |  | 1 |  | trainer | Kyozosu |
| Lileep | Lileep | 1 |  |  | 5 | RustboroCity_DevonCorp_2F | **無** |
| Lotad | Lotad | 1 |  | 1 |  | trainer | Shojobob |
| Lotad | Lombre | 2 |  | 1 |  | trainer | Shojomai |
| Magikarp | Magikarp | 1 | 6 | 2 |  | PetalburgCity, Route102, Route103, trainer | Magatide |
| Makuhita | Makuhita | 1 |  | 1 |  | trainer | Shishiblaze |
| Minun | Minun | 1 |  | 1 |  | trainer | Tomoeden |
| Nosepass | Nosepass | 1 |  | 1 |  | trainer | Iwadawn |
| Numel | Numel | 1 |  | 1 |  | trainer | Hifukko |
| Oddish | Oddish | 1 |  | 1 |  | trainer | Okinoir |
| Plusle | Plusle | 1 |  | 1 |  | trainer | Tomoeden |
| Poochyena | Poochyena | 1 |  | 1 |  | trainer | Shachound |
| Ralts | Ralts | 1 |  | 2 |  | trainer | Omotelle |
| Sandshrew | Sandshrew | 1 | 27 | 5 |  | MirageTower_1F, MirageTower_2F, MirageTower_3F, MirageTower_4F, Route111, trainer | Yamambrr |
| Sandshrew | Sandslash | 2 |  | 2 |  | trainer | **無** |
| Seedot | Nuzleaf | 2 |  | 1 |  | trainer | Karabeki |
| Shroomish | Shroomish | 1 |  | 3 |  | trainer | Yamambrr |
| Skitty | Skitty | 1 |  | 3 |  | trainer | Mandalumb |
| Skitty | Delcatty | 2 |  | 1 |  | trainer | Mandaring |
| Slakoth | Slakoth | 1 |  | 1 |  | trainer | Mandalumb |
| Slakoth | Vigoroth | 2 |  | 2 |  | trainer | Mandaring |
| Slakoth | Slaking | 3 |  | 1 |  | trainer | Mandaloka |
| Spinda | Spinda | 1 |  | 2 |  | trainer | Mandalumb |
| Swablu | Swablu | 1 |  | 1 |  | trainer | Utoghast |
| Taillow | Taillow | 1 |  | 1 |  | trainer | Shawabolt |
| Taillow | Swellow | 2 |  | 1 |  | trainer | Utomaw |
| Tentacool | Tentacool | 1 | 2 | 1 |  | Route103, trainer | Shojobob |
| Trapinch | Trapinch | 1 | 27 |  |  | MirageTower_1F, MirageTower_2F, MirageTower_3F, MirageTower_4F, Route111 | Mandalumb |
| Voltorb | Voltorb | 1 |  | 1 |  | trainer | Suzurai |
| Wailmer | Wailmer | 1 | 5 |  |  | Route103 | Kamorai |
| Wingull | Wingull | 1 |  | 1 |  | trainer | Utoghast |
| Wurmple | Beautifly | 3 |  | 1 |  | trainer | Yokozunat |
| Zangoose | Zangoose | 1 |  | 1 |  | trainer | Kyozosu |
| Zigzagoon | Zigzagoon | 1 |  | 4 |  | trainer | Kyokon |
| Zigzagoon | Linoone | 2 |  | 1 |  | trainer | Kyozosu |
| Zubat | Zubat | 1 | 12 |  |  | AlteringCave | Komorimen |

- 化石：Lileep、Anorith（`givemon`、`bufferspeciesname`，共 10 筆）是劇情送的角色，建議跟 `EGG_GIFT` 一樣做成代號（例如 `FOSSIL_ROOT`、`FOSSIL_CLAW`），也需要對應的原創角色。
- 還沒有對照的另外 3 種：Cacnea（沙漠野生 3 欄）、Sandslash（Sandshrew 線第 2 階段，party 2：Bryan、Dusty；Sandshrew 已經對到 Yamambrr）、Wigglytuff（Igglybuff 線第 3 階段，Alexia 的 party 1）。

### 10.3 回歸腳本 `to_norman` 的預估

- 路線（最短）：
  1. 在 Lavaridge 從勁敵拿到 Go-Goggles。
  2. Route 112 → Route 111 → Mauville → Route 117 → Verdanturf → Rusturf Tunnel → Rustboro → Route 104 → Petalburg Woods → Petalburg 道館。
  3. 道館裡依序打開門、打訓練家 → Norman。
  4. 如果要截圖化石：加走沙漠／Mirage Tower 拿化石，再到 Rustboro 的 Devon 2F 復原。
- 長度：`to_lavaridge` 自己的部分約 15 萬格（約 60 秒），`to_norman` 自己的部分估計 15–25 萬格。加上化石的繞路，再多約 10 萬格。所以從開機跑 `to_norman` 約 650–690 秒，加化石約 730 秒，會超過約 600 秒的指引（§9.3 的方向 3 可以解決這個問題）。
- Norman 前的隊伍：只有 Grinarbor（`to_lavaridge` 打 Flannery 時，在 Lv36 進化）。再打路上和道館的訓練家，估計到 Norman 時約 Lv37–38。招式：Rock Smash（格鬥，打一般系 2 倍，但威力只有 40）、Seed Bomb、Giga Drain、Crunch。如果路線去復原化石，隊伍會多一隻 Lv20 的化石角色。Norman 原版的隊伍是 Spinda、Vigoroth、Linoone、Slaking（Lv31，Truant），換成對照之後的平衡計算交給 Mark。
