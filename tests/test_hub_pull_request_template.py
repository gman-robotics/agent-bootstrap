"""Hub .github PR template must match docs/shared/hub-pull-request-template.md from Tier: onward."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.hub_pull_request_template import (
    check_pr_template_file,
    read_canonical_github_body,
    read_committed_github_body,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


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

    def test_check_cli_passes_on_committed_github_template(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/hub_pull_request_template.py"),
                "check",
                "--file",
                str(REPO_ROOT / ".github/PULL_REQUEST_TEMPLATE.md"),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

    def test_check_helper_reports_mismatch(self) -> None:
        err = check_pr_template_file(REPO_ROOT, REPO_ROOT / "docs/shared/hub-pull-request-template.md")
        self.assertIsNotNone(err)


if __name__ == "__main__":
    unittest.main()
