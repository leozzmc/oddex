---
name: oddex-new-species
description: Add or redesign an original oddex creature (species) end to end — TOML data, Blender/placeholder/imported art, regional dex, roles, generated code, gallery screenshots and verification. Use this whenever work in the oddex repo touches content/species/*.toml or graphics/pokemon/oddex/, e.g. "add a new mask creature", "make the next batch of species", "redesign Kamorai's sprite", "rename a species", "give X an evolution", "turn my friend into a Pokémon", or importing outside artwork, even if the request doesn't say "species".
---

# 新增或改設計 oddex 原創角色

原創角色的唯一來源是 `content/species/<name>.toml` 和它的圖檔目錄；`game/` 裡的 species 程式碼都是由 `tools/oddex/gen_species.py` 產生的。所以修改都從 TOML 和圖檔開始，不要手改產生出來的檔案（`oddex_data.h`、`oddex_families.h`、`oddex_species.h`、`species.h`／`pokedex.h` 裡 `oddex:` 標記包起來的區段、`oddex_gallery.txt`），下次產生時會被覆蓋。

開始前先 `. tools/env.sh`。

## 1. 先讀過的東西

- `docs/DECISIONS.md`：目前的設計方向（例如面具風格是「傳統日式恐怖」、名字是暫定名、叫聲先用 `NONE`）。
- `docs/research/mask-designs.md`：每隻面具角色的來源、象徵和配色。新的面具角色也要在這裡補一段（面具名稱、出處劇目或舞蹈、面具本體還是四腳獸、屬性理由）。
- 拿一個現有的 TOML 當範本：`content/species/omotelle.toml` 是最完整的例子（有 `previous_ids`、進化、`[design].family`），單階的看 `okinoir.toml`。行內註解只寫了容易弄錯的欄位，各欄位的檢查和預設值在 `tools/oddex/gen_species.py`。

## 2. 寫 TOML

- `id` 全大寫，會變成 `SPECIES_<ID>`。`name` 和 `category` 各最多 12 個字元。
- 名字要和原版、以及真實存在的寶可夢比對過，避免重名（之前 Glimmet 就因為是第 9 世代的真實寶可夢而改名）。
- 屬性維持「少見又怪」的組合；數值先比照它在劇情中取代的原版角色，平衡之後再調。
- 進化寫在最上層的 `evolutions = [{ method = "LEVEL", param = 20, into = "DEIGLOOM" }]`，要放在第一個 `[表格]` **之前**（例如緊接在 `cry` 後面）；寫在 `[dex]`、`[learnset]` 這類表格底下，TOML 會把它歸到那個表格裡，產生器會報錯。同一條進化線的每一階都是獨立的 TOML，`[design].family` 要一致。
- **species ID 只能往後追加**，因為 ID 會存進存檔。新角色排在最後面。改名時保留原本的編號，不要刪掉舊檔再新增：
  1. `git mv content/species/<舊>.toml content/species/<新>.toml`，圖檔目錄也 `git mv`，再把 `[graphics] dir` 改成新目錄。
  2. 把 `id` 改成新名字，加上 `previous_ids = ["<舊 ID>"]`（可以列多個，改名第二次時保留更早的名字）。`gen_species.py` 會把舊 ID 的編號給新 ID，並從 `all_learnables.json` 拿掉舊的 key。
  3. 舊 ID 不能再被其他角色使用，產生器會擋下來；`regional_dex.toml`、`roles.toml`、`replacements.toml` 裡的舊 ID 要自己換掉。
- 每隻角色都要在 `content/regional_dex.toml` 的 `order` 裡出現**恰好一次**，否則產生器會報錯。
- 如果這隻角色要放到劇情位置（御三家、救 Birch、Wally 教學等），改的是 `content/roles.toml`，不是 C 或腳本：劇情一律引用 `SPECIES_ODDEX_<ROLE>`。

## 3. 美術

三種來源，依情況選一種：

1. **Blender 面具（目前的主要做法）**：說明在 `tools/oddex/blender/README.md`。
   - 每隻一個建模檔 `tools/oddex/blender/species/<model>.py`（`<model>` 是 TOML 的 `[graphics] model`，沒寫就是 id 的小寫），裡面定義 `NORMAL`、`SHINY` 兩組配色和 `build(k, c)`。`k` 是共用函式庫 `tools/oddex/blender/maskkit.py`，`c` 是配色；`build` 回傳 `{'kind': 'mask' 或 'beast', 'size', 'front_az', 'front_el', 'side_az', 'squash'}`，`kind` 也決定足跡的形狀。從最像的一隻複製開始改（有獠牙的面具看 `kamorai.py`、`hannyagon.py`；靜態的看 `omotelle.py`；四腳獸看 `shachound.py`）。
   - 有獠牙的面具用 `k.glare_eyes()`（金眼加黑瞳）和 `k.fanged_mouth()`（上下排牙齒、深色縫、暗紅牙齦），配 `steps=k.HORROR_STEPS` 和 `weathered`；靜態的面具用慘白、無表情、空洞的眼神（`k.hole()`）。貼在臉上的部件用 `k.front_only()` 標記，背面圖拍的是面具內側。
   - 產生圖檔（一隻約 15 秒，會寫入 `[graphics] dir` 裡所有的圖和調色盤，異色版的調色盤索引自動對齊）：
     ```bash
     python3 tools/oddex/blender/make_art.py HANNYAGON [ID ...] --preview <scratchpad>/sheet.png
     ```
     `--preview` 產生正面、背面、異色、icon、overworld 的對照表，先看過這張再跑產生器；`--keep DIR` 保留 256px 的原始渲染，用來除錯。不需要自己呼叫 `$BLENDER`，也不需要開介面或 MCP。
2. **外部 PNG**：`python3 tools/oddex/import_art.py <id> --front F --back B [--icon I] [--overworld O] --out <dir>`，會自動去背、縮放、量化成 15 色，並產生異色版、icon 和 overworld。用之前要確認素材的授權（`docs/research/art-assets.md`）。
3. **幾何佔位圖**：在 TOML 寫 `[graphics.placeholder]`，再跑 `python3 tools/oddex/placeholder_art.py <id>`。換成正式美術後，要刪掉這一段。

GBA 的限制：正背面 64×64、15 色加透明；異色版必須和普通色共用同一個調色盤索引（換色不換形）；icon 必須用共用的 icon 調色盤。這些產生器都會檢查。

## 4. 產生並驗證

```bash
python3 tools/oddex/gen_species.py          # 也會重新產生 tools/headless/scripts/oddex_gallery.txt
cd game && make check-oddex -j$(sysctl -n hw.ncpu)
```

`check-oddex` 會在 sprite 檢視器裡逐隻截圖普通色和異色（`oddex_gallery`）。新角色或改過的圖一定會跟基準不同，這是預期中的：

1. 打開 `game/build/oddex-check/oddex_gallery/shots/` 裡的新截圖，**逐張看過**：輪廓是否清楚、眼睛和嘴巴在 64px 下是否還看得出來、異色是否只換色、平台上的位置有沒有偏。
2. 確認沒問題後再更新基準。截圖檔名是 `<編號>_<id>.png`／`<編號>_<id>_shiny.png`，改名或新增角色後舊檔名不會被覆蓋，所以先整個清掉再複製：
   ```bash
   git rm -q tools/headless/baselines/oddex_gallery/*.png
   cp game/build/oddex-check/oddex_gallery/shots/*.png tools/headless/baselines/oddex_gallery/
   ```
   再跑一次 `make check-oddex`，要 0 差異。
3. 其他腳本（例如 `to_petalburg`）也可能跟著變：角色數量改變會影響亂數，對手寶可夢的性別之類的會換。一樣把截圖跟基準並排看過，確認只有這類差異，才更新那一張，並在 commit 訊息說明。
4. 如果改到了 C（例如常數改名波及程式碼），用 REA CLI（先 `. tools/env.sh`）或 `tools/oddex/ghidra_decompile.sh <函式>` 確認實際編出來的結果。增減角色時，可以反組譯 `SanitizeSpeciesId` 或 `GetSpeciesName`，確認上界是新的 `SPECIES_EGG`（Ghidra 顯示成 `_UNK_` literal 時，直接從 `game/pokeemerald.gba` 讀那個位址的 4 個 byte）。

## 5. 提交與交件

- 工具（Blender 函式庫、腳本）和內容（TOML、圖檔、重錄的基準截圖）分開 commit；同一個內容 commit 裡要同時包含造成畫面改變的修改和更新後的基準。
- 回報給 David 時附上：新增或修改了哪些角色、畫廊總覽圖的路徑、`make check-oddex` 的結果，以及任何需要使用者決定的設計問題。造型風格的新方向，先交 3～4 隻的截圖給使用者看過再大量製作。
