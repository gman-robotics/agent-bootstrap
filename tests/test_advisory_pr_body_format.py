"""Tests for scripts/advisory_pr_body_format.py."""

from __future__ import annotations

import unittest

from scripts.advisory_pr_body_format import check_body


class AdvisoryPrBodyFormatTests(unittest.TestCase):
    def test_valid_hub_body_has_no_warnings(self) -> None:
        body = """Tier: T0
Models: composer-2.5
Linear: https://linear.app/gman-personal-projects/issue/GMA-410
Summary: test
Gates: N/A (hub Markdown)

## pstack (Poteto) principles cited

- prove-it-works: unittest
"""
        self.assertEqual(check_body(body), [])

    def test_missing_linear_warns(self) -> None:
        body = "Tier: T0\nModels: x\nLinear: sketch://bad\nSummary: s\nGates: g\n"
        warnings = check_body(body)
        self.assertTrue(any("Linear" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
