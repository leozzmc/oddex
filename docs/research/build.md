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

## 已知問題
- mGBA 0.10.5 的 Qt 版沒有命令列腳本參數，所以另外寫了這個 runner。
- 沒有載入 .sav，每次都是全新遊戲。
