# 現成像素素材調查（原創角色美術）

調查日期：2026-11-19。只查網頁資訊，沒有下載任何素材檔。
目的：找出 oddex 能**合法使用**的現成素材，用於原創角色（Fakemon）的戰鬥圖、icon、地圖上的造型等。決策背景：目前先用程式產生的佔位圖，之後再統一設計角色（見 `docs/DECISIONS.md`）。

篩選原則：
1. 不能是 Nintendo、Game Freak、The Pokémon Company 的素材，也不能是從官方圖描繪或修改而來（traced / edited）的圖。
2. 一定要有明確的授權條款，而且允許**修改**與**再散布**（包含放進 ROM）。
3. 授權條款依各頁面的說明為準。itch.io 的作者可以隨時修改條款，**實際採用前要再確認一次並存檔**（截圖或保存授權文字）。

> 重要前提：oddex 本身是 pokeemerald-expansion 的衍生作品，`game/` 裡含有原作的程式與素材。素材的授權合規只能確保「這些圖可以用」，**不會**改變整個 ROM 的散布風險。是否公開散布仍需另外決定（見之前的提醒）。

## GBA 規格對照

| 用途 | GBA / pokeemerald 規格 |
|---|---|
| 戰鬥正面／背面圖 | 64×64，4bpp，每張最多 16 色（第 0 色為透明），普通色與異色各一組調色盤 |
| 隊伍 icon | 32×32，2 幀，必須使用 3 組**共用**的 icon 調色盤之一 |
| 地圖上的造型（object event） | 16×16 或 32×32，4bpp，使用共用的物件調色盤 |
| 足跡 | 16×16，1bpp |

現成素材幾乎都需要**縮減色數（量化到 15 色以內）並重新指定調色盤**；icon 和地圖造型一定要重新對應到共用調色盤。這一步可以併入 `tools/oddex/gen_species.py` 的圖檔驗證流程。

## 可以考慮的來源

| 名稱 | 授權 | 內容 | 規格是否符合 GBA | 修改／放進 ROM 再散布 | 標示作者 |
|---|---|---|---|---|---|
| [50+ Monsters Pack 2D](https://opengameart.org/node/167826)（isaiah658，OpenGameArt） | **CC0** | 56 隻怪物，**正面＋背面**，每隻另有一組替代配色 | 64×64，每隻只用純黑＋4 色 → **完全符合**，可直接當普通色／異色 | 可以，CC0 沒有任何限制 | 不要求（作者表示歡迎標示）。#26、#47 是改編自其他作者的設計，但改編版與原版都是 CC0 |
| [Tuxemon](https://github.com/Tuxemon/Tuxemon)（開源怪物收集遊戲，素材也在 [OpenGameArt 的 Set 1](https://opengameart.org/content/tuxemon-set-1-154-monsters-front-and-back-sprites-and-menu-animations)） | **逐隻不同**，依 repo 的 `ATTRIBUTIONS.md`：怪物圖約 76 筆，大多是 **CC BY-SA 4.0**，少數是 CC BY 3.0/4.0、public domain | 正面＋背面，另有 24×24 的選單動畫圖；也有 NPC、地圖、道具圖示（各自標授權） | 64×64 → **尺寸符合**；色數不固定，需要量化 | 可以。**BY-SA 的 ShareAlike**：我們修改過的圖必須同樣以 CC BY-SA 釋出 | **必須逐隻標示**作者與授權。有些角色註明「based on」DeviantArt 上的作品，採用前要確認上游授權 |
| [Retromon 系列](https://willibab.itch.io/)（Willibab／Monsteretrope，itch.io） | 作者自訂：可用於個人與商業專案、可修改，**須標示作者**，禁止轉售或宣稱為自己的作品 | 每包 10～32 隻，**正面＋背面**，多組配色、陰影 | 56×56（另有 2×、3×）→ 放進 64×64 畫布即可；買家回報部分圖尺寸不一致 | 可修改；條款沒有明確說「再散布」，但允許用於遊戲，一般解讀為可以隨遊戲散布 | 必須（標示 Willibab 或 Monsteretrope，各頁措辭略有不同）。部分是付費包 |
| [Kenney – Tiny Creatures](https://opengameart.org/content/tiny-creatures) | **CC0** | 100+ 怪物、50+ 動物 | 16×16，只有單一方向 → **不適合戰鬥圖**，可以當地圖上的小造型或靈感 | 可以 | 不要求 |

只有正面圖的包（[Dan's MONSTERS pack 01](https://danieruart.itch.io/dans-monsters-pack01)、[Retro Pixel Monster Asset Pack 1](https://hsmtug.itch.io/retro-pixel-monster-asset-pack-1)、[Monsterparty 5](https://ninjagame-dev.itch.io/monsterparty-5) 等）：都是 64×64，條款大致允許商業使用與修改，但**沒有背面圖**，要自己補畫，所以優先度較低。採用前要逐一確認條款（例如 Dan's 禁止用於 NFT）。

## 不能用的（或風險太高的）

| 來源 | 原因 |
|---|---|
| 任何從官方遊戲擷取（ripped）的圖、Spriters Resource 上的官方素材 | 版權屬於 Nintendo、Game Freak、The Pokémon Company |
| 社群的「sprite base／模板」 | 許多是**描繪或修改官方圖**而來，屬於官方作品的衍生物。除非作者明確聲明是從零繪製，否則不用 |
| Pokémon Essentials 套件附帶的圖 | 套件本身含有官方素材 |
| [Fakemon Festival Pack](https://eeveeexpo.com/resources/654)（Eevee Expo） | 條款寬鬆（只要求在製作名單標示這個包），但內容混雜：包含**既有寶可夢的地區型態、Mega 進化、新型態**（明顯衍生自官方設計），也有作者表示「參考其他畫師的作品」，頁面沒有說明是否使用官方 base。尺寸以 Gen 4/5 為主。**要逐隻審查，整體不建議直接用** |
| [Battlers – Free Fakemon Pack](https://eeveeexpo.com/resources/1517)（Mikitari，Eevee Expo） | 作者寫「任何專案都可以使用」，是 Gen 4 風格、有背面圖和 icon。但沒有正式授權條款（沒寫能否修改、再散布），也沒說明是否使用官方 base。**可以聯絡作者取得書面同意，否則不用** |
| PokeCommunity 上的個人 fakemon 圖集 | 多數沒有正式授權，有些要求「使用前先私訊」，也有作者自承部分 icon 是修改官方圖。**不用** |
| Tuxemon 已標為「Formerly used」的素材 | 其中有 CC BY-NC／BY-NC-SA（**禁止商業使用**），Tuxemon 自己已經停用。只採用目前清單內、非 NC 的項目 |
| 授權不明或互相矛盾的包 | 例如 OpenGameArt 上某個 Tuxemon 相關包標 CC0，作者卻另外附加使用限制，跟 CC0 衝突 |

## 製作工具（簡述）

| 工具 | 授權／費用 | 適合用途 |
|---|---|---|
| [Pixelorama](https://orama-interactive.itch.io/pixelorama) | MIT，免費 | 支援索引色（indexed）模式與自訂調色盤，可以直接用 GBA 調色盤作畫 |
| LibreSprite | GPL（Aseprite 最後一個 GPL 版本的分支），免費 | 類似 Aseprite 的工作流程 |
| Aseprite | 付費（原始碼公開但非自由授權） | 業界最常用；可以鎖定 16 色調色盤、輸出索引色 PNG |
| 我們自己的管線 | — | `gbagfx` 轉換＋`gen_species.py` 驗證（尺寸、色數、調色盤）；佔位圖由 `gen_mossprit.py` 類型的腳本產生 |
| AI 像素生成（[PixelLab](https://www.pixellab.ai/termsofservice)、[Retro Diffusion](https://astropulse.itch.io/retrodiffusion)） | PixelLab 條款寫明產出歸使用者，但同時要遵守 Open RAIL-M 授權，商業條款沒有直接寫清楚；Retro Diffusion 的 EULA 在擴充套件內，網頁上沒有明文寫出能否商業使用 | **風險**：(1) 純 AI 產出在美國等地可能**無法取得著作權**，別人可以自由拿走；(2) 訓練資料可能含官方圖，產出可能「太像」官方角色；(3) Eevee Expo 等社群禁止 AI 內容，發表時可能被拒。只建議用來**發想**，最終圖要人工重繪或大幅修改 |

## 建議

1. **首選：isaiah658 的 50+ Monsters Pack（CC0）**。正面＋背面齊全、64×64、色數低到可以直接放進 GBA 調色盤，CC0 沒有任何義務，非常適合當作「比程式佔位圖更像樣」的第二階段佔位或正式素材的基礎。缺點：只有 56 隻，畫風比較簡單（4 色），跟 Emerald 原版的細緻度有落差；沒有 icon 與地圖造型，要自己補。
2. **次選：Tuxemon 的怪物圖（逐隻挑 CC BY-SA 4.0 ／ CC BY ／ public domain）**。數量多、規格接近，畫風也比較接近 GBA 時代。義務：製作名單**逐隻標示作者與授權**；我們修改過的圖要以 **CC BY-SA 4.0** 釋出（例如在 repo 放一份 `CREDITS-ART.md` 並附上修改後的 PNG）；「based on」外部作品的角色先跳過。
3. **補充：Retromon 系列**（可用於商業、須標示作者），用來補足特定屬性或造型。採用前保存當時的條款頁面。
4. **長期方向**：使用者已經決定之後要統一設計角色。比較穩的路線是**自己繪製**（Pixelorama／Aseprite＋我們的驗證管線），現成素材只當參考或過渡。這樣整個 oddex 的美術風格一致，也不會有授權混雜的問題。

**實作上的配套**（如果採用現成素材）：
- 在 TOML 裡為每隻角色加上 `art_source`、`art_license`、`art_author` 欄位，由 `gen_species.py` 自動產生製作名單，並在授權為 NC 或不明時讓 build 失敗。
- 在 repo 保存每個來源的授權文字快照（`content/licenses/`）。

## 來源
- https://opengameart.org/node/167826
- https://github.com/Tuxemon/Tuxemon（`ATTRIBUTIONS.md`、`README.md`）
- https://opengameart.org/content/tuxemon-set-1-154-monsters-front-and-back-sprites-and-menu-animations
- https://wiki.tuxemon.org/Creating_Creatures
- https://willibab.itch.io/retromon-pack-2、https://monsteretrope.itch.io/retro-pixel-monsters
- https://opengameart.org/content/tiny-creatures
- https://danieruart.itch.io/dans-monsters-pack01、https://hsmtug.itch.io/retro-pixel-monster-asset-pack-1、https://ninjagame-dev.itch.io/monsterparty-5
- https://eeveeexpo.com/resources/654、https://eeveeexpo.com/resources/1517
- https://www.pokecommunity.com/threads/earthretha-fakemon-pack.527306/、https://www.pokecommunity.com/threads/smileycorps-sprite-collection.352068/
- https://www.pixellab.ai/termsofservice、https://astropulse.itch.io/retrodiffusion
- https://orama-interactive.itch.io/pixelorama
