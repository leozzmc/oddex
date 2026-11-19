# 編譯與無頭測試

## 工具鏈（本機，不需要 sudo）
全部放在 `~/oddex-toolchain/`：

| 項目 | 版本 | 來源 |
|---|---|---|
| ARM GNU Toolchain (arm-none-eabi) | 15.2.rel1, darwin-arm64 | developer.arm.com（sha256 已比對官方 `.sha256asc`） |
| mGBA.app（GUI，手動遊玩用） | 0.10.5 | github.com/mgba-emu/mgba releases |
| libmgba 靜態庫（無頭測試用） | 0.10.5 原始碼 | `src/mgba/build-headless/libmgba.a` |
| cmake | pip 版 | `venv/`，只用來編 libmgba |

Xcode 授權尚未同意，所以 `/usr/bin/clang`、`make` 和 Homebrew 都不能用。`tools/env.sh` 會設定 `DEVELOPER_DIR=/Library/Developer/CommandLineTools` 來繞過。

## 編譯 ROM
```bash
. tools/env.sh
cd game && make -j$(sysctl -n hw.ncpu) TOOLCHAIN=$TOOLCHAIN
```
- 輸出：`game/pokeemerald.gba`（32 MB）。乾淨編譯約 80 秒。
- 工具鏈**一定要在 PATH 上**：`trainer_rules.mk` 直接呼叫 `arm-none-eabi-cpp`，只設 `TOOLCHAIN=` 會讓 `src/data/trainers.h` 產生失敗（Error 127）。
- libpng 的 warning 可以忽略。

## 無頭測試：`oddex-run`
`tools/headless/runner.c` 用 libmgba 執行 ROM，不限速（約 2,000 幀不到 1 秒），依照按鍵腳本操作並輸出 PNG 截圖。

建置（只需要一次）：`tools/headless/build.sh` → `~/oddex-toolchain/bin/oddex-run`

```bash
$ODDEX_RUN game/pokeemerald.gba script.txt
```

腳本語法（每行一個指令，`#` 之後是註解）：
| 指令 | 作用 |
|---|---|
| `wait N` | 不按鍵，跑 N 幀 |
| `press KEYS [hold=2] [after=10]` | 按住 KEYS hold 幀，放開後再跑 after 幀 |
| `hold KEYS N` | 按住 N 幀 |
| `repeat N <指令>` | 重複執行 |
| `shot path.png` | 截圖（240×160） |
| `save path.ss` / `load path.ss` | 存／讀 savestate（只能用在同一個 ROM 編譯結果） |
| `include other.txt` | 在這裡執行另一支腳本（路徑相對於目前這支腳本所在的目錄；最多巢狀 8 層）。被引入腳本的 `shot` 也會照常輸出。用來讓回歸腳本共用開頭段落，又不必依賴別支腳本留下的 savestate |

KEYS：`A B SELECT START RIGHT LEFT UP DOWN R L`，可用 `+` 組合（例如 `A+B`）。

參考腳本見 `tools/headless/scripts/`。目前時機（原版 1.17.2）：約第 700 幀進到 GAME FREAK 標題動畫；按 START 進標題畫面；之後每 52 幀按一次 A，第 4 次出現選單（NEW GAME），約第 7 次開始 Birch 開場白。
**不要按 SELECT**：標題畫面的 SELECT 是 Quickstart，會跳過 Birch 開場。

## 決定性（determinism）
runner 把 RTC 固定成「從 2026-01-01 12:00 UTC（白天）開始、隨幀數前進」的假時鐘（`RTC_FAKE_EPOCH`）。如果改用真實時間，遊戲的亂數會受影響，同一支腳本每次跑出來的戰鬥都會不一樣。
現在「同一個 ROM + 同一支腳本」每次都會產生逐像素相同的截圖。不過 ROM 一改（例如對話長度、程式碼），亂數的時機也可能跟著變，所以會經過戰鬥或草叢的腳本可能要重新調整。

## 驗收：`make check-oddex`
```bash
cd game && . ../tools/env.sh && make check-oddex -j$(sysctl -n hw.ncpu)
```
依序檢查產生檔是否過期、原版角色的引用（設定 `ODDEX_STRICT_MAPS` 後，指定路線有引用就失敗）、回歸腳本有沒有出現 crash screen，最後跟 `tools/headless/baselines/` 的基準截圖逐像素比對。

**基準截圖有放進 git。** 刻意改變畫面時（例如改對話、換圖），請在同一個 commit 裡更新基準：
```bash
cp game/build/oddex-check/<script>/**/*.png tools/headless/baselines/<script>/
```
更新前先看過新截圖，確認變化是預期中的。合併時，基準截圖的差異就是畫面變更的紀錄。

## 用 REA 分析編譯產物
分析「實際編進 ROM 的東西」時，優先用 REA（`reverse-engineer-anything` skill，後端是 Ghidra 12.1.4），不要手動 `nm` 加上逐位元組解碼。原始碼本身的問題，還是直接讀原始碼。

> **`GhidraLaunchError` 的原因（2026-11-19 已查明）**：REA 在 macOS 啟動 Ghidra 前，會先用 `xcrun swiftc` 編譯一個追蹤行程用的小工具（`bridge/process/ProcessRunTokenReader.swift`）。這台電腦還沒同意 Xcode 授權，所以 `xcrun` 失敗（exit 69），REA 只回報「Ghidra headless launch failed」。跟 ELF 大小無關；之前成功的幾次，剛好都是在先 source 了 `tools/env.sh`（會設定 `DEVELOPER_DIR=/Library/Developer/CommandLineTools`）的 shell 裡執行。
>
> **用法**：在 shell 裡先 `. tools/env.sh` 再執行 `rea ...`（CLI），就能正常使用。MCP 版的 REA 工具（`mcp__rea__*`）是由 `rea mcp` 行程執行，環境裡沒有 `DEVELOPER_DIR`，所以**目前一定會失敗，請改用 CLI**。根本解法要由使用者決定：在終端機執行 `sudo xcodebuild -license accept`（同時也會修好 Homebrew），或在 `~/.claude.json` 的 REA MCP 註冊中加上 `DEVELOPER_DIR=/Library/Developer/CommandLineTools` 並重新啟動 session。

完整的 `game/pokeemerald.elf`（34 MB）可以直接分析，第一次約 4 分鐘，資料符號也會解析出名稱（例如 `&sStarterMon`）。如果只需要看程式邏輯，可以先產生只保留程式碼和符號的版本，第一次分析約 2 分鐘，但資料位址只會顯示成 `0x08xxxxxx`：
```bash
tools/oddex/rea_code_elf.sh    # → game/build/pokeemerald.code.elf（約 7 MB）
```
之後在同一個 session 裡查詢很快。可以用 `close_binary` 的 `snapshot_path` 存快照，下次 `open_binary` 帶 `snapshot_path` 就能重用分析結果。

適合的用途：
- 反編譯確認某次修改實際編出來的邏輯（例如代號最後解析成哪個 species 常數）。
- 比對兩次 build 的同一個函式（`compare_functions`），確認合併只改到預期的地方。
- crash screen（`ODDEX_CRASH_SCREEN`）出現時，追呼叫路徑（`procedure_callers`、`get_call_graph`）。

限制：程式碼版的 ELF 不含 `.rodata`，所以資料表（例如 `gSpeciesInfo`、文字）要用完整 ELF 的符號位址去讀 `pokeemerald.gba`；反編譯結果裡指向 `0x08xxxxxx` 的常數位址，就是這些資料。

**REA 本身啟動失敗時**（`GhidraLaunchError` / `failure_kind: start`，MCP 和 `rea decompile` 都在 1 秒內失敗，但 `rea doctor` 全部通過）：問題出在 REA 的橋接層，不是 Ghidra 或 ELF（Sonia 在 2b 驗收時遇到；直接用 `analyzeHeadless` 匯入同一個 ELF 是成功的）。替代做法是直接用 REA 的後端 Ghidra 反編譯：
```bash
tools/oddex/ghidra_decompile.sh StartWallyTutorialBattle LoadWallyZigzagoon   # 約 10 秒，不做全域分析
```
這支腳本會產生程式碼版的 ELF，用暫時的 Ghidra 專案匯入（`-noanalysis`），再用 `tools/oddex/ghidra/DecompileFns.java` 反編譯指定的函式並印出 C。它只適合「確認某個函式編出來的樣子」；呼叫圖、跨函式比對這類需要全域分析的用途，還是要等 REA 修好。

## 已知問題
- mGBA 0.10.5 的 Qt 版沒有命令列腳本參數，所以另外寫了這個 runner。
- 沒有載入 .sav，每次都是全新遊戲。
