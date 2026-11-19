"""Closed-loop route authoring for oddex-run scripts.

Executes a route one unit at a time from a savestate, reads the player's map/position/callback
after each unit, recovers (extra A runs while in battle, replanning when off course), and prints
the exact command sequence that worked. Because the game is deterministic, replaying those
commands in one continuous run reproduces the same result (verified separately).

usage: autopilot.py START.ss OUT_PREFIX FACING WAYPOINT [WAYPOINT ...]
WAYPOINT = Map:x:y
"""
import os, subprocess, sys, tempfile

sys.argv, ARGS = [sys.argv[0]], sys.argv[1:]
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "plan.py")).read().split('if __name__')[0])
W = {"__file__": os.path.join(HERE, "where.py")}
exec(open(os.path.join(HERE, "where.py")).read().split("S = syms()")[0], W)
SYMS = W["syms"]()
NAMES = W["map_names"]()
RUN = os.environ.get("ODDEX_RUN", os.path.expanduser("~/oddex-toolchain/bin/oddex-run"))
ROM = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "game", "pokeemerald.gba")
MASH = 60          # A presses after each grass step
BATTLE_EXTRA = 40  # extra A presses while still in battle
DIALOG_B = 15      # B presses when a move went nowhere outside battle


def run(ss_in, cmds, ss_out):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(f"load {os.path.abspath(ss_in)}\n" + "\n".join(cmds) + f"\nsave {os.path.abspath(ss_out)}\n")
    r = subprocess.run([RUN, ROM, f.name], capture_output=True, text=True)
    os.unlink(f.name)
    if "ODDEX_CRASH_SCREEN" in r.stderr:
        raise SystemExit("crash screen:\n" + r.stderr)


def where(ss):
    st = W["state"](ss)
    sb1 = W["read"](st, SYMS["gSaveBlock1Ptr"], "<I")[0]
    x, y = W["read"](st, sb1, "<hh")
    grp, num = W["read"](st, sb1 + 4, "<bb")
    cb2 = W["read"](st, SYMS["gMain"] + 4, "<I")[0] & ~1
    cb = max(((v, k) for k, v in SYMS.items() if 0 <= cb2 - v < 0x2000), default=(0, "?"))[1]
    return NAMES.get((grp, num)), x, y, cb


def units(start, goal, facing, stopped):
    """First executable unit of the planned route: (cmds, expected_end, new_facing, stopped_after)."""
    steps = plan(start, goal, True, bool(os.environ.get("AVOID_SIGHT")), want_steps=True)
    if not steps:
        return None
    d, grassy = steps[0]
    cmds = []
    if stopped and d != facing:
        cmds.append(f"press {d} 3 20")
    if grassy:
        n = 1
    else:
        n = 0
        for d2, g2 in steps:
            if d2 != d or g2:
                break
            n += 1
    pos = start
    for _ in range(n):
        pos = step(pos[0], pos[1], pos[2], d)
    cmds.append(f"hold {d} {16 * n}")
    if grassy:
        cmds.append(f"repeat {MASH} press A 2 30")
    return cmds, pos, d, grassy


def main():
    ss, prefix, facing = ARGS[0], ARGS[1], ARGS[2]
    goals = [(m, int(x), int(y)) for m, x, y in (w.split(":") for w in ARGS[3:])]
    out, k, stopped, stuck = [], 0, True, False
    for goal in goals:
        tries = 0
        while True:
            name, x, y, cb = where(ss)
            if cb != "CB2_Overworld":
                cmds, exp = [f"repeat {BATTLE_EXTRA} press A 2 30"], None
            elif stuck:
                # Not in battle but the last move went nowhere: a script message is probably
                # open. B advances it, answers NO to prompts and never starts a new interaction.
                cmds, exp, stopped = [f"repeat {DIALOG_B} press B 2 30"], None, True
                stuck = False
            elif (name, x, y) == goal:
                break
            else:
                u = units((name, x, y), goal, facing, stopped)
                cmds, exp, facing, stopped = u
            nxt = f"{prefix}_{k:04d}.ss"
            run(ss, cmds, nxt)
            k += 1
            out += cmds
            ss = nxt
            got = where(ss)
            stuck = bool(exp) and got[:3] == (name, x, y) and got[3] == "CB2_Overworld"
            if exp and got[:3] != exp and got[3] == "CB2_Overworld":
                tries += 1
                stopped = True
                print(f"# off course: expected {exp}, got {got}", file=sys.stderr)
                if tries > 20:
                    raise SystemExit("giving up")
    print("\n".join(out))
    print(f"# end {where(ss)} facing {facing} state {ss}", file=sys.stderr)


main()
