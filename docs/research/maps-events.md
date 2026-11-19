# 地圖／NPC／事件／劇情腳本 研究筆記

負責：Sonia（`feat/events`）　基準：pokeemerald-expansion `expansion/1.17.2`（`game/`）
以下路徑皆相對於 `game/`。

## 1. 檔案位置總覽

| 內容 | 位置 | 說明 |
|---|---|---|
| 單張地圖定義 | `data/maps/<Map>/map.json` | 地圖屬性、connections、object/warp/coord/bg events |
| 該地圖的腳本與文字 | `data/maps/<Map>/scripts.inc` | 組語巨集腳本 + `.string` 文字 |
| 地圖分組 | `data/maps/map_groups.json` | 新地圖要在此登記，決定 `MAP_*` 常數 |
| Layout（地形） | `data/layouts/layouts.json` + `data/layouts/<Map>/map.bin`、`border.bin` | `map.bin` 是 u16 陣列：bit0-9 metatile、bit10-11 collision、bit12-15 elevation |
| Tilesets | `data/tilesets/` | 圖塊圖像與 metatile 屬性 |
| 共用文字 | `data/text/*.inc` | 例：Birch 開場白 `data/text/birch_speech.inc` |
| 共用腳本 | `data/scripts/*.inc` | 例：`std_msgbox.inc`、`new_game.inc`（新遊戲時設定的 flags） |
| 腳本總入口 | `data/event_scripts.s` | `.include` 所有 `scripts.inc` 與 `data/text/*.inc` |
| 腳本巨集定義 | `asm/macros/event.inc` | `msgbox`、`applymovement`、`setflag`… |
| Flags / Vars | `include/constants/flags.h`、`include/constants/vars.h` | |
| NPC 圖像常數 | `include/constants/event_objects.h` | `OBJ_EVENT_GFX_*` |
| Map JSON 編譯規則 | `map_data_rules.mk` | |

## 2. 編譯流程

```
map.json ──mapjson map──▶ data/maps/<Map>/{header,events,connections}.inc   (自動產生，gitignored)
所有 map.json ──mapjson groups──▶ data/maps/{groups,headers,events,connections}.inc
                                  include/constants/map_groups.h
所有 map.json ──mapjson event_constants──▶ include/constants/map_event_ids.h  (LOCALID_* 常數)
layouts.json ──mapjson layouts──▶ data/layouts/layouts*.inc, include/constants/layouts.h

data/event_scripts.s (.include scripts.inc / text/*.inc)
   └▶ preproc -s (charmap.txt 轉換 .string) ▶ cpp ▶ preproc -ie ▶ as ▶ build/.../event_scripts.o
data/map_events.s (.include events.inc) ─ 同上 ▶ map_events.o
```

- 腳本巨集只是 `as` 的 macro，例如 `msgbox text, MSGBOX_NPC` 會展開為 `loadword 0, text` + `callstd MSGBOX_NPC`；`MSGBOX_NPC` 的實作是 `lock / faceplayer / message / waitbuttonpress / release`（`data/scripts/std_msgbox.inc`）。
- `.string` 會由 `tools/preproc` 依 `charmap.txt` 轉成遊戲內編碼。`\n` 換行、`\l` 捲動換行、`\p` 換頁、`$` 結尾。`{PLAYER}`、`{PAUSE n}` 等是 charmap 定義的控制碼。
- 標籤用 `::` 會變成 global（可以被其他檔案和 map.json 引用），用 `:` 則是 local。

## 3. map.json 事件類型

- `object_events`：NPC／物件。重點欄位有 `graphics_id`、`x`、`y`、`elevation`、`movement_type`、`script`、`flag`（flag 被設定時隱藏；`"0"` 表示永遠顯示）、`local_id`（選填，填了會產生 `LOCALID_*` 常數）。
  - **編號依陣列順序**：mapjson 依序編號 1..N，`LOCALID_*` 就是這個序號。**新的 NPC 一律加在陣列最後面**，否則既有的 `LOCALID_*` 和腳本中寫死的編號都會偏移。
  - 上限：每張地圖最多 64 個 templates（`OBJECT_EVENT_TEMPLATES_COUNT`），同時最多 16 個存在（`OBJECT_EVENTS_COUNT`）。
- `warp_events`：`dest_map` + `dest_warp_id`（目標地圖 warp 陣列的索引）。
- `coord_events`：踩上去觸發，條件是 `var == var_value`（例：未白鎮北邊出口的 `VAR_LITTLEROOT_TOWN_STATE` 擋人事件）。
- `bg_events`：看板（sign）、隱藏道具等。
- 地圖層級的腳本：`scripts.inc` 開頭的 `<Map>_MapScripts::`（`MAP_SCRIPT_ON_TRANSITION`、`ON_FRAME_TABLE`、`ON_WARP_INTO_MAP_TABLE`…）。

## 4. MVP 修改內容（本分支）

| # | 檔案 | 修改 | 遊戲中如何看到 |
|---|---|---|---|
| a | `data/text/birch_speech.inc` `gText_Birch_Welcome` | 開場白改成 oddex 原創文字（含「Welcome to the world of ODDEX!」） | 標題畫面 → NEW GAME，Birch 開口的第一段話 |
| b | `data/maps/LittlerootTown/scripts.inc` | Boy NPC（位於 (14,17) 研究所旁，flag 為 `0`，一開始就會出現）的對話改掉；標籤 `LittlerootTown_Text_BirchSpendsDaysInLab` 改名為 `LittlerootTown_Text_OddexBoy`（只有這裡引用） | 走出家門 → 往南走到研究所右側找男孩對話 |
| c | `map.json` + `scripts.inc` | 新增 NPC：`OBJ_EVENT_GFX_SCIENTIST_1`，位於 (9,12)，面朝下、不移動，腳本為 `LittlerootTown_EventScript_OddexGuide`；加在 object_events 最後（local id 9） | 走出家門後，廣場中央的科學家，對話內容是「...the new map event works!」 |

(9,12) 是從 `map.bin` 解析 collision/elevation 後挑的格子：可行走、elevation 3、不在任何 coord trigger 上（(10–11,1–2)、(8–11,9)），也不會擋住玩家從家門往南、往北的路線。

### 驗證（不需 arm-gcc）

```bash
cd game
export DEVELOPER_DIR=/Library/Developer/CommandLineTools
make tools
make include/constants/map_groups.h        # mapjson map 需要這個產生出來的 header
./tools/mapjson/mapjson map emerald data/maps/LittlerootTown/map.json data/layouts/layouts.json /tmp/out
grep OddexGuide /tmp/out/events.inc
# 預期：object_event 9, OBJ_EVENT_GFX_SCIENTIST_1, 9, 12, 3, ... LittlerootTown_EventScript_OddexGuide, 0
cp data/maps/LittlerootTown/scripts.inc /tmp/lr.s && ./tools/preproc/preproc /tmp/lr.s charmap.txt >/dev/null && echo OK
```

已確認：mapjson 成功；`LOCALID_LITTLEROOT_TWIN/MOM/RIVAL/BIRCH` 仍然是 1/4/7/8；preproc 接受所有新字串。**完整 ROM 編譯與實機畫面尚未驗證**（等 arm-none-eabi-gcc）。

### 實機測試步驟（給模擬器自動化）

1. 標題畫面請用 **START/A → NEW GAME**。**不要用 SELECT（Quickstart）**：`src/quickstart.c` 會直接呼叫 `CB2_SkipToNewGame`，跳過 Birch 開場，(a) 就看不到。
2. (a)：第一個文字框應該出現 `Ah, there you are! The odd one!`，下一頁是 `Welcome to the world of ODDEX!`。
3. 開場結束後，進入卡車 → 家 → 調整時鐘 → 出門（依照原版流程）。
4. (c)：出門後，廣場 (9,12) 會有一位科學家。
5. (b)：研究所右側 (14,17) 的男孩，對話內容是 `Did you hear? Something odd was…`。
6. 捷徑：debug 版可以按住 R + START 開啟 overworld debug menu（`DEBUG_OVERWORLD_MENU`）來設定 flag/var 或傳送。

## 5. 踩到的坑

1. **charmap 只有拉丁字元，不支援中文**。`.string` 裡寫中文時，preproc 會回報 `error: unknown character U+4F60` 並以 exit 1 結束（已實測）。要用中文需要另外處理字型與編碼（社群有 `rh-hideout-chinese/pokeemerald-expansion` fork，可以當參考）。→ **需要使用者決定 oddex 的文字語言**。
2. 文字寬度沒有自動換行，要自己用 `\n`、`\l`、`\p` 斷行。原版每行大約 ≤ 38 個字元（實際限制以像素寬度為準）；本分支每行都 ≤ 31 個字元。
3. Quickstart（標題畫面按 SELECT）會跳過 Birch 開場。
4. 新增 object event 時如果插在陣列中間，會讓後面所有 `LOCALID_*` 偏移。
5. `mapjson map` 會讀取 `include/constants/map_groups.h`，必須先用 `make` 產生。另外 `make` 有些目標（例：`src/data/trainers.h`）需要 `arm-none-eabi-cpp`，在工具鏈裝好前會失敗。
6. `preproc` 是依副檔名判斷模式，直接丟 `.inc` 會報 `unknown file extension`，要改成 `.s` 再處理。
7. 腳本文字裡有寫死的角色名和屬性（例：`PetalburgCity_PokemonCenter_1F` 的初始角色屬性說明）。替換角色後要改用 `bufferspeciesname STR_VAR_1, SPECIES_X` 加 `{STR_VAR_1}`，讓名字跟著 species 資料走；屬性相剋的說明則需要手動更新。Mossprit（Grass/Rock）已經用這個方式修正。
8. develop 首次匯入時，`game/.gitignore` 的 `tools/compresSmol/` 規則把上游 force-add 的原始碼略過了（已由 David 在 782c1ad2 修正）。

## 6. Porymap／Poryscript 評估

### Porymap（地圖 GUI 編輯器，huderlem/porymap）
- expansion 原生支援，map.json 格式本來就是 Porymap 的格式；changelog 裡也有「透過 Porymap 加 custom attribute」的說明。
- macOS 有官方的預編譯版本（GitHub Releases），不需要 Homebrew，下載解壓就能用。
- 對 Agent：GUI，沒辦法自動化。NPC、warp、trigger、腳本這些**直接改 JSON 比較快，也方便 review**（本分支就是這樣做的）。真正需要它的是 **`map.bin` 地形繪製和新地圖設計**，這部分用手寫 binary 不切實際。
- **建議**：Agent 不需要安裝。等到要重新設計地圖或繪製原創地形時，再由使用者在自己的機器上安裝來用，Agent 負責之後的 JSON/腳本修改。在那之前不需要。

### Poryscript（腳本語言，huderlem/poryscript）
- expansion 1.17.2 **預設沒有使用**（Makefile 裡沒有 `.pory` 規則，repo 裡也沒有 `.pory` 檔）。
- 導入方式：GitHub Releases 有 macOS 預編譯 binary（Go 寫的），或用 `go install` 安裝；放在 `tools/poryscript/`，在 Makefile 加上 `data/%.inc: data/%.pory` 規則，並加進 `make_tools.mk`。`.pory` 和既有的 `.inc` 可以並存，可以逐張地圖導入。
- 優點：if/while/switch 的可讀性比 `goto_if_*` 好很多；`format()` 能依字型寬度**自動換行**，正好解決坑 #2。CLI 工具，對 Agent 很友善。
- 缺點：多一個建置依賴和 Makefile patch；把上游原有的 `.inc` 轉換過來沒什麼好處；社群回報過 make_tools 規則和 Makefile 縮排的錯誤。
- **建議**：MVP 不導入。進入第二階段、開始寫大量原創劇情時再導入，**只用在新寫的原創地圖腳本**，上游原有的 `.inc` 保持不動。導入時由我提 Makefile patch 給 David review。
