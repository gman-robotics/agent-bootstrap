"""Hub .github PR template must match docs/shared/hub-pull-request-template.md from Tier: onward."""

from __future__ import annotations

import unittest

from scripts.hub_pull_request_template import (
    read_canonical_github_body,
    read_committed_github_body,
)


class HubPullRequestTemplateTests(unittest.TestCase):
    def test_github_template_matches_canonical_body_from_tier(self) -> None:
        canonical_body = read_canonical_github_body()
        github_body = read_committed_github_body()
        self.assertEqual(
            github_body,
            canonical_body,
            ".github/PULL_REQUEST_TEMPLATE.md must match hub-pull-request-template.md "
            "from the first Tier: line (optional Canonical source footer allowed on GitHub copy)",
        )


if __name__ == "__main__":
    unittest.main()
