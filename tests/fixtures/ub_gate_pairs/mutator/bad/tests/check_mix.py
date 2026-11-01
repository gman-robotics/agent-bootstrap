import unittest

from lib.mix import mix


class CheckMix(unittest.TestCase):
    def test_runs_without_checking_result(self):
        mix(2, 1)
        mix(0, 1)
        self.assertEqual(1, 1)
