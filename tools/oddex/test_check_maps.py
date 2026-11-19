"""Tests for check_maps.py's connection tileset check.

    python3 tools/oddex/test_check_maps.py
"""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_maps as cm  # noqa: E402


class BorderCellsTest(unittest.TestCase):
    def test_up_and_down_take_rows_next_to_the_border(self):
        # A is 10x10; B (20x30) is above A, B's x=0 at A's x=-5 (offset -5).
        cells = cm.border_cells(10, 10, 20, 30, "up", -5, view=8)
        self.assertEqual({y for _, y in cells}, set(range(22, 30)))  # B's bottom 8 rows
        # A's columns -8..17 are B's columns -3..22, clipped to 0..19.
        self.assertEqual({x for x, _ in cells}, set(range(0, 20)))
        cells = cm.border_cells(10, 10, 20, 30, "down", 12, view=8)
        self.assertEqual({y for _, y in cells}, set(range(0, 8)))  # B's top 8 rows
        self.assertEqual({x for x, _ in cells}, set(range(0, 6)))  # A's x -8..17 -> B's x -20..5

    def test_left_and_right_take_columns_next_to_the_border(self):
        cells = cm.border_cells(10, 40, 30, 30, "left", 0, view=8)
        self.assertEqual({x for x, _ in cells}, set(range(22, 30)))
        self.assertEqual({y for _, y in cells}, set(range(0, 30)))
        cells = cm.border_cells(10, 40, 30, 30, "right", 35, view=8)
        self.assertEqual({x for x, _ in cells}, set(range(0, 8)))
        self.assertEqual({y for _, y in cells}, set(range(0, 13)))  # A's y -8..47 -> B's y -43..12

    def test_small_neighbor_is_clipped(self):
        cells = cm.border_cells(10, 10, 3, 2, "up", 0, view=8)
        self.assertEqual(set(cells), {(x, y) for x in range(3) for y in range(2)})


class ConnectionTilesetTest(unittest.TestCase):
    def test_primary_mismatch_is_reported_without_reading_tiles(self):
        mine = {"id": "A", "primary_tileset": "gTileset_General", "secondary_tileset": "gTileset_Petalburg"}
        theirs = {"id": "B", "primary_tileset": "gTileset_Building", "secondary_tileset": "gTileset_Petalburg"}
        errors = cm.connection_tileset_errors("a.json", mine, theirs, "B", {"direction": "up", "offset": 0})
        self.assertEqual(len(errors), 1)
        self.assertIn("primary tileset gTileset_Building differs", errors[0])

    def test_vanilla_route104_sees_petalburg_secondary_tiles(self):
        # Vanilla accepts this (check_maps_baseline.json): Petalburg's top-left corner uses
        # gTileset_Petalburg metatiles that Route 104 (gTileset_Rustboro) draws with its own set.
        lays = cm.layouts()
        errors = cm.connection_tileset_errors("Route104", lays["LAYOUT_ROUTE104"], lays["LAYOUT_PETALBURG_CITY"],
                                              "PetalburgCity", {"direction": "right", "offset": 50})
        self.assertEqual(len(errors), 1)
        self.assertIn("8 of its tiles", errors[0])
        self.assertIn("first at (4, 1)", errors[0])

    def test_same_tilesets_need_no_tile_scan(self):
        lays = cm.layouts()
        errors = cm.connection_tileset_errors("Route101", lays["LAYOUT_ROUTE101"], lays["LAYOUT_OLDALE_TOWN"],
                                              "OldaleTown", {"direction": "up", "offset": 0})
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
