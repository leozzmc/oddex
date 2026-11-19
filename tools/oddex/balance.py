#!/usr/bin/env python3
"""Compare every original species' base stat total with the vanilla species it replaces.

Usage (repository root): python3 tools/oddex/balance.py [--out docs/research/balance.md] [--threshold 15]

For each original (content/species/*.toml, in regional dex order): types, base stat total,
evolution stage, where it is used ([design].habitat, level_band), and every vanilla species that
content/replacements.toml maps onto it with that species' total and the difference. Vanilla stats
come from game/src/data/pokemon/species_info/*_families.h; a stat written as
`P_UPDATED_STATS >= GEN_n ? new : old` (directly or through a #define) counts as the new value.
Rows where any difference exceeds the threshold (default 15%) are flagged. Report only: the tool
changes nothing.
"""
import argparse
import re
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from species_data import GAME, ROOT, load_regional_dex, load_species, oddex_stages, vanilla_stages  # noqa: E402

STATS = ('baseHP', 'baseAttack', 'baseDefense', 'baseSpeed', 'baseSpAttack', 'baseSpDefense')
NOTES = '<!-- notes: kept when balance.py regenerates the table above -->'
SHORT = {'hp': 'baseHP', 'atk': 'baseAttack', 'def': 'baseDefense', 'spa': 'baseSpAttack',
         'spd': 'baseSpDefense', 'spe': 'baseSpeed'}


def value(expr, defines):
    expr = expr.strip().strip('()').strip()
    if expr in defines:
        return value(defines[expr], defines)
    m = re.match(r'.*\?\s*(\d+)\s*:\s*\d+$', expr)
    if m:
        return int(m.group(1))
    if expr.isdigit():
        return int(expr)
    return None


def vanilla_totals():
    """{SPECIES name without prefix: base stat total} for every vanilla species whose six stats parse."""
    totals = {}
    for f in sorted((GAME / 'src/data/pokemon/species_info').glob('gen_*_families.h')):
        text = f.read_text(errors='replace')
        defines = dict(re.findall(r'^#define (\w+)\s+(.+)$', text, re.M))
        for m in re.finditer(r'\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n    \},', text, re.S):
            name, body = m.group(1), m.group(2)
            stats = {}
            for s in STATS:
                sm = re.search(rf'\.{s}\s*=\s*([^,\n]+),', body)
                if sm:
                    stats[s] = value(sm.group(1), defines)
            if len(stats) == 6 and None not in stats.values() and name not in totals:
                totals[name] = sum(stats.values())
    return totals


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', help='write the Markdown report here (default: stdout)')
    ap.add_argument('--threshold', type=float, default=15.0, help='flag differences above this percent')
    args = ap.parse_args()
    species = {s['id']: s for s in load_species()}
    order = load_regional_dex()
    replace = tomllib.loads((ROOT / 'content/replacements.toml').read_text())['replace']
    by_original = {}
    for van, orig in replace.items():
        by_original.setdefault(orig, []).append(van)
    vtotal = vanilla_totals()
    ostage = oddex_stages(list(species.values()))
    vstage = vanilla_stages(GAME)
    rows, flagged = [], []
    for sid in order:
        s = species[sid]
        total = sum(s['base_stats'].get(k, 0) for k in SHORT)
        comps = []
        worst = 0.0
        for van in by_original.get(sid, []):
            vt = vtotal.get(van)
            if vt is None:
                comps.append(f'{van.capitalize()} (?)')
                continue
            d = (total - vt) / vt * 100
            worst = max(worst, abs(d))
            mark = ' **⚠**' if abs(d) > args.threshold else ''
            comps.append(f'{van.capitalize()} {vt} ({d:+.0f}%){mark}')
        d = s.get('design', {})
        where = ', '.join(d.get('habitat', [])) + (f' Lv{d["level_band"][0]}–{d["level_band"][1]}' if d.get('level_band') else '')
        types = '/'.join(t.capitalize() for t in s['types'])
        row = (f'| {s["name"]} | {types} | {ostage.get(sid, 1)} | {total} | {where} | '
               f'{"; ".join(comps) or "(no vanilla slot)"} |')
        rows.append(row)
        if worst > args.threshold:
            flagged.append((sid, worst))
    out = ['# 原創角色的平衡檢查(種族值總和)', '',
           f'由 `tools/oddex/balance.py` 產生,只做報告,不會調整任何數值。差異 = (原創 − 原版) ÷ 原版。'
           f'超過 ±{args.threshold:g}% 的標記為 **⚠**。原版的種族值取自 `species_info/*_families.h`,'
           '`P_UPDATED_STATS` 的條件式取新世代的值。', '',
           '| 原創角色 | 屬性 | 階段 | 總和 | 出現位置 | 取代的原版(總和、差異) |',
           '|---|---|---|---|---|---|'] + rows + ['', f'## 被標記的角色({len(flagged)} 隻)', '']
    for sid, worst in sorted(flagged, key=lambda x: -x[1]):
        out.append(f'- {species[sid]["name"]}:最大差異 {worst:.0f}%')
    text = '\n'.join(out) + '\n'
    if args.out and Path(args.out).exists():
        # Hand-written notes below the marker survive regeneration.
        old = Path(args.out).read_text()
        if NOTES in old:
            text += '\n' + NOTES + old.split(NOTES, 1)[1]
    if args.out:
        Path(args.out).write_text(text)
        print(f'wrote {args.out} ({len(rows)} species, {len(flagged)} flagged)')
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
