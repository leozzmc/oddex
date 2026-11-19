#!/usr/bin/env python3
"""Rewrite vanilla species in trainers.party and wild_encounters.json to oddex species, in place.

  apply_replacements.py [--table content/replacements.toml] --scope early [--fallback ID] [--dry-run]
  apply_replacements.py [--table ...] [--maps A,B] [--kinds land_mons] ...   (ad hoc scope)

The table maps each vanilla species (one key per evolution stage) to an original species id:

    stage_mismatch_ok = ["MIGHTYENA"]   # optional: allow these keys to map across stages
    [replace]
    POOCHYENA = "SHADEPUP"

Only species tokens change: the species of each Pokemon in trainers.party (nickname, gender and
item kept) and the "species" values in wild_encounters.json (no reformatting). Species that are
already original are left alone, so running twice changes nothing. What to rewrite comes from a
scope in content/migration_scope.toml (explicit trainers, wild maps and table kinds), shared with
check_species_refs.py. For ad hoc runs, --maps selects trainers referenced by those maps' scripts
and those maps' encounter tables, and --kinds limits the tables. FRLG (Kanto) tables are skipped. Without --fallback, any vanilla species
in scope that the table does not cover is listed and nothing is written.
"""
import argparse, collections, json, os, re, sys, tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_species_refs as refs  # noqa: E402
import migration_scope  # noqa: E402
from species_data import load_species, oddex_stages, old_name_hint, renamed_ids, vanilla_stages  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
GAME = os.path.join(ROOT, "game")
TABLE = os.path.join(ROOT, "content", "replacements.toml")
PARTY = os.path.join(GAME, "src", "data", "trainers.party")
WILD = os.path.join(GAME, "src", "data", "wild_encounters.json")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def display_name(oddex_id):
    """Party spelling that trainerproc turns back into SPECIES_<ID> (FOO_BAR -> 'Foo Bar')."""
    return " ".join(w.capitalize() for w in oddex_id.split("_"))


def species_span(line):
    """(start, end) of the species text in a party species line."""
    head_end = line.find(" @ ")
    head_end = len(line.rstrip()) if head_end < 0 else head_end
    head = line[:head_end]
    stripped = re.sub(r"\s*\((M|F)\)\s*$", "", head)
    m = re.search(r"\(([^()]+)\)\s*$", stripped)
    if m:
        return m.start(1), m.end(1)
    start = len(stripped) - len(stripped.lstrip())
    return start, len(stripped.rstrip())


def in_scope(name, prefixes):
    return not prefixes or any(name == p or name.startswith(p + "_") for p in prefixes)


class Replacer:
    def __init__(self, table_path, fallback):
        with open(table_path, "rb") as fp:
            table = tomllib.load(fp)
        self.replace = {k.upper(): v.upper() for k, v in table.get("replace", {}).items()}
        self.mismatch_ok = {k.upper() for k in table.get("stage_mismatch_ok", [])}
        self.fallback = fallback.upper() if fallback else None
        self.vanilla, self.known, self.aliases = refs.load_species(GAME)
        originals = load_species()
        self.oddex_ids = {s["id"] for s in originals}
        self.renamed = renamed_ids(originals)
        self.oddex_stage = oddex_stages(originals)
        self.vanilla_stage = vanilla_stages(GAME)
        self.errors = []
        self.missing = collections.defaultdict(list)
        self.changed = collections.Counter()
        self._validate()

    def _validate(self):
        for key, value in sorted(self.replace.items()):
            const = "SPECIES_" + key
            if self.aliases.get(const, const) not in self.vanilla:
                self.errors.append(f"table key {key} is not a vanilla species")
            if value not in self.oddex_ids:
                self.errors.append(f"table value {value} (for {key}) is not an id in content/species/*.toml"
                                   f"{old_name_hint(value, self.renamed)}")
                continue
            vs = self.vanilla_stage.get(self.aliases.get(const, const)[len("SPECIES_"):])
            os_ = self.oddex_stage.get(value)
            if vs and os_ and vs != os_ and key not in self.mismatch_ok:
                self.errors.append(f"{key} is evolution stage {vs} but {value} is stage {os_} "
                                   f"(add {key} to stage_mismatch_ok if intended)")
        if self.fallback and self.fallback not in self.oddex_ids:
            self.errors.append(f"--fallback {self.fallback} is not an id in content/species/*.toml"
                               f"{old_name_hint(self.fallback, self.renamed)}")

    def target(self, const, where):
        """Original species id for a vanilla SPECIES_ constant, or None to leave it unchanged."""
        resolved = self.aliases.get(const, const)
        if resolved not in self.vanilla:
            return None
        name = const[len("SPECIES_"):]
        new = self.replace.get(name) or self.replace.get(resolved[len("SPECIES_"):])
        if new:
            return new
        if self.fallback:
            return self.fallback
        self.missing[name].append(where)
        return None

    def party(self, text, select_trainer):
        lines = text.split("\n")
        trainer, after_blank, in_header = None, False, False
        for i, line in enumerate(lines):
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
                if select_trainer(trainer):
                    a, b = species_span(line)
                    old = line[a:b]
                    const = old if old.startswith("SPECIES_") else refs.party_species_token(old)
                    new = self.target(const, f"{trainer} (trainers.party:{i + 1})")
                    if new:
                        lines[i] = line[:a] + ("SPECIES_" + new if old.startswith("SPECIES_") else display_name(new)) + line[b:]
                        self.changed["party"] += 1
            after_blank = False
        return "\n".join(lines)

    def wild(self, text, select_table):
        regions, names = refs.map_regions(GAME)
        data = json.loads(text)
        slots = []
        for group in data["wild_encounter_groups"]:
            for enc in group.get("encounters", []):
                mp = enc.get("map", "")
                hoenn = group["label"] != "gWildMonHeaders" or regions.get(mp) == "REGION_HOENN"
                where = names.get(mp, enc.get("base_label", ""))
                for kind, table in enc.items():
                    if isinstance(table, dict) and "mons" in table:
                        selected = hoenn and select_table(where, kind)
                        for mon in table["mons"]:
                            slots.append((selected, f"{where}:{kind}", mon["species"]))
        matches = list(re.finditer(r'("species"\s*:\s*")(SPECIES_[A-Z0-9_]+)(")', text))
        if len(matches) != len(slots) or any(m.group(2) != s[2] for m, s in zip(matches, slots)):
            sys.exit("wild_encounters.json: species values are not in document order; refusing to edit")
        out, last = [], 0
        for m, (selected, where, const) in zip(matches, slots):
            new = self.target(const, where) if selected else None
            if new:
                out.append(text[last:m.start(2)] + "SPECIES_" + new)
                last = m.end(2)
                self.changed["wild"] += 1
        out.append(text[last:])
        return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--table", default=TABLE)
    ap.add_argument("--scope", help="a scope in content/migration_scope.toml (trainers + wild_maps/wild_kinds)")
    ap.add_argument("--scope-file", default=migration_scope.SCOPE_FILE, help=argparse.SUPPRESS)
    ap.add_argument("--maps", help="ad hoc instead of --scope: map name prefixes (same rule as check_species_refs.py)")
    ap.add_argument("--kinds", help="ad hoc instead of --scope: encounter tables to rewrite, e.g. land_mons")
    ap.add_argument("--fallback", help="original species id for vanilla species the table does not cover")
    ap.add_argument("--party", default=PARTY, help="trainers.party to rewrite (default: the game's)")
    ap.add_argument("--wild", default=WILD, help="wild_encounters.json to rewrite (default: the game's)")
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    args = ap.parse_args()
    if args.scope and (args.maps or args.kinds):
        ap.error("--scope already defines what to rewrite; drop --maps/--kinds")
    if args.scope:
        scope = migration_scope.get(GAME, [args.scope], args.scope_file)[0]
        select_trainer = scope.trainers.__contains__
        select_table = scope.has_wild
    else:
        prefixes = [p for p in (args.maps or "").split(",") if p]
        kinds = {k for k in (args.kinds or "").split(",") if k}
        trainer_maps = refs.trainer_maps(GAME)

        def select_trainer(trainer):
            return not prefixes or any(in_scope(mp, prefixes) for mp in trainer_maps.get(trainer, ()))

        def select_table(where, kind):
            return in_scope(where, prefixes) and (not kinds or kind in kinds)

    r = Replacer(args.table, args.fallback)
    if r.errors:
        print("\n".join(r.errors))
        sys.exit(1)
    party_in = read(args.party)
    wild_in = read(args.wild)
    party_out = r.party(party_in, select_trainer)
    wild_out = r.wild(wild_in, select_table)

    if r.missing:
        print("vanilla species in scope that the table does not cover (nothing written):")
        for name, wheres in sorted(r.missing.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            print(f"  {name}: {len(wheres)} ({', '.join(sorted(set(wheres))[:3])}{', ...' if len(set(wheres)) > 3 else ''})")
        sys.exit(1)
    print(f"party: {r.changed['party']} Pokemon, wild: {r.changed['wild']} slots"
          f"{' (dry run)' if args.dry_run else ''}")
    if not args.dry_run:
        for path, old, new in ((args.party, party_in, party_out), (args.wild, wild_in, wild_out)):
            if new != old:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)


if __name__ == "__main__":
    main()
