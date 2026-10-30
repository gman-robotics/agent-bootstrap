"""Changed-line scope for the ub-gates.

`UB_SCOPE_FUNCTIONS_JSON` is a test seam. When it is set, `crap` reads that
JSON file instead of importing crapper. Each object is
`{namespace, name, start_line, end_line, path}`.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
_NAME = re.compile(r'^"((?:\\.|[^"\\])*)"')
_NS = re.compile(r':namespace\s+"((?:\\.|[^"\\])*)"')
_CRAP = re.compile(r":crap\s+(nil|-?\d+(?:\.\d+)?)")
_SCORE = re.compile(r":score\s+([\d.]+)")
_SPAN = re.compile(
    r'\{:file\s+"((?:\\.|[^"\\])*)"\s*,\s*:start-line\s+(\d+)\s*,\s*:end-line\s+(\d+)\}'
)


class CrapperUnavailable(Exception):
    """crapper could not be imported."""


class ScopeJoinError(Exception):
    """A changed-file crapper row could not be joined to a span."""


@dataclass
class FnSpan:
    namespace: str
    name: str
    start_line: int
    end_line: int
    path: str


@dataclass
class CrapRow:
    namespace: str
    name: str
    crap: float | None


@dataclass
class Span:
    file: str
    start_line: int
    end_line: int


@dataclass
class DryRow:
    score: float
    left: Span | None
    right: Span | None


Provider = Callable[[Path, Path], list[FnSpan]]


def _strip_tab(raw: str) -> str:
    return raw.partition("\t")[0].strip()


def _unquote(raw: str) -> str:
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    return raw


def _b_path(raw: str) -> str | None:
    if raw.startswith("b/"):
        return raw[2:]
    return None


def plus_path(line: str) -> str | None:
    if not line.startswith("+++ "):
        return None
    return _b_path(_unquote(_strip_tab(line[4:])))


def _hunk_count(raw: str | None) -> int:
    if raw is None:
        return 1
    return int(raw)


def _span_numbers(start: int, count: int) -> list[int]:
    return list(range(start, start + count))


def hunk_added_lines(line: str) -> list[int]:
    match = _HUNK.match(line)
    if match is None:
        return []
    return _span_numbers(int(match.group(1)), _hunk_count(match.group(2)))


def _remember(found: dict[str, set[int]], path: str | None) -> str | None:
    if path is None:
        return None
    found.setdefault(path, set())
    return path


def _add_numbers(found: dict[str, set[int]], path: str, line: str) -> None:
    for number in hunk_added_lines(line):
        found[path].add(number)


def _add_hunk(found: dict[str, set[int]], path: str | None, line: str) -> None:
    if path is None:
        return
    _add_numbers(found, path, line)


def _on_body(found: dict[str, set[int]], current: str | None, line: str) -> str | None:
    if line.startswith("+++ "):
        return _remember(found, plus_path(line))
    _add_hunk(found, current, line)
    return current


def _on_line(found: dict[str, set[int]], current: str | None, line: str) -> str | None:
    if line.startswith("diff --git "):
        return None
    return _on_body(found, current, line)


def _sorted_lines(found: dict[str, set[int]]) -> dict[str, list[int]]:
    return {key: sorted(values) for key, values in found.items()}


def changed_lines_from_diff(text: str) -> dict[str, list[int]]:
    found: dict[str, set[int]] = {}
    current: str | None = None
    for line in text.splitlines():
        current = _on_line(found, current, line)
    return _sorted_lines(found)


def git_diff_text(base: str) -> str:
    proc = subprocess.run(
        ["git", "diff", "-U0", "--diff-filter=ACMRT", base, "HEAD"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git diff failed")
    return proc.stdout


def _unescape(value: str) -> str:
    return value.replace('\\"', '"').replace("\\\\", "\\")


def _chunks(text: str) -> list[str]:
    parts = text.split("{:name ")
    parts.pop(0)
    return parts


def _crap_number(token: str) -> float | None:
    if token == "nil":
        return None
    return float(token)


def _crap_value(rest: str) -> float | None:
    match = _CRAP.search(rest)
    if match is None:
        return None
    return _crap_number(match.group(1))


def _crap_named(name: str, rest: str) -> CrapRow | None:
    namespace = _NS.search(rest)
    if namespace is None:
        return None
    return CrapRow(_unescape(namespace.group(1)), _unescape(name), _crap_value(rest))


def _crap_row(chunk: str) -> CrapRow | None:
    name = _NAME.match(chunk)
    if name is None:
        return None
    return _crap_named(name.group(1), chunk[name.end() :])


def _append_crap(rows: list[CrapRow], chunk: str) -> None:
    row = _crap_row(chunk)
    if row is not None:
        rows.append(row)


def parse_crap_edn(text: str) -> list[CrapRow]:
    rows: list[CrapRow] = []
    for chunk in _chunks(text):
        _append_crap(rows, chunk)
    return rows


def _span_from_match(match: re.Match[str]) -> Span:
    return Span(_unescape(match.group(1)), int(match.group(2)), int(match.group(3)))


def _at(items: list, index: int):
    if index >= len(items):
        return None
    return items[index]


def _two_spans(part: str) -> tuple[Span | None, Span | None]:
    spans = [_span_from_match(match) for match in _SPAN.finditer(part)]
    return _at(spans, 0), _at(spans, 1)


def _dry_row(part: str) -> DryRow | None:
    score = _SCORE.search(part)
    if score is None:
        return None
    left, right = _two_spans(part)
    return DryRow(float(score.group(1)), left, right)


def _dry_parts(text: str) -> list[str]:
    return [part for part in re.split(r"(?=\{:score\b)", text) if ":score" in part]


def _append_dry(rows: list[DryRow], part: str) -> None:
    row = _dry_row(part)
    if row is not None:
        rows.append(row)


def parse_dry_edn(text: str) -> list[DryRow]:
    rows: list[DryRow] = []
    for part in _dry_parts(text):
        _append_dry(rows, part)
    return rows


_SOURCE_SUFFIXES = (
    ".bb",
    ".cjs",
    ".clj",
    ".cljc",
    ".cljs",
    ".cts",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".mjs",
    ".mts",
    ".py",
    ".rs",
    ".ts",
    ".tsx",
)


def _normalize_rel(path: str) -> str:
    return path.replace("\\", "/")


def _is_source(rel: str) -> bool:
    name = Path(_normalize_rel(rel)).name
    if name.endswith(".d.ts"):
        return False
    return Path(name).suffix in _SOURCE_SUFFIXES


def _under_root(text: str, root: Path | None) -> str | None:
    if root is None:
        return None
    base = root.resolve().as_posix().rstrip("/") + "/"
    resolved = Path(text).resolve().as_posix()
    if resolved.startswith(base):
        return resolved[len(base) :]
    return None


def _repo_rel(path: str, root: Path | None) -> str | None:
    text = _normalize_rel(path)
    if text.startswith("/"):
        return _under_root(text, root)
    return text


def _same_repo_path(left: str, right: str, root: Path | None) -> bool:
    one = _repo_rel(left, root)
    if one is None:
        return False
    other = _repo_rel(right, root)
    if other is None:
        return False
    return one == other


def _lines_for_key(rel: str, key: str, lines: list[int], root: Path | None) -> list[int] | None:
    if _repo_rel(key, root) == rel:
        return lines
    return None


def lines_for_path(path: str, changed: dict[str, list[int]], root: Path | None = None) -> list[int]:
    rel = _repo_rel(path, root)
    if rel is None:
        return []
    for key, lines in changed.items():
        found = _lines_for_key(rel, key, lines, root)
        if found is not None:
            return found
    return []


def _inside(start: int, end: int, number: int) -> bool:
    if number < start:
        return False
    return number <= end


def _span_hits(start: int, end: int, lines: list[int]) -> bool:
    return any(_inside(start, end, number) for number in lines)


def _function_hits(fn: FnSpan, changed: dict[str, list[int]], root: Path | None) -> bool:
    return _span_hits(fn.start_line, fn.end_line, lines_for_path(fn.path, changed, root))


def _same_fn(fn: FnSpan, row: CrapRow) -> bool:
    if fn.name != row.name:
        return False
    return fn.namespace == row.namespace


def _named(functions: list[FnSpan], row: CrapRow) -> list[FnSpan]:
    return [fn for fn in functions if _same_fn(fn, row)]


def _any_changed(functions: list[FnSpan], changed: dict[str, list[int]], root: Path | None) -> bool:
    return any(_function_hits(fn, changed, root) for fn in functions)


def _crap_payload(row: CrapRow) -> dict[str, object]:
    return {"namespace": row.namespace, "name": row.name, "crap": row.crap}


def _append_if_over(row: CrapRow, threshold: float, findings: list[dict[str, object]]) -> None:
    if row.crap > threshold:
        findings.append(_crap_payload(row))


def _nil_coverage(row: CrapRow, coverage_expected: bool) -> None:
    if coverage_expected:
        raise ScopeJoinError(f"no coverage for {row.namespace} {row.name}")


def _keep_finding(
    row: CrapRow,
    threshold: float,
    findings: list[dict[str, object]],
    coverage_expected: bool,
) -> None:
    if row.crap is None:
        _nil_coverage(row, coverage_expected)
        return
    _append_if_over(row, threshold, findings)


def _keep_debt(row: CrapRow, matched: list[FnSpan], debt: list[dict[str, object]]) -> None:
    if matched:
        debt.append(_crap_payload(row))


def _unjoined(row: CrapRow, threshold: float) -> None:
    if row.crap is None:
        return
    if row.crap > threshold:
        raise ScopeJoinError(f"unjoined {row.namespace} {row.name}")


def _classify_crap(
    row: CrapRow,
    functions: list[FnSpan],
    changed: dict[str, list[int]],
    threshold: float,
    findings: list[dict[str, object]],
    debt: list[dict[str, object]],
    root: Path | None,
    coverage_expected: bool,
) -> None:
    matched = _named(functions, row)
    if not matched:
        _unjoined(row, threshold)
        return
    if _any_changed(matched, changed, root):
        _keep_finding(row, threshold, findings, coverage_expected)
        return
    _keep_debt(row, matched, debt)


def _collect(changed: dict[str, list[int]], provider: Provider, root: Path) -> list[FnSpan]:
    found: list[FnSpan] = []
    for rel in changed:
        if _is_source(rel):
            found.extend(provider(root / rel, root))
    return found


def filter_crap(
    edn_text: str,
    changed: dict[str, list[int]],
    provider: Provider,
    threshold: float = 10.0,
    root: Path | None = None,
    *,
    coverage_expected: bool = False,
) -> dict[str, list[dict[str, object]]]:
    base = root or Path(".")
    findings: list[dict[str, object]] = []
    debt: list[dict[str, object]] = []
    functions = _collect(changed, provider, base)
    for row in parse_crap_edn(edn_text):
        _classify_crap(row, functions, changed, threshold, findings, debt, base, coverage_expected)
    return {"findings": findings, "debt": debt}


def _span_payload(span: Span | None) -> dict[str, object] | None:
    if span is None:
        return None
    return {"file": span.file, "start_line": span.start_line, "end_line": span.end_line}


def _dry_payload(row: DryRow) -> dict[str, object]:
    return {"score": row.score, "left": _span_payload(row.left), "right": _span_payload(row.right)}


def _span_overlap(span: Span | None, changed: dict[str, list[int]], root: Path | None) -> bool:
    if span is None:
        return False
    return _span_hits(span.start_line, span.end_line, lines_for_path(span.file, changed, root))


def _either_side(row: DryRow, changed: dict[str, list[int]], root: Path | None) -> bool:
    if _span_overlap(row.left, changed, root):
        return True
    return _span_overlap(row.right, changed, root)


def _dry_is_finding(row: DryRow, changed: dict[str, list[int]], threshold: float, root: Path | None) -> bool:
    if row.score < threshold:
        return False
    return _either_side(row, changed, root)


def _classify_dry(
    row: DryRow,
    changed: dict[str, list[int]],
    threshold: float,
    findings: list[dict[str, object]],
    debt: list[dict[str, object]],
    root: Path | None,
) -> None:
    if _dry_is_finding(row, changed, threshold, root):
        findings.append(_dry_payload(row))
        return
    debt.append(_dry_payload(row))


def filter_dry(
    edn_text: str,
    changed: dict[str, list[int]],
    threshold: float = 0.8,
    root: Path | None = None,
) -> dict[str, list[dict[str, object]]]:
    findings: list[dict[str, object]] = []
    debt: list[dict[str, object]] = []
    for row in parse_dry_edn(edn_text):
        _classify_dry(row, changed, threshold, findings, debt, root)
    return {"findings": findings, "debt": debt}


def _span_from_item(item: dict[str, object]) -> FnSpan:
    return FnSpan(
        str(item["namespace"]),
        str(item["name"]),
        int(item["start_line"]),
        int(item["end_line"]),
        str(item["path"]).replace("\\", "/"),
    )


def _append_span(found: list[FnSpan], item: dict[str, object], path: Path, root: Path) -> None:
    raw = str(item["path"]).replace("\\", "/")
    if _same_repo_path(path.as_posix(), raw, root):
        found.append(_span_from_item(item))


def _spans_for(rows: list[dict[str, object]], path: Path, root: Path) -> list[FnSpan]:
    found: list[FnSpan] = []
    for item in rows:
        _append_span(found, item, path, root)
    return found


def functions_from_json(spec: str, path: Path, root: Path) -> list[FnSpan]:
    rows = json.loads(Path(spec).read_text(encoding="utf-8"))
    return _spans_for(rows, path, root)


def _crapper_api():
    try:
        from crapper.discover import language_of
        from crapper.languages import functions_in_file
    except ImportError as exc:
        raise CrapperUnavailable("crapper is not importable") from exc
    return language_of, functions_in_file


def _require_crapper() -> None:
    if os.environ.get("UB_SCOPE_FUNCTIONS_JSON"):
        return
    _crapper_api()


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _from_function(item: object, relative: str) -> FnSpan:
    return FnSpan(item.namespace, item.name, item.start_line, item.end_line, relative)


def _read_functions(functions_in_file, language: str, path: Path, root: Path) -> list[FnSpan]:
    relative = _relative(path, root)
    source = path.read_text(encoding="utf-8", errors="replace")
    found = functions_in_file(language, source, relative, str(root.resolve()))
    return [_from_function(item, relative) for item in found]


def _reject_unknown_language(language: str | None, path: Path) -> str:
    if language is None:
        raise ScopeJoinError(f"no language for {path.as_posix()}")
    return language


def functions_from_crapper(path: Path, root: Path) -> list[FnSpan]:
    language_of, functions_in_file = _crapper_api()
    language = _reject_unknown_language(language_of(path), path)
    return _read_functions(functions_in_file, language, path, root)


def default_provider(path: Path, root: Path) -> list[FnSpan]:
    spec = os.environ.get("UB_SCOPE_FUNCTIONS_JSON")
    if spec:
        return functions_from_json(spec, path, root)
    return functions_from_crapper(path, root)


def _flag(argv: list[str], name: str) -> str | None:
    if name not in argv:
        return None
    return _at(argv, argv.index(name) + 1)


def _usage() -> int:
    print("usage: ub_changed_scope.py lines|crap|dry ...", file=sys.stderr)
    return 1


def _emit_lines(changed: dict[str, list[int]], one: str | None) -> None:
    if one is None:
        print(json.dumps(changed))
        return
    print(",".join(str(number) for number in changed.get(one, [])))


def _print_lines(base: str, one: str | None) -> int:
    try:
        changed = changed_lines_from_diff(git_diff_text(base))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    _emit_lines(changed, one)
    return 0


def cmd_lines(argv: list[str]) -> int:
    base = _flag(argv, "--base")
    if base is None:
        print("lines requires --base", file=sys.stderr)
        return 1
    return _print_lines(base, _flag(argv, "--file"))


def _need(base: str | None, edn: str | None) -> bool:
    if base is None:
        return False
    return edn is not None


def _threshold(argv: list[str], default: float) -> float:
    raw = _flag(argv, "--threshold")
    if raw is None:
        return default
    return float(raw)


def _coverage_expected(argv: list[str]) -> bool:
    return "--coverage-expected" in argv


def _payload(
    kind: str,
    base: str,
    edn: str,
    threshold: float,
    coverage_expected: bool,
) -> dict[str, list[dict[str, object]]]:
    changed = changed_lines_from_diff(git_diff_text(base))
    text = Path(edn).read_text(encoding="utf-8")
    if kind == "crap":
        return filter_crap(
            text,
            changed,
            default_provider,
            threshold,
            Path.cwd(),
            coverage_expected=coverage_expected,
        )
    return filter_dry(text, changed, threshold, Path.cwd())


def _filter_error(exc: Exception) -> int:
    print(str(exc), file=sys.stderr)
    if isinstance(exc, CrapperUnavailable):
        return 2
    return 1


def _print_payload(kind: str, base: str, edn: str, argv: list[str], default_threshold: float) -> int:
    try:
        payload = _payload(
            kind,
            base,
            edn,
            _threshold(argv, default_threshold),
            _coverage_expected(argv),
        )
    except (RuntimeError, OSError, CrapperUnavailable, ValueError, ScopeJoinError) as exc:
        return _filter_error(exc)
    print(json.dumps(payload))
    return 0


def _cmd_filter(kind: str, argv: list[str], default_threshold: float) -> int:
    base = _flag(argv, "--base")
    edn = _flag(argv, "--edn")
    if not _need(base, edn):
        print(f"{kind} requires --base and --edn", file=sys.stderr)
        return 1
    return _print_payload(kind, base, edn, argv, default_threshold)


def cmd_crap(argv: list[str]) -> int:
    try:
        _require_crapper()
    except CrapperUnavailable as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return _cmd_filter("crap", argv, 10.0)


def cmd_dry(argv: list[str]) -> int:
    return _cmd_filter("dry", argv, 0.8)


def _dispatch(command: str, argv: list[str]) -> int:
    commands = {"lines": cmd_lines, "crap": cmd_crap, "dry": cmd_dry}
    func = commands.get(command)
    if func is None:
        return _usage()
    return func(argv)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return _usage()
    return _dispatch(args[0], args[1:])


if __name__ == "__main__":
    sys.exit(main())
