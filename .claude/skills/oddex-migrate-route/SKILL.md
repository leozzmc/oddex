---
name: oddex-migrate-route
description: Migrate a stretch of the oddex game (a route, town or story segment) from vanilla Pokémon to original oddex species under plan B — scope file, replacement table, apply_replacements, scripts/text/map objects, regression script and strict checks. Use this whenever work in the oddex repo involves replacing vanilla species in trainers, wild encounters, scripts or dialogue for some area, preparing the next segment (e.g. "do Route 104 to Rustboro", "migrate the early game", "run 4b", "make Petalburg Woods use our creatures"), or flipping a scope in content/migration_scope.toml to strict.
---

# 遷移一段路線到原創角色（方案 B）

方案 B 的目標是讓遊戲完全不再用原版角色。一段路線算「遷移完成」的定義是：`content/migration_scope.toml` 裡它的範圍設成 `strict = true` 之後，`make check-oddex` 仍然通過。編譯器不會幫忙：原版世代關掉之後，release build 會默默把原版角色變成 `SPECIES_NONE`，所以殘留只能靠 `check_species_refs.py` 和回歸腳本裡 debug build 的 assert 抓到。整體計畫在 `docs/research/plan-b-references.md` §5。

開始前先 `. tools/env.sh`。

## 1. 定義範圍

在 `content/migration_scope.toml` 加一個新範圍（先 `strict = false`）。檔案開頭的註解說明了每個欄位。

- **訓練家用明確清單**，不要依地圖推斷：同一張地圖上常有中期才走得到的訓練家（例如 Route 103 有 8 名要從 Route 110 或衝浪才遇得到）。用 `python3 tools/headless/authoring/stage_reach.py <起點地圖> X Y "Map,Map*,..."` 確認這個階段走得到誰：它只走陸路、跨 connection 和 warp，不能衝浪、居合斬、碎岩、怪力，訓練家旁邊或視線內有一格到得了就算。劇情上的封鎖它判斷不出來（例如 Petalburg 道館的地形走得到，但 Norman 是第 5 個徽章），要人工排除。不要用 `check_maps.py` 的可達性，那個假設已經有所有場地招式，判斷的是「最終」走不走得到。
- 野生遭遇用 `wild_maps` 加 `wild_kinds`；還沒有釣竿或衝浪時，只放 `land_mons`。
- 這段路線用到的**共用腳本**（`game/data/scripts/*.inc`，例如兩戶主角家共用的 `players_house.inc`）不在任何地圖底下，`maps` 涵蓋不到，要列進 `script_files`。用 `grep -rn "goto\|call" data/maps/<地圖>/scripts.inc` 找出這段的地圖跳去哪些共用腳本。
- 刻意留下的原版引用（例如設定角色、破關後才出現的東西）放進 `exclude_refs`，每一條都要寫明理由。用例外並寫清楚，比用不相干的佔位角色硬頂替更好。
- 列出這段的工作清單：
  ```bash
  python3 tools/oddex/check_species_refs.py --scope <name>
  ```
  清單會分成 party、wild、script、text、gfx、c 等類別。

## 2. 先錄原版基準

改內容之前，先有一支能從開機獨立跑到這段路線的回歸腳本（`tools/headless/scripts/to_<地點>.txt`，用 `include` 接前一段，不要 `load` 別支腳本的 savestate），在**還沒遷移**的 ROM 上錄好基準截圖，連跑兩次逐像素一致，並加進 `check_oddex.sh` 預設的腳本清單。這樣之後每一步都能證明「只有預期的畫面改變了」。路線用 `tools/headless/authoring/autopilot.py` 閉環產生：草叢逐格走；戰鬥一次按一鍵（A；新招比最弱的現有招式好才學，否則按 B；選招畫面依對手的屬性和攻防（物理對防禦、特殊對特防）挑最有效、還有 PP 的攻擊招式；打不贏的野生戰逃跑）；被腳本擋住按 B；第一格變成狀態招式或 PP 低於 5 時，在大地圖上換招式；被走過來的訓練家擋路時繞路；需要練等級用 `grind:Map:x1:y1:x2:y2:LV`。組好之後從開機連跑一次，確認跟分段結果相同，再連跑兩次確認逐像素一致。確定性靠的是固定的 RTC，所以角色或 ROM 一改就要重新產生。

## 3. 對照表與代號

- `content/replacements.toml` 的 `[replace]`：每個原版角色（每一個進化階段一個 key）對到一個原創角色的 `id`。進化階段要對得上；刻意跨階段的列進 `stage_mismatch_ok`。
- 缺少的原創角色，先用 `oddex-new-species` 技能做出來，不要用不相干的角色湊數。
- 劇情位置（御三家、教學、劇情戰）要改 `content/roles.toml`，讓 `SPECIES_ODDEX_<ROLE>` 指向原創角色，不要改 C 或腳本裡的引用。

## 4. 套用

```bash
python3 tools/oddex/apply_replacements.py --scope <name> --dry-run   # 先看會改什麼
python3 tools/oddex/apply_replacements.py --scope <name>
```
它只改 species 字樣（暱稱、性別、持有物都保留），重複執行結果不變。表有缺漏或進化階段不一致時，會列出全部並且什麼都不寫入；這時補齊對照表，不要用 `--fallback` 草草帶過（`--fallback` 只適合暫時試跑）。

`apply_replacements.py` 只處理 `trainers.party` 和 `wild_encounters.json`。其餘的要手改，每一項都要在這段的回歸腳本截圖裡看到結果：
- **腳本**裡的 `SPECIES_*`：包括 `givemon`、`setwildbattle`、`seteventmon`、`bufferspeciesname`，以及 **`playmoncry`**（叫聲雖然「先無聲」，但原版角色的 `playmoncry` 在 debug build 一樣會 assert）。
- **文字**裡寫死的角色名：改用 `bufferspeciesname` 加代號，或重寫句子。牽涉屬性的說明（例如 Petalburg 寶可夢中心的屬性介紹）要跟著原創角色的屬性改。
- **地圖上寶可夢造型的物件**（`map.json` 的 `OBJ_EVENT_GFX_*`）：改用 `OBJ_EVENT_GFX_SPECIES(<原創角色或代號>)`，讓地圖上看到的和實際戰鬥一致；不屬於角色的（例如搬家公司的設定角色，以及民宅裡的裝飾娃娃）列進 `exclude_refs` 並寫理由。改 `map.json` 後跑 `python3 tools/oddex/check_maps.py --maps <地圖>`，確認沒有被上層圖層蓋住或走不到。

## 5. 驗證並收尾

1. `cd game && make check-oddex -j$(sysctl -n hw.ncpu)`：回歸腳本不能出現 crash screen。
2. 逐張看過改變的截圖（新角色出現在戰鬥、對話裡的名字和屬性），確認都是預期中的，再在同一個 commit 更新 `tools/headless/baselines/`。經過戰鬥的腳本，角色換了之後亂數時機會變，可能要用 `tools/headless/authoring/` 重新校準。
3. 把範圍改成 `strict = true`，再跑一次 `make check-oddex`，要通過。這一步就是「這段遷移完成」的證明。
4. 改到 C 的部分，用 REA CLI 或 `tools/oddex/ghidra_decompile.sh` 確認代號解析成原創角色。
5. 回報給 David：範圍名稱、改了多少隻（party／wild／script／text／gfx）、`exclude_refs` 新增的條目和理由、更新了哪些基準截圖，以及需要使用者決定的劇情或設計問題（例如「搬家改由誰來搬」）。
