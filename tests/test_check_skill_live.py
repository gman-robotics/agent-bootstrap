import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_skill_live import check_skill_live, skill_sha256


class CheckSkillLiveTests(unittest.TestCase):
    def _write_skill(self, skill_dir: Path, content: str) -> None:
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    def test_fails_when_no_run_record_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "some-skill"
            self._write_skill(skill_dir, "---\nname: some-skill\n---\nbody\n")

            live, message = check_skill_live(skill_dir)

            self.assertFalse(live)
            self.assertIn("no run record", message)

    def test_fails_when_run_record_verdict_is_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "some-skill"
            self._write_skill(skill_dir, "---\nname: some-skill\n---\nbody\n")
            (skill_dir / "black-box-run.json").write_text(
                json.dumps(
                    {
                        "verdict": "blocked",
                        "skill_sha256": skill_sha256(skill_dir),
                    }
                ),
                encoding="utf-8",
            )

            live, message = check_skill_live(skill_dir)

            self.assertFalse(live)
            self.assertIn("blocked", message)

    def test_passes_when_run_record_matches_current_skill_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "some-skill"
            self._write_skill(skill_dir, "---\nname: some-skill\n---\nbody\n")
            (skill_dir / "black-box-run.json").write_text(
                json.dumps(
                    {
                        "verdict": "pass",
                        "skill_sha256": skill_sha256(skill_dir),
                    }
                ),
                encoding="utf-8",
            )

            live, message = check_skill_live(skill_dir)

            self.assertTrue(live, message)

    def test_fails_when_skill_md_changed_since_the_run_record_was_captured(self) -> None:
        """Silent-refine guard: editing SKILL.md after a pass was captured (even a
        well-intentioned trajectory refine) must invalidate the record until a fresh
        black-box-agent-qa pass is captured. See skills/close-out/SKILL.md Step 9.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "some-skill"
            self._write_skill(skill_dir, "---\nname: some-skill\n---\nbody v1\n")
            (skill_dir / "black-box-run.json").write_text(
                json.dumps(
                    {
                        "verdict": "pass",
                        "skill_sha256": skill_sha256(skill_dir),
                    }
                ),
                encoding="utf-8",
            )

            # Refine the skill after the record was captured, with no fresh run.
            self._write_skill(skill_dir, "---\nname: some-skill\n---\nbody v2 (silent refine)\n")

            live, message = check_skill_live(skill_dir)

            self.assertFalse(live)
            self.assertIn("stale", message)

    def test_fails_when_run_record_is_not_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "some-skill"
            self._write_skill(skill_dir, "---\nname: some-skill\n---\nbody\n")
            (skill_dir / "black-box-run.json").write_text("not json", encoding="utf-8")

            live, message = check_skill_live(skill_dir)

            self.assertFalse(live)


if __name__ == "__main__":
    unittest.main()
