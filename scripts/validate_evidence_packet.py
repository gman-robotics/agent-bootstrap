#!/usr/bin/env python3
"""Validator for evidence-packet-protocol's E_t.json (GB-1/3/4/6, H-1..5 schema rules).

Implements the schema in skills/evidence-packet-protocol/SCHEMA.md: `head_sha` required
at the packet root (GB-4 freeze binding); `qa_status` (packet root) and every record's
`status` restricted to `verified | gap` only -- never `partial`, `blocked`, or "looks
good" (GB-1/GB-6); every claim's `execution_records` non-empty with a restricted type
vocabulary of `screenshot | runtime_trace | fixture` (GB-1 -- "empty is a gap, not a
pass"); `planner_handoff.update_targets`/`preservation_constraints` structural
non-emptiness rules (GB-3); and a forbidden living-PII check across every string value
in the packet (no bare "Lisa"/"Tanya", no phone number outside the reserved
`+1555XXXXXXX` fictitious range).

Usage:
    python3 scripts/validate_evidence_packet.py <E_t.json> [<E_t.json> ...]
    python3 scripts/validate_evidence_packet.py --expect-head-sha <sha> <E_t.json>
    python3 scripts/validate_evidence_packet.py --retry-then-escalate <attempt-1.json> <attempt-2.json>

Exit codes:
    0 = every given packet is valid (and, when --expect-head-sha is given, its head_sha
        matches).
    1 = at least one packet is invalid, OR --retry-then-escalate exhausted its one retry
        on two invalid attempts (prints "ESCALATE" per GB-6's schema-or-retry-once rule).

This script never exits 2. Exit code 2 is reserved for
scripts/run_black_box_fixture.py's own "blocked" verdict (an environment problem, e.g. a
missing executable) -- it is never emitted by this validator itself, so a GB-6
escalation is never confused with an environment block. See SCHEMA.md "Exit codes".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STATUS_VALUES = frozenset({"verified", "gap"})
EXECUTION_RECORD_TYPES = frozenset({"screenshot", "runtime_trace", "fixture"})

# Forbidden living-PII check class (SCHEMA.md "Forbidden living PII"): a bare first name
# used as if referring to a real teammate, or a phone number outside the reserved
# fictitious range. "Lisa"/"Tanya" are named explicitly by the task as the forbidden
# fixture pair -- never permitted content, only ever used to prove this check fires.
FORBIDDEN_NAME_RE = re.compile(r"\b(Lisa|Tanya)\b", re.IGNORECASE)
PHONE_CANDIDATE_RE = re.compile(r"\+1\d{10}\b")
RESERVED_FICTITIOUS_PHONE_RE = re.compile(r"^\+1555\d{7}$")


def iter_strings(value, path="root"):
    """Yield (path, string) for every string leaf in a nested dict/list structure."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, sub_value in value.items():
            yield from iter_strings(sub_value, f"{path}.{key}")
    elif isinstance(value, list):
        for index, sub_value in enumerate(value):
            yield from iter_strings(sub_value, f"{path}[{index}]")


def find_living_pii(data) -> list[str]:
    """Return one 'living-pii: ...' message per forbidden name or non-fictitious phone
    number found anywhere in the packet's string values."""
    violations = []
    for path, text in iter_strings(data):
        name_match = FORBIDDEN_NAME_RE.search(text)
        if name_match:
            violations.append(f"living-pii: forbidden name {name_match.group(0)!r} found in {path}")
        for phone in PHONE_CANDIDATE_RE.findall(text):
            if not RESERVED_FICTITIOUS_PHONE_RE.match(phone):
                violations.append(
                    f"living-pii: phone number {phone!r} in {path} is not in the reserved "
                    "+1555XXXXXXX fictitious range"
                )
    return violations


def _validate_execution_record(execution_record, claim_id) -> list[str]:
    violations = []
    if not isinstance(execution_record, dict):
        return [f"record {claim_id!r} has an execution_record that is not an object"]
    record_type = execution_record.get("type")
    if record_type not in EXECUTION_RECORD_TYPES:
        violations.append(f"record {claim_id!r} has invalid execution_records type: {record_type}")
    if not execution_record.get("path"):
        violations.append(f"record {claim_id!r} execution_record missing required field: path")
    if not execution_record.get("observation"):
        violations.append(f"record {claim_id!r} execution_record missing required field: observation")
    return violations


def _validate_record(record, *, is_gap_record: bool) -> list[str]:
    violations = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]

    claim_id = record.get("claim_id")
    if not claim_id:
        violations.append("record missing required field: claim_id")
    if not record.get("claim"):
        violations.append(f"record {claim_id!r} missing required field: claim")

    execution_records = record.get("execution_records")
    if not execution_records:
        violations.append(
            f"record {claim_id!r} has missing or empty execution_records "
            "(empty is a gap, not a pass -- GB-1)"
        )
    else:
        for execution_record in execution_records:
            violations.extend(_validate_execution_record(execution_record, claim_id))

    status = record.get("status")
    if status not in STATUS_VALUES:
        violations.append(f"invalid record status: {status}")

    if is_gap_record:
        if not record.get("player_impact"):
            violations.append(f"gap record {claim_id!r} missing required field: player_impact")
        if not record.get("recommended_update"):
            violations.append(f"gap record {claim_id!r} missing required field: recommended_update")

    return violations


def validate_packet(data, expect_head_sha: str | None = None) -> list[str]:
    """Return one message per schema violation; an empty list means the packet is valid.

    Mirrors the JSON schema in skills/evidence-packet-protocol/SCHEMA.md exactly --
    including the crossed-enum-pair case, where a bad packet-level qa_status and a bad
    record-level status can both be present in the same packet and must both be
    reported (task-instruction should-fix: reject BOTH crossed pairs, not only one).
    """
    if not isinstance(data, dict):
        return ["packet root must be a JSON object"]

    violations: list[str] = []

    iteration = data.get("iteration")
    if not isinstance(iteration, int) or isinstance(iteration, bool) or iteration < 1:
        violations.append(f"invalid iteration: {iteration!r} (must be an integer >= 1)")

    head_sha = data.get("head_sha")
    if not head_sha:
        violations.append("missing required field: head_sha (GB-4 freeze binding)")
    elif expect_head_sha is not None and head_sha != expect_head_sha:
        violations.append(f"head_sha mismatch: expected {expect_head_sha}, got {head_sha}")

    qa_status = data.get("qa_status")
    if qa_status not in STATUS_VALUES:
        violations.append(f"invalid qa_status: {qa_status}")

    verified_records = data.get("verified_records")
    if not isinstance(verified_records, list):
        violations.append("verified_records must be an array")
        verified_records = []
    gap_records = data.get("gap_records")
    if not isinstance(gap_records, list):
        violations.append("gap_records must be an array")
        gap_records = []

    for record in verified_records:
        violations.extend(_validate_record(record, is_gap_record=False))
    for record in gap_records:
        violations.extend(_validate_record(record, is_gap_record=True))

    handoff = data.get("planner_handoff")
    if not isinstance(handoff, dict):
        violations.append("missing required object: planner_handoff")
    else:
        preservation_constraints = handoff.get("preservation_constraints")
        update_targets = handoff.get("update_targets")
        validation_requirements = handoff.get("validation_requirements")

        if not isinstance(preservation_constraints, list):
            violations.append("planner_handoff.preservation_constraints must be an array")
        elif not preservation_constraints and iteration != 1:
            violations.append(
                "planner_handoff.preservation_constraints must be non-empty when iteration != 1"
            )

        if not isinstance(update_targets, list):
            violations.append("planner_handoff.update_targets must be an array")
        elif not update_targets and qa_status != "verified":
            violations.append(
                "planner_handoff.update_targets must be non-empty unless qa_status is verified (GB-3)"
            )

        if not isinstance(validation_requirements, list):
            violations.append("planner_handoff.validation_requirements must be an array")

    violations.extend(find_living_pii(data))
    return violations


def load_packet(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def handle_validate(paths: list[str], expect_head_sha: str | None) -> int:
    """Validate every given file independently; print every violation for every file.

    Returns 1 if any file is invalid or unparsable, 0 if every file is valid.
    """
    exit_code = 0
    for path in paths:
        try:
            data = load_packet(path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"invalid: {path}: could not be read as JSON: {exc}")
            exit_code = 1
            continue
        violations = validate_packet(data, expect_head_sha=expect_head_sha)
        if violations:
            exit_code = 1
            print(f"invalid packet: {path}")
            for violation in violations:
                print(f"  {violation}")
        else:
            print(f"valid: {path}")
    return exit_code


def handle_retry_then_escalate(paths: list[str]) -> int:
    """GB-6: schema-or-retry once, then escalate -- never a silent T=70 reinvoke.

    Validates the first attempt; if invalid, validates the second (retry) attempt. If
    the retry is also invalid, prints ESCALATE and returns 1 (never 2 -- see module
    docstring). Recovering on the retry returns 0 with no escalation.
    """
    if len(paths) != 2:
        print(
            "error: --retry-then-escalate requires exactly two files: "
            "<first-attempt> <retry-attempt>"
        )
        return 1

    labels = ("attempt 1", "attempt 2 (retry)")
    for label, path in zip(labels, paths):
        try:
            data = load_packet(path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"{label} could not be read as JSON: {path}: {exc}")
            continue
        violations = validate_packet(data)
        if not violations:
            print(f"valid: {path} ({label}) -- schema-or-retry recovered, no escalation needed")
            return 0
        print(f"{label} invalid: {path}")
        for violation in violations:
            print(f"  {violation}")

    print(
        "ESCALATE: schema-or-retry-once exhausted on both attempts; "
        "escalate to CoS/human review (GB-6) -- never a silent T=70 reinvoke"
    )
    return 1


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("files", nargs="+", help="one or more E_t.json packet files")
    parser.add_argument(
        "--expect-head-sha",
        help="fail with 'head_sha mismatch' if the packet's head_sha does not equal this value (GB-4)",
    )
    parser.add_argument(
        "--retry-then-escalate",
        action="store_true",
        help=(
            "treat the two given files as (initial attempt, retry attempt); "
            "print ESCALATE and exit 1 if both are invalid (GB-6)"
        ),
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.retry_then_escalate:
        if args.expect_head_sha:
            print("error: --expect-head-sha and --retry-then-escalate are mutually exclusive")
            return 1
        return handle_retry_then_escalate(args.files)
    return handle_validate(args.files, expect_head_sha=args.expect_head_sha)


if __name__ == "__main__":
    sys.exit(main())
