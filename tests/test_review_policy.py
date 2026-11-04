"""Tests for scripts/review_policy.py (GMA-552)."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import review_policy as rp
from scripts.advisory_pr_body_format import check_body

POLICY = rp.load_policy()
MODEL = "grok-4.7 high"


def _v(sha: str, round_no: int, decision: str = "REVISE", cap: int = 2) -> rp.Verdict:
    return rp.Verdict(decision, sha, round_no, cap, MODEL)


def _run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = rp.main(list(argv))
    return code, out.getvalue().strip(), err.getvalue().strip()


class PolicyFileTests(unittest.TestCase):
    def test_every_action_has_one_known_approver(self) -> None:
        approvers = set(POLICY["approvers"])
        self.assertEqual(approvers, {"self", "morgan", "tom"})
        for action, who in POLICY["actions"].items():
            self.assertIn(who, approvers, action)
        self.assertIn(POLICY["default_approver"], approvers)
        self.assertIn(POLICY["review"]["cap_plus_one_approver"], approvers)

    def test_v1_actions_are_listed(self) -> None:
        expected = {
            "self": {"clone-in-dev", "worktree-in-dev", "toolchain-in-dev", "rm-container",
                     "merge-greenfield-poc-no-ci"},
            "morgan": {"merge-approved-pr", "system-install-pinned", "review-cap-plus-one-small",
                       "merge-docs-only-final-revise-no-must-fix", "clear-defaults"},
            "tom": {"prod-migration", "aws", "outside-send", "budget", "strategy"},
        }
        got: dict[str, set[str]] = {}
        for action, who in POLICY["actions"].items():
            got.setdefault(who, set()).add(action)
        self.assertEqual(got, expected)


class CapTests(unittest.TestCase):
    def test_caps_per_tier(self) -> None:
        self.assertEqual([rp.cap_for(POLICY, t) for t in ("T0", "T1", "T2", "T3")], [2, 2, 4, 4])

    def test_small_label_lowers_a_large_tier(self) -> None:
        self.assertEqual(rp.cap_for(POLICY, "T3", ["small"]), 2)
        self.assertEqual(rp.cap_for(POLICY, "T2", ["docs"]), 4)

    def test_is_small(self) -> None:
        self.assertTrue(rp.is_small(POLICY, "T0"))
        self.assertTrue(rp.is_small(POLICY, "T2", ["small"]))
        self.assertFalse(rp.is_small(POLICY, "T1"))

    def test_unknown_tier_raises(self) -> None:
        with self.assertRaises(ValueError):
            rp.cap_for(POLICY, "T9")


class VerdictTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        line = rp.format_verdict("APPROVE", "cd704544", 1, 2, MODEL)
        self.assertEqual(line, "Verdict: APPROVE @cd704544 (round 1/2, grok-4.7 high)")
        self.assertEqual(rp.parse_verdict(line + "\n\nbody"), rp.Verdict("APPROVE", "cd704544", 1, 2, MODEL))

    def test_bad_lines_do_not_parse(self) -> None:
        for bad in ("", "Verdict: APPROVE (round 1/2, grok-4.7 high)",
                    "Verdict: LGTM @abcdef1 (round 1/2, grok-4.7 high)",
                    "Verdict: APPROVE @abc (round 1/2, grok-4.7 high)",
                    "Verdict: APPROVE @abcdef1 round 1/2"):
            self.assertIsNone(rp.parse_verdict(bad), bad)

    def test_format_rejects_unknown_decision(self) -> None:
        with self.assertRaises(ValueError):
            rp.format_verdict("LGTM", "abcdef1", 1, 2, MODEL)

    def test_lint(self) -> None:
        self.assertEqual(rp.lint_verdict(POLICY, "Verdict: REVISE @abcdef1 (round 3/2, grok-4.7 high)"), [])
        self.assertEqual(rp.lint_verdict(POLICY, "Verdict: REVISE @abcdef1 (round 4/2, grok-4.7 high)"),
                         ["round 4 is outside 1..3"])
        self.assertEqual(len(rp.lint_verdict(POLICY, "Verdict: REVISE @abcdef1 (round 0/2, grok-4.7 high)")), 1)
        self.assertEqual(len(rp.lint_verdict(POLICY, "Verdict: REVISE @abcdef1 (round 1/3, grok-4.7 high)")), 1)
        self.assertEqual(len(rp.lint_verdict(POLICY, "Verdict: REVISE @abcdef1 (round 1/2, other)")), 1)
        self.assertEqual(len(rp.lint_verdict(POLICY, "nope")), 1)


class NextRoundTests(unittest.TestCase):
    def test_repeat_verdicts_on_one_sha_count_once(self) -> None:
        history = [_v("1111111", 1), _v("1111111abc", 1)]
        self.assertEqual(rp.next_round(POLICY, history, "2222222", "T1"), ("ok", 2))

    def test_first_round_ok(self) -> None:
        self.assertEqual(rp.next_round(POLICY, [], "aaaaaaa", "T1"), ("ok", 1))

    def test_unchanged_sha_blocks_even_with_short_sha(self) -> None:
        history = [_v("abcdef1", 1)]
        self.assertEqual(rp.next_round(POLICY, history, "abcdef1234", "T1"), ("unchanged_sha", 2))

    def test_second_round_ok_then_cap(self) -> None:
        self.assertEqual(rp.next_round(POLICY, [_v("1111111", 1)], "2222222", "T1"), ("ok", 2))
        history = [_v("1111111", 1), _v("2222222", 2)]
        self.assertEqual(rp.next_round(POLICY, history, "3333333", "T1"), ("cap_reached", 3))

    def test_cap_plus_one_only_for_small(self) -> None:
        history = [_v("1111111", 1), _v("2222222", 2)]
        self.assertEqual(rp.next_round(POLICY, history, "3333333", "T0"), ("cap_plus_one_needs_morgan", 3))
        self.assertEqual(rp.next_round(POLICY, history, "3333333", "T1", ["small"]),
                         ("cap_plus_one_needs_morgan", 3))
        history.append(_v("3333333", 3))
        self.assertEqual(rp.next_round(POLICY, history, "4444444", "T0"), ("cap_reached", 4))

    def test_t3_has_four_rounds_and_no_plus_one(self) -> None:
        history = [_v(f"{i}" * 7, i, cap=4) for i in range(1, 4)]
        self.assertEqual(rp.next_round(POLICY, history, "9999999", "T3"), ("ok", 4))
        history.append(_v("4444444", 4, cap=4))
        self.assertEqual(rp.next_round(POLICY, history, "9999999", "T3"), ("cap_reached", 5))


class ApproverTests(unittest.TestCase):
    def test_known_and_unknown_actions(self) -> None:
        self.assertEqual(rp.approver_for(POLICY, "rm-container"), "self")
        self.assertEqual(rp.approver_for(POLICY, "system-install-pinned"), "morgan")
        self.assertEqual(rp.approver_for(POLICY, "aws"), "tom")
        self.assertEqual(rp.approver_for(POLICY, "outside-send"), "tom")
        self.assertEqual(rp.approver_for(POLICY, "something-new"), "tom")

    def test_merge_approver(self) -> None:
        m = rp.merge_approver
        self.assertEqual(m(POLICY, "APPROVE", 0, False, True, False), "self")
        self.assertEqual(m(POLICY, "APPROVE", 0, False, False, False), "morgan")
        self.assertEqual(m(POLICY, "APPROVE", 1, False, False, True), "blocked")
        self.assertEqual(m(POLICY, "REVISE", 0, True, False, True), "morgan")
        self.assertEqual(m(POLICY, "REVISE", 0, True, False, False), "blocked")
        self.assertEqual(m(POLICY, "REVISE", 1, True, False, True), "blocked")
        self.assertEqual(m(POLICY, "REVISE", 0, False, False, True), "blocked")
        self.assertEqual(m(POLICY, "REVISE", 0, False, True, True), "blocked")

    def test_merge_approver_reads_the_json(self) -> None:
        policy = json.loads(json.dumps(POLICY))
        del policy["actions"]["merge-approved-pr"]
        self.assertEqual(rp.merge_approver(policy, "APPROVE", 0, False, False, False), "tom")


class CliTests(unittest.TestCase):
    def test_cap_and_approver(self) -> None:
        self.assertEqual(_run("cap", "--tier", "T2"), (0, "4", ""))
        self.assertEqual(_run("cap", "--tier", "T2", "--label", "small"), (0, "2", ""))
        self.assertEqual(_run("approver", "clear-defaults"), (0, "morgan", ""))
        code, _, err = _run("cap", "--tier", "T7")
        self.assertEqual(code, 2)
        self.assertIn("unknown tier", err)

    def test_format_and_lint(self) -> None:
        code, out, _ = _run("format-verdict", "APPROVE", "abcdef1", "1", "--tier", "T3")
        self.assertEqual((code, out), (0, "Verdict: APPROVE @abcdef1 (round 1/4, grok-4.7 high)"))
        self.assertEqual(_run("lint-verdict", out)[0], 0)
        code, _, err = _run("lint-verdict", "bad")
        self.assertEqual(code, 1)
        self.assertIn("first line", err)

    def test_check_round_reads_saved_pr_json(self) -> None:
        data = {
            "headRefOid": "bbbbbbbbbb",
            "labels": [{"name": "small"}],
            "comments": [
                {"body": "unrelated"},
                {"body": "Verdict: REVISE @aaaaaaa (round 1/2, grok-4.7 high)"},
                {"body": "Verdict: REVISE @ccccccc (round 2/2, grok-4.7 high)"},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pr.json"
            path.write_text(json.dumps(data))
            code, out, _ = _run("check-round", "--tier", "T2", "--pr-json", str(path))
            self.assertEqual((code, out), (3, "cap_plus_one_needs_morgan round=3 cap=2"))
            self.assertEqual(_run("check-round", "--tier", "T2", "--morgan-ok", "--pr-json", str(path))[:2],
                             (0, "ok round=3 cap=2"))
            self.assertEqual(_run("check-round", "--tier", "T1", "--morgan-ok", "--pr-json", str(path))[:2],
                             (0, "ok round=3 cap=2"))
            data["comments"] = data["comments"][:2]
            path.write_text(json.dumps(data))
            self.assertEqual(_run("check-round", "--tier", "T1", "--pr-json", str(path))[:2],
                             (0, "ok round=2 cap=2"))
            data["headRefOid"] = "aaaaaaa"
            path.write_text(json.dumps(data))
            self.assertEqual(_run("check-round", "--tier", "T1", "--pr-json", str(path))[:2],
                             (3, "unchanged_sha round=2 cap=2"))


class CliArgTests(unittest.TestCase):
    def _exits_2(self, *argv: str) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            rp.main(list(argv))
        self.assertEqual(ctx.exception.code, 2, argv)

    def test_required_arguments(self) -> None:
        self._exits_2()
        self._exits_2("cap")
        self._exits_2("format-verdict", "APPROVE", "abcdef1", "1")
        self._exits_2("check-round", "--pr", "1")
        self._exits_2("check-round", "--tier", "T1")

    def test_check_round_pr_reads_gh(self) -> None:
        from unittest import mock

        data = {"headRefOid": "bbbbbbb", "labels": [], "comments": []}
        done = mock.Mock(stdout=json.dumps(data))
        with mock.patch.object(rp.subprocess, "run", return_value=done) as run:
            self.assertEqual(_run("check-round", "--tier", "T1", "--pr", "7")[:2], (0, "ok round=1 cap=2"))
        run.assert_called_once_with(
            ["gh", "pr", "view", "7", "--json", "headRefOid,comments,labels"],
            check=True, capture_output=True, text=True,
        )


class AdvisoryTierTests(unittest.TestCase):
    def test_unreadable_policy_warns_instead_of_raising(self) -> None:
        from unittest import mock

        base = "Tier: T9\nModels: x\nLinear: N/A\nSummary: x\nGates: x\nPoteto\n"
        with mock.patch.object(rp, "load_policy", side_effect=OSError("gone")):
            warnings = check_body(base)
        self.assertIn("Review policy unreadable, tier not checked: gone", warnings)
        self.assertFalse(any("not a policy tier" in w for w in warnings))

    def test_unknown_tier_warns_and_known_tier_does_not(self) -> None:
        base = "Models: x\nLinear: N/A\nSummary: x\nGates: x\nPoteto\n"
        self.assertIn("Tier: T9 is not a policy tier ['T0', 'T1', 'T2', 'T3'] "
                      "(docs/shared/policy/review-autonomy.json)", check_body("Tier: T9\n" + base))
        self.assertFalse(any("policy tier" in w for w in check_body("Tier: T2\n" + base)))


if __name__ == "__main__":
    unittest.main()
