#!/usr/bin/env python3
"""One-shot port helper: adapt upstream Cursor pstack skills into hub layout."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import yaml

UPSTREAM = Path("/tmp/pstack-upstream/pstack/skills")
REPO_SKILLS = Path(__file__).resolve().parent.parent / "skills"

PROVENANCE = """## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT). Native multi-harness hub playbook — not a marketplace plugin copy. Cursor-only harness names stripped per `skills/subagent-routing/SKILL.md`.

*Last updated: 2026-09-15 | Hub version: 0.11.0*
"""

SKILLS_TO_PORT = [
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
]

REPLACEMENTS: list[tuple[str, str]] = [
    (r"disable-model-invocation:\s*true\n", ""),
    (
        r"`~/.cursor/rules/pstack-models\.mdc`",
        "project model-routing rules (or `skills/subagent-routing/SKILL.md` defaults)",
    ),
    (
        r"from `~/.cursor/rules/pstack-models\.mdc` when present",
        "from project model-routing rules when present (else `skills/subagent-routing/SKILL.md`)",
    ),
    (
        r"Use the `interrogate reviewers` list from `~/.cursor/rules/pstack-models\.mdc` when present",
        "Use the project's configured interrogate reviewer models when present (else defaults below)",
    ),
    (
        r"Use `arena runners` from `~/.cursor/rules/pstack-models\.mdc` when present",
        "Use project-configured arena runner models when present",
    ),
    (
        r"Pick the worker model from `swarm workers` in `~/.cursor/rules/pstack-models\.mdc` when present",
        "Pick the worker model from project swarm-worker config when present",
    ),
    (
        r"choose one model from the `arena cross-judge pool` in `~/.cursor/rules/pstack-models\.mdc` when present",
        "choose one model from the project arena cross-judge pool when present",
    ),
    (r"claude-fable-5-1-thinking-max", "Sonnet-tier model per `skills/subagent-routing/SKILL.md`"),
    (r"gpt-5\.6-sol-max", "Sonnet-tier model per `skills/subagent-routing/SKILL.md`"),
    (r"grok-4\.6-fast-xhigh", "Haiku-tier model per `skills/subagent-routing/SKILL.md`"),
    (r"claude-opus-5-thinking-xhigh", "Sonnet-tier model per `skills/subagent-routing/SKILL.md`"),
    (r"`subagent_type`: `generalPurpose`", "`subagent_type` per `skills/subagent-routing/SKILL.md`"),
    (r"using the Task tool", "using the harness subagent tool (`Task()` in Claude Code / Cursor)"),
    (
        r"Launch all reviewers in a single message using the Task tool",
        "Launch all reviewers in a single message using parallel subagent spawns",
    ),
    (r"`readonly`: `true`", "read-only subagent mode when the harness supports it"),
    (r"`readonly`: `false`", "writable subagent mode when MCP or spot-check access is required"),
    (r"`run_in_background`: `true`", "background subagent execution when the harness supports it"),
    (
        r'Spawn all N workers in one message with `subagent_type: generalPurpose`, `environment: "cloud"`, `run_in_background: true`',
        "Spawn all N workers in one message with parallel subagent spawns, background execution when the harness supports it",
    ),
    (r'`environment`: `"local"` only when the worker needs access to something on the user\'s computer', "local/host access only when the worker needs something on the user's machine"),
    (r"cloud_base_branch", "base branch override for cloud subagents"),
    (r"AskQuestion", "`reply-contract` clarify card"),
    (r"Cursor's built-in `create-skill`", "hub skill authoring (`skills/docs-protocol/SKILL.md` + `skills/close-out/SKILL.md` Step 8)"),
    (r"via `create-skill`", "via hub skill authoring"),
    (r"follow `create-skill`", "follow `docs-protocol` frontmatter rules"),
    (r"\.cursor/skills/verify-<app>/", "`skills/verify-<app>/`"),
    (r"\.cursor/skills/<handle>", "`skills/<handle>`"),
    (r"~/.cursor/skills/", "harness personal-skill overlay (e.g. `~/.grok/skills/`)"),
    (r"Never glob `~/.cursor/projects/\*/`", "Do not glob across unrelated workspace transcript roots"),
    (r"Don't glob across `~/.cursor/projects/\*/`", "Do not glob across unrelated workspace transcript roots"),
    (r"\*\*poteto-mode\*\* skill", "`pstack-principles` skill"),
    (r"poteto-mode", "pstack-principles"),
    (r"principle-([a-z0-9-]+)", r"`pstack-principles` (\1)"),
    (r"\*\*([a-z-]+)\*\* principle skill", r"`pstack-principles` (\1)"),
    (r"the \*\*([a-z-]+)\*\* principle skill", r"`pstack-principles` (\1)"),
    (r"per the \*\*([a-z-]+)\*\* principle skill", r"per `pstack-principles` (\1)"),
    (r"../principle-[a-z0-9-]+/SKILL\.md", "`pstack-principles`"),
    (r"List the available MCPs from the Cursor environment", "Discover MCP namespaces via `GetDynamicTools`"),
    (r"inspect the `mcps/` directory Cursor exposes", "inspect available MCP namespaces"),
    (r"agent-transcripts/", "harness transcript storage for the active workspace"),
    (
        r"Default: proceed directly to implementation with the synthesized design\. No human checkpoint\.",
        "Default: present the synthesized design via `reply-contract`'s spec-gate card before fill-in.",
    ),
    (r"## Phase C: Agree \(opt-in\)", "## Phase C: Agree"),
    (r"/architect", "architect"),
    (r"/arena", "arena"),
    (r"/swarm", "swarm"),
    (r"/figure-it-out", "figure-it-out"),
    (r"/show-me-your-work", "show-me-your-work"),
    (r"/create-verification-skill", "create-verification-skill"),
    (r"/maintain-verification-skill", "maintain-verification-skill"),
    (r"/technical-writing", "technical-writing"),
    (r"/reflect", "reflect"),
    (r"/automate-me", "automate-me"),
]


def adapt_text(text: str) -> str:
    for pattern, repl in REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    return text


def parse_frontmatter(skill_md: str) -> tuple[str, str, str]:
    if not skill_md.startswith("---"):
        raise ValueError("missing frontmatter")
    parts = skill_md.split("---", 2)
    fm = parts[1]
    body = parts[2].lstrip("\n")
    data = yaml.safe_load(fm)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    name = data.get("name")
    description = data.get("description")
    if not name or not description:
        raise ValueError("missing name or description")
    return str(name).strip(), str(description).strip(), body


def format_frontmatter(name: str, description: str) -> str:
    payload = {"name": name, "description": description, "version": "1.0.0"}
    dumped = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{dumped}\n---"


def build_hub_skill(name: str, description: str, body: str) -> str:
    body = adapt_text(body).rstrip()
    fm = format_frontmatter(name, description)
    return f"""{fm}

# {name}

{description}

---

{body}

{PROVENANCE}
"""


def copy_references(src: Path, dest: Path) -> None:
    ref_src = src / "references"
    if not ref_src.is_dir():
        return
    ref_dest = dest / "references"
    ref_dest.mkdir(parents=True, exist_ok=True)
    for path in ref_src.rglob("*"):
        if path.is_file():
            rel = path.relative_to(ref_src)
            target = ref_dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix in {".md", ".tsv", ".sh"}:
                target.write_text(adapt_text(path.read_text(encoding="utf-8")), encoding="utf-8")
            else:
                shutil.copy2(path, target)


def port_skill(name: str) -> None:
    src = UPSTREAM / name
    dest = REPO_SKILLS / name
    if not src.is_dir():
        raise FileNotFoundError(src)
    raw = (src / "SKILL.md").read_text(encoding="utf-8")
    skill_name, description, body = parse_frontmatter(raw)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "SKILL.md").write_text(build_hub_skill(skill_name, description, body), encoding="utf-8")
    copy_references(src, dest)
    scripts_src = src / "scripts"
    if scripts_src.is_dir():
        scripts_dest = dest / "scripts"
        scripts_dest.mkdir(parents=True, exist_ok=True)
        for path in scripts_src.rglob("*"):
            if path.is_file():
                rel = path.relative_to(scripts_src)
                target = scripts_dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if path.suffix in {".sh", ".md"}:
                    target.write_text(adapt_text(path.read_text(encoding="utf-8")), encoding="utf-8")
                else:
                    shutil.copy2(path, target)


def main() -> int:
    for name in SKILLS_TO_PORT:
        port_skill(name)
        print(f"ported {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
