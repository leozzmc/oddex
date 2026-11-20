"""Tests for tools/headless/authoring/autopilot.py helpers (needs the built ELF, like check-oddex).

    python3 tools/oddex/test_autopilot.py
"""
import os, sys, unittest

AP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "headless", "authoring", "autopilot.py")
argv, sys.argv = sys.argv, [AP]
G = {"__file__": AP, "__name__": "autopilot_test"}
with open(AP) as f:
    exec(compile(f.read().replace("\nmain()\n", "\n"), AP, "exec"), G)
sys.argv = argv


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
