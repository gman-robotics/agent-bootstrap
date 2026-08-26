import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_black_box_fixture import load_case, run_case, write_run_record


class RunBlackBoxFixtureTests(unittest.TestCase):
    def _write_case(self, fixture_dir: Path, case: dict) -> None:
        fixture_dir.mkdir(parents=True, exist_ok=True)
        (fixture_dir / "case.json").write_text(json.dumps(case), encoding="utf-8")

    def test_load_case_reads_case_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture_dir = Path(tmpdir)
            self._write_case(fixture_dir, {"name": "x", "input": {"command": ["true"]}})

            case = load_case(fixture_dir)

            self.assertEqual(case["name"], "x")

    def test_run_case_passes_on_matching_exit_code_and_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture_dir = Path(tmpdir)
            case = {
                "name": "echo-case",
                "input": {"command": ["python3", "-c", "print('hello fixture')"]},
                "expected": {"exit_code": 0, "stdout_contains": ["hello fixture"]},
            }

            outcome = run_case(case, repo_root=Path(tmpdir))

            self.assertEqual(outcome["verdict"], "pass")
            self.assertEqual(outcome["exit_code"], 0)
            self.assertEqual(outcome["mismatches"], [])

    def test_run_case_fails_when_expected_output_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            case = {
                "name": "wrong-expectation",
                "input": {"command": ["python3", "-c", "print('actual output')"]},
                "expected": {"exit_code": 0, "stdout_contains": ["this substring is not present"]},
            }

            outcome = run_case(case, repo_root=Path(tmpdir))

            self.assertEqual(outcome["verdict"], "fail")
            self.assertTrue(outcome["mismatches"])

    def test_run_case_fails_on_exit_code_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            case = {
                "name": "bad-exit",
                "input": {"command": ["python3", "-c", "import sys; sys.exit(3)"]},
                "expected": {"exit_code": 0},
            }

            outcome = run_case(case, repo_root=Path(tmpdir))

            self.assertEqual(outcome["verdict"], "fail")
            self.assertEqual(outcome["exit_code"], 3)

    def test_run_case_blocks_instead_of_passing_when_command_is_missing(self) -> None:
        """Environment-blocked runs escalate, they never count as a pass (Step 4)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            case = {
                "name": "missing-executable",
                "input": {"command": ["this-executable-does-not-exist-anywhere"]},
                "expected": {"exit_code": 0},
            }

            outcome = run_case(case, repo_root=Path(tmpdir))

            self.assertEqual(outcome["verdict"], "blocked")
            self.assertNotEqual(outcome["verdict"], "pass")

    def test_write_run_record_includes_skill_sha256_and_persists_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "skills" / "some-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: some-skill\n---\nbody\n", encoding="utf-8")
            case = {"name": "n", "input": {"command": ["true"]}, "expected": {"exit_code": 0}}
            outcome = {"verdict": "pass", "exit_code": 0, "stdout_tail": "", "stderr_tail": "", "mismatches": []}
            out_path = skill_dir / "black-box-run.json"

            write_run_record(out_path, case=case, skill_dir=skill_dir, outcome=outcome, fixture_dir=Path("fixtures/x"))

            record = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(record["verdict"], "pass")
            self.assertIsNotNone(record["skill_sha256"])
            self.assertEqual(record["case_name"], "n")


if __name__ == "__main__":
    unittest.main()
