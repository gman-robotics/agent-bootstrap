#!/usr/bin/env python3
"""Export agent-bootstrap skills into Codex global-skill folders."""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillConfig:
    description: str
    short_description: str
    trigger_summary: str
    quick_start: tuple[str, ...]


SKILL_CONFIGS: dict[str, SkillConfig] = {
    "plan-code-review-workflow": SkillConfig(
        description=(
            "Use when work is non-trivial and should follow the team workflow of "
            "planning with the user, implementing cleanly, critically reviewing, "
            "and iterating before finalizing."
        ),
        short_description="Plan, code, review workflow",
        trigger_summary=(
            "Triggers on requests to follow the main team workflow, co-create a "
            "plan for substantial work, or run a full plan-to-review delivery loop."
        ),
        quick_start=(
            "Read `references/source.md` before acting; it is the authoritative workflow.",
            "Run the phases in order: PLAN, CODE, REVIEW, ITERATE, FINALIZE.",
            "Preserve all user-approval gates before posting reviews, committing, or pushing.",
        ),
    ),
    "expert-pr-review": SkillConfig(
        description=(
            "Use for GitHub pull request reviews that need a deep, critical pass "
            "covering context gathering, build and test verification, security review, "
            "and a user-approved final review decision."
        ),
        short_description="Critical PR review workflow",
        trigger_summary=(
            "Triggers on requests to review a PR, inspect a diff, or provide an "
            "approve/request-changes recommendation."
        ),
        quick_start=(
            "Read `references/source.md` fully before starting the review.",
            "Treat this as review-only work: do not edit the PR branch.",
            "Present findings and wait for explicit user approval before posting APPROVE or REQUEST_CHANGES.",
        ),
    ),
    "write-tests": SkillConfig(
        description=(
            "Use when implementing features, fixing bugs, or refactoring code that "
            "requires strict red-green-refactor TDD with the project's existing test framework."
        ),
        short_description="TDD execution playbook",
        trigger_summary=(
            "Triggers on requests to add behavior, fix a bug, improve coverage, or "
            "retrofit tests around existing code."
        ),
        quick_start=(
            "Read `references/source.md` before changing production code.",
            "Write one failing test for the next behavior, then make it pass with the minimum change.",
            "Run the focused test and then the relevant full suite after each meaningful step.",
        ),
    ),
    "debug-investigation": SkillConfig(
        description=(
            "Use for bug reports, flaky tests, or unexplained regressions that need "
            "systematic reproduction, isolation, a failing test, and a verified fix."
        ),
        short_description="Systematic debugging workflow",
        trigger_summary=(
            "Triggers on requests to diagnose a bug, investigate flaky behavior, or "
            "root-cause an incident before fixing it."
        ),
        quick_start=(
            "Read `references/source.md` before attempting a fix.",
            "Do not fix anything until you can reproduce it reliably.",
            "Write a failing test that captures the reproduction before changing production code.",
        ),
    ),
    "performance-profiling": SkillConfig(
        description=(
            "Use for slow requests, latency spikes, backlog growth, heavy renders, or "
            "other performance issues that need measurement-first profiling and before/after validation."
        ),
        short_description="Performance bottleneck workflow",
        trigger_summary=(
            "Triggers on requests about slowness, timeouts, latency, throughput, or optimization."
        ),
        quick_start=(
            "Read `references/source.md` before changing code.",
            "Define the exact slow path and record a baseline measurement first.",
            "Change one thing at a time and re-measure using the same method.",
        ),
    ),
    "feature-flag-lifecycle": SkillConfig(
        description=(
            "Use when adding, rolling out, auditing, or removing feature flags so "
            "flags stay default-off, tested on both paths, and removed on schedule."
        ),
        short_description="Feature flag lifecycle",
        trigger_summary=(
            "Triggers on requests to create a flag, stage a rollout, or clean up a retired flag."
        ),
        quick_start=(
            "Read `references/source.md` before implementing the flag.",
            "Create default-off flags with an explicit cleanup date and tracking entry.",
            "Test both flag-off and flag-on behavior, then remove the flag promptly after rollout.",
        ),
    ),
    "cherry-pick-to-release-branch": SkillConfig(
        description=(
            "Use when backporting a merged pull request onto an existing release branch "
            "and incrementing the release-candidate version suffix safely."
        ),
        short_description="Release-branch cherry-pick",
        trigger_summary=(
            "Triggers on requests to hotfix or backport a merged PR onto a release branch."
        ),
        quick_start=(
            "Read `references/source.md` before touching git state.",
            "Fetch the release branch and the PR head, identify the exact PR commits, then cherry-pick them oldest first.",
            "Update all configured version files consistently and verify the branch state before pushing.",
        ),
    ),
    "memory-bank-protocol": SkillConfig(
        description=(
            "Use whenever a project needs the six-file memory-bank structure, when "
            "starting a session, switching projects, or updating persistent project state."
        ),
        short_description="Memory-bank protocol",
        trigger_summary=(
            "Triggers on project initialization, session startup, project switching, "
            "or requests to update long-lived project context."
        ),
        quick_start=(
            "Read `references/source.md` before initializing or updating a memory bank.",
            "Every session: read hot files (activeContext + progress); foundation files conditionally.",
            "Apply evidence and compaction rules at task end; use mem0 only when configured.",
        ),
    ),
    "docs-protocol": SkillConfig(
        description=(
            "Use when creating or updating project or shared technical documentation "
            "so docs stay separate from operational memory-bank state."
        ),
        short_description="Technical docs protocol",
        trigger_summary=(
            "Triggers on requests to create or update API docs, data models, pipeline docs, or ADRs."
        ),
        quick_start=(
            "Read `references/source.md` before editing technical docs.",
            "Choose the correct target under `docs/shared/` or `docs/projects/<name>/`.",
            "Keep `docs/` for technical reference and `memory-bank/` for operational state.",
        ),
    ),
    "delegation-patterns": SkillConfig(
        description=(
            "Use when spawning subagents in Claude Code or Grok: two-tier model selection, "
            "parallel dispatch patterns, and mandatory worktree isolation for editing agents."
        ),
        short_description="Subagent delegation patterns",
        trigger_summary=(
            "Triggers when setting up multi-agent delegation, choosing agent tiers, or "
            "running parallel analysis or isolated parallel edits."
        ),
        quick_start=(
            "Read `references/source.md` for the three canonical patterns.",
            "Use worktree isolation for ANY editing agent when the checkout may be shared.",
            "Emit independent agent calls in a single message so they run in parallel.",
        ),
    ),
    "subagent-routing": SkillConfig(
        description=(
            "Use before any task with independent subtasks to decide what to delegate "
            "and which model tier each subagent should use."
        ),
        short_description="Subagent and model routing",
        trigger_summary=(
            "Triggers before tasks with parallelizable or isolatable subtasks, or when "
            "selecting a model for a spawned agent."
        ),
        quick_start=(
            "Read `references/source.md` for the decomposition checklist and model table.",
            "Use the cheap tier for retrieval tasks and the full tier for code and judgment.",
            "Editing agents must run in worktree isolation when the checkout may be shared.",
        ),
    ),
    "triage-review-feedback": SkillConfig(
        description=(
            "Use when a PR we authored receives review feedback from humans, AI reviewers, "
            "or scanners: verify every claim against the code, then fix or dismiss with evidence."
        ),
        short_description="Respond to PR review feedback",
        trigger_summary=(
            "Triggers when our PR gets a review, inline comments, or scanner findings, or "
            "the user asks to address review feedback on a PR."
        ),
        quick_start=(
            "Read `references/source.md` before acting.",
            "Inventory all claims first; verify each at the cited code location before classifying.",
            "Fix TDD-first, QA-pass before posting, reply to every thread, then re-request review.",
            "Tag every FIX NEW or REPEAT; REPEAT closes only with a mechanical check (lint/diagnostic/test/CI rule), never an instance fix or a comment — worked example: fixtures/repeat-exporter-dropped-references/.",
        ),
    ),
    "pr-shepherd": SkillConfig(
        description=(
            "Use to keep open PRs moving: classify blockers, front-load all reviewer-dependent "
            "asks in the first hour, and fill reviewer-wait time with reviewer-free work."
        ),
        short_description="PR pipeline shepherding",
        trigger_summary=(
            "Triggers at the start of the working day, after opening or un-drafting a PR, or "
            "when asked what is blocked or for PR status."
        ),
        quick_start=(
            "Read `references/source.md` before acting.",
            "Enumerate open PRs across manifest repos and classify each blocker.",
            "Batch every review request and ping in the first hour, then pick disjoint fill work.",
        ),
    ),
    "end-of-day-review": SkillConfig(
        description=(
            "Use at the end of each working day to verify outcomes against evidence, capture "
            "learnings, compact the memory bank, and write tomorrow's plan."
        ),
        short_description="Daily wrap-up and planning",
        trigger_summary=(
            "Triggers on end-of-day wrap-up requests, EOD, plan-tomorrow requests, or before "
            "an extended break."
        ),
        quick_start=(
            "Read `references/source.md` before acting.",
            "Verify the day's outcomes from live git/GitHub state, never session memory.",
            "Write tomorrow's plan with reviewer-dependent asks queued for the first hour.",
        ),
    ),
    "multi-harness-coordination": SkillConfig(
        description=(
            "Use when coordinating work across two or more agent harnesses with separated "
            "planner/reviewer and implementer roles and an adversarial review loop."
        ),
        short_description="Cross-harness coordination",
        trigger_summary=(
            "Triggers when routing tasks between harnesses, running the multi-harness workflow, "
            "or establishing planner vs implementer roles across agents."
        ),
        quick_start=(
            "Read `references/source.md` before acting.",
            "Step A: full-context plan, no production code. Step B: TDD on isolated branch.",
            "Steps C/D: cumulative git diff review, max 3 iterations, then Step E PR if approved.",
            "Optional: lead a handoff with the four-field envelope stanza (type/to/priority/task).",
        ),
    ),
    "task-loop-7-phase": SkillConfig(
        description=(
            "Use when a task should follow the strict 7-Phase Algorithm: OBSERVE, THINK, "
            "PLAN, BUILD, EXECUTE, VERIFY, LEARN, with TaskLoopState updates in mem0 "
            "and durable lessons captured at the end."
        ),
        short_description="Seven-phase task loop",
        trigger_summary=(
            "Triggers when the user invokes the 7-Phase Algorithm, TaskLoopState, or "
            "an observe-think-plan-build-execute-verify-learn workflow."
        ),
        quick_start=(
            "Read `references/source.md` before starting the loop.",
            "Run phases strictly in order and announce each phase transition.",
            "Update TaskLoopState in mem0 after each phase, then write a lesson in LEARN.",
        ),
    ),
    "agent-orchestration-roles": SkillConfig(
        description=(
            "Use to orient a new harness or coordinate tasks when multiple agent "
            "harnesses (e.g. a planner/reviewer harness and an implementer harness) "
            "collaborate across the projects in this hub's manifest.yaml."
        ),
        short_description="Multi-harness role division",
        trigger_summary=(
            "Triggers when setting up or clarifying the division of labor between "
            "a planning/reviewing harness and an implementing harness."
        ),
        quick_start=(
            "Read `references/source.md` for the full role split and workflow loop.",
            "Resolve the coordination root directory from manifest.yaml, not a hardcoded path.",
            "Keep the planner harness out of bulk implementation when an implementer harness is available.",
        ),
    ),
    "adversarial-coordination-workflow": SkillConfig(
        description=(
            "Use when an Orchestrator (human or automated) needs to run a planner "
            "harness and an implementer harness as adversarial peers through a "
            "plan → implement → adversarial-review → PR loop."
        ),
        short_description="Adversarial plan/implement/review loop",
        trigger_summary=(
            "Triggers when starting multi-agent implementation work that requires "
            "a critical, adversarial review pass before any PR is created."
        ),
        quick_start=(
            "Read `references/source.md` for the full Step A–E loop.",
            "Step A: full-context plan, no production code. Step B: TDD on isolated branch.",
            "Steps C/D: cumulative `git diff main...HEAD` review, max 3 iterations, then Step E PR if approved.",
            "Optional: lead a handoff with the four-field envelope stanza (type/to/priority/task).",
        ),
    ),
    "close-out": SkillConfig(
        description=(
            "Use at the end of any significant task or conversation thread to "
            "verify memory-bank/shared-memory continuity (Phase 1) and turn session "
            "friction into concrete skill/process improvement proposals (Phase 2)."
        ),
        short_description="Task close-out & retrospective",
        trigger_summary=(
            "Triggers on 'close this out', 'wrap this up', or after completing a "
            "multi-step implementation session — task-scoped, not day-scoped."
        ),
        quick_start=(
            "Read `references/source.md` for the full two-phase protocol.",
            "Phase 1: audit activeContext.md/progress.md and sync shared memory if configured.",
            "Phase 2: scan for friction/skill gaps and propose specific, filed improvements.",
            "Step 8 proposals for a skill need a named case.json; Step 9 requires scripts/run_black_box_fixture.py to capture a pass and scripts/check_skill_live.py <name> to exit 0 before the skill is live — approval to write it is not a ship, and re-editing invalidates the record.",
        ),
    ),
    "reply-contract": SkillConfig(
        description=(
            "Use when giving status, a your-turn / smoke checklist, or any longer "
            "explanation to a human who may have just switched projects. Write as "
            "if they are new: one show-me visual, gloss jargon, leftover vs bug, "
            "who is waiting."
        ),
        short_description="Status and your-turn as if they just walked in",
        trigger_summary=(
            "Triggers on status after another agent finished, smoke / tap-through, "
            "or anything the human must do or decide."
        ),
        quick_start=(
            "Read `references/source.md` before writing the reply.",
            "Load `skills/show-me/SKILL.md` for the one visual (tree, stack, or diff); never reimplement its recipes here. No mermaid/HTML on Photon unless asked.",
            "Gloss only the jargon you used. Say leftover vs bug and who is waiting.",
            "Use the spec-gate card for a binary Approve/Reject on a held artifact; use the clarify card for a plain question, never both.",
        ),
    ),
    "codebase-simplification-audit": SkillConfig(
        description=(
            "Use when the user wants a whole-repo read-only audit for simpler data "
            "structures, state representation, control flow, algorithms, or ownership. "
            "Do not edit, test, implement, commit, or push until they accept a recommendation."
        ),
        short_description="Read-only whole-repo representation audit",
        trigger_summary=(
            "Triggers on codebase simplification audit, messy state/ownership reviews, "
            "or a paste of the Aaron Francis audit-your-codebase gist."
        ),
        quick_start=(
            "Read `references/source.md` before acting; it is the authoritative workflow.",
            "Hard rule: no file edits, tests, implement skills, commits, or pushes until the user accepts a rec.",
            "Inventory every subsystem, bound workers to \u22642 material recs or skip, verify, audit the audit, then stop.",
            "Ownership rows may use the Architectural Review Phases checklist names (no CRAP/mutation/DRY tooling).",
        ),
    ),
    "grill-with-docs": SkillConfig(
        description=(
            "Use when aligning on a plan or design before code: grill the user in "
            "rounds, keep CONTEXT.md as a glossary, and offer ADRs only for "
            "hard-to-reverse trade-offs. Do not implement until they confirm."
        ),
        short_description="Align on domain language before code",
        trigger_summary=(
            "Triggers on grill this, grill-with-docs, align on the domain, or "
            "build CONTEXT.md before a change."
        ),
        quick_start=(
            "Read `references/source.md` before acting; it is the authoritative workflow.",
            "Hard rule: no implement skills, feature branches, or PRs until the user confirms shared understanding.",
            "Ask the whole decision frontier each round; look up facts yourself; write glossary-only CONTEXT.md as terms resolve.",
            "Final confirm uses reply-contract's spec-gate card, not chat prose; a single blocking fact-question uses its clarify card.",
        ),
    ),
    "show-me": SkillConfig(
        description=(
            "Use before code ('show the shape' / 'show-me'), or when reply-contract "
            "loads it for a status/your-turn visual. Owns the recipes: call tree, "
            "file/screen tree, stack, diff of those shapes, optional mermaid. One "
            "primary visual per reply."
        ),
        short_description="Recipes for the one status visual",
        trigger_summary=(
            "Triggers on 'show the shape' / 'show-me' before code, or is auto-loaded "
            "by reply-contract for a status/your-turn reply that needs a visual."
        ),
        quick_start=(
            "Read `references/source.md` for the recipe behind each visual; do not build it from memory.",
            "Pick exactly one recipe (call tree, file/screen tree, stack, or diff of those shapes) per reply.",
            "Default to fenced text; mermaid or HTML only if the user explicitly asked, and never open it with a shell/browser command.",
        ),
    ),
    "black-box-agent-qa": SkillConfig(
        description=(
            "Use before treating any agent, harness, verb, or skill change as verified: "
            "name an input fixture and expected output, then actually run it. Reading the "
            "PR or skill Markdown is not a pass; mocking the system under test is not the "
            "only proof; an environment-blocked run escalates, it never passes."
        ),
        short_description="Black-box run-it verification for agent/harness/skill changes",
        trigger_summary=(
            "Triggers before marking a change to an agent persona, harness wiring, a "
            "verb/command, or a skill file as tested, passing, or ready to ship."
        ),
        quick_start=(
            "Read `references/source.md` before acting; it is the authoritative workflow.",
            "Write fixtures/<case>/case.json (schema: SCHEMA.md), then run scripts/run_black_box_fixture.py to actually execute it against the real system under test.",
            "A diff read, a description, or a mock-only suite is not a pass; check scripts/check_skill_live.py <name> exits 0 before treating a skill as live.",
            "Environment-blocked runs escalate (verdict blocked), they do not pass; never authorize auto-merge or a silent harness/agent-state refine from the run.",
        ),
    ),
    "evidence-packet-protocol": SkillConfig(
        description=(
            "Use when an implementer/QA-Tester role needs to hand a planner "
            "claim-bound, checkable evidence of what actually works (and what still "
            "has a gap) instead of a prose status update: the E_t.json evidence packet."
        ),
        short_description="Claim-bound evidence packets (E_t.json)",
        trigger_summary=(
            "Triggers after an implementer/QA-Tester turn needing checkable evidence, "
            "or before a planner starts the next iteration and must read the prior packet."
        ),
        quick_start=(
            "Read `references/source.md` before acting; it is the authoritative schema and rules.",
            "head_sha is required (GB-4 freeze); qa_status and every record's status are verified|gap only, never partial/blocked/looks good.",
            "execution_records must be non-empty and typed screenshot|runtime_trace|fixture; empty is a gap, not a pass (GB-1).",
            "Schema failure gets one retry, then ESCALATE at exit 1 (never exit 2, which is the runner's own environment-blocked verdict) -- GB-6.",
        ),
    ),
    "preservation-gate": SkillConfig(
        description=(
            "Use when writing a development-document markdown (Dt) from iteration 2 "
            "onward: every such document needs an exact '## Preservation Gate' heading "
            "listing the previous iteration's verified claims the Developer must not regress."
        ),
        short_description="The Preservation Gate plan-document field",
        trigger_summary=(
            "Triggers when writing or reviewing a Dt plan/development document for "
            "iteration 2 or later of a warm-started, evidence-driven workflow."
        ),
        quick_start=(
            "Read `references/source.md` before acting; it is the authoritative field definition.",
            "Use the exact literal heading `## Preservation Gate` with at least one bullet from the prior iteration's verified claims.",
            "Distinct from REPEAT: Preservation Gate is positive and never closes; REPEAT is negative and closes only via a mechanical check.",
        ),
    ),
}


def collect_preserved_files(skill_dir: Path) -> dict[Path, bytes]:
    """Return every file under skill_dir the exporter does not itself generate.

    `SKILL.md` and `references/source.md` are fully regenerated on every export; anything
    else (a hand-added reference file, for example) must survive a `force=True` re-export
    byte-for-byte. See the REPEAT-lock fixture at
    `skills/triage-review-feedback/fixtures/repeat-exporter-dropped-references/`.
    """
    if not skill_dir.is_dir():
        return {}
    generated = {Path("SKILL.md"), Path("references") / "source.md"}
    preserved: dict[Path, bytes] = {}
    for path in skill_dir.rglob("*"):
        if path.is_file():
            rel = path.relative_to(skill_dir)
            if rel not in generated:
                preserved[rel] = path.read_bytes()
    return preserved


def load_source_skills(source_dir: Path) -> dict[str, str]:
    skills: dict[str, str] = {}
    for path in sorted(source_dir.glob("*/SKILL.md")):
        if path.parent.name == "agent-bootstrap":
            continue
        skills[path.parent.name] = path.read_text(encoding="utf-8")
    return skills


def strip_trailing_footer(text: str) -> str:
    lines = text.rstrip().splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and lines[-1].lower().startswith("last updated:"):
        lines.pop()
    return "\n".join(lines).rstrip() + "\n"


def build_skill_markdown(skill_name: str, config: SkillConfig) -> str:
    quick_start = "\n".join(f"{index}. {step}" for index, step in enumerate(config.quick_start, start=1))
    return f"""---
name: {skill_name}
description: {config.description}
metadata:
  short-description: {config.short_description}
---

# {skill_name}

{config.trigger_summary}

## Quick Start

{quick_start}

## Compatibility Notes

- The detailed workflow lives in `references/source.md`; treat that file as the authoritative procedure.
- Translate harness-specific tool names from the source into Grok (or Codex) equivalents while preserving the workflow intent.
- Keep all safety rules from the source, especially approval gates, review-only constraints, and absolute-path requirements.
"""


def export_skills(source_dir: Path, output_dir: Path, force: bool = False) -> list[Path]:
    source_skills = load_source_skills(source_dir)
    missing_configs = sorted(set(source_skills) - set(SKILL_CONFIGS))
    if missing_configs:
        raise ValueError(f"Missing exporter configs for skills: {', '.join(missing_configs)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    exported_paths: list[Path] = []

    for skill_name, source_text in source_skills.items():
        config = SKILL_CONFIGS[skill_name]
        skill_dir = output_dir / skill_name
        preserved_files: dict[Path, bytes] = {}
        if skill_dir.exists():
            if not force:
                raise FileExistsError(f"{skill_dir} already exists; rerun with --force")
            preserved_files = collect_preserved_files(skill_dir)
            shutil.rmtree(skill_dir)
        (skill_dir / "references").mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            build_skill_markdown(skill_name, config),
            encoding="utf-8",
        )
        (skill_dir / "references" / "source.md").write_text(
            strip_trailing_footer(source_text),
            encoding="utf-8",
        )
        for rel_path, content in preserved_files.items():
            target = skill_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        exported_paths.append(skill_dir)

    return exported_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path(__file__).parent.parent / "skills",
        help="Directory containing the source skill markdown files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where Codex skill folders should be written.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated skill folders in the output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    exported_paths = export_skills(args.source_dir, args.output_dir, force=args.force)
    for path in exported_paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
