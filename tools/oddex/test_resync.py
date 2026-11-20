"""Tests for tools/headless/authoring/resync.py's pure parts (chunking, acceptance, reassembly).

    python3 tools/oddex/test_resync.py
"""
import importlib.util, os, tempfile, unittest

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "headless", "authoring", "resync.py")
spec = importlib.util.spec_from_file_location("resync", P)
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)


class ResyncTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        open(os.path.join(self.d, "a.txt"), "w").write("# a\nwait 1\nwait 2\n")
        body = "\n".join(f"hold UP {i}" for i in range(1, 42))
        open(os.path.join(self.d, "b.txt"), "w").write(f"# b\ninclude a.txt\nwait 3\n# part two\n{body}\nshot shots/x.png\n")

    def test_chunks_break_at_files_comments_and_forty_commands(self):
        ch = R.flatten("b.txt", self.d)
        self.assertEqual([(c["file"], len(c["lines"])) for c in ch], [("a.txt", 2), ("b.txt", 1), ("b.txt", 40), ("b.txt", 2)])
        self.assertEqual(ch[3]["lines"][-1][1], "shot shots/x.png")

    def test_acceptance_needs_place_level_and_trainers(self):
        old = ("Route110", 4, 33, True, 30, 50)
        self.assertTrue(R.accept(("Route110", 4, 33, True, 30, 50), old, 50, True))
        self.assertFalse(R.accept(("Route110", 4, 33, True, 30, 49), old, 50, True))   # skipped a trainer
        self.assertFalse(R.accept(("Route110", 4, 33, True, 29, 50), old, 50, True))   # lower level
        self.assertFalse(R.accept(("Route110", 4, 33, False, 30, 50), old, 50, True))  # stuck in a message
        self.assertTrue(R.accept(("Route110", 4, 33, False, 30, 50), old[:3] + (False,) + old[4:], 50, False))

    def test_assemble_keeps_unchanged_text_and_replaces_chunks(self):
        ch = R.flatten("b.txt", self.d)
        same = R.assemble(ch, {k: [l for _, l in c["lines"]] for k, c in enumerate(ch)}, 1, self.d)
        self.assertEqual(same["b.txt"], open(os.path.join(self.d, "b.txt")).read())
        new = R.assemble(ch, {1: ["wait 9"], 2: ["hold UP 1"], 3: []}, 1, self.d)
        self.assertEqual(new["b.txt"], "# b\ninclude a.txt\nwait 9\n# part two\nhold UP 1\n")
        self.assertNotIn("a.txt", new)


if __name__ == "__main__":
    unittest.main()
