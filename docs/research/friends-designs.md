# 新御三家:山行三人組(使用者和朋友)

使用者的決定(經 David 轉達,記在 `docs/DECISIONS.md`):
- 御三家改成使用者和兩位朋友。
- **本體只有一顆頭**,臉越寫實越好。寫實的大臉上再合成怪異的附加部位,例如蜘蛛腳、翅膀。不戴面具。
- 主屬性維持草、火、水三角相剋;第二屬性要怪。
- 原本的御三家 Okinoir、Shishiblaze、Kamorai 保留,之後再安排位置(見 `mask-designs.md`)。

## 美術:寫實的臉

2026-11-20 使用者核准**寫實版**作為正式造型,並同意放進 GitHub(`CLAUDE.md` 的「私人素材」一節)。

- **sprite 放在 repo** 的 `game/graphics/pokemon/oddex/<dir>/`,由 `tools/oddex/likeness/compose.py` 產生:
  1. 從參考照片裁出頭部(蛋形遮罩,下半部往下巴收窄)。
  2. 拉高對比、稍微加強飽和度,減到 8 色。
  3. 夾在 Blender 渲染的「頭後面的部位」和「頭前面的部位」之間。
  4. 跑 make_art 的同一套流程,量化成 15 色。
- 背面和 overworld 用 Blender 的後腦勺和頭髮,膚色和髮色取自照片。
- **來源不進 repo**:參考照片和 `crop.toml`(臉在照片裡的位置)只放在 `~/oddex-private/`,compose.py 從那裡讀。`--keep`、`--preview` 的中間檔也要放在 repo 外。
- 文件、TOML、commit 訊息都不寫真名。
- Blender 模型裡的卡通臉仍然留著,用在背面、overworld,以及沒有照片的時候(例如別人 clone repo 後重新跑 make_art)。用 make_art 重新產生的話會變成卡通版;正式的圖要用 compose.py 產生。
- 如果以後有只能留在本機的素材,用 `compose.py --private` 輸出到 `~/oddex-private/likeness/`,再用 `tools/oddex/build_private.sh` 編譯。

**建模的分層**:
- 每個模型用 `maskkit.tag()` 把臉、頭髮、眼鏡標成 `head`,compose.py 會用照片取代這一層。
- 疊在臉前面的附加物標成 `front`。
- 其餘的部位都畫在頭的後面。
- `render_species.py` 在設定 `ODDEX_LAYERS` 時,會另外輸出分層的圖和頭部的像素框。

## 三隻(取日本妖怪裡「只有頭」的類型)

| 暫定名 | 屬性 | 妖怪 | 造型元素 → 附加部位 |
|---|---|---|---|
| Trekkeye | 火/鋼 | 輪入道(嵌在燃燒牛車輪裡的頭) | 亂翹的黑髮(髮梢冒火星)、放大的圓形墨鏡;頭後面是一圈燃燒的鐵車輪,輪輻往外伸成**蜘蛛腳**撐地;運動相機長在額頭,變成第三隻眼,錄影燈著了火 |
| Grinpack | 草/惡 | 釣瓶落とし(從樹上掉下來襲擊路人的大頭) | 齊瀏海、咧到耳邊的笑和兩排亮得過分的牙、瞇成弧線的眼睛;用藤蔓吊在樹枝下,頭頂長出葉子;細長的**蜘蛛腳**往上抓著藤,另一對往下垂 |
| Ridgecap | 水/飛行 | 飛頭蛮(夜裡離開身體、用耳朵飛的頭) | 紅帽長進頭裡,帽頂隆起成冠;細金框的圓眼鏡放大,裡面裝滿水,所以眼睛在水裡游;耳朵張開成**魚鰭狀的翅膀**;下巴滴著融雪水 |

蜘蛛腳(`spider_leg`、`spider_legs`)和翅膀(`wing`、`membrane`)是 `maskkit.py` 的共用零件,Rustboro 段的 Kumozuka 等也會用到。

### 屬性相剋(交給 Sonia,用在 Petalburg 屬性說明和 `to_petalburg` 的練等)

| | 弱點(受到的傷害) | 抵抗 | 免疫 |
|---|---|---|---|
| Trekkeye 火/鋼 | 地面 ×4、格鬥 ×2、水 ×2 | 蟲、鋼、草、冰、妖精 ×¼;一般、飛行、超能力、龍 ×½ | 毒 |
| Grinpack 草/惡 | 蟲 ×4;火、冰、毒、飛行、格鬥、妖精 ×2 | 水、電、草、地面、幽靈、惡 ×½ | 超能力 |
| Ridgecap 水/飛行 | 電 ×4、岩石 ×2 | 火、鋼、水、蟲、格鬥 ×½ | 地面 |

- Lv5 的招式和原本的御三家一樣:
  - 草:Tackle、Growl、Leafage。
  - 火:Scratch、Growl、Ember。
  - 水:Tackle、Tail Whip、Water Gun。
- 這樣 `to_starter` 的招式順序不用改。

## 在遊戲中的位置
- 2026-11-20 已經接手御三家:`roles.toml` 的 `STARTER_GRASS/FIRE/WATER` 改成 GRINPACK、TREKKEYE、RIDGECAP;`replacements.toml` 的 TREECKO、TORCHIC、MUDKIP 也一起改;`regional_dex.toml` 把三隻移到最前面(地區圖鑑 No.1~3,原版世代關掉之後才會從 1 開始)。
- `to_starter`、`to_petalburg`、`to_rustboro` 的基準截圖,以及 Petalburg 寶可夢中心的屬性說明,由 Sonia 重錄和改寫。
- 目前只有一個階段;要不要做進化線,之後再問使用者。
