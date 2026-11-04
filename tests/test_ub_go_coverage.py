"""Go coverprofile rewrite: import paths become repo-relative keys."""

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.ub_go_coverage import main, missing_files, modules, profile_paths, rewrite_profile, rewrite_tree


ROOT_MOD = "github.com/org/repo"
NESTED_MOD = "github.com/org/repo/adapters"
IMPORT_KEY = "github.com/org/repo/adapters/engram/x.go"
PROFILE = f"mode: set\n{IMPORT_KEY}:10.20,12.2 1 1\n"


def _git_init(repo: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)


def _parts(path: str) -> tuple[str, ...]:
    return tuple(part for part in path.split("/") if part)


def _trailing(longer: tuple[str, ...], shorter: tuple[str, ...]) -> bool:
    if not shorter or len(shorter) > len(longer):
        return False
    return longer[-len(shorter) :] == shorter


class RewriteProfileTests(unittest.TestCase):
    def _mods(self) -> list[tuple[str, str]]:
        return [(ROOT_MOD, "."), (NESTED_MOD, "adapters")]

    def test_import_path_becomes_repo_path(self) -> None:
        out = rewrite_profile(PROFILE, self._mods())
        self.assertEqual(out.splitlines()[1].split(":")[0], "adapters/engram/x.go")

    def test_longest_module_prefix_wins(self) -> None:
        text = f"mode: set\n{ROOT_MOD}/cmd/main.go:1.1,2.2 1 0\n"
        out = rewrite_profile(text, self._mods())
        self.assertEqual(out.splitlines()[1].split(":")[0], "cmd/main.go")
        nested = rewrite_profile(PROFILE, [(ROOT_MOD, "."), (NESTED_MOD, "adapters")])
        self.assertTrue(nested.splitlines()[1].startswith("adapters/engram/x.go:"))

    def test_root_module_maps_to_bare_rest(self) -> None:
        text = f"mode: set\n{ROOT_MOD}/main.go:1.2,3.4 2 1\n"
        out = rewrite_profile(text, [(ROOT_MOD, ".")])
        self.assertEqual(out.splitlines()[1], "main.go:1.2,3.4 2 1")

    def test_foreign_key_stays(self) -> None:
        text = "mode: set\nexample.com/other/file.go:1.1,2.2 1 0\n"
        self.assertEqual(rewrite_profile(text, self._mods()), text)

    def test_mode_line_stays(self) -> None:
        out = rewrite_profile("mode: atomic\n", self._mods())
        self.assertEqual(out, "mode: atomic\n")

    def test_malformed_line_raises(self) -> None:
        with self.assertRaises(ValueError):
            rewrite_profile("mode: set\nnot-a-record\n", self._mods())

    def test_idempotent(self) -> None:
        once = rewrite_profile(PROFILE, self._mods())
        twice = rewrite_profile(once, self._mods())
        self.assertEqual(twice, once)

    def test_single_char_module_path_maps(self) -> None:
        text = "mode: set\nb/file.go:1.1,2.2 1 0\n"
        out = rewrite_profile(text, [("b", ".")])
        self.assertEqual(out.splitlines()[1].split(":")[0], "file.go")

    def test_equal_module_path_keeps_the_first_dir(self) -> None:
        text = "mode: set\nexample.com/m/file.go:1.1,2.2 1 0\n"
        mods = [("example.com/m", "first"), ("example.com/m", "second")]
        out = rewrite_profile(text, mods)
        self.assertEqual(out.splitlines()[1].split(":")[0], "first/file.go")

    def test_repo_file_key_stays_on_the_second_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dest = root / "b" / "a"
            dest.mkdir(parents=True)
            (dest / "file.go").write_text("package a\n", encoding="utf-8")
            mods = [("b", "b/a")]
            text = "mode: set\nb/file.go:1.1,2.2 1 1\n"
            once = rewrite_profile(text, mods, root)
            self.assertEqual(once.splitlines()[1].split(":")[0], "b/a/file.go")
            self.assertEqual(rewrite_profile(once, mods, root), once)
            github = rewrite_profile(PROFILE, self._mods(), root)
            self.assertEqual(rewrite_profile(github, self._mods(), root), github)

    def test_rewritten_parts_match_mutator_suffix_rank(self) -> None:
        source = "/tmp/app/adapters/engram/internal/front/server.go"
        import_key = f"{NESTED_MOD}/engram/internal/front/server.go"
        text = f"mode: set\n{import_key}:10.20,12.2 1 1\n"
        out = rewrite_profile(text, self._mods())
        key = out.splitlines()[1].split(":")[0]
        source_parts = _parts(source)
        key_parts = _parts(key)
        import_parts = _parts(import_key)
        self.assertEqual(key_parts, ("adapters", "engram", "internal", "front", "server.go"))
        self.assertTrue(_trailing(source_parts, key_parts))
        self.assertFalse(_trailing(source_parts, import_parts))
        self.assertFalse(_trailing(import_parts, source_parts))

    def test_three_fields_stay(self) -> None:
        out = rewrite_profile(PROFILE, self._mods())
        self.assertEqual(len(out.splitlines()[1].split()), 3)


class ModulesTests(unittest.TestCase):
    def test_modules_parse_tracked_and_untracked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "go.mod").write_text("module github.com/acme/root\n\ngo 1.22\n", encoding="utf-8")
            nested = root / "adapters"
            nested.mkdir()
            (nested / "go.mod").write_text(
                "// comment\nmodule github.com/acme/root/adapters // note\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "go.mod"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "root"], cwd=root, check=True, capture_output=True)
            found = dict(modules(root))
            self.assertEqual(found["github.com/acme/root"], ".")
            self.assertEqual(found["github.com/acme/root/adapters"], "adapters")

    def test_module_line_comment_is_not_the_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "go.mod").write_text("module example.com/m // note\n", encoding="utf-8")
            self.assertEqual(modules(root), [("example.com/m", ".")])

    def test_modules_skip_ignored_and_non_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(modules(root), [])
            _git_init(root)
            (root / ".gitignore").write_text("vendor/\n", encoding="utf-8")
            vendor = root / "vendor"
            vendor.mkdir()
            (vendor / "go.mod").write_text("module example.com/vendored\n", encoding="utf-8")
            (root / "empty").mkdir()
            (root / "empty" / "go.mod").write_text("go 1.22\n", encoding="utf-8")
            self.assertEqual(modules(root), [])


class ProfileTreeTests(unittest.TestCase):
    def test_rewrite_tree_updates_merge_go_paths_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "go.mod").write_text("module github.com/acme/app\n", encoding="utf-8")
            body = "mode: set\ngithub.com/acme/app/main.go:1.1,2.2 1 1\n"
            paths = [
                root / "target" / "coverage" / "coverage.out",
                root / "target" / "coverage" / "go" / "coverage.out",
                root / "coverage.out",
                root / "pkg" / "target" / "coverage" / "go" / "coverage.out",
                root / "a" / "b" / "target" / "coverage" / "go" / "coverage.out",
            ]
            deep = root / "a" / "b" / "c" / "target" / "coverage" / "go" / "coverage.out"
            for path in [*paths, deep]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body, encoding="utf-8")
            rewrite_tree(root)
            for path in paths:
                self.assertIn("main.go:", path.read_text(encoding="utf-8"))
                self.assertNotIn("github.com/acme/app/main.go", path.read_text(encoding="utf-8"))
            self.assertIn("github.com/acme/app/main.go", deep.read_text(encoding="utf-8"))
            listed = {path.relative_to(root).as_posix() for path in profile_paths(root)}
            self.assertNotIn("a/b/c/target/coverage/go/coverage.out", listed)

    def test_check_reports_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "target" / "coverage" / "go" / "coverage.out"
            profile.parent.mkdir(parents=True)
            profile.write_text("mode: set\npkg/main.go:1.1,1.2 1 1\n", encoding="utf-8")
            self.assertEqual(missing_files(root, ["pkg/main.go"]), [])
            self.assertEqual(missing_files(root, ["pkg/other.go"]), ["pkg/other.go"])

    def test_cli_rewrite_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "go.mod").write_text("module github.com/acme/app\n", encoding="utf-8")
            profile = root / "coverage.out"
            profile.write_text("mode: set\ngithub.com/acme/app/main.go:1.1,2.2 1 1\n", encoding="utf-8")
            code = main(["rewrite", "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("main.go:", profile.read_text(encoding="utf-8"))
            self.assertEqual(main(["check", "--root", str(root), "main.go"]), 0)
            self.assertEqual(main(["check", "--root", str(root)]), 0)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["check", "--root", str(root), "missing.go"])
            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue().splitlines(), ["absent: missing.go"])

    def test_main_reads_sys_argv_when_argv_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "coverage.out").write_text("mode: set\npkg/main.go:1.1,1.2 1 1\n", encoding="utf-8")
            argv = ["ub_go_coverage.py", "check", "--root", str(root)]
            with patch.object(sys, "argv", argv):
                self.assertEqual(main(), 0)

    def test_check_no_profile_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["check", "--root", str(root), "pkg/main.go"])
            self.assertEqual(code, 1)
            self.assertEqual(stdout.getvalue().splitlines(), ["absent: pkg/main.go"])

    def test_check_profile_without_record_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "coverage.out").write_text("mode: set\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["check", "--root", str(root), "main.go"])
            self.assertEqual(code, 1)
            self.assertEqual(stdout.getvalue().splitlines(), ["absent: main.go"])

    def test_check_absent_scoped_file_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "target" / "coverage" / "go" / "coverage.out"
            profile.parent.mkdir(parents=True)
            profile.write_text("mode: set\npkg/main.go:1.1,1.2 1 1\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["check", "--root", str(root), "pkg/main.go", "pkg/doc.go"])
            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue().splitlines(), ["absent: pkg/doc.go"])

    def test_cli_rewrite_malformed_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "coverage.out").write_text("nope\n", encoding="utf-8")
            self.assertEqual(main(["rewrite", "--root", str(root)]), 2)


if __name__ == "__main__":
    unittest.main()
