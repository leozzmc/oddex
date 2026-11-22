"""Tests for blender/make_art.py: the hand-placed pixel overlay.

    python3 tools/oddex/test_make_art.py
"""
import os, sys, unittest

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'blender'))
import make_art as ma  # noqa: E402

PAL = [(152, 200, 176), (20, 20, 20), (250, 250, 250), (200, 30, 30)]


def sheet(w, h, box):
    im = Image.new('P', (w, h), 0)
    im.putpalette([c for rgb in PAL for c in rgb] + [0] * (768 - 3 * len(PAL)))
    im.paste(3, box)
    return im


class Pixels(unittest.TestCase):
    def test_paints_nearest_palette_entry_and_skips_dots(self):
        front = sheet(64, 128, (10, 20, 30, 40))
        front.paste(3, (10, 84, 30, 104))   # the second frame
        pixels = {'keys': {'k': (0, 0, 0), 'w': (255, 255, 255)},
                  'front': {'box': (10, 20, 30, 40), 'patches': [((12, 22), ['kw.', '.k.'])]},
                  'front2': {'box': (10, 20, 30, 40), 'patches': [((12, 23), ['kw'])]}}
        ma.apply_pixels({'front': front}, {'front': PAL}, pixels)
        self.assertEqual([front.getpixel((x, 22)) for x in (12, 13, 14)], [1, 2, 3])
        self.assertEqual([front.getpixel((x, 23)) for x in (12, 13)], [3, 1])
        self.assertEqual([front.getpixel((x, 64 + 23)) for x in (12, 13)], [1, 2])   # frame 2 is 64 lower

    def test_a_moved_sprite_fails_instead_of_misplacing_the_eyes(self):
        front = sheet(64, 128, (11, 20, 31, 40))
        pixels = {'keys': {'k': (0, 0, 0)}, 'front': {'box': (10, 20, 30, 40), 'patches': [((12, 22), ['k'])]}}
        with self.assertRaises(SystemExit) as e:
            ma.apply_pixels({'front': front}, {'front': PAL}, pixels, 'TEST')
        self.assertIn('redraw the patches', str(e.exception.code))
        self.assertEqual(front.getpixel((12, 22)), 3)


if __name__ == '__main__':
    unittest.main()
