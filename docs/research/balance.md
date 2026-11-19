# 原創角色的平衡檢查(種族值總和)

由 `tools/oddex/balance.py` 產生,只做報告,不會調整任何數值。差異 = (原創 − 原版) ÷ 原版。超過 ±15% 的標記為 **⚠**。原版的種族值取自 `species_info/*_families.h`,`P_UPDATED_STATS` 的條件式取新世代的值。

| 原創角色 | 屬性 | 階段 | 總和 | 出現位置 | 取代的原版(總和、差異) |
|---|---|---|---|---|---|
| Grinpack | Grass/Dark | 1 | 310 | starter Lv2–8 | Treecko 310 (+0%) |
| Trekkeye | Fire/Steel | 1 | 310 | starter Lv2–8 | Torchic 310 (+0%) |
| Ridgecap | Water/Flying | 1 | 310 | starter Lv2–8 | Mudkip 310 (+0%) |
| Okinoir | Grass/Ground | 1 | 310 | Route110, Route117 Lv12–20 | Oddish 320 (-3%) |
| Shishiblaze | Fire/Fighting | 1 | 310 | DewfordGym, GraniteCave, Route104 Lv12–19 | Makuhita 237 (+31%) **⚠**; Slugma 250 (+24%) **⚠**; Torkoal 470 (-34%) **⚠** |
| Kamorai | Water/Electric | 1 | 310 | Route104, Route106, Route107, DewfordTown Lv10–20 | Wailmer 400 (-22%) **⚠**; Carvanha 305 (+2%); Goldeen 320 (-3%) |
| Shachound | Dark/Psychic | 1 | 220 | Route101, Route102, Route103 Lv2–8 | Poochyena 220 (+0%) |
| Kyokon | Normal/Ghost | 1 | 240 | Route101, Route102, Route103, GraniteCave Lv2–8 | Zigzagoon 240 (+0%); Sableye 380 (-37%) **⚠** |
| Usobuzz | Bug/Fighting | 1 | 195 | Route101, Route102 Lv2–8 | Wurmple 195 (+0%) |
| Shawabolt | Electric/Fairy | 1 | 270 | Route102 Lv2–8 | Taillow 270 (+0%) |
| Utoghast | Flying/Ghost | 1 | 270 | Route103 Lv2–8 | Wingull 270 (+0%) |
| Shojobob | Water/Fairy | 1 | 220 | Route102, Route106 Lv2–8 | Lotad 220 (+0%); Tentacool 335 (-34%) **⚠**; Azurill 190 (+16%) **⚠** |
| Bekurama | Grass/Steel | 1 | 220 | Route102, GraniteCave Lv2–8 | Seedot 220 (+0%); Aron 330 (-33%) **⚠** |
| Yamambrr | Ice/Ground | 1 | 295 | Route102 Lv2–8 | Shroomish 295 (+0%) |
| Omotelle | Psychic/Dragon | 1 | 198 | Route102 Lv2–8 | Ralts 198 (+0%) |
| Deigloom | Psychic/Ghost | 2 | 290 | evolution Lv2–8 | Kirlia 278 (+4%) |
| Hannyagon | Ghost/Dragon | 3 | 520 | evolution Lv2–8 | Gardevoir 518 (+0%); Gallade 518 (+0%) |
| Komarock | Rock/Fighting | 1 | 285 | RustboroGym, Route116 Lv8–16 | Geodude 300 (-5%) |
| Iwadawn | Rock/Fairy | 1 | 375 | RustboroGym Lv14–16 | Nosepass 375 (+0%) |
| Kumozuka | Bug/Poison | 1 | 266 | Route116, PetalburgWoods Lv5–10 | Nincada 266 (+0%); Gulpin 302 (-12%) |
| Magatide | Water/Dragon | 1 | 255 | Route104 Lv5–10 | Magikarp 200 (+28%) **⚠**; Marill 250 (+2%) |
| Mandalumb | Normal/Ground | 1 | 280 | PetalburgWoods, Route116 Lv5–10 | Skitty 260 (+8%); Slakoth 280 (+0%); Whismur 240 (+17%) **⚠** |
| Tsunacoon | Bug/Fighting | 2 | 205 | PetalburgWoods Lv7–10 | Silcoon 205 (+0%); Cascoon 205 (+0%) |
| Tsukuyume | Dark/Fairy | 1 | 310 | Route116 Lv6–10 | Abra 310 (+0%) |
| Karuvajra | Fighting/Flying | 1 | 305 | Route116 Lv8–12 | Machop 305 (+0%) |
| Inarizuma | Electric/Grass | 1 | 320 | RustboroCity Lv5–10 | Pikachu 320 (+0%) |
| Gachirinza | Fighting/Psychic | 1 | 280 | DewfordGym Lv14–19 | Meditite 280 (+0%) |
| Komorimen | Poison/Flying | 1 | 245 | GraniteCave Lv6–11 | Zubat 245 (+0%) |
| Mandaring | Normal/Ground | 2 | 400 | evolution Lv20–38 | Delcatty 400 (+0%); Vigoroth 440 (-9%); Loudred 360 (+11%) |
| Mandaloka | Ground/Fire | 3 | 540 | evolution Lv38–60 | Slaking 670 (-19%) **⚠**; Exploud 490 (+10%) |
| Suzurai | Steel/Electric | 1 | 325 | Route110, MauvilleGym Lv13–22 | Magnemite 325 (+0%); Voltorb 330 (-2%) |
| Kagurai | Steel/Electric | 2 | 465 | MauvilleGym, evolution Lv22–40 | Magneton 465 (+0%) |
| Raijumen | Electric/Dark | 1 | 295 | Route110, MauvilleGym Lv12–20 | Electrike 295 (+0%) |
| Raijuoh | Electric/Dark | 2 | 475 | MauvilleGym, evolution Lv24–45 | Manectric 475 (+0%) |
| Torobi | Bug/Electric | 1 | 400 | MauvilleGym Lv18–22 | Illumise 430 (-7%); Volbeat 430 (-7%) |
| Tomoeden | Electric/Psychic | 1 | 405 | Route110 Lv12–16 | Plusle 405 (+0%); Minun 405 (+0%) |
| Shojomai | Water/Fairy | 2 | 340 | Route110, evolution Lv14–30 | Lombre 340 (+0%) |

## 被標記的角色(8 隻)

- Kyokon:最大差異 37%
- Shojobob:最大差異 34%
- Shishiblaze:最大差異 34%
- Bekurama:最大差異 33%
- Magatide:最大差異 28%
- Kamorai:最大差異 22%
- Mandaloka:最大差異 19%
- Mandalumb:最大差異 17%

<!-- notes: kept when balance.py regenerates the table above -->
## 說明(2026-11-20,Mark;先只報告,等使用者決定要不要調)

**沒有被標記的部分**:三人組、早期 12 隻、Rustboro 段、Dewford 的 2 隻,種族值都照著它們取代的原版角色設定,差異在 ±11% 以內。

**被標記的 8 隻,原因分成三類**:

1. **用現有角色填後面的位置**(Dewford 段;一隻原創角色同時涵蓋早期和後期的位置):
   - Kyokon(240)填 Sableye(380),差 −37%。
   - Shojobob(220)填 Tentacool(335),差 −34%。
   - Bekurama(220)填 Aron(330),差 −33%。
   - 這三隻都是早期的第 1 階段角色,種族值本來就低。到了 Granite Cave 和 Route 106,牠們的等級比 Route 101–103 高,但種族值仍然偏低。
   - 原版的 Sableye 和 Aron 本身就是「中期才遇到、比較硬」的角色,所以這裡的落差最明顯。
   - 可能的做法:這些位置之後換成新角色;或者讓這三隻有第 2 階段,把後期的位置對到第 2 階段。
2. **原御三家的新位置**:
   - Shishiblaze(310)同時取代 Makuhita(237,+31%)、Slugma(250,+24%)和 Torkoal(470,−34%)。
   - Kamorai(310)取代 Wailmer(400,−22%)。
   - 牠們是照御三家的數值設計的,所以拿來取代野生的格鬥系、水系時偏強,取代 Torkoal 時又偏弱。
   - Torkoal 只出現在勁敵的隊伍裡(Route 104),可以靠等級補。
   - 如果 Shishiblaze 要當 Brawly 的王牌(Makuhita 的位置),道館會比原版難一點。
3. **單一進化線涵蓋多個原版角色**:
   - Magatide(255)同時取代 Magikarp(200,+28%)和 Marill(250,+2%)。Magikarp 原本就是故意設計得很弱的角色,Magatide 的總和是照 Marill 抓的。
   - Mandalumb 取代 Whismur(240,+17%);同一條線的 Mandaloka(540)取代 Slaking(670,−19%)。
   - Slaking 的 670 有 Truant(懶惰,兩回合才能行動一次)這個特性壓著,實際戰力沒那麼高,所以 −19% 不一定代表偏弱。

**Roxanne 對 Grinpack(Sonia 在 `to_rustboro` 實測)**:
- Grinpack 要練到 Lv22 才贏得了,Lv19 會輸。
- Roxanne 的隊伍沿用原版的招式:Komarock 是 Tackle、Defense Curl、Rock Throw、Rock Tomb;Iwadawn 是 Block、Harden、Tackle、Rock Tomb。沒有格鬥招或妖精招,所以原創角色的屬性弱點在這場其實沒有被打到。
- 岩石招打草系只有 0.5 倍,所以難度比較可能來自 Iwadawn 的防禦 135 和 Harden:Grinpack 的主力招 Leafage 和 Razor Leaf 都是物理招,再加上 Oran 果和兩瓶傷藥。
- Grinpack 在 Lv9 會學 Mega Drain(特殊招,打 Iwadawn 是 2 倍、特防只有 90)。autopilot 是固定用第一格招式,值得用 Mega Drain 再測一次。
- 可以調整的地方:Iwadawn 的防禦或特防、Roxanne 的等級或道具,或者讓 Grinpack 早一點學到特殊的草系招式。

**要請使用者決定的事**:
- 第 1 類:要做新角色,還是幫現有角色加進化型?
- 第 2 類:Shishiblaze 當 Brawly 的王牌可以嗎?
- 選草系御三家的玩家打 Roxanne 偏難,要不要調(見上一段)?

在使用者決定之前,任何數值都不改。

## 建議調整(2026-11-20,Mark;只是建議,數值和對照都還沒改,等使用者決定)

「改對照」只動 `content/replacements.toml`,角色本身的數值不變。每一項的候選都用 15% 的規則檢查過(至少有一個屬性相同、階段一致、種族值差在 15% 以內)。

| # | 被標記 | 差異 | 建議 | 理由 |
|---|---|---|---|---|
| 1 | Shojobob ← Tentacool | −34% | **改對照:Tentacool → Kamorai**(310,−7%) | 水系相同;Kamorai 的雷神面帶電,也能聯想到水母的刺。Tentacool 在 Route 106–110 的釣魚、海面和訓練家隊伍裡出現很多次,這一項影響最大。Kamorai 已經涵蓋 Wailmer、Carvanha、Goldeen,所以海邊的種類會比較單調;如果之後做新的水系角色,可以再拆出去 |
| 2 | Bekurama ← Aron | −33% | **改對照:Aron → Komarock**(285,−14%) | 岩石系相同,而且 Granite Cave 本來就有 Komarock(Geodude)。缺點是鋼屬性會消失;等 Bekurama 有第 2 階段之後,也可以把 Lairon 對到它 |
| 3 | Kyokon ← Sableye | −37% | **暫時不改** | 幽靈系的現有角色都差太多(Utoghast −29%、Deigloom −24% 而且是第 2 階段)。偏弱只會讓 Granite Cave 稍微簡單一點。建議之後新增一隻 Dewford／洞窟的幽靈系角色 |
| 4 | Shishiblaze ← Makuhita | +31% | **暫時不改**;如果 Brawly 太難,把他王牌的等級降 1–2 | 格鬥系的現有角色都超過 15%(Gachirinza +18%、Karuvajra +29%)。Makuhita 的種族值低但 HP 很高,實際強度的差距沒有數字上那麼大。這一項請 Sonia 在 `to_dewford` 實測後再判斷 |
| 5 | Shishiblaze ← Torkoal | −34% | **改對照(選項):Torkoal → Mandaloka**(540,+15%,地面/火) | 只出現在勁敵隊伍。Mandaloka 是第 3 階段,而 Torkoal 是單一階段,所以要把 TORKOAL 列進 `stage_mismatch_ok`,理由寫「勁敵限定、沒有野生」;或者維持原樣,把勁敵那隻的等級加 3 |
| 6 | Kamorai ← Wailmer | −22% | **暫時不改** | Wailmer 要用 Good/Super Rod 才釣得到,實際遇到是在下一段以後。等 Wailord 出現的那一段,再做一條新的鯨魚系進化線 |
| 7 | Magatide ← Magikarp | +28% | **不改** | Magikarp 本來就是故意設計得很弱(只會 Splash),Magatide 的種族值是照 Marill 抓的;招式一開始也只有 Splash 和 Water Gun |
| 8 | Mandaloka ← Slaking | −19% | **不改** | Slaking 的 670 有 Truant 特性壓著,實際戰力接近 500 左右 |
| 9 | Mandalumb ← Whismur | +17% | **不改** | 只超出 2%,Skitty(+8%)和 Slakoth(0%)都在範圍內 |
| 10 | Shojobob ← Azurill | +16% | **不改** | 嬰兒寶可夢本來就特別弱,只超出 1% |

照這些建議做的話,只有 Bekurama 會從標記中移除,被標記的從 8 隻變成 7 隻。Shojobob 還有 Azurill(+16%),Shishiblaze 還有 Makuhita,Kamorai 還有 Wailmer。最大的差距(Tentacool、Aron)會消失,剩下的每一項都寫了暫時不改的理由。

## Brawly 戰的選項(2026-11-20,Mark;用數據比較,只是分析,數值都還沒改)

### 怎麼算的
- 工具是 `tools/oddex/damage_calc.py`,用 Gen 5 以後的傷害公式。
  - 中性性格,不加努力值。玩家的個體值算 15,對手照 `trainers.party` 寫的值。
  - 招式的威力、屬性、物理或特殊,取自 `moves_info.h`(取新世代的值)。
  - 不算會心、特性、道具、天氣和能力等級的變化。
  - Focus Punch 不算:它最後才出手,只要使用者先被打中就會失敗,而玩家一定會先攻擊它。
- 「打得過」的判定:一對一、雙方都用最好的招式,我方用最低的亂數,對手用最高的亂數。我方需要的擊倒次數不比對手多(對手先出手的話要少一次),就算贏。這是很保守的標準,實際上有道具、換人和等級優勢,會比這裡好打。
- **基準**:用同樣的標準算原版,Treecko、Torchic、Mudkip 打原版 Brawly(Machop、Meditite、Makuhita)要 **Lv19–21**(`--vanilla 421e141a`)。所以目標是三隻御三家都落在 Lv19–21,彼此差不多。

### 現況:三人組 Lv17 對 Brawly(Karuvajra Lv16、Gachirinza Lv16、Shishiblaze Lv19)
| 御三家 | Lv | 對手 | 我方最佳招式 | 打對手 | 幾下擊倒 | 對手最佳招式 | 打我方 | 幾下擊倒 | 速度 |
|---|---|---|---|---|---|---|---|---|---|
| Grinpack | 17 | Karuvajra Lv16 | Sucker Punch | 18–22% | 5–6 | Karate Chop | 65–78% | 2 | 我方先 |
| Grinpack | 17 | Gachirinza Lv16 | Sucker Punch | 45–56% | 2–3 | — | 0% | ∞ | 對手先 |
| Grinpack | 17 | Shishiblaze Lv19 | Sucker Punch | 16–20% | 5–7 | Vital Throw | 97–117% | 1–2 | 對手先 |
| Trekkeye | 17 | Karuvajra Lv16 | Flame Wheel | 32–38% | 3–4 | Low Kick | 90–109% | 1–2 | 我方先 |
| Trekkeye | 17 | Gachirinza Lv16 | Flame Wheel | 40–48% | 3 | — | 0% | ∞ | 我方先 |
| Trekkeye | 17 | Shishiblaze Lv19 | Scratch | 14–18% | 6–8 | Vital Throw | 120–143% | 1 | 對手先 |
| Ridgecap | 17 | Karuvajra Lv16 | Wing Attack | 60–72% | 2 | Seismic Toss | 34–34% | 3 | 我方先 |
| Ridgecap | 17 | Gachirinza Lv16 | Wing Attack | 75–89% | 2 | — | 0% | ∞ | 對手先 |
| Ridgecap | 17 | Shishiblaze Lv19 | Bubble Beam | 60–72% | 2 | Vital Throw | 21–25% | 4–5 | 對手先 |

- **問題的核心**:草/惡和火/鋼的第二屬性都怕格鬥。王牌 Shishiblaze(火/格鬥)又同時抵抗草和惡(Grinpack 的全部攻擊屬性),以及火和鋼(Trekkeye 的全部攻擊屬性),所以這兩隻練到幾級都打不過它。
- 反過來,Ridgecap(水/飛行)的飛行屬性抵抗格鬥,Lv14 就全贏,比原版的 Mudkip(Lv20)輕鬆很多。

### 各選項打得過的最低等級(Lv14–24 的範圍內;✗ 表示這個範圍內打不過)

| 選項 | Grinpack | Trekkeye | Ridgecap | 說明 |
|---|---|---|---|---|
| 原版基準(Treecko/Torchic/Mudkip) | Lv21 | Lv19 | Lv20 | 目標範圍 |
| 現況 | ✗ | ✗ | Lv14 | Shishiblaze 擋住兩隻,Ridgecap 太輕鬆 |
| (a1) Karuvajra 改成格鬥/幽靈 | ✗ | ✗ | Lv14 | 沒有用:問題出在王牌,而且 Karuvajra 的格鬥招一樣打得到 |
| (a2) Karuvajra 改成格鬥/火 | ✗ | ✗ | Lv14 | 同上,火屬性讓 Trekkeye 更難打 |
| (b1) 王牌改成 Karuvajra Lv19(招式不變) | ✗ | Lv24 | Lv17 | Grinpack 還是打不動(暗、草都被抵抗) |
| (b2) 王牌改成 Komarock Lv19(岩石/格鬥) | Lv24 | Lv24 | Lv14 | 有解但太高 |
| (b3) 王牌降到 Lv17 | ✗ | ✗ | Lv14 | 等級降低沒有用,屬性才是問題 |
| (b4) 全隊降 2 級(14/14/17) | ✗ | ✗ | Lv14 | 同上 |
| (c) Grinpack、Trekkeye 在 Lv15 學會 Aerial Ace | ✗ | Lv22 | Lv14 | 飛行打格鬥是 2 倍;但 Grinpack 打 Shishiblaze 還是不夠 |
| (b4)+(c) | Lv24 | Lv20 | Lv14 | |
| (b2)+(c)+全隊降級:王牌 Komarock Lv17,其餘 Lv14 | Lv19 | Lv21 | Lv14 | 草和火進入目標範圍,水還是太輕鬆 |
| **(F) 同上,再把王牌的 Reversal 換成 Rock Tomb** | **Lv19** | **Lv21** | **Lv16** | **三隻最接近原版**;Rock Tomb 打飛行是 2 倍,讓 Ridgecap 也有壓力 |
| (F),王牌改成 Lv18 | Lv21 | Lv23 | Lv17 | 偏難 |

### 建議
- **推薦 (F)**:
  - Brawly 的王牌從 Shishiblaze 換成 Komarock(Lv17,招式 Arm Thrust、Vital Throw、Rock Tomb、Bulk Up),Karuvajra 和 Gachirinza 降到 Lv14。
  - Grinpack 和 Trekkeye 在 Lv15 學會 Aerial Ace,寫在 TOML 的 learnset。這也能幫他們打之後的格鬥系訓練家。
  - 這樣三隻御三家需要的等級都在原版的 Lv19–21 附近,而且不會讓任何一隻變得太簡單或太難。
  - 這個方案要動 `trainers.party`(Sonia 的範圍)和三人組的 TOML(我的範圍)。
- **不推薦**:只改 Karuvajra 的屬性(a1、a2),或只降等級(b3、b4),算出來都沒有用。
- **連帶影響**:Shishiblaze 原本被安排在 Makuhita 的位置。如果它不再當王牌,Makuhita 在 Dewford 的野生和 Cristian 的隊伍可以保留 Shishiblaze;平衡報告裡 Makuhita 那筆(+31%)主要的影響也會跟著消失,因為不再是王牌。

### Roxanne 用同樣的方法重算(三人組 Lv15)
| 御三家 | Lv | 對手 | 我方最佳招式 | 打對手 | 幾下擊倒 | 對手最佳招式 | 打我方 | 幾下擊倒 | 速度 |
|---|---|---|---|---|---|---|---|---|---|
| Grinpack | 15 | Komarock Lv12 | Mega Drain | 90–109% | 1–2 | Rock Tomb | 26–30% | 4 | 我方先 |
| Grinpack | 15 | Komarock Lv12 | Mega Drain | 90–109% | 1–2 | Rock Tomb | 26–30% | 4 | 我方先 |
| Grinpack | 15 | Iwadawn Lv15 | Mega Drain | 40–48% | 3 | Rock Tomb | 33–38% | 3 | 我方先 |
| Trekkeye | 15 | Komarock Lv12 | Metal Claw | 60–72% | 2 | Rock Tomb | 35–40% | 3 | 我方先 |
| Trekkeye | 15 | Komarock Lv12 | Metal Claw | 60–72% | 2 | Rock Tomb | 35–40% | 3 | 我方先 |
| Trekkeye | 15 | Iwadawn Lv15 | Metal Claw | 67–81% | 2 | Rock Tomb | 40–47% | 3 | 我方先 |
| Ridgecap | 15 | Komarock Lv12 | Bubble Beam | 145–172% | 1 | Rock Tomb | 47–57% | 2–3 | 我方先 |
| Ridgecap | 15 | Komarock Lv12 | Bubble Beam | 145–172% | 1 | Rock Tomb | 47–57% | 2–3 | 我方先 |
| Ridgecap | 15 | Iwadawn Lv15 | Bubble Beam | 54–64% | 2 | Rock Tomb | 59–71% | 2 | 我方先 |

- **打得過的最低等級**:Grinpack Lv15、Trekkeye Lv13、Ridgecap Lv15,**都在 Lv14–17 以內**。
- 原版對照:Treecko Lv16、Mudkip Lv15,Torchic 在 Lv20 以內打不過。
- 結論:Roxanne 不需要調整。Sonia 之前量到的 Lv22,是因為 autopilot 固定用 Leafage(物理招)去打防禦 135 的 Iwadawn。改用 Mega Drain(特殊招,2 倍)就打得過,autopilot 已經改成依照攻防選招了。
