import unittest

from birthday_goose_hunt import (
    DOORS,
    ENEMY_COUNT,
    FLOOR_DECALS,
    LIGHTS,
    PROPS,
    ROOMS,
    WORLD_HEIGHT,
    WORLD_WIDTH,
    clamp,
    is_walkable,
    make_hidden_geese,
)


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
            self.assertTrue(is_walkable(goose.x, goose.y, radius=24))
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
        for x1, y1, x2, y2, _label in DOORS:
            self.assertGreaterEqual(x1, 0)
            self.assertGreaterEqual(y1, 0)
            self.assertLessEqual(x2, WORLD_WIDTH)
            self.assertLessEqual(y2, WORLD_HEIGHT)
        for x, y, radius, _color in LIGHTS:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertGreater(radius, 0)
            self.assertLessEqual(x, WORLD_WIDTH)
            self.assertLessEqual(y, WORLD_HEIGHT)
        for x, y, width, height, _text, _color in FLOOR_DECALS:
            self.assertGreater(width, 0)
            self.assertGreater(height, 0)
            self.assertTrue(is_walkable(x, y, radius=24))

    def test_collision_blocks_walls_but_allows_rooms_and_corridors(self):
        self.assertTrue(is_walkable(1400, 950))
        self.assertTrue(is_walkable(940, 375))
        self.assertFalse(is_walkable(930, 650))
        self.assertFalse(is_walkable(40, 40))


if __name__ == "__main__":
    unittest.main()
