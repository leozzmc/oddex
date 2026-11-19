# 方案 B:關掉原版世代 + 原創角色產生器(Mark)

基準:develop f5a957b3。決策見 `docs/DECISIONS.md`(關掉原版各世代 species,原創角色全部新增在 custom 區段)。
這份文件是 Sonia 的 `docs/research/plan-b-references.md` §4(她負責 §1–§3:引用盤點和改寫策略)。
**本分支目前提交的是產生器和一隻原型角色;關掉原版世代只做了實驗,沒有提交。**

## 1. 實驗:關掉原版世代會怎樣

做法:把 `include/config/species_enabled.h` 的 `P_GEN_1_POKEMON` ~ `P_GEN_9_POKEMON` 全部設成 `FALSE`,編譯並實際玩一遍(之後還原)。

### 1.1 編譯:不會壞
- 只出現一個 `SwapFusionMonMoves defined but not used` 警告,沒有錯誤。原因:所有 species 資料都包在 `#if P_FAMILY_X` 裡,而 `SPECIES_X` 常數本身(enum)永遠存在,所以 trainers.party、wild_encounters.json、腳本、C 對原版的引用全部照樣能編譯。
- 換句話說,**編譯器不會告訴我們哪裡還在用原版角色**,要靠 Sonia 的 `tools/oddex/check_species_refs.py --strict` 和執行期的 assert。
- ROM 大小(都是乾淨建置):原版 26,743,268 B → 全部關掉加上原型 11,647,032 B,**少了約 15.1 MB(−56%)**。

### 1.2 執行期:debug build 會停在 assert
- 判斷是否啟用的是 `IsSpeciesEnabled()`(`src/pokemon.c`):`baseHP > 0`(或 `SPECIES_EGG`)。全部關掉之後只剩 `SPECIES_NONE` 和 `SPECIES_EGG`;我們新增的角色只要 `baseHP > 0` 就自動算啟用。
- 用到被關掉的 species 時,`SanitizeSpeciesId()` 會觸發 `assertf("disabled species: %d")`:
  - **debug build(我們目前的建置)**:顯示藍色的 assert 畫面(檔名:行號 + species 編號),按 START 可以繼續。實驗中第一個被擋下的是開場 Birch 展示的 Lotad(`SPECIES 270`)。
  - **release build**:默默換成 `SPECIES_NONE`(顯示成問號或空白)。
  - 所以 debug build 的 assert 可以當作「漏網之魚偵測器」,跟無頭截圖搭配使用。

### 1.3 只改劇情位置,就能用原創角色走完開頭
在全部關掉的狀態下,只把這幾處 C 改成角色代號 `SPECIES_ODDEX_STARTER_GRASS`(實驗中全部指向 Mossprit):
- `src/main_menu.c` 開場展示(Lotad,2 處)
- `src/battle_controllers.c:163` 救 Birch 時的野生寶可夢(Zigzagoon)
- `src/starter_choose.c:113–115` 御三家

`to_starter.txt` 就能從開機一路走到最後:開場展示、選御三家、對戰 Lv2 的野生 Mossprit、研究所、隊伍、能力畫面都正常,過程中沒有任何 assert。
截圖:`~/oddex-shots/mark/plan-b/`(`00_intro_mon` ~ `08_summary_moves`)。

### 1.4 關掉之後一定要另外處理的東西

| 問題 | 原因 | 處理方式 |
|---|---|---|
| **地區圖鑑**(玩家看到的編號) | `FOREACH_SPECIES_IN_HOENN_DEX_ORDER`(`include/constants/pokedex.h`)不受開關影響,永遠列出 Treecko~Deoxys;`HOENN_DEX_COUNT` 寫死成 `HOENN_DEX_DEOXYS + 1`。我們的角色不在表裡,能力畫面顯示 **No000**(實驗截圖 `06_summary_info`) | 由產生器輸出我們的地區圖鑑順序,取代 Hoenn 列表(第二階段第 1 步) |
| **叫聲** | `include/constants/cries.h` 每一個 `CRY_*` 都包在 `#if P_FAMILY_X` 裡,全部關掉後只剩 `CRY_NONE` | 原型先用 `CRY_NONE`(沒有聲音)。之後需要原創叫聲(**需要使用者決定**,見第 5 節) |
| **全國圖鑑數量** | `NATIONAL_DEX_COUNT` 的 `#if` 鏈還會看 cross-evo、regional form 等開關;只關 `P_GEN_x` 時會變成 `NATIONAL_DEX_HYDRAPPLE` | 產生器在 `oddex:dex-count` 區段覆寫成我們最後一隻。建議同時把 `P_CROSS_GENERATION_EVOS`、`P_REGIONAL_FORMS`、`P_MEGA_EVOLUTIONS`、`P_GIGANTAMAX_FORMS`、`P_TERA_FORMS`、`P_FUSION_FORMS`、`P_PIKACHU_EXTRA_FORMS` 也關掉,讓設定一致 |
| **sprite 檢視器** | 從 #0001 開始,一打開就 assert(`09_visualizer_normal`) | 讓它從第一個啟用的 species 開始(小改 `src/pokemon_sprite_visualizer.c`) |
| 存檔 | 圖鑑旗標的大小跟著 `NATIONAL_DEX_COUNT` 變 | 開發期間每次改動都要開新遊戲,不需要處理相容性 |
| 原版內容引用 | 訓練家、野生、腳本、文字、地圖物件等 | 見 Sonia 的 §1–§3 |

## 2. 三種格式(和 Sonia 對齊用的草稿)

### 2.1 (a) 角色資料:`content/species/<id>.toml`,一隻一個檔案

範例見 `content/species/mossprit.toml`。欄位:

| 欄位 | 說明 | 產生到 |
|---|---|---|
| `id` | `UPPER_SNAKE_CASE`,決定 `SPECIES_<id>`、`NATIONAL_DEX_<id>`、`gMonFrontPic_<Id>` 等名稱。不能和原版重複 | species.h、pokedex.h |
| `name`、`category` | 遊戲內名稱和分類,各最多 12 字 | species_info |
| `types`、`abilities`(slot1/slot2/隱藏)、`base_stats`、`ev_yield`、`catch_rate`、`exp_yield`、`gender`(女性百分比或 `"GENDERLESS"`)、`egg_cycles`、`egg_groups`、`growth_rate`、`body_color`、`cry` | 戰鬥與基本資料;常數名稱不寫前綴(`GRASS` → `TYPE_GRASS`) | species_info |
| `[dex]` `height`(dm)、`weight`(hg)、`text`(最多 4 行 × 42 字)、`scale` | 圖鑑 | species_info |
| `[learnset]` `level`(`[等級, 招式]`)、`teachable`、`egg` | 招式。`teachable` 會寫進 `all_learnables.json`,建置時只保留遊戲裡真的學得到的 TM/教學招式 | oddex_data.h、all_learnables.json |
| `evolutions` | `[{ method = "LEVEL", param = 16, into = "<id>" }]` | species_info |
| `[graphics]` | 圖像資料夾(相對於 `game/`)、icon 調色盤、正背面圖大小和 Y 位移、動畫、影子、overworld 設定 | oddex_data.h、species_info |
| `[design]` | **產生器不讀**,給地圖和事件用的設計資訊:`habitat`(棲息地/路線)、`level_band`(等級帶)、`family`(進化線)。Sonia 需要的欄位直接加在這裡 | — |

為什麼用 TOML 而不是 YAML:Python 3.11+ 內建 `tomllib`,建置流程不需要安裝任何第三方套件(上游的 learnset 產生器也只用標準函式庫);PyYAML 在這台機器上沒有安裝。結構和 YAML 一一對應,如果要換回 YAML,只要改 `load_species()` 一個函式。**請 David 確認。**

產生器會先驗證再輸出:所有常數(type、ability、move、egg group、growth、color、cry、evo method、animation、jump、shadow)都必須真的存在於 `game/include`;名稱和圖鑑文字的長度;`baseHP > 0`;圖檔是否齊全;id 不能跟原版重複。任何一項不通過都會列出全部錯誤後失敗。

### 2.2 (b) 原版 → 原創替換表:`content/replacements.toml`(提案,尚未實作)

```toml
# key = 原版 species(每個進化階段各一行),value = 原創 species id
[replace]
TREECKO   = "MOSSPRIT"
GROVYLE   = "MOSSPRIT_2"       # 第 2 階段
SCEPTILE  = "MOSSPRIT_3"
WURMPLE   = "XXX"              # 分歧進化:Silcoon/Cascoon 可以對到同一條線的不同角色
SILCOON   = "XXX_A"
CASCOON   = "XXX_B"
```

規則(和 Sonia 的提案一致):
- **key 直接用原版的每一隻**,所以進化階段天然包含在 key 裡。產生器會從原版的 `.evolutions` 算出 key 的階段,從 TOML 的 `evolutions` 算出 value 的階段,兩邊不一致就報錯(可以用 `stage_mismatch_ok = ["X"]` 個別放行)。
- `trainers.party`/`wild_encounters.json` 裡出現、但替換表沒有的原版角色 → **直接失敗並列出全部**;`--fallback <id>` 可以先填佔位角色。
- 我傾向「一次性改寫原始檔」:工具把 `trainers.party`、`wild_encounters.json` 裡的原版名稱就地換成原創名稱(trainerproc 會把 `Mossprit` 轉成 `SPECIES_MOSSPRIT`),之後的平衡調整直接改這兩個檔案,再由 Sonia 的 `check_species_refs.py --strict` 擋住殘留的原版引用。另一種做法是保留原版原始檔、在建置時才轉換,但這樣日後手動調整隊伍會很彆扭。這兩個檔案歸 Sonia,**由她決定**。

### 2.3 (c) 角色代號:`content/roles.toml` → `include/constants/oddex_species.h`

```toml
STARTER_GRASS = "MOSSPRIT"     # -> #define SPECIES_ODDEX_STARTER_GRASS SPECIES_MOSSPRIT
```

- `oddex_species.h` 在 `include/constants/species.h` 的最後被 include,所以凡是看得到 `SPECIES_*` 的地方都看得到代號。
- **四條路都已經實際驗證**(實驗後還原):
  - C:`starter_choose.c` 用 `SPECIES_ODDEX_STARTER_GRASS` → 選御三家拿到的是 #1573。
  - trainers.party:寫 `Oddex Starter Grass` → trainerproc 輸出 `.species = SPECIES_ODDEX_STARTER_GRASS`,在 `data.c` 編譯成功。
  - wild_encounters.json:`"species": "SPECIES_ODDEX_STARTER_GRASS"` → `wild_encounters.h` 原樣輸出;讀 ROM 的 `gRoute101_LandMons` 第一格,species = **1573**。
  - 腳本:`bufferspeciesname STR_VAR_1, SPECIES_ODDEX_STARTER_GRASS` → 組譯和連結都通過(`data/event_scripts.s` 會 include `constants/species.h`)。
- 代號可以指向原創角色,也可以指向原版角色(遷移期間方便逐步替換)。

## 3. 產生器:`tools/oddex/gen_species.py`

```bash
python3 tools/oddex/gen_species.py            # 產生/更新
python3 tools/oddex/gen_species.py --check    # 產生檔不是最新的就 exit 1(給 CI)
```

| 輸出 | 內容 |
|---|---|
| `game/include/constants/species.h` 的 `oddex:species-ids` 區段 | `SPECIES_<id>,`,位於 `SPECIES_CUSTOM_START` 和 `SPECIES_CUSTOM_END` 之間(Mossprit = 1573) |
| `game/include/constants/pokedex.h` 的 `oddex:dex-ids`、`oddex:dex-count` 區段 | `NATIONAL_DEX_<id>,`,以及覆寫 `NATIONAL_DEX_COUNT` |
| `game/include/constants/oddex_species.h` | 角色代號 |
| `game/src/data/pokemon/oddex_data.h` | 升級招式、蛋招式、`INCGFX` 圖像宣告、overworld pic table |
| `game/src/data/pokemon/species_info/oddex_families.h` | `gSpeciesInfo` 的條目(檔名以 `_families.h` 結尾,上游的 teachable 產生器才會掃到) |
| `game/src/data/pokemon/all_learnables.json` | 只更新我們自己的 key;格式和原檔逐位元組一致(indent 2、結尾不換行) |

接到上游的地方(都只有一兩行):`species.h`、`pokedex.h` 的標記區段、`species_info.h` 一行 include、`src/pokemon.c` 一行 include、`Makefile` 一行 `include oddex.mk`。

建置整合:`game/oddex.mk`。內容或產生器有變動時,`make` 會自動重跑產生器。產生的檔案**有提交進 git**(方便 review 和 grep,Sonia 的檢查工具也看得到),而 `--check` 可以確認它們不是過期的。

圖像:`scripts/species/gen_mossprit.py <dir>` 可以輸出到任何資料夾;原型角色放在 `game/graphics/pokemon/oddex/mossprit/`。

### 3.1 原型目前的狀態
- 提交的版本**仍然啟用原版世代**,所以 Treecko slot(#252)的 Mossprit 和 custom slot(#1573)的 Mossprit 同時存在;代號 `SPECIES_ODDEX_STARTER_GRASS` 已經定義,但遊戲裡還沒有用到。現有的遊玩內容完全不受影響:`to_starter.txt` 的 10 張截圖和 develop 逐像素一致。
- #1573 已經用 sprite 檢視器確認過(`~/oddex-shots/mark/plan-b/custom_1573_visualizer*.png`):正面、背面、異色、icon、足跡都正常。
- ROM 增加 3,776 B。

### 3.2 踩到的坑
1. **組合語言那條路不能在 enum 裡 `#include`**:`tools/preproc -e` 會自己解析 `species.h` 的 enum,遇到 enum 中間的 `#include` 就報「unterminated enum」。所以 enum 項目改成由產生器寫進標記區段,而不是 include 一個檔案。
2. **`ANIM_FRAMES` 最後一個 frame 也要加逗號**:巨集是 `{ __VA_ARGS__ ANIMCMD_END }`。
3. **macOS 的 GNU Make 是 3.81,沒有 grouped targets(`&:`)**,所以用 stamp 檔代表多個輸出。
4. **不能讓 `all_learnables.json` 依賴 stamp**:它已經有一條 recipe(`make_learnables.py`,會從 porymoves 整份重建,把我們的 key 洗掉)。改成讓它的使用者(`teachable_learnsets.h`、`all_teaching_types.json`)依賴 stamp。
5. **沒有 arm-none-eabi-cpp 時,`trainers.h` 會無聲變成空的**:管線的結束碼只看 trainerproc。David 已經在 develop 修好(拆成兩步)。教訓:**ROM 大小不合理時先 `make clean`**。我一開始拿這個殘缺版本的大小當基準,算出的差異多了 65 KB。

## 4. 建議的第二階段順序(Mark 的部分,要和 Sonia 的 §3.5 合併)

1. **地區圖鑑產生**:產生器輸出我們的地區圖鑑順序和 `HOENN_DEX_COUNT`,取代 Hoenn 列表;順便修好 sprite 檢視器的起始編號。這是關掉原版之前的前置作業。
2. **代號接上劇情位置**:§1.3 的 5 處 C,加上 Route 103 勁敵的 6 組隊伍(Sonia),改成用 `SPECIES_ODDEX_*`。這時代號先指向原版角色,遊戲內容不變。
3. **早期約 10 隻原創角色**(御三家 3 隻 + 早期野生 6–7 種,見 Sonia §2)的資料和圖像,寫成 `content/species/*.toml`。
4. **替換表工具**(§2.2)+ 套用早期角色;改代號指向原創角色。
5. **關掉原版世代**(連同 §1.4 建議的 forms/cross-evo 開關);用 `to_littleroot`、`to_starter` 和新的到 Petalburg 的腳本截圖驗證,搭配 debug assert 和 `check_species_refs.py --strict`。
6. 往後依路線擴充;設施類最後。

## 5. 需要使用者決定的事
1. **原創角色的美術**:目前的 Mossprit 是程式產生的佔位圖。早期約 10 隻要用什麼方式製作?(繼續程式產生佔位圖、手繪像素圖、或外包/委託)這會決定第 3 步的工期。
2. **叫聲**:關掉原版後,所有原版叫聲都會消失。選項:暫時無聲(`CRY_NONE`)、用程式合成原創叫聲、或另外製作音效。
3. **資料格式用 TOML**(David 確認即可)。
