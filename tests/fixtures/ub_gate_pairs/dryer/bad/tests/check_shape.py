import unittest

from lib.shape import shape_left, shape_right


class CheckShape(unittest.TestCase):
    def test_both_return_the_joined_parts(self):
        sample = ["a", "b", "c", "d", "e"]
        left = shape_left(sample)
        right = shape_right(sample)
        self.assertEqual(left, right)
        self.assertIn("abcde", left)
        self.assertIn("end", left)
