"""Tests for scripts/check_pr_body_blast_radius.py."""

from __future__ import annotations

import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts.check_pr_body_blast_radius import EMPTY, MISSING, check_body, main

REPO_ROOT = Path(__file__).resolve().parent.parent
HUB_TEMPLATE = REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"

_COMMENT_AND_BOX = """## Blast radius

<!-- What could this change break, and who depends on it? See skills/blast-radius/SKILL.md. Docs-only PRs: write `N/A (docs-only)`. Required: ub-gates fails if this section is missing or empty. -->

- [ ] Blast radius considered (`skills/blast-radius/SKILL.md`) for non-docs diffs
"""


class CheckPrBodyBlastRadiusTests(unittest.TestCase):
    def test_missing_heading_fails(self) -> None:
        self.assertEqual(check_body("## Checklist\n\n- [x] done\n"), [MISSING])
        self.assertEqual(check_body(""), [MISSING])

    def test_comment_and_unchecked_box_fails(self) -> None:
        self.assertEqual(check_body(_COMMENT_AND_BOX), [EMPTY])

    def test_empty_heading_at_eof_fails(self) -> None:
        self.assertEqual(check_body("## Blast radius"), [EMPTY])
        self.assertEqual(check_body("## Blast radius\n"), [EMPTY])

    def test_heading_followed_by_next_heading_fails(self) -> None:
        self.assertEqual(check_body("## Blast radius\n## Checklist\n"), [EMPTY])

    def test_ticked_box_passes(self) -> None:
        body = (
            "## Blast radius\n\n"
            "- [x] Blast radius considered (`skills/blast-radius/SKILL.md`) for non-docs diffs\n"
        )
        self.assertEqual(check_body(body), [])

    def test_free_text_passes(self) -> None:
        body = "## Blast radius\n\nCallers in other repos copy this template.\n"
        self.assertEqual(check_body(body), [])

    def test_docs_only_marker_passes(self) -> None:
        self.assertEqual(check_body("## Blast radius\n\nN/A (docs-only)\n"), [])

    def test_heading_is_case_insensitive(self) -> None:
        self.assertEqual(check_body("## bLaSt RaDiUs\n\nN/A (docs-only)\n"), [])

    def test_unedited_hub_template_is_empty(self) -> None:
        body = HUB_TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(check_body(body), [EMPTY])

    def test_main_pr_body_error_returns_1(self) -> None:
        buf = StringIO()
        with patch.dict(os.environ, {"PR_BODY": "no section here\n"}), redirect_stdout(buf):
            code = main()
        self.assertEqual(code, 1)
        self.assertIn(f"::error title=PR body blast radius::{MISSING}", buf.getvalue())

    def test_main_pr_body_ok_returns_0(self) -> None:
        buf = StringIO()
        with (
            patch.dict(os.environ, {"PR_BODY": "## Blast radius\n\nN/A (docs-only)\n"}),
            redirect_stdout(buf),
        ):
            code = main()
        self.assertEqual(code, 0)
        self.assertNotIn("::error", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
