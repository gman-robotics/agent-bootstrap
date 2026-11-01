import unittest

from lib.over import over_two


class CheckOverTwo(unittest.TestCase):
    def test_below_boundary(self):
        self.assertEqual(over_two(0), 0)
        self.assertEqual(over_two(1), 0)
        self.assertIs(type(over_two(0)), int)

    def test_at_boundary(self):
        self.assertEqual(over_two(2), 0)
        self.assertIs(type(over_two(2)), int)

    def test_above_boundary(self):
        self.assertEqual(over_two(3), 1)
        self.assertEqual(over_two(4), 1)
        self.assertIs(type(over_two(3)), int)
