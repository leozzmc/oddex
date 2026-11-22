"""Walk where autopilot.py's static planner cannot, replanning after every unit.

usage: stepwalk.py START.ss OUT_PREFIX MAP X Y [--live] [--surf] [--avoid x,y;x,y...] [--min-hp N]

default  BFS on map data across warps and ledges: a warp is taken only where its tile has a warp
         behavior (doors, ladders, holes; the Lavaridge Gym's holes and geysers are one-way), ledges
         only downhill. Walks the maps of the start's and the goal's areas (named alike up to the
         first "_": LavaridgeTown, its houses, LavaridgeTown_Gym_1F and _B1F); no map
         connections. An exit mat (arrow warp) is stepped on, then pushed again. Rotating gate
         puzzles (the Fortree Gym, Trick House puzzle 6) are planned with the gates' live
         orientations (VAR_TEMP_0..) and the rotation rules of src/rotating_gate.c. The Mossdeep
         Gym's arrow tiles are planned with the objects where they stand now: a floor switch moves
         those on arrows of its colour, the pads warp inside the gym. One step per unit (trainers
         interrupt).
         When the way is lost after some steps (a tile turned out blocked), the commands so far and
         the state they end in are still printed, with exit status 2.
--min-hp N  stop (commands so far, end state) once the lead stands free below N percent HP, so the
         caller can heal and call again.
--surf   water is walkable (waterfalls are not); stepping from land onto water uses Surf (A, YES).
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
    """Directions from start to goal (a state, or a predicate on states); neighbors(state) yields
    (direction, next_state)."""
    is_goal = goal if callable(goal) else (lambda s: s == goal)
    prev, q, end = {start: None}, deque([start]), None
    while q:
        cur = q.popleft()
        if is_goal(cur):
            end = cur
            break
        for d, nxt in neighbors(cur):
            if nxt not in prev:
                prev[nxt] = (cur, d)
                q.append(nxt)
    if end is None:
        return None
    out, k = [], end
    while prev[k]:
        k, d = prev[k]
        out.append(d)
    return out[::-1]


def is_warp(beh):
    """Tiles that warp when stepped on or pushed, like field_control_avatar.c's IsWarpMetatileBehavior."""
    return any(k in beh for k in ("WARP", "DOOR", "LADDER", "ESCALATOR", "HOLE"))


def warp_neighbors(maps, surf=False):
    """Steps on map data: collision, map.json objects, ledges, warps into `maps` (marked '|'); water
    only with surf."""
    def warps(mp):
        m = G["load"](mp)
        return {(w["x"], w["y"]): w for w in m["json"]["warp_events"]  # vanilla has warps outside their map
                if 0 <= w["x"] < m["W"] and 0 <= w["y"] < m["H"] and is_warp(G["cell"](m, w["x"], w["y"])[2])}

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
            if G["is_water"](G["cell"](m, nx, ny)[2]) and (not surf or "WATERFALL" in G["cell"](m, nx, ny)[2]):
                continue
            w = warps(mp).get((nx, ny))
            if not w or "ARROW" in G["cell"](m, nx, ny)[2]:
                yield d, (mp, nx, ny)
            elif G["ID2NAME"].get(w["dest_map"]) in maps:
                yield through(mp, w, d)
    return neighbors


# Rotating gate puzzles (src/rotating_gate.c). shortcut: the tables below are copied from that file
# (BUGFIX on: any collision blocks an arm); re-copy them if it changes. Gate positions are parsed.
GATE_MAPS = {"FortreeCity_Gym": "sRotatingGate_FortreePuzzleConfig",
             "Route110_TrickHousePuzzle6": "sRotatingGate_TrickHousePuzzleConfig"}
ACW, CW = 1, 2
def _rot(d, arm, long):
    return (d << 4) | (arm << 1) | long
_N = 255
ROT_INFO = {
    "UP": [[_N] * 4, [_rot(CW, 3, 1), _rot(CW, 3, 0), _rot(ACW, 1, 0), _rot(ACW, 1, 1)], [_N] * 4, [_N] * 4],
    "DOWN": [[_N] * 4, [_N] * 4, [_rot(ACW, 3, 1), _rot(ACW, 3, 0), _rot(CW, 1, 0), _rot(CW, 1, 1)], [_N] * 4],
    "LEFT": [[_N, _rot(ACW, 0, 1), _N, _N], [_N, _rot(ACW, 0, 0), _N, _N], [_N, _rot(CW, 2, 0), _N, _N], [_N, _rot(CW, 2, 1), _N, _N]],
    "RIGHT": [[_N, _N, _rot(CW, 0, 1), _N], [_N, _N, _rot(CW, 0, 0), _N], [_N, _N, _rot(ACW, 2, 0), _N], [_N, _N, _rot(ACW, 2, 1), _N]],
}
ARM_POS = {CW: [(0, -1), (1, -2), (0, 0), (1, 0), (-1, 0), (-1, 1), (-1, -1), (-2, -1)],
           ACW: [(-1, -1), (-1, -2), (0, -1), (1, -1), (0, 0), (0, 1), (-1, 0), (-2, 0)]}
ARM_LAYOUT = [[1, 0, 1, 0, 0, 0, 0, 0], [1, 1, 1, 0, 0, 0, 0, 0], [1, 0, 1, 1, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0, 0],
              [1, 0, 1, 0, 1, 0, 0, 0], [1, 1, 1, 0, 1, 0, 0, 0], [1, 0, 1, 1, 1, 0, 0, 0], [1, 0, 1, 0, 1, 1, 0, 0]]
SHAPES = ["L1", "L2", "L3", "L4", "T1", "T2", "T3", "T4"]
VARS_OFFSET = 5020  # offsetof(struct SaveBlock1, vars); shortcut: hard-coded, re-measure if SaveBlock1 changes


def gates(mp):
    """[(x, y, shape, orientation)] of the map's rotating gate puzzle, or []."""
    import re
    if mp not in GATE_MAPS:
        return []
    src = open(os.path.join(os.path.dirname(G["ROM"]), "src", "rotating_gate.c")).read()
    body = src[src.index(GATE_MAPS[mp]):]
    body = body[:body.index("};")]
    return [(int(x), int(y), SHAPES.index(sh), int(o) // 90) for x, y, sh, o in
            re.findall(r"\{\s*(\d+),\s*(\d+),\s*GATE_SHAPE_(\w+),\s*GATE_ORIENTATION_(\d+)\s*\}", body)]


def gate_step(m, gs, orients, d, x, y):
    """Moving `d` into (x, y): (blocked, new orientations), like CheckForRotatingGatePuzzleCollision."""
    for i, (gx, gy, shape, _) in enumerate(gs):
        if gx - 2 <= x <= gx + 1 and gy - 2 <= y <= gy + 1:
            info = ROT_INFO[d][y - gy + 2][x - gx + 2]
            if info == _N:
                continue
            rd, arm, long = info >> 4, (info & 0xF) >> 1, info & 1
            if not ARM_LAYOUT[shape][((arm - orients[i] + 4) % 4) * 2 + long]:
                continue
            for a in range(4):
                for j in range(2):
                    if ARM_LAYOUT[shape][2 * a + j]:
                        ax, ay = ARM_POS[rd][2 * ((orients[i] + a) % 4) + j]
                        if not (0 <= gx + ax < m["W"] and 0 <= gy + ay < m["H"]) or G["cell"](m, gx + ax, gy + ay)[0]:
                            return True, orients
            o = list(orients)
            o[i] = (o[i] + (1 if rd == CW else -1)) % 4
            return False, tuple(o)
    return False, orients


def gate_neighbors(mp, objs=None):
    """Steps in a rotating gate puzzle; states are (map, x, y, gate orientations). objs: tiles taken
    by objects (the live ones: a trainer walks up to the player), default map.json's."""
    m, gs = G["load"](mp), gates(mp)
    objs = m["objs"] if objs is None else objs

    def neighbors(cur):
        _, x, y, orients = cur
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < m["W"] and 0 <= ny < m["H"]) or (nx, ny) in objs or G["cell"](m, nx, ny)[0]:
                continue
            blocked, o = gate_step(m, gs, orients, d, nx, ny)
            if not blocked:
                yield d, (mp, nx, ny, o)
    return neighbors


# Arrow-tile puzzles (src/rotating_tile_puzzle.c): stepping on a floor switch moves every object that
# stands on an arrow of the switch's colour one tile along the arrow (nothing checks where it lands).
# shortcut: the colour order and the script name pattern are copied from the Mossdeep Gym; add the Trick
# House puzzle (another first metatile) when a route needs it.
TILE_PUZZLES = {"MossdeepCity_Gym": 0x250}  # METATILE_MossdeepGym_YellowArrow_Right; 8 metatiles per colour
SWITCH_COLOURS = ["Yellow", "Blue", "Green", "Purple", "Red"]
ARROWS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # right, down, left, up


def puzzle_neighbors(mp, objs=None):
    """Steps in an arrow-tile puzzle; states are (map, x, y, frozenset of object tiles). objs: the
    objects' tiles now (default map.json's). Pads warping inside the map are taken ('|'), exits are not."""
    import re, struct
    m, first = G["load"](mp), TILE_PUZZLES[mp]
    start = frozenset(m["objs"] if objs is None else objs)
    events = {(c["x"], c["y"]): c.get("script", "") for c in m["json"].get("coord_events", [])}
    switch = {t: SWITCH_COLOURS.index(c.group(1)) for t, sc in events.items()
              if (c := re.search(r"_(%s)FloorSwitch$" % "|".join(SWITCH_COLOURS), sc))}
    pads, exits = {}, set()
    for w in m["json"]["warp_events"]:
        if G["ID2NAME"].get(w["dest_map"]) == mp:
            d = m["json"]["warp_events"][int(w["dest_warp_id"])]
            pads[(w["x"], w["y"])] = (d["x"], d["y"])
        else:
            exits.add((w["x"], w["y"]))
    exits |= {t for t, sc in events.items() if t not in switch}  # e.g. the pad back to the entrance

    def press(objs, colour):
        out = set()
        for x, y in objs:
            k = (struct.unpack_from("<H", m["blk"], 2 * (y * m["W"] + x))[0] & 0x3FF) - first
            dx, dy = ARROWS[k % 8] if 0 <= k < 40 and k // 8 == colour and k % 8 < 4 else (0, 0)
            out.add((x + dx, y + dy))
        return frozenset(out)

    def neighbors(cur):
        _, x, y, objs = cur
        for d, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < m["W"] and 0 <= ny < m["H"]) or (nx, ny) in objs or (nx, ny) in exits \
                    or G["cell"](m, nx, ny)[0]:
                continue
            if (nx, ny) in pads:
                yield d + "|", (mp, *pads[(nx, ny)], objs)
            else:
                yield d, (mp, nx, ny, press(objs, switch[(nx, ny)]) if (nx, ny) in switch else objs)
    neighbors.start = start
    return neighbors


def live_objects(ss):
    """Tiles of the active objects other than the player, in map coordinates."""
    st, out = W["state"](ss), set()
    for i in range(16):
        b = SYMS["gObjectEvents"] + 36 * i
        if W["read"](st, b, "<B")[0] & 1 and W["read"](st, b + 8, "<B")[0] != 255:  # active, not the player
            x, y = W["read"](st, b + 16, "<hh")
            out.add((x - OFF, y - OFF))
    return out


TEMPLATES_OFFSET = 0xC70  # offsetof(struct SaveBlock1, objectEventTemplates); shortcut: hard-coded like VARS_OFFSET


def template_objects(ss, mp):
    """Tiles of the map's objects in the save block's templates: where the arrow-tile puzzle keeps
    them, also for the ones too far from the player to be active."""
    st = W["state"](ss)
    sb1 = W["read"](st, SYMS["gSaveBlock1Ptr"], "<I")[0]
    return {W["read"](st, sb1 + TEMPLATES_OFFSET + 24 * i + 4, "<hh")
            for i in range(len(G["load"](mp)["json"]["object_events"]))}


def live_neighbors(ss, avoid):
    """Steps on the running game's grid for the current map, with objects where they stand."""
    st = W["state"](ss)
    w, h, p = W["read"](st, SYMS["gBackupMapLayout"], "<iiI")
    blocked = set(avoid) | live_objects(ss)

    def free(x, y):
        return 0 <= x < w - 2 * OFF and 0 <= y < h - 2 * OFF and (x, y) not in blocked \
            and not (W["read"](st, p + 2 * ((y + OFF) * w + x + OFF), "<H")[0] >> 10) & 3

    def neighbors(cur):
        mp, x, y = cur
        for d, (dx, dy) in DIRS.items():
            if free(x + dx, y + dy):
                yield d, (mp, x + dx, y + dy)
    return neighbors


SURF_FRAMES = 8  # frames per tile while surfing (twice walking speed)


def surfing(ss):
    """gPlayerAvatar.flags has PLAYER_AVATAR_FLAG_SURFING (1 << 3)."""
    return bool(W["read"](W["state"](ss), SYMS["gPlayerAvatar"], "<B")[0] & 8)


def main():
    ss, prefix, goal = ARGV[0], ARGV[1], (ARGV[2], int(ARGV[3]), int(ARGV[4]))
    live, surf = "--live" in ARGV, "--surf" in ARGV
    min_hp = int(ARGV[ARGV.index("--min-hp") + 1]) if "--min-hp" in ARGV else 0
    avoid = []
    if "--avoid" in ARGV:
        avoid = [tuple(map(int, t.split(","))) for t in ARGV[ARGV.index("--avoid") + 1].split(";")]
    cmds, facing, stuck = [], "DOWN", None
    # Tiles two steps in a row did not reach (a standing NPC, a height the map data hides) are planned around.
    blocked, fails, tried = set(), {}, None
    for k in range(G["MAX_STEPS"]):
        mp, x, y, cb = G["where"](ss)
        free = cb == "CB2_Overworld" and G["controls_free"](ss)
        if (mp, x, y) == goal and free:
            break
        if free and min_hp:
            hp, mhp = W["read"](W["state"](ss), SYMS["gParties"] + 86, "<HH")
            if hp * 100 < mhp * min_hp:
                print(f"# stopped: lead HP {hp}/{mhp} below --min-hp {min_hp}; heal and resume", file=sys.stderr)
                break
        if free and tried and tried[0] == (mp, x, y):
            fails[tried[1]] = fails.get(tried[1], 0) + 1
            if fails[tried[1]] >= 2:
                blocked.add(tried[1])
        tried = None
        if not free:
            c = [G["battle_press"](ss) if cb != "CB2_Overworld" else "press B 2 30"]
        else:
            area = {goal[0].split("_")[0], mp.split("_")[0]}
            floors = {n for n in G["ID2NAME"].values() if n.split("_")[0] in area}
            if mp in GATE_MAPS and not live:
                st = W["state"](ss)
                sb1 = W["read"](st, SYMS["gSaveBlock1Ptr"], "<I")[0]
                orients = tuple(W["read"](st, sb1 + VARS_OFFSET, f"<{len(gates(mp))}B"))  # VAR_TEMP_0.. bytes
                dirs = bfs((mp, x, y, orients), lambda st_: st_[:3] == goal, gate_neighbors(mp, live_objects(ss)))
            elif mp in TILE_PUZZLES and goal[0] == mp and not live:
                objs = frozenset(template_objects(ss, mp) | live_objects(ss))
                dirs = bfs((mp, x, y, objs), lambda st_: st_[:3] == goal, puzzle_neighbors(mp, objs))
            else:
                nb = live_neighbors(ss, avoid) if live else warp_neighbors(floors, surf)
                dirs = bfs((mp, x, y), goal, lambda cur: ((d, n) for d, n in nb(cur) if n not in blocked))
            if not dirs:
                if not cmds:
                    raise SystemExit(f"no path {(mp, x, y)} -> {goal}")
                # Part of the way is walked: report it like a finished run, but fail (exit status 2).
                stuck = f"no path {(mp, x, y)} -> {goal}"
                break
            d = dirs[0].rstrip("|")
            n = 1 if not live else next((i for i, e in enumerate(dirs) if e != dirs[0]), len(dirs))
            m = G["load"](mp)
            nx, ny = x + DIRS[d][0], y + DIRS[d][1]
            tried = ((mp, x, y), (mp, nx, ny))
            onto_water = 0 <= nx < m["W"] and 0 <= ny < m["H"] and G["is_water"](G["cell"](m, nx, ny)[2])
            if surf and onto_water and not surfing(ss):
                # Face the water, A for the prompt, A for YES; the "used SURF" text is cleared by
                # the not-free branch above.
                c = ["wait 2", f"hold {d} 16", "wait 20", "press A 2 120", "press A 2 60"]
            else:
                # A release frame first: a new direction right after the last hold keeps walking.
                c = ["wait 2", f"hold {d} {(SURF_FRAMES if surfing(ss) else 16) * n}",
                     "wait 120" if dirs[0].endswith("|") else "wait 4"]
            facing = d
        nxt = f"{prefix}_{k:04d}.ss"
        G["run"](ss, c, nxt)
        cmds += c
        ss = nxt
    else:
        raise SystemExit(f"step limit at {G['where'](ss)}")
    print("\n".join(G["compress"](cmds)))
    print(f"# end {G['where'](ss)} facing {facing} state {ss}", file=sys.stderr)
    if stuck:
        print(stuck, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
