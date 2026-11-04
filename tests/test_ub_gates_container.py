"""Checks for scripts/ub_gates_container.sh. These tests do not run docker."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "ub_gates_container.sh"


class UbGatesContainerTests(unittest.TestCase):
    def test_bash_n_accepts_the_script(self) -> None:
        proc = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_help_describes_throwaway_container(self) -> None:
        proc = subprocess.run(["bash", str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Usage:", proc.stdout)
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("docker run", text)
        self.assertIn("--rm", text)
        self.assertIn("rust:1.83", text)
        self.assertIn("golang:1.26", text)
        self.assertIn("UB_GATES_IMAGE", text)
        self.assertIn(":ro", text)
        self.assertIn("uv venv", text)
        self.assertIn("UB_GATES_ADVISORY=0", text)

    def test_docker_stub_records_passthrough_mounts_and_safe_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stub_dir = root / "bin"
            stub_dir.mkdir()
            record = root / "docker-record"
            record.mkdir()
            stub = stub_dir / "docker"
            stub.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        f'printf "%s\\n" "$@" > "{record / "argv"}"',
                        f'cat > "{record / "stdin"}"',
                        "exit 0",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stub.chmod(0o755)
            work = root / "work"
            work.mkdir()
            _write_lock(work)
            main_git = root / "main-git"
            main_git.mkdir()
            metrics = root / "metrics"
            env = os.environ.copy()
            env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
            env["UB_GATES_COVERAGE_CMD"] = "echo coverage marker"
            env["UB_GATES_MUTATOR_TEST_CMD"] = "echo mutator marker"
            env["UB_GATES_BASE_REF"] = "origin/release"
            proc = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--worktree",
                    str(work),
                    "--main-git",
                    str(main_git),
                    "--metrics-dir",
                    str(metrics),
                ],
                env=env,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            argv = (record / "argv").read_text(encoding="utf-8")
            stdin = (record / "stdin").read_text(encoding="utf-8")
            recorded = argv + "\n" + stdin
            self.assertIn("--rm", recorded)
            self.assertIn("rust:1.83", recorded)
            self.assertIn(f"{work}:/work:ro", recorded)
            self.assertIn(f"{main_git}:{main_git}:ro", recorded)
            self.assertIn("UB_GATES_ADVISORY=0", recorded)
            self.assertIn("UB_GATES_BASE_REF=origin/release", recorded)
            self.assertIn("UB_GATES_COVERAGE_CMD=echo coverage marker", recorded)
            self.assertIn("UB_GATES_MUTATOR_TEST_CMD=echo mutator marker", recorded)
            self.assertIn("git config --global --add safe.directory", recorded)

    def test_installs_requirements_dev_into_the_venv(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("[[ -f /work/requirements-dev.txt ]]", text)
        self.assertIn("uv pip install -r /work/requirements-dev.txt", text)
        self.assertIn('UB_GATES_COVERAGE_CMD=${UB_GATES_COVERAGE_CMD:-}', text)
        self.assertIn('UB_GATES_MUTATOR_TEST_CMD=${UB_GATES_MUTATOR_TEST_CMD:-}', text)
        self.assertIn("UB_GATES_ADVISORY=0", text)
        self.assertLess(
            text.find('uv pip install "${dest}/crapper"'),
            text.find("uv pip install -r /work/requirements-dev.txt"),
        )

    def test_cleared_clone_matches_the_mounted_tree(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("overlay_worktree()", text)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src-repo"
            src.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=src, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "ub-gates@example.com"], cwd=src, check=True)
            subprocess.run(["git", "config", "user.name", "ub-gates"], cwd=src, check=True)
            (src / "scripts").mkdir()
            (src / "src").mkdir()
            (src / "scripts" / "run.sh").write_text("echo hi\n", encoding="utf-8")
            (src / "src" / "lib.rs").write_text("fn main() {}\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=src, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=src, check=True, capture_output=True)
            (src / "notes.txt").write_text("untracked\n", encoding="utf-8")
            (src / "target").mkdir()
            (src / "target" / "junk").write_text("keep\n", encoding="utf-8")
            (src / ".metrics").mkdir()
            (src / ".metrics" / "x").write_text("keep\n", encoding="utf-8")
            dest = root / "clone"
            subprocess.run(
                ["git", "clone", "--quiet", str(src), str(dest)],
                check=True,
                capture_output=True,
                text=True,
            )
            (dest / "stale.txt").write_text("stale\n", encoding="utf-8")
            (dest / "src" / "src").mkdir()
            (dest / "src" / "src" / "nested.rs").write_text("nested\n", encoding="utf-8")
            proc = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1"; overlay_worktree "$2" "$3"',
                    "_",
                    str(SCRIPT),
                    str(src),
                    str(dest),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse((dest / "src" / "src").exists())
            self.assertFalse((dest / "scripts" / "scripts").exists())
            self.assertFalse((dest / "stale.txt").exists())
            self.assertTrue((dest / ".git").exists())
            self.assertEqual((dest / "scripts" / "run.sh").read_text(encoding="utf-8"), "echo hi\n")
            self.assertEqual((dest / "src" / "lib.rs").read_text(encoding="utf-8"), "fn main() {}\n")
            self.assertEqual((dest / "notes.txt").read_text(encoding="utf-8"), "untracked\n")
            self.assertEqual((dest / "target" / "junk").read_text(encoding="utf-8"), "keep\n")
            self.assertEqual((dest / ".metrics" / "x").read_text(encoding="utf-8"), "keep\n")

    def test_base_ref_comes_from_the_mounted_worktree(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("map_base_ref()", text)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src-repo"
            src.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=src, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "ub-gates@example.com"], cwd=src, check=True)
            subprocess.run(["git", "config", "user.name", "ub-gates"], cwd=src, check=True)
            (src / "f.txt").write_text("a\n", encoding="utf-8")
            subprocess.run(["git", "add", "f.txt"], cwd=src, check=True)
            subprocess.run(["git", "commit", "-m", "a"], cwd=src, check=True, capture_output=True)
            old = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=src, check=True, capture_output=True, text=True
            ).stdout.strip()
            (src / "f.txt").write_text("b\n", encoding="utf-8")
            subprocess.run(["git", "add", "f.txt"], cwd=src, check=True)
            subprocess.run(["git", "commit", "-m", "b"], cwd=src, check=True, capture_output=True)
            upstream = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=src, check=True, capture_output=True, text=True
            ).stdout.strip()
            subprocess.run(["git", "update-ref", "refs/remotes/origin/main", upstream], cwd=src, check=True)
            subprocess.run(["git", "reset", "--hard", old], cwd=src, check=True, capture_output=True)
            dest = root / "clone"
            subprocess.run(
                ["git", "clone", "--quiet", str(src), str(dest)],
                check=True,
                capture_output=True,
                text=True,
            )
            cloned = subprocess.run(
                ["git", "rev-parse", "refs/remotes/origin/main"],
                cwd=dest,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(cloned, old)
            env = os.environ.copy()
            env["UB_GATES_BASE_REF"] = "origin/main"
            proc = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1"; map_base_ref "$2" "$3"',
                    "_",
                    str(SCRIPT),
                    str(src),
                    str(dest),
                ],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            mapped = subprocess.run(
                ["git", "rev-parse", "refs/remotes/origin/main"],
                cwd=dest,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(mapped, upstream)

    def test_local_scope_commit_includes_untracked_files(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("commit_local_scope()", text)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src-repo"
            src.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=src, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "ub-gates@example.com"], cwd=src, check=True)
            subprocess.run(["git", "config", "user.name", "ub-gates"], cwd=src, check=True)
            (src / "tracked.txt").write_text("tracked\n", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.txt"], cwd=src, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=src, check=True, capture_output=True)
            (src / "notes.txt").write_text("untracked\n", encoding="utf-8")
            dest = root / "clone"
            subprocess.run(
                ["git", "clone", "--quiet", str(src), str(dest)],
                check=True,
                capture_output=True,
                text=True,
            )
            proc = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1"; overlay_worktree "$2" "$3"; (cd "$3" && commit_local_scope)',
                    "_",
                    str(SCRIPT),
                    str(src),
                    str(dest),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            shown = subprocess.run(
                ["git", "show", "HEAD:notes.txt"],
                cwd=dest,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(shown.stdout, "untracked\n")

    def test_pick_image_reads_lock_and_go_mod(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            _git_repo(work)
            _write_lock(work, rust="rust:from-lock", go="golang:1.26")
            rust = _pick_image(work)
            self.assertEqual(rust.returncode, 0, rust.stderr)
            self.assertEqual(rust.stdout.strip(), "rust:from-lock")
            (work / "go.mod").write_text("module example.com/app\n", encoding="utf-8")
            go = _pick_image(work)
            self.assertEqual(go.returncode, 0, go.stderr)
            self.assertEqual(go.stdout.strip(), "golang:1.26")
            forced = _pick_image(work, {"UB_GATES_IMAGE": "example.invalid/override:9"})
            self.assertEqual(forced.returncode, 0, forced.stderr)
            self.assertEqual(forced.stdout.strip(), "example.invalid/override:9")

    def test_pick_image_mixed_modules_asks_for_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            _git_repo(work)
            _write_lock(work)
            (work / "go.mod").write_text("module example.com/app\n", encoding="utf-8")
            (work / "Cargo.toml").write_text("[package]\nname = \"app\"\n", encoding="utf-8")
            proc = _pick_image(work)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("UB_GATES_IMAGE", proc.stderr)

    def test_pick_image_go_dash_mod_is_not_a_go_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            _git_repo(work)
            _write_lock(work, rust="rust:from-lock", go="golang:1.26")
            (work / "go-mod").write_text("not a module\n", encoding="utf-8")
            proc = _pick_image(work)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "rust:from-lock")

    def test_pick_image_git_failure_uses_rust_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            _write_lock(work, rust="rust:from-lock", go="golang:1.26")
            (work / "go.mod").write_text("module example.com/app\n", encoding="utf-8")
            proc = _pick_image(work)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "rust:from-lock")

    def test_docker_stub_uses_go_image_from_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stub_dir = root / "bin"
            stub_dir.mkdir()
            record = root / "docker-record"
            record.mkdir()
            stub = stub_dir / "docker"
            stub.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        f'printf "%s\\n" "$@" > "{record / "argv"}"',
                        "exit 0",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stub.chmod(0o755)
            work = root / "work"
            work.mkdir()
            _git_repo(work)
            _write_lock(work)
            (work / "go.mod").write_text("module example.com/app\n", encoding="utf-8")
            metrics = root / "metrics"
            env = os.environ.copy()
            env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
            env.pop("UB_GATES_IMAGE", None)
            proc = subprocess.run(
                ["bash", str(SCRIPT), "--worktree", str(work), "--metrics-dir", str(metrics)],
                env=env,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            argv = (record / "argv").read_text(encoding="utf-8")
            self.assertIn("golang:1.26", argv)
            self.assertNotIn("rust:1.83", argv)


def _write_lock(work: Path, rust: str = "rust:1.83", go: str = "golang:1.26") -> None:
    scripts = work / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "ub-tools.lock").write_text(f"rust_image={rust}\ngo_image={go}\n", encoding="utf-8")


def _git_repo(work: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=work, check=True, capture_output=True)


def _pick_image(work: Path, extra: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.pop("UB_GATES_IMAGE", None)
    if extra:
        env.update(extra)
    return subprocess.run(
        ["bash", "-c", 'source "$1"; pick_image "$2"', "_", str(SCRIPT), str(work)],
        capture_output=True,
        text=True,
        env=env,
    )


if __name__ == "__main__":
    unittest.main()
