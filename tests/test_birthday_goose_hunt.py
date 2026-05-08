import unittest

from birthday_goose_hunt import ENEMY_COUNT, PROPS, ROOMS, WORLD_HEIGHT, WORLD_WIDTH, clamp, make_hidden_geese


class BirthdayGooseHuntTests(unittest.TestCase):
    def test_clamp_limits_values(self):
        self.assertEqual(clamp(-1, 0, 10), 0)
        self.assertEqual(clamp(11, 0, 10), 10)
        self.assertEqual(clamp(5, 0, 10), 5)

    def test_hidden_geese_have_unique_gifts_and_valid_positions(self):
        geese = make_hidden_geese(seed=123)

        self.assertEqual(len(geese), ENEMY_COUNT)
        self.assertEqual(sorted(goose.gift_number for goose in geese), list(range(1, ENEMY_COUNT + 1)))
        for goose in geese:
            self.assertGreaterEqual(goose.x, 80)
            self.assertLessEqual(goose.x, WORLD_WIDTH - 80)
            self.assertGreaterEqual(goose.y, 80)
            self.assertLessEqual(goose.y, WORLD_HEIGHT - 80)
            self.assertFalse(goose.defeated)

    def test_ship_art_layout_stays_inside_world(self):
        self.assertGreaterEqual(len(ROOMS), 6)
        self.assertGreaterEqual(len(PROPS), 10)
        for room in ROOMS:
            self.assertGreaterEqual(room.x1, 0)
            self.assertGreaterEqual(room.y1, 0)
            self.assertLessEqual(room.x2, WORLD_WIDTH)
            self.assertLessEqual(room.y2, WORLD_HEIGHT)
            self.assertLess(room.x1, room.x2)
            self.assertLess(room.y1, room.y2)
        for prop in PROPS:
            self.assertGreaterEqual(prop.x, 0)
            self.assertGreaterEqual(prop.y, 0)
            self.assertLessEqual(prop.x + prop.w, WORLD_WIDTH)
            self.assertLessEqual(prop.y + prop.h, WORLD_HEIGHT)


if __name__ == "__main__":
    unittest.main()
