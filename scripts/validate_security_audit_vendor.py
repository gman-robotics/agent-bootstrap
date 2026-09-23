#!/usr/bin/env python3
"""Mechanical structure check for the vendored `security-audit` skill (GMA-56).

Standalone validator — modeled on `scripts/validate_pstack_skill.py`'s structure-check
style, but `security-audit` is a vendor-of-a-real-upstream skill (Cloudflare
`security-audit-skill`, MIT), not a pstack port, so it is not added to that script's
`PSTACK_SKILL_NAMES`. Bidirectional companion pointers for `security-audit` are still
checked via `scripts/validate_pstack_skill.py`'s `COMPANION_PAIRS` mechanism (that script
already supports companion names outside `PSTACK_SKILL_NAMES` — see
`validate_companion_reverse_pointers_for`).

Usage:
    python3 scripts/validate_security_audit_vendor.py security-audit
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

SKILL_NAME = "security-audit"

UPSTREAM_PIN_SHA = "c1c8a8c1471069fb0e188eeaff69b8e8db6564a8"
UPSTREAM_URL = "https://github.com/cloudflare/security-audit-skill"

# Upstream's own frontmatter `description:` auto-matches these bare phrases (verified
# against the vendored companion at references/cloudflare/SKILL.md). The house hub-entry
# description must never contain them, or it would collide with expert-pr-review /
# blast-radius triggers exactly as Blocker 1 describes.
UPSTREAM_BROAD_MATCH_PHRASES: tuple[str, ...] = (
    "security questions",
    "focused reviews",
)

# Opt-in language: the house wrapper must state it is not invoked automatically by any
# always-on pipeline. Checked as a set of required substrings rather than one exact
# sentence so the wrapper's prose can be edited without breaking this check on wording
# alone, while still requiring every named pipeline to be mentioned.
REQUIRED_OPT_IN_MENTIONS: tuple[str, ...] = (
    "opt-in",
    "plan-code-review-workflow",
    "SecurityReviewer",
)

# Blocker 5: the four Universal execution-safety controls, named by house paraphrase
# (not required to match upstream's wording verbatim, but each concept must appear).
REQUIRED_CONTROL_MENTIONS: tuple[str, ...] = (
    "no external network",
    "allowlisted environment",
    "scratch",
    "resource limits",
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
    if name != SKILL_NAME:
        errors.append(f"unknown security-audit vendor skill name: {name}")
        return errors

    skill_dir = SKILLS_DIR / name
    skill_md = skill_dir / "SKILL.md"
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

    description = str(fm.get("description", ""))
    for phrase in UPSTREAM_BROAD_MATCH_PHRASES:
        if phrase in description:
            errors.append(
                f"frontmatter description must not contain upstream broad-match phrase "
                f"{phrase!r} (Blocker 1: would collide with expert-pr-review/blast-radius)"
            )

    # Blocker 1/3/4 structure — reuse the house section shape by convention.
    for section in ("**Purpose**", "**Do not use for**", "## Companions", "**Verification**"):
        if section not in text:
            errors.append(f"missing house-adapt section: {section}")

    for mention in REQUIRED_OPT_IN_MENTIONS:
        if mention not in text:
            errors.append(f"missing required opt-in mention: {mention!r}")

    lowered_text = text.lower()
    for mention in REQUIRED_CONTROL_MENTIONS:
        if mention.lower() not in lowered_text:
            errors.append(f"missing required Universal execution safety control mention: {mention!r}")

    if "needs_validation" not in text:
        errors.append("missing required needs_validation fallback verdict language")

    # Blocker 1: attribution trail.
    notice_md = skill_dir / "references" / "cloudflare" / "NOTICE.md"
    if not notice_md.is_file():
        errors.append(f"missing {notice_md}")
    else:
        notice_text = notice_md.read_text(encoding="utf-8")
        if UPSTREAM_PIN_SHA not in notice_text:
            errors.append(f"NOTICE.md missing pinned SHA {UPSTREAM_PIN_SHA}")
        if UPSTREAM_URL not in notice_text:
            errors.append(f"NOTICE.md missing upstream URL {UPSTREAM_URL}")

    license_file = skill_dir / "references" / "cloudflare" / "LICENSE"
    if not license_file.is_file():
        errors.append(f"missing {license_file}")
    else:
        if "MIT" not in license_file.read_text(encoding="utf-8"):
            errors.append("references/cloudflare/LICENSE does not mention MIT")

    # Blocker 1: upstream's own SKILL.md must never be treated as the hub entry — it is
    # vendored, unmodified, as a companion reference only.
    upstream_skill_md = skill_dir / "references" / "cloudflare" / "SKILL.md"
    if not upstream_skill_md.is_file():
        errors.append(f"missing vendored companion {upstream_skill_md}")
    else:
        upstream_fm_raw, _ = _split_frontmatter(
            upstream_skill_md.read_text(encoding="utf-8")
        )
        upstream_fm = yaml.safe_load(upstream_fm_raw)
        if isinstance(upstream_fm, dict) and "version" in upstream_fm:
            errors.append(
                "vendored companion references/cloudflare/SKILL.md unexpectedly has a "
                "version: field — confirm this is still upstream's real file, not "
                "accidentally overwritten with the house hub entry"
            )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_security_audit_vendor.py <skill-name>", file=sys.stderr)
        return 2
    skill_name = argv[1]
    errors = validate_skill(skill_name)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"OK: {skill_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
