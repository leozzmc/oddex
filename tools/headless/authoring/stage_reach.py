"""Which trainers the player can meet at a story stage, for content/migration_scope.toml.

usage: stage_reach.py START_MAP X Y "MapPattern,MapPattern*,..." [--rock-smash]

Land-only BFS from a start tile across connections and warps, limited to maps matching the
patterns, without Surf, Cut or Strength (and without Rock Smash unless --rock-smash): water is
impassable and cuttable trees, boulders and breakable rocks block. A trainer counts as reachable
when a tile next to it or in its sight line is reachable. (check_maps.py's reachability is
different: it assumes every field move and only asks whether an event can ever be reached.)
"""
import fnmatch, json, os, sys
from collections import deque

sys.argv, ARGS = [sys.argv[0]], sys.argv[1:]
A = os.path.dirname(os.path.abspath(__file__))
__file__ = os.path.join(A, "plan.py")
exec(open(__file__).read().split("if __name__")[0])

start = (ARGS[0], int(ARGS[1]), int(ARGS[2]))
patterns = ARGS[3].split(",")
IDS = {}
for f in __import__("glob").glob(f"{G}/data/maps/*/map.json"):
    j = json.load(open(f))
    IDS[j["id"]] = j["name"]
names = set(IDS.values())
allowed = {n for n in names if any(fnmatch.fnmatchcase(n, p) for p in patterns)}
FIELD = ("CUTTABLE_TREE", "PUSHABLE_BOULDER") + (() if "--rock-smash" in ARGS else ("BREAKABLE_ROCK",))


def blocked_objs(m):
    return {xy for xy, o in m["objs"].items() if any(k in o["graphics_id"] for k in FIELD)}


seen = {start}
q = deque([start])
while q:
    name, x, y = q.popleft()
    m = load(name)
    col, el, beh = cell(m, x, y)
    for w in m["json"].get("warp_events") or []:
        if (w["x"], w["y"]) == (x, y) and w["dest_map"] in IDS and IDS[w["dest_map"]] in allowed:
            dm = load(IDS[w["dest_map"]])
            dws = dm["json"].get("warp_events") or []
            wid = int(w["dest_warp_id"]) if str(w["dest_warp_id"]).isdigit() else -1
            if 0 <= wid < len(dws):
                t = (IDS[w["dest_map"]], dws[wid]["x"], dws[wid]["y"])
                if t not in seen:
                    seen.add(t); q.append(t)
    for d in DIRS:
        nxt = step(name, x, y, d)
        if not nxt or nxt[0] not in allowed:
            continue
        nn, nx, ny = nxt
        mm = load(nn)
        if not (0 <= nx < mm["W"] and 0 <= ny < mm["H"]) or (nx, ny) in blocked_objs(mm):
            continue
        c2, e2, b2 = cell(mm, nx, ny)
        is_warp = any((w["x"], w["y"]) == (nx, ny) for w in mm["json"].get("warp_events") or [])
        if b2 in JUMP:
            if JUMP[b2] != d:
                continue
            nxt = step(nn, nx, ny, d)
            if not nxt:
                continue
            nn, nx, ny = nxt
            mm = load(nn)
            c2, e2, b2 = cell(mm, nx, ny)
        elif not (el == e2 or el in (0, 15) or e2 in (0, 15)):
            continue
        if (c2 and not is_warp) or is_water(b2):
            continue
        if (nn, nx, ny) not in seen:
            seen.add((nn, nx, ny)); q.append((nn, nx, ny))

reached_maps = sorted({s[0] for s in seen})
print("maps reached:", reached_maps)
for mname in reached_maps:
    m = load(mname)
    for (x, y), o in m["objs"].items():
        if o.get("trainer_type", "TRAINER_TYPE_NONE") == "TRAINER_TYPE_NONE":
            continue
        r = int(o.get("trainer_sight_or_berry_tree_id", "0") or 0)
        cand = [(x + dx, y + dy) for dx, dy in DIRS.values()]
        for dx, dy in DIRS.values():
            cand += [(x + dx * k, y + dy * k) for k in range(1, r + 1)]
        ok = any((mname, cx, cy) in seen for cx, cy in cand)
        print(f"  {'REACH' if ok else 'no   '} {mname} ({x},{y}) {o['script']}")
