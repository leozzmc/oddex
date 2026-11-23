# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

oddex 是以 pokeemerald-expansion 1.17.2 為底的 GBA RPG：保留戰鬥、捕捉、進化系統，把角色、地圖和劇情換成原創內容。遊戲內文字用英文；docs 和團隊溝通用繁體中文。決策紀錄在 `docs/DECISIONS.md`，改方向之前先看這份。

## 環境（每個 shell 都要先做）

```bash
. tools/env.sh
```
這台 Mac 沒有同意 Xcode 授權，所以 Homebrew、`/usr/bin/clang`、`xcrun` 都不能直接用。`env.sh` 會設定 `DEVELOPER_DIR=/Library/Developer/CommandLineTools`，把 ARM 工具鏈（`~/oddex-toolchain/arm-none-eabi`）加進 PATH，並匯出 `$TOOLCHAIN`、`$ODDEX_RUN`、`$BLENDER`。工具鏈、mGBA、libmgba、Blender 都裝在 `~/oddex-toolchain/`，細節見 `docs/research/build.md`。

## 常用指令

```bash
cd game && make -j$(sysctl -n hw.ncpu)            # 編譯 → game/pokeemerald.gba（約 80 秒）
cd game && make check-oddex -j$(sysctl -n hw.ncpu)  # 驗收：一定要通過才能合併
python3 tools/oddex/check_maps.py [--maps X] [--render X]   # 地圖靜態檢查／預覽圖（不用編譯）
python3 tools/oddex/check_species_refs.py --summary [--scope early]
python3 tools/oddex/test_apply_replacements.py     # 替換工具的單元測試
$ODDEX_RUN game/pokeemerald.gba <script.txt>        # 無頭執行按鍵腳本並截圖
```
- `make` 預設不是 release build，assert 是開著的；`check-oddex` 靠它抓出 crash screen。
- 工具鏈一定要在 PATH 上：`trainer_rules.mk` 直接呼叫 `arm-none-eabi-cpp`。
- 上游的 `make check` 測試不是我們的門檻：有些測試寫死原版角色，內容被替換後失敗是預期中的。

## `make check-oddex` 做了什麼（`tools/oddex/check_oddex.sh`）

1. `gen_species.py --check`：產生檔是否過期。
2. `check_species_refs.py`：回報所有原版 species 的引用；`content/migration_scope.toml` 裡 `strict = true` 的範圍若還有引用就失敗。
3. `check_maps.py`：地圖大小、connection、warp、遮擋、可達性。原版本來就有的例外在 `check_maps_baseline.json`，只有新發現會失敗。
4. 用無頭模擬器跑 `tools/headless/scripts/` 的回歸腳本（預設清單寫在 `check_oddex.sh`）。只要出現 crash screen（`src/assertf.c` 會輸出 `ODDEX_CRASH_SCREEN` 到 log），或遊戲被默默重置（runner 監看 `gMain.vblankCounter1`，變小時輸出 `ODDEX_RESET`；這種情況不會有 crash screen）就失敗，然後跟 `tools/headless/baselines/<script>/` 逐像素比對。

**刻意改變畫面的 commit，要在同一個 commit 更新基準截圖**（`find game/build/oddex-check/<script> -name '*.png' -exec cp {} tools/headless/baselines/<script>/ \;`），更新前要先逐張看過。

## 架構：原創內容怎麼進入遊戲

**角色（species）**
- 資料來源是 `content/species/<name>.toml`（一隻一檔）、`content/roles.toml`、`content/regional_dex.toml`。圖檔在 `game/graphics/pokemon/oddex/<name>/`。
- `tools/oddex/gen_species.py`（共用載入器：`species_data.py`）會改寫 `game/` 裡用 `oddex:` 標記包起來的區段（例如 `include/constants/species.h` 的 `// oddex:species-ids begin/end`），並產生 `oddex_data.h`、`oddex_families.h`、`oddex_species.h`。產生的檔案有提交進 git；`game/oddex.mk`（被 `game/Makefile` include）會在來源改變時自動重跑。
- species ID 只能往後追加，因為 ID 會存進存檔；刪除角色時產生器會警告。改名會連帶改到 `SPECIES_*` 常數，必須保留原本的編號：在 TOML 加 `previous_ids = ["<舊 ID>"]`，產生器會把舊編號給新 ID。進化只能指向 `content/species/` 裡的原創角色（產生器會擋）。
- **代號（roles）**：劇情用到的角色一律寫成 `SPECIES_ODDEX_<ROLE>`，例如 `STARTER_GRASS`、`RESCUE_WILD`、`TUTORIAL_CATCH`。C、腳本、`trainers.party`（寫成 `Oddex Starter Grass`）、`wild_encounters.json` 都引用代號，所以換角色只要改 `roles.toml`。
- 美術：**先讀 `docs/ART_GUIDELINES.md`**（先設計再畫像素、8–12 色、真正的像素構圖、一定要在遊戲裡看；SpriteCook 的費用規則）。舊流程是 `tools/oddex/blender/`（headless Blender 建模渲染；面具風格見 `docs/research/mask-designs.md`）→ `tools/oddex/import_art.py`（量化成 15 色，產生異色、icon、overworld、足跡）。`placeholder_art.py` 是舊的幾何佔位圖產生器。

**方案 B（把原版角色換掉）**
- 整體計畫和步驟在 `docs/research/plan-b-references.md` §5 和 `docs/research/species-plan-b.md`。
- `content/migration_scope.toml` 定義每一段遷移的範圍（地圖、野生遭遇種類、明確的訓練家清單、例外）。`apply_replacements.py --scope <name>` 和 `check_species_refs.py --scope <name>` 讀的是同一份。
- `apply_replacements.py` 依 `content/replacements.toml`（原版 → 原創的對照表，早期角色定名後才會建立）就地改寫 `trainers.party`、`battle_partners.party`（雙打的隊友，scope 用 `partners` 列出）和 `wild_encounters.json`，只改 species 字樣、保持最小 diff，重複執行結果不變；對照表有缺漏或進化階段對不上時，失敗而且什麼都不寫入。
- 原版世代關掉之後，編譯器不會報錯，release build 會默默把原版角色變成 `SPECIES_NONE`。所以殘留只能靠 `check_species_refs` 和 debug build 的 assert 抓到，這也是 `check-oddex` 存在的原因。叫聲也一樣：`playmoncry` 原版角色在 debug build 會 assert。

**地圖與事件**
- 直接編輯 `game/data/maps/<Map>/map.json` 和 `scripts.inc`（不用 Porymap）。注意事項見 `docs/research/maps-events.md` 和 `docs/research/mapping.md`：mapjson 會靜默排除 region 不是 `REGION_HOENN` 的地圖；connection 兩邊都要寫、offset 互為相反數；「走得到」不等於「看得到」（上層圖層會蓋住物件）。

## 私人素材（寫實臉孔）

御三家是使用者和兩位朋友。2026-11-20 使用者核准**寫實版**作為正式造型，並同意放進 GitHub：`tools/oddex/likeness/compose.py` 產生的寫實 sprite 直接放在 `game/graphics/pokemon/oddex/<dir>/` 並提交。**原始照片和 `crop.toml` 仍然只放在 repo 外的 `~/oddex-private/`**，不提交（遊戲只需要產生出來的 sprite）。文件、TOML、commit 訊息都不要寫這三人的真名。`tools/oddex/build_private.sh` 留著，供之後若有只能留在本機的素材使用。

## 無頭測試（`tools/headless/`）

`runner.c` 是用 libmgba 寫的無頭執行器，不限速，RTC 固定在 2026-01-01 12:00 UTC，所以同一個 ROM 加同一支腳本，結果逐像素相同。腳本指令：`wait`、`press KEYS [hold] [after]`、`hold`、`repeat N <cmd>`、`shot`、`save`/`load`、`include other.txt`。
- 回歸腳本必須能從開機獨立跑完：共用開頭用 `include`，不要 `load` 別支腳本留下的 savestate。
- 組合回歸腳本時，截圖前不要另外插入 `wait`：`shot` 本身不會讓遊戲多跑影格，但多出來的 `wait` 會讓之後的戰鬥亂數錯開。需要等畫面時，在分段錄製時就把 `wait` 做成一段（例如 `raw:wait 20`），再接著錄後面的分段。
- 標題畫面不要按 SELECT（那是 Quickstart，會跳過 Birch 開場）。推進對話用 B，避免 A 又跟 NPC 講話或在 YES/NO 選到 YES。
- 腳本的確定性來自固定的 RTC；ROM 或角色一改，經過戰鬥和草叢的路線就要重新產生。用 `tools/headless/authoring/autopilot.py` 閉環產生（每段之後讀 RAM 判斷位置、戰鬥、HP、招式；`where.py` 讀 savestate、`plan.py` 規劃少踩草的路線），組好後從開機連跑一次確認和分段結果相同，再連跑兩次確認逐像素一致。autopilot 的靜態規劃走不通時（隱藏物件、執行中才改變的地塊、單向 warp），改用 `tools/headless/authoring/stepwalk.py START.ss OUT_PREFIX MAP X Y [--live]`。
- 原創角色可學的 HM，等於它在 `content/replacements.toml` 取代的原版角色能學的 HM（例外寫在 TOML 裡）；`gen_species` 會擋下沒有任何原創角色能學的 HM。
- ROM 一改（角色數、美術、版面）讓長路線的亂數位移時，用 `tools/headless/authoring/resync.py prepare OLD_GAME WORK SCRIPT` → `run` → `shots` → `assemble` 重新同步（OLD_GAME 是錄製時那個 commit 編好的 game/，例如 git worktree）；驗收要位置、等級和打倒的訓練家數都一致。細節見 `docs/research/plan-b-references.md` §6.4。
- 回報 check 結果前，要在**最後一個 commit** 上重跑，並對整份 log grep `FAIL|Error|CRASH|RESET|differs`，不要只看結尾。

## 分析編譯產物

問「實際編進 ROM 的是什麼」時用 REA CLI（先 `. tools/env.sh`，否則 `xcrun` 失敗會讓 Ghidra 啟動失敗）；MCP 版 `mcp__rea__*` 拿不到 `DEVELOPER_DIR`，目前不能用。只想看幾個函式時，用 `tools/oddex/ghidra_decompile.sh <函式...>`（約 10 秒）。資料表（`gSpeciesInfo`、文字）要用符號位址去讀 `.gba`。原始碼層面的問題直接讀原始碼。

## 寫程式的原則（ponytail）

使用者要求寫程式時善用 ponytail skill（已裝成使用者層級的外掛 `ponytail@ponytail`；新 session 會自動載入，也可以用 `/ponytail` 叫出）。重點：
- 先讀任務和它碰到的程式碼，列出改動必須碰到的所有地方（callers、測試、fixtures、設定）。
- 照順序取第一個能完整解決的選項：這需要存在嗎 → repo 裡已經有的（例如 `species_data.py`、`migration_scope.py`、`png_reader.py`、`maskkit.py`）→ 標準函式庫 → 已安裝的相依套件 → 一行能寫完 → 最後才寫最少的程式碼。
- 對解法偷懶，對改動本身不偷懶：callers、測試、基準截圖都要一起改完。新的非簡單邏輯要留一個小測試（放在 `tools/oddex/test_*.py`，`check-oddex` 會自動跑）。
- 知道限制的捷徑要註解成 `shortcut: <限制>, <何時要升級>`。
- 回報結尾用一兩行寫出「沒做或沒驗證的部分」和使用者需要知道的風險。

## 團隊與分支

- David：Tech Lead，負責工具鏈、整合、驗收；只有 David 會合併進 `develop`。Mark：角色、圖像、戰鬥（`feat/species`，worktree `~/oddex-wt/mark`）。Sonia：地圖、事件、腳本（`feat/events`，worktree `~/oddex-wt/sonia`）。
- `main` 不直接修改。各自在 feature branch 上 commit，rebase 到最新的 `develop` 後交給 David 合併；`develop` 在 `make check-oddex` 通過後推上 GitHub。
- 需要使用者決定的事（設計方向、要下載或安裝的東西、需要 sudo 的操作）交給 David 轉達，不要自己繞過。
