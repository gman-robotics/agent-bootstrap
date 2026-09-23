#!/usr/bin/env python3
"""Mechanical structure check for ported pstack hub skills."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

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

WORKFLOW_SKILL_NAMES = PSTACK_SKILL_NAMES - {"pstack-principles"}

HOUSE_SECTIONS = (
    "**Purpose**",
    "**Do not use for**",
    "## Companions",
    "**Verification**",
)

CURSOR_LEFTOVER_CHECKS: list[tuple[str, str]] = [
    (r"\.cursor/skills", ".cursor/skills paths"),
    (r"~/.cursor/projects", "~/.cursor/projects paths"),
    (r"Cursor's built-in [`']?create-skill", "Cursor's built-in create-skill"),
    (r"from the Cursor environment", "Cursor environment (operational language)"),
    (r'environment:\s*["\']cloud["\']', 'required environment: "cloud" spawn parameter'),
    (r"\bvia create-skill\b", "bare create-skill reference"),
    (r"follow [`']?create-skill[`']?", "create-skill authoring reference"),
    (r"run_in_background:\s*true", "required run_in_background: true spawn parameter"),
    (r"base branch override for cloud subagents", "cloud subagent base-branch override"),
]

# Bidirectional companion pairs: each side must cite the other in Do not use for + Companions.
COMPANION_PAIRS: tuple[tuple[str, str], ...] = (
    ("show-me", "show-me-your-work"),
    ("expert-pr-review", "interrogate"),
    ("security-audit", "expert-pr-review"),
    ("security-audit", "blast-radius"),
)

COMPANION_SKILL_NAMES = frozenset(
    skill for pair in COMPANION_PAIRS for skill in pair
)


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        raise ValueError("SKILL.md missing YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md frontmatter not closed")
    return parts[1], parts[2]


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
    try:
        fm_raw, body = _split_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    try:
        fm = yaml.safe_load(fm_raw)
    except yaml.YAMLError as exc:
        errors.append(f"invalid YAML frontmatter: {exc}")
        return errors

    if not isinstance(fm, dict):
        errors.append("frontmatter must be a YAML mapping")
        return errors

    for field in ("name", "description", "version"):
        if field not in fm:
            errors.append(f"frontmatter missing {field}")

    if fm.get("name") != name:
        errors.append(f"frontmatter name must be {name}")

    if fm.get("disable-model-invocation") is True:
        errors.append("Cursor-only disable-model-invocation must be stripped from frontmatter")

    for pattern, label in CURSOR_LEFTOVER_CHECKS:
        if re.search(pattern, text, re.IGNORECASE):
            errors.append(f"leftover Cursor-only token: {label}")

    if "github.com/cursor/plugins" not in text and "cursor/plugins/pstack" not in text:
        errors.append("Provenance must cite cursor/plugins/pstack")

    if "MIT" not in text:
        errors.append("Provenance must mention MIT license")

    if name in WORKFLOW_SKILL_NAMES:
        for section in HOUSE_SECTIONS:
            if section not in text:
                errors.append(f"missing house-adapt section: {section}")

    if name == "pstack-principles":
        if "never-block-on-the-human" not in text:
            errors.append("pstack-principles must document never-block-on-the-human")
        if "Approve" not in text or "Reject" not in text:
            errors.append("pstack-principles carve-out must mention Approve/Reject gates")
        if "prove-it-works" not in text:
            errors.append("pstack-principles must include prove-it-works")

    if name == "architect":
        if "Phase C: Agree (opt-in)" in text:
            errors.append("architect Phase C must not be opt-in skip-by-default")
        if "agents/software-architect.md" not in text:
            errors.append("architect must distinguish agents/software-architect.md plan role")
        if "Default: proceed directly to implementation" in text:
            errors.append("architect must not default-skip human checkpoint")
        if "No human checkpoint" in text:
            errors.append("architect must not say No human checkpoint")
        if "spec-gate card" not in text:
            errors.append("architect Phase C must default to reply-contract spec-gate card")

    if name == "figure-it-out":
        if "never-block-on-the-human" in text and "Article 1" not in text:
            errors.append("figure-it-out must cite Article 1 wherever never-block appears")
        if "never-block-on-the-human" in text and "literal **Approve**" not in text:
            errors.append("figure-it-out must restate literal Approve/Reject carve-out with never-block")

    if name == "interrogate":
        if "expert-pr-review" not in text:
            errors.append("interrogate must point PR reviews to expert-pr-review")

    if name == "show-me-your-work":
        if "show-me" not in text:
            errors.append("show-me-your-work must companion with show-me")

    return errors


def _do_not_use_section(text: str) -> str:
    if "**Do not use for**" not in text:
        return ""
    after = text.split("**Do not use for**", 1)[1]
    if "## Companions" in after:
        after = after.split("## Companions", 1)[0]
    else:
        match = re.search(r"\n##\s", after)
        if match:
            after = after[: match.start()]
    return after


def _companions_section(text: str) -> str:
    """Return only the Companions table — stop before Verification, ---, or next ##."""
    if "## Companions" not in text:
        return ""
    after = text.split("## Companions", 1)[1]
    end_at = len(after)
    for pattern in (r"\n\*\*Verification\*\*", r"\n---\n", r"\n##\s"):
        match = re.search(pattern, after)
        if match:
            end_at = min(end_at, match.start())
    return after[:end_at]


def _companion_sections(text: str) -> tuple[str, str]:
    return _do_not_use_section(text), _companions_section(text)


def _mentions_skill(section: str, skill_name: str) -> bool:
    """Match a skill slug without hyphen-prefix false positives (show-me vs show-me-your-work)."""
    if f"`{skill_name}`" in section:
        return True
    pattern = rf"(?<![\w-]){re.escape(skill_name)}(?![\w-])"
    return bool(re.search(pattern, section))


def _validate_companion_pair(left: str, right: str, left_text: str, right_text: str) -> list[str]:
    errors: list[str] = []
    left_dnu, left_comp = _companion_sections(left_text)
    right_dnu, right_comp = _companion_sections(right_text)

    if "## Companions" not in left_text:
        errors.append(f"{left} missing ## Companions section")
    elif not _mentions_skill(left_comp, right):
        errors.append(f"{left} Companions must point at {right}")
    if not _mentions_skill(left_dnu, right):
        errors.append(f"{left} Do not use for must cite companion {right}")

    if "## Companions" not in right_text:
        errors.append(f"{right} missing ## Companions section")
    elif not _mentions_skill(right_comp, left):
        errors.append(f"{right} Companions must point at {left}")
    if not _mentions_skill(right_dnu, left):
        errors.append(f"{right} Do not use for must cite companion {left}")

    return errors


def validate_companion_reverse_pointers() -> list[str]:
    """Ensure hub skills with pstack companions cite each other both ways."""
    errors: list[str] = []
    for left, right in COMPANION_PAIRS:
        left_md = SKILLS_DIR / left / "SKILL.md"
        right_md = SKILLS_DIR / right / "SKILL.md"
        if not left_md.is_file():
            errors.append(f"missing companion skill file: {left_md}")
            continue
        if not right_md.is_file():
            errors.append(f"missing companion skill file: {right_md}")
            continue

        left_text = left_md.read_text(encoding="utf-8")
        right_text = right_md.read_text(encoding="utf-8")
        errors.extend(_validate_companion_pair(left, right, left_text, right_text))

    return errors


def validate_companion_reverse_pointers_for(skill_name: str) -> list[str]:
    """Validate companion pairs involving skill_name (works outside PSTACK_SKILL_NAMES)."""
    errors: list[str] = []
    for left, right in COMPANION_PAIRS:
        if skill_name not in (left, right):
            continue
        left_md = SKILLS_DIR / left / "SKILL.md"
        right_md = SKILLS_DIR / right / "SKILL.md"
        if not left_md.is_file():
            errors.append(f"missing companion skill file: {left_md}")
            continue
        if not right_md.is_file():
            errors.append(f"missing companion skill file: {right_md}")
            continue
        left_text = left_md.read_text(encoding="utf-8")
        right_text = right_md.read_text(encoding="utf-8")
        errors.extend(_validate_companion_pair(left, right, left_text, right_text))
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_pstack_skill.py <skill-name>", file=sys.stderr)
        return 2
    skill_name = argv[1]
    errors: list[str] = []
    if skill_name in PSTACK_SKILL_NAMES:
        errors.extend(validate_skill(skill_name))
    elif skill_name not in COMPANION_SKILL_NAMES:
        errors.append(f"unknown pstack skill name: {skill_name}")
    if skill_name in COMPANION_SKILL_NAMES:
        errors.extend(validate_companion_reverse_pointers_for(skill_name))
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"OK: {skill_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
