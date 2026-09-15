#!/usr/bin/env python3
"""Mechanical structure check for ported pstack hub skills."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

PSTACK_SKILL_NAMES = frozenset(
    {
        "architect",
        "arena",
        "swarm",
        "blast-radius",
        "interrogate",
        "figure-it-out",
        "show-me-your-work",
        "create-verification-skill",
        "maintain-verification-skill",
        "how",
        "why",
        "teach",
        "technical-writing",
        "unslop",
        "reflect",
        "automate-me",
        "pstack-principles",
    }
)


def validate_skill(name: str) -> list[str]:
    errors: list[str] = []
    if name not in PSTACK_SKILL_NAMES:
        errors.append(f"unknown pstack skill name: {name}")
        return errors

    skill_md = SKILLS_DIR / name / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"missing {skill_md}")
        return errors

    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append("SKILL.md missing YAML frontmatter")
    else:
        fm = text.split("---", 2)[1]
        for field in ("name:", "description:", "version:"):
            if field not in fm:
                errors.append(f"frontmatter missing {field.strip(':')}")
        if f"name: {name}" not in fm and f'name: {name}' not in fm:
            errors.append(f"frontmatter name must be {name}")

    if re.search(r"^disable-model-invocation:\s*true\s*$", text.split("---", 2)[1], re.M):
        errors.append("Cursor-only disable-model-invocation must be stripped from frontmatter")

    if "github.com/cursor/plugins" not in text and "cursor/plugins/pstack" not in text:
        errors.append("Provenance must cite cursor/plugins/pstack")

    if "MIT" not in text:
        errors.append("Provenance must mention MIT license")

    if name == "pstack-principles":
        if "never-block-on-the-human" not in text:
            errors.append("pstack-principles must document never-block-on-the-human")
        if "Approve" not in text or "Reject" not in text:
            errors.append("pstack-principles carve-out must mention Approve/Reject gates")
        if "prove-it-works" not in text:
            errors.append("pstack-principles must include prove-it-works")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_pstack_skill.py <skill-name>", file=sys.stderr)
        return 2
    errors = validate_skill(argv[1])
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"OK: {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
