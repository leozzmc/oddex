"""Tests for tools/headless/authoring/autopilot.py and stepwalk.py (needs the built ELF, like check-oddex).

    python3 tools/oddex/test_autopilot.py
"""
import os, sys, unittest

AP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "headless", "authoring", "autopilot.py")
argv, sys.argv = sys.argv, [AP]
G = {"__file__": AP, "__name__": "autopilot_test"}
with open(AP) as f:
    exec(compile(f.read().replace("\nmain()\n", "\n"), AP, "exec"), G)
SW = os.path.join(os.path.dirname(AP), "stepwalk.py")
sys.argv = [SW]
S = {"__file__": SW, "__name__": "stepwalk_test"}
with open(SW) as f:
    exec(compile(f.read(), SW, "exec"), S)
sys.argv = argv


class StepwalkTest(unittest.TestCase):
    def test_bfs_shortest_path(self):
        grid = {(0, 0), (1, 0), (2, 0), (2, 1), (0, 1)}
        def nb(c):
            for d, (dx, dy) in S["DIRS"].items():
                if (c[0] + dx, c[1] + dy) in grid:
                    yield d, (c[0] + dx, c[1] + dy)
        self.assertEqual(S["bfs"]((0, 1), (2, 1), nb), ["UP", "RIGHT", "RIGHT", "DOWN"])
        self.assertIsNone(S["bfs"]((0, 1), (5, 5), nb))

    def test_lavaridge_gym_needs_its_holes_and_geysers(self):
        # Flannery's pocket on 1F is closed by a ledge you can only jump down: the way in goes
        # through B1F and back up a geyser, so the path takes warps ('|').
        gym = {"LavaridgeTown_Gym_1F", "LavaridgeTown_Gym_B1F"}
        path = S["bfs"](("LavaridgeTown_Gym_1F", 13, 18), ("LavaridgeTown_Gym_1F", 13, 10), S["warp_neighbors"](gym))
        self.assertIsNotNone(path)
        self.assertTrue(any(d.endswith("|") for d in path))
        # Below the ledge (row 13), straight up is not a way back.
        up = S["bfs"](("LavaridgeTown_Gym_1F", 13, 14), ("LavaridgeTown_Gym_1F", 13, 12), S["warp_neighbors"](gym))
        self.assertNotEqual(up, ["UP", "UP"])

    def test_exit_mat_is_pushed_again(self):
        # The gym's door mat (13,18) warps only when DOWN is pushed while standing on it.
        path = S["bfs"](("LavaridgeTown_Gym_1F", 13, 17), ("LavaridgeTown", 5, 16),
                        S["warp_neighbors"]({"LavaridgeTown", "LavaridgeTown_Gym_1F"}))
        self.assertEqual(path, ["DOWN", "DOWN|", "DOWN"])

    def test_ladders_and_doors_are_warps(self):
        tower = {"MirageTower_1F", "MirageTower_2F", "Route111"}
        path = S["bfs"](("MirageTower_1F", 10, 13), ("MirageTower_2F", 15, 3), S["warp_neighbors"](tower))
        self.assertIsNotNone(path)
        self.assertTrue(path[-2].endswith("|"))
        # A building door has collision; walking into it opens it.
        house = {"VerdanturfTown", "VerdanturfTown_FriendshipRatersHouse"}
        path = S["bfs"](("VerdanturfTown", 1, 15), ("VerdanturfTown_FriendshipRatersHouse", 4, 5), S["warp_neighbors"](house))
        self.assertEqual(path[0], "UP|")

    def test_surf_crosses_route118s_river(self):
        cross = lambda surf: S["bfs"](("Route118", 10, 9), ("Route118", 32, 9), S["warp_neighbors"]({"Route118"}, surf))
        self.assertIsNone(cross(False))
        self.assertIsNotNone(cross(True))

    def test_fortree_gym_needs_its_gates_turned(self):
        gs = S["gates"]("FortreeCity_Gym")
        self.assertEqual(len(gs), 8)
        start = ("FortreeCity_Gym", 15, 23, tuple(g[3] for g in gs))
        at_winona = lambda s: s[:3] == ("FortreeCity_Gym", 15, 3)
        path = S["bfs"](start, at_winona, S["gate_neighbors"]("FortreeCity_Gym"))
        self.assertIsNotNone(path)
        frozen = lambda cur: ((d, n) for d, n in S["gate_neighbors"]("FortreeCity_Gym")(cur) if n[3] == cur[3])
        self.assertIsNone(S["bfs"](start, at_winona, frozen))

    def test_mossdeep_gym_needs_its_floor_switches(self):
        nb = S["puzzle_neighbors"]("MossdeepCity_Gym")
        start = ("MossdeepCity_Gym", 7, 34, nb.start)
        at_leaders = lambda s: s[1:3] == (23, 8)  # below Tate
        path = S["bfs"](start, at_leaders, nb)
        self.assertIsNotNone(path)
        self.assertTrue(any(d.endswith("|") for d in path))  # the pads warp inside the gym
        still = lambda cur: ((d, n) for d, n in nb(cur) if n[3] == cur[3])  # no statue ever moves
        self.assertIsNone(S["bfs"](start, at_leaders, still))

    def test_warps_outside_their_map_are_ignored(self):
        # A Slateport map lists a warp past its layout; a search that visits them all must not crash.
        maps = {n for n in G["ID2NAME"].values() if n.split("_")[0] == "SlateportCity"}
        self.assertIsNone(S["bfs"](("SlateportCity_Harbor", 8, 13), ("SlateportCity", 28, 13), S["warp_neighbors"](maps)))


class StageReachTest(unittest.TestCase):
    def test_surf_opens_the_sea(self):
        import subprocess
        sr = os.path.join(os.path.dirname(AP), "stage_reach.py")
        def maps(*flags):
            out = subprocess.run([sys.executable, "-I", sr, "Route104", "32", "43", "Route104,Route105", *flags],
                                 capture_output=True, text=True, check=True).stdout
            return out.splitlines()[0]
        self.assertNotIn("Route105", maps())
        self.assertIn("Route105", maps("--surf"))


class AutopilotTest(unittest.TestCase):
    def test_hm_moves_are_the_eight_hms(self):
        names = {G["W"]["move_names"]()[m] for m in G["hm_moves"]()}
        self.assertEqual(names, {"CUT", "FLY", "SURF", "STRENGTH", "FLASH", "ROCK_SMASH", "WATERFALL", "DIVE"})

    def test_counter_users_get_special_moves(self):
        self.assertLess(G["reflect_factor"](False, {"COUNTER", "YAWN"}), 1)
        self.assertEqual(G["reflect_factor"](True, {"COUNTER", "YAWN"}), 1)
        self.assertLess(G["reflect_factor"](True, {"MIRROR_COAT"}), 1)

    def test_replacement_is_the_strongest_benched_member(self):
        party = [(40, 121), (23, 0), (4, 17), (25, 71), (0, 0), (0, 0)]
        self.assertEqual(G["replacement"](party, {0}), 3)          # not the fainted one, not Lv4
        self.assertIsNone(G["replacement"]([(40, 0), (23, 0)], set()))

    def test_turning_releases_the_pad_first(self):
        # Facing UP after a hold, the next leg goes LEFT: a release frame comes before the turn tap,
        # or the tap would continue the walk a tile.
        cmds, _, facing, _ = G["units"](("LittlerootTown", 10, 10), ("LittlerootTown", 6, 10), "UP", True)
        self.assertEqual(cmds[:2], ["wait 2", "press LEFT 3 20"])
        self.assertEqual(facing, "LEFT")


if __name__ == "__main__":
    unittest.main()
