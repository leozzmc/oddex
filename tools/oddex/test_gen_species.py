"""Tests for gen_species.warnings() on small made-up species (the real content is untouched).

    python3 tools/oddex/test_gen_species.py
"""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_species as gs  # noqa: E402


def sp(sid, moves, into=None):
    return {'id': sid, '_file': f'{sid.lower()}.toml', 'learnset': {'level': moves},
            'evolutions': [{'method': 'LEVEL', 'param': 16, 'into': into}] if into else []}


class Warnings(unittest.TestCase):
    def test_level_1_evolution_move(self):
        base = sp('A', [[1, 'TACKLE']], into='B')
        bad = gs.warnings([base, sp('B', [[1, 'NIGHT_SLASH'], [1, 'TACKLE']])], ['A', 'B'])
        self.assertEqual(len(bad), 1)
        self.assertIn('NIGHT_SLASH', bad[0])
        # Level 0 is taught on evolution; level 1 moves the first stage already knows are fine.
        self.assertEqual(gs.warnings([base, sp('B', [[0, 'NIGHT_SLASH'], [1, 'TACKLE']])], ['A', 'B']), [])
        self.assertEqual(gs.warnings([base, sp('B', [[1, 'TACKLE'], [5, 'BITE']])], ['A', 'B']), [])

    def test_dex_keeps_lines_together(self):
        species = [sp('A', [], into='B'), sp('B', []), sp('C', [])]
        self.assertEqual(gs.warnings(species, ['A', 'B', 'C']), [])
        apart = gs.warnings(species, ['A', 'C', 'B'])
        self.assertEqual(len(apart), 1)
        self.assertIn('B should come right after A', apart[0])


class Hms(unittest.TestCase):
    def test_unlearnable_hms(self):
        species = [{'learnset': {'teachable': ['CUT', 'SURF']}}, {'learnset': {}}]
        self.assertEqual(gs.unlearnable_hms(species, ['CUT', 'SURF', 'DIVE']), ['DIVE'])

    def test_game_hm_list(self):   # reads FOREACH_HM from the game's tms_hms.h
        self.assertEqual(gs.unlearnable_hms([], None)[:2], ['CUT', 'FLY'])


if __name__ == '__main__':
    unittest.main()
