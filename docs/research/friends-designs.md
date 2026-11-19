# 新御三家:山行三人組(使用者和朋友)

使用者的決定(經 David 轉達,記在 `docs/DECISIONS.md`):
- 御三家改成使用者和兩位朋友。
- **本體只有一顆頭**,臉越寫實越好。寫實的大臉上再合成怪異的附加部位,例如蜘蛛腳、翅膀。不戴面具。
- 主屬性維持草、火、水三角相剋;第二屬性要怪。
- 原本的御三家 Okinoir、Shishiblaze、Kamorai 保留,之後再安排位置(見 `mask-designs.md`)。

## 兩套圖

**公開版**放在 repo 的 `game/graphics/pokemon/oddex/<dir>/`:
- 臉是 Blender 建模的卡通版,認得出造型元素(墨鏡、齊瀏海、紅帽加圓眼鏡),但不是真實的臉孔。
- `make check-oddex` 和畫廊基準截圖都用這一版。

**私人寫實版**放在 `~/oddex-private/likeness/<dir>/`,**絕對不能進 repo**:
- 由 `tools/oddex/likeness/compose.py` 產生。repo 裡只有程式;參考照片、`crop.toml`(臉在照片裡的位置)和產出都在 `~/oddex-private/`。
- 做法:
  1. 從照片裁出頭部(蛋形遮罩,下半部往下巴收窄),減到 8 色。
  2. 夾在 Blender 渲染的「頭後面的部位」和「頭前面的部位」之間。
  3. 跑 make_art 的同一套流程,量化成 15 色。
- 背面和 overworld 用 Blender 的後腦勺和頭髮,膚色和髮色取自照片。
- 用 `tools/oddex/build_private.sh` 編成本機的 ROM。

文件、TOML、commit 訊息都不寫真名,外型只寫造型元素。

**建模的分層**:
- 每個模型用 `maskkit.tag()` 把臉、頭髮、眼鏡標成 `head`,私人版會用照片取代這一層。
- 疊在臉前面的附加物標成 `front`,兩版都會畫出來。
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
- 風格核准後,`roles.toml` 的 `STARTER_GRASS/FIRE/WATER` 才改成指向 GRINPACK、TREKKEYE、RIDGECAP;`replacements.toml` 裡的 TREECKO、TORCHIC、MUDKIP 也一起改。`regional_dex.toml` 要把三隻移到最前面。
- 這一步要和 Sonia 協調,重錄 `to_starter`、`to_petalburg` 的基準截圖。
- 目前只有一個階段;要不要做進化線,之後再問使用者。
