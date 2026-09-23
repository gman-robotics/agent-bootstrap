"""GMA-56: prove the vendored Cloudflare `.cjs` validators still run.

`scripts/check_skill_live.py` hashes only `skills/security-audit/SKILL.md` — it proves
nothing about the vendored `.cjs` files under `references/cloudflare/` continuing to
execute correctly. This module is the separate, real-execution check the vendor plan
requires (see `docs/projects/agent-bootstrap/gma-56-security-audit-vendor-plan.md`
Blocker 6): missing or too-old Node is a hard test **failure**, never a soft skip, and
both vendored `.test.cjs` files are actually executed via `node --test`, not read.
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
VENDOR_DIR = REPO_ROOT / "skills" / "security-audit" / "references" / "cloudflare"
MINIMUM_NODE_MAJOR = 18

VENDORED_TEST_FILES = (
    VENDOR_DIR / "validate-findings.test.cjs",
    VENDOR_DIR / "validate-coverage-ledger.test.cjs",
)


class SecurityAuditVendorCjsTests(unittest.TestCase):
    def _require_node(self) -> str:
        node_path = shutil.which("node")
        if node_path is None:
            self.fail(
                "node executable not found on PATH — a missing Node is a hard failure "
                "for this test, not a skip (GMA-56 Blocker 6): the vendored .cjs "
                f"validators require Node >= {MINIMUM_NODE_MAJOR} to prove they still run."
            )
        return node_path

    def _require_minimum_node_version(self, node_path: str) -> None:
        result = subprocess.run(
            [node_path, "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"node --version failed: {result.stderr}")
        version_text = result.stdout.strip()
        self.assertTrue(version_text.startswith("v"), f"unexpected node --version output: {version_text!r}")
        major = int(version_text[1:].split(".", 1)[0])
        self.assertGreaterEqual(
            major,
            MINIMUM_NODE_MAJOR,
            f"node {version_text} is older than the pinned minimum v{MINIMUM_NODE_MAJOR} "
            "(GMA-56 Blocker 6) — this is a failure, not a skip.",
        )

    def test_node_available_and_meets_minimum_version(self) -> None:
        node_path = self._require_node()
        self._require_minimum_node_version(node_path)

    def test_vendored_cjs_test_files_exist(self) -> None:
        for test_file in VENDORED_TEST_FILES:
            self.assertTrue(test_file.is_file(), f"missing vendored test file: {test_file}")

    def test_validate_findings_cjs_tests_pass(self) -> None:
        node_path = self._require_node()
        self._require_minimum_node_version(node_path)

        test_file = VENDOR_DIR / "validate-findings.test.cjs"
        result = subprocess.run(
            [node_path, "--test", str(test_file)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"node --test {test_file} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}",
        )

    def test_validate_coverage_ledger_cjs_tests_pass(self) -> None:
        node_path = self._require_node()
        self._require_minimum_node_version(node_path)

        test_file = VENDOR_DIR / "validate-coverage-ledger.test.cjs"
        result = subprocess.run(
            [node_path, "--test", str(test_file)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"node --test {test_file} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
