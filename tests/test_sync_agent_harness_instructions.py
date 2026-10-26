"""Tests for scripts/sync_agent_harness_instructions.py (GMA-410 agent harness files)."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.sync_agent_harness_instructions import (
    MARKER_BEGIN,
    MARKER_END,
    MarkerError,
    block_present,
    restore_repo,
    sync_repo,
    upsert_marked_block,
    validate_markers,
    validate_repo_id,
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

    def test_mdc_preserves_frontmatter_and_trailer(self) -> None:
        self._copy_fixture()
        mdc = self.repo / ".cursor/rules/fixture-app-harness.mdc"
        mdc.parent.mkdir(parents=True, exist_ok=True)
        mdc.write_text(
            """---
description: Team-owned cursor rule
globs: ["src/**"]
alwaysApply: false
---

Notes that must survive sync.

"""
            + f"{MARKER_BEGIN}\nold block\n{MARKER_END}\n\nTrailer line stays.\n",
            encoding="utf-8",
        )
        sync_repo(self.repo, repo_id="fixture-app")
        text = mdc.read_text(encoding="utf-8")
        self.assertIn("Team-owned cursor rule", text)
        self.assertIn("Notes that must survive sync.", text)
        self.assertIn("Trailer line stays.", text)
        self.assertIn("standards-fixture-app", text)

        before_restore = mdc.read_text(encoding="utf-8")
        missing, _ = restore_repo(self.repo, repo_id="fixture-app")
        self.assertEqual(missing, [])
        self.assertEqual(mdc.read_text(encoding="utf-8"), before_restore)

    def test_restore_agents_only_leaves_other_files_unchanged(self) -> None:
        self._copy_fixture()
        sync_repo(self.repo, repo_id="fixture-app")
        claude_bytes = (self.repo / "CLAUDE.md").read_bytes()
        grok_bytes = (self.repo / ".grok/README.md").read_bytes()
        mdc_bytes = (
            self.repo / ".cursor/rules/fixture-app-harness.mdc"
        ).read_bytes()

        agents = (self.repo / "AGENTS.md").read_text(encoding="utf-8")
        start = agents.index(MARKER_BEGIN)
        end = agents.index(MARKER_END) + len(MARKER_END)
        stripped = agents[:start] + agents[end:]
        (self.repo / "AGENTS.md").write_text(stripped, encoding="utf-8")

        missing, changed = restore_repo(self.repo, repo_id="fixture-app")
        self.assertEqual(missing, ["AGENTS.md"])
        self.assertTrue(changed)
        self.assertEqual((self.repo / "CLAUDE.md").read_bytes(), claude_bytes)
        self.assertEqual((self.repo / ".grok/README.md").read_bytes(), grok_bytes)
        self.assertEqual(
            (self.repo / ".cursor/rules/fixture-app-harness.mdc").read_bytes(),
            mdc_bytes,
        )

    def test_malformed_markers_raise(self) -> None:
        bad = f"{MARKER_END}\n{MARKER_BEGIN}\n"
        with self.assertRaises(MarkerError) as ctx:
            validate_markers(bad)
        self.assertIn("before", str(ctx.exception).lower())
        with self.assertRaises(MarkerError):
            upsert_marked_block(f"{MARKER_BEGIN}\nno end\n", "block")

    def test_repo_id_slug_validation(self) -> None:
        self.assertEqual(validate_repo_id("fixture-app"), "fixture-app")
        with self.assertRaises(ValueError):
            validate_repo_id("../evil")
        with self.assertRaises(ValueError):
            validate_repo_id("Bad_Case")


if __name__ == "__main__":
    unittest.main()
