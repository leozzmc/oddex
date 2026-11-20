#!/usr/bin/env python3
"""Damage ranges for gym battles: the three starters against a leader's team, and back.

Usage (repository root):
  python3 tools/oddex/damage_calc.py BRAWLY_1 [--levels 14-18] [--set SPECIES:types=FIGHTING,FIRE]
      [--set SPECIES:level=14] [--drop SPECIES] [--learn GRINPACK:15:AERIAL_ACE] [--markdown]

Reads the trainer's party (game/src/data/trainers.party), species stats, types, weight and
level-up learnsets (content/species/*.toml), and move power/type/category/effect
(game/src/data/moves_info.h; `UPDATED >= GEN_n ? new : old` counts as the new value). Damage is
the Gen 5+ formula without critical hits, abilities (except a starter's type-immunity ability), items, weather or stat stages:
  floor(floor(floor(2L/5 + 2) * P * A / D) / 50) + 2, then x random 0.85..1.00, STAB 1.5, type.
Stats use neutral natures and no EVs; the player's IVs are 15, the trainer's come from the party.
Special effects handled: fixed level damage (Seismic Toss), Low Kick (target weight), multi-hit
(2-5 hits, shown as 2..5), Reversal at full HP. Status moves are skipped, and so is Focus Punch
(it moves last and fails once the user is hit, which a player attacking it always does).
For each starter and level: its best move against each of the leader's species (percent of the
target's HP and hits to KO) and the leader's best move against the starter. Analysis only.
"""
import argparse
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from species_data import GAME, load_species  # noqa: E402

STARTERS = ('GRINPACK', 'TREKKEYE', 'RIDGECAP')
TYPES = ['NORMAL', 'FIRE', 'WATER', 'ELECTRIC', 'GRASS', 'ICE', 'FIGHTING', 'POISON', 'GROUND', 'FLYING',
         'PSYCHIC', 'BUG', 'ROCK', 'GHOST', 'DRAGON', 'DARK', 'STEEL', 'FAIRY']
# Gen 6+ chart: CHART[attacker][defender], only the non-1 entries.
_C = {
    'NORMAL': {'ROCK': .5, 'GHOST': 0, 'STEEL': .5},
    'FIRE': {'FIRE': .5, 'WATER': .5, 'GRASS': 2, 'ICE': 2, 'BUG': 2, 'ROCK': .5, 'DRAGON': .5, 'STEEL': 2},
    'WATER': {'FIRE': 2, 'WATER': .5, 'GRASS': .5, 'GROUND': 2, 'ROCK': 2, 'DRAGON': .5},
    'ELECTRIC': {'WATER': 2, 'ELECTRIC': .5, 'GRASS': .5, 'GROUND': 0, 'FLYING': 2, 'DRAGON': .5},
    'GRASS': {'FIRE': .5, 'WATER': 2, 'GRASS': .5, 'POISON': .5, 'GROUND': 2, 'FLYING': .5, 'BUG': .5, 'ROCK': 2,
              'DRAGON': .5, 'STEEL': .5},
    'ICE': {'FIRE': .5, 'WATER': .5, 'GRASS': 2, 'ICE': .5, 'GROUND': 2, 'FLYING': 2, 'DRAGON': 2, 'STEEL': .5},
    'FIGHTING': {'NORMAL': 2, 'ICE': 2, 'POISON': .5, 'FLYING': .5, 'PSYCHIC': .5, 'BUG': .5, 'ROCK': 2, 'GHOST': 0,
                 'DARK': 2, 'STEEL': 2, 'FAIRY': .5},
    'POISON': {'GRASS': 2, 'POISON': .5, 'GROUND': .5, 'ROCK': .5, 'GHOST': .5, 'STEEL': 0, 'FAIRY': 2},
    'GROUND': {'FIRE': 2, 'ELECTRIC': 2, 'GRASS': .5, 'POISON': 2, 'FLYING': 0, 'BUG': .5, 'ROCK': 2, 'STEEL': 2},
    'FLYING': {'ELECTRIC': .5, 'GRASS': 2, 'FIGHTING': 2, 'BUG': 2, 'ROCK': .5, 'STEEL': .5},
    'PSYCHIC': {'FIGHTING': 2, 'POISON': 2, 'PSYCHIC': .5, 'DARK': 0, 'STEEL': .5},
    'BUG': {'FIRE': .5, 'GRASS': 2, 'FIGHTING': .5, 'POISON': .5, 'FLYING': .5, 'PSYCHIC': 2, 'GHOST': .5, 'DARK': 2,
            'STEEL': .5, 'FAIRY': .5},
    'ROCK': {'FIRE': 2, 'ICE': 2, 'FIGHTING': .5, 'GROUND': .5, 'FLYING': 2, 'BUG': 2, 'STEEL': .5},
    'GHOST': {'NORMAL': 0, 'PSYCHIC': 2, 'GHOST': 2, 'DARK': .5},
    'DRAGON': {'DRAGON': 2, 'STEEL': .5, 'FAIRY': 0},
    'DARK': {'FIGHTING': .5, 'PSYCHIC': 2, 'GHOST': 2, 'DARK': .5, 'FAIRY': .5},
    'STEEL': {'FIRE': .5, 'WATER': .5, 'ELECTRIC': .5, 'ICE': 2, 'ROCK': 2, 'STEEL': .5, 'FAIRY': 2},
    'FAIRY': {'FIRE': .5, 'FIGHTING': 2, 'POISON': .5, 'DRAGON': 2, 'DARK': 2, 'STEEL': .5},
}


def effectiveness(move_type, target_types):
    e = 1.0
    for t in target_types:
        e *= _C.get(move_type, {}).get(t, 1.0)
    return e


def newer(expr):
    """`COND ? new : old` -> new; otherwise the expression itself."""
    m = re.match(r'.*?\?\s*(.+?)\s*:\s*.+$', expr.strip())
    return (m.group(1) if m else expr).strip()


def load_moves():
    text = (GAME / 'src/data/moves_info.h').read_text(errors='replace')
    moves = {}
    for m in re.finditer(r'\[MOVE_(\w+)\]\s*=\s*\{(.*?)\n    \},', text, re.S):
        body = m.group(2)

        def field(name, default=None):
            f = re.search(rf'\.{name}\s*=\s*([^,\n]+),', body)
            return newer(f.group(1)) if f else default
        power = field('power', '0')
        moves[m.group(1)] = {
            'power': int(power) if power.isdigit() else 0,
            'type': field('type', 'TYPE_NORMAL').replace('TYPE_', ''),
            'category': field('category', 'DAMAGE_CATEGORY_STATUS').replace('DAMAGE_CATEGORY_', ''),
            'effect': field('effect', 'EFFECT_HIT').replace('EFFECT_', ''),
        }
    return moves


def load_vanilla_species():
    """Vanilla species in the same shape as the TOMLs (base_stats, types, dex.weight,
    learnset.level), from species_info/*_families.h and level_up_learnsets/gen_9.h."""
    learn = {}
    text = (GAME / 'src/data/pokemon/level_up_learnsets/gen_9.h').read_text(errors='replace')
    for m in re.finditer(r's(\w+)LevelUpLearnset\[\] = \{(.*?)\};', text, re.S):
        learn[m.group(1)] = [(int(a), b) for a, b in re.findall(r'LEVEL_UP_MOVE\(\s*(\d+), MOVE_(\w+)\)', m.group(2))]
    out = {}
    for f in sorted((GAME / 'src/data/pokemon/species_info').glob('gen_*_families.h')):
        body_text = f.read_text(errors='replace')
        defines = dict(re.findall(r'^#define (\w+)\s+(.+)$', body_text, re.M))
        for m in re.finditer(r'\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n    \},', body_text, re.S):
            name, body = m.group(1), m.group(2)
            if name in out:
                continue
            st = {}
            for k, field in (('hp', 'baseHP'), ('atk', 'baseAttack'), ('def', 'baseDefense'), ('spa', 'baseSpAttack'),
                             ('spd', 'baseSpDefense'), ('spe', 'baseSpeed')):
                sm = re.search(rf'\.{field}\s*=\s*([^,\n]+),', body)
                v = newer(sm.group(1)) if sm else ''
                v = newer(defines.get(v, v))
                st[k] = int(v) if v.isdigit() else None
            ty = re.search(r'\.types\s*=\s*MON_TYPES\(([^)]*)\)', body)
            ab = re.search(r'\.abilities\s*=\s*\{([^}]*)\}', body)
            wt = re.search(r'\.weight\s*=\s*(\d+)', body)
            ls = re.search(r'\.levelUpLearnset\s*=\s*s(\w+)LevelUpLearnset', body)
            if None in st.values() or not ty:
                continue
            out[name] = {'id': name, 'base_stats': st, 'types': [x.strip().replace('TYPE_', '') for x in ty.group(1).split(',')],
                         'abilities': [x.strip().replace('ABILITY_', '') for x in ab.group(1).split(',')] if ab else [],
                         'dex': {'weight': int(wt.group(1)) if wt else 100},
                         'learnset': {'level': learn.get(ls.group(1), []) if ls else []}}
    return out


def load_party(trainer, ref=None):
    if ref:
        import subprocess
        text = subprocess.run(['git', 'show', f'{ref}:game/src/data/trainers.party'], capture_output=True, text=True,
                              cwd=GAME).stdout
    else:
        text = (GAME / 'src/data/trainers.party').read_text()
    name = trainer.upper().removeprefix('TRAINER_')
    header = f'=== TRAINER_{name} ==='
    if header not in text:
        near = sorted({h for h in re.findall(r'=== TRAINER_(\w+) ===', text) if h.startswith(name.split('_')[0])})[:8]
        raise SystemExit(f'damage_calc: no trainer TRAINER_{name} in trainers.party'
                         + (f' (did you mean: {", ".join(near)}?)' if near else ''))
    block = text.split(header, 1)[1].split('\n=== ', 1)[0]
    party = []
    for chunk in block.split('\n\n')[1:]:
        lines = [ln.strip() for ln in chunk.strip().split('\n') if ln.strip()]
        if not lines:
            continue
        name = lines[0].split('@')[0].strip().upper().replace(' ', '_')
        mon = {'species': name, 'level': 5, 'iv': 0, 'moves': []}
        for ln in lines[1:]:
            if ln.startswith('Level:'):
                mon['level'] = int(ln.split(':')[1])
            elif ln.startswith('IVs:'):
                mon['iv'] = int(ln.split(':')[1].split()[0])
            elif ln.startswith('- '):
                mon['moves'].append(ln[2:].strip().upper().replace(' ', '_'))
        party.append(mon)
    return party


def stats(sp, level, iv):
    b = sp['base_stats']
    out = {'hp': (2 * b['hp'] + iv) * level // 100 + level + 10}
    for k in ('atk', 'def', 'spa', 'spd', 'spe'):
        out[k] = (2 * b[k] + iv) * level // 100 + 5
    return out


def damage(attacker, defender, move, moves):
    """(min, max) damage of one use, or None for status moves."""
    mv = moves.get(move)
    if not mv:
        return None
    eff = mv['effect']
    if mv['type'] in defender.get('immune', ()):   # an ability like Volt Absorb or Levitate
        return None if mv['category'] == 'STATUS' else (0, 0)
    if eff == 'FIXED_HP_DAMAGE':   # Sonic Boom: 20 (its argument), type immunity still applies
        e = effectiveness(mv['type'], defender['types'])
        return (20, 20) if e else (0, 0)
    if eff in ('LEVEL_DAMAGE',):
        e = effectiveness(mv['type'], defender['types'])
        d = attacker['level'] if e else 0
        return (d, d)
    if mv['category'] == 'STATUS' or eff == 'FOCUS_PUNCH':
        # Focus Punch moves last and fails if the user was hit this turn: against a player who
        # attacks it does nothing, so it is left out.
        return None
    power = mv['power']
    if eff == 'LOW_KICK':
        w = defender['weight'] / 10
        power = 20 if w < 10 else 40 if w < 25 else 60 if w < 50 else 80 if w < 100 else 100 if w < 200 else 120
    if eff in ('REVERSAL', 'FLAIL'):
        power = 20
    if not power:
        return None
    phys = mv['category'] == 'PHYSICAL'
    a = attacker['stats']['atk' if phys else 'spa']
    d = defender['stats']['def' if phys else 'spd']
    base = (2 * attacker['level'] // 5 + 2) * power * a // d // 50 + 2
    mod = (1.5 if mv['type'] in attacker['types'] else 1.0) * effectiveness(mv['type'], defender['types'])
    lo, hi = math.floor(base * 0.85 * mod), math.floor(base * mod)
    if eff == 'MULTI_HIT':
        lo, hi = lo * 2, hi * 5
    return (lo, hi)


def best(attacker, defender, move_list, moves):
    """The move with the highest average damage: (move, lo, hi)."""
    top = None
    for mv in move_list:
        r = damage(attacker, defender, mv, moves)
        if r and (top is None or sum(r) > top[1] + top[2]):
            top = (mv, r[0], r[1])
    return top


# Abilities that make the holder immune to a type. Only the starters' slot-1 ability is applied
# (the player's starter); the trainers' abilities are still not modelled.
IMMUNE_ABILITIES = {'LIGHTNING_ROD': 'ELECTRIC', 'VOLT_ABSORB': 'ELECTRIC', 'MOTOR_DRIVE': 'ELECTRIC',
                    'WATER_ABSORB': 'WATER', 'STORM_DRAIN': 'WATER', 'DRY_SKIN': 'WATER', 'FLASH_FIRE': 'FIRE',
                    'LEVITATE': 'GROUND', 'SAP_SIPPER': 'GRASS'}


def starter_immune(sp):
    ab = (sp.get('abilities') or ['NONE'])[0]
    return [IMMUNE_ABILITIES[ab]] if ab in IMMUNE_ABILITIES else []


def mon(species, sid, level, iv, overrides):
    sp = species[sid]
    m = {'id': sid, 'level': overrides.get(sid, {}).get('level', level),
         'types': overrides.get(sid, {}).get('types', sp['types']), 'weight': sp['dex']['weight'],
         'immune': overrides.get(sid, {}).get('immune', [])}
    m['stats'] = stats(sp, m['level'], iv)
    return m


def learned(sp, level, extra):
    moves = [mv for lv, mv in sp['learnset']['level'] if lv <= level]
    moves += [mv for lv, mv in extra.get(sp['id'], []) if lv <= level]
    return list(dict.fromkeys(moves))


def run(trainer, levels, overrides, drops, extra, moves, species, starters=STARTERS, ref=None):
    party = [p for p in load_party(trainer, ref) if p['species'] not in drops]
    for p in party:
        new = overrides.get(p['species'], {}).get('species')
        if new:
            p['species'] = new
        if overrides.get(p['species'], {}).get('moves'):
            p['moves'] = overrides[p['species']]['moves']
    rows = []
    for sid in starters:
        for lv in levels:
            # A starter's level is the loop variable, but types and immune overrides apply to it too.
            own = {'immune': starter_immune(species[sid])}
            own.update({k: v for k, v in overrides.get(sid, {}).items() if k in ('types', 'immune')})
            me = mon(species, sid, lv, 15, {sid: own})
            my_moves = learned(species[sid], lv, extra)
            for p in party:
                foe = mon(species, p['species'], p['level'], p['iv'], overrides)
                mine = best(me, foe, my_moves, moves)
                theirs = best(foe, me, p['moves'], moves)
                rows.append((sid, lv, p['species'], foe['level'], me, foe, mine, theirs))
    return rows


def pct(lo, hi, hp):
    return f'{100 * lo // hp}–{100 * hi // hp}%'


def hits(lo, hi, hp):
    if hi <= 0:
        return '∞'
    a, b = math.ceil(hp / hi), (math.ceil(hp / lo) if lo > 0 else '∞')
    return f'{a}' if a == b else f'{a}–{b}'


def render(rows, markdown):
    out = []
    if markdown:
        out += ['| 御三家 | Lv | 對手 | 我方最佳招式 | 打對手 | 幾下擊倒 | 對手最佳招式 | 打我方 | 幾下擊倒 | 速度 |',
                '|---|---|---|---|---|---|---|---|---|---|']
    for sid, lv, foe_id, foe_lv, me, foe, mine, theirs in rows:
        m = (f'{mine[0].title().replace("_", " ")}', pct(mine[1], mine[2], foe['stats']['hp']),
             hits(mine[1], mine[2], foe['stats']['hp'])) if mine else ('—', '0%', '∞')
        t = (f'{theirs[0].title().replace("_", " ")}', pct(theirs[1], theirs[2], me['stats']['hp']),
             hits(theirs[1], theirs[2], me['stats']['hp'])) if theirs else ('—', '0%', '∞')
        spd = '我方先' if me['stats']['spe'] > foe['stats']['spe'] else '對手先' if me['stats']['spe'] < foe['stats']['spe'] else '同速'
        cells = [sid.title(), str(lv), f'{foe_id.title()} Lv{foe_lv}', *m, *t, spd]
        out.append('| ' + ' | '.join(cells) + ' |' if markdown else '  '.join(cells))
    return '\n'.join(out)


def wins(me, foe, mine, theirs):
    """Whether the starter wins this one-on-one in the worst case: it needs at most as many hits
    (its max-roll hits against their min-roll hits... i.e. its slowest KO) as the foe's fastest KO,
    minus one if the foe moves first. No items, crits, stat stages or switching."""
    if not mine or mine[2] <= 0:
        return False
    need = math.ceil(foe['stats']['hp'] / mine[1]) if mine[1] > 0 else 99
    if not theirs or theirs[2] <= 0:
        return True
    they = math.ceil(me['stats']['hp'] / theirs[2])
    first = me['stats']['spe'] > foe['stats']['spe']
    return need <= they if first else need < they


def summary(rows):
    """Per starter: the lowest level (in the range) at which it wins every one-on-one, and per foe
    the lowest winning level."""
    out = []
    for sid in dict.fromkeys(r[0] for r in rows):
        mine = [r for r in rows if r[0] == sid]
        foes = list(dict.fromkeys(r[2] for r in mine))
        per = {}
        for f in foes:
            lv = [r[1] for r in mine if r[2] == f and wins(r[4], r[5], r[6], r[7])]
            per[f] = min(lv) if lv else None
        all_lv = [lv for lv in sorted({r[1] for r in mine}) if all(
            wins(r[4], r[5], r[6], r[7]) for r in mine if r[1] == lv)]
        cell = ', '.join(f'{f.title()} {"Lv" + str(v) if v else "✗"}' for f, v in per.items())
        out.append((sid, min(all_lv) if all_lv else None, cell))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--summary', action='store_true',
                    help='per starter, the lowest level that wins every one-on-one (worst-case rolls)')
    ap.add_argument('trainer', help='trainer id, with or without TRAINER_ (e.g. BRAWLY_1)')
    ap.add_argument('--levels', default='14-18')
    ap.add_argument('--set', action='append', default=[], help='SPECIES:types=A,B, SPECIES:level=N, SPECIES:moves=A,B,C,D, SPECIES:immune=TYPE (an ability like Volt Absorb) or SPECIES:species=OTHER (swap; later keys use the new species)')
    ap.add_argument('--drop', action='append', default=[])
    ap.add_argument('--learn', action='append', default=[], help='SPECIES:LEVEL:MOVE (extra level-up move)')
    ap.add_argument('--markdown', action='store_true')
    ap.add_argument('--starters', help='comma-separated species to test instead of the trio '
                    '(e.g. GRINVINE,TREKWHEEL,RIDGEFIN, or GROVYLE,COMBUSKEN,MARSHTOMP with --vanilla)')
    ap.add_argument('--vanilla', metavar='REF', help='calibrate: vanilla starters against the party at this git ref '
                    '(e.g. 421e141a, the upstream import)')
    args = ap.parse_args()
    lv = args.levels.split('-')   # '24' or '18-36'
    a, b = int(lv[0]), int(lv[-1])
    overrides = {}
    for s in args.set:
        sid, kv = s.split(':', 1)
        k, v = kv.split('=')
        overrides.setdefault(sid, {})[k] = v.split(',') if k in ('types', 'moves', 'immune') else v if k == 'species' else int(v)
    extra = {}
    for s in args.learn:
        sid, lv, mv = s.split(':')
        extra.setdefault(sid, []).append((int(lv), mv))
    species = {s['id']: s for s in load_species()}
    if args.vanilla:
        species = {**load_vanilla_species(), **species}
        starters = tuple(args.starters.split(',')) if args.starters else ('TREECKO', 'TORCHIC', 'MUDKIP')
        rows = run(args.trainer, range(a, b + 1), overrides, set(args.drop), extra, load_moves(), species,
                   starters, args.vanilla)
    else:
        starters = tuple(args.starters.split(',')) if args.starters else STARTERS
        rows = run(args.trainer, range(a, b + 1), overrides, set(args.drop), extra, load_moves(), species, starters)
    if args.summary:
        for sid, lv, cell in summary(rows):
            print(f'{sid.title()}: {"Lv" + str(lv) if lv else "✗ (no level in range)"}  [{cell}]')
    else:
        print(render(rows, args.markdown))


if __name__ == '__main__':
    main()
