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


if __name__ == '__main__':
    unittest.main()
