import unittest

import lib.pick as pick


class CheckPick(unittest.TestCase):
    def test_function_is_present(self):
        self.assertEqual(pick.pick.__name__, "pick")
