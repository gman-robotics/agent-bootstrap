"""GMA-351: `scripts/box-tools.sh --check` reports pstack present/missing per CLI.

Runs the script against a synthetic HOME so results never depend on the real machine.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPT = REPO_ROOT / "scripts" / "box-tools.sh"


def _run(home: Path, *args: str) -> subprocess.CompletedProcess:
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}
    return subprocess.run(
        ["bash", str(SCRIPT), *args], env=env, capture_output=True, text=True, check=False
    )


def _skill(root: Path, name: str) -> None:
    d = root / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")


class BoxToolsCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _lines(self, out: str) -> dict:
        return {l.split(":")[0]: l.split(":", 1)[1].strip() for l in out.splitlines() if ":" in l}

    def test_all_missing_on_empty_home(self) -> None:
        r = _run(self.home, "--check")
        self.assertEqual(r.returncode, 1)
        lines = self._lines(r.stdout)
        for cli in ("grok", "claude", "cursor-agent"):
            self.assertTrue(lines[f"pstack {cli}"].startswith("missing"), r.stdout)

    def test_all_present(self) -> None:
        g = self.home / ".grok"
        (g / "installed-plugins").mkdir(parents=True)
        (g / "installed-plugins" / "registry.json").write_text('{"plugins": {"pstack": {}}}')
        (g / "config.toml").write_text('[plugins]\nenabled = [\n    "pstack",\n]\n')
        _skill(self.home / ".claude" / "skills", "poteto-mode")
        _skill(self.home / ".cursor" / "skills", "poteto-mode")
        r = _run(self.home, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        lines = self._lines(r.stdout)
        for cli in ("grok", "claude", "cursor-agent"):
            self.assertTrue(lines[f"pstack {cli}"].startswith("present"), r.stdout)

    def test_grok_installed_but_disabled_is_missing(self) -> None:
        g = self.home / ".grok"
        (g / "installed-plugins").mkdir(parents=True)
        (g / "installed-plugins" / "registry.json").write_text('{"pstack": {}}')
        (g / "config.toml").write_text('[plugins]\nenabled = ["superpowers"]\n')
        lines = self._lines(_run(self.home, "--check").stdout)
        self.assertTrue(lines["pstack grok"].startswith("missing"))

    def test_claude_plugin_install_counts(self) -> None:
        p = self.home / ".claude" / "plugins"
        p.mkdir(parents=True)
        (p / "installed_plugins.json").write_text('{"plugins": {"pstack@cursor-plugins": []}}')
        lines = self._lines(_run(self.home, "--check").stdout)
        self.assertTrue(lines["pstack claude"].startswith("present"))

    def test_cursor_hub_port_without_poteto_mode_is_partial(self) -> None:
        for n in ("architect", "interrogate"):
            _skill(self.home / ".cursor" / "skills", n)
        r = _run(self.home, "--check")
        lines = self._lines(r.stdout)
        self.assertTrue(lines["pstack cursor-agent"].startswith("partial"), r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_unknown_flag_is_usage_error(self) -> None:
        r = _run(self.home, "--bogus")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
