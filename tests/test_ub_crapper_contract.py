"""Fixture contract for crapper.languages.functions_in_file.

Skipped when crapper is not installed. UB_REQUIRE_CRAPPER=1 turns that skip
into a failure so the ub-gates CI job cannot pass without the real tool.
"""

import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "ub_scope"

PYTHON_SPANS = [
    ("alpha", "tests.fixtures.ub_scope.sample", 1, 2),
    ("beta", "tests.fixtures.ub_scope.sample.Box", 6, 7),
    ("gamma", "tests.fixtures.ub_scope.sample", 10, 11),
]
RUST_SPANS = [
    ("alpha", "ub_scope::sample", 1, 3),
    ("beta", "ub_scope::sample::Widget", 8, 10),
    ("gamma", "ub_scope::sample", 13, 15),
]
TYPESCRIPT_SPANS = [
    ("alpha", "tests.fixtures.ub_scope.sample", 1, 3),
    ("beta", "tests.fixtures.ub_scope.sample.Box", 6, 8),
    ("gamma", "tests.fixtures.ub_scope.sample", 11, 13),
]


def _crapper_missing() -> bool:
    try:
        import crapper  # noqa: F401
    except ImportError:
        return True
    return False


class CrapperFunctionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        if _crapper_missing():
            self._missing()

    def _missing(self) -> None:
        if os.environ.get("UB_REQUIRE_CRAPPER") == "1":
            self.fail("UB_REQUIRE_CRAPPER=1 but crapper is not importable")
        self.skipTest("crapper is not installed")

    def test_python_fixture_spans(self) -> None:
        self.assertEqual(_spans("sample.py"), PYTHON_SPANS)

    def test_rust_fixture_spans(self) -> None:
        self.assertEqual(_spans("sample.rs"), RUST_SPANS)

    def test_typescript_fixture_spans(self) -> None:
        self.assertEqual(_spans("sample.ts"), TYPESCRIPT_SPANS)


def _spans(name: str) -> list[tuple[str, str, int, int]]:
    from crapper.discover import language_of
    from crapper.languages import functions_in_file

    path = FIXTURE / name
    relative = path.relative_to(REPO_ROOT).as_posix()
    language = language_of(relative)
    source = path.read_text(encoding="utf-8")
    found = functions_in_file(language, source, relative, str(REPO_ROOT))
    return [(item.name, item.namespace, item.start_line, item.end_line) for item in found]


if __name__ == "__main__":
    unittest.main()
