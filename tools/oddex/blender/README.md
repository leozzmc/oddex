# Blender 面具渲染

用 headless Blender 以 Python 建模並渲染原創角色,產生 GBA 規格的圖檔。不需要開介面,也不需要外掛或 MCP。
Blender 5.2.4 LTS,安裝在 `~/oddex-toolchain/Blender.app`(`. tools/env.sh` 之後用 `$BLENDER`)。

```bash
. tools/env.sh
python3 tools/oddex/blender/make_art.py KAMORAI [ID ...] [--keep DIR] [--preview sheet.png]
python3 tools/oddex/gen_species.py          # 由新圖算出大小、Y 位移、icon 調色盤
```

一隻約 15 秒。`make_art.py` 會用 NORMAL 和 SHINY 兩組配色各渲染一次,然後縮小、加輪廓、量化,寫進該角色 `[graphics] dir` 的所有檔案:`anim_front`(2 幀)、`back`、`icon`、`overworld`(6 幀)、足跡,以及 4 個調色盤。

## 檔案
- `maskkit.py`:共用的建模和渲染函式庫(在 Blender 裡執行)。
  - 材質:`toon()` 是 3 階明暗(`two_tone` 只有 2 階,給小部件省色)、`glint` 是漆面高光、`weathered` 是斑駁的舊漆(把局部壓到較暗的那一階,不會多佔顏色)、`HORROR_STEPS` 是陰影更深的 3 階。`flat()` 是不打光的純色。
  - 面具:`mask_shell()` 是有厚度的外殼(背面看得到內側)、`on_face()`/`bump()`/`hole()`、`glare_eyes()`(深眼窩、大金眼、黑瞳孔)、`brows()`(眉頭往中間皺起)、`fanged_mouth()`(口腔、牙齦、一顆一顆的牙、獠牙)、`wrinkles()`、`cord_holes()`/`cord()`。貼在臉上的部件用 `front_only()` 標記,拍背面時會隱藏,因為面具的內側只有漆面。
  - 四腳獸:`beast_behind_mask()` 把一隻小獸放在原點面具的後方。
  - 其他:`spike()`/`rod()`/`ellipsoid()`/`torus()`、`snapshot()`/`since()`/`transform()`(整組旋轉或移動)、`set_light()`。
- `species/<model>.py`:每隻一個檔(`[graphics] model`,預設是 id 的小寫),定義 `NORMAL`、`SHINY` 配色表和 `build(kit, palette)`。回傳值可以設定 `kind`(`mask` 或 `beast`)、`size`、`front_az`、`front_el`、`side_az`、`squash`。
- `render_species.py`:Blender 的進入點,建模後渲染 front、front2(壓扁的第二幀)、back、ow_front、ow_back、ow_side。
- `make_art.py`:系統 Python 的進入點,負責上面說的後處理和寫檔。

## 為什麼這樣做(在 GBA 上看起來最好的組合)
- 用 EEVEE 加 toon,把 Diffuse 接到 Shader to RGB,再接常數色階,最後用 Emission 輸出。色彩管理用 **Standard**,AgX 或 Filmic 會改變顏色。Workbench 的 STUDIO 打光會把白臉壓成灰色,所以不用。
- 用 256 px、**1 個取樣**(沒有反鋸齒混色)渲染,再以 4×4 區塊取最多的顏色縮小到 64 px。用平均縮小的話,顏色會變混濁。
- 縮小後加 1 px 的深色輪廓。
- 量化:顏色少的話全部保留;超過 15 色時,優先合併「距離近、面積又小」的顏色,所以眼睛、水滴這類面積小但顏色獨特的不會被吃掉。
- 異色:用同樣的幾何渲染另一組配色,在同一個像素位置讀出顏色,所以兩組調色盤的索引完全一致。
- 背面圖拍的是面具內側(漆面加綁繩孔),這是面具角色獨有的特色。

`proto_mask.py` 是最早的流程原型(Workbench),留作參考。
