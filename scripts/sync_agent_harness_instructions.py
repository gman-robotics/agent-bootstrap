#!/usr/bin/env python3
"""Upsert agent-bootstrap harness workflow blocks in target repos (GMA-410)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER_BEGIN = "<!-- agent-bootstrap-hub:BEGIN harness-workflow -->"
MARKER_END = "<!-- agent-bootstrap-hub:END harness-workflow -->"

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


def block_present(text: str) -> bool:
    return MARKER_BEGIN in text and MARKER_END in text


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
    if block_present(text):
        start = text.index(MARKER_BEGIN)
        end = text.index(MARKER_END) + len(MARKER_END)
        new_text = text[:start] + block.strip() + text[end:]
        return new_text, new_text != text
    stripped_block = block.strip() + "\n"
    if text.endswith("\n"):
        return text + "\n" + stripped_block, True
    return text + "\n\n" + stripped_block, True


def _cursor_rule_path(repo_root: Path, repo_id: str) -> Path:
    return repo_root / ".cursor/rules" / f"{repo_id}-harness.mdc"


def _cursor_rule_body(repo_id: str, block: str) -> str:
    return f"""---
description: Load standards-{repo_id}, verify/ub checks before PR, and PR templates
globs: []
alwaysApply: true
---

{block.strip()}
"""


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


def sync_repo(repo_root: Path, repo_id: str) -> bool:
    block = build_block(repo_id)
    changed = False

    agents = repo_root / "AGENTS.md"
    if not agents.exists():
        initial = f"# AGENTS.md\n\nProject agent instructions for `{repo_id}`.\n\n"
    else:
        initial = None
    changed |= sync_file(agents, initial, block)

    changed |= sync_file(repo_root / "CLAUDE.md", DEFAULT_CLAUDE, block)

    changed |= sync_file(repo_root / ".grok/README.md", DEFAULT_GROK_README, block)

    rule_path = _cursor_rule_path(repo_root, repo_id)
    rule_body = _cursor_rule_body(repo_id, block)
    if rule_path.exists():
        existing = rule_path.read_text(encoding="utf-8")
        if existing != rule_body:
            rule_path.write_text(rule_body, encoding="utf-8")
            changed = True
    else:
        rule_path.parent.mkdir(parents=True, exist_ok=True)
        rule_path.write_text(rule_body, encoding="utf-8")
        changed = True

    return changed


def verify_repo(repo_root: Path, repo_id: str) -> list[str]:
    missing: list[str] = []
    for rel in TARGET_REL_PATHS:
        path = repo_root / rel
        if not path.exists():
            missing.append(rel)
            continue
        if not block_present(path.read_text(encoding="utf-8")):
            missing.append(rel)
    rule_path = _cursor_rule_path(repo_root, repo_id)
    if not rule_path.exists():
        missing.append(str(rule_path.relative_to(repo_root)))
    elif MARKER_BEGIN not in rule_path.read_text(encoding="utf-8"):
        missing.append(str(rule_path.relative_to(repo_root)))
    return missing


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
        help="Write only when verify would fail (maintain-verification-skill)",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    repo_id = args.repo_id or repo_root.name

    if args.verify:
        missing = verify_repo(repo_root, repo_id)
        if missing:
            print("MISSING:", ", ".join(missing), file=sys.stderr)
            return 1
        print("OK: harness workflow blocks present")
        return 0

    if args.restore:
        missing = verify_repo(repo_root, repo_id)
        if not missing:
            print("OK: nothing to restore")
            return 0
        sync_repo(repo_root, repo_id)
        print("RESTORED:", ", ".join(missing))
        return 0

    changed = sync_repo(repo_root, repo_id)
    print("SYNC:", "changed" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
