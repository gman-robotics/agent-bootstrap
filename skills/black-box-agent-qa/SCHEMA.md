# black-box-agent-qa — fixture I/O contract (minimum schema)

This is the runnable contract behind `SKILL.md` Steps 1-5: every fixture is a directory that
`scripts/run_black_box_fixture.py` can execute and score without any human reading a diff or a
skill's Markdown.

## Directory shape

```
skills/black-box-agent-qa/fixtures/<case-name>/
  case.json      # required — the I/O contract, schema below
  README.md      # optional — provenance/history for the fixture, human-readable
```

## `case.json` minimum schema

```json
{
  "name": "string, should match the directory name",
  "description": "one sentence: what agent/harness/verb/skill change this exercises",
  "input": {
    "command": ["argv0", "argv1", "..."],
    "cwd": "repo-root-relative path, defaults to '.' (the repo root)",
    "timeout_seconds": 120
  },
  "expected": {
    "exit_code": 0,
    "stdout_contains": ["optional list of literal substrings"],
    "stderr_contains": ["optional list of literal substrings"]
  }
}
```

- `input.command` **is** the literal input fixture from Step 1 — an argv list run as a real
  subprocess against the real system under test. Not a description of a command; the actual
  argv.
- `expected` **is** the literal, checkable expected output from Step 1 — an exit code and,
  optionally, substrings the real run's stdout/stderr must contain. Nothing here is inferred
  or assumed; every field is checked against the actual captured output.
- `cwd` and `timeout_seconds` are optional; only `command` is required under `input`.
- Extra fields are ignored, so a fixture may carry additional documentation fields (e.g.
  `description`) without breaking the runner.

## Invocation (the "way to invoke it")

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/black-box-agent-qa/fixtures/<case-name> \
  --skill <skill-name-this-run-is-evidence-for> \
  --out skills/<skill-name>/black-box-run.json
```

This actually runs `input.command`, compares the real output to `expected`, and writes a run
record to `--out` (defaults to `skills/<skill-name>/black-box-run.json`). The run record
includes a `skill_sha256` of the target skill's current `SKILL.md` — `scripts/check_skill_live.py`
uses that hash to detect a silent refine (the skill edited after the pass was captured) and
will refuse to call the skill live until a fresh pass matches the current file.

## Exit codes

| Code | Verdict | Meaning |
|---|---|---|
| `0` | `pass` | The real run matched every `expected` field. |
| `1` | `fail` | The real run executed but did not match `expected`. |
| `2` | `blocked` | The environment prevented the run (missing executable, timeout). Per Step 4, this is an escalation and is recorded as `"verdict": "blocked"` — it is never scored as a pass. |

## Worked examples in this repo

`input.command` is an arbitrary argv — it is not specific to Python's `unittest`. Two of the
three examples below happen to run a `unittest` module because that is the most direct
evidence for the mechanism each is proving; the third deliberately runs a plain CLI script
with no test runner involved, so the contract's generality is not only asserted, it is shown.

- `fixtures/repeat-lock-mechanical-check/` — runs the REPEAT-lock mechanical check itself
  (`tests/test_export_codex_skills.py::test_force_reexport_preserves_hand_added_reference_files`)
  and expects `OK` on a clean run — evidence that `triage-review-feedback`'s REPEAT mechanism
  and this skill's own runner both actually work end to end.
- `fixtures/close-out-live-gate-check/` — runs `tests/test_check_skill_live.py` and expects
  `OK` — evidence that `close-out`'s Step 9 live-flip gate (`scripts/check_skill_live.py`)
  actually works end to end.
- `fixtures/check-skill-live-cli/` — runs `python3 scripts/check_skill_live.py black-box-agent-qa`
  directly (no `unittest`, no test runner) and expects `live-eligible` in stdout — evidence
  that the runner's contract is a generic subprocess argv/exit-code/stdout check, not a
  `unittest`-specific wrapper.

Every skill's `black-box-run.json` in this repo (e.g. `skills/close-out/black-box-run.json`)
was produced by an actual invocation of one of these fixtures, not written by hand.
