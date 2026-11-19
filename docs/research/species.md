# Species 資料、圖像與替換流程研究

> 對象：pokeemerald-expansion `expansion/1.17.2`(本 repo `game/`)
> 作者：Mark(`feat/species`)
> MVP 成果：Treecko slot 原地替換成原創佔位角色 **Mossprit**(草/岩,「Moss Pebble」)

---

## 1. 一個 species 由哪些東西組成

以 `SPECIES_TREECKO` 為例,資料分散在這些地方(路徑相對於 `game/`):

| 項目 | 檔案 | 說明 |
|---|---|---|
| Species ID | `include/constants/species.h` | `enum`,`SPECIES_TREECKO = 252`。**ID 會存進存檔**,不要重新編號 |
| 啟用開關 | `include/config/species_enabled.h` | `P_FAMILY_TREECKO`(預設跟著 `P_GEN_3_POKEMON`)。所有相關資料都包在 `#if P_FAMILY_TREECKO` 裡 |
| 主要資料 `SpeciesInfo` | `src/data/pokemon/species_info/gen_3_families.h` | 種族值、屬性、特性、名字、分類、圖鑑文字、身高體重、圖像指標、動畫、learnset 指標、進化…… 幾乎全部集中在這裡 |
| 圖像 `INCGFX` 宣告 | `src/data/graphics/pokemon.h` | 把 `graphics/pokemon/treecko/*.png/.pal` 綁成 `gMonFrontPic_Treecko` 等符號 |
| 圖像原始檔 | `graphics/pokemon/treecko/` | 見第 2 節 |
| 升級招式 | `src/data/pokemon/level_up_learnsets/gen_N.h` | **只有 `P_LVL_UP_LEARNSETS` 選中的那個檔案有效**(預設 `GEN_LATEST` → `gen_9.h`)。每個 gen 檔都有一份 `sTreeckoLevelUpLearnset` |
| 招式機/教學招式 | `src/data/pokemon/all_learnables.json`(來源) → `teachable_learnsets.h`(產生,gitignored) | 編譯時由 `tools/learnset_helpers/make_teachables.py` 與遊戲中實際存在的 TM/教學交叉比對產生 |
| 蛋招式 | `src/data/pokemon/egg_moves.h` | `sTreeckoEggMoveLearnset` |
| 進化 | `SpeciesInfo.evolutions` | `EVOLUTION({EVO_LEVEL, 16, SPECIES_GROVYLE})` |
| 叫聲 | `include/constants/cries.h`、`sound/cry_tables.inc`、`sound/direct_sound_data.inc`、`sound/direct_sound_samples/cries/` | `SpeciesInfo.cryId` 指向 `CRY_TREECKO` |
| 全國圖鑑號 | `include/constants/pokedex.h` | `NATIONAL_DEX_TREECKO`;豐緣圖鑑順序在 `src/data/pokemon/pokedex_orders.h` |
| 型態表 | `src/data/pokemon/form_species_tables.h`、`form_change_tables.h` | Treecko 家族因為 Mega Sceptile 而有 |

### 會顯示角色名字、但不在 species 資料裡的地方
`speciesName` 改掉後,下列地方**仍然寫死原名**,需要另外處理(大多屬於事件/地圖線):

- `data/maps/PetalburgCity_PokemonCenter_1F/scripts.inc:73`:「For example, your TREECKO…」+ 說它是 GRASS 屬性 → **已由 Sonia 在 `feat/events` 修正**(改用 `bufferspeciesname` 讀取資料)
- 裝飾品 `DECOR_TREECKO_DOLL` → **已改成 MOSSPRIT DOLL**:
  - 名稱/說明:`src/data/decoration/header.h`(`name` 是 `u8[16]`,最多 15 字);遊戲角選單:`src/data/script_menu.h`(`MultichoiceList_GameCornerDolls`,視窗寬度會依最長字串自動計算)。地圖腳本用 `bufferdecorationname`,不用改
  - 圖像:`graphics/object_events/pics/dolls/treecko_doll.png`,16×16 4bpp。**沒有自己的調色盤**,用共用的 `OBJ_EVENT_PAL_TAG_NPC_3`(`graphics/object_events/palettes/npc_3.pal`,見 `object_event_graphics_info.h` 的 `gObjectEventGraphicsInfo_TreeckoDoll`),所以只能用那 16 色(沒有黃色)。秘密基地的放置也透過 `DecorGfx_TREECKO_DOLL` 引用同一張圖
  - 產生:`python3 ../scripts/species/gen_mossprit.py graphics/pokemon/treecko graphics/object_events/pics/dolls/treecko_doll.png`。16×16 用程序化繪製會太擠,所以玩偶是腳本裡手動排的對稱像素圖(`DOLL_LEFT`)
- **尚未處理**:秘密基地裝飾品 `DECOR_GREEN_POSTER` 的說明「A small poster with a TREECKO print.」(`src/data/decoration/header.h`)。海報圖案在秘密基地 tileset 裡,要連圖案一起換
- `src/data/trainers.party`:隊伍用的是 species 識別名(`Treecko` → `SPECIES_TREECKO`),**名稱改了也不用改這裡**;trainer 常數名稱如 `TRAINER_MAY_ROUTE_103_TREECKO` 只是識別字
- 單元測試(見第 6 節)

---

## 2. 圖像格式限制

`graphics/pokemon/<species>/` 底下的檔案:

| 檔案 | 尺寸 | 格式 | 用途 / 注意事項 |
|---|---|---|---|
| `anim_front.png` | 64×128 | 4bpp 索引色、16 色 | 兩個 64×64 幀**垂直堆疊**(幀 0 在上)。`frontAnimFrames` 用 `ANIMCMD_FRAME(n, 時長)` 指定幀 |
| `back.png` | 64×64 | 4bpp、16 色 | 單幀 |
| `normal.pal` / `shiny.pal` | 16 色 | JASC-PAL 文字檔 | **調色盤以 `.pal` 為準**,不是 PNG 內嵌的調色盤。front/back 共用同一組;shiny 只換顏色,**索引必須對應同一位置** |
| `icon.png` | 32×64 | 4bpp | 兩個 32×32 幀垂直堆疊。**不使用自己的調色盤**,而是共用 `graphics/pokemon/icon_palettes/pal0..pal5.pal` 其中之一,由 `iconPalIndex` 指定。像素索引必須照那份共用調色盤畫 |
| `footprint.png` | 16×16 | 1bpp | 黑白兩色 |
| `overworld.png` | 192×32 | 4bpp | 6 個 32×32 幀**水平排列**:0 面向下、1 下走、2 面向上、3 上走、4 面向左、5 左走;向右 = 4/5 水平翻轉(`sAnimTable_Following`)。`OW_POKEMON_OBJECT_EVENTS` 預設 TRUE,所以會被編進去 |
| `overworld_normal.pal` / `overworld_shiny.pal` | 16 色 | JASC-PAL | `OW_PKMN_OBJECTS_SHARE_PALETTES == FALSE`(預設)時使用 |
| `*_gba.png` / `*_gba.pal` | 同上 | 同上 | 只有 `P_GBA_STYLE_SPECIES_GFX` / `P_GBA_STYLE_SPECIES_ICONS` 設為 TRUE 才用到(預設 FALSE) |

共通規則:
- **調色盤索引 0 = 透明**。它的 RGB 值不會顯示,但一定要佔用一格。
- PNG 必須是 palette(索引)模式或灰階;gbagfx 接受 1/2/4/8 bit,超過 16 色會壞。建議直接存成 4-bit。
- 轉檔鏈:`png → .4bpp`(gbagfx)→ `.4bpp.smol`(compresSmol,front/back/overworld)。`.pal → .gbapal`(gbagfx,32 bytes)。產物在 `build/assets/graphics/pokemon/<species>/`。
- `SpeciesInfo` 的位置參數:
  - `frontPicSize` / `backPicSize = MON_COORDS_SIZE(w, h)`:可見範圍的寬高,以 8 為單位無條件進位
  - `frontPicYOffset` / `backPicYOffset`:**圖底部有幾列透明**(= 64 − 最後一列不透明像素 − 1)。設錯會讓角色浮空或陷進地面
  - `SHADOW(x, y, size)`:敵方影子位置
  - `pokemonScale/pokemonOffset/trainerScale/trainerOffset`:圖鑑「大小比較」畫面用
- 調整位置可以用遊戲內的 sprite debug 選單:在能力畫面(非戰鬥中)按 `Select`。

---

## 3. MVP:原地替換 Treecko → Mossprit(可重現步驟)

```bash
cd game
# 1) 產生原創圖像(覆蓋 treecko 資料夾內所有 png/pal,含 _gba 版本)
python3 ../scripts/species/gen_mossprit.py graphics/pokemon/treecko

# 2) 驗證圖像能被工具鏈轉換
export DEVELOPER_DIR=/Library/Developer/CommandLineTools
make tools
tools/gbagfx/gbagfx graphics/pokemon/treecko/anim_front.png /tmp/f.4bpp   # 應為 4096 bytes
tools/gbagfx/gbagfx graphics/pokemon/treecko/normal.pal /tmp/n.gbapal     # 應為 32 bytes
```

`scripts/species/gen_mossprit.py`(在 repo 根目錄,不在 `game/` 內)用 PIL 程序化繪製,沒有使用任何現有素材:
- 正面兩幀(第二幀壓扁,配合 `ANIM_V_SQUISH_AND_BOUNCE`)、背面、icon 兩幀、overworld 6 幀、足跡
- 普通色:灰石 + 綠苔 + 黃花;shiny:砂岩 + 青苔 + 粉花(同樣索引)
- icon 會把自己的索引重新對應到共用的 `icon_palettes/pal1.pal`(`iconPalIndex = 1`)

程式碼修改:

| 檔案 | 修改 |
|---|---|
| `src/data/pokemon/species_info/gen_3_families.h`(`[SPECIES_TREECKO]`) | 名字 `Mossprit`、分類 `Moss Pebble`、草/岩、種族值 50/45/65/35/60/55(總和 310,與原本相同)、特性 Overgrow / Sturdy(隱藏)、蛋群 Grass/Mineral、性別比 50%、努力值 Def+1、身高 0.4m、體重 18.0kg、新的圖鑑文字、`frontPicSize`/`backPicSize`/影子/跳躍類型配合新圖 |
| `src/data/pokemon/level_up_learnsets/gen_9.h`(`sTreeckoLevelUpLearnset`) | 草+岩招式:Tackle、Growl、Leafage、Rock Throw、Mega Drain、Defense Curl、Rollout、Rock Tomb、Giga Drain、Ancient Power、Ingrain、Energy Ball、Stealth Rock、Synthesis、Leaf Storm |

刻意**沒改**的(MVP 範圍外,之後換整個家族時一起處理):
- `cryId` 仍是 `CRY_TREECKO`(原創叫聲需要音訊素材,見第 4 節)
- 進化仍是 Lv16 → Grovyle;蛋招式、TM 相容性(`all_learnables.json`)維持原樣
- 圖鑑號 `NATIONAL_DEX_TREECKO` 不變
- 第 1 節列出的寫死文字(之後已處理:Petalburg 對話由 Sonia 修正,玩偶在後續 commit 改成 MOSSPRIT DOLL;GREEN POSTER 延到第二階段)

### 驗證
**模擬器畫面驗證(回歸腳本)**:`tools/headless/scripts/to_starter.txt` 從開機一路玩到選御三家、第一場戰鬥、Birch 研究所、隊伍、能力畫面和 sprite 檢視器,共 10 張截圖,約 58,500 幀,執行時間約 10 秒。runner 已固定 RTC,同一個 ROM 連跑兩次的截圖逐像素一致:

```bash
. tools/env.sh
mkdir -p ~/oddex-shots/mark && cd ~/oddex-shots/mark
$ODDEX_RUN <worktree>/game/pokeemerald.gba <worktree>/tools/headless/scripts/to_starter.txt   # → shots/01..10
```

結果:選擇畫面顯示「Moss Pebble POKéMON / Mossprit」;確認畫面的圖置中、沒有裁切;背面圖的位置和原版 Torchic 一致(腳都剛好碰到文字框上緣);能力畫面的屬性、特性、招式、能力值正確;隊伍 icon 正常。**當對手時的正面圖**是用 sprite 檢視器驗證的:它用戰鬥中的實際位置畫出正面(敵方)和背面圖,Mossprit 站在平台上的位置和旁邊原版的 0253 Grovyle 一致。不需要調整任何偏移量。

寫腳本時學到的:
- 文字速度無法透過 OPTION 預先調快,因為 NEW GAME 會呼叫 `SetDefaultOptions()` 重設選項。
- 對話盡量用 **B** 推進:A 在對話結束後會再跟面前的 NPC 說話,遇到 YES/NO 時還會選 YES(例如取暱稱)。需要回答 YES 的地方(時鐘、Birch 的「去見我的孩子?」)要算好次數再按 A。B 在 YES/NO 時等於選 NO,可能造成對話循環。
- 要先等提示框真的出現再按方向鍵,否則方向鍵會被前一個畫面吃掉(設時鐘時就轉動了指針)。
- **不要讓輸入依賴亂數**。RTC 固定前,同一個 ROM 每次跑的亂數都不同;固定後雖然可以重現,但只要 ROM 一改,亂數的消耗量就會不同。第一場戰鬥的回合數會隨性格、個體值和會心一擊改變(用 Leafage 需要 1~3 回合),所以腳本改成 4 輪「Battle → Leafage」,每輪後面接 250 次 B。B 在戰鬥選單上沒有作用,戰後只會推進文字,遇到「取暱稱?」會選 NO,最後一定會停在「去見我的孩子?→ NO → 別這樣嘛」的穩定循環,再改按 A 選 YES。250 次是必要的:文字印出途中按 B 不會加速,從戰鬥結束到取暱稱提示就要大約 120 次。驗證方式:在戰鬥前插入 0~987 幀的等待打亂亂數,16 種狀態全部成功走到最後。
- 刻意避開需要穿過草叢的路線(例如去 Route 103 跟 May 對戰),因為隨機遭遇會讓腳本一改 ROM 就失準。檢查敵方正面圖用 sprite 檢視器比較穩定:能力畫面按 SELECT,物種編號逐位調整(LEFT/RIGHT 換位數、UP/DOWN 改數字),START 切換異色。
- 檢視器下方顯示的 BACK/FRONT 動畫名稱會晚一步更新(顯示的是前一個物種的),不要當真。

**ROM 編譯前的靜態驗證**(工具鏈還沒裝好時的做法,保留作參考):
1. `make -k` 建出所有 host 端資產,新圖成功產生 `.4bpp.smol` / `.gbapal`,compresSmol 壓縮/解壓縮來回一致。
2. 用與 Makefile 相同的管線 `cpp → tools/preproc/preproc → clang -fsyntax-only` 檢查 `src/pokemon.c`(它 include 了 species_info、learnsets 和圖像宣告):0 錯誤。指令:
   ```bash
   SDK=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk
   clang -E --target=armv4t-none-eabi -ffreestanding -idirafter $SDK/usr/include -iquote include \
     -DMODERN=1 -DTESTING=0 -DEMERALD -std=gnu17 src/pokemon.c \
     | tools/preproc/preproc -i -g build/assets src/pokemon.c charmap.txt > /tmp/pokemon.pp.c
   clang --target=armv4t-none-eabi -ffreestanding -fsyntax-only -idirafter $SDK/usr/include -std=gnu17 -w -x c /tmp/pokemon.pp.c
   ```
   (前提:先跑過 `make -k` 讓 `build/assets` 存在,否則 preproc 會因找不到 `.smol` 失敗。)

---

## 4. 如何「新增」一個 species slot

上游教學:`game/docs/tutorials/how_to_new_pokemon.md`。**注意教學範例用的是舊的 `#define SPECIES_X N` 寫法,1.17.2 已改成 `enum`**:

1. `include/constants/species.h`:在 `SPECIES_CUSTOM_START` 和 `SPECIES_CUSTOM_END` 之間加 `SPECIES_MOSSPRIT,`(目前 `SPECIES_CUSTOM_START = SPECIES_GLIMMORA_MEGA = 1572`)。**加在最後**,不要插在中間,否則存檔中的 ID 會錯位。
2. `src/data/pokemon/species_info/` 新增一筆 `[SPECIES_MOSSPRIT] = { ... }`(可以另開一個檔案,例如 `oddex_families.h`,並在 `src/data/pokemon/species_info.h` 裡仿照 `#include "species_info/gen_3_families.h"` 加入)。沒填的欄位預設回落到 `SPECIES_NONE`,不會當機但會顯示 `?`。
3. 圖像:建 `graphics/pokemon/mossprit/`,在 `src/data/graphics/pokemon.h` 加 `INCGFX_*` 宣告;前面圖的動畫要在 `species_info` 填 `frontAnimFrames`。
4. 招式:在目前生效的 `level_up_learnsets/gen_9.h` 加 learnset;在 `all_learnables.json` 加 `"MOSSPRIT": [...]`,teachable 會自動產生;蛋招式在 `egg_moves.h`。
5. 叫聲(可選):wav(單聲道 13379Hz `pcm_u8`)放進 `sound/direct_sound_samples/cries/`,在 `direct_sound_data.inc` 加 `Cry_Mossprit`,`cries.h` 的 enum 加 `CRY_MOSSPRIT`,`sound/cry_tables.inc` 的 `cry` 與 `cry_reverse` **兩個表都要加,而且順序要跟 enum 一致**。
6. 圖鑑:`include/constants/pokedex.h` 的 `NationalDexOrder` 加 `NATIONAL_DEX_MOSSPRIT` 並更新對應 `P_GEN_x_POKEMON` 分支的 `NATIONAL_DEX_COUNT`;要進豐緣圖鑑還要改同檔案的 `FOREACH_SPECIES_IN_HOENN_DEX_ORDER` 巨集與 `src/data/pokemon/pokedex_orders.h`。
7. 出現:`src/data/wild_encounters.json`、`trainers.party` 或事件腳本裡的 `givemon`。

---

## 5. 大量替換(換掉全部角色)的方向

兩條路,各有取捨,**需要 David/使用者決定**:

**A. 原地替換既有 slot(本 MVP 的做法)**
- 優點:所有引用(劇情腳本、trainer、野生遇敵、遊戲角、bard 音樂、easy chat……)自動跟著換,不會有懸空引用;不需要動 enum、圖鑑號。
- 缺點:原始碼識別字仍叫 `SPECIES_TREECKO`、`gMonFrontPic_Treecko`,長期閱讀很混亂;家族結構(幾段進化、Mega/型態)被原本的 slot 綁住。
- 緩解:可以在 `species.h` 加別名(`#define SPECIES_MOSSPRIT SPECIES_TREECKO`)讓新程式碼用新名字。

**B. 關閉原版、全部新增在 custom 區段**
- 用 `species_enabled.h` 把 `P_GEN_1_POKEMON` ~ `P_GEN_9_POKEMON` 設成 FALSE,原版資料全部不會編進去,在 `SPECIES_CUSTOM_START` 之後新增自己的角色。
- 優點:乾淨、ROM 空間省很多(原版有 1500+ 個 species 的圖)。
- 缺點:原版所有引用 species 的地方(trainers.party 上百隊、wild_encounters.json、地圖腳本、裝飾品、遊戲角、bard、frontier 等)都要一起改,工作量大,且需要和 Sonia 的地圖/事件線緊密協調。

**建議**:不管選哪條,都做成「單一來源 + 產生器」:每個原創角色一個 YAML/JSON(數值、文字、招式、圖像路徑),用 Python 腳本產生 `species_info` 片段、learnset、`all_learnables.json` 條目、圖像宣告。這樣就能大量替換而且可重現。`gen_mossprit.py` 的圖像部分可以直接當作產生器的一部分。

---

## 6. 踩到的坑

1. **develop 匯入時漏檔**:`game/.gitignore` 有 `tools/compresSmol/`,上游是用強制追蹤加入的,所以普通 `git add` 會跳過 → `make tools` 在 compresSmol 失敗。David 已在 `782c1ad2` 修好。之後從上游同步檔案時要注意 `.gitignore` 會擋掉已被追蹤的檔案。
2. **`.pal` 才是調色盤的來源**:PNG 內嵌的調色盤不會被用到,只有像素索引會用到。改顏色要改 `.pal`;畫圖時索引要和 `.pal` 對齊。
3. **icon 不能有自己的顏色**:只能從 6 組共用 icon 調色盤挑一組,畫的時候要照那組索引。
4. **YOffset = 底部透明列數**:第一版的腳在 y=58,但 `frontPicYOffset = 8`,會差 3px;背面的花碰到 y=0 頂端。調整繪製參數後才修正。
5. **Learnset 有 9 份**:每個 gen 檔都有 `sTreeckoLevelUpLearnset`,只有 `P_LVL_UP_LEARNSETS` 選中的那份(預設 gen_9)會生效。改錯檔案不會有任何錯誤訊息。
6. **`teachable_learnsets.h` 是產生的而且被 gitignore**:要改 TM 相容性請改 `all_learnables.json`(或 `special_movesets.json`)。
7. **上游測試寫死了 Treecko 的名字/屬性**,`make check` 會失敗:
   - `test/battle/spread_moves.c:417, 435`:斷言「not very effective on … Treecko」—— 名字不同,而且 Precipice Blades(地面)對草/岩是 1 倍,不再是效果不好
   - `test/battle/move_effect/instruct.c:407`:「Treecko transformed into the Water type!」
   - `test/battle/ability/intimidate.c:244`、`test/battle/ability/forewarn.c:80`:「2 sent out Treecko!」
   - 換掉越多角色,這類失敗會越多。需要決定測試策略(改測試用的 species、或內容改動不以上游測試為門檻)。
8. **host 端做語法檢查**:Apple clang 預設 Mach-O target 不接受 `section` 屬性,要用 `--target=armv4t-none-eabi`;加 `-D__INTELLISENSE__` 的 IDE 捷徑不可行(`species_info` 檔案會多開一個陣列)。必須走完整的 `cpp | preproc` 管線。
