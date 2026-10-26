"""Tests for scripts/sync_agent_harness_instructions.py (GMA-410 agent harness files)."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.sync_agent_harness_instructions import (
    MARKER_BEGIN,
    MARKER_END,
    block_present,
    sync_repo,
    verify_repo,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = (
    REPO_ROOT / "skills/create-verification-skill/fixtures/agent-harness-sync"
)


class SyncAgentHarnessInstructionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="agent-harness-sync-")
        self.repo = Path(self._tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _copy_fixture(self) -> None:
        shutil.copytree(FIXTURE_ROOT, self.repo, dirs_exist_ok=True)

    def test_adds_block_preserves_existing_agents_content(self) -> None:
        self._copy_fixture()
        before = (self.repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Legacy project rules that must stay.", before)
        self.assertNotIn(MARKER_BEGIN, before)

        changed = sync_repo(self.repo, repo_id="fixture-app")
        self.assertTrue(changed)

        after_first = (self.repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Legacy project rules that must stay.", after_first)
        self.assertIn(MARKER_BEGIN, after_first)
        self.assertIn("standards-fixture-app", after_first)
        self.assertIn(MARKER_END, after_first)

        changed_again = sync_repo(self.repo, repo_id="fixture-app")
        self.assertFalse(changed_again)
        after_second = (self.repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(after_first, after_second)

    def test_verify_reports_missing_block(self) -> None:
        self._copy_fixture()
        missing = verify_repo(self.repo, repo_id="fixture-app")
        self.assertTrue(missing)

        sync_repo(self.repo, repo_id="fixture-app")
        missing_after = verify_repo(self.repo, repo_id="fixture-app")
        self.assertEqual(missing_after, [])

    def test_block_present_helper(self) -> None:
        text = f"hello\n{MARKER_BEGIN}\nbody\n{MARKER_END}\n"
        self.assertTrue(block_present(text))


if __name__ == "__main__":
    unittest.main()
