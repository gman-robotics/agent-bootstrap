#!/usr/bin/env python3
"""End-to-end black-box fixture for skills/wayfinder: chart a map with the local tracker.

Exit 0 = contract met, 1 = contract violated, 2 = blocked (no claude CLI / model call failed).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SKILL = REPO / "skills" / "wayfinder" / "SKILL.md"
LOCAL_TRACKER = REPO / "skills" / "wayfinder" / "references" / "local-tracker.md"
MODEL = os.environ.get("WAYFINDER_FIXTURE_MODEL", "sonnet")
TYPES = {"research", "prototype", "grilling", "task"}
SECTIONS = ["## Destination", "## Notes", "## Decisions so far", "## Not yet specified", "## Out of scope"]

IDEA = """# Loose idea: move scheduled jobs off the EC2 crontab

Our ~40 scheduled jobs run from one EC2 box's crontab. It's a single point of failure,
nobody knows which jobs are still needed, and secrets live in the crontab env. We want
to move them to a managed scheduler, but we don't know the target yet.
"""

HUMAN_ANSWERS = """## The human's side of the grilling (pre-supplied for this non-interactive fixture run)

This is a black-box fixture. There is no live human. The answers below ARE the human's answers:
use them wherever the skill tells you to grill or confirm with the human. Do not ask questions,
and do not invoke any other skill or subagent. Where the skill says to fire research subagents,
don't. Leave the research tickets open and note in the map's Notes that research is pending.

- Tracker: CONFIRMED. Use the local-markdown tracker. The effort slug is `cron-migration`.
- Destination: a decided migration plan. The target scheduler is chosen, every job is classified
  keep/retire/merge, and the secrets approach is picked, so an engineer can start migrating.
- Known facts: the jobs are Python and bash; the box is in us-west-2; the team already uses ECS
  and Terraform.
- Open questions the human raised: EventBridge Scheduler + ECS tasks vs Step Functions vs
  keeping cron in a container; which jobs are dead (no owner knows); where secrets should come
  from (SSM vs Secrets Manager); how to verify parity before cutover. Picking the scheduler
  depends on knowing each job's runtime and duration profile.
- Out of scope: rewriting any job's business logic; moving off AWS.
"""


def build_prompt() -> str:
    return (
        "Run the following skill exactly as written, in **Chart the map** mode, on the loose idea in "
        "`idea.md` in the current directory. Write only the map and ticket files the skill and tracker "
        "reference prescribe.\n\n"
        "<skill name=\"wayfinder\">\n" + SKILL.read_text() + "\n</skill>\n\n"
        "<tracker-reference>\n" + LOCAL_TRACKER.read_text() + "\n</tracker-reference>\n\n"
        + HUMAN_ANSWERS
    )


def section_body(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    rest = text[start + len(heading):]
    nxt = re.search(r"^## ", rest, flags=re.M)
    body = rest[: nxt.start()] if nxt else rest
    return re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()


def check(work: Path) -> list[str]:
    errs: list[str] = []
    maps = sorted(work.glob(".scratch/*/map.md"))
    if len(maps) != 1:
        return [f"expected exactly one .scratch/<effort>/map.md, found {[str(m.relative_to(work)) for m in maps]}"]
    map_md = maps[0]
    text = map_md.read_text()
    for s in SECTIONS:
        if s not in text:
            errs.append(f"map.md missing section {s!r}")
    if not section_body(text, "## Destination"):
        errs.append("map.md Destination is empty")
    if re.search(r"^\s*[-*] ", section_body(text, "## Decisions so far"), flags=re.M):
        errs.append("map.md Decisions so far has entries; charting must hand-resolve nothing")

    issues_dir = map_md.parent / "issues"
    tickets = sorted(issues_dir.glob("*.md")) if issues_dir.is_dir() else []
    if len(tickets) < 3:
        errs.append(f"expected >= 3 ticket files in {issues_dir.relative_to(work)}, found {len(tickets)}")
    numbers = []
    for t in tickets:
        m = re.match(r"^(\d{2})-[a-z0-9-]+\.md$", t.name)
        if not m:
            errs.append(f"ticket filename not NN-<slug>.md: {t.name}")
            continue
        numbers.append(m.group(1))
        body = t.read_text()
        tm = re.search(r"^\**Type:?\**:?\s*`?([a-z]+)`?", body, flags=re.M | re.I)
        if not tm or tm.group(1).lower() not in TYPES:
            errs.append(f"{t.name}: missing or invalid Type: line (want one of {sorted(TYPES)})")
        if "## Question" not in body:
            errs.append(f"{t.name}: missing '## Question'")
        if re.search(r"^\**Status:?\**:?\s*`?resolved", body, flags=re.M | re.I):
            errs.append(f"{t.name}: resolved during charting")
    if numbers and numbers[0] != "01":
        errs.append(f"tickets must be numbered from 01, first is {numbers[0]}")
    blocked = []
    for t in tickets:
        for line in re.findall(r"^\**Blocked by:?\**:?\s*(.+)$", t.read_text(), flags=re.M | re.I):
            blocked += re.findall(r"\d{1,2}", line)
    if not blocked:
        errs.append("no 'Blocked by:' edge in any ticket (the idea has a stated dependency)")
    for b in blocked:
        if b.zfill(2) not in numbers:
            errs.append(f"'Blocked by: {b}' points at a ticket that doesn't exist")

    stray = [
        str(p.relative_to(work)) for p in work.rglob("*")
        if p.is_file() and ".git" not in p.parts and ".scratch" not in p.parts and p.name != "idea.md"
    ]
    if stray:
        errs.append(f"wrote files outside .scratch/ (plan, don't do): {stray}")
    return errs


def main() -> int:
    if not shutil.which("claude"):
        print("BLOCKED: claude CLI not on PATH", file=sys.stderr)
        return 2
    work = Path(tempfile.mkdtemp(prefix="wayfinder-fixture-"))
    try:
        (work / "idea.md").write_text(IDEA)
        subprocess.run(["git", "init", "-q"], cwd=work, check=True)
        cmd = [
            "claude", "-p", build_prompt(),
            "--model", MODEL,
            "--permission-mode", "acceptEdits",
            "--allowedTools", "Read", "Write", "Edit", "Glob", "Grep",
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--no-session-persistence",
        ]
        run = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=840)
        if run.returncode != 0:
            print(f"BLOCKED: claude exited {run.returncode}: {run.stderr[-800:]}", file=sys.stderr)
            return 2
        errs = check(work)
        for p in sorted(work.glob(".scratch/**/*.md")):
            print(f"--- {p.relative_to(work)}")
            print(p.read_text()[:1500])
        if errs:
            print("FAIL: wayfinder chart-local-map")
            for e in errs:
                print(f"  - {e}")
            return 1
        print("OK: wayfinder chart-local-map")
        return 0
    finally:
        if os.environ.get("WAYFINDER_FIXTURE_KEEP") != "1":
            shutil.rmtree(work, ignore_errors=True)
        else:
            print(f"kept: {work}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
