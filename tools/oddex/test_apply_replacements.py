"""Tests for apply_replacements.py on scratch copies of the game's data (the real files are untouched).

The trainer and wild data come from FIXTURE_REF, a commit from before any scope was migrated, so the
expectations do not change as content/migration_scope.toml scopes are migrated.

    python3 tools/oddex/test_apply_replacements.py
"""
import collections, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apply_replacements as ar  # noqa: E402
import check_species_refs as refs  # noqa: E402

TOOL = os.path.join(HERE, "apply_replacements.py")
FIXTURE_REF = "7910be01"  # develop before plan B step 4b: Routes 101-103 still vanilla
def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


EARLY_TABLE = """
[replace]
POOCHYENA = "SHACHOUND"
ZIGZAGOON = "KYOKON"
WURMPLE = "USOBUZZ"
WINGULL = "UTOGHAST"
LOTAD = "SHOJOBOB"
SEEDOT = "BEKURAMA"
RALTS = "OMOTELLE"
SHROOMISH = "YAMAMBRR"
TAILLOW = "SHAWABOLT"
"""


class ApplyReplacementsTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.party = os.path.join(self.dir, "trainers.party")
        self.wild = os.path.join(self.dir, "wild_encounters.json")
        for src, dst in ((ar.PARTY, self.party), (ar.WILD, self.wild)):
            rel = os.path.relpath(src, os.path.dirname(ar.GAME))
            data = subprocess.run(["git", "-C", ar.GAME, "show", f"{FIXTURE_REF}:{rel}"],
                                  capture_output=True, check=True).stdout
            with open(dst, "wb") as f:
                f.write(data)
        self.party0 = read(self.party)
        self.wild0 = read(self.wild)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def table(self, text, name="table.toml"):
        path = os.path.join(self.dir, name)
        with open(path, "w") as f:
            f.write(text)
        return path

    def run_tool(self, *args, table=EARLY_TABLE):
        cmd = [sys.executable, "-I", TOOL, "--table", self.table(table), "--party", self.party, "--wild", self.wild, *args]
        return subprocess.run(cmd, capture_output=True, text=True)

    def files(self):
        return read(self.party), read(self.wild)

    @staticmethod
    def changed_lines(a, b):
        la, lb = a.split("\n"), b.split("\n")
        assert len(la) == len(lb), "line count changed"
        return [(x, y) for x, y in zip(la, lb) if x != y]

    def test_rewrites_only_species_tokens_in_scope(self):
        r = self.run_tool("--maps", "Route101,Route102", "--kinds", "land_mons")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        party, wild = self.files()
        # Route 102 trainers: Calvin, Rick x2, Tiana x2, Allen x2. Route 101 has none.
        pc = self.changed_lines(self.party0, party)
        self.assertEqual(len(pc), 7, pc)
        for old, new in pc:
            self.assertIn(new.strip(), {"Shachound", "Kyokon", "Usobuzz", "Yamambrr", "Shawabolt"}, (old, new))
        # 12 land slots each on Route 101 and Route 102; only the "species" value changes.
        wc = self.changed_lines(self.wild0, wild)
        self.assertEqual(len(wc), 24, wc[:3])
        for old, new in wc:
            self.assertEqual(old.split('"species"')[0], new.split('"species"')[0])
            self.assertIn('"SPECIES_', new)
        a, b = json.loads(self.wild0), json.loads(wild)
        self.assertEqual(json.dumps(a, sort_keys=True).count('"species"'), json.dumps(b, sort_keys=True).count('"species"'))
        self.assertIn("party: 7 Pokemon, wild: 24 slots", r.stdout)

    def test_second_run_changes_nothing(self):
        self.assertEqual(self.run_tool("--maps", "Route101,Route102", "--kinds", "land_mons").returncode, 0)
        once = self.files()
        r = self.run_tool("--maps", "Route101,Route102", "--kinds", "land_mons")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(self.files(), once)
        self.assertIn("party: 0 Pokemon, wild: 0 slots", r.stdout)

    def test_missing_species_are_all_listed_and_nothing_is_written(self):
        r = self.run_tool("--maps", "Route102")
        self.assertEqual(r.returncode, 1)
        for name in ("CORPHISH", "MARILL", "GOLDEEN", "MAGIKARP"):
            self.assertIn(name, r.stdout)
        self.assertEqual(self.files(), (self.party0, self.wild0))

    def test_fallback_covers_the_rest(self):
        r = self.run_tool("--maps", "Route102", "--fallback", "SHACHOUND")
        self.assertEqual(r.returncode, 0, r.stdout)
        enc = [e for g in json.loads(self.files()[1])["wild_encounter_groups"] for e in g.get("encounters", [])
               if e.get("map") == "MAP_ROUTE102"]
        species = {m["species"] for e in enc for k, t in e.items() if isinstance(t, dict) for m in t.get("mons", [])}
        vanilla = refs.load_species(ar.GAME)[0]
        self.assertFalse(species & vanilla, species & vanilla)

    def test_out_of_scope_maps_are_untouched(self):
        self.assertEqual(self.run_tool("--maps", "Route101,Route102", "--kinds", "land_mons").returncode, 0)
        before = [e for g in json.loads(self.wild0)["wild_encounter_groups"] for e in g.get("encounters", [])
                  if e.get("map") == "MAP_ROUTE104"]
        after = [e for g in json.loads(self.files()[1])["wild_encounter_groups"] for e in g.get("encounters", [])
                 if e.get("map") == "MAP_ROUTE104"]
        self.assertEqual(before, after)

    def test_dry_run_writes_nothing(self):
        r = self.run_tool("--maps", "Route101,Route102", "--kinds", "land_mons", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("(dry run)", r.stdout)
        self.assertEqual(self.files(), (self.party0, self.wild0))

    def test_stage_mismatch_fails_unless_allowed(self):
        r = self.run_tool("--dry-run", table='[replace]\nMIGHTYENA = "SHACHOUND"\n')
        self.assertEqual(r.returncode, 1)
        self.assertIn("MIGHTYENA is evolution stage 2 but SHACHOUND is stage 1", r.stdout)
        r = self.run_tool("--maps", "Route101", "--kinds", "land_mons", "--dry-run",
                          table='stage_mismatch_ok = ["MIGHTYENA"]\n' + EARLY_TABLE + 'MIGHTYENA = "SHACHOUND"\n')
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_unknown_keys_and_values_fail(self):
        r = self.run_tool("--dry-run", table='[replace]\nNOTAMON = "SHACHOUND"\nPOOCHYENA = "NOTREAL"\n')
        self.assertEqual(r.returncode, 1)
        self.assertIn("table key NOTAMON is not a vanilla species", r.stdout)
        self.assertIn("table value NOTREAL", r.stdout)
        self.assertEqual(self.files(), (self.party0, self.wild0))

    def test_party_line_forms(self):
        for line, species in [
            ("Poochyena", "Poochyena"),
            ("Poochyena @ Oran Berry", "Poochyena"),
            ("Poochyena (M)", "Poochyena"),
            ("Rex (Poochyena) (F) @ Oran Berry", "Poochyena"),
            ("SPECIES_POOCHYENA @ ITEM_ORAN_BERRY", "SPECIES_POOCHYENA"),
            ("Mr. Mime", "Mr. Mime"),
        ]:
            a, b = ar.species_span(line)
            self.assertEqual(line[a:b], species, line)

    def test_display_name_round_trips_through_trainerproc_rules(self):
        for oddex_id in ("SHADEPUP", "FOO_BAR", "MOSS2"):
            self.assertEqual(refs.party_species_token(ar.display_name(oddex_id)), "SPECIES_" + oddex_id)

    # --- content/migration_scope.toml -------------------------------------------------------

    def test_scope_early_rewrites_its_trainers_and_land_tables_only(self):
        r = self.run_tool("--scope", "early")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Route 102's four trainers (the Route 103 rival is already role aliases); 12 land slots
        # each on Route 101/102/103. Route 103's mid-game trainers and water/fishing stay vanilla.
        self.assertIn("party: 7 Pokemon, wild: 36 slots", r.stdout)
        party, wild = self.files()
        self.assertIn("Skitty", party)  # Miguel on Route 103 is out of scope
        enc = {e["map"]: e for g in json.loads(wild)["wild_encounter_groups"] for e in g.get("encounters", [])
               if e.get("map") in ("MAP_ROUTE102", "MAP_ROUTE103")}
        self.assertIn("SPECIES_MAGIKARP", {m["species"] for m in enc["MAP_ROUTE102"]["fishing_mons"]["mons"]})

    def test_scope_and_ad_hoc_options_are_exclusive(self):
        r = self.run_tool("--scope", "early", "--maps", "Route101")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.files(), (self.party0, self.wild0))

    def test_check_species_refs_reads_the_same_scope_file(self):
        cmd = [sys.executable, "-I", os.path.join(HERE, "check_species_refs.py"), "--scope", "early", "--json"]
        found = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
        by_cat = collections.Counter(f["category"] for f in found)
        # [early] is migrated (strict since step 4b): nothing is left in the real game data, including
        # data/scripts/players_house.inc (script_files); the Johto starters are in exclude_refs.
        self.assertEqual(sum(by_cat.values()), 0, found[:3])

    def test_strict_scope_with_vanilla_left_fails(self):
        # Reads the real game: Victory Road stays vanilla until its own scope is migrated.
        # shortcut: needs a still-vanilla map, use a FIXTURE_REF game tree once Victory Road is migrated
        scope = self.table('[early]\nstrict = true\nwild_maps = ["VictoryRoad_1F"]\nwild_kinds = ["land_mons"]\n',
                           "scope.toml")
        cmd = [sys.executable, "-I", os.path.join(HERE, "check_species_refs.py"), "--strict-scopes", "--summary",
               "--scope-file", scope]
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("strict scopes: early", r.stdout)
        self.assertIn("wild           12 refs", r.stdout)

    def test_script_files_bring_shared_scripts_into_scope(self):
        # cave_of_origin.inc (data/scripts/) has a playmoncry SPECIES_KYOGRE (and GROUDON in a comment);
        # no map's `maps` entry covers it, so it is in scope only through script_files.
        # shortcut: needs a still-vanilla shared script (Kyogre is endgame), use a fixture game tree once it is migrated
        def refs(body):
            scope = self.table(body, "scope.toml")
            cmd = [sys.executable, "-I", os.path.join(HERE, "check_species_refs.py"), "--scope", "s", "--json",
                   "--scope-file", scope]
            return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
        self.assertEqual(refs('[s]\nmaps = ["Route101"]\n'), [])  # migrated map, no shared script
        found = refs('[s]\nscript_files = ["data/scripts/cave_of_origin.inc"]\n')
        self.assertEqual({f["file"] for f in found}, {"data/scripts/cave_of_origin.inc"})
        self.assertIn("SPECIES_KYOGRE", {f["species"] for f in found})
        excl = ", ".join(sorted({f'"data/scripts/cave_of_origin.inc:{f["species"]}"' for f in found}))
        excluded = refs(f'[s]\nscript_files = ["data/scripts/cave_of_origin.inc"]\nexclude_refs = [{excl}]\n')
        self.assertEqual(excluded, [])

    def test_roles_pointing_at_vanilla_resolve_to_it(self):
        # A role left on a vanilla species (e.g. EGG_GIFT before its original exists) must be
        # reported like the vanilla species itself, not hidden behind SPECIES_ODDEX_*.
        game = os.path.join(self.dir, "game")
        for rel, text in (("src/data/pokemon/species_info/gen_3_families.h", "    [SPECIES_WYNAUT] =\n"),
                          ("include/constants/species.h", "    SPECIES_WYNAUT = 360,\n"),
                          ("include/constants/oddex_species.h", "#define SPECIES_ODDEX_EGG_GIFT    SPECIES_WYNAUT\n")):
            os.makedirs(os.path.dirname(os.path.join(game, rel)), exist_ok=True)
            with open(os.path.join(game, rel), "w", encoding="utf-8") as f:
                f.write(text)
        vanilla, _, aliases = refs.load_species(game)
        self.assertIn(aliases["SPECIES_ODDEX_EGG_GIFT"], vanilla)

    def test_dialogue_scan_knows_form_aliases(self):
        # The Weather Institute said "received CASTFORM!" and nothing flagged it: the species key is
        # SPECIES_CASTFORM_NORMAL, the word in the text is its alias.
        words = refs.text_words({"SPECIES_CASTFORM_NORMAL", "SPECIES_ZUBAT"},
                                {"SPECIES_CASTFORM": "SPECIES_CASTFORM_NORMAL", "SPECIES_ODDEX_PEEKO": "SPECIES_ZUBAT"})
        self.assertEqual(words, {"CASTFORM", "ZUBAT"})

    def test_exclude_refs_also_hold_back_apply_replacements(self):
        # Altering Cave's tables 2-9 only switch in by a Mystery Event: exclude_refs keeps their species
        # out, so a table that maps Zubat (table 1) is enough.
        others = ["MAREEP", "PINECO", "HOUNDOUR", "TEDDIURSA", "AIPOM", "SHUCKLE", "STANTLER", "SMEARGLE"]
        body = '[s]\nwild_maps = ["AlteringCave"]\n'
        r = self.run_tool("--scope", "s", "--scope-file", self.table(body, "s.toml"), table='[replace]\nZUBAT = "KOMORIMEN"\n')
        self.assertEqual(r.returncode, 1)
        self.assertIn("MAREEP", r.stdout)
        excl = ", ".join(f'"src/data/wild_encounters.json:SPECIES_{s}"' for s in others)
        r = self.run_tool("--scope", "s", "--scope-file", self.table(body + f"exclude_refs = [{excl}]\n", "s.toml"),
                          table='[replace]\nZUBAT = "KOMORIMEN"\n')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("wild: 12 slots", r.stdout)
        self.assertIn("SPECIES_MAREEP", read(self.wild))
        # check_species_refs reads exclude_refs the same way, for wild and party findings too.
        cmd = [sys.executable, "-I", os.path.join(HERE, "check_species_refs.py"), "--scope", "s", "--json",
               "--scope-file", self.table(body + f"exclude_refs = [{excl}]\n", "s.toml")]
        found = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
        self.assertFalse({f["species"] for f in found} & {f"SPECIES_{s}" for s in others})

    def test_partners_are_scanned_and_rewritten_like_trainers(self):
        # battle_partners.party (Steven in the Space Center) has the trainers.party format.
        partners = os.path.join(self.dir, "battle_partners.party")
        with open(partners, "w") as f:
            f.write("=== PARTNER_NONE ===\nName:\n\n=== PARTNER_STEVEN ===\nName: STEVEN\nAI: Basic Trainer\n\n"
                    "Metang\nLevel: 42\n- Psychic\n\nSkarmory @ Leftovers\nLevel: 43\n- Steel Wing\n")
        body = '[s]\npartners = ["PARTNER_STEVEN"]\n'
        table = 'stage_mismatch_ok = ["SKARMORY"]\n[replace]\nSKARMORY = "DAIBEKI"\n'
        r = self.run_tool("--scope", "s", "--scope-file", self.table(body, "s.toml"), "--partners", partners, table=table)
        self.assertEqual(r.returncode, 1)  # Metang has no mapping: listed, nothing written
        self.assertIn("METANG: 1 (PARTNER_STEVEN (battle_partners.party:8))", r.stdout)
        self.assertIn("Skarmory @ Leftovers", read(partners))
        excl = body + 'exclude_refs = ["src/data/battle_partners.party:SPECIES_METANG"]\n'
        r = self.run_tool("--scope", "s", "--scope-file", self.table(excl, "s.toml"), "--partners", partners, table=table)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("party: 1 Pokemon", r.stdout)
        self.assertIn("Metang\nLevel: 42", read(partners))
        self.assertIn("Daibeki @ Leftovers\nLevel: 43", read(partners))
        self.assertEqual(self.files(), (self.party0, self.wild0))
        # A scope without the partner leaves the file alone, and an unknown partner is a scope error.
        r = self.run_tool("--scope", "s", "--scope-file", self.table('[s]\npartners = ["PARTNER_NOBODY"]\n', "s.toml"),
                          "--partners", partners, table=table)
        self.assertIn("partners: PARTNER_NOBODY is not in battle_partners.party", r.stderr + r.stdout)

    def test_check_species_refs_sees_partner_parties(self):
        # On a scratch file, so it does not depend on which partners the game has migrated.
        import types
        path = "src/data/battle_partners.party"
        os.makedirs(os.path.join(self.dir, "src", "data"))
        with open(os.path.join(self.dir, path), "w") as f:
            f.write("=== PARTNER_STEVEN ===\nName: STEVEN\nAI: Basic Trainer\n\nMetang\nLevel: 42\n- Psychic\n")
        found = []
        refs.scan_party_file(self.dir, lambda *a: found.append(a), path)
        self.assertEqual(found, [("party", path, 5, "SPECIES_METANG", "PARTNER_STEVEN")])
        finding = {"category": "party", "file": path, "species": "SPECIES_METANG", "context": "PARTNER_STEVEN"}
        scope = types.SimpleNamespace(trainers=set(), partners={"PARTNER_STEVEN"}, excludes=lambda p, sp: False)
        self.assertTrue(refs.in_scope(finding, scope))
        scope.partners = set()
        self.assertFalse(refs.in_scope(finding, scope))

    def test_wild_maps_map_kind_takes_one_table(self):
        # "VictoryRoad_B1F:rock_smash_mons" takes that one table, whatever wild_kinds says;
        # Sky Pillar follows wild_kinds and has no fishing table.
        # shortcut: needs still-vanilla maps (Victory Road is endgame), use a fixture game tree once they are migrated
        scope = self.table('[s]\nwild_maps = ["VictoryRoad_B1F:rock_smash_mons", "SkyPillar_1F"]\nwild_kinds = ["fishing_mons"]\n',
                           "scope.toml")
        cmd = [sys.executable, "-I", os.path.join(HERE, "check_species_refs.py"), "--scope", "s", "--json",
               "--scope-file", scope]
        found = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
        self.assertEqual({f["context"] for f in found}, {"VictoryRoad_B1F:rock_smash_mons"})
        bad = self.table('[s]\nwild_maps = ["Route111:sand_mons"]\n', "bad.toml")
        r = self.run_tool("--scope", "s", "--scope-file", bad, "--dry-run")
        self.assertIn("Route111:sand_mons: unknown kind sand_mons", r.stdout + r.stderr)

    def test_script_files_must_be_shared_scripts(self):
        scope = self.table('[bad]\nscript_files = ["data/scripts/nope.inc", "data/maps/Route101/scripts.inc"]\n',
                           "scope.toml")
        r = self.run_tool("--scope", "bad", "--scope-file", scope, "--dry-run")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("data/scripts/nope.inc does not exist", r.stdout + r.stderr)
        self.assertIn("data/maps/Route101/scripts.inc is not a data/scripts/*.inc file", r.stdout + r.stderr)

    def test_scope_file_typos_fail(self):
        scope = self.table('[bad]\ntrainers = ["TRAINER_NOBODY"]\nmaps = ["Nowhere*"]\nwlid_maps = []\n', "scope.toml")
        r = self.run_tool("--scope", "bad", "--scope-file", scope, "--dry-run")
        self.assertNotEqual(r.returncode, 0)
        for text in ("unknown field wlid_maps", "TRAINER_NOBODY is not in trainers.party", "Nowhere* matches no map"):
            self.assertIn(text, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
