import unittest

from birthday_goose_hunt import ENEMY_COUNT, WORLD_HEIGHT, WORLD_WIDTH, clamp, make_hidden_geese


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


if __name__ == "__main__":
    unittest.main()
