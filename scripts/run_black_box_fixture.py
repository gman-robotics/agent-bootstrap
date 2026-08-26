#!/usr/bin/env python3
"""Runner for black-box-agent-qa fixtures.

Implements `skills/black-box-agent-qa/SKILL.md` Steps 1-5 mechanically: load a fixture's
`case.json` (the named input fixture + expected output), actually run the command it names,
compare the real output against the expectation, and write a captured run record — never a
pass produced by reading a diff or a skill's Markdown. See
`skills/black-box-agent-qa/SCHEMA.md` for the `case.json` contract.

Usage:
    python3 scripts/run_black_box_fixture.py \\
        --fixture skills/black-box-agent-qa/fixtures/<case-name> \\
        --skill <skill-name-this-run-is-evidence-for> \\
        --out skills/<skill-name>/black-box-run.json

Exit code 0 = pass, 1 = fail, 2 = blocked (environment prevented the run; this is an
escalation per Step 4, never a pass).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_case(fixture_dir: Path) -> dict:
    case_path = fixture_dir / "case.json"
    return json.loads(case_path.read_text(encoding="utf-8"))


def run_case(case: dict, repo_root: Path) -> dict:
    """Actually run the fixture's command and compare against its expected output.

    Returns a dict with at least a "verdict" key: "pass", "fail", or "blocked".
    "blocked" means the environment prevented the run (missing executable, timeout) -
    this is an escalation, never a pass, per Step 4 of skills/black-box-agent-qa/SKILL.md.
    """
    command = case["input"]["command"]
    cwd = repo_root / case["input"].get("cwd", ".")

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=case["input"].get("timeout_seconds", 120),
        )
    except FileNotFoundError as exc:
        return {"verdict": "blocked", "reason": f"command not found: {exc}"}
    except subprocess.TimeoutExpired:
        return {"verdict": "blocked", "reason": "command timed out"}

    expected = case.get("expected", {})
    mismatches: list[str] = []

    if "exit_code" in expected and result.returncode != expected["exit_code"]:
        mismatches.append(f"exit_code: expected {expected['exit_code']}, got {result.returncode}")

    for substr in expected.get("stdout_contains", []):
        if substr not in result.stdout:
            mismatches.append(f"stdout missing expected substring: {substr!r}")

    for substr in expected.get("stderr_contains", []):
        if substr not in result.stderr:
            mismatches.append(f"stderr missing expected substring: {substr!r}")

    return {
        "verdict": "pass" if not mismatches else "fail",
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-4000:],
        "stderr_tail": result.stderr[-4000:],
        "mismatches": mismatches,
    }


def skill_sha256(skill_dir: Path) -> str | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None
    return hashlib.sha256(skill_md.read_bytes()).hexdigest()


def write_run_record(
    out_path: Path,
    *,
    case: dict,
    skill_dir: Path,
    outcome: dict,
    fixture_dir: Path,
) -> dict:
    record = {
        "fixture": str(fixture_dir),
        "case_name": case.get("name"),
        "description": case.get("description"),
        "skill_sha256": skill_sha256(skill_dir),
        "input": case.get("input"),
        "expected": case.get("expected"),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "captured_by": "scripts/run_black_box_fixture.py",
        **outcome,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="path to a fixtures/<case-name> directory")
    parser.add_argument("--skill", required=True, help="skill name this run is evidence for")
    parser.add_argument(
        "--out",
        help="path to write the run record JSON (defaults to skills/<skill>/black-box-run.json)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture_dir = Path(args.fixture)
    skill_dir = REPO_ROOT / "skills" / args.skill
    out_path = Path(args.out) if args.out else skill_dir / "black-box-run.json"

    case = load_case(fixture_dir)
    outcome = run_case(case, repo_root=REPO_ROOT)
    record = write_run_record(out_path, case=case, skill_dir=skill_dir, outcome=outcome, fixture_dir=fixture_dir)

    print(json.dumps({"verdict": record["verdict"], "out": str(out_path)}, indent=2))

    if record["verdict"] == "blocked":
        return 2
    return 0 if record["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
