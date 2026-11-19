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
| **地區圖鑑**(玩家看到的編號) | `FOREACH_SPECIES_IN_HOENN_DEX_ORDER`(`include/constants/pokedex.h`)不受開關影響,永遠列出 Treecko~Deoxys;`HOENN_DEX_COUNT` 寫死成 `HOENN_DEX_DEOXYS + 1`。我們的角色不在表裡,能力畫面顯示 **No000**(實驗截圖 `06_summary_info`) | **已處理(第 1 步)**:見 §1.5 |
| **叫聲** | `include/constants/cries.h` 每一個 `CRY_*` 都包在 `#if P_FAMILY_X` 裡,全部關掉後只剩 `CRY_NONE` | 使用者決定先無聲(`CRY_NONE`),見第 5 節 |
| **全國圖鑑數量** | `NATIONAL_DEX_COUNT` 的 `#if` 鏈還會看 cross-evo、regional form 等開關;只關 `P_GEN_x` 時會變成 `NATIONAL_DEX_HYDRAPPLE` | 產生器在 `oddex:dex-count` 區段覆寫成我們最後一隻。建議同時把 `P_CROSS_GENERATION_EVOS`、`P_REGIONAL_FORMS`、`P_MEGA_EVOLUTIONS`、`P_GIGANTAMAX_FORMS`、`P_TERA_FORMS`、`P_FUSION_FORMS`、`P_PIKACHU_EXTRA_FORMS` 也關掉,讓設定一致 |
| **sprite 檢視器** | 從 #0001 開始,一打開就 assert(`09_visualizer_normal`) | **已處理(第 1 步)**:見 §1.5 |
| 存檔 | 圖鑑旗標的大小跟著 `NATIONAL_DEX_COUNT` 變 | 開發期間每次改動都要開新遊戲,不需要處理相容性 |
| 原版內容引用 | 訓練家、野生、腳本、文字、地圖物件等 | 見 Sonia 的 §1–§3 |

### 1.5 第 1 步:地區圖鑑與 sprite 檢視器(已完成)
- `include/constants/pokedex.h`:原版列表改名為 `VANILLA_HOENN_DEX_ORDER`。`FOREACH_SPECIES_IN_HOENN_DEX_ORDER` 改成**第 3 世代開著時用原版列表再接上原創角色;關掉時只有原創角色**。原創角色的順序由 `content/regional_dex.toml` 決定,產生器寫進 `oddex:regional-dex` 區段(同時定義 `HOENN_DEX_LAST`),`HOENN_DEX_COUNT` 改成 `HOENN_DEX_LAST + 1`。每隻原創角色都必須在順序表裡出現恰好一次,否則產生器會報錯。
- `src/pokemon_sprite_visualizer.c`:改成從第一個啟用的 species 開始(原版開著時仍然是 Bulbasaur,畫面不變)。
- `src/pokedex.c` `HasAllHoennMons()`:原本用**全國圖鑑編號**當索引去查 `gSpeciesInfo`,原版的編號剛好等於 species ID,所以沒出問題;原創角色(全國 1026、species 1573)就會查錯角色,誤判是否為幻之寶可夢。改成先轉成 species 再查。
- 驗證(截圖在 `~/oddex-shots/mark/step1/`):
  - 原版開著、御三家改成原創 Mossprit:能力畫面顯示 **No215**(接在原版的 214 隻後面)。
  - 全部世代關掉、早期代號都指向 Mossprit:顯示 **No001**;sprite 檢視器直接從 #1573 開始;整個 `to_starter` 沒有任何 crash screen。
  - 正式設定(原版開著、代號指向原版):`make check-oddex` 的 16 張截圖和基準 0 差異。
- 副作用(原版開著時):地區圖鑑多了原創角色,所以「抓滿地區圖鑑」需要多抓這幾隻,`RANDOM_MON_DEX_HOENN` 的隨機池也會包含它們。第 5 步關掉原版之後,這就是我們要的行為。

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

## 4. 第二階段順序

已和 Sonia 合併,以 `docs/research/plan-b-references.md` §5 為準。

## 5. 使用者決策(已決定,`docs/DECISIONS.md`)
1. **美術**:先全部用程式產生的佔位圖,之後再統一設計所有角色。
2. **叫聲**:關掉原版後先無聲(`CRY_NONE`),不合成。注意:這只是指原創角色本身。腳本裡對**原版**角色的 `playmoncry` 仍然會觸發 `disabled species` 的 assert,要在第 6 步依路線改掉(Sonia §5)。
3. **資料格式**:TOML。

### 5.1 佔位圖產生器的要求(第 3 步)
依美術決策,`scripts/species/gen_mossprit.py` 要擴充成通用的佔位圖產生器:
- **一眼就能分辨**:主色和副色依屬性決定(例如草 = 綠、火 = 橘、水 = 藍);輪廓用幾種體型模板(圓球、直立、四足、有翼、蛇形),由角色資料指定;身上加一個屬性記號(葉子、火焰、水滴…);進化階段越後面體型越大、細節越多,同一條進化線共用同一套配色。
- **之後換正式美術只換圖檔**:佔位圖的參數放在 TOML 的選填區段 `[graphics.placeholder]`,產生器只讀這一段,輸出到 `[graphics] dir` 指定的資料夾。換成正式美術時,把同一個資料夾裡的圖檔換掉,再刪掉 `[graphics.placeholder]` 就好,其他欄位結構都不用動;只有圖像相關的數值(大小、Y 位移、影子)可能需要依新圖調整。
- **圖檔匯入要能吃外部 PNG**(David 的建議,見 `docs/research/art-assets.md`):`[graphics] dir` 裡放的圖不一定是我們產生的,所以驗證流程要能接受一般 PNG(例如 CC0 的 64×64 素材),自動量化成透明色加 15 色、寫出 `normal.pal`,icon 對應到最接近的共用 icon 調色盤,並檢查尺寸和 Y 位移。這樣之後無論換成哪種正式美術,都走同一條匯入流程。
- 工期:通用產生器大約一次工作階段;之後每隻角色是填一份 TOML(數值、招式、佔位圖參數),再用 sprite 檢視器檢查。

### 5.2 給 `apply_replacements.py` 用的載入函式
`tools/oddex/species_data.py`:`load_species()`、`load_roles()`、`oddex_stages()`(原創角色的進化階段,由 TOML 的 `evolutions` 計算)、`vanilla_stages()`(原版的,解析 `gen_*_families.h` 的 `.evolutions`;1,571 種,Wurmple 1 → Silcoon/Cascoon 2 → Beautifly/Dustox 3 這類分歧也算得正確)。Mega 等型態不是進化,一律算第 1 階段;替換表本來就不會用它們當 key。`gen_species.py` 也改用這個模組。

### 5.3 第 3 步:早期 12 隻佔位角色(已完成)

| # | id | 屬性 | 體型 | 對應的早期位置 |
|---|---|---|---|---|
| 1573 | MOSSPRIT | 草/岩 | 圓球(手繪原型) | 御三家・草 |
| 1574 | ACORNIK | 草/鋼 | 圓球 + 角 | Seedot |
| 1575 | CHIRPIP | 電/飛行 | 鳥 | Taillow(Route 102 訓練家) |
| 1576 | DOZELET | 超能力/龍 | 雙足 | Ralts |
| 1577 | EMBERKIT | 火/格鬥 | 雙足 + 耳 + 尾 | 御三家・火 |
| 1578 | FUNGLOO | 草/冰 | 圓球 + 刺 | Shroomish(Route 102 訓練家) |
| 1579 | GULLWISP | 飛行/幽靈 | 鳥 + 冠羽 | Wingull |
| 1580 | PADLILY | 水/妖精 | 圓球 + 葉 | Lotad |
| 1581 | PUDDLEFIN | 水/電 | 四足 + 鰭 | 御三家・水 |
| 1582 | SCRUFFLE | 一般 | 四足 + 尾 | Zigzagoon |
| 1583 | SHADEPUP | 惡 | 四足 + 耳 + 尾 | Poochyena |
| 1584 | SPROUTWORM | 蟲/草 | 蟲 + 觸角 + 葉 | Wurmple |

依照「屬性不同、又怪」的設計方向,刻意用了少見的屬性組合。數值、招式、圖鑑文字都是暫定的(早期角色的種族值總和約 200~310,和原版同位置的角色相近)。名字都和原版 1,500 多隻比對過,沒有重複(Glimmet 是第 9 世代真實存在的寶可夢,所以改名)。目前都還沒有進化,進化線等統一設計時再補。

新增或調整的工具:
- `tools/oddex/placeholder_art.py`:通用佔位圖產生器(§5.1 的要求):5 種體型、配件、依屬性配色、頭上的屬性記號,還有異色版、icon(自動挑最接近的共用 icon 調色盤)、overworld 6 幀、足跡。不認得的屬性(將來的原創屬性)會用名稱雜湊出一個穩定的顏色,所以不會壞。`--preview` 可以輸出總覽圖。
- `tools/oddex/import_art.py`:外部 PNG 匯入(RGBA、全彩、索引色都可以),詳見檔頭說明。用兩種合成素材測過:1,413 色的半透明漸層圖,以及 96×96、洋紅色背景的圖。兩者都通過驗證。
- `gen_species.py` 的圖檔驗證:用標準函式庫寫的 `png_reader.py`(66 個檔案和 PIL 的結果逐像素一致)檢查尺寸、色數、調色盤。`front_size`/`back_size`/Y 位移和 `icon_palette` 改成**選填**:沒寫的話,由圖的實際邊界和 icon 的調色盤自動算出,所以換正式美術時不用手改數值(Mossprit 的值是手寫的,也會被檢查)。
- **species ID 只往後追加**:ID 會存進存檔。原本是依檔名排序,新增一隻 Acornik 就把 Mossprit 從 #1573 擠到 #1579;現在沿用 `species.h` 裡既有的順序,新角色接在最後面。刪除角色會印出警告,因為後面的 ID 會跟著移動。
- `tools/headless/scripts/oddex_gallery.txt`(由產生器產生):接在 `to_starter` 後面,在 sprite 檢視器裡逐隻截圖(普通色 + 異色,共 24 張),已加入 `make check-oddex` 的預設清單,基準截圖放在 `tools/headless/baselines/oddex_gallery/`。檢視器只能逐位調整編號,所以用 BFS 找出只經過原創角色編號的路徑,第 5 步關掉原版之後也不會經過已停用的物種。注意:離開檢視器會一路退回開始選單,要重新進入隊伍 → 能力畫面 → SELECT。

已知的限制:共用 icon 調色盤只有 6 組,顏色和本體差很多的角色,icon 會偏灰(硬體限制;要改善得新增 icon 調色盤)。佔位圖都偏小,等正式美術。

### 5.4 研究筆記:新增原創屬性的可行性(還沒實作)
使用者之後想把朋友設計成「屬性不同、又怪」的寶可夢,可能會需要原創屬性。在 expansion 1.17.2 裡,一個屬性由這些部分組成:
- `include/constants/pokemon.h` 的 `enum Type`:目前 `TYPE_NONE`(0) ~ `TYPE_STELLAR`(20),`NUMBER_OF_MON_TYPES` = 21。新屬性要加在 `TYPE_STELLAR` 之前或之後都可以,但 **`teraType` 只有 5 bits**(`include/pokemon.h:135`,註解寫 30 types),所以最多到 31,也就是還能加約 10 個。`TYPE_MYSTERY`(10,也就是「???」)目前也有程式在用(`src/*.c` 54 處),不建議挪用。
- `src/data/types_info.h`:`gTypeEffectivenessTable[21][21]` 相剋表(要加一列加一欄);`gTypesInfo[]`:名稱、`generic` 文字、icon 調色盤編號、Z 招式/極巨招式、太晶顏色、傷害分類(舊世代物理/特殊)、TM 圖示調色盤、是否算覺醒力量屬性(改了會影響所有覺醒力量的分布)。檔案裡的註解也列出要配套的道具(屬性強化道具、半減果、寶石、石板…),可以先不做。
- 圖示:`graphics/types/<name>.png`(32×16、4bpp),`graphics_file_rules.mk` 的 `types :=` 清單,`src/type_icons.c` 的動畫表;戰鬥中的小圖示在 `graphics/types/battle_icons*.png`。
- 我們這邊的工具:`gen_species.py` 只檢查 `TYPE_<名稱>` 有沒有定義,`placeholder_art.py` 不認得的屬性會用雜湊配色,所以**資料格式和工具都不用改**,只要先在遊戲裡定義好屬性就能直接用。
- 估計工作量:加一個屬性(定義、相剋表、TypeInfo、圖示)大約一次工作階段,不含平衡設計。建議等角色設計確定、真的需要時再做,而且一次決定好所有新屬性,相剋表只改一次。

## 6. 建置防線:`make check-oddex`
因為「編譯不會壞、release 默默變成 `SPECIES_NONE`」,能抓到漏網之魚的只有內容檢查和 debug build 的 assert。這兩者都排進建置流程,不靠人記得去跑:

```bash
cd game && . ../tools/env.sh
make check-oddex TOOLCHAIN=$TOOLCHAIN -j$(sysctl -n hw.ncpu)        # 先建好 ROM,再跑下面三項
make check-oddex ODDEX_STRICT_MAPS=LittlerootTown,Route101 ...        # 指定的路線不准有原版引用
```

`tools/oddex/check_oddex.sh` 依序執行,任何一項失敗就 exit 1:
1. `gen_species.py --check`:產生的檔案是最新的。
2. `check_species_refs.py`:預設只回報數量;設定 `ODDEX_STRICT_MAPS` 後,改成 `--strict --maps`,指定路線有原版引用就失敗。第 4b 步完成後,把早期路線寫進 `oddex.mk` 的預設值,之後每遷移一段就加上去。
3. 用 headless runner 跑回歸腳本(預設 `to_littleroot to_starter`,第 2c 步之後加上 `to_petalburg`),**只要出現 crash screen 就失敗**。做法:`src/assertf.c` 的 `CrashScreen` 在 debug build 會多送一行 `ODDEX_CRASH_SCREEN assert: <檔案:行號: 訊息>` 到 mGBA 的除錯 log(release build 不會編進去),runner 本來就會把 ERROR 等級的 log 印到 stderr,腳本只要 grep 就能抓到。已驗證:把第 3 世代關掉,runner 印出 `ODDEX_CRASH_SCREEN assert: src/pokemon.c:6389: disabled species: 270`(開場的 Lotad)。
   - 選用:`ODDEX_SHOTS_BASELINE=<dir>` 會把 `<dir>/<腳本名>/*.png` 和這次的截圖逐像素比對。

輸出在 `game/build/oddex-check/<腳本名>/`(含 `err.log`)。目前 develop 加上這次的修改:三項全部通過(引用檢查是回報模式),乾淨的 ROM 建置加檢查約 40 秒。
