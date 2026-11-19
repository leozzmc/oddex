#!/usr/bin/env python3
"""List references to vanilla species in oddex content (read-only).

A species is "vanilla" if it is defined in src/data/pokemon/species_info/gen_*_families.h.
FRLG-only content is skipped because the Emerald build compiles it out.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

CATEGORIES = ["party", "wild", "script", "c", "text", "gfx", "facility", "dictionary", "mechanics", "unknown"]
# Categories that hold content to rewrite; --strict fails on these. Facilities are stubbed
# during the plan B migration (docs/DECISIONS.md), so they are reported but not strict.
STRICT_DEFAULT = ["party", "wild", "script", "c", "unknown"]

# C files whose species references are battle/form/animation mechanics, not content.
MECHANICS_C = {
    "src/battle_util.c", "src/battle_z_move.c", "src/battle_dynamax.c", "src/pokemon.c",
    "src/battle_main.c", "src/battle_ai_main.c", "src/battle_ai_util.c", "src/battle_ai_switch.c",
    "src/battle_move_resolution.c", "src/battle_script_commands.c", "src/battle_gfx_sfx_util.c",
    "src/battle_controller_player.c", "src/battle_anim.c", "src/battle_anim_mons.c",
    "src/battle_anim_new.c", "src/battle_bg.c", "src/battle_set_effect.c", "src/battle_end_turn.c",
    "src/battle_interface.c", "src/battle_terastal.c", "src/battle_gimmick.c", "src/evolution_scene.c",
    "src/pokemon_icon.c", "src/decompress.c", "src/data/moves_info.h", "src/event_object_movement.c",
    "src/follower_helper.c", "src/pokemon_sprite_visualizer.c", "src/daycare.c", "src/data/types_info.h",
    "src/pokedex_plus_hgss.c", "src/pokemon_size_record.c", "src/berry.c", "src/random_mon_generation.c",
    "src/dexnav.c",
}
FACILITY_C_PREFIXES = (
    "src/data/battle_frontier/", "src/battle_pike.c", "src/battle_factory.c", "src/battle_pyramid",
    "src/battle_tent.c", "src/trainer_hill.c", "src/apprentice.c", "src/frontier_util.c",
    "src/ereader_helpers.c",
)
DICTIONARY_C_PREFIXES = ("src/data/easy_chat/", "src/data/bard_music/")
# Generated from party/json files, FRLG-only, or species definition tables.
SKIP_C_PREFIXES = ("src/data/pokemon", "src/data/graphics")
SKIP_C = {
    "src/data/trainers.h", "src/data/trainers_frlg.h", "src/data/wild_encounters.h",
    "src/data/battle_partners.h", "src/data/debug_trainers.h",
    "src/trainer_tower_sets.c", "src/credits_frlg.c", "src/oak_speech.c",
}

SPECIES_TOKEN = re.compile(r"\bSPECIES_[A-Z0-9_]+\b")


def is_frlg(path):
    return "frlg" in path.lower()


def load_species(game):
    """Return (vanilla keys, all known species names, alias -> target)."""
    vanilla, known = set(), set()
    for f in glob.glob(os.path.join(game, "src/data/pokemon/species_info/*.h")):
        keys = re.findall(r"^\s*\[(SPECIES_[A-Z0-9_]+)\]\s*=", open(f, encoding="utf-8").read(), re.M)
        known.update(keys)
        if re.search(r"gen_\d+_families\.h$", f):
            vanilla.update(keys)
    header = open(os.path.join(game, "include/constants/species.h"), encoding="utf-8").read()
    aliases = dict(re.findall(r"\b(SPECIES_[A-Z0-9_]+)\s*=\s*(SPECIES_[A-Z0-9_]+)\s*,", header))
    known.update(re.findall(r"^\s*(SPECIES_[A-Z0-9_]+)\b", header, re.M))
    return vanilla, known, aliases


def party_species_token(line):
    first = re.sub(r"\s*@.*$", "", line).strip()
    first = re.sub(r"\((M|F)\)", "", first).strip()
    m = re.search(r"\(([^)]+)\)\s*$", first)
    name = (m.group(1) if m else first).strip()
    if name.startswith("SPECIES_"):
        return name
    name = name.replace("♂", "_M").replace("♀", "_F").replace("é", "E")
    return "SPECIES_" + re.sub(r"_+", "_", re.sub(r"[^A-Z0-9]", "_", name.upper().replace("'", "").replace("’", ""))).strip("_")


def scan_party(game, add):
    path = "src/data/trainers.party"
    trainer, after_blank, in_header = None, False, False
    for ln, raw in enumerate(open(os.path.join(game, path), encoding="utf-8"), 1):
        line = raw.rstrip("\n")
        m = re.match(r"^=== (TRAINER_\w+) ===", line)
        if m:
            trainer, after_blank, in_header = m.group(1), False, True
            continue
        if trainer is None or line.startswith(("/*", "*", "//")):
            continue
        if not line.strip():
            after_blank, in_header = True, False
            continue
        if after_blank and not in_header:
            add("party", path, ln, party_species_token(line), trainer)
        after_blank = False


def map_regions(game):
    regions, names = {}, {}
    for f in glob.glob(os.path.join(game, "data/maps/*/map.json")):
        j = json.load(open(f, encoding="utf-8"))
        regions[j["id"]] = j.get("region")
        names[j["id"]] = j["name"]
    return regions, names


def scan_wild(game, add, regions, names):
    path = "src/data/wild_encounters.json"
    data = json.load(open(os.path.join(game, path), encoding="utf-8"))
    for group in data["wild_encounter_groups"]:
        for enc in group.get("encounters", []):
            mp = enc.get("map", "")
            if group["label"] == "gWildMonHeaders" and regions.get(mp) != "REGION_HOENN":
                continue
            where = names.get(mp, enc.get("base_label", ""))
            for kind, table in enc.items():
                if isinstance(table, dict) and "mons" in table:
                    for mon in table["mons"]:
                        add("wild", path, 0, mon["species"], f"{where}:{kind}")


def map_of(path):
    parts = path.split("/")
    return parts[2] if len(parts) > 3 and parts[1] == "maps" else ""


def scan_scripts(game, add, vanilla_words):
    word_re = re.compile(r"\b(" + "|".join(sorted(vanilla_words, key=len, reverse=True)) + r")\b")
    files = glob.glob(os.path.join(game, "data/**/*.inc"), recursive=True) + glob.glob(os.path.join(game, "data/*.s"))
    for f in sorted(files):
        rel = os.path.relpath(f, game)
        if is_frlg(rel) or rel.endswith("debug.inc"):
            continue
        for ln, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
            s = line.strip()
            if s.startswith("@"):
                continue
            if ".string" in s:
                for w in word_re.findall(s.split(".string", 1)[1]):
                    add("text", rel, ln, "SPECIES_" + w, map_of(rel))
                continue
            for tok in SPECIES_TOKEN.findall(s):
                add("script", rel, ln, tok, f"{map_of(rel)} {s.split()[0]}".strip())


def scan_c(game, add):
    files = glob.glob(os.path.join(game, "src/**/*.c"), recursive=True) + glob.glob(os.path.join(game, "src/**/*.h"), recursive=True)
    for f in sorted(files):
        rel = os.path.relpath(f, game)
        if rel in SKIP_C or rel.startswith(SKIP_C_PREFIXES) or is_frlg(rel):
            continue
        if rel in MECHANICS_C:
            cat = "mechanics"
        elif rel.startswith(FACILITY_C_PREFIXES):
            cat = "facility"
        elif rel.startswith(DICTIONARY_C_PREFIXES):
            cat = "dictionary"
        else:
            cat = "c"
        for ln, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
            for tok in SPECIES_TOKEN.findall(line):
                add(cat, rel, ln, tok, "")


def scan_gfx(game, add, regions, vanilla_words):
    for f in sorted(glob.glob(os.path.join(game, "data/maps/*/map.json"))):
        rel = os.path.relpath(f, game)
        j = json.load(open(f, encoding="utf-8"))
        if j.get("region") != "REGION_HOENN":
            continue
        for i, o in enumerate(j.get("object_events", [])):
            g = o.get("graphics_id", "").replace("OBJ_EVENT_GFX_", "")
            head = g.split("_")[0]
            if g in vanilla_words or head in vanilla_words:
                add("gfx", rel, 0, "SPECIES_" + head, f"{j['name']} object #{i + 1} {o.get('graphics_id')} ({o['x']},{o['y']})")


def trainer_maps(game):
    out = collections.defaultdict(set)
    for f in glob.glob(os.path.join(game, "data/maps/*/scripts.inc")):
        m = f.split(os.sep)[-2]
        for t in re.findall(r"\b(TRAINER_[A-Z0-9_]+)\b", open(f, encoding="utf-8").read()):
            out[t].add(m)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=os.path.join(os.path.dirname(__file__), "..", "..", "game"))
    ap.add_argument("--category", action="append", choices=CATEGORIES, help="limit to these categories (repeatable)")
    ap.add_argument("--maps", help="comma-separated map name prefixes, e.g. LittlerootTown,Route101 (filters party/wild/script/text/gfx)")
    ap.add_argument("--summary", action="store_true", help="print counts only")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("--strict", action="store_true", help=f"exit 1 if any finding in {','.join(STRICT_DEFAULT)} (or --category)")
    args = ap.parse_args()
    game = os.path.abspath(args.game)

    vanilla, known, aliases = load_species(game)
    if not vanilla:
        sys.exit(f"no species found under {game}/src/data/pokemon/species_info")
    vanilla_words = {s[len("SPECIES_"):] for s in vanilla if "_" not in s[len("SPECIES_"):] and len(s) > len("SPECIES_") + 3}
    findings = []

    def add(cat, path, line, token, context):
        resolved = aliases.get(token, token)
        if resolved in vanilla:
            findings.append({"category": cat, "file": path, "line": line, "species": token, "context": context})
        elif cat in ("party", "wild") and token not in known and not token.startswith("SPECIES_ODDEX_"):
            # A species name we could not resolve: a typo, or a parser gap that would hide references.
            findings.append({"category": "unknown", "file": path, "line": line, "species": token, "context": context})

    regions, names = map_regions(game)
    scan_party(game, add)
    scan_wild(game, add, regions, names)
    scan_scripts(game, add, vanilla_words)
    scan_c(game, add)
    scan_gfx(game, add, regions, vanilla_words)

    cats = args.category or CATEGORIES
    findings = [f for f in findings if f["category"] in cats]
    if args.maps:
        prefixes = [p.strip() for p in args.maps.split(",") if p.strip()]
        tmaps = trainer_maps(game)

        def on_maps(f):
            ctx = f["context"]
            if f["category"] == "party":
                ms = tmaps.get(ctx, set())
            elif f["category"] in ("c", "mechanics"):
                return False
            else:
                ms = {ctx.split(":")[0].split(" ")[0]}
            return any(m == p or m.startswith(p + "_") for m in ms for p in prefixes)

        findings = [f for f in findings if on_maps(f)]

    if args.json:
        json.dump(findings, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        by_cat = collections.Counter(f["category"] for f in findings)
        species = collections.Counter(f["species"] for f in findings)
        print(f"vanilla species references: {len(findings)} ({len(species)} distinct species)")
        for c in cats:
            files = len({f["file"] for f in findings if f["category"] == c})
            print(f"  {c:10} {by_cat[c]:6} refs  {files:4} files")
        if not args.summary:
            for f in findings:
                loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
                print(f"{f['category']}\t{loc}\t{f['species']}\t{f['context']}")

    if args.strict:
        strict = args.category or STRICT_DEFAULT
        if any(f["category"] in strict for f in findings):
            sys.exit(1)


if __name__ == "__main__":
    main()
