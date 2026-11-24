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
  - 預設：用地圖資料做 BFS，會跨 warp 和崖，例如 Lavaridge 道館的洞和間歇泉。只有地塊有 warp 行為（warp、門、梯子、洞）的那一邊才能用，所以單向的 warp 也算得對。門的地塊本身有碰撞，走進去才會開，所以不當成牆。出口的地墊（箭頭 warp）要先站上去，再往箭頭方向按一次才會傳送。走的範圍是起點和終點所屬的區域（地圖名稱第一個 `_` 之前相同的地圖，例如 `LavaridgeTown`、它的民宅和道館），不跨 connection，跨地圖的路先用 autopilot 走到區域裡。
    - 修正（`to_norman` 錄製時）：以前把「踩上出口地墊」當成已經傳送，於是在地墊和上面那格之間來回，直到步數上限，什麼都不輸出（David 從 Lavaridge 道館出來時遇到）。以前也只認名稱裡有 `WARP` 的行為，門和梯子都走不過去；範圍只有終點的同一層，城鎮和建築之間走不通。測試在 `tools/oddex/test_autopilot.py`。
  - `--live`：用執行中的地圖（`gBackupMapLayout`）和物件目前的位置規劃，例如已經藏起來的物件、`setmetatile` 改過的電閘、打完之後走過來擋路的訓練家。不想踩的格子（例如道館的開關）用 `--avoid x,y;...` 避開。
  - 用法：`stepwalk.py START.ss OUT_PREFIX MAP X Y [--live] [--avoid ...]`。
- **防止空轉**：總共執行超過 `AP_MAX_STEPS` 個單位（預設 20000），或在戰鬥外同一位置連續 100 次送出同一個指令，就印出原因、已執行的指令和最後的狀態，以 exit 3 結束（`AP_PARTIAL=1` 也一樣會失敗）。起因是 Mauville 練等時，練等格上跳出 Match Call 的訊息，`grind` 在練等格上遇到操作被鎖住只會 `wait 30`，而 B 只在「走一步沒動」時才按，結果空轉了 32 萬步（約 5 小時 40 分）都沒停；那時攻擊招式還剩 Aerial Ace 的 19 PP，高於暫停門檻 10，所以也沒有因為 PP 不足而暫停。現在練等格上連續 3 次操作被鎖住就按 B。
- **`resync.py`**：ROM 一改（角色數、美術、版面）讓長路線的亂數位移時，用來重新同步回歸腳本。
  - 用法：`resync.py prepare OLD_GAME WORK SCRIPT` → `run WORK` → `shots WORK K NAME...` → `assemble WORK`。`OLD_GAME` 是錄製時那個 commit 編好的 `game/`，例如用 `git worktree` 另外編一份。
  - 腳本先切成段落：在註解、檔案邊界、每 40 個指令的地方切開。新舊 ROM 各跑一次，每段結束時存 savestate。
  - 從第一個不一樣的段落開始，依序嘗試：照舊指令重播 → 補完戰鬥和訊息 → autopilot／stepwalk → 走到門口再進去 → 跟著舊 ROM 逐指令的軌跡走。
  - 接受一段的條件：位置相同、等級不低於舊的，而且**打敗的訓練家數不能少**。只比位置的話，曾經繞過 Flannery 沒打。
  - 截圖用 `shots` 放回最接近基準截圖的那一格。長時間練等改成手動用 autopilot `grind:`。
  - 第一次用在 Winona 批的美術上，見 §11.5。
  - 測試在 `tools/oddex/test_resync.py`（只測切段、接受條件、重組）。`prepare` 拿同一個 ROM 跑過，結果是沒有差異。`run` 用的是錄製時在暫存區的原型，正式版還沒完整跑過一次。
- **反彈招式**：`best_move` 看對手的招式，對手有 Counter 時物理招式的分數乘 0.25，有 Mirror Coat 時特殊招式也一樣。Norman 的 Mandaloka 用 Counter 把 Seed Bomb 加倍反彈，一擊打倒 Grinarbor；改成用 Giga Drain 之後就贏了。
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

只有在遊戲裡看過的手改：Fallarbor 的 Shojobob、Mt. Chimney 的 Shachound。Verdanturf、Route 117 育幼屋和 Lavaridge 民宅的手改後來在 `to_norman` 裡看到了（§10.4）；Fallarbor Mart 和 Route 114 的仍然沒有。Lavaridge 的蛋（`EGG_GIFT`）在畫面上看不出物種，只靠資料檢查。


## 10. 第 6 步第五段：Flannery 之後 → Norman（第 5 個徽章）

`[norman]`（`strict = true`）：對照（Mark 的 Norman 批：Haniwort、Dogoggle、Sphinmen）已經套用，回歸腳本是 `to_norman`（§10.4）。範圍的理由寫在 `content/migration_scope.toml` 的註解裡。

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

### 10.4 `to_norman`

接在 `to_lavaridge` 後面，從開機約 640 秒（同時跑兩次的時間）。路線：
1. 出道館，勁敵給 Go-Goggles → Lavaridge 民宅（截圖 n01：Kyokon 的造型和台詞）→ 回血 → Route 112 → Route 111（岩石進地圖就會復原，要再敲一次）→ Mauville：Rydel 給 Mach Bike，從背包登記到 SELECT。
2. Route 111 的沙漠 → Mirage Tower。塔是否出現，每次進 Route 111 都隨機決定（`SetMirageTowerVisibility`，50%），這次錄製剛好出現；前面的路線一改，就要重新確認。
   - 2F 的裂地板要騎 Mach Bike 全速通過：連續騎第 3 格才是全速，轉彎不會減速，停在裂地板上就會掉下去。騎車的段落是逐格依玩家所在的地塊決定方向錄的。3F 右邊的裂地板是死路，要走左邊敲岩石。
   - 3F、4F 要 Rock Smash（騎在車上也能用）。拿 Root Fossil 之後塔會崩塌，回到 Route 111。
3. 南下 Mauville → Route 117（截圖 n02：育幼屋院子的 Kyokon、Kyozosu）→ Verdanturf Friendship Rater 的家（截圖 n03：Inarizuma）→ 回血 → Rusturf Tunnel（敲岩石，接著是 Wanda 的劇情）→ Route 116 → Rustboro → Devon 2F。
   - 交出 Root Fossil 後跟另一位研究員說話，復原就完成了，拿到 Haniwort（`FOSSIL_ROOT` 代號，Lv20），截圖 n04 是它的能力畫面。
4. 回血 → Route 104 → Petalburg Woods → Petalburg 道館。
   - 道館的門是告示牌：面向門按 A，再選 YES。
   - 走 Speed room（Randall）→ Confusion room（Parker）→ Strength room（Jody）→ Norman（截圖 n05 戰鬥、n06 王牌 Mandaloka、n07 徽章）。
   - 之後 Wally 爸爸的劇情一路按 B 到 Wally 家，拿到 HM03 Surf。Grinarbor 在 Lv37 剩 110/113 HP 贏了。

錄製時發現、已處理的問題：
- Friendship Rater 的 Inarizuma 台詞還是「Pika pika!」，改成同樣長度的「Kokon-zap!」。長度相同，ROM 的版面就不會變，之前存的 savestate 仍然能用。
- autopilot 會被 Counter 打敗（見 §6.4）。
- stepwalk 的出口地墊、門、梯子和範圍（見 §6.4）。
- 剛停下時，3 格的轉向輕按會被吃掉。敲岩石之前改用 `hold DIR 16`：前面是岩石，所以只會轉向。

給 Mark 確認：Kyokon 的走路圖朝下的影格是白色、比較大的角色，朝左右時是棕色的狐狸，像是別的角色的影格混了進來（Lavaridge 民宅、Route 117 都看得到）。

仍然只靠資料檢查、沒在遊戲裡看過：
- Route 117 育幼屋院子的 Magatide (42,2) 和 Inarizuma (51,1)，截圖裡辨認不出來（Inarizuma 在育幼屋後面）。
- Fallarbor Mart 的 Mandalumb、Route 114 的 Shachound。
- Lavaridge 的蛋（`EGG_GIFT`，看不出物種）。
- Claw Fossil 那條（`FOSSIL_CLAW` = Dogoggle）：路線選了 Root Fossil。

## 11. 第 6 步第六段：Norman 之後 → Winona（第 6 個徽章）

`[winona]`（`strict = true`）：對照（Mark 的 Winona 批）、Ichimai 和代號都已經套用，回歸腳本是 `to_winona`（§11.6）。範圍的理由寫在 `content/migration_scope.toml` 的註解裡。

### 11.1 可達性

- 用 `stage_reach.py --rock-smash --cut --strength --surf` 從 Petalburg 跑。`--surf` 是這一段新增的：水面可以走，瀑布不行（Waterfall 之後才拿到）。Surf 是打完 Norman 後由 Wally 的爸爸給的 HM03。
- 有了 Surf，整片海都連起來了，所以故事上還到不了的地方用地圖名單排除，再跑一次 BFS：
  - Route 121 以後、Lilycove、Mt. Pyre、Aqua Hideout、東邊的海、Pacifidlog、Shoal Cave：在故事上都在 Fortree 之後。Route 120 的橋要用 Devon Scope 打開，Devon Scope 在 Winona 之前就拿得到，但橋後面的地方交給下一段。
  - New Mauville：要 Basement Key。
  - Island Cave、Ancient Tomb：點字封印，破關後才開。
  - Abandoned Ship 的隱藏樓層和水下：要 Dive。
- 跟沒有 Surf 的結果相比，新增 88 名訓練家，再加上 Route 119 的勁敵（腳本，6 種組合）和 Winona：
  - Surf 補漏：Route 103 東側的 Isabelle、Pete；Route 105–109、115 的游泳選手和島上的訓練家；Abandoned Ship 的 7 名。
  - 新區域：Route 118 東側、Route 119、Weather Institute（Shelly 和 5 名手下）、Route 120、Fortree 道館的 6 名。
- 野生表 30 個：
  - 以前的路線的 `water_mons`（Route 102–111、114、115、117，Dewford、Slateport、Petalburg，Meteor Falls 1F）。
  - 以前漏掉的 `land_mons`：Route 115、Route 118 西側。
  - 新區域：Route 118–120 的 land／water／fishing、Route 105 和 108 的 fishing、Abandoned Ship B1F。

### 11.2 範圍內的原版角色

`check_species_refs.py --scope winona`：422 筆、74 種。各類別的筆數：

| wild | party | script | text | gfx |
|---|---|---|---|---|
| 203 | 181 | 10 | 9 | 19 |

其中 20 種還沒有對照。下表依進化線排列：

| 進化線 | 物種 | 階段 | wild | party | script/text/gfx | 出現 | 目前對照 |
|---|---|---|---|---|---|---|---|
| Abra | Kadabra | 2 |  | 1 |  | trainer | **無** |
| Absol | Absol | 1 | 2 |  |  | Route120 | **無** |
| Azurill | Marill | 2 | 27 | 7 |  | PetalburgCity, Route102, Route111, Route114, Route117, Route120, trainer | Magatide |
| Baltoy | Baltoy | 1 |  | 1 |  | trainer | Sphinmen |
| Barboach | Barboach | 1 | 6 |  |  | Route120 | Namazura |
| Budew | Roselia | 2 |  | 2 |  | trainer | Higanmen |
| Carvanha | Carvanha | 1 | 6 | 10 |  | Route119, trainer | Kamorai |
| Castform | Castform | 1 |  | 1 |  | trainer | **無** |
| Castform_Normal | Castform_Normal | 1 |  |  | 3 | Route119_WeatherInstitute_2F | **無** |
| Doduo | Doduo | 1 |  | 3 |  | trainer | Karuvajra |
| Doduo | Dodrio | 2 |  | 1 |  | trainer | **無** |
| Electrike | Electrike | 1 | 2 | 1 |  | Route118, trainer | Raijumen |
| Electrike | Manectric | 2 | 1 | 4 |  | Route118, trainer | Raijuoh |
| Feebas | Feebas | 1 |  | 1 |  | trainer | **無** |
| Goldeen | Goldeen | 1 | 7 | 7 |  | Route102, Route111, Route114, Route117, Route120, trainer | Kamorai |
| Gulpin | Gulpin | 1 |  | 1 |  | trainer | Kumozuka |
| Horsea | Horsea | 1 |  | 2 |  | trainer | **無** |
| Igglybuff | Jigglypuff | 2 | 2 |  |  | Route115 | **無** |
| Illumise | Illumise | 1 |  | 2 |  | trainer | Torobi |
| Kecleon | Kecleon | 1 | 3 |  | 13 | FortreeCity, Route118, Route119, Route120 | Kyozosu |
| Koffing | Koffing | 1 |  | 5 |  | trainer | Kumozuka |
| Lotad | Lotad | 1 |  | 1 |  | trainer | Shojobob |
| Lotad | Lombre | 2 |  | 7 |  | trainer | Shojomai |
| Machop | Machop | 1 |  | 2 |  | trainer | Karuvajra |
| Machop | Machoke | 2 |  | 2 |  | trainer | **無** |
| Magikarp | Magikarp | 1 | 10 | 1 |  | AbandonedShip_Rooms_B1F, Route105, Route108, Route119, Route120, trainer | Magatide |
| Makuhita | Makuhita | 1 |  | 2 |  | trainer | Shishiblaze |
| Makuhita | Hariyama | 2 |  | 1 |  | trainer | **無** |
| Meditite | Meditite | 1 |  | 2 |  | trainer | Gachirinza |
| Mudkip | Marshtomp | 2 |  | 2 |  | trainer | Ridgefin |
| Natu | Natu | 1 |  | 1 |  | trainer | **無** |
| Natu | Xatu | 2 |  | 1 |  | trainer | **無** |
| Nincada | Nincada | 1 |  | 2 |  | trainer | Kumozuka |
| Nincada | Ninjask | 2 |  | 6 |  | trainer | Torobi |
| Numel | Numel | 1 |  | 1 |  | trainer | Hifukko |
| Oddish | Oddish | 1 | 7 |  |  | Route119, Route120 | Okinoir |
| Oddish | Gloom | 2 |  | 1 |  | trainer | **無** |
| Plusle | Plusle | 1 |  |  | 1 | FortreeCity_House1 | Tomoeden |
| Poochyena | Poochyena | 1 | 1 | 4 |  | Route120, trainer | Shachound |
| Poochyena | Mightyena | 2 | 2 | 1 |  | Route120, trainer | Shachowl |
| Ralts | Kirlia | 2 |  | 1 |  | trainer | Deigloom |
| Sableye | Sableye | 1 |  | 1 |  | trainer | Kyokon |
| Sandshrew | Sandshrew | 1 |  | 4 |  | trainer | Yamambrr |
| Sandshrew | Sandslash | 2 |  | 3 |  | trainer | Mandaring |
| Seedot | Seedot | 1 | 1 | 1 |  | Route120, trainer | Bekurama |
| Seedot | Nuzleaf | 2 |  | 2 |  | trainer | Karabeki |
| Shroomish | Breloom | 2 |  | 1 |  | trainer | **無** |
| Skarmory | Skarmory | 1 |  | 5 |  | trainer | Daibeki |
| Slugma | Slugma | 1 |  | 5 |  | trainer | Shishiblaze |
| Solrock | Solrock | 1 | 3 |  |  | MeteorFalls_1F_1R | Iwadawn |
| Spheal | Spheal | 1 |  | 1 |  | trainer | **無** |
| Staryu | Staryu | 1 |  | 1 |  | trainer | **無** |
| Surskit | Surskit | 1 |  | 4 |  | trainer | **無** |
| Swablu | Swablu | 1 | 2 | 5 |  | Route115, trainer | Utoghast |
| Swablu | Altaria | 2 |  | 1 |  | trainer | **無** |
| Taillow | Taillow | 1 | 3 | 2 |  | Route115, trainer | Shawabolt |
| Taillow | Swellow | 2 | 1 | 4 |  | Route115, trainer | Utomaw |
| Tentacool | Tentacool | 1 | 27 | 11 |  | AbandonedShip_Rooms_B1F, DewfordTown, Route103, Route105, Route106, Route107, Route108, Route109, Route110, Route115, Route118, Route119, SlateportCity, trainer | Shojobob |
| Tentacool | Tentacruel | 2 | 4 | 2 |  | AbandonedShip_Rooms_B1F, trainer | **無** |
| Torchic | Combusken | 2 |  | 2 |  | trainer | Trekwheel |
| Treecko | Grovyle | 2 |  | 2 |  | trainer | Grinvine |
| Tropius | Tropius | 1 | 3 | 4 |  | Route119, trainer | **無** |
| Volbeat | Volbeat | 1 |  | 2 | 1 | FortreeCity_House1, trainer | Torobi |
| Wailmer | Wailmer | 1 | 12 | 5 |  | Route105, Route108, trainer | Kamorai |
| Wingull | Wingull | 1 | 36 | 9 | 14 | DewfordTown, FortreeCity_House4, Route103, Route104, Route105, Route106, Route107, Route108, Route109, Route110, Route115, Route118, Route119, Route119_House, SlateportCity, trainer | Utoghast |
| Wingull | Pelipper | 2 | 26 | 5 |  | DewfordTown, Route103, Route104, Route105, Route106, Route107, Route108, Route109, Route110, Route115, Route118, Route119, SlateportCity, trainer | Utomaw |
| Wurmple | Wurmple | 1 |  | 2 |  | trainer | Usobuzz |
| Wurmple | Cascoon | 2 |  | 1 |  | trainer | Tsunacoon |
| Wurmple | Silcoon | 2 |  | 1 |  | trainer | Tsunacoon |
| Wurmple | Beautifly | 3 |  | 2 |  | trainer | Yokozunat |
| Wurmple | Dustox | 3 |  | 2 |  | trainer | Yokozunat |
| Zigzagoon | Zigzagoon | 1 | 4 | 1 | 6 | FortreeCity_House1, FortreeCity_House5, Route118, Route119, trainer | Kyokon |
| Zigzagoon | Linoone | 2 | 3 |  |  | Route118, Route119 | Kyozosu |
| Zubat | Zubat | 1 | 2 | 3 |  | MeteorFalls_1F_1R, trainer | Komorimen |

script／text／gfx 的手改（不是 `apply_replacements` 會處理的）：
- Weather Institute 送的 Castform（`givemon`、`setvar`、`bufferspeciesname`）：劇情送的角色，建議做成代號（例如 `WEATHER_GIFT`）。Castform 會隨天氣變形，原創角色要不要有形態由 Mark 決定。
- Route 120 和 Fortree 的隱形 Kecleon：Steven 的戰鬥（`setwildbattle`、叫聲）、Fortree 道館前和 Route 119、120 的 Kecleon 物件，包括橋上的影子圖（`OBJ_EVENT_GFX_KECLEON_BRIDGE_SHADOW`）。Kecleon 目前對照到 Kyozosu；劇情用到的這幾處建議做成代號（例如 `HIDDEN_BLOCKER`），Devon Scope 的台詞也要對得上。
- 寵物和文字：Fortree 民宅的 Zigzagoon（House1、House5）、House1 文字裡的 Volbeat 和 Plusle、House4 和 Route 119 民宅的 Wingull。
- 已經先做（不需要新角色）：Fortree House1、House5 的 Zigzagoon → Kyokon；Fortree House4 和 Route 119 民宅的 Wingull → Utoghast（造型、叫聲、文字；House4 一句太長，重新換行）。Fortree House4 的 Wingull 會飛去 Mossdeep House2 送信，所以那一隻也一起改成 Utoghast，雖然 Mossdeep 不在這個範圍。
- C 裡寫死的角色（`c_files` 目前都是空的）：
  - Route 119 的 Feebas：`src/wild_encounter.c` 的 `gWildFeebas`，這個檔案裡只有這一筆 species。
  - 遊戲內交換（`src/data/trade.h`）：Fortree House1 用 Volbeat 換 Plusle。它的對話文字也提到兩者的名字。Rustboro House1 的交換（用 Ralts 換 Seedot）在 `[rustboro]` 時也漏掉了。

**已改（David 核准，見 DECISIONS.md）：Feebas 和遊戲內交換都在這一段就改，不留到第 5 步的 C 清理。**
- 理由：這兩個不是看不到的資料，玩家碰得到。原版角色已經停用，所以 debug build 會 assert（`check-oddex` 會當成 crash），release build 會變成 `SPECIES_NONE` 的戰鬥或交換。
  - Feebas 從 Dewford 拿到 Old Rod 起就釣得到，Route 119 的 Feebas 格在這一段就走得到。
  - Rustboro 的交換從第 2 段起就是壞的。
  - 用 `exclude_refs` 擋著，等於把一個玩得到的錯誤藏起來，而且 `check_species_refs` 再也不會提醒。
- Feebas：`gWildFeebas` 改成代號 `SPECIES_ODDEX_FISHING_SPOT`，暫定 Namazura（只在幾個釣點出現的稀有魚，Mark 那一批可以改）。`[winona]` 的 `c_files = ["src/wild_encounter.c"]`，這個檔案裡只有這一筆 species。
- 交換：用 `TRADE_RUSTBORO`／`_WANT`（Bekurama／Omotelle，取代 Seedot／Ralts）、`TRADE_FORTREE`／`_WANT`（Tomoeden／Torobi，取代 Plusle／Volbeat）四個代號，照 `replacements.toml` 的對照。
  - 暱稱 DOTS → KURAMA（鞍馬的天狗）、PLUSES → TOMOE。
  - Fortree 的交換信件，原本的 `EC_POKEMON(PLUSLE)`、`EC_POKEMON(VOLBEAT)` 改成一般單字（BE NICE TO IT! YOU WILL BE FANTASTIC），因為原創角色沒有 easy chat 單字。
  - Fortree House1 交換後的台詞也一起改了。
  - `trade.h` 放進 `[rustboro]` 的 `c_files`，strict 會擋下漏改的交換。檔案裡其他的交換（Pacifidlog、Battle Frontier、FRLG）用 `exclude_refs` 排除，等各自的段落再改。
- 只靠資料檢查：兩個交換都要玩家先有對方要的角色，現有的路線都沒有，所以沒有在遊戲裡交換過。`to_rustboro` 會經過 Rustboro，但在那裡多加截圖，後面所有的長路線都要重錄，所以不划算。`to_winona` 錄製時，可以順路跟 Fortree House1 的人說話，拍他開出交換條件的台詞（台詞用 `STR_VAR` 填入兩個名字），代價只是一小段路。

### 11.3 Ichimai：Route 120 的稀有野生角色

使用者決定把 Ichimai（Okiku，幽靈／水，Mark 在做）放在 Route 120 當稀有的野生角色。方案：換掉 Route 120 `land_mons` 機率 1% 的欄位之一。
- 欄位 10 是 Kecleon（1%）：Route 120 的隱形 Kecleon 是這條路的特色，保留。
- 欄位 11 是 Seedot（1%，Lv25）：Seedot 在別的地方很常見，在這裡只是陪襯，所以換成 `SPECIES_ICHIMAI`。
- 時機：`SPECIES_ICHIMAI` 要等 Mark 那一批合併後才存在，在那之前寫進去會編不過。到時候直接改這一格（不經過 `replacements.toml`），`apply_replacements` 看到原創角色會跳過，重複執行結果也不變。


### 11.4 `to_winona` 的事前調查（還沒錄）

- 錄製要等 Mark 的對照和 Winona 那一批合併（角色數一改，長路線的 RNG 就會位移）。Mark 也用同一個比例重新產生了所有角色的走路圖。這也會讓長路線的亂數位移：`main.c` 每個 VBlank 都呼叫 `AdvanceRandom()`，走路圖載入的時間一變，到處走的 NPC 就會走到別的位置。所以等整批合併後，`to_dewford` 到 `to_norman` 再加上 `to_winona` 一次重錄。
- 路線：Wally 家拿到 Surf → Route 118 東側（要衝浪過河）→ Route 119（北邊 (25,31)、(26,31) 的勁敵觸發格）→ Weather Institute（Shelly 和手下，送 Castform）→ Fortree → Route 120 橋上的 Steven（Devon Scope，跟隱形 Kecleon 戰鬥）→ 回 Fortree 道館 → Winona。
- 工具上要先補的：
  - autopilot／plan／stepwalk 目前都把水當成牆。衝浪要面向水按 A、選 YES，所以要加「上水」的單位，水上再用一般的移動。
  - Fortree 道館的旋轉門（`src/rotating_gate.c` 的 `sRotatingGate_FortreePuzzleConfig`，8 個門）不是物件，也不在碰撞資料裡，靜態規劃和 `--live` 都看不到。要寫一個模擬旋轉門狀態的小 BFS，或照原版的解法手寫路線。

### 11.5 Winona 批之後的重錄

Winona 批的美術改了走路圖，載入時間跟著變，亂數從 Slateport 開始位移，所以 `to_mauville`、`to_lavaridge`、`to_norman` 都重新同步了（`resync.py` 的原型）。
- Route 110 的練等（Lv24 → 33）改成手動用 autopilot `grind:` 重做。
- Fan Club 的寵物截圖（m02）那一段是用走路補的；為了不讓後面全部位移，沒有再加對話，所以只拍到寵物，台詞只靠資料檢查。
- Route 110 有 1 名訓練家在新路線上被繞過，只影響經驗值。

### 11.6 `to_winona`

接在 `to_norman` 後面。路線：
1. 出 Wally 家 → Route 103 的草叢抓一隻 Kyokon（Grinarbor 學不了 Surf），從背包教 HM03 → Oldale 回血 → 衝浪橫越 Route 103。
2. Route 110 → Mauville 回血 → 衝浪過 Route 118 的河 → Route 119。
   - (6,54)–(6,55) 是泥坡，要騎 Mach Bike 全速才上得去（跟 Mirage Tower 一樣逐格錄）。
   - 第一次走到 Weather Institute 門口時血量太低，身上也沒有藥，所以折回 Mauville 回血、在 Mart 買 15 個 Super Potion 再上來。這一段繞路約 3.3 萬格，留在腳本裡。
3. Weather Institute：手下 → 喝藥 → Shelly（截圖 w01）→ 研究員送 `WEATHER_GIFT`（Terubozu，截圖 w02）。
4. 往北到 (25,31) 的勁敵（截圖 w03），拿到 HM02 → Fortree 回血 → House1 的交換（截圖 w04：台詞同時顯示 Torobi 和 Tomoeden，選 NO）。
5. Route 120 橋上的 Steven（截圖 w05）→ `HIDDEN_BLOCKER` 的野生戰（Kyozosu Lv30，截圖 w06）→ Devon Scope → 回 Fortree 用 Devon Scope 趕走道館前的那隻（截圖 w07）。
6. Fortree 道館：旋轉門 → Jared、Ashley → 喝藥 → Flint 和 Edwardo 同一步看到玩家，變成雙打，贏了但 Grinarbor 倒下 → 出道館回血再進來（旋轉門會重置）→ Darius → 喝藥 → Winona（截圖 w08 戰鬥、w09 王牌 Kumoryu、w10 徽章）。Grinarbor Lv41 剩 33/124 HP 贏了。

這一段新增或修正的工具（測試都在 `tools/oddex/test_autopilot.py`）：
- stepwalk `--surf`：水可以走，瀑布不行；從陸地踏上水面時走 Surf 的提示（A、YES）。沒加 `--surf` 時，水現在會擋路（以前靜態 BFS 把水當成可走）。
- stepwalk 的旋轉門：在 Fortree 道館和 Trick House 謎題 6，BFS 的狀態包含每個門的方向，方向從 `VAR_TEMP_0` 起的位元組讀，規則照 `src/rotating_gate.c`（表格是抄過來的，那個檔案一改就要重抄）。物件用執行中的位置：訓練家打完會走到玩家旁邊，只看 `map.json` 會卡住。
- autopilot 的隊伍選單：隊伍超過一隻之後，打倒對手會問要不要換（選到 YES 就進隊伍選單），現在按 B 退出；有人倒下必須換上時，選等級最高、還有 HP、不在場上的那一隻。
- stage_reach `--surf`（§11.1）。

錄製時發現、已處理的問題：
- Weather Institute 的台詞寫死「received CASTFORM!」，`check_species_refs` 的文字檢查沒抓到。改成先 `bufferspeciesname` 再顯示「received {STR_VAR_1}!」；下一句「changes shape according to the weather」不符合單一型態的 Terubozu，改成「wishes for clear skies, whatever the weather conditions」。兩句合計的長度跟原本相同，ROM 的版面不變。
- 背包和隊伍選單會記住上次的位置：雙打換過人之後，「用在誰身上」的游標停在別隻身上，藥就用錯對象。喝藥的指令一律先按 LEFT 回到第一隻。

只靠資料檢查、沒在遊戲裡看過：
- Ichimai（Route 120 的 1% 欄位）：要遇到得在草叢耗很久，沒有排進路線。
- Route 119 的 Feebas 釣點（`FISHING_SPOT`）、Fortree 的交換本身（只拍了開出條件的台詞）。
- 橋上的影子圖（`OBJ_EVENT_GFX_KECLEON_BRIDGE_SHADOW`）有畫出來：截圖 w05 畫面最下緣、橋的陰影帶下面多出一小塊帶兩個尖角的凸起（Kyozosu 的耳朵，倒影是上下顛倒的）。物件本身被橋的地塊蓋住，只看得到水面的倒影，顏色跟陰影帶相同，所以只有凸出來的 4 列看得見；原版的 Kecleon 也是這樣。
- 沒經過的訓練家：Surf 補漏的游泳選手（Route 103 東側以外）、Abandoned Ship、Route 120 橋以南、道館的 Humberto；他們的隊伍只靠 `check_species_refs`。

## 12. 第 6 步第七段：Winona 之後 → Tate & Liza（第 7 個徽章）

`[mossdeep]` 已套用並設為 `strict = true`（接在 Mark 的 feat/mossdeep-batch 之後）；回歸腳本是 `to_mossdeep`（§12.4）。

### 12.1 可達性

- 用 `stage_reach.py --rock-smash --cut --strength --surf` 從 Fortree 跑，再依故事用地圖名單限制。
- 範圍內：Route 121–125、Safari Zone 西邊 4 區、Lilycove、Mt. Pyre、Magma Hideout、Aqua Hideout、Mossdeep（含道館和 Space Center）、Shoal Cave（退潮的 5 張地圖）。
- 人工判斷：
  - Magma Hideout：入口是腳本打開的（要 Mt. Pyre 的 Magma Emblem），BFS 走不到，所以整個 Hideout 和 Jagged Pass 的手下是人工加入的。Mark 草稿加這兩處是對的。
  - Space Center 的 Magma 襲擊：在拿到徽章之後，但緊接著發生、在同一個城市，所以放進來。
  - Route 125 和 Shoal Cave：從 Mossdeep 往北衝浪一小段就到，放進來。
  - Mossdeep 南邊和西邊的海（Route 126–134、Pacifidlog）：有 Surf 就到得了，但故事是拿到 Dive 之後才去，留給下一段，跟水下和 Sootopolis 一起做。
  - Safari Zone 的東北、東南兩區：破關後才開（`hall_of_fame.inc`），用 `exclude_maps` 排除。
  - Lilycove 的華麗大賽會場：屬於設施資料，排除。
- 以前漏掉、這一段補上的：
  - New Mauville：`[winona]` 把它當成「要 Basement Key」而排除，但玩家有 Surf 之後 Wattson 就會給鑰匙，所以那時就進得去。這是我之前判斷錯的。
  - Trick House 謎題 4（5 個徽章，應該在 `[winona]`）和謎題 5（6 個徽章）。謎題 5 沒有訓練家。
  - Route 116 的 Tunneler's Rest House。
- 新增 115 筆訓練家（含勁敵 6 種組合、Tate & Liza、Maxie 兩次、Tabitha 兩次、Matt）和 52 個野生表。

### 12.2 範圍內的原版角色，和 Mark 草稿的差別

`check_species_refs.py --scope mossdeep`：749 筆、102 種（wild 518、party 204、script 13、text 11、gfx 3）。Mark 的草稿是主路線 542 筆加 Route 125 的 27 筆；多出來的是 Safari Zone、Shoal Cave、New Mauville、Trick House 和 Space Center。

- 拿 Mark 分支的 `replacements.toml` 對照：party 和 wild 全部都有對照（Snorunt 在 ca2c25be 補上，對到 Yamambrr）。
- 依決策用 `exclude_refs` 排除：Groudon（Magma Hideout 4F 的過場、Space Center 和 Mt. Pyre 的文字）、Kyogre（Mt. Pyre 的文字）、Steven 家的 Beldum（破關後才送）。
- 手改的 script／text／gfx（共 27 筆，已完成；之後這三類是 0 筆）：
  - New Mauville 的假道具球：Voltorb → Suzurai（`setwildbattle` 和叫聲 6 筆）。
  - Aqua Hideout B1F 的假道具球：Electrode → Kagurai（4 筆）。
  - 寵物：Lilycove 百貨 1F 的 Azumarill → Magatide、Lilycove House1 的 Kecleon → Kyozosu、Mossdeep House4 的 Skitty → Mandalumb。
  - 文字：Team Aqua 在 Lilycove 海灣訓練的 Wailmer 和 Mossdeep 的「Wailmer watching」→ Kamorai（共 5 句）、Mt. Pyre 兩位訓練家提到的 Zigzagoon → Kyokon 和 Skitty → Mandalumb。
  - 在 `to_mossdeep` 裡看過的：Lilycove House1 的 Kyozosu（s01）、Aqua Hideout 的 Kagurai（s05）、Mossdeep House4 的 Mandalumb（s06）。沒看過的：Lilycove 百貨的 Magatide（勁敵站在門口）、New Mauville、Mt. Pyre 裡面和 Lilycove／Mossdeep 改過的那幾句對話。
- Tate & Liza 的隊伍照 Mark 在 balance.md 寫的改了（Iwadusk Lv42 帶 Moonblast、Iwadawn Lv44）。
- 沒處理：擋住 Route 124 的那幾格是 Lilycove tileset 裡畫成 Wailmer 的 metatile（`METATILE_Lilycove_Wailmer*`），文字已經改成 Kamorai，但圖還是 Wailmer。這是 tileset 美術，`check_species_refs` 看不到。

### 12.3 套用和重新同步

- `apply_replacements.py --scope mossdeep`：204 隻訓練家的角色、518 格野生資料；之後 `check_species_refs.py --scope mossdeep` 是 0 筆。
- `resync.py prepare`（舊 ROM = 5a7585ec，新 ROM = 套用後）第一次實際跑：`to_winona` 的 770 個 chunk 全部「no difference」（地圖、座標、是否可操作、等級、打倒的訓練家數都相同），所以腳本不用改，`run`／`shots`／`assemble` 還是沒有實際跑過。兩個 ROM 並排跑約 22 分鐘。
- 72 張截圖有 10 張差 15–78 個像素，逐張看過後更新基準：
  - 重畫的眼睛（Shojobob、Omotelle、Utomaw、Kyozosu）。
  - Haniwort 的圖鑑編號 269 → 271。
  - 6 隻訓練家角色的性別符號。原因：`GeneratePartySeed` 是 `Crc32B(struct Trainer) ^ OT id`，struct 裡有指標，ROM 版面一動，訓練家角色的 personality（性別）就會變。目前只影響畫面；哪天有 Attract、Rivalry、Cute Charm 介入就會影響戰鬥。

### 12.4 `to_mossdeep`

接在 `to_winona` 後面。路線：
1. 出 Fortree 道館（旋轉門）→ 回血 → Mart（5 個 Ultra Ball、20 個 Hyper Potion）→ Route 120 的橋和訓練家 → Route 121（Team Aqua 往 Mt. Pyre 的過場）→ Lilycove 回血 → House1 的寵物（截圖 s01）。
2. 回 Route 121 的碼頭，往南衝浪到 Route 122，抓一隻野生 Utoghast（會 Fly 也會 Surf；Ultra Ball 丟兩顆），從背包教 HM02。
3. Mt. Pyre：1F → 外側 → 山頂的 4 個手下 → Archie 帶走寶珠（截圖 s02）、拿到 Magma Emblem。
4. Fly 到 Lavaridge → 纜車 → Jagged Pass，Magma Emblem 打開 Hideout。
   - 1F 有 3 顆 Strength 巨石：在門口把 HM04 教給 Kyokon。回程從北邊再推一次（換地圖後巨石會復位）。
   - 手下、Tabitha → 4F 的 Maxie（截圖 s03）。打完 Grinarbor 剩 4 HP、招式 PP 幾乎用完，這一場很驚險。
5. 走出 Hideout → Fly 到 Slateport 回血 → Harbor 前 Capt. Stern 的訪問 → Archie 開走潛水艇（截圖 s04）。
6. Fly 到 Lilycove → 衝浪進 Aqua Hideout → B1F 的假道具球是野生 Kagurai（截圖 s05）→ B2F 的 Matt → 潛水艇離開。
7. 從入口的水池出來，往東衝浪過 Route 124 到 Mossdeep 回血 → House4 的寵物（截圖 s06）。
8. Mossdeep 道館：箭頭地板的規劃器踩開關讓雕像讓路 → Tate & Liza 的雙打（截圖 s07）→ Mind Badge（截圖 s08）。
   - 這一場只剩 Kyokon 站著：Grinarbor、Haniwort、Terubozu、Utoghast 都倒了。贏了，但等於是 Mark 擔心的「一打二」；要讓路線更穩，可以先練第二隻。

Fly 的地圖游標（每格一次方向鍵）：Mt. Pyre 山頂 → Lavaridge 是左 11、上 1；Jagged Pass → Slateport 是右 2、下 7；Slateport → Lilycove 是右 10、上 7。

這一段新增或修正的工具（測試在 `tools/oddex/test_autopilot.py`）：
- autopilot `AP_MIN_HP=N`：隊首在野外、可操作、HP 低於 N% 時停下來（印出到目前為止的指令和狀態，結束碼 0），呼叫的人喝藥後接著跑。
- stepwalk `--min-hp N`：同樣的停法。
- stepwalk 的箭頭地板（Mossdeep 道館，`src/rotating_tile_puzzle.c`）：BFS 的狀態包含每個物件的位置；踩到地板開關時，站在同色箭頭上的物件往箭頭方向移一格；道館內的傳送點會走。物件位置讀 save block 的 `objectEventTemplates`（離玩家太遠、沒有生成的雕像也算得到）。
- stepwalk：同一格連續兩步都沒走到（站著的 NPC、地圖資料看不出來的高低差）就當成擋住，重新規劃；以前會無限重試（David 遇到的 600 秒逾時是另一個原因，但症狀一樣）。
- stepwalk：走到一半才發現沒有路時，還是印出已經走的指令和狀態，結束碼 2；以前整段指令會丟掉。
- stepwalk：`warp_events` 座標超出地圖的 warp（Slateport 有一個）會讓靜態規劃當掉，現在略過。
- 靜態規劃看不到「已經隱藏」的物件：Route 120 橋上的 `HIDDEN_BLOCKER` 和 Steven、Route 121 的 Aqua 手下、Route 112 纜車前的 Magma 手下、Mt. Chimney 南邊、Aqua Hideout 門口的兩個手下，都要用 `--live` 走過去。Fortree 的樹屋和吊橋（高低差）靜態規劃也過不了，一樣用 `--live`。
- 錄製時踩到的坑：
  - Fly、教招式之後，START 選單的游標和背包的口袋會留在上次的位置；喝藥的按鍵巨集假設游標在 BAG、口袋在 ITEMS，所以每次 Fly 或教完招式都要把它們放回去。
  - 一串分段重跑時，中間有一段失敗而沒有停下來，後面的分段就接在舊的 savestate 上，組起來從開機跑會走偏。分段結束時除了位置，也要比 `gRngValue` 和 vblank 計數。
  - 分段的檔名一律用小寫，後面的系列加數字前綴（`a1`…`z8`、`2a1`…），不要只靠大小寫來區分：這台 Mac 的檔案系統不分大小寫，`A1.txt` 會直接蓋掉 `a1.txt`（`to_sootopolis` 有 31 段被蓋掉，靠原指令從倖存的 savestate 重新產生、再和下一個倖存的狀態比對簽章才救回來）。

## 13. 第 6 步第八段：Tate & Liza 之後 → Juan（第 8 個徽章）

`[sootopolis]` 已套用並設為 `strict = true`（§13.5）。§13.1–13.4 是套用前的草稿，數字是當時的。回歸腳本 `to_sootopolis` 還沒錄。

### 13.1 可達性和範圍邊界

- `stage_reach.py --rock-smash --cut --strength --surf` 跑三次：從 Mossdeep（海面）、Seafloor Cavern 裡面、Sootopolis 裡面。工具不會算 Dive，所以只有 Dive 才到得了的地方是人工加入的。
- 範圍內：
  - Route 126–131：主線會經過（Route 128 潛水到 Seafloor Cavern、Route 126 潛水到 Sootopolis、Route 129–131 往 Sky Pillar）。
  - Route 132–134 和 Pacifidlog：只要有 Surf 就到得了（`[mossdeep]` 留到這一段），海上的角色和 Route 126–131 是同一批，一起做比留一塊原版划算。
  - Seafloor Cavern、Sootopolis（含道館和 Juan）、Cave of Origin、Sky Pillar。
  - 水下地圖：Route 124、126、127、128、129、Seafloor Cavern 和 Sootopolis 的水下。只有 Route 124 和 126 的水下有野生表。
  - Abandoned Ship 隱藏樓層的野生表（要 Dive 才進得去；地圖本身早就在範圍裡）。
  - Route 126 小島上的 Brenda：要 Dive 才到得了，人工加入。
- 人工判斷：
  - Sky Pillar 的入口只存在於 Route 131 被劇情換掉的版面（`setmaplayoutindex LAYOUT_ROUTE131_SKY_PILLAR`，在 Cave of Origin 見過 Wallace 之後），BFS 看不到，人工加入。
  - 沒有 Waterfall：Wallace 在道館前給 HM07，但要 Rain Badge 才能用。Ever Grande、Victory Road、Meteor Falls 上層和其他瀑布留給下一段。
  - Cave of Origin 有 3 張 R/S 留下來、進不去的地圖，但有野生表。一起放進來，免得留下原版資料。
- 排除：
  - 破關後才有的：Marine Cave、Terra Cave 和它們的水下入口（Route 105、125 的水下）、Mystery Events House 的地下室。
  - **待決定**：Sealed Chamber（Route 134 潛水）和三個 Regi 洞窟。`src/braille_puzzles.c` 直接檢查隊伍裡有沒有 Wailord 和 Relicanth，三隻 Regi 是 `setwildbattle`。這是支線，草稿先不放。
- 80 名訓練家：Route 126–134 的 62 名、Seafloor Cavern 的 5 名手下加 Shelly 和 Archie、Sootopolis 道館 10 名、Juan。31 個野生表。

### 13.2 範圍內的原版角色

`check_species_refs.py --scope sootopolis`：677 筆、68 種（wild 439、party 139、text 65、script 23、gfx 11）。

- 54 種在 `replacements.toml` 已經有對照（海上最多的是 Zubat/Golbat 164、Wailmer 70、Tentacool 51、Magikarp 42、Wingull/Pelipper 47）。進化階段對不對得上要等 `apply_replacements` 檢查。
- **沒有對照的 11 種一般角色**：

| 原版 | 出現的地方 |
|---|---|
| Clamperl | Route 124、126 水下的野生（各 2 格）、道館的 Olivia |
| Relicanth | Route 124、126 水下的野生（各 2 格） |
| Corsola | Route 128 釣魚 1 格、Pacifidlog PC 的一句話 |
| Wailord | Route 129 水面 1 格 |
| Whiscash | Juan、Route 133 的 Mollie |
| Sealeo | Juan、Route 133 的 Franklin |
| Crawdaunt | Juan |
| Kingdra | Juan（王牌，Lv46） |
| Seadra | Route 133 的 Linda |
| Medicham | Route 132 的 Makayla |
| Bagon | Route 134 的 Aaron、Pacifidlog House3 的一句話 |

  - Juan 的 5 隻裡有 4 隻沒對照（Luvdisc 已對到 Shojomai）。
- **一般角色的 script／text／gfx（要手改，都有對照）**：
  - Pacifidlog House2 的兩隻 Azurill（造型、叫聲、文字）。
  - Sootopolis House1 的 Kecleon、House4 的 Azumarill（造型、叫聲、文字）；House6 提到 Wailmer 的一句話。
  - Sootopolis 的「Lotad and Seedot House」：比大小的活動，`setvar` 傳 `SPECIES_SEEDOT`／`SPECIES_LOTAD` 給 C，文字提到兩者共 28 處。照對照是 Bekurama 和 Shojobob；變數名和地圖名（LotadAndSeedotHouse）保留。

- **Pacifidlog 的交換**（已完成，跟 Rustboro、Fortree 一樣用代號）：照對照會變成「給 Magatide、換 Magatide」，所以另外定 `TRADE_PACIFIDLOG = MAGATIDE`（NPC 給的，暱稱 TAMA）和 `TRADE_PACIFIDLOG_WANT = KAMIKKO`（NPC 要的）。`src/data/trade.h` 改用代號，信件裡的 `EC_POKEMON(BAGON)`、`EC_POKEMON(HORSEA)` 換成一般單字（I WILL MAKE IT TOUGH PLEASE TRAIN IT WELL），House3 那句「wanted to get a BAGON」改成 KAMIKKO。`[rustboro]` 對 `trade.h` 的 Bagon、Horsea 例外已經拿掉。

### 13.3 Kyogre、Groudon、Rayquaza 在劇情裡的出場

三隻都沒有對照（依 2026-11-22 的決策，Kyogre 和 Groudon 跟這一段一起設計）。範圍內共 56 筆：

| 檔案 | 角色 | 方式 |
|---|---|---|
| `data/maps/SeafloorCavern_Room9/map.json` | Kyogre | 物件造型 `OBJ_EVENT_GFX_KYOGRE_FRONT`、`OBJ_EVENT_GFX_KYOGRE_ASLEEP` |
| `data/maps/SeafloorCavern_Room9/scripts.inc` | Kyogre（8）、Groudon（1） | 只有文字（Archie 的台詞）；過場用 `DoOrbEffect`、`ShakeCamera`，沒有叫聲 |
| `data/scripts/cave_of_origin.inc` | Kyogre、Groudon | `playmoncry SPECIES_KYOGRE`（R/S 留下的共用腳本，一行同時被算成兩種） |
| `data/maps/CaveOfOrigin_B1F/scripts.inc` | Rayquaza（5）、Kyogre、Groudon | 只有文字（Wallace） |
| `data/maps/SootopolisCity/map.json` | 三隻 | 物件造型 `OBJ_EVENT_GFX_GROUDON_SIDE`、`OBJ_EVENT_GFX_KYOGRE_SIDE`、`OBJ_EVENT_GFX_RAYQUAZA` |
| `data/maps/SootopolisCity/scripts.inc` | 三隻 | `playmoncry`：Kyogre 4、Groudon 2、Rayquaza 4；`special Script_DoRayquazaScene` 4 次；`setweather WEATHER_ABNORMAL`／`WEATHER_DOWNPOUR`；文字 14 處 |
| `data/maps/SkyPillar_Outside/scripts.inc` | Rayquaza | 文字 1 處；`setweather WEATHER_ABNORMAL` |
| `data/maps/SkyPillar_Top/map.json` | Rayquaza | 物件造型 `OBJ_EVENT_GFX_RAYQUAZA`、`OBJ_EVENT_GFX_RAYQUAZA_STILL` |
| `data/maps/SkyPillar_Top/scripts.inc` | Rayquaza | `playmoncry` 3、`setwildbattle SPECIES_RAYQUAZA`（事件結束後回到山頂可以打的那一場，`BattleSetup_StartLegendaryBattle`）、`setvar`、文字 1 處 |

範圍外、但同樣寫死這三隻的地方（`check_species_refs` 歸在 c／mechanics，或根本看不到）：

| 檔案 | 內容 |
|---|---|
| `src/rayquaza_scene.c` | Sootopolis 的過場動畫（三隻的大圖、`PlayCry_Normal(SPECIES_RAYQUAZA)`）；圖在 `graphics/rayquaza_scene/` 的 5 個資料夾 |
| `src/intro.c` | 開機動畫第 3 幕：Groudon 和 Kyogre 的叫聲和大圖 |
| `src/title_screen.c` | 標題畫面的 Rayquaza 圖 |
| `src/battle_setup.c:595`、`src/battle_bg.c:911`、`src/pokemon.c:5096`、`src/battle_transition.c` | 對戰這三隻時的專用轉場、背景和音樂 |
| `src/field_specials.c:3534`、`src/field_weather_effect.c` | 異常天氣（`WEATHER_ABNORMAL`）；破關後 Marine／Terra Cave 的位置 |
| `src/event_object_movement.c:521`、`src/field_effect.c:3440` | 物件的色盤和倒影；`FldEff_RayquazaSpotlight` |
| `src/follower_helper.c:389` | 跟隨者台詞的條件 |
| `data/maps/MarineCave_End`、`TerraCave_End` | 破關後的 `setwildbattle`（排除） |
| `[mossdeep]` 的 `exclude_refs` | Magma Hideout 4F 的 Groudon 造型和叫聲、Space Center 和 Mt. Pyre 的文字：這一段要一起收掉 |

要請使用者決定的是：這三隻要不要換、換成什麼；過場動畫（`rayquaza_scene.c`）、開機動畫和標題畫面是大圖，換掉的成本比一般角色高很多。

### 13.4 路線錄製的難度

接在 `to_mossdeep` 後面（它停在道館裡 Tate & Liza 面前，隊伍只剩 Kyokon 站著）。預估順序和每一段的難處：

1. Mossdeep 回血 → **Space Center**：手下 → 和 Steven 搭檔的雙打（`multi_2_vs_2`，要先在選單選 3 隻出場）。
   - 新東西：多人對戰的選隊伍畫面；autopilot 沒打過有搭檔的雙打。
   - Steven 的搭檔隊伍（Metang、Skarmory、Aggron）在 `src/data/battle_partners.party`。以前 `check_species_refs` 和 `apply_replacements` 都不看這個檔案，所以 `[mossdeep]` 是 strict 但這三隻還是原版。
     - 已修：兩個工具都會讀這個檔案（格式跟 `trainers.party` 一樣），scope 用 `partners = ["PARTNER_STEVEN"]` 明確列出。
     - `[mossdeep]` 加了 `partners`。Steven 的隊伍現在是 Kagurai（Metang 的對照）、Daibeki（Skarmory 的對照）、Enigmen（Aggron 的對照也是 Daibeki，為了不重複，這一格是手改的），`exclude_refs` 的兩行已經拿掉。
2. Steven 家拿 HM08。**隊伍裡沒有能學 Dive 的**（Kyokon、Utoghast 都不行）；海上的 Shojobob（Tentacool 的對照）同時能學 Surf、Dive、Waterfall，抓一隻可以取代 Kyokon 的 Surf。
3. Route 127 → 128 潛水 → **Seafloor Cavern**。這是最難的一段：
   - 潛水：stepwalk 沒有 Dive（深水上按 B 下潛、水下再按 B 上浮、`dive`／`emerge` 連接）。要加，規模跟 `--surf` 差不多。
   - 洞裡有 225 格水流（踩上去會被沖走）、31 顆 Strength 巨石、5 顆 Rock Smash 岩石。規劃器不會算水流和推石頭的結果，大概要逐間手解，或替水流加規劃。
   - 5 名手下、Shelly、Archie。
4. Kyogre 醒來之後，海上是 `WEATHER_ABNORMAL`（對戰時算下雨）：水系招式變強。autopilot 選招不看天氣，照樣能跑，只是受到的傷害會變多。
5. Route 126 潛水 → Sootopolis → Steven、Wallace → Cave of Origin（沒有戰鬥，可以用 `--live` 走）。
6. 出 Sootopolis，衝浪 Route 127 → 131（沿路的游泳訓練家很多，要喝藥）→ Route 131 換版面後的 **Sky Pillar**：
   - 2F 和 4F 有 72 格裂開的地板，要騎 Mach Bike 全速通過（跟 Mirage Tower 一樣逐格錄），掉下去會回到下一層。
7. 山頂的 Rayquaza 過場 → Fly 回 Sootopolis → 過場 → Wallace 給 HM07 → **道館**：
   - 3 區薄冰（同一張地圖，共 64 格），每格只能踩一次、全部踩過樓梯才出現；踩錯會掉到 B1F 跟訓練家打。規劃器不會，三區的走法要手寫。
   - Juan：5 隻水系，Lv41–46，對草系的 Grinarbor 有利，但要看 Mark 怎麼對照。

估計：
- 長度跟 `to_mossdeep` 差不多或更長（7000 行、每次約 25 分鐘）。`check-oddex-full` 會從約 30 分鐘變成約 50 分鐘以上。
- 要新增的工具：stepwalk 的 Dive（一定要）；水流的規劃（看 Seafloor Cavern 手解的結果決定）；選隊伍畫面的按鍵。
- 最大的風險是隊伍：`to_mossdeep` 的兩場頭目戰都只是驚險過關，這一段開頭就是連續戰鬥（Space Center），中途又沒有地方回血（Seafloor Cavern）。建議這一段一開始先練第二隻。

### 13.5 套用和接線（接在 Mark 的 Sootopolis 批次之後）

- 使用者的決定（2026-11-23）：新做 Onamazu、Magaryu、Yukinba；傳說三隻是 Sokonemu（海，代號 `LEGEND_SEA`）、Okafumi（陸，`LEGEND_LAND`）、Utsuroban（空，`LEGEND_SKY`）；Regi 和 Sealed Chamber 延到破關後。
- `apply_replacements.py --scope sootopolis`：139 隻訓練家的角色、439 格野生資料。
- 一般角色的手改：
  - Pacifidlog House2 的兩隻 Azurill → Shojobob；Sootopolis House1 的 Kecleon → Kyozosu、House4 的 Azumarill → Magatide（造型、叫聲、文字）。
  - 文字：Pacifidlog PC 的 Corsola → Haniwort、Sootopolis House6 的 Wailmer Doll → Kamorai Doll。
  - 比大小的兄弟：C（`src/pokemon_size_record.c`）和腳本都改用代號 `SIZE_RECORD_1`（Bekurama，原本的 Seedot）和 `SIZE_RECORD_2`（Shojobob，原本的 Lotad）；文字 28 處。`[sootopolis]` 的 `c_files` 加了這個檔案。
- 傳說三隻的接線（腳本、文字、地圖物件都用代號）：
  - `playmoncry`、`setwildbattle`、`setvar`：Sootopolis、Sky Pillar 山頂、`cave_of_origin.inc`。
  - 地圖物件：`OBJ_EVENT_GFX_KYOGRE_*`、`GROUDON_*`、`RAYQUAZA*` → `OBJ_EVENT_GFX_SPECIES(ODDEX_LEGEND_*)`（Seafloor Cavern Room9、Magma Hideout 4F、Sootopolis、Sky Pillar 山頂）。原版是 64×64 的專用圖，有「睡著」和「靜止」兩種造型；現在都是一般的角色小圖。
  - Sootopolis 裡 Kyogre 的移動用了 `init_affine_anim`／`walk_left_affine`，要靠它自己的 affine 表；一般角色小圖沒有這張表，所以改成 `walk_fast_left`（跟 Groudon 的 `walk_fast_right` 對稱）。
  - 文字：8 個腳本檔裡的名字都換了（含 `[mossdeep]` 之前排除的 Magma Hideout 4F、Space Center、Mt. Pyre）。名字變長，9 行重新換行。
  - `[mossdeep]` 的 `exclude_refs` 只剩 Steven 家的 Beldum。
- 過場動畫（決定於 2026-11-23：不重畫，改成在地圖上演）：Sootopolis 腳本原本呼叫 4 次 `Script_DoRayquazaScene`，會播 Kyogre、Groudon、Rayquaza 的大圖，現在都拿掉了。
  - 兩隻對打的那一段（從 PC 和從潛水上來各一次）：天氣變成 `WEATHER_ABNORMAL`、打雷，接著就是原本就有的地圖上對打（叫聲、鏡頭晃動）。
  - 第三隻出現的那一段（各一次）：新的子腳本 `SootopolisCity_EventScript_SkyLegendArrives`。`LEGEND_SKY` 出現在兩隻中間，打雷、叫聲、鏡頭晃動；兩隻各退兩步，畫面暗下去，原地留下洶湧的水面（`SetRoughWater`），再亮起來。之後接原本的腳本（叫聲、放晴、飛走）。
  - 從 PC 那個版本原本把 Rayquaza 的物件藏起來（`hideobjectat`），現在看得到。
  - `src/rayquaza_scene.c` 和那個 special 還在，只是沒有腳本呼叫。
- 山頂那一場野生戰（`BattleSetup_StartLegendaryBattle`）：角色不是原版的 Rayquaza，所以走 `default`，用一般的傳說轉場和音樂（`B_TRANSITION_BLUR`、`MUS_RG_VS_LEGEND`），不會出現原版的轉場圖。
- **還是原版、這個範圍管不到的**：
  - **待處理：intro、title**。開機動畫（`src/intro.c`）和標題畫面（`src/title_screen.c`）還是原版三隻。拿掉開機動畫會改變開機的影格數，所有回歸腳本開頭的按鍵時序都可能位移；標題畫面要等 Mark 的 128×128 圖。David 會另外排成一個獨立的 commit。
  - 對戰背景和音樂對原版三隻的特例（`battle_bg.c`、`pokemon.c`）：新角色不會觸發，沒有壞處，只是少了專用背景。
- Juan 的招式：套用後 20 招裡有 7 招是新角色學不到的，照 Mark 在 balance.md 定的換掉，現在 20 招都學得到：Shojomai 是 Water Pulse／Attract／Teeter Dance／Draining Kiss，Yukinba 是 Icy Wind／Body Slam／Aurora Beam／Water Pulse，Jatai 是 Water Pulse／Poison Jab／Crunch／Haze；Onamazu 和 Magaryu 不變。
- 重新同步：`resync.py prepare`（舊 ROM = a3bfcfb2，新 ROM = 這一段全部套用後）對 `to_mossdeep` 的 950 個 chunk 全部「no difference」，腳本不用改（`run`／`shots`／`assemble` 還是沒有實際用到）。80 張截圖有 9 張不同，逐張看過後更新基準：8 張是訓練家角色的性別符號（原因見 §12.3），1 張是 Haniwort 的圖鑑編號 271 → 274。
- 沒有在遊戲裡看過：這一段還沒有路線。試過用除錯選單直接傳送去看，沒成功（選單按法跟 `to_dolls` 的不一樣），留給 `to_sootopolis`。

### 13.6 `to_sootopolis`

接在 `to_mossdeep` 後面（`include` 鏈有 9 層，超過 runner 原本的上限 8，所以上限改成 16）。路線：
1. 出 Mossdeep 道館 → 回血 → Mart（15 個 Hyper Potion、20 個 Max Repel）→ 往北衝浪到 Route 125，打 7 個訓練家 → Fly 回 Mossdeep → Route 127 的 8 個訓練家。
   - 目的是練主力，但經驗值會依等級差縮減：對手 Lv30 上下時，15 個訓練家只讓 Grinarbor 從 Lv47 升到 Lv49。
2. Space Center：1F 的手下和樓梯口的守衛 → 2F 三個手下連戰 → 喝藥 → Steven 的雙打（截圖 t01）。
3. Steven 家拿 HM08 → Mossdeep 南邊的水面抓一隻 Shojobob，教 Dive（蓋掉 Absorb）。
4. Route 127 → Route 126 潛水（規劃器第一次潛水，順便遇到野生 Magatide）→ Route 128 潛水，從水裡的門浮上來進 Seafloor Cavern。
   - Room1、Room2、Room8：巨石規劃器（敲岩石、推巨石）。Room6：水流把人帶到 Room3 的門。
   - Room3：從下面跟手下講話，Shelly 才不會加入變成雙打；喝藥後單獨打 Shelly（截圖 t02）。
   - Room9：Archie（截圖 t03）→ 紅色寶珠喚醒 `LEGEND_SEA`（截圖 t04）→ 被帶到 Route 128，天氣異常。
5. Fly 到 Mossdeep 回血、再買 15 個 Hyper Potion → Route 126 潛水到火山口底下，浮上來進 Sootopolis：兩隻在水面上對打。跟著 Steven 到 Cave of Origin，告訴 Wallace `LEGEND_SKY` 在 Sky Pillar（選單要按下兩次）。
6. Fly 到 Mossdeep → Routes 127、128、129、130、131。Route 131 一進地圖就換成 `LAYOUT_ROUTE131_SKY_PILLAR`，北邊的水道只有這個版面才通，要用 `--live`。
7. Sky Pillar：洞口是 `MB_SOUTH_ARROW_WARP`（站上去按下）→ Wallace 開門 → 爬塔。
   - 第一次爬（`VAR_SKY_PILLAR_STATE < 2`）用的是 `*_CLEAN` 版面，沒有裂地板，不需要 Mach Bike。
   - 但 4F 還是分成兩半：從 3F 右邊的樓梯上去，走到 (5,4) 往右踩上 (6,4) 的裂地板（clean 版面也留著這幾格），掉到 3F 中間的小房間，那裡的樓梯才通到 4F 有 5F 樓梯的那一半。
   - 山頂 (14,9) 的觸發點：`LEGEND_SKY` 醒來、飛走（截圖 t05）。山頂的地圖類型是 `MAP_TYPE_ROUTE`，可以直接 Fly。
8. Fly 到 Sootopolis：`LEGEND_SKY` 出現、兩隻退場、放晴（截圖 t06）→ 跟 Maxie、Archie 講話（兩個都講過才會離開）→ Wallace 給 HM07 → 回血。
9. 道館：三段薄冰每一格只能踩一次（踩 7、19、38 格後樓梯才出現），照解出來的走法逐個轉角走，不會掉到 B1F，一個訓練家都不用打。Juan（截圖 t07）→ Rain Badge（截圖 t08）。

頭目戰結束時的 HP（David 的標準：主力 ≥ 1/3、我方沒有人倒下）：

| 對戰 | 上場 | 結束時 | 標準 |
| --- | --- | --- | --- |
| Steven 雙打（Maxie、Tabitha） | Grinarbor Lv49、Haniwort、Terubozu | Grinarbor 0/149（倒下）、Haniwort 41/88、Terubozu 71/71 | 不套用 |
| Shelly | Grinarbor | 70/149 | — |
| Archie | Grinarbor Lv51 | 76/152，沒有人倒下 | 符合 |
| Juan | Grinarbor Lv51 | 89/152，沒有人倒下 | 符合 |

- Steven 雙打不套用這條標準（David，2026-11-24）：回歸路線幾乎只用一隻在打，跟一般玩家的平衡不同；三隻上場、確定能贏就好。只派主力上場會輸（主力倒下就算輸）。
- Juan：戰鬥中主力低於 60% 時喝一瓶 Hyper Potion（只喝了一瓶）。不喝的話贏是贏，但結束時只剩 24/152。Wood Hammer 的反作用力佔了損血的大半。David 接受這個做法（2026-11-24）：標準的目的是留餘裕，玩家本來就會喝藥，所以不用另外練一隻 Magaryu。
- 沒有練第二隻：隊伍是滿的（主力、Haniwort、Terubozu，加上 Strength／Surf、Fly、Dive 三隻 HM 載具）。

Fly 的地圖游標：Route 125 → Mossdeep 是下 1；Route 127 → Mossdeep 是上 1、右 1；Route 128 → Mossdeep 是上 4；Sootopolis → Mossdeep 是右 3、上 2；Sky Pillar 山頂 → Sootopolis 是上、右、上、右、上。

在遊戲裡第一次看到的地圖場景（截圖在 `~/oddex-shots/sonia/sootopolis/`）：
- Seafloor Cavern 的甦醒、Sootopolis 的對打、Sky Pillar 山頂、Sootopolis 的到場，都能播完，沒有當機。角色是 32×32 的一般小圖，暴雨裡偏小偏暗，但看得出是誰。
- 山頂的「翻身」原本靠 Rayquaza 專用的動畫格，現在變成左右轉頭再飛走，可以接受。
- 修了一個問題：`SkyLegendArrives` 的淡出淡入原本用 `fadescreenspeed`，在暴雨下會把已經被天氣調暗的調色盤再調暗一次，之後大約 10 秒幾乎全黑。改用 `fadescreenswapbuffers`（原版在天氣下就是用它；指令一樣是 3 個位元組，ROM 版面不動）。

這一段新增的工具（測試在 `tools/oddex/test_autopilot.py`）：
- stepwalk `--dive`：水面上深水格的 DIVE、水底的 EMERGE，目的地讀 dive／emerge connection 和 `setdivewarp`；包含 `Underwater` 的地圖。
- stepwalk 的巨石規劃器：BFS 的狀態包含巨石和可敲岩石的位置，`PUSH_<方向>`／`SMASH_<方向>`；第一次推會回答 Strength 的詢問。
- stepwalk 的水流：踩上水流格只會被帶走（`carried`），一路到停下來的地方。
- autopilot：雙打隊友戰（`multi_2_vs_2`）的隊伍選單位置是自己的隊首 0、隊友 1、自己的後備 2、3。

錄製時踩到的坑：
- 長錄製放在 `~/oddex-recording/`，不要放 session 的暫存目錄（session 重啟會被清掉，這一段因此重錄過一次）。
- Repel 還有效時不能再用；失效時會問要不要再用一個，這時 Surf 的 A 會選到 YES。喝藥、用 Repel 的巨集都要驗證效果（HP 有沒有增加、計數是不是 250）。
- 巡邏的訓練家追不到：站在它的原位那一排（左右走的）或那一列等它看到。
- Route 128 → 129 要從 x=33–43 過去（x=46–54 是死水）；Route 131 的靜態版面南北不通。
- 靜止時按住新的方向會先花 8 影格轉身，`hold RIGHT 32` 只會走一格多；要走到定點用 stepwalk。
- 戰鬥中喝藥：行動選單 RIGHT、A（背包）、A、A（USE）、A（隊首）。

