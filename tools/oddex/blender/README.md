# Blender 面具渲染

用 headless Blender 以 Python 建模並渲染原創角色，再用 `tools/oddex/import_art.py` 轉成 GBA 規格。

```bash
. tools/env.sh
"$BLENDER" -b --factory-startup -P tools/oddex/blender/proto_mask.py -- /tmp/out
python3 tools/oddex/import_art.py <species_id> --front /tmp/out/front.png --back /tmp/out/back.png --out <dir>
```

- Blender 5.2.4 LTS，安裝在 `~/oddex-toolchain/Blender.app`（`$BLENDER`）。不需要開介面，也不需要外掛或 MCP。
- `proto_mask.py` 是流程原型（小面風格），渲染一次約 4 秒。造型和打光都還很粗糙，只用來證明整條流程走得通。
- 原型目前的問題：Workbench 的 STUDIO 打光會把白色的臉壓成灰色；256 px 縮到 64 px 時顏色會變混濁。可以試試 FLAT 或 Eevee 加 toon 著色、直接用 64 px 不反鋸齒渲染，搭配 outline。
- 背面圖（我方戰鬥時看到的那一面）可以直接拍面具內側：漆面加上綁繩的孔。這是面具角色才有的特色。
