"""GMA-56 Blocker 2: prove nested `references/<dir>/**` files round-trip.

`skills/security-audit/references/cloudflare/` is the first hub skill with a *directory*
(not a flat file) directly under its `references/`. Two mechanisms are involved:

1. `scripts/export_codex_skills.py --force`'s `collect_preserved_files` — already
   recursive (`skill_dir.rglob("*")`), so it already preserves a nested reference file
   byte-for-byte across a re-export. This test locks that in; it is not a new fix.
2. `scripts/install-grok.sh`'s "Restoring extra skill references" step — the mechanism
   that actually populates a skill's extra reference files in the first place. Before the
   GMA-56 fix, its restore loop was one level deep only (`[[ -f "$ref" ]]` silently skipped
   directories), so `references/cloudflare/**` never reached `.grok/skills/security-audit/`
   on any `install-grok.sh --local`/plugin install. This test proves the fix: the loop now
   recurses into subdirectories of `references/`, excluding `source.md` at any depth.

Uses a synthetic nested-scratch skill source (not the real `security-audit` tree) so this
test is fast, isolated, and does not depend on `security-audit` staying in any particular
state.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.export_codex_skills import SKILL_CONFIGS, SkillConfig, export_skills

REPO_ROOT = Path(__file__).parent.parent


def _write_nested_scratch_skill(skills_source_dir: Path) -> Path:
    """Create a minimal synthetic skill with a nested references/ subdirectory."""
    skill_dir = skills_source_dir / "nested-scratch-skill"
    (skill_dir / "references" / "vendorsub").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: nested-scratch-skill\ndescription: test\nversion: 1.0.0\n---\nbody\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "top.md").write_text("top-level reference\n", encoding="utf-8")
    (skill_dir / "references" / "vendorsub" / "nested.md").write_text(
        "nested vendor reference\n", encoding="utf-8"
    )
    return skill_dir


class DualHomeNestedReferencesTests(unittest.TestCase):
    def test_export_force_reexport_preserves_nested_reference_byte_for_byte(self) -> None:
        """Already-true mechanism (collect_preserved_files is recursive) — this locks it in."""
        synthetic_config = SkillConfig(
            description="test",
            short_description="test",
            trigger_summary="test",
            quick_start=("test",),
        )
        with tempfile.TemporaryDirectory() as source_root, tempfile.TemporaryDirectory() as output_root:
            source_dir = Path(source_root)
            output_dir = Path(output_root)
            _write_nested_scratch_skill(source_dir)

            with patch.dict(SKILL_CONFIGS, {"nested-scratch-skill": synthetic_config}):
                export_skills(source_dir, output_dir)

                nested_dest = output_dir / "nested-scratch-skill" / "references" / "vendorsub" / "nested.md"
                nested_dest.parent.mkdir(parents=True, exist_ok=True)
                nested_dest.write_text("nested vendor reference\n", encoding="utf-8")

                export_skills(source_dir, output_dir, force=True)

            self.assertTrue(
                nested_dest.is_file(),
                "export_codex_skills.py --force must preserve a nested references/<dir>/<file> "
                "byte-for-byte across re-export",
            )
            self.assertEqual(nested_dest.read_text(encoding="utf-8"), "nested vendor reference\n")

    def test_install_grok_local_copies_nested_reference_directory(self) -> None:
        """The actual GMA-56 fix: install-grok.sh's restore loop must recurse.

        Uses `--local --target <isolated tmp dir>` (the same pattern as
        `test_install_grok_local_runs_without_error` in test_export_codex_skills.py) so this
        test writes only into a throwaway directory, never mutating the committed
        `.grok/skills/` tree in this checkout. `--local` mode always reads real skill
        sources from `<REPO_ROOT>/skills`, so the real vendored `security-audit` tree is the
        one actually exercised.
        """
        script = REPO_ROOT / "scripts" / "install-grok.sh"

        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(script), "--local", "--target", tmp, "--force"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(
                result.returncode,
                0,
                f"install-grok.sh --local failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}",
            )

            nested_dest = (
                Path(tmp)
                / ".grok"
                / "skills"
                / "security-audit"
                / "references"
                / "cloudflare"
                / "validate-findings.cjs"
            )
            self.assertTrue(
                nested_dest.is_file(),
                "install-grok.sh --local must copy nested references/cloudflare/** into "
                ".grok/skills/security-audit/references/cloudflare/** (GMA-56 Blocker 2 fix) — "
                "a one-level-deep restore loop would silently skip this directory",
            )

            canonical = (
                REPO_ROOT
                / "skills"
                / "security-audit"
                / "references"
                / "cloudflare"
                / "validate-findings.cjs"
            )
            self.assertEqual(
                nested_dest.read_bytes(),
                canonical.read_bytes(),
                "restored nested reference file must match the canonical vendored source byte-for-byte",
            )


if __name__ == "__main__":
    unittest.main()
