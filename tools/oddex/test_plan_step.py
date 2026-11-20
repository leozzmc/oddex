"""Tests for tools/headless/authoring/plan.py's step() across map connections.

    python3 tools/oddex/test_plan_step.py
"""
import os, sys, unittest

PLAN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "headless", "authoring", "plan.py")
argv, sys.argv = sys.argv, [PLAN]
P = {"__file__": PLAN}
with open(PLAN) as f:
    exec(f.read().split("if __name__")[0], P)
sys.argv = argv


class StepTest(unittest.TestCase):
    def test_a_side_with_two_connections(self):
        # Route 111's left side is Route 113 (offset 0) and Route 112 (offset 20).
        self.assertEqual(P["step"]("Route111", 0, 5, "LEFT"), ("Route113", P["load"]("Route113")["W"] - 1, 5))
        self.assertEqual(P["step"]("Route111", 0, 25, "LEFT"), ("Route112", P["load"]("Route112")["W"] - 1, 5))

    def test_past_the_end_of_a_narrower_neighbor(self):
        # Route 110's left is Route 103 at offset 60; Route 103 is shorter than the rest of that edge.
        h = P["load"]("Route103")["H"]
        self.assertEqual(P["step"]("Route110", 0, 61, "LEFT"), ("Route103", P["load"]("Route103")["W"] - 1, 1))
        self.assertIsNone(P["step"]("Route110", 0, 60 + h, "LEFT"))


if __name__ == "__main__":
    unittest.main()
