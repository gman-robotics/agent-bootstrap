#!/usr/bin/env python3
"""Upsert agent-bootstrap harness workflow blocks in target repos (GMA-410)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER_BEGIN = "<!-- agent-bootstrap-hub:BEGIN harness-workflow -->"
MARKER_END = "<!-- agent-bootstrap-hub:END harness-workflow -->"

REPO_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

REPO_ROOT = Path(__file__).resolve().parent.parent
HUB_PR_TEMPLATE = REPO_ROOT / "docs/shared/hub-pull-request-template.md"

TARGET_REL_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".grok/README.md",
)

DEFAULT_CLAUDE = """# CLAUDE.md

**This project uses AGENTS.md as the single source of truth for agent instructions.**

See `AGENTS.md` in this directory for workflows, skills, and verification rules.
"""

DEFAULT_GROK_README = """# Grok project notes

Grok discovers project rules from `AGENTS.md` at the repo root and skills under `.grok/skills/` when exported.

Run `bash /path/to/agent-bootstrap/scripts/install-grok.sh` from a sibling agent-bootstrap checkout to sync hub skills into `.grok/skills/`.
"""


class MarkerError(ValueError):
    """Delimited harness-workflow markers are missing or malformed."""


def validate_markers(text: str) -> None:
    """Raise MarkerError when marker pairs are malformed."""
    begin_count = text.count(MARKER_BEGIN)
    end_count = text.count(MARKER_END)
    if begin_count == 0 and end_count == 0:
        return
    if begin_count > 1:
        raise MarkerError(f"expected at most one {MARKER_BEGIN}, found {begin_count}")
    if end_count > 1:
        raise MarkerError(f"expected at most one {MARKER_END}, found {end_count}")
    if end_count > 0 and begin_count == 0:
        raise MarkerError(f"{MARKER_END} without {MARKER_BEGIN}")
    if begin_count > 0 and end_count == 0:
        raise MarkerError(f"{MARKER_BEGIN} without {MARKER_END}")
    if text.index(MARKER_END) < text.index(MARKER_BEGIN):
        raise MarkerError(f"{MARKER_END} appears before {MARKER_BEGIN}")


def block_present(text: str) -> bool:
    try:
        validate_markers(text)
    except MarkerError:
        return False
    return MARKER_BEGIN in text and MARKER_END in text


def validate_repo_id(repo_id: str) -> str:
    if not repo_id or not REPO_ID_RE.fullmatch(repo_id):
        raise ValueError(
            "repo-id must be a lowercase slug (a-z, 0-9, hyphens; no slashes or dots)"
        )
    return repo_id


def resolve_repo_root(repo_root: Path) -> Path:
    resolved = repo_root.resolve()
    if not resolved.is_dir():
        raise ValueError(f"repo-root is not a directory: {resolved}")
    return resolved


def _path_inside_repo(repo_root: Path, path: Path) -> None:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        raise ValueError(f"path escapes repo-root: {path}") from None


def build_block(repo_id: str) -> str:
    standards_name = f"standards-{repo_id}"
    return f"""{MARKER_BEGIN}
## Agent harness workflow (agent-bootstrap)

Do **not** skip or override this block when other agent files exist.

1. **Load `skills/{standards_name}/SKILL.md`** from harness skill folders this repo already uses (for example `.cursor/skills/`, `.claude/skills/`, `.grok/skills/`). Read it at session start for PR, issue, planning, and verification formats.
2. **Before opening a PR:** run the project verify skill (`verify-*` / `bin/verify-*-ci`) and the **pre-PR ub checks** documented in `{standards_name}` and `docs/shared/ub-mode-practice.md` when bootstrapped from agent-bootstrap (crapper, dryer, mutator on merge-base scope; record results honestly).
3. **PR body:** use `.github/PULL_REQUEST_TEMPLATE.md`. Hub canonical copy: `docs/shared/hub-pull-request-template.md` when this repo tracks agent-bootstrap.
4. **PR review:** for non-trivial diffs, apply `skills/blast-radius/SKILL.md` to the changed surface before APPROVE.

Maintained by `scripts/sync_agent_harness_instructions.py` (`create-verification-skill` / `maintain-verification-skill`).
{MARKER_END}
"""


def upsert_marked_block(text: str, block: str) -> tuple[str, bool]:
    validate_markers(text)
    if block_present(text):
        start = text.index(MARKER_BEGIN)
        end = text.index(MARKER_END) + len(MARKER_END)
        new_text = text[:start] + block.strip() + text[end:]
        return new_text, new_text != text
    stripped_block = block.strip() + "\n"
    if text.endswith("\n"):
        return text + "\n" + stripped_block, True
    return text + "\n\n" + stripped_block, True


def _split_mdc_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    front = f"---{parts[1]}---"
    body = parts[2]
    if body.startswith("\n"):
        body = body[1:]
    return front, body


def _default_mdc_frontmatter(repo_id: str) -> str:
    return f"""---
description: Load standards-{repo_id}, verify/ub checks before PR, and PR templates
globs: []
alwaysApply: true
---"""


def cursor_rule_rel(repo_id: str) -> str:
    return f".cursor/rules/{repo_id}-harness.mdc"


def cursor_rule_path(repo_root: Path, repo_id: str) -> Path:
    path = repo_root / cursor_rule_rel(repo_id)
    _path_inside_repo(repo_root, path)
    return path


def sync_file(path: Path, initial: str | None, block: str) -> bool:
    if path.exists():
        text = path.read_text(encoding="utf-8")
        new_text, changed = upsert_marked_block(text, block)
        if changed:
            path.write_text(new_text, encoding="utf-8")
        return changed
    if initial is None:
        initial = ""
    if initial and not initial.endswith("\n"):
        initial += "\n"
    body = initial + ("\n" if initial else "") + block.strip() + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return True


def sync_mdc_file(path: Path, repo_id: str, block: str) -> bool:
    if path.exists():
        text = path.read_text(encoding="utf-8")
        front, body = _split_mdc_frontmatter(text)
        new_body, changed = upsert_marked_block(body, block)
        if not changed:
            return False
        if front is None:
            new_text = new_body
        else:
            new_text = front + "\n\n" + new_body
            if not new_text.endswith("\n"):
                new_text += "\n"
        path.write_text(new_text, encoding="utf-8")
        return True
    front = _default_mdc_frontmatter(repo_id)
    body = block.strip() + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(front + "\n\n" + body, encoding="utf-8")
    return True


def _all_target_rels(repo_id: str) -> tuple[str, ...]:
    return (*TARGET_REL_PATHS, cursor_rule_rel(repo_id))


def sync_targets(
    repo_root: Path, repo_id: str, only: set[str] | None = None
) -> bool:
    block = build_block(repo_id)
    changed = False
    targets = set(_all_target_rels(repo_id))
    if only is not None:
        unknown = only - targets
        if unknown:
            raise ValueError(f"unknown harness path(s): {', '.join(sorted(unknown))}")
        targets = only

    if "AGENTS.md" in targets:
        agents = repo_root / "AGENTS.md"
        initial = (
            f"# AGENTS.md\n\nProject agent instructions for `{repo_id}`.\n\n"
            if not agents.exists()
            else None
        )
        changed |= sync_file(agents, initial, block)

    if "CLAUDE.md" in targets:
        changed |= sync_file(repo_root / "CLAUDE.md", DEFAULT_CLAUDE, block)

    if ".grok/README.md" in targets:
        changed |= sync_file(
            repo_root / ".grok/README.md", DEFAULT_GROK_README, block
        )

    mdc_rel = cursor_rule_rel(repo_id)
    if mdc_rel in targets:
        changed |= sync_mdc_file(cursor_rule_path(repo_root, repo_id), repo_id, block)

    return changed


def sync_repo(repo_root: Path, repo_id: str) -> bool:
    return sync_targets(repo_root, repo_id, only=None)


def verify_repo(repo_root: Path, repo_id: str) -> list[str]:
    missing: list[str] = []
    for rel in TARGET_REL_PATHS:
        path = repo_root / rel
        if not path.exists():
            missing.append(rel)
            continue
        text = path.read_text(encoding="utf-8")
        try:
            validate_markers(text)
        except MarkerError:
            missing.append(rel)
            continue
        if not block_present(text):
            missing.append(rel)
    mdc_rel = cursor_rule_rel(repo_id)
    rule_path = cursor_rule_path(repo_root, repo_id)
    if not rule_path.exists():
        missing.append(mdc_rel)
    else:
        text = rule_path.read_text(encoding="utf-8")
        _, body = _split_mdc_frontmatter(text)
        try:
            validate_markers(body)
        except MarkerError:
            missing.append(mdc_rel)
        else:
            if not block_present(body):
                missing.append(mdc_rel)
    return missing


def restore_repo(repo_root: Path, repo_id: str) -> tuple[list[str], bool]:
    missing = verify_repo(repo_root, repo_id)
    if not missing:
        return [], False
    changed = sync_targets(repo_root, repo_id, only=set(missing))
    return missing, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Target repository root",
    )
    parser.add_argument(
        "--repo-id",
        help="Repository id for standards-<repo> (default: directory basename)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Exit 1 when harness blocks are missing (no writes)",
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Write only paths --verify reports missing (maintain-verification-skill)",
    )
    args = parser.parse_args(argv)

    try:
        repo_root = resolve_repo_root(args.repo_root)
        repo_id = validate_repo_id(args.repo_id or repo_root.name)
        cursor_rule_path(repo_root, repo_id)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.verify:
        missing = verify_repo(repo_root, repo_id)
        if missing:
            print("MISSING:", ", ".join(missing), file=sys.stderr)
            return 1
        print("OK: harness workflow blocks present")
        return 0

    if args.restore:
        try:
            missing, _changed = restore_repo(repo_root, repo_id)
        except MarkerError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        if not missing:
            print("OK: nothing to restore")
            return 0
        print("RESTORED:", ", ".join(missing))
        return 0

    try:
        changed = sync_repo(repo_root, repo_id)
    except MarkerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("SYNC:", "changed" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
