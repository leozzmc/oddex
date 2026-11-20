"""Print map, position, gMain.callback2 and lead level/HP from oddex-run savestates.

usage: where.py STATE.ss [...]   (symbols come from game/pokeemerald.elf; build first)
"""
import glob, json, os, re, struct, subprocess, sys, zlib
from functools import lru_cache

GAME = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")), "game")
NM = os.path.join(os.environ.get("ODDEX_TOOLCHAIN", os.path.expanduser("~/oddex-toolchain")), "arm-none-eabi/bin/arm-none-eabi-nm")


def state(path):
    d = open(path, "rb").read()
    i = 8
    while i < len(d):
        n, t = struct.unpack(">I4s", d[i:i + 8])
        if t == b"gbAs":
            return zlib.decompress(d[i + 8:i + 8 + n])
        i += 12 + n
    raise SystemExit("no gbAs chunk")


def syms():
    out = {}
    for line in subprocess.run([NM, GAME + "/pokeemerald.elf"], capture_output=True, text=True).stdout.splitlines():
        p = line.split()
        if len(p) == 3:
            out[p[2]] = int(p[0], 16)
    return out


def read(st, addr, fmt):
    if 0x03000000 <= addr < 0x03008000:
        off = 0x19000 + addr - 0x03000000
    elif 0x02000000 <= addr < 0x02040000:
        off = 0x21000 + addr - 0x02000000
    else:
        raise ValueError(hex(addr))
    return struct.unpack_from(fmt, st, off)


def map_names():
    groups = json.load(open(GAME + "/data/maps/map_groups.json"))
    names = {}
    gi = 0
    for g in groups["group_order"]:
        for mi, m in enumerate(groups[g]):
            names[(gi, mi)] = m
        gi += 1
    return names


SUBSTRUCT_SLOT_0 = [0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 2, 3, 1, 1, 2, 3, 2, 3, 1, 1, 2, 3, 2, 3]  # sSubstructOffsets[0]
SUBSTRUCT_SLOT_1 = [1, 1, 2, 3, 2, 3, 0, 0, 0, 0, 0, 0, 2, 3, 1, 1, 3, 2, 2, 3, 1, 1, 3, 2]  # sSubstructOffsets[1]
SUBSTRUCT_BYTES = 12


def lead_species(st, syms):
    """Decrypt the lead party Pokemon's species (growth substruct, species in the low 11 bits)."""
    base = syms["gParties"]
    personality, ot_id = read(st, base, "<II")
    raw = [w ^ personality ^ ot_id for w in read(st, base + 32, "<12I")]
    sub = struct.pack("<12I", *raw)[SUBSTRUCT_BYTES * SUBSTRUCT_SLOT_0[personality % 24]:]
    return struct.unpack_from("<H", sub)[0] & 0x7FF


def lead_moves(st, syms):
    """Decrypt the lead party Pokemon's moves and PP (src/pokemon.c EncryptBoxMon/GetSubstruct)."""
    base = syms["gParties"]
    personality, ot_id = read(st, base, "<II")
    raw = [w ^ personality ^ ot_id for w in read(st, base + 32, "<12I")]
    sub = struct.pack("<12I", *raw)[SUBSTRUCT_BYTES * SUBSTRUCT_SLOT_1[personality % 24]:][:SUBSTRUCT_BYTES]
    words = struct.unpack_from("<4H", sub)
    moves = [w & 0x7FF for w in words]
    pp = [b & 0x7F for b in sub[8:12]]
    return moves, pp


@lru_cache(None)
def move_names():
    text = open(os.path.join(GAME, "include/constants/moves.h"), encoding="utf-8").read()
    return {int(v): k[len("MOVE_"):] for k, v in re.findall(r"\b(MOVE_[A-Z0-9_]+)\s*=\s*(\d+)\s*,", text)}


S = syms()
names = map_names()
for path in sys.argv[1:]:
    st = state(path)
    sb1 = read(st, S["gSaveBlock1Ptr"], "<I")[0]
    x, y = read(st, sb1, "<hh")
    grp, num = read(st, sb1 + 4, "<bb")
    cb2 = read(st, S["gMain"] + 4, "<I")[0] & ~1
    cb = max(((v, k) for k, v in S.items() if 0 <= cb2 - v < 0x2000), default=(0, "?"))
    p = S["gParties"] + 80
    lvl = read(st, p + 4, "<B")[0]
    hp, mhp = read(st, p + 6, "<HH")
    moves, pp = lead_moves(st, S)
    mv = " ".join(f"{move_names().get(m, m)}:{p}" for m, p in zip(moves, pp) if m)
    print(f"{path}: {names.get((grp, num), (grp, num))} ({x},{y}) cb2={cb[1]} lead=Lv{lvl} {hp}/{mhp} [{mv}]")
