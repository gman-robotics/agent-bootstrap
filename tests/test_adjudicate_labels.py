"""TDD for scripts/adjudicate_labels.py — deterministic two-labeler merge + adjudicator."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPT = REPO_ROOT / "scripts" / "adjudicate_labels.py"
FIXTURE_DIR = (
    REPO_ROOT
    / "skills"
    / "label-adjudication"
    / "fixtures"
    / "merge-agree-and-adjudicated"
)


class AdjudicateLabelsMergeTests(unittest.TestCase):
    def test_merge_agree_and_adjudicated_fixture_exits_zero(self):
        self.assertTrue(FIXTURE_DIR.is_dir(), "positive fixture dir must exist")
        out = tempfile.TemporaryDirectory()
        adjudication_out = Path(out.name) / "adjudication.jsonl"
        final_out = Path(out.name) / "final.jsonl"
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--labels-a",
                str(FIXTURE_DIR / "labels_a.jsonl"),
                "--labels-b",
                str(FIXTURE_DIR / "labels_b.jsonl"),
                "--items",
                str(FIXTURE_DIR / "items.jsonl"),
                "--adjudicator-jsonl",
                str(FIXTURE_DIR / "adjudicator.jsonl"),
                "--adjudication-out",
                str(adjudication_out),
                "--final-out",
                str(final_out),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertIn("agree=", proc.stdout)
        self.assertIn("adjudicated=", proc.stdout)
        rows = [json.loads(line) for line in adjudication_out.read_text().splitlines() if line.strip()]
        self.assertEqual(len(rows), 2)
        by_id = {r["id"]: r for r in rows}
        self.assertEqual(by_id["item-1"]["resolution"], "agree")
        self.assertEqual(by_id["item-2"]["resolution"], "adjudicated")
        self.assertIsNone(by_id["item-1"].get("adjudicator_rationale"))
        finals = [json.loads(line) for line in final_out.read_text().splitlines() if line.strip()]
        self.assertEqual(len(finals), 2)
        final_by_id = {r["id"]: r for r in finals}
        self.assertEqual(final_by_id["item-1"]["label"], "positive")
        self.assertEqual(final_by_id["item-1"]["label_status"], "agreed_pending_human")
        self.assertEqual(final_by_id["item-2"]["label_status"], "adjudicated_pending_human")

    def test_unresolved_disagreement_exits_nonzero(self):
        out = tempfile.TemporaryDirectory()
        labels_a = Path(out.name) / "a.jsonl"
        labels_b = Path(out.name) / "b.jsonl"
        labels_a.write_text('{"id": "x", "label": "a"}\n', encoding="utf-8")
        labels_b.write_text('{"id": "x", "label": "b"}\n', encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--labels-a",
                str(labels_a),
                "--labels-b",
                str(labels_b),
                "--adjudication-out",
                str(Path(out.name) / "adj.jsonl"),
                "--final-out",
                str(Path(out.name) / "final.jsonl"),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("x", proc.stderr + proc.stdout)
        self.assertIn("unresolved", (proc.stderr + proc.stdout).lower())


if __name__ == "__main__":
    unittest.main()
