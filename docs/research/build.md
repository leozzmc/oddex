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

## 已知問題
- mGBA 0.10.5 的 Qt 版沒有命令列腳本參數，所以另外寫了這個 runner。
- 沒有載入 .sav，每次都是全新遊戲。
