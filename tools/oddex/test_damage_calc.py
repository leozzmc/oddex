"""Tests for damage_calc.py: the damage formula, type chart, trainer lookup and party parsing.

    python3 tools/oddex/test_damage_calc.py
"""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import damage_calc as dc  # noqa: E402

MOVES = {'TACKLE': {'power': 40, 'type': 'NORMAL', 'category': 'PHYSICAL', 'effect': 'HIT'},
         'EMBER': {'power': 40, 'type': 'FIRE', 'category': 'SPECIAL', 'effect': 'HIT'},
         'SEISMIC_TOSS': {'power': 1, 'type': 'FIGHTING', 'category': 'PHYSICAL', 'effect': 'LEVEL_DAMAGE'},
         'FOCUS_PUNCH': {'power': 150, 'type': 'FIGHTING', 'category': 'PHYSICAL', 'effect': 'FOCUS_PUNCH'},
         'ARM_THRUST': {'power': 15, 'type': 'FIGHTING', 'category': 'PHYSICAL', 'effect': 'MULTI_HIT'},
         'GROWL': {'power': 0, 'type': 'NORMAL', 'category': 'STATUS', 'effect': 'ATTACK_DOWN'}}


def mon(level, types, atk=50, de=50, spa=50, spd=50, weight=100):
    return {'level': level, 'types': types, 'weight': weight,
            'stats': {'hp': 50, 'atk': atk, 'def': de, 'spa': spa, 'spd': spd, 'spe': 50}}


class Formula(unittest.TestCase):
    def test_base_damage(self):
        # Level 10, power 40, A = D: floor(floor(6 * 40 * 1) / 50) + 2 = 6, no STAB, neutral.
        a, d = mon(10, ['WATER']), mon(10, ['WATER'])
        self.assertEqual(dc.damage(a, d, 'TACKLE', MOVES), (5, 6))

    def test_stab_and_type(self):
        a, d = mon(10, ['FIRE']), mon(10, ['GRASS'])
        lo, hi = dc.damage(a, d, 'EMBER', MOVES)
        self.assertEqual(hi, 18)   # 6 x STAB 1.5 x 2 (fire on grass)

    def test_immunity_and_fixed(self):
        a, d = mon(16, ['FIGHTING']), mon(16, ['GHOST'])
        self.assertEqual(dc.damage(a, d, 'SEISMIC_TOSS', MOVES), (0, 0))
        self.assertEqual(dc.damage(a, mon(16, ['NORMAL']), 'SEISMIC_TOSS', MOVES), (16, 16))

    def test_skipped_moves(self):
        a, d = mon(16, ['FIGHTING']), mon(16, ['NORMAL'])
        self.assertIsNone(dc.damage(a, d, 'GROWL', MOVES))
        self.assertIsNone(dc.damage(a, d, 'FOCUS_PUNCH', MOVES))

    def test_multi_hit_range(self):
        a, d = mon(16, ['FIGHTING']), mon(16, ['NORMAL'])
        one = dc.damage(a, d, 'TACKLE', {**MOVES, 'TACKLE': {**MOVES['ARM_THRUST'], 'effect': 'HIT'}})
        lo, hi = dc.damage(a, d, 'ARM_THRUST', MOVES)
        self.assertEqual((lo, hi), (one[0] * 2, one[1] * 5))

    def test_type_chart(self):
        self.assertEqual(dc.effectiveness('FIGHTING', ['GRASS', 'DARK']), 2)
        self.assertEqual(dc.effectiveness('FIGHTING', ['FIRE', 'STEEL']), 2)
        self.assertEqual(dc.effectiveness('FIGHTING', ['WATER', 'FLYING']), 0.5)
        self.assertEqual(dc.effectiveness('ELECTRIC', ['WATER', 'FLYING']), 4)
        self.assertEqual(dc.effectiveness('GROUND', ['WATER', 'FLYING']), 0)


class Party(unittest.TestCase):
    def test_both_spellings(self):
        a = dc.load_party('BRAWLY_1')
        b = dc.load_party('TRAINER_BRAWLY_1')
        self.assertEqual(a, b)
        self.assertGreaterEqual(len(a), 2)
        self.assertTrue(all(m['moves'] and m['level'] > 1 for m in a))

    def test_unknown_trainer(self):
        with self.assertRaises(SystemExit) as e:
            dc.load_party('BRAWLY_99')
        self.assertIn('no trainer TRAINER_BRAWLY_99', str(e.exception.code))


class Moves(unittest.TestCase):
    def test_aerial_ace_data(self):
        moves = dc.load_moves()
        self.assertEqual(moves['AERIAL_ACE']['type'], 'FLYING')
        self.assertEqual(moves['AERIAL_ACE']['power'], 60)
        self.assertEqual(moves['AERIAL_ACE']['category'], 'PHYSICAL')


if __name__ == '__main__':
    unittest.main()
