"""Closed-loop route authoring for oddex-run scripts.

Executes a route one unit at a time from a savestate, reads the player's map/position/callback
after each unit, recovers (one battle press at a time: A, or B to decline forgetting a move; B when a script
message blocks movement,
replanning when off course, swapping a damaging move back into slot 1 after a level-up put a
status move there or its PP ran out), and prints
the exact command sequence that worked. Because the game is deterministic, replaying those
commands in one continuous run reproduces the same result (verified separately).

usage: autopilot.py START.ss OUT_PREFIX FACING WAYPOINT [WAYPOINT ...]
WAYPOINT = Map:x:y, or grind:Map:x1:y1:x2:y2:LEVEL to walk between two grass tiles until the lead
reaches LEVEL (stops early when its HP drops below 35% or its damaging moves have fewer than 10
PP left, so the caller can heal)
"""
import os, subprocess, sys, tempfile
from functools import lru_cache

sys.argv, ARGS = [sys.argv[0]], sys.argv[1:]
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "plan.py")).read().split('if __name__')[0])
W = {"__file__": os.path.join(HERE, "where.py")}
exec(open(os.path.join(HERE, "where.py")).read().split("S = syms()")[0], W)
SYMS = W["syms"]()
NAMES = W["map_names"]()
RUN = os.environ.get("ODDEX_RUN", os.path.expanduser("~/oddex-toolchain/bin/oddex-run"))
ROM = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "game", "pokeemerald.gba")
SETTLE = 40        # frames after each grass step for a wild battle transition to start
LOW_PP = 5         # swap slot 1 out before a battle once its PP drops below this
MAX_BATTLE_PRESSES = 600  # a battle longer than this is stuck (e.g. slot 1 out of PP mid-battle)
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


@lru_cache(None)
def move_power():
    """{move id: base power}; conditional powers take the updated (post-'?') value."""
    import re as _re
    ids = {k: v for v, k in W["move_names"]().items()}
    with open(os.path.join(os.path.dirname(ROM), "src/data/moves_info.h"), encoding="utf-8") as f:
        blocks = _re.split(r"\n\s*\[MOVE_([A-Z0-9_]+)\]\s*=", f.read())
    out = {}
    for i in range(1, len(blocks), 2):
        m = _re.search(r"\.power\s*=\s*([^,\n]+),", blocks[i + 1])
        if m and blocks[i] in ids:
            nums = _re.findall(r"\d+", m.group(1).split("?")[-1])
            out[ids[blocks[i]]] = int(nums[0]) if nums else 0
    return out


def controls_free(ss):
    """No script is running and the player's field controls are not locked (src/script.c)."""
    st = W["state"](ss)
    locked = W["read"](st, SYMS["sLockFieldControls"], "<B")[0]
    status = W["read"](st, SYMS["sGlobalScriptContextStatus"], "<B")[0]
    return not locked and status != 0  # 0 = CONTEXT_RUNNING


def slot_fix(ss):
    """Slot to swap into slot 1 when slot 1 is a status move or low on PP, else None.

    Running out of PP mid-battle would stall the A presses ("no PP left"), so slot 1 is replaced
    in the overworld once its PP drops below LOW_PP, by the strongest damaging move with more PP.
    """
    moves, pp = W["lead_moves"](W["state"](ss), SYMS)
    power = move_power()
    damaging = [(power.get(m, 0), -i, i) for i, (m, p) in enumerate(zip(moves, pp)) if m and power.get(m, 0) > 0]
    fresh = [d for d in damaging if pp[d[2]] >= LOW_PP]
    slot1_ok = power.get(moves[0], 0) > 0 and (pp[0] >= LOW_PP or not any(d[2] for d in fresh))
    if slot1_ok and pp[0] > 0:
        return None
    pick = max(fresh or [d for d in damaging if pp[d[2]] > 0], default=None)
    return None if pick is None or pick[2] == 0 else pick[2]


def fix_lead(ss, prefix, k, slot=None):
    """Open the summary and swap `slot` (default: the best damaging move) into slot 1."""
    explicit = slot is not None
    slot = slot if explicit else slot_fix(ss)
    opened = f"{prefix}_{k:04d}m.ss"
    run(ss, ["wait 60", "press START 2 40"], opened)
    st = W["state"](opened)
    n = W["read"](st, SYMS["sNumStartMenuActions"], "<B")[0]
    actions = list(W["read"](st, SYMS["sCurrentStartMenuActions"], f"<{n}B"))
    cur = W["read"](st, SYMS["sStartMenuCursorPos"], "<B")[0]
    to = actions.index(1)  # MENU_ACTION_POKEMON
    down = (to - cur) % n
    nav = [f"press DOWN 2 15"] * down if down <= n - down else [f"press UP 2 15"] * (n - down)
    cmds = ["wait 60", "press START 2 40"] + nav + [
        "press A 2 90", "press A 2 40", "press A 2 90", "press RIGHT 2 60", "press RIGHT 2 60",
        "press A 2 40"] + ["press DOWN 2 20"] * slot + ["press A 2 40"] + ["press UP 2 20"] * slot + [
        "press A 2 60", "repeat 8 press B 2 60", "wait 30"]
    out = f"{prefix}_{k:04d}f.ss"
    run(ss, cmds, out)
    moved = W["lead_moves"](W["state"](out), SYMS)[0][0] == W["lead_moves"](W["state"](ss), SYMS)[0][slot]
    if (not moved if explicit else slot_fix(out) is not None) or where(out)[3] != "CB2_Overworld" or not controls_free(out):
        # A script (e.g. a trigger stepped on this frame) took over: discard the attempt.
        print(f"# lead move fix did not take from {ss}; retrying later", file=sys.stderr)
        return None, ss
    print(f"# moved slot {slot + 1} to slot 1: {W['lead_moves'](W['state'](out), SYMS)}", file=sys.stderr)
    return cmds, out


def battle_press(ss):
    """Next single input in battle: B at "delete a move?", cursor moves away from a slot with no
    PP in the move menu, otherwise A (fight with the selected move)."""
    st = W["state"](ss)
    instr = W["read"](st, SYMS["gBattlescriptCurrInstr"], "<I")[0]
    if SYMS["BattleScript_AskToLearnMove"] <= instr < SYMS["BattleScript_ForgotAndLearnedNewMove"]:
        return "press B 2 30"
    func = W["read"](st, SYMS["gBattlerControllerFuncs"], "<I")[0] & ~1
    if func == SYMS["HandleInputChooseMove"]:
        moves, pp = W["lead_moves"](st, SYMS)
        power = move_power()
        cur = W["read"](st, SYMS["gMoveSelectionCursor"], "<B")[0] & 3
        if not (pp[cur] and power.get(moves[cur], 0) > 0):
            usable = [(power.get(m, 0), i) for i, (m, p) in enumerate(zip(moves, pp)) if m and p and power.get(m, 0) > 0]
            if usable:
                to = max(usable)[1]
                if to % 2 != cur % 2:
                    return "press RIGHT 2 20" if to % 2 else "press LEFT 2 20"
                return "press DOWN 2 20" if to // 2 else "press UP 2 20"
    return "press A 2 30"


def first_step(cmds, pos):
    """(map, x, y) of the first tile a movement unit walks onto."""
    for c in cmds:
        if c.startswith("hold "):
            return step(pos[0], pos[1], pos[2], c.split()[1])
    return None


def compress(cmds):
    """Fold runs of identical commands into `repeat N <cmd>` (same frames, shorter script)."""
    out = []
    for c in cmds:
        if out and out[-1][0] == c and not c.startswith("repeat"):
            out[-1][1] += 1
        else:
            out.append([c, 1])
    return [c if n == 1 else f"repeat {n} {c}" for c, n in out]


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
        cmds.append(f"wait {SETTLE}")
    return cmds, pos, d, grassy


def main():
    ss, prefix, facing = ARGS[0], ARGS[1], ARGS[2]
    goals = []
    for w in ARGS[3:]:
        parts = w.split(":")
        if parts[0] == "grind":  # grind:Map:x1:y1:x2:y2:level -> walk between two grass tiles
            m, x1, y1, x2, y2, lvl = parts[1], *map(int, parts[2:])
            goals.append(("grind", (m, x1, y1), (m, x2, y2), lvl))
        else:
            goals.append((parts[0], int(parts[1]), int(parts[2])))
    out, k, stopped, stuck, presses, cooldown = [], 0, True, False, 0, 0
    blocked_once = {}
    for spec in goals:
        tries = 0
        grind = spec[0] == "grind"
        goal = spec[1] if grind else spec
        while True:
            name, x, y, cb = where(ss)
            if grind and cb == "CB2_Overworld" and not stuck and controls_free(ss):
                st = W["state"](ss)
                lvl = W["read"](st, SYMS["gParties"] + 84, "<B")[0]
                hp, mhp = W["read"](st, SYMS["gParties"] + 86, "<HH")
                if lvl >= spec[3]:
                    break
                moves, pp = W["lead_moves"](st, SYMS)
                attack_pp = sum(p for m, p in zip(moves, pp) if move_power().get(m, 0) > 0)
                if hp * 100 < mhp * 35 or attack_pp < 10:
                    print(f"# grind paused: HP {hp}/{mhp}, attack PP {attack_pp} at Lv{lvl}; heal and resume", file=sys.stderr)
                    break
                if (name, x, y) == goal:
                    goal = spec[2] if goal == spec[1] else spec[1]
            if cb != "CB2_Overworld":
                # One press at a time in battle: A fights with move slot 1, but at "delete a move
                # to make room?" A would answer YES and forget slot 1, so B (NO) is pressed there.
                cmds, exp = [battle_press(ss)], None
                presses += 1
                if presses > MAX_BATTLE_PRESSES:
                    raise SystemExit(f"battle did not end after {MAX_BATTLE_PRESSES} presses ({ss}); "
                                     f"lead: {W['lead_moves'](W['state'](ss), SYMS)}")
            elif stuck:
                # Not in battle but the last move went nowhere: a script message is probably
                # open. B advances it, answers NO to prompts and never starts a new interaction.
                cmds, exp, stopped = [f"repeat {DIALOG_B} press B 2 30"], None, True
                stuck = False
            elif (presses := 0) or (cooldown == 0 and controls_free(ss) and slot_fix(ss) is not None):
                # Slot 1 is a status move or low on PP: A presses would stall the next battle,
                # so put a damaging move with PP into slot 1 first.
                cmds, fixed = fix_lead(ss, prefix, k)
                k += 1
                if cmds:
                    out += cmds
                    ss = fixed
                    stopped = True
                else:
                    cooldown = 3
                continue
            elif (name, x, y) == goal and not grind:
                break
            elif (name, x, y) == goal:
                cmds, exp = ["wait 30"], None  # grinding: wait until controls are free to toggle
            else:
                u = units((name, x, y), goal, facing, stopped)
                cmds, exp, facing, stopped = u
            cooldown = max(0, cooldown - 1)
            nxt = f"{prefix}_{k:04d}.ss"
            run(ss, cmds, nxt)
            k += 1
            out += cmds
            ss = nxt
            got = where(ss)
            stuck = bool(exp) and got[:3] == (name, x, y) and got[3] == "CB2_Overworld"
            grind_tiles = {spec[1], spec[2]} if grind else set()
            if stuck and first_step(cmds, (name, x, y)) in grind_tiles:
                pass  # never block the grinding tiles themselves; B and retries clear the way
            elif stuck and blocked_once.get((name, x, y)) == first_step(cmds, (name, x, y)):
                # Second time this exact step went nowhere, after B already cleared any message:
                # something (e.g. a trainer who walked over after a battle) stands there now.
                EXTRA_BLOCKED.add(first_step(cmds, (name, x, y)))
                print(f"# treating {first_step(cmds, (name, x, y))} as blocked", file=sys.stderr)
                stuck = False
            elif stuck:
                blocked_once[(name, x, y)] = first_step(cmds, (name, x, y))
            if exp and got[:3] != exp and got[3] == "CB2_Overworld":
                tries += 1
                stopped = True
                print(f"# off course: expected {exp}, got {got}", file=sys.stderr)
                if tries > 20:
                    raise SystemExit("giving up")
    print("\n".join(compress(out)))
    print(f"# end {where(ss)} facing {facing} state {ss}", file=sys.stderr)


main()
