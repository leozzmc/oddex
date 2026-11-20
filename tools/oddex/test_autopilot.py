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


class AutopilotTest(unittest.TestCase):
    def test_hm_moves_are_the_eight_hms(self):
        names = {G["W"]["move_names"]()[m] for m in G["hm_moves"]()}
        self.assertEqual(names, {"CUT", "FLY", "SURF", "STRENGTH", "FLASH", "ROCK_SMASH", "WATERFALL", "DIVE"})

    def test_turning_releases_the_pad_first(self):
        # Facing UP after a hold, the next leg goes LEFT: a release frame comes before the turn tap,
        # or the tap would continue the walk a tile.
        cmds, _, facing, _ = G["units"](("LittlerootTown", 10, 10), ("LittlerootTown", 6, 10), "UP", True)
        self.assertEqual(cmds[:2], ["wait 2", "press LEFT 3 20"])
        self.assertEqual(facing, "LEFT")


if __name__ == "__main__":
    unittest.main()
