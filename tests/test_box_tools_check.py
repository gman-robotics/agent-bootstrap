"""GMA-351: `scripts/box-tools.sh` reports pstack per CLI plus lean-context tools, and installs tools.

Every run uses a synthetic HOME and an isolated PATH (stub binaries plus a few real
system utilities), so results never depend on the real machine and nothing hits the network.
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPT = REPO_ROOT / "scripts" / "box-tools.sh"

SYSTEM_TOOLS = ("bash", "awk", "grep", "sed", "head", "cat", "mkdir", "dirname", "tr", "cut")

# python3 stub: modules "exist" when $HOME/.fakepy/<name> exists (its content is the version).
# `-m pip install ...` succeeds and creates the modules listed in $HOME/.fakepy-pip-creates.
PY_STUB = r"""#!/bin/bash
fp="$HOME/.fakepy"
if [[ "$1" == "-m" && "$2" == "pip" ]]; then
  echo "pip $*" >> "$HOME/.pip-log"
  if [[ -f "$HOME/.fakepy-pip-creates" ]]; then
    mkdir -p "$fp"
    while read -r m; do echo "9.9.9" > "$fp/$m"; done < "$HOME/.fakepy-pip-creates"
  fi
  exit 0
fi
code="$2"
for m in markitdown trafilatura; do
  case "$code" in
    *"version('$m')"*) [[ -f "$fp/$m" ]] && { cat "$fp/$m"; exit 0; }; exit 1 ;;
    *"import $m"*) [[ -f "$fp/$m" ]] && exit 0; exit 1 ;;
  esac
done
exit 1
"""


def _stub(bindir: Path, name: str, body: str) -> None:
    p = bindir / name
    p.write_text(body, encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _skill(root: Path, name: str) -> None:
    d = root / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")


class _Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.home = root / "home"
        self.home.mkdir()
        self.bin = root / "bin"
        self.bin.mkdir()
        self.sys = root / "sys"
        self.sys.mkdir()
        for t in SYSTEM_TOOLS:
            real = shutil.which(t)
            assert real, f"missing system tool {t}"
            os.symlink(real, self.sys / t)
        _stub(self.bin, "python3", PY_STUB)
        self.os_name = "Linux"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        _stub(self.bin, "uname", f'#!/bin/bash\n[[ "$1" == "-m" ]] && echo x86_64 || echo {self.os_name}\n')
        env = {"HOME": str(self.home), "PATH": f"{self.bin}:{self.sys}"}
        return subprocess.run(
            [str(self.sys / "bash"), str(SCRIPT), *args],
            env=env, capture_output=True, text=True, check=False,
        )

    def lines(self, out: str) -> dict:
        return {l.split(":")[0]: l.split(":", 1)[1].strip() for l in out.splitlines() if ":" in l}

    # --- fixtures ---
    def add_tools(self, rtk: bool = False) -> None:
        _stub(self.bin, "rg", "#!/bin/bash\necho 'ripgrep 14.1.1'\necho '-SIMD -AVX'\n")
        _stub(self.bin, "jq", "#!/bin/bash\necho 'jq-1.7.1'\n")
        _stub(self.bin, "markitdown", "#!/bin/bash\necho 'markitdown 0.1.9'\n")
        fp = self.home / ".fakepy"
        fp.mkdir(exist_ok=True)
        (fp / "markitdown").write_text("0.1.9\n")
        (fp / "trafilatura").write_text("2.3.1\n")
        if rtk:
            _stub(self.bin, "rtk", "#!/bin/bash\necho 'rtk 1.0.1'\n")

    def grok(self, registry: str | None, config: str | None) -> None:
        g = self.home / ".grok"
        (g / "installed-plugins").mkdir(parents=True, exist_ok=True)
        if registry is not None:
            (g / "installed-plugins" / "registry.json").write_text(registry)
        if config is not None:
            (g / "config.toml").write_text(config)

    def add_pstack(self) -> None:
        self.grok('{"plugins": {"pstack": {}}}', '[plugins]\nenabled = [\n    "pstack",\n]\n')
        _skill(self.home / ".claude" / "skills", "poteto-mode")
        _skill(self.home / ".cursor" / "skills", "poteto-mode")


class PstackCheckTest(_Base):
    def test_all_missing_on_empty_home(self) -> None:
        r = self.run_script("--check")
        self.assertEqual(r.returncode, 1)
        lines = self.lines(r.stdout)
        for cli in ("grok", "claude", "cursor-agent"):
            self.assertTrue(lines[f"pstack {cli}"].startswith("missing"), r.stdout)

    def test_all_present(self) -> None:
        self.add_pstack()
        self.add_tools()
        r = self.run_script("--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        lines = self.lines(r.stdout)
        for cli in ("grok", "claude", "cursor-agent"):
            self.assertTrue(lines[f"pstack {cli}"].startswith("present"), r.stdout)

    def test_grok_installed_but_disabled_is_missing(self) -> None:
        self.grok('{"pstack": {}}', '[plugins]\nenabled = ["superpowers"]\n')
        r = self.run_script("--check")
        self.assertTrue(self.lines(r.stdout)["pstack grok"].startswith("missing"))
        self.assertEqual(r.returncode, 1)

    def test_claude_plugin_install_counts(self) -> None:
        p = self.home / ".claude" / "plugins"
        p.mkdir(parents=True)
        (p / "installed_plugins.json").write_text('{"plugins": {"pstack@cursor-plugins": []}}')
        self.assertTrue(self.lines(self.run_script("--check").stdout)["pstack claude"].startswith("present"))

    def test_claude_skill_only_counts(self) -> None:
        _skill(self.home / ".claude" / "skills", "poteto-mode")
        self.assertEqual(self.lines(self.run_script("--check").stdout)["pstack claude"], "present (~/.claude/skills)")

    def test_cursor_hub_port_without_poteto_mode_is_partial(self) -> None:
        for n in ("architect", "interrogate"):
            _skill(self.home / ".cursor" / "skills", n)
        r = self.run_script("--check")
        self.assertTrue(self.lines(r.stdout)["pstack cursor-agent"].startswith("partial"), r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_cursor_only_one_hub_skill_is_missing(self) -> None:
        _skill(self.home / ".cursor" / "skills", "architect")
        self.assertTrue(self.lines(self.run_script("--check").stdout)["pstack cursor-agent"].startswith("missing"))

    def test_unknown_flag_is_usage_error(self) -> None:
        self.assertEqual(self.run_script("--bogus").returncode, 2)

    def test_no_args_is_usage_error(self) -> None:
        self.assertEqual(self.run_script().returncode, 2)

    def test_grok_missing_registry_says_not_found(self) -> None:
        self.assertIn("not found", self.lines(self.run_script("--check").stdout)["pstack grok"])

    def test_grok_registry_without_entry_says_no_entry(self) -> None:
        self.grok('{"plugins": {}}', None)
        self.assertIn("no pstack entry", self.lines(self.run_script("--check").stdout)["pstack grok"])

    def test_grok_missing_config_is_distinct(self) -> None:
        self.grok('{"pstack": {}}', None)
        detail = self.lines(self.run_script("--check").stdout)["pstack grok"]
        self.assertTrue(detail.startswith("missing"), detail)
        self.assertIn("config.toml not found", detail)

    def test_grok_substring_entry_is_not_a_match(self) -> None:
        self.grok('{"pstack": {}}', '[plugins]\nenabled = ["foo-pstack"] # "pstack"\n')
        self.assertTrue(self.lines(self.run_script("--check").stdout)["pstack grok"].startswith("missing"))

    def test_grok_bracket_in_comment_does_not_end_array(self) -> None:
        self.grok('{"pstack": {}}', '[plugins]\nenabled = [ # list ] here\n  "a]b",\n  "pstack",\n]\n')
        self.assertTrue(self.lines(self.run_script("--check").stdout)["pstack grok"].startswith("present"))

    def test_grok_plugins_header_with_trailing_space_and_comment(self) -> None:
        self.grok('{"pstack": {}}', '[plugins]   # enabled plugins\nenabled = ["pstack"]\n')
        self.assertTrue(self.lines(self.run_script("--check").stdout)["pstack grok"].startswith("present"))


class ToolCheckTest(_Base):
    def test_tools_only_ignores_pstack(self) -> None:
        self.add_tools()
        r = self.run_script("--check", "--tools-only")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("pstack", r.stdout)

    def test_missing_required_tool_fails_even_with_pstack(self) -> None:
        self.add_pstack()
        self.add_tools()
        (self.bin / "jq").unlink()
        r = self.run_script("--check")
        self.assertEqual(r.returncode, 1)
        self.assertTrue(self.lines(r.stdout)["jq"].startswith("missing"))

    def test_missing_optional_tools_do_not_fail(self) -> None:
        self.add_tools()
        (self.home / ".fakepy" / "trafilatura").unlink()
        r = self.run_script("--check", "--tools-only")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertTrue(self.lines(r.stdout)["trafilatura"].startswith("missing (optional"))
        self.assertTrue(self.lines(r.stdout)["rtk"].startswith("missing (optional"))

    def test_versions_are_parsed(self) -> None:
        self.add_tools(rtk=True)
        lines = self.lines(self.run_script("--check", "--tools-only").stdout)
        self.assertEqual(lines["rg"], "present (14.1.1)")
        self.assertEqual(lines["jq"], "present (1.7.1)")
        self.assertEqual(lines["markitdown"], "present (0.1.9)")
        self.assertEqual(lines["trafilatura"], "present (2.3.1)")
        self.assertEqual(lines["rtk"], "present (1.0.1)")

    def test_tools_only_requires_check(self) -> None:
        self.assertEqual(self.run_script("--tools-only").returncode, 2)


class InstallTest(_Base):
    def test_darwin_skips_with_brew_hint(self) -> None:
        self.os_name = "Darwin"
        r = self.run_script("--install")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("brew install", r.stdout + r.stderr)
        self.assertFalse((self.home / ".pip-log").exists())

    def test_second_run_skips_everything(self) -> None:
        self.add_tools(rtk=True)
        r = self.run_script("--install", "--with-rtk")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = [l for l in r.stdout.splitlines() if l.strip()]
        self.assertEqual(len(out), 5, r.stdout)
        for l in out:
            self.assertTrue(l.startswith("skip "), l)

    def test_trafilatura_installs_with_html_clean_pin(self) -> None:
        self.add_tools()
        (self.home / ".fakepy" / "trafilatura").unlink()
        (self.home / ".fakepy-pip-creates").write_text("trafilatura\n")
        r = self.run_script("--install")
        self.assertEqual(r.returncode, 0, r.stderr)
        log = (self.home / ".pip-log").read_text()
        self.assertIn("trafilatura==", log)
        self.assertIn("lxml_html_clean==", log)

    def test_trafilatura_import_failure_exits_nonzero(self) -> None:
        self.add_tools()
        (self.home / ".fakepy" / "trafilatura").unlink()
        r = self.run_script("--install")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("trafilatura", r.stderr)


if __name__ == "__main__":
    unittest.main()
