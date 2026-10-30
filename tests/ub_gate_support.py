"""Git fixtures shared by the ub-gates tests."""

import subprocess
from pathlib import Path


def run_git(repo: Path, args: list[str]) -> None:
    proc = subprocess.run(["git", *args], cwd=repo)
    if proc.returncode != 0:
        raise AssertionError(proc.returncode)


def init_repo(repo: Path) -> None:
    for args in (
        ["init", "-b", "main"],
        ["config", "user.email", "t@example.com"],
        ["config", "user.name", "t"],
    ):
        run_git(repo, args)


def commit_all(repo: Path, message: str) -> None:
    run_git(repo, ["add", "."])
    run_git(repo, ["commit", "-m", message])


def crapper_importable() -> bool:
    try:
        import crapper  # noqa: F401
    except ImportError:
        return False
    return True


def write_text(repo: Path, rel: str, text: str) -> Path:
    path = repo / rel
    _ensure(path.parent)
    path.write_text(text, encoding="utf-8")
    return path


def _ensure(path: Path) -> None:
    if path.is_dir():
        return
    _ensure(path.parent)
    path.mkdir()


def make_repo(repo: Path, kind: str) -> None:
    spec = _REPO_SPEC[kind]
    if spec is None:
        return
    init_repo(repo)
    base, base_msg, branch, head, head_msg = spec
    for rel, text in base:
        write_text(repo, rel, text)
    if base:
        commit_all(repo, base_msg)
    if branch == "orphan":
        run_git(repo, ["checkout", "--orphan", "other"])
    elif branch:
        run_git(repo, ["checkout", "-b", branch])
    for rel, text in head:
        write_text(repo, rel, text)
    if head:
        commit_all(repo, head_msg)


_PY_BEFORE = "def f():\n    return 1\n"
_PY_AFTER = "def f():\n    return 2\n"

_REPO_SPEC = {
    "not_git": None,
    "no_base": ((("a.py", "x = 1\n"),), "only", "", (), ""),
    "orphan": ((("a.py", "x = 1\n"),), "mainline", "orphan", (("a.py", "y = 2\n"),), "other"),
    "readme": ((("README.md", "a\n"),), "base", "feat", (("README.md", "b\n"),), "change"),
    "foo": ((("scripts/foo.py", "x = 1\n"),), "base", "feat", (("scripts/foo.py", "x = 2\n"),), "change"),
    "one": ((("lib/a.py", _PY_BEFORE),), "base", "feat", (("lib/a.py", _PY_AFTER),), "change"),
    "two": (
        (("lib/a.py", _PY_BEFORE), ("lib/b.py", "def g():\n    return 1\n")),
        "base",
        "feat",
        (("lib/a.py", _PY_AFTER), ("lib/b.py", "def g():\n    return 2\n")),
        "change",
    ),
    "lines": ((("lib/a.py", "a\nb\nc\n"),), "base", "feat", (("lib/a.py", "a\nB\nc\n"),), "change"),
    "seam": ((("a.py", _PY_BEFORE),), "base", "feat", (("a.py", _PY_AFTER),), "change"),
}
