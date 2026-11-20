"""Tests for import_art.py fitting.

    python3 tools/oddex/test_import_art.py
"""
import os, sys, unittest

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import import_art as ia  # noqa: E402


def box(w, h):
    im = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    im.paste((255, 0, 0, 255), (10, 10, 10 + w, 10 + h))
    return im


class Fit(unittest.TestCase):
    def test_shared_scale_keeps_relative_size(self):
        big, small = box(64, 64), box(32, 16)
        k = ia.fit_scale([big, small], (32, 32), 31)
        self.assertEqual(k, 0.5)
        self.assertEqual(ia.content_box(ia.fit(big, (32, 32), 31, scale=k)), (0, 0, 32, 32))
        self.assertEqual(ia.content_box(ia.fit(small, (32, 32), 31, scale=k)), (8, 24, 24, 32))
        # Alone it is not shrunk at all (fit never enlarges), so it would match the big one's width.
        self.assertEqual(ia.content_box(ia.fit(small, (32, 32), 31)), (0, 16, 32, 32))

    def test_empty_frames_are_ignored(self):
        self.assertEqual(ia.fit_scale([Image.new('RGBA', (8, 8)), box(16, 16)], (32, 32), 31), 1.0)


if __name__ == '__main__':
    unittest.main()
