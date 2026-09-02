"""TDD for scripts/validate_evidence_packet.py — the GB-1/3/4/6 Et validator.

Covers the JSON schema rules from skills/evidence-packet-protocol/SCHEMA.md: head_sha
required (GB-4 freeze), qa_status/record status restricted to verified|gap only (never
partial/blocked/"looks good"), execution_records non-empty with a restricted type
vocabulary (GB-1), the crossed-enum-pair case (a bad packet-level qa_status paired with a
bad record-level status, and vice versa), the forbidden living-PII check class, and the
GB-6 retry-then-escalate flow (escalate is exit 1 + "ESCALATE" in stdout — never exit 2,
which is reserved for scripts/run_black_box_fixture.py's own "blocked" verdict).

Written before scripts/validate_evidence_packet.py existed — first run is ModuleNotFoundError
(red), per this hub's TDD convention (see tests/test_run_black_box_fixture.py).
"""
import json
import unittest
from pathlib import Path

from scripts.validate_evidence_packet import (
    find_living_pii,
    handle_retry_then_escalate,
    handle_validate,
    validate_packet,
)

REPO_ROOT = Path(__file__).parent.parent
FIXTURES_ROOT = REPO_ROOT / "skills" / "evidence-packet-protocol" / "fixtures"


def _valid_packet(**overrides):
    packet = {
        "iteration": 2,
        "head_sha": "0123456789abcdef0123456789abcdef01234567",
        "qa_status": "gap",
        "verified_records": [
            {
                "claim_id": "player_control",
                "claim": "Player input changes avatar motion.",
                "execution_records": [
                    {
                        "type": "runtime_trace",
                        "path": "traces/core_loop.json",
                        "observation": "Avatar moved in response to input.",
                    }
                ],
                "status": "verified",
            }
        ],
        "gap_records": [
            {
                "claim_id": "result_state",
                "claim": "Completing the objective produces a visible result.",
                "execution_records": [
                    {
                        "type": "screenshot",
                        "path": "screenshots/frame_018.png",
                        "observation": "No completion banner is shown.",
                    }
                ],
                "status": "gap",
                "player_impact": "Completion is not visible to the player.",
                "recommended_update": "Add and replay a result state.",
            }
        ],
        "planner_handoff": {
            "preservation_constraints": ["Preserve verified player movement."],
            "update_targets": ["Implement a visible completion state."],
            "validation_requirements": ["Replay objective completion through the result screen."],
        },
    }
    packet.update(overrides)
    return packet


class ValidatePacketSchemaTests(unittest.TestCase):
    def test_valid_packet_has_no_violations(self):
        self.assertEqual(validate_packet(_valid_packet()), [])

    def test_missing_head_sha_is_a_violation(self):
        packet = _valid_packet()
        del packet["head_sha"]
        violations = validate_packet(packet)
        self.assertTrue(any("head_sha" in v for v in violations))

    def test_expect_head_sha_mismatch_is_flagged_by_literal_substring(self):
        packet = _valid_packet(head_sha="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        violations = validate_packet(packet, expect_head_sha="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        self.assertTrue(any("head_sha mismatch" in v for v in violations), violations)

    def test_expect_head_sha_match_has_no_mismatch_violation(self):
        sha = "cccccccccccccccccccccccccccccccccccccccc"[:40]
        packet = _valid_packet(head_sha=sha)
        violations = validate_packet(packet, expect_head_sha=sha)
        self.assertEqual(violations, [])

    def test_invalid_qa_status_partial_is_flagged_with_exact_literal(self):
        packet = _valid_packet(qa_status="partial")
        violations = validate_packet(packet)
        self.assertIn("invalid qa_status: partial", violations)

    def test_invalid_qa_status_blocked_is_flagged_with_exact_literal(self):
        packet = _valid_packet(qa_status="blocked")
        violations = validate_packet(packet)
        self.assertIn("invalid qa_status: blocked", violations)

    def test_invalid_qa_status_looks_good_is_rejected(self):
        packet = _valid_packet(qa_status="looks good")
        violations = validate_packet(packet)
        self.assertIn("invalid qa_status: looks good", violations)

    def test_invalid_record_status_blocked_is_flagged_with_exact_literal(self):
        packet = _valid_packet()
        packet["verified_records"][0]["status"] = "blocked"
        violations = validate_packet(packet)
        self.assertIn("invalid record status: blocked", violations)

    def test_invalid_record_status_partial_is_flagged_with_exact_literal(self):
        packet = _valid_packet()
        packet["gap_records"][0]["status"] = "partial"
        violations = validate_packet(packet)
        self.assertIn("invalid record status: partial", violations)

    def test_crossed_enum_pair_reports_all_four_required_tokens_across_two_packets(self):
        """task-instruction should-fix: reject BOTH crossed pairs, not only one direction."""
        partial_blocked = _valid_packet(qa_status="partial")
        partial_blocked["verified_records"][0]["status"] = "blocked"
        blocked_partial = _valid_packet(qa_status="blocked")
        blocked_partial["verified_records"][0]["status"] = "partial"

        joined = " ".join(validate_packet(partial_blocked) + validate_packet(blocked_partial))

        for token in (
            "invalid qa_status: partial",
            "invalid record status: blocked",
            "invalid qa_status: blocked",
            "invalid record status: partial",
        ):
            self.assertIn(token, joined)

    def test_empty_execution_records_is_a_gap_not_a_pass(self):
        packet = _valid_packet()
        packet["verified_records"][0]["execution_records"] = []
        violations = validate_packet(packet)
        self.assertTrue(any("execution_records" in v for v in violations), violations)

    def test_missing_execution_records_key_is_flagged(self):
        packet = _valid_packet()
        del packet["gap_records"][0]["execution_records"]
        violations = validate_packet(packet)
        self.assertTrue(any("execution_records" in v for v in violations), violations)

    def test_invalid_execution_record_type_is_rejected(self):
        packet = _valid_packet()
        packet["verified_records"][0]["execution_records"][0]["type"] = "replay"
        violations = validate_packet(packet)
        self.assertTrue(any("execution_records type" in v for v in violations), violations)

    def test_valid_execution_record_types_are_accepted(self):
        for allowed_type in ("screenshot", "runtime_trace", "fixture"):
            with self.subTest(allowed_type=allowed_type):
                packet = _valid_packet()
                packet["verified_records"][0]["execution_records"][0]["type"] = allowed_type
                self.assertEqual(validate_packet(packet), [])

    def test_gap_record_missing_player_impact_is_flagged(self):
        packet = _valid_packet()
        del packet["gap_records"][0]["player_impact"]
        violations = validate_packet(packet)
        self.assertTrue(any("player_impact" in v for v in violations), violations)

    def test_gap_record_missing_recommended_update_is_flagged(self):
        packet = _valid_packet()
        del packet["gap_records"][0]["recommended_update"]
        violations = validate_packet(packet)
        self.assertTrue(any("recommended_update" in v for v in violations), violations)

    def test_update_targets_must_be_non_empty_unless_qa_status_verified(self):
        packet = _valid_packet(qa_status="gap")
        packet["planner_handoff"]["update_targets"] = []
        violations = validate_packet(packet)
        self.assertTrue(any("update_targets" in v for v in violations), violations)

    def test_update_targets_may_be_empty_when_qa_status_verified(self):
        packet = _valid_packet(qa_status="verified", gap_records=[])
        packet["planner_handoff"]["update_targets"] = []
        self.assertEqual(validate_packet(packet), [])

    def test_preservation_constraints_required_when_iteration_not_one(self):
        packet = _valid_packet(iteration=2)
        packet["planner_handoff"]["preservation_constraints"] = []
        violations = validate_packet(packet)
        self.assertTrue(any("preservation_constraints" in v for v in violations), violations)

    def test_preservation_constraints_may_be_empty_on_iteration_one(self):
        packet = _valid_packet(iteration=1)
        packet["planner_handoff"]["preservation_constraints"] = []
        self.assertEqual(validate_packet(packet), [])


class LivingPiiTests(unittest.TestCase):
    def test_forbidden_name_lisa_is_flagged(self):
        packet = _valid_packet()
        packet["gap_records"][0]["execution_records"][0]["observation"] = "Lisa confirmed the bug."
        violations = find_living_pii(packet)
        self.assertTrue(any("living-pii" in v for v in violations), violations)

    def test_forbidden_name_tanya_is_flagged(self):
        packet = _valid_packet()
        packet["gap_records"][0]["claim"] = "Tanya said completion looks broken."
        violations = find_living_pii(packet)
        self.assertTrue(any("living-pii" in v for v in violations), violations)

    def test_clean_valid_packet_has_no_living_pii_violations(self):
        self.assertEqual(find_living_pii(_valid_packet()), [])

    def test_non_reserved_phone_number_is_flagged(self):
        packet = _valid_packet()
        packet["gap_records"][0]["player_impact"] = "Call +12025550123 for details."
        violations = find_living_pii(packet)
        self.assertTrue(any("living-pii" in v for v in violations), violations)

    def test_reserved_fictitious_phone_range_is_allowed(self):
        packet = _valid_packet()
        packet["gap_records"][0]["player_impact"] = "Fictitious contact: +15551234567."
        self.assertEqual(find_living_pii(packet), [])

    def test_validate_packet_includes_living_pii_check(self):
        packet = _valid_packet()
        packet["gap_records"][0]["claim"] = "Lisa reported this."
        violations = validate_packet(packet)
        self.assertTrue(any("living-pii" in v for v in violations), violations)


class RetryThenEscalateTests(unittest.TestCase):
    def test_two_invalid_attempts_escalates_with_exit_1(self):
        with_tmpdir_files(
            self,
            [_valid_packet(qa_status="blocked"), _valid_packet(qa_status="partial")],
            lambda paths: self._assert_escalates(paths),
        )

    def _assert_escalates(self, paths):
        exit_code = handle_retry_then_escalate(paths)
        self.assertEqual(exit_code, 1)

    def test_recovering_on_the_retry_does_not_escalate(self):
        with_tmpdir_files(
            self,
            [_valid_packet(qa_status="blocked"), _valid_packet()],
            lambda paths: self.assertEqual(handle_retry_then_escalate(paths), 0),
        )

    def test_escalate_message_is_printed_on_double_failure(self):
        import io
        from contextlib import redirect_stdout

        def run(paths):
            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = handle_retry_then_escalate(paths)
            self.assertEqual(exit_code, 1)
            self.assertIn("ESCALATE", buf.getvalue())

        with_tmpdir_files(
            self,
            [_valid_packet(qa_status="blocked"), _valid_packet(qa_status="partial")],
            run,
        )


def with_tmpdir_files(testcase, packets, fn):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        paths = []
        for index, packet in enumerate(packets):
            path = Path(tmpdir) / f"packet-{index}.json"
            path.write_text(json.dumps(packet), encoding="utf-8")
            paths.append(str(path))
        fn(paths)


class RealFixtureRedGreenProofTests(unittest.TestCase):
    """Prove et-living-pii and et-status fixtures go red on bad packets, green on valid
    (task instruction: TDD). Uses the real, committed sample packets, not synthetic-only
    data, so this is a live proof against the fixtures Kit will actually run later."""

    def test_et_living_pii_sample_is_invalid_red(self):
        path = FIXTURES_ROOT / "et-living-pii" / "E_t.sample.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        violations = validate_packet(data)
        self.assertTrue(any("living-pii" in v for v in violations), violations)

    def test_et_schema_valid_sample_is_clean_green(self):
        path = FIXTURES_ROOT / "et-schema-valid" / "E_t.sample.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(validate_packet(data), [])

    def test_et_status_crossed_pair_samples_are_both_invalid_red(self):
        dir_path = FIXTURES_ROOT / "et-status-not-verified-or-gap"
        partial_blocked = json.loads((dir_path / "E_t.partial-blocked.json").read_text(encoding="utf-8"))
        blocked_partial = json.loads((dir_path / "E_t.blocked-partial.json").read_text(encoding="utf-8"))
        joined = " ".join(validate_packet(partial_blocked) + validate_packet(blocked_partial))
        for token in (
            "invalid qa_status: partial",
            "invalid record status: blocked",
            "invalid qa_status: blocked",
            "invalid record status: partial",
        ):
            self.assertIn(token, joined)


class HandleValidateCliBehaviorTests(unittest.TestCase):
    def test_handle_validate_returns_zero_for_all_valid_files(self):
        with_tmpdir_files(self, [_valid_packet()], lambda paths: self.assertEqual(handle_validate(paths, None), 0))

    def test_handle_validate_returns_one_if_any_file_invalid(self):
        with_tmpdir_files(
            self,
            [_valid_packet(), _valid_packet(qa_status="partial")],
            lambda paths: self.assertEqual(handle_validate(paths, None), 1),
        )


if __name__ == "__main__":
    unittest.main()
