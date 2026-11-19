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
