"""Tests for title_art.py: the title layer must fit vanilla's format (src/title_screen.c).

    python3 tools/oddex/test_title_art.py
"""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import title_art as ta  # noqa: E402


class Layer(unittest.TestCase):
    def setUp(self):
        self.g = ta.draw()
        self.tiles, self.entries = ta.tilemap(self.g)

    def test_fits_the_sheet_and_round_trips(self):
        self.assertLessEqual(len(self.tiles), 256)
        self.assertEqual(len(self.entries), 32 * 32)
        self.assertEqual(ta.untile(self.tiles, self.entries), self.g)
        self.assertTrue(all(e >> 12 == 14 for e in self.entries))   # BG palette 14 everywhere

    def test_mirrored_tiles_are_shared(self):
        g = [[ta.SKY[y // 8]] * ta.W for y in range(ta.H)]
        g[0][0] = g[0][15] = g[15][0] = ta.DARK   # one tile, its h-flip and its v-flip
        tiles, entries = ta.tilemap(g)
        self.assertEqual(entries[0] & 0x3FF, entries[1] & 0x3FF)
        self.assertEqual(entries[1] >> 10 & 3, 1)
        self.assertEqual(entries[32] >> 10 & 3, 2)
        self.assertEqual(ta.untile(tiles, entries), g)

    def test_colours_the_game_relies_on(self):
        self.assertEqual(ta.PALETTE[2], (255, 255, 255))     # the clouds' white
        self.assertEqual(ta.PALETTE[12], (180, 230, 172))    # the clouds' second colour
        used = {c for row in self.g for c in row}
        self.assertIn(ta.GLOW, used)       # index 15 is the one the game animates
        self.assertNotIn(0, used)          # nothing transparent: the backdrop flashes during the logo shine
        self.assertFalse(used & {12, 13, 14})

    def test_no_glow_under_press_start(self):
        x0, y0, x1, y1 = ta.PRESS_START
        self.assertFalse([(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if self.g[y][x] == ta.GLOW])


class Text(unittest.TestCase):
    GREYS = [(255, 74, 238)] + [(v, v, v) for v in (156, 90, 222, 24, 74, 238, 41, 172, 106, 189, 139, 205, 123, 65, 255)]

    def test_banner(self):
        rows = ta.banner(self.GREYS)
        self.assertEqual((len(rows), len(rows[0])), (32, 128))
        xs = [x for r in rows for x, c in enumerate(r) if c != ta.BANNER_PAL_KEY]
        self.assertTrue(90 <= max(xs) - min(xs) <= 126, (min(xs), max(xs)))   # five letters across both 64px sprites
        self.assertTrue(min(xs) < 32 and max(xs) > 96)
        self.assertIn(15, {c for r in rows for c in r})                        # white letters
        self.assertTrue(all(r[0] == r[-1] == ta.BANNER_PAL_KEY for r in rows))  # nothing cut off at the sides

    def test_fan_line(self):
        rows = ta.fan_line()
        self.assertEqual((len(rows), len(rows[0])), (8, 160))
        self.assertLessEqual({c for r in rows for c in r}, {0, 1, 3, 4, 5})     # the sheet's own shades
        xs = [x for r in rows for x, c in enumerate(r) if c]
        self.assertTrue(ta.LINE_X0 - 1 <= min(xs) and max(xs) <= ta.LINE_X1)
        mid = (min(xs) + max(xs)) / 2
        self.assertLess(abs(mid - (ta.LINE_X0 + ta.LINE_X1) / 2), 2)            # centred where vanilla's line was
        with self.assertRaises(SystemExit):
            ta.fan_line('FAN GAME, NOT OFFICIAL, NOT OFFICIAL')   # too wide for the line


if __name__ == '__main__':
    unittest.main()
