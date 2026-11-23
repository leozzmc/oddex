# 標題畫面(2026-11-23,Mark)

## 現況
- **背景層換成 Utsuroban 了**(`feat/title-screen`);使用者看過,照用。開機動畫不在這次範圍。
- **使用者對文字的決定(2026-11-23)**:
  - 上面的「POKéMON」標題字維持原版,不換(下面兩個草稿都不用)。
  - 副標題「EMERALD VERSION」改成「**ODDEX**」:`emerald_version.png`,大小、配色(白字、深色邊、陰影)和往右上斜的角度都照原版;調色盤沒有動。
  - 底部版權那一行改成「**FAN GAME, NOT OFFICIAL**」:在 `press_start.png` 的第二列,PRESS START 那一列沒有動。字是照原版那一行的畫法另外點的(5 px 高、上白下灰、黑邊)。
  - 兩張圖也由 `title_art.py` 產生;C 沒有改。
- 回歸腳本 `tools/headless/scripts/oddex_title.txt`(在 `check-oddex` 的預設清單裡):標題字加副標題 1 張,背景出現後每隔 64 個影格 1 張、共 4 張(閃光一個循環的四個點)。
- 產生方式:`python3 tools/oddex/title_art.py [--preview OUT.png]`,會寫出 `game/graphics/title_screen/` 的 `rayquaza.png`、`rayquaza.bin`、`rayquaza_and_clouds.pal`。檔名沿用原版,所以 C 一行都沒改。測試是 `tools/oddex/test_title_art.py`。
- 截圖:`~/oddex-shots/mark/title/`(`01_title_glow_frames_2x.png` 是遊戲內閃光的四個階段)。

## 背景層的格式和限制(讀 `src/title_screen.c` 得到的)
- 它不是一張 128×128 的圖。`rayquaza.png` 是一張 tile 表(128×128 = 256 個 8×8 的 tile,16 色),`rayquaza.bin` 是 32×32 的 tilemap,把 tile 排成**整個 240×160 的畫面**:上面是 7 階的天空色帶,下面是剪影。
- BG0、優先權最低,所以標題字、PRESS START(y 104–112、x 88–152)和版權那一行(y 144–152)都畫在它上面。
- 全部用 BG 調色盤第 14 組(`rayquaza_and_clouds.pal`),**和飄動的雲共用**:雲用第 2 色(白)和第 12 色,這兩色不能改。
- **第 15 色是程式在動的**:`UpdateLegendaryMarkingColor` 每 4 個影格重寫一次,在亮黃 (255,255,98) 和剪影的深色 (0,74,98) 之間來回,一個循環 256 個影格。原版 Rayquaza 身上的花紋就是這一色。
- 標題字閃光的那幾個影格,程式改的是整個畫面的底色(調色盤第 0 色),所以背景層不能有透明的像素。
- tile 上限:這一層的 tile 放在 char block 2,最多 512 個;原版用 256 個(一張 128×128)。

## 這次怎麼畫
- 天空色帶照原版。船是深色剪影(第 11 色),加兩個新的顏色:第 1 色(更深,鐵板的接縫)和第 3 色(較亮,圓頂和船緣的受光邊);這兩格原版沒有用到。
- 用第 15 色的地方(會跟著閃):三扇窗、船緣的燈、船身上四個看不懂的記號、光束的兩條邊和幾點光。暗的時候窗子和剪影同色,只剩窗裡的白眼睛。
- 窗裡是訪客的頭和兩隻杏仁形的眼(白色,第 2 色),沒有嘴。
- PRESS START 底下沒有第 15 色(測試會擋),所以字不會被閃光蓋掉;光束中間留著天空的顏色,版權那一行讀得出來。
- 箱子是素面的深色箱子,一條繩子吊著,沒有十字。
- 用了 99 個 tile(上限 256);左右和上下鏡像的 tile 會共用。

## 標題字:兩個草稿(使用者決定不用;留著備查)
草稿圖在 `~/oddex-shots/mark/title/`:`logo_A_lacquer_mask_*`、`logo_B_night_eyes_*`(`_on_title_3x.png` 是放在新背景上的樣子)。

| | A:漆面 | B:夜裡的眼睛 |
|---|---|---|
| 樣子 | 朱紅色的 ODDEX、金邊;O 換成一張白色的能面(兩條眼縫、閉著的嘴,不笑) | 淡玉色的 ODDEX、亮黃邊(和背景閃光同色);兩個 D 裡各有一個瞳孔,像一對盯著人看的眼睛 |
| 和遊戲的關係 | 直接點出「面具」;顏色和 Kamorai 的朱漆一致 | 和背景的船、訪客的眼睛呼應;比較冷、比較怪 |

要做進遊戲時要改的檔案和限制:
- `graphics/title_screen/pokemon_logo.png`(256×64,8bpp)和 `pokemon_logo.bin`:這也是 tile 表加 tilemap(32×32,每格 1 byte,仿射背景 BG2),**最多 256 個 tile**;兩個草稿各用 171 個。圖在畫面上的位置由 tilemap 決定,不是 256 px 寬的圖直接貼上去。
- `pokemon_logo.pal`:224 色(調色盤第 0–13 組)。第 14 組是背景層的,不能佔用。草稿各只用 6–9 色。
- `emerald_version.png`(128×32,兩個 64×32 的 sprite,16 色):副標題「EMERALD VERSION」。要換成什麼字(或拿掉)請使用者決定;拿掉要改 `title_screen.c`。
- `logo_shine.png`:掃過標題字的白光,形狀照舊就不用動;標題字的高度變了的話要在遊戲裡確認光有掃到。
- `press_start.png`(160×24):裡面除了 PRESS START,還有版權那一行「©2005 GAME FREAK inc.」。那一行要不要留、改成什麼,也請使用者決定。
- 標題字從上面滑下來、放大縮小的動作是程式做的(BG2 的仿射參數),新的字只要大小和原版接近就不用改程式。
