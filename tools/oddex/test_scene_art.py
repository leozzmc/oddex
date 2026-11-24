"""Tests for scene_art.py: the legendaries' 64x64 scene sheets (no Blender needed; side views are stubbed).

    python3 tools/oddex/test_scene_art.py
"""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene_art as sa  # noqa: E402
from placeholder_art import read_jasc  # noqa: E402

BLOB = [[0] * 64 for _ in range(64)]
for _y in range(10, 30):
    for _x in range(20, 40):
        BLOB[_y][_x] = 1 if _y in (10, 29) or _x in (20, 39) else 5


class Pieces(unittest.TestCase):
    def test_seat_stands_the_content_on_the_foot_row(self):
        self.assertEqual(sa.box(sa.seat(BLOB)), (22, 43, 42, 63))
        self.assertEqual(sa.box(sa.seat(BLOB, top=2)), (22, 2, 42, 22))

    def test_ring_only_fills_empty_pixels_next_to_content(self):
        g = sa.ring(sa.seat(BLOB), 9)
        self.assertEqual(sa.box(g), (21, 42, 43, 64))
        self.assertEqual(sum(v == 9 for row in g for v in row), 2 * 20 + 2 * 20)
        self.assertEqual(sum(v == 5 for row in g for v in row), 18 * 18)

    def test_breathe_keeps_the_feet_and_drops_one_row(self):
        g = sa.breathe(BLOB)
        self.assertEqual(sa.box(g), (20, 11, 40, 30))

    def test_asleep_puts_the_eyes_out(self):
        pal = [(0, 0, 0), (28, 18, 22), (60, 100, 80), (250, 238, 139)]
        stone = sa.asleep(pal, eyes=(3,))
        self.assertEqual(stone[0], pal[0])
        self.assertLess(max(stone[3]), 80)                       # the glow is gone
        self.assertLess(max(stone[2]) - min(stone[2]), 20)       # nearly grey


class Sheets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = sa.build(sides={name: BLOB for name in sa.BEASTS})

    def test_layout_matches_the_vanilla_objects(self):
        for name in sa.BEASTS:
            self.assertEqual(self.built[name]['scene.png'].size, (256, 64))
            self.assertEqual(len(self.built[name]['scene_asleep.pal']), 16)
        self.assertEqual(self.built['utsuroban']['scene.png'].size, (320, 64))    # sAnimTable_Rayquaza: 5 frames
        self.assertEqual(self.built['utsuroban']['scene_still.png'].size, (64, 64))

    def test_committed_pictures_are_current(self):
        """Everything that does not need a render must equal what is in the repo: redraw a battle sprite
        and the scene sheet has to be regenerated with it."""
        from PIL import Image
        for name, files in self.built.items():
            width = 128 if name in sa.BEASTS else None   # the stubbed side frames are not compared
            for file, im in files.items():
                if not file.endswith('.png'):
                    self.assertEqual(read_jasc(sa.GAME / name / file), im, f'{name}/{file}')
                    continue
                on_disk = Image.open(sa.GAME / name / file)
                box = (0, 0, width or im.width, 64)
                self.assertEqual(on_disk.crop(box).tobytes(), im.crop(box).tobytes(), f'{name}/{file}')

    def test_the_landed_ship_has_no_beam_and_a_closed_outline(self):
        frames = self.built['utsuroban']['scene.png']
        landed = sa.grid(frames.crop((64, 0, 128, 64)))
        used = {v for row in landed for v in row}
        self.assertFalse({5, 8} & used)                  # the box hangs in the beam; neither is here
        x0, y0, x1, y1 = sa.box(landed)
        self.assertEqual(y1, 64)                         # rim on the last row, outline above it
        self.assertTrue(all(v in (0, sa.SHIP['rim']) for v in landed[63]))


if __name__ == '__main__':
    unittest.main()
