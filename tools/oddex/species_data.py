"""Shared loaders for oddex species tooling (gen_species.py, apply_replacements.py).

    from species_data import load_species, oddex_stages, vanilla_stages

Stages are 1-based evolution depth: a species nothing evolves into is stage 1, and each
evolution adds one (Wurmple 1, Silcoon/Cascoon 2, Beautifly/Dustox 3).
"""
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
CONTENT = ROOT / 'content' / 'species'
ROLES = ROOT / 'content' / 'roles.toml'
REGIONAL_DEX = ROOT / 'content' / 'regional_dex.toml'

_BLOCK = re.compile(r'^\s*\[SPECIES_(\w+)\]\s*=', re.M)
_EVO_TARGET = re.compile(r'\{\s*EVO_\w+\s*,[^{}]*?SPECIES_(\w+)')


def load_species():
    """Every content/species/*.toml, sorted by file name, with '_file' set."""
    species = []
    for path in sorted(CONTENT.glob('*.toml')):
        with path.open('rb') as fp:
            data = tomllib.load(fp)
        data['_file'] = path.relative_to(ROOT)
        species.append(data)
    return species


def renamed_ids(all_species=None):
    """{old id: current id} from every TOML's previous_ids."""
    if all_species is None:
        all_species = load_species()
    return {old: s['id'] for s in all_species for old in s.get('previous_ids', [])}


def old_name_hint(species_id, renamed):
    """' (X is the old name of Y; use Y)' when species_id was renamed, else ''."""
    if species_id in renamed:
        return f' ({species_id} is the old name of {renamed[species_id]}; use {renamed[species_id]})'
    return ''


def load_roles():
    with ROLES.open('rb') as fp:
        return tomllib.load(fp)


def load_regional_dex():
    with REGIONAL_DEX.open('rb') as fp:
        return tomllib.load(fp)['order']


def _stages(edges, names):
    parents = {}
    for src, dsts in edges.items():
        for dst in dsts:
            parents.setdefault(dst, src)
    stages = {}

    def stage(name, seen=()):
        if name not in stages:
            parent = parents.get(name)
            stages[name] = 1 if parent is None or parent in seen else stage(parent, seen + (name,)) + 1
        return stages[name]

    for name in names:
        stage(name)
    return stages


def oddex_stages(all_species=None):
    """{id: stage} for original species, from their TOML `evolutions`."""
    all_species = load_species() if all_species is None else all_species
    edges = {s['id']: [e['into'] for e in s.get('evolutions', [])] for s in all_species}
    return _stages(edges, [s['id'] for s in all_species])


def vanilla_stages(game=GAME):
    """{NAME: stage} for every species defined in species_info/gen_*_families.h."""
    edges = {}
    for path in sorted((Path(game) / 'src/data/pokemon/species_info').glob('gen_*_families.h')):
        text = path.read_text(encoding='utf-8', errors='ignore')
        heads = list(_BLOCK.finditer(text))
        for i, head in enumerate(heads):
            body = text[head.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
            edges.setdefault(head.group(1), [])
            evo = body.find('.evolutions')
            if evo >= 0:
                edges[head.group(1)] += _EVO_TARGET.findall(body[evo:])
    return _stages(edges, list(edges))
