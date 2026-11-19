#!/usr/bin/env python3
"""Static map checks and previews for oddex (read-only).

  check_maps.py                    check every Emerald (Hoenn) map; exit 1 on errors
  check_maps.py --maps A,B         check only maps whose name starts with these prefixes
  check_maps.py --render MAP [-o OUT.png]   draw a map with collision/object/warp/trigger overlays

Checks: map size limit, connection reciprocity, warp destinations, object event count, region
(non-Hoenn maps are silently dropped from the Emerald build), event coordinates in bounds, and
object events standing on tiles whose top metatile layer is drawn over sprites.
Findings already present in vanilla are accepted in tools/oddex/check_maps_baseline.json;
only new findings fail (rerun with --update-baseline after reviewing them).
"""
import argparse, glob, json, os, re, struct, sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
GAME = os.path.join(ROOT, "game")
MAX_MAP_DATA_SIZE = 10240          # include/fieldmap.h
MAP_OFFSET_W, MAP_OFFSET_H = 15, 14
NUM_METATILES_IN_PRIMARY = 512
NUM_TILES_IN_PRIMARY = 512
OBJECT_EVENT_TEMPLATES_COUNT = 64  # include/constants/global.h
LAYER_NORMAL, LAYER_COVERED, LAYER_SPLIT = 0, 1, 2
# An object is reported when this share of its tile's top layer is opaque and drawn over sprites at
# its elevation. Vanilla puts objects under umbrellas, trees and bridges on purpose, so existing
# findings live in check_maps_baseline.json and only new ones fail.
OCCLUDED_RATIO = 0.5


def g(path):
    return os.path.join(GAME, path)


@lru_cache(None)
def tileset_sources():
    """Map tileset symbol -> {tiles, palettes[], metatiles, attributes} file paths."""
    incs = {}
    for f in ["src/graphics.c", "src/data/tilesets/graphics.h", "src/data/tilesets/metatiles.h"]:
        text = open(g(f), encoding="utf-8").read()
        for m in re.finditer(r"\b(g(?:TilesetTiles|TilesetPalettes|Metatiles|MetatileAttributes)_\w+)\s*(?:\[\d*\])+\s*=\s*(.*?);", text, re.S):
            incs[m.group(1)] = re.findall(r'"(data/[^"]+)"', m.group(2))
    out = {}
    headers = open(g("src/data/tilesets/headers.h"), encoding="utf-8").read()
    for m in re.finditer(r"const struct Tileset (gTileset_\w+)\s*=\s*\{(.*?)\};", headers, re.S):
        fields = dict(re.findall(r"\.(\w+)\s*=\s*(\w+)", m.group(2)))
        out[m.group(1)] = {
            "tiles": (incs.get(fields.get("tiles"), [None]) or [None])[0],
            "palettes": incs.get(fields.get("palettes"), []),
            "metatiles": (incs.get(fields.get("metatiles"), [None]) or [None])[0],
            "attributes": (incs.get(fields.get("metatileAttributes"), [None]) or [None])[0],
        }
    return out


def read_pal(path):
    lines = open(g(path)).read().split()
    vals = [int(v) for v in lines[3:3 + 48]]
    return [tuple(vals[i:i + 3]) for i in range(0, 48, 3)]


@lru_cache(None)
def tileset(sym):
    src = tileset_sources()[sym]
    tiles = Image.open(g(src["tiles"])) if src["tiles"] else None
    return {
        "tiles": tiles,
        "pals": [read_pal(p) for p in src["palettes"]],
        "metatiles": open(g(src["metatiles"]), "rb").read(),
        "attrs": open(g(src["attributes"]), "rb").read(),
    }


class Layout:
    def __init__(self, lay):
        self.id, self.w, self.h = lay["id"], lay["width"], lay["height"]
        self.blk = open(g(lay["blockdata_filepath"]), "rb").read()
        self.primary, self.secondary = tileset(lay["primary_tileset"]), tileset(lay["secondary_tileset"])

    def cell(self, x, y):
        v = struct.unpack_from("<H", self.blk, 2 * (y * self.w + x))[0]
        return v & 0x3FF, (v >> 10) & 3, v >> 12

    def meta(self, mt):
        ts, i = (self.primary, mt) if mt < NUM_METATILES_IN_PRIMARY else (self.secondary, mt - NUM_METATILES_IN_PRIMARY)
        if 16 * i + 16 > len(ts["metatiles"]):
            return None, 0
        entries = struct.unpack_from("<8H", ts["metatiles"], 16 * i)
        attr = struct.unpack_from("<H", ts["attrs"], 2 * i)[0] if 2 * i + 2 <= len(ts["attrs"]) else 0
        return entries, attr

    def _tile_pixels(self, e):
        idx, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        ts, n = (self.primary, idx) if idx < NUM_TILES_IN_PRIMARY else (self.secondary, idx - NUM_TILES_IN_PRIMARY)
        img = ts["tiles"]
        cols = img.width // 8
        if n >= cols * (img.height // 8):
            return None, pal
        px = [[img.getpixel(((n % cols) * 8 + x, (n // cols) * 8 + y)) & 0xF for x in range(8)] for y in range(8)]
        if hf:
            px = [row[::-1] for row in px]
        if vf:
            px = px[::-1]
        return px, pal

    @lru_cache(None)
    def top_coverage(self, mt):
        """Share of the 16x16 metatile covered by top-layer pixels drawn above sprites."""
        entries, attr = self.meta(mt)
        if entries is None or (attr >> 12) == LAYER_COVERED:
            return 0.0
        opaque = 0
        for e in entries[4:]:
            px, _ = self._tile_pixels(e)
            if px:
                opaque += sum(1 for row in px for c in row if c)
        return opaque / 256

    def _pal(self, slot):
        src = self.primary if slot < 6 else self.secondary
        return src["pals"][slot] if slot < len(src["pals"]) else [(255, 0, 255)] * 16

    @lru_cache(None)
    def render_metatile(self, mt):
        """Bottom layer then top layer over the backdrop (palette 0, color 0); index 0 is transparent."""
        im = Image.new("RGB", (16, 16), self._pal(0)[0])
        entries, _ = self.meta(mt)
        if entries is None:
            return im
        for k, e in enumerate(entries):
            px, pal = self._tile_pixels(e)
            if not px:
                continue
            colors = self._pal(pal)
            ox, oy = (k % 2) * 8, ((k % 4) // 2) * 8
            for y in range(8):
                for x in range(8):
                    if px[y][x]:
                        im.putpixel((ox + x, oy + y), colors[px[y][x]])
        return im


@lru_cache(None)
def layouts():
    return {l["id"]: l for l in json.load(open(g("data/layouts/layouts.json")))["layouts"] if "id" in l}


@lru_cache(None)
def layout(lid):
    return Layout(layouts()[lid])


def load_maps():
    maps = {}
    for f in sorted(glob.glob(g("data/maps/*/map.json"))):
        j = json.load(open(f, encoding="utf-8"))
        j["_path"] = os.path.relpath(f, ROOT)
        maps[j["id"]] = j
    return maps


# Sprite priority by elevation (src/event_object_movement.c sElevationToPriority). Priority 2
# draws below BG1, where NORMAL/SPLIT metatiles put their top layer.
ELEVATION_TO_PRIORITY = [2, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 0, 2]
BASELINE_PATH = os.path.join(ROOT, "tools", "oddex", "check_maps_baseline.json")
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


def is_emerald_map(j):
    return not j["name"].endswith("_Frlg") and j.get("region") in (None, "", "REGION_HOENN")


def check(maps, prefixes):
    errors = []
    names = {j["id"]: j["name"] for j in maps.values()}

    def selected(j):
        return not prefixes or any(j["name"] == p or j["name"].startswith(p + "_") for p in prefixes)

    for mid, j in sorted(maps.items(), key=lambda kv: kv[1]["name"]):
        if j["name"].endswith("_Frlg"):
            continue
        if not selected(j):
            continue
        where = j["_path"]
        if j.get("region") not in (None, "", "REGION_HOENN"):
            errors.append(f"{where}: region {j['region']} is not REGION_HOENN; mapjson drops it from the Emerald build")
            continue
        lid = j.get("layout")
        if lid not in layouts():
            errors.append(f"{where}: unknown layout {lid}")
            continue
        lay = layout(lid)
        if (lay.w + MAP_OFFSET_W) * (lay.h + MAP_OFFSET_H) > MAX_MAP_DATA_SIZE:
            errors.append(f"{where}: {lay.w}x{lay.h} exceeds (w+15)*(h+14) <= {MAX_MAP_DATA_SIZE}; the map will not load")
        objs = j.get("object_events") or []
        if len(objs) > OBJECT_EVENT_TEMPLATES_COUNT:
            errors.append(f"{where}: {len(objs)} object events > {OBJECT_EVENT_TEMPLATES_COUNT}")
        for kind in ("object_events", "warp_events", "coord_events", "bg_events"):
            for i, e in enumerate(j.get(kind) or []):
                if "x" in e and not (0 <= e["x"] < lay.w and 0 <= e["y"] < lay.h):
                    errors.append(f"{where}: {kind}[{i}] at ({e['x']},{e['y']}) is outside {lay.w}x{lay.h}")
        for c in j.get("connections") or []:
            if c["direction"] not in OPPOSITE:
                continue
            other = maps.get(c["map"])
            if not other:
                errors.append(f"{where}: connection to unknown map {c['map']}")
                continue
            back = [d for d in other.get("connections") or [] if d["map"] == mid and d["direction"] == OPPOSITE[c["direction"]]]
            if not back:
                errors.append(f"{where}: connection {c['direction']} to {other['name']} has no {OPPOSITE[c['direction']]} connection back")
            elif int(back[0]["offset"]) != -int(c["offset"]):
                errors.append(f"{where}: connection offset {c['offset']} to {other['name']} is not the negation of {back[0]['offset']}")
        for i, w in enumerate(j.get("warp_events") or []):
            dest = maps.get(w["dest_map"])
            if w["dest_map"] in ("MAP_DYNAMIC", "MAP_NONE"):
                continue
            if not dest:
                errors.append(f"{where}: warp_events[{i}] goes to unknown map {w['dest_map']}")
                continue
            n = len(dest.get("warp_events") or [])
            wid = int(w["dest_warp_id"]) if str(w["dest_warp_id"]).lstrip("-").isdigit() else None
            if wid is not None and not 0 <= wid < n:
                errors.append(f"{where}: warp_events[{i}] dest_warp_id {wid} but {dest['name']} has {n} warps")
        for o in objs:
            x, y = o["x"], o["y"]
            if not (0 <= x < lay.w and 0 <= y < lay.h):
                continue
            if ELEVATION_TO_PRIORITY[int(o["elevation"]) & 0xF] != 2:
                continue
            cov = lay.top_coverage(lay.cell(x, y)[0])
            if cov >= OCCLUDED_RATIO:
                errors.append(f"{where}: {o['graphics_id']} at ({x},{y}) stands under a top layer "
                              f"({cov:.0%} of the tile is drawn over sprites at elevation {o['elevation']})")
    return errors


def render(j, out):
    lay = layout(j["layout"])
    s = 16
    im = Image.new("RGB", (lay.w * s, lay.h * s))
    for y in range(lay.h):
        for x in range(lay.w):
            im.paste(lay.render_metatile(lay.cell(x, y)[0]), (x * s, y * s))
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(lay.h):
        for x in range(lay.w):
            mt, col, el = lay.cell(x, y)
            if col:
                d.rectangle([x * s, y * s, x * s + s - 1, y * s + s - 1], fill=(255, 0, 0, 70))
    for e in j.get("coord_events") or []:
        d.rectangle([e["x"] * s + 2, e["y"] * s + 2, e["x"] * s + s - 3, e["y"] * s + s - 3], outline=(255, 160, 0, 255))
    for e in j.get("bg_events") or []:
        d.rectangle([e["x"] * s + 5, e["y"] * s + 5, e["x"] * s + s - 6, e["y"] * s + s - 6], fill=(0, 160, 255, 220))
    for i, w in enumerate(j.get("warp_events") or []):
        d.rectangle([w["x"] * s, w["y"] * s, w["x"] * s + s - 1, w["y"] * s + s - 1], outline=(160, 0, 255, 255), width=2)
        d.text((w["x"] * s + 2, w["y"] * s + 2), str(i), fill=(160, 0, 255, 255))
    for i, o in enumerate(j.get("object_events") or []):
        x, y = o["x"] * s, o["y"] * s
        hidden = lay.top_coverage(lay.cell(o["x"], o["y"])[0]) >= OCCLUDED_RATIO and ELEVATION_TO_PRIORITY[int(o["elevation"]) & 0xF] == 2
        d.ellipse([x + 2, y + 2, x + s - 3, y + s - 3], outline=(255, 0, 0, 255) if hidden else (0, 255, 0, 255), width=2)
        d.text((x + 4, y + 3), str(i + 1), fill=(255, 255, 255, 255))
    im = Image.alpha_composite(im.convert("RGBA"), ov)
    im.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--maps", help="comma-separated map name prefixes to check")
    ap.add_argument("--render", metavar="MAP", help="draw MAP (name from map.json) to a PNG")
    ap.add_argument("-o", "--out", help="PNG path for --render (default game/build/maps/<MAP>.png)")
    ap.add_argument("--update-baseline", action="store_true",
                    help="accept every current finding (only after reviewing each new one, e.g. in a screenshot)")
    args = ap.parse_args()
    maps = load_maps()
    if args.render:
        j = next((m for m in maps.values() if m["name"] == args.render), None)
        if not j:
            sys.exit(f"unknown map {args.render}")
        out = args.out or g(f"build/maps/{args.render}.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        render(j, out)
        print(out)
        return
    baseline = set(json.load(open(BASELINE_PATH))) if os.path.exists(BASELINE_PATH) else set()
    prefixes = [p for p in (args.maps or "").split(",") if p]
    findings = check(maps, prefixes)
    if args.update_baseline:
        keep = sorted(set(findings) | (baseline if prefixes else set()))
        with open(BASELINE_PATH, "w") as f:
            json.dump(keep, f, indent=1)
            f.write("\n")
        print(f"{len(keep)} accepted findings in {os.path.relpath(BASELINE_PATH, ROOT)}")
        return
    new = [e for e in findings if e not in baseline]
    for e in new:
        print(e)
    checked = sum(1 for j in maps.values() if not j["name"].endswith("_Frlg") and (not prefixes or any(j["name"] == p or j["name"].startswith(p + "_") for p in prefixes)))
    print(f"check_maps: {checked} maps, {len(new)} new findings ({len(findings) - len(new)} accepted in "
          f"{os.path.relpath(BASELINE_PATH, ROOT)})")
    sys.exit(1 if new else 0)


if __name__ == "__main__":
    main()
