"""Plan a walking path across connected maps and print oddex-run hold commands.

usage: plan.py MAP X Y GOAL_MAP GX GY [--grass] [--avoid-sight] [--mash N --face DIR]
Minimizes tall-grass steps (forbidden unless --grass or --mash); --avoid-sight penalizes trainer
sight lines. --mash N emits each grass step as its own hold followed by N A presses, with a short
tap to turn first whenever the player has stopped and must change direction (--face = start facing).
"""
import heapq, json, os, re, struct, sys
from collections import deque

G = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")), "game")
enum = re.findall(r"^\s*(MB_[A-Z0-9_]+)", open(f"{G}/include/constants/metatile_behaviors.h").read(), re.M)
LAYOUTS = {l["id"]: l for l in json.load(open(f"{G}/data/layouts/layouts.json"))["layouts"] if "id" in l}
ID2NAME = {}
for f in __import__("glob").glob(f"{G}/data/maps/*/map.json"):
    j = json.load(open(f))
    ID2NAME[j["id"]] = j["name"]
DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
JUMP = {"MB_JUMP_EAST": "RIGHT", "MB_JUMP_WEST": "LEFT", "MB_JUMP_NORTH": "UP", "MB_JUMP_SOUTH": "DOWN"}
WATER = ("WATER", "OCEAN", "WATERFALL", "CURRENT")
_cache = {}


def is_water(beh):
    """Needs Surf. MB_BRIDGE_OVER_OCEAN (Route 110's wooden bridges) is walkable despite its name."""
    return any(w in beh for w in WATER) and "BRIDGE" not in beh


def ts_attr(sym, primary):
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", sym.replace("gTileset_", "")).lower()
    return open(f"{G}/data/tilesets/{'primary' if primary else 'secondary'}/{name}/metatile_attributes.bin", "rb").read()


def load(name):
    if name in _cache:
        return _cache[name]
    mj = json.load(open(f"{G}/data/maps/{name}/map.json"))
    lay = LAYOUTS[mj["layout"]]
    m = {
        "json": mj, "W": lay["width"], "H": lay["height"],
        "blk": open(f"{G}/" + lay["blockdata_filepath"], "rb").read(),
        "pa": ts_attr(lay["primary_tileset"], True), "sa": ts_attr(lay["secondary_tileset"], False),
        "objs": {(o["x"], o["y"]): o for o in mj.get("object_events", [])},
        "conn": mj.get("connections") or [],  # a side can have several (Route 111's left: 113 and 112)
    }
    _cache[name] = m
    return m


def cell(m, x, y):
    v = struct.unpack_from("<H", m["blk"], 2 * (y * m["W"] + x))[0]
    mt = v & 0x3FF
    data, i = (m["pa"], mt) if mt < 512 else (m["sa"], mt - 512)
    beh = enum[struct.unpack_from("<H", data, 2 * i)[0] & 0xFF]
    return (v >> 10) & 3, v >> 12, beh


def sight(m):
    seen = set()
    for (x, y), o in m["objs"].items():
        if o.get("trainer_type", "TRAINER_TYPE_NONE") == "TRAINER_TYPE_NONE":
            continue
        r = int(o.get("trainer_sight_or_berry_tree_id", "0") or 0)
        mv = o["movement_type"]
        dirs = [d for d, k in (("UP", "UP"), ("DOWN", "DOWN"), ("LEFT", "LEFT"), ("RIGHT", "RIGHT")) if k in mv]
        if not dirs or "LOOK_AROUND" in mv or "ROTATE" in mv or "WANDER" in mv:
            dirs = list(DIRS)
        for d in dirs:
            dx, dy = DIRS[d]
            for k in range(1, r + 1):
                seen.add((x + dx * k, y + dy * k))
    return seen


def step(name, x, y, d):
    """Return (name, x, y) after moving one tile, crossing connections; None if leaving with no
    connection, or past the end of a narrower neighbor."""
    m = load(name)
    dx, dy = DIRS[d]
    nx, ny = x + dx, y + dy
    if 0 <= nx < m["W"] and 0 <= ny < m["H"]:
        return name, nx, ny
    for c in m["conn"]:
        if c["direction"] != d.lower():
            continue
        other = ID2NAME[c["map"]]
        o = load(other)
        off = int(c["offset"])
        ox, oy = {"UP": (nx - off, o["H"] - 1), "DOWN": (nx - off, 0),
                  "LEFT": (o["W"] - 1, ny - off), "RIGHT": (0, ny - off)}[d]
        if 0 <= ox < o["W"] and 0 <= oy < o["H"]:
            return other, ox, oy
    return None


# (map, x, y) tiles found blocked at authoring time, e.g. a trainer who walked over after a battle.
EXTRA_BLOCKED = set()


def plan(start, goal, grass=False, avoid_sight=False, want_steps=False):
    sights = {}
    prev = {start: None}
    dist = {start: 0}
    pq = [(0, start)]
    while pq:
        cost, cur = heapq.heappop(pq)
        if cur == goal:
            break
        if cost > dist[cur]:
            continue
        name, x, y = cur
        el = cell(load(name), x, y)[1]
        for d in DIRS:
            nxt = step(name, x, y, d)
            if not nxt:
                continue
            nn, nx, ny = nxt
            m = load(nn)
            if not (0 <= nx < m["W"] and 0 <= ny < m["H"]) or (nx, ny) in m["objs"] or (nn, nx, ny) in EXTRA_BLOCKED:
                continue
            col, nel, beh = cell(m, nx, ny)
            if beh in JUMP:
                if JUMP[beh] != d:
                    continue
                nxt = step(nn, nx, ny, d)
                if not nxt:
                    continue
                nn, nx, ny = nxt
                m = load(nn)
                col, nel, beh = cell(m, nx, ny)
            elif not (el == nel or el in (0, 15) or nel in (0, 15)):
                continue
            if col or is_water(beh):
                continue
            c = 1
            if "GRASS" in beh:
                if not grass:
                    continue
                c = 100
            if avoid_sight:
                if nn not in sights:
                    sights[nn] = sight(load(nn))
                if (nx, ny) in sights[nn]:
                    c += 1000
            key = (nn, nx, ny)
            if key not in dist or cost + c < dist[key]:
                dist[key] = cost + c
                prev[key] = (cur, d)
                heapq.heappush(pq, (cost + c, key))
    if goal not in prev:
        raise SystemExit(f"no path {start} -> {goal}")
    dirs = []
    k = goal
    while prev[k]:
        nxt = k
        k, d = prev[k]
        dirs.append((d, "GRASS" in cell(load(nxt[0]), nxt[1], nxt[2])[2]))
    dirs.reverse()
    if want_steps:
        return dirs
    dirs = [d for d, _ in dirs]
    out = []
    for d in dirs:
        if out and out[-1][0] == d:
            out[-1][1] += 1
        else:
            out.append([d, 1])
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    s = (a[0], int(a[1]), int(a[2]))
    g = (a[3], int(a[4]), int(a[5]))
    mash = int(a[a.index("--mash") + 1]) if "--mash" in a else 0
    if not mash:
        for d, n in plan(s, g, "--grass" in a, "--avoid-sight" in a):
            print(f"hold {d} {16 * n}")
        sys.exit()
    # Each step onto grass is its own hold followed by an A run: it fights any wild
    # encounter with the first move and does nothing in the overworld (facing open grass).
    # After an A run the player stands still; turning from a standstill can eat a 16-frame
    # hold, so a short tap turns first whenever the direction changes.
    facing = a[a.index("--face") + 1] if "--face" in a else None
    stopped = True
    run = []
    for d, grassy in plan(s, g, True, "--avoid-sight" in a, want_steps=True):
        if run and (grassy or run[0] != d):
            print(f"hold {run[0]} {16 * len(run)}")
            run = []
        if stopped and d != facing:
            print(f"press {d} 3 20")
        if grassy:
            print(f"hold {d} 16")
            print(f"repeat {mash} press A 2 30")
            stopped = True
        else:
            run.append(d)
            stopped = False
        facing = d
    if run:
        print(f"hold {run[0]} {16 * len(run)}")
