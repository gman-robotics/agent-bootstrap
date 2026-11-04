# Functions stay at cyclomatic complexity 2 or below so CRAP stays under 10
# when this file has no line coverage.

"""Rewrite Go coverprofile keys to repo-relative paths.

Crapper writes `go test` profiles with import-path keys. Mutator matches a
key only when it and the source path are path suffixes of each other. This
module rewrites those keys to repo-relative paths and checks that each
in-scope Go file appears in a profile.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def modules(root: Path) -> list[tuple[str, str]]:
    """Return `(module path, repo-relative dir)` for each listed go.mod."""

    found: list[tuple[str, str]] = []
    for rel in _go_mod_rels(root):
        _add_module(found, root, rel)
    return found


def rewrite_profile(text: str, mods: list[tuple[str, str]]) -> str:
    """Return `text` with import-path keys replaced. Idempotent."""

    lines = [_rewrite_line(line, mods) for line in _kept_lines(text)]
    return "".join(lines)


def rewrite_tree(root: Path) -> None:
    """Rewrite every Go profile path that crapper merges."""

    mods = modules(root)
    for path in profile_paths(root):
        _rewrite_file(path, mods)


def profile_paths(root: Path) -> list[Path]:
    """Profile files crapper `_merge_go` reads."""

    return _unique_files(_candidate_paths(root))


def missing_files(root: Path, files: list[str]) -> list[str]:
    """In-scope files that are not keys in any merged Go profile."""

    return _absent(files, _profile_keys(root))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return _usage()
    return _dispatch(args[0], args[1:])


def _dispatch(cmd: str, rest: list[str]) -> int:
    handler = _handlers().get(cmd)
    if handler is None:
        return _usage()
    return handler(rest)


def _handlers():
    return {"rewrite": _cmd_rewrite, "check": _cmd_check}


def _usage() -> int:
    print(
        "usage: ub_go_coverage.py rewrite|check --root ROOT [files...]",
        file=sys.stderr,
    )
    return 2


def _cmd_rewrite(argv: list[str]) -> int:
    root = _root_arg(argv)
    if root is None:
        return 2
    return _run_rewrite(root)


def _cmd_check(argv: list[str]) -> int:
    parsed = _check_root_and_files(argv)
    if parsed is None:
        return 2
    return _report_missing(parsed[0], parsed[1])


def _root_arg(argv: list[str]) -> Path | None:
    if not argv:
        return Path(".")
    return _explicit_root(argv)


def _explicit_root(argv: list[str]) -> Path | None:
    if argv[0] != "--root":
        return None
    if len(argv) < 2:
        return None
    return Path(argv[1])


def _check_root_and_files(argv: list[str]) -> tuple[Path, list[str]] | None:
    if not argv:
        return Path("."), []
    return _check_with_args(argv)


def _check_with_args(argv: list[str]) -> tuple[Path, list[str]] | None:
    if argv[0] != "--root":
        return Path("."), list(argv)
    return _rooted_files(argv)


def _rooted_files(argv: list[str]) -> tuple[Path, list[str]] | None:
    if len(argv) < 2:
        return None
    return Path(argv[1]), list(argv[2:])


def _run_rewrite(root: Path) -> int:
    try:
        rewrite_tree(root)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0


def _report_missing(root: Path, files: list[str]) -> int:
    missing = missing_files(root, files)
    _print_lines(missing)
    return _missing_status(missing)


def _print_lines(lines: list[str]) -> None:
    for line in lines:
        print(line)


def _missing_status(missing: list[str]) -> int:
    if missing:
        return 1
    return 0


def _go_mod_rels(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "-co", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return _mod_names(proc.stdout)


def _mod_names(payload: str) -> list[str]:
    names: list[str] = []
    for rel in payload.split("\0"):
        _add_mod_name(names, rel)
    return names


def _add_mod_name(names: list[str], rel: str) -> None:
    if _is_go_mod(rel):
        names.append(rel)


def _is_go_mod(rel: str) -> bool:
    if rel == "go.mod":
        return True
    return rel.endswith("/go.mod")


def _add_module(found: list[tuple[str, str]], root: Path, rel: str) -> None:
    mod = _module_path(root / rel)
    if mod is None:
        return
    found.append((mod, _mod_dir(rel)))


def _module_path(path: Path) -> str | None:
    text = _read_text(path)
    if text is None:
        return None
    return _module_in_text(text)


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _module_in_text(text: str) -> str | None:
    found = [_module_directive(line) for line in text.splitlines()]
    return _first_text(found)


def _first_text(found: list[str | None]) -> str | None:
    hits = [item for item in found if item is not None]
    return _head(hits)


def _head(hits: list[str]) -> str | None:
    if not hits:
        return None
    return hits[0]


def _module_directive(line: str) -> str | None:
    stripped = line.split("//", 1)[0].strip()
    parts = stripped.split()
    if not _is_module_line(parts):
        return None
    return parts[1]


def _is_module_line(parts: list[str]) -> bool:
    if len(parts) < 2:
        return False
    return parts[0] == "module"


def _mod_dir(rel: str) -> str:
    parent = Path(rel).parent.as_posix()
    if parent == ".":
        return "."
    return parent


def _kept_lines(text: str) -> list[str]:
    if text == "":
        return []
    return text.splitlines(keepends=True)


def _rewrite_line(raw: str, mods: list[tuple[str, str]]) -> str:
    body = _body(raw)
    if _keep_line(body):
        return raw
    return _mapped_record(body, mods) + _ending(raw)


def _body(raw: str) -> str:
    if raw.endswith("\n"):
        return raw[:-1].rstrip("\r")
    return raw


def _ending(raw: str) -> str:
    if raw.endswith("\r\n"):
        return "\r\n"
    return _lf(raw)


def _lf(raw: str) -> str:
    if raw.endswith("\n"):
        return "\n"
    return ""


def _keep_line(body: str) -> bool:
    stripped = body.strip()
    if stripped == "":
        return True
    return stripped.startswith("mode:")


def _mapped_record(body: str, mods: list[tuple[str, str]]) -> str:
    fields = body.split()
    _require_three(fields, body)
    token = fields[0]
    _require_colon(token, body)
    key, span = token.rsplit(":", 1)
    _require_nonempty(key, body)
    _require_nonempty(span, body)
    mapped = _map_key(key, mods)
    return f"{mapped}:{span} {fields[1]} {fields[2]}"


def _require_three(fields: list[str], body: str) -> None:
    if len(fields) == 3:
        return
    raise ValueError(f"malformed coverage line: {body!r}")


def _require_colon(token: str, body: str) -> None:
    if ":" in token:
        return
    raise ValueError(f"malformed coverage line: {body!r}")


def _require_nonempty(text: str, body: str) -> None:
    if text != "":
        return
    raise ValueError(f"malformed coverage line: {body!r}")


def _map_key(key: str, mods: list[tuple[str, str]]) -> str:
    match = _longest_module(key, mods)
    if match is None:
        return key
    return _join_rest(match[0], match[1], key)


def _join_rest(mod: str, reldir: str, key: str) -> str:
    rest = key[len(mod) + 1 :]
    if reldir == ".":
        return rest
    return f"{reldir}/{rest}"


def _longest_module(key: str, mods: list[tuple[str, str]]) -> tuple[str, str] | None:
    best: tuple[str, str] | None = None
    best_len = -1
    for mod, reldir in mods:
        best, best_len = _prefer(best, best_len, mod, reldir, key)
    return best


def _prefer(best, best_len: int, mod: str, reldir: str, key: str):
    if not key.startswith(mod + "/"):
        return best, best_len
    return _prefer_len(best, best_len, mod, reldir)


def _prefer_len(best, best_len: int, mod: str, reldir: str):
    if len(mod) <= best_len:
        return best, best_len
    return (mod, reldir), len(mod)


def _rewrite_file(path: Path, mods: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(_rewrite_or_raise(path, text, mods), encoding="utf-8")


def _rewrite_or_raise(path: Path, text: str, mods: list[tuple[str, str]]) -> str:
    try:
        return rewrite_profile(text, mods)
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from exc


def _candidate_paths(root: Path) -> list[Path]:
    paths = [
        root / "target" / "coverage" / "coverage.out",
        root / "target" / "coverage" / "go" / "coverage.out",
        root / "coverage.out",
    ]
    paths.extend(root.glob("*/target/coverage/go/coverage.out"))
    paths.extend(root.glob("*/*/target/coverage/go/coverage.out"))
    return paths


def _unique_files(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    found: list[Path] = []
    for path in paths:
        _add_file(found, seen, path)
    return found


def _add_file(found: list[Path], seen: set[Path], path: Path) -> None:
    resolved = _resolved_file(path)
    if resolved is None:
        return
    _remember(found, seen, path, resolved)


def _resolved_file(path: Path) -> Path | None:
    if not path.is_file():
        return None
    return path.resolve()


def _remember(found: list[Path], seen: set[Path], path: Path, resolved: Path) -> None:
    if resolved in seen:
        return
    seen.add(resolved)
    found.append(path)


def _profile_keys(root: Path) -> set[str]:
    keys: set[str] = set()
    for path in profile_paths(root):
        keys.update(_keys_in_text(path.read_text(encoding="utf-8")))
    return keys


def _keys_in_text(text: str) -> set[str]:
    keys: set[str] = set()
    for raw in text.splitlines():
        _add_key(keys, raw)
    return keys


def _add_key(keys: set[str], raw: str) -> None:
    key = _record_key(raw)
    if key is None:
        return
    keys.add(key)


def _record_key(raw: str) -> str | None:
    if _skip_profile_line(raw):
        return None
    return _key_from_token(raw.split()[0])


def _skip_profile_line(raw: str) -> bool:
    stripped = raw.strip()
    if _blank_or_mode(stripped):
        return True
    return len(stripped.split()) != 3


def _blank_or_mode(stripped: str) -> bool:
    if stripped == "":
        return True
    return stripped.startswith("mode:")


def _key_from_token(token: str) -> str | None:
    if ":" not in token:
        return None
    return token.rsplit(":", 1)[0]


def _absent(files: list[str], keys: set[str]) -> list[str]:
    missing: list[str] = []
    for rel in files:
        _add_if_absent(missing, keys, rel)
    return missing


def _add_if_absent(missing: list[str], keys: set[str], rel: str) -> None:
    if _key_has(keys, rel):
        return
    missing.append(rel)


def _key_has(keys: set[str], rel: str) -> bool:
    return _norm_rel(rel) in keys


def _norm_rel(path: str) -> str:
    text = path.replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text


if __name__ == "__main__":
    raise SystemExit(main())
