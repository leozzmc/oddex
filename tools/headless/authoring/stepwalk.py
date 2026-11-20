"""Walk where autopilot.py's static planner cannot, replanning after every unit.

usage: stepwalk.py START.ss OUT_PREFIX MAP X Y [--live] [--avoid x,y;x,y...]

default  BFS on map data across warps and ledges: a warp is taken only where its tile has a warp
         behavior (doors, ladders, holes; the Lavaridge Gym's holes and geysers are one-way), ledges
         only downhill. Walks the maps of the start's and the goal's areas (named alike up to the
         first "_": LavaridgeTown, its houses, LavaridgeTown_Gym_1F and _B1F); no map connections. An exit mat (arrow warp) is stepped on, then pushed again.
         One step per unit (trainers interrupt).
--live   BFS on the running game's collision grid of the current map (gBackupMapLayout) with the
         objects where they stand now: hidden objects that map.json still lists, setmetatile
         barriers (the Mauville Gym) and trainers who walked over after a battle are all right.
         Floor switches and the like can be avoided with --avoid. One straight leg per unit.
Battles and messages go through autopilot's battle_press (B outside battle). Prints the commands
and "# end <where> facing <dir> state <ss>" like autopilot.py.
"""
import os, sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ARGV, sys.argv = sys.argv[1:], [os.path.join(HERE, "autopilot.py")]
G = {"__file__": sys.argv[0], "__name__": "stepwalk"}
with open(sys.argv[0]) as f:
    exec(compile(f.read().replace("\nmain()\n", "\n"), sys.argv[0], "exec"), G)
W, SYMS, DIRS = G["W"], G["SYMS"], G["DIRS"]
OFF = 7  # gBackupMapLayout's border around the map
ARROW = {"EAST": "RIGHT", "WEST": "LEFT", "NORTH": "UP", "SOUTH": "DOWN"}


def bfs(start, goal, neighbors):
    """Directions from start to goal; neighbors(state) yields (direction, next_state)."""
    prev, q = {start: None}, deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for d, nxt in neighbors(cur):
            if nxt not in prev:
                prev[nxt] = (cur, d)
                q.append(nxt)
    if goal not in prev:
        return None
    out, k = [], goal
    while prev[k]:
        k, d = prev[k]
        out.append(d)
    return out[::-1]


def is_warp(beh):
    """Tiles that warp when stepped on or pushed, like field_control_avatar.c's IsWarpMetatileBehavior."""
    return any(k in beh for k in ("WARP", "DOOR", "LADDER", "ESCALATOR", "HOLE"))


def warp_neighbors(maps):
    """Steps on map data: collision, map.json objects, ledges, warps into `maps` (marked '|')."""
    def warps(mp):
        m = G["load"](mp)
        return {(w["x"], w["y"]): w for w in m["json"]["warp_events"] if is_warp(G["cell"](m, w["x"], w["y"])[2])}

    def through(mp, w, d):
        dest = G["ID2NAME"][w["dest_map"]]
        dw = G["load"](dest)["json"]["warp_events"][int(w["dest_warp_id"])]
        return d + "|", (dest, dw["x"], dw["y"])

    def neighbors(cur):
        mp, x, y = cur
        m = G["load"](mp)
        w = warps(mp).get((x, y))
        beh = G["cell"](m, x, y)[2]
        if w and "ARROW" in beh and G["ID2NAME"].get(w["dest_map"]) in maps:
            # An exit mat warps only when pushed again while standing on it.
            yield through(mp, w, ARROW[beh.split("_")[-3]])
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < m["W"] and 0 <= ny < m["H"]) or (nx, ny) in m["objs"]:
                continue
            beh = G["cell"](m, nx, ny)[2]
            if beh in G["JUMP"]:
                if G["JUMP"][beh] != d:
                    continue
                nx, ny = nx + dx, ny + dy
                if (nx, ny) in m["objs"]:
                    continue
            if G["cell"](m, nx, ny)[0] and "DOOR" not in G["cell"](m, nx, ny)[2]:  # doors collide, then open
                continue
            w = warps(mp).get((nx, ny))
            if not w or "ARROW" in G["cell"](m, nx, ny)[2]:
                yield d, (mp, nx, ny)
            elif G["ID2NAME"].get(w["dest_map"]) in maps:
                yield through(mp, w, d)
    return neighbors


def live_neighbors(ss, avoid):
    """Steps on the running game's grid for the current map, with objects where they stand."""
    st = W["state"](ss)
    w, h, p = W["read"](st, SYMS["gBackupMapLayout"], "<iiI")
    blocked = set(avoid)
    for i in range(16):
        b = SYMS["gObjectEvents"] + 36 * i
        if W["read"](st, b, "<B")[0] & 1 and W["read"](st, b + 8, "<B")[0] != 255:  # active, not the player
            x, y = W["read"](st, b + 16, "<hh")
            blocked.add((x - OFF, y - OFF))

    def free(x, y):
        return 0 <= x < w - 2 * OFF and 0 <= y < h - 2 * OFF and (x, y) not in blocked \
            and not (W["read"](st, p + 2 * ((y + OFF) * w + x + OFF), "<H")[0] >> 10) & 3

    def neighbors(cur):
        mp, x, y = cur
        for d, (dx, dy) in DIRS.items():
            if free(x + dx, y + dy):
                yield d, (mp, x + dx, y + dy)
    return neighbors


def main():
    ss, prefix, goal = ARGV[0], ARGV[1], (ARGV[2], int(ARGV[3]), int(ARGV[4]))
    live = "--live" in ARGV
    avoid = []
    if "--avoid" in ARGV:
        avoid = [tuple(map(int, t.split(","))) for t in ARGV[ARGV.index("--avoid") + 1].split(";")]
    cmds, facing = [], "DOWN"
    for k in range(G["MAX_STEPS"]):
        mp, x, y, cb = G["where"](ss)
        free = cb == "CB2_Overworld" and G["controls_free"](ss)
        if (mp, x, y) == goal and free:
            break
        if not free:
            c = [G["battle_press"](ss) if cb != "CB2_Overworld" else "press B 2 30"]
        else:
            area = {goal[0].split("_")[0], mp.split("_")[0]}
            floors = {n for n in G["ID2NAME"].values() if n.split("_")[0] in area}
            nb = live_neighbors(ss, avoid) if live else warp_neighbors(floors)
            dirs = bfs((mp, x, y), goal, nb)
            if not dirs:
                raise SystemExit(f"no path {(mp, x, y)} -> {goal}")
            d = dirs[0].rstrip("|")
            n = 1 if not live else next((i for i, e in enumerate(dirs) if e != dirs[0]), len(dirs))
            # A release frame first: a new direction right after the last hold keeps walking.
            c = ["wait 2", f"hold {d} {16 * n}", "wait 120" if dirs[0].endswith("|") else "wait 4"]
            facing = d
        nxt = f"{prefix}_{k:04d}.ss"
        G["run"](ss, c, nxt)
        cmds += c
        ss = nxt
    else:
        raise SystemExit(f"step limit at {G['where'](ss)}")
    print("\n".join(G["compress"](cmds)))
    print(f"# end {G['where'](ss)} facing {facing} state {ss}", file=sys.stderr)


if __name__ == "__main__":
    main()
