"""Closed-loop route authoring for oddex-run scripts.

Executes a route one unit at a time from a savestate, reads the player's map/position/callback
after each unit, recovers (one battle press at a time: A with the cursor on the most effective move
against the opponent's types, or B to decline forgetting a move; B when a script message blocks movement,
replanning when off course, swapping a damaging move back into slot 1 after a level-up put a
status move there or its PP ran out), and prints
the exact command sequence that worked. Because the game is deterministic, replaying those
commands in one continuous run reproduces the same result (verified separately).

usage: autopilot.py START.ss OUT_PREFIX FACING WAYPOINT [WAYPOINT ...]
(AP_PARTIAL=1: when the route cannot be finished, still print the commands executed so far and
the state they end in, instead of failing)
WAYPOINT = Map:x:y, or grind:Map:x1:y1:x2:y2:LEVEL to walk between two grass tiles until the lead
reaches LEVEL (stops early when its HP drops below GRIND_MIN_HP percent, default 35, or its
damaging moves have fewer than 10 PP left, so the caller can heal). Wild battles against an
opponent whose types hit the lead super-effectively, with no super-effective move back, are fled.

Runaway guards (exit status 3, even with AP_PARTIAL, after printing the reason, the commands so
far and the last state): more than AP_MAX_STEPS units in total (default 20000), or the same
command at the same position NO_PROGRESS times in a row outside battle.
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
GRIND_MIN_HP = int(os.environ.get("GRIND_MIN_HP", "35"))  # grind pauses below this HP percent
MAX_STEPS = int(os.environ.get("AP_MAX_STEPS", "20000"))  # units per run; a real route needs far fewer
NO_PROGRESS = 100  # same command at the same position this many times in a row outside battle
LOCKED_WAITS = 3   # waits on a grind tile with controls locked before B clears the message


class Runaway(SystemExit):
    """A guard stopped a run that was making no progress."""


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
def move_info():
    """{move id: (base power, type id, is special)}; conditional powers take the updated (post-'?')
    value."""
    import re as _re
    ids = {k: v for v, k in W["move_names"]().items()}
    game = os.path.dirname(ROM)
    with open(os.path.join(game, "include/constants/pokemon.h"), encoding="utf-8") as f:
        types = {k: int(v) for k, v in _re.findall(r"\bTYPE_([A-Z]+)\s*=\s*(\d+)", f.read())}
    with open(os.path.join(game, "src/data/moves_info.h"), encoding="utf-8") as f:
        blocks = _re.split(r"\n\s*\[MOVE_([A-Z0-9_]+)\]\s*=", f.read())
    out = {}
    for i in range(1, len(blocks), 2):
        m = _re.search(r"\.power\s*=\s*([^,\n]+),", blocks[i + 1])
        # ".type = B_UPDATED_MOVE_TYPES >= GEN_2 ? TYPE_DARK : TYPE_NORMAL": the updated type comes first
        t = _re.search(r"\.type\s*=[^,\n]*?TYPE_([A-Z]+)", blocks[i + 1])
        special = "DAMAGE_CATEGORY_SPECIAL" in blocks[i + 1].split("\n\n")[0]
        if m and blocks[i] in ids:
            nums = _re.findall(r"\d+", m.group(1).split("?")[-1])
            out[ids[blocks[i]]] = (int(nums[0]) if nums else 0, types.get(t.group(1), 0) if t else 0, special)
    return out


def move_power():
    return {m: p for m, (p, _, _) in move_info().items()}


@lru_cache(None)
def type_chart():
    """gTypeEffectivenessTable[attacker][defender] as floats, read from the built ROM
    (uq4_12_t is a u32 holding a 4.12 fixed-point value, include/fpmath.h)."""
    import struct as _struct
    n = 21  # NUMBER_OF_MON_TYPES (include/constants/pokemon.h)
    with open(ROM, "rb") as f:
        f.seek(SYMS["gTypeEffectivenessTable"] - 0x08000000)
        raw = _struct.unpack(f"<{n * n}I", f.read(4 * n * n))
    return [[raw[a * n + d] / 4096 for d in range(n)] for a in range(n)]


@lru_cache(None)
def species_info_size():
    """sizeof(struct SpeciesInfo) in this build (pokemon.h's /*0xC4*/ comment is stale).
    SPECIES_BULBASAUR is 1, so its entry starts that many bytes into gSpeciesInfo: find its base
    stats (from gen_1_families.h) there, and check the size divides the table's size (nm -S)."""
    import re as _re
    src = open(os.path.join(os.path.dirname(ROM), "src/data/pokemon/species_info/gen_1_families.h")).read()
    block = src[src.index("[SPECIES_BULBASAUR]"):]
    stats = bytes(int(_re.search(r"\.%s\s*=\s*(\d+)" % k, block).group(1)) for k in
                  ("baseHP", "baseAttack", "baseDefense", "baseSpeed", "baseSpAttack", "baseSpDefense"))
    with open(ROM, "rb") as f:
        f.seek(SYMS["gSpeciesInfo"] - 0x08000000)
        head = f.read(0x400)
    hits = [s for s in range(4, len(head) - 6, 4) if head[s:s + 6] == stats]
    nm = subprocess.run([W["NM"], "-S", os.path.join(os.path.dirname(ROM), "pokeemerald.elf")],
                        capture_output=True, text=True).stdout
    total = int(_re.search(r"^\w+ (\w+) \w gSpeciesInfo$", nm, _re.M).group(1), 16)
    assert len(hits) == 1 and total % hits[0] == 0, f"sizeof(struct SpeciesInfo) not found: {hits}, {total:#x}"
    return hits[0]


def species_types(species):
    """A species' types from gSpeciesInfo in the built ROM (types, u8 x2, at +6)."""
    with open(ROM, "rb") as f:
        f.seek(SYMS["gSpeciesInfo"] - 0x08000000 + species * species_info_size() + 6)
        types = set(f.read(2))
    assert 0 not in types, f"species {species}: TYPE_NONE in gSpeciesInfo"
    return types


BATTLE_MON = 0x8C  # sizeof(struct BattlePokemon); moves at +12 (u16 x4), types at +34 (u8 x3), pp at +37
# struct BattlePokemon: attack +2, defense +4, spAttack +8, spDefense +10 (u16); statStages +24
# (s8 x8, STAT_HP/ATK/DEF/SPEED/SPATK/SPDEF/ACC/EVASION, 6 = no change).


def battle_stat(st, battler, offset, stage_index):
    """A battler's stat with its stat stage applied (2/2 .. 8/2 and 2/8 .. 2/3, as in the game)."""
    base = SYMS["gBattleMons"] + battler * BATTLE_MON
    value = W["read"](st, base + offset, "<H")[0]
    stage = W["read"](st, base + 24 + stage_index, "<b")[0] - 6
    return value * (2 + max(stage, 0)) / (2 + max(-stage, 0))


def best_move(st):
    """Slot of the move with the highest power x type effectiveness x STAB x attack/defense ratio
    (Attack against Defense for physical moves, Sp. Atk against Sp. Def for special ones, stat
    stages included) against battler 1 that still has PP, or None when nothing damaging is usable."""
    base = SYMS["gBattleMons"]
    moves = W["read"](st, base + 12, "<4H")
    own = set(W["read"](st, base + 34, "<3B")) - {0}
    pp = W["read"](st, base + 37, "<4B")
    foe = [t for t in set(W["read"](st, base + BATTLE_MON + 34, "<3B")) if t]
    ratio = {False: battle_stat(st, 0, 2, 1) / max(1, battle_stat(st, 1, 4, 2)),
             True: battle_stat(st, 0, 8, 4) / max(1, battle_stat(st, 1, 10, 5))}
    info, chart = move_info(), type_chart()
    scored = []
    for i, (m, p) in enumerate(zip(moves, pp)):
        power, t, special = info.get(m, (0, 0, False))
        if m and p and power > 0:
            eff = 1.0
            for d in foe:
                eff *= chart[t][d]
            scored.append((power * eff * (1.5 if t in own else 1.0) * ratio[special], power, -i, i))
    return max(scored)[3] if scored else None


BATTLE_TYPE_TRAINER = 1 << 3  # include/constants/battle.h


def should_flee(st):
    """Wild battle where the opponent's own types hit the lead super-effectively and no usable move
    is super-effective back (e.g. Taillow's Peck on a grass lead that only has Tackle): run."""
    if W["read"](st, SYMS["gBattleTypeFlags"], "<I")[0] & BATTLE_TYPE_TRAINER:
        return False
    base = SYMS["gBattleMons"]
    own = [t for t in set(W["read"](st, base + 34, "<3B")) if t]
    foe = [t for t in set(W["read"](st, base + BATTLE_MON + 34, "<3B")) if t]
    chart, info = type_chart(), move_info()

    def eff(t, defender):
        e = 1.0
        for d in defender:
            e *= chart[t][d]
        return e
    threat = max((eff(t, own) for t in foe), default=1.0) >= 2
    moves = W["read"](st, base + 12, "<4H")
    pp = W["read"](st, base + 37, "<4B")
    best = max((eff(info[m][1], foe) for m, p in zip(moves, pp) if m and p and info.get(m, (0, 0, False))[0] > 0),
               default=0.0)
    return threat and best < 2


@lru_cache(None)
def text_range(obj):
    """(start, end) of an object file's .text in the linker map, e.g. "battle_controller_player.o"."""
    import re as _re
    text = open(os.path.join(os.path.dirname(ROM), "pokeemerald.map"), encoding="utf-8").read()
    m = _re.search(r"\.text\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+\S*/" + _re.escape(obj), text)
    lo = int(m.group(1), 16)
    return lo, lo + int(m.group(2), 16)


@lru_cache(None)
def player_choose_action():
    """Address of battle_controller_player.c's static HandleInputChooseAction (three files define
    one; the map file gives the player controller's .text range)."""
    lo, hi = text_range("battle_controller_player.o")
    out = subprocess.run([W["NM"], os.path.join(os.path.dirname(ROM), "pokeemerald.elf")],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        p = line.split()
        if len(p) == 3 and p[2] == "HandleInputChooseAction" and lo <= int(p[0], 16) < hi:
            return int(p[0], 16)
    raise SystemExit("player HandleInputChooseAction not found")


SUMMARY_FIRST_MOVE_INDEX = 16588
COVERAGE = 1.5  # slot_to_forget: worth of a move that is the only one of its type  # offsetof(struct PokemonSummaryScreenData, firstMoveIndex)


def move_value(move, types, stats=(1, 1)):
    """Power x STAB x the lead's own Attack (physical) or Sp. Atk (special); 0 for status moves."""
    power, t, special = move_info().get(move, (0, 0, False))
    return power * (1.5 if t in types else 1.0) * stats[special]


def slot_to_forget(st):
    """Move slot to replace with gMoveToLearn, or None to decline. Moves are compared by
    move_value, times COVERAGE when the move is the lead's only damaging move of its type (for the
    new move: of a type none of the kept moves has), so a weaker move of a new type (e.g. Aerial
    Ace for a grass/dark lead facing fighting types) can replace a second move of a type that is
    already covered. The weakest current move goes first (status moves first), except the lead's
    only physical or only special damaging move when the new move is of the other category: the
    next weakest goes then, so the lead keeps both kinds."""
    new = W["read"](st, SYMS["gMoveToLearn"], "<H")[0]
    base = SYMS["gBattleMons"]
    types = set(W["read"](st, base + 34, "<3B")) - {0}
    stats = (W["read"](st, base + 2, "<H")[0], W["read"](st, base + 8, "<H")[0])
    if not any(stats):
        # Out of battle (the evolution scene) gBattleMons is cleared: use the party lead instead
        # (struct Pokemon: attack +90, spAttack +96).
        party = SYMS["gParties"]
        stats = (W["read"](st, party + 90, "<H")[0], W["read"](st, party + 96, "<H")[0])
        types = species_types(W["lead_species"](st, SYMS))
    moves, _ = W["lead_moves"](st, SYMS)
    info = move_info()

    def kind(m):
        power, _, special = info.get(m, (0, 0, False))
        return special if power > 0 else None

    def move_type(m):
        return info.get(m, (0, 0, False))[1]

    def worth(m, others):
        value = move_value(m, types, stats)
        others_types = {move_type(o) for o in others if kind(o) is not None}
        return value * (COVERAGE if value > 0 and move_type(m) not in others_types else 1.0)

    def kept_worth(i):
        return worth(moves[i], [m for j, m in enumerate(moves) if j != i])
    order = sorted(range(4), key=lambda i: (kept_worth(i), -i))
    for slot in order:
        k = kind(moves[slot])
        if k is not None and k != kind(new) and sum(kind(m) == k for m in moves) == 1:
            continue  # last move of its category
        kept = [m for j, m in enumerate(moves) if j != slot]
        if worth(new, kept) > kept_worth(slot):
            return slot
        return None
    return None


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


@lru_cache(None)
def evo_states():
    """(EVOSTATE_REPLACE_MOVE, MVSTATE_HANDLE_YES_NO) from evolution_scene.c's state enums."""
    import re as _re
    src = open(os.path.join(os.path.dirname(ROM), "src", "evolution_scene.c"), encoding="utf-8").read()

    def index(name):
        body = _re.search(r"enum\s*\{([^}]*\b" + name + r"\b[^}]*)\}", src).group(1)
        names = _re.findall(r"^\s*(\w+)\s*,", body, _re.M)
        return names.index(name)
    return index("EVOSTATE_REPLACE_MOVE"), index("MVSTATE_HANDLE_YES_NO")


TASK_SIZE, NUM_TASKS = 40, 16  # struct Task: func, isActive, prev, next, priority, s16 data[16]


def evo_at_learn_prompt(st):
    """True while the evolution scene shows "delete a move to make room for ...?" with YES/NO."""
    replace, yes_no = evo_states()
    for i in range(NUM_TASKS):
        t = SYMS["gTasks"] + TASK_SIZE * i
        func, active = W["read"](st, t, "<IB")
        if active and func & ~1 == SYMS["Task_EvolutionScene"]:
            state, learn = W["read"](st, t + 8, "<h")[0], W["read"](st, t + 8 + 2 * 6, "<h")[0]
            return state == replace and learn == yes_no  # tState is data[0], tLearnMoveState data[6]
    return False


def battle_press(ss):
    """Next single input in battle: B at "delete a move?"; in the move menu, move the cursor to the
    best move against the opponent's types (best_move); otherwise A."""
    st = W["state"](ss)
    cb2 = W["read"](st, SYMS["gMain"] + 4, "<I")[0] & ~1
    lo, hi = text_range("evolution_scene.o")
    if lo <= cb2 < hi:
        # Evolution scene. A advances its text; B would stop the evolution, so it is only used
        # to answer NO at "delete a move to make room?" (P_ASK_MOVE_CONFIRMATION is FALSE, so NO
        # gives up the move at once). The battle script check below must not run here: after a
        # battle, gBattlescriptCurrInstr can still point into the learn-move script.
        if evo_at_learn_prompt(st) and slot_to_forget(st) is None:
            return "press B 2 30"
        return "press A 2 30"
    lo, hi = text_range("pokemon_summary_screen.o")
    if lo <= cb2 < hi:
        # "Forget which move?" summary screen: move the cursor to the slot to forget, then A.
        ptr = W["read"](st, SYMS["sMonSummaryScreen"], "<I")[0]
        target = slot_to_forget(st)
        if not ptr or target is None:
            return "press B 2 30"
        cur = W["read"](st, ptr + SUMMARY_FIRST_MOVE_INDEX, "<B")[0]
        return "press A 2 30" if cur == target else ("press DOWN 2 20" if cur < target else "press UP 2 20")
    instr = W["read"](st, SYMS["gBattlescriptCurrInstr"], "<I")[0]
    if SYMS["BattleScript_AskToLearnMove"] <= instr < SYMS["BattleScript_ForgotAndLearnedNewMove"]:
        # A advances the text and answers YES (the cursor starts there); B declines.
        return "press A 2 30" if slot_to_forget(st) is not None else "press B 2 30"
    func = W["read"](st, SYMS["gBattlerControllerFuncs"], "<I")[0] & ~1
    if func == player_choose_action():
        # Action menu: Battle (0) / Bag (1) / Pokemon (2) / Run (3) in a 2x2 grid.
        cur = W["read"](st, SYMS["gActionSelectionCursor"], "<B")[0] & 3
        to = 3 if should_flee(st) else 0
        if to % 2 != cur % 2:
            return "press RIGHT 2 20" if to % 2 else "press LEFT 2 20"
        if to // 2 != cur // 2:
            return "press DOWN 2 20" if to // 2 else "press UP 2 20"
    if func == SYMS["HandleInputChooseMove"]:
        cur = W["read"](st, SYMS["gMoveSelectionCursor"], "<B")[0] & 3
        to = best_move(st)
        if to is not None and to != cur:
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
    m = load(start[0])
    if not (0 <= start[1] < m["W"] and 0 <= start[2] < m["H"]):
        # Mid-crossing of a map connection the position is a tile past the map's edge: let it finish.
        return ["wait 10"], None, facing, stopped
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
    out = []
    runaway = False
    try:
        walk(goals, ss, prefix, facing, out)
    except SystemExit as e:
        runaway = isinstance(e, Runaway)
        if not (os.environ.get("AP_PARTIAL") or runaway) or not isinstance(e.code, str):
            raise
        # AP_PARTIAL=1: report what was executed up to the failure, so the caller can continue
        # from the last state by hand (the commands reproduce it exactly). Runaway guards report
        # the same way but always fail.
        print(f"# stopped: {e.code}", file=sys.stderr)
    ss, facing = PROGRESS["ss"], PROGRESS["facing"]
    print("\n".join(compress(out)))
    print(f"# end {where(ss)} facing {facing} state {ss}", file=sys.stderr)
    if runaway:
        sys.exit(3)


PROGRESS = {}


def walk(goals, ss, prefix, facing, out):
    k, stopped, stuck, presses, cooldown = 0, True, False, 0, 0
    blocked_once = {}
    locked_waits, last_unit, repeats = 0, None, 0
    PROGRESS.update(ss=ss, facing=facing)
    for spec in goals:
        tries = 0
        grind = spec[0] == "grind"
        goal = spec[1] if grind else spec
        while True:
            name, x, y, cb = where(ss)
            if grind and cb == "CB2_Overworld" and not stuck and controls_free(ss):
                locked_waits = 0
                st = W["state"](ss)
                lvl = W["read"](st, SYMS["gParties"] + 84, "<B")[0]
                hp, mhp = W["read"](st, SYMS["gParties"] + 86, "<HH")
                if lvl >= spec[3]:
                    break
                moves, pp = W["lead_moves"](st, SYMS)
                attack_pp = sum(p for m, p in zip(moves, pp) if move_power().get(m, 0) > 0)
                if hp * 100 < mhp * GRIND_MIN_HP or attack_pp < 10:
                    print(f"# grind paused: HP {hp}/{mhp}, attack PP {attack_pp} at Lv{lvl}; heal and resume", file=sys.stderr)
                    break
                if (name, x, y) == goal:
                    goal = spec[2] if goal == spec[1] else spec[1]
            if cb != "CB2_Overworld":
                # One press at a time in battle: A fights with the move best_move picks, but at
                # "delete a move to make room?" A would answer YES and forget a move, so B (NO).
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
                    PROGRESS.update(ss=ss, facing=facing)
                    stopped = True
                else:
                    cooldown = 3
                continue
            elif (name, x, y) == goal and not grind:
                break
            elif (name, x, y) == goal and locked_waits >= LOCKED_WAITS:
                # Grinding, and controls stayed locked: a message (e.g. a Match Call) is open,
                # which waiting never closes. B advances it and answers NO to prompts.
                cmds, exp, stopped, locked_waits = [f"repeat {DIALOG_B} press B 2 30"], None, True, 0
            elif (name, x, y) == goal:
                cmds, exp = ["wait 30"], None  # grinding: wait until controls are free to toggle
                locked_waits += 1
            else:
                u = units((name, x, y), goal, facing, stopped)
                cmds, exp, facing, stopped = u
            if k >= MAX_STEPS:
                raise Runaway(f"step limit AP_MAX_STEPS={MAX_STEPS} reached at {where(ss)} ({ss})")
            unit = ((name, x, y, cb), tuple(cmds))
            repeats = repeats + 1 if unit == last_unit and cb == "CB2_Overworld" else 0
            last_unit = unit
            if repeats >= NO_PROGRESS:
                raise Runaway(f"no progress: {cmds} repeated {NO_PROGRESS} times at {where(ss)} ({ss})")
            cooldown = max(0, cooldown - 1)
            nxt = f"{prefix}_{k:04d}.ss"
            run(ss, cmds, nxt)
            k += 1
            out += cmds
            ss = nxt
            PROGRESS.update(ss=ss, facing=facing)
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
    PROGRESS.update(ss=ss, facing=facing)


main()
