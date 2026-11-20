"""Tests for pixelkit.py shapes and checks.

    python3 tools/oddex/test_pixelkit.py
"""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixelkit as pk  # noqa: E402


class Shapes(unittest.TestCase):
    def test_ellipse_is_symmetric(self):
        e = pk.ellipse(31.5, 20, 10, 6)   # centre 31.5 is pixel-centre line 31, so width 63
        self.assertEqual(e, pk.mirror(e, 63))
        self.assertEqual(pk.ellipse(32, 20, 10, 6), pk.mirror(pk.ellipse(32, 20, 10, 6), 64))
        self.assertIn((31, 20), e)
        self.assertNotIn((31, 27), e)

    def test_polygon_and_rect(self):
        self.assertEqual(pk.polygon([(0, 0), (4, 0), (4, 3), (0, 3)]), pk.rect(0, 0, 4, 3))

    def test_edge_is_the_rim(self):
        r = pk.rect(0, 0, 4, 4)
        self.assertEqual(pk.edge(r), r - pk.rect(1, 1, 2, 2))

    def test_line_is_connected(self):
        pts = sorted(pk.line(0, 0, 5, 3))
        self.assertEqual(pts[0], (0, 0))
        self.assertEqual(pts[-1], (5, 3))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            self.assertLessEqual(max(abs(x1 - x0), abs(y1 - y0)), 1)

    def test_orphans(self):
        c = pk.Canvas(8, 8)
        c.part(pk.rect(1, 1, 5, 5), 2, 1)
        self.assertEqual(c.orphans(), [])
        c.put({(3, 3)}, 4)   # a lone pixel of another colour inside
        self.assertEqual(c.orphans(), [(3, 3)])
        c.put(pk.line(0, 7, 3, 4), 5)   # a diagonal 1px line is not noise
        self.assertEqual(c.orphans(), [(3, 3)])


if __name__ == '__main__':
    unittest.main()
