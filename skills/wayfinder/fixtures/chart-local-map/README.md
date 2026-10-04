# chart-local-map

The real end-to-end fixture for `wayfinder`. It replaces reading the Markdown as evidence (see `skills/black-box-agent-qa/SKILL.md`).

`run_chart.py` does four things:

1. It creates a throwaway git repo containing a loose idea (`idea.md`).
2. It runs `claude -p` headless in that repo. The prompt is the verbatim content of `skills/wayfinder/SKILL.md` and `references/local-tracker.md`, plus pre-supplied human answers. Wayfinder's grilling is HITL, so a non-interactive run must carry the human's side, and the fixture says so explicitly.
3. It checks what the run wrote, against the skill's contract for charting:
   - `.scratch/<effort>/map.md` has Destination, Notes, Decisions so far, Not yet specified and Out of scope.
   - Destination is non-empty.
   - Decisions so far is empty, because charting hand-resolves nothing.
   - There are at least 3 ticket files, `issues/NN-<slug>.md`, numbered from `01`.
   - Each ticket has a valid `Type:` and a `## Question`.
   - No ticket is `resolved`.
   - At least one `Blocked by:` line points at an existing ticket.
   - Nothing was written outside `.scratch/` ("plan, don't do").
4. It prints `OK: wayfinder chart-local-map`, or lists every failure and exits 1. If the `claude` CLI is missing or the model call fails, it exits 2, which counts as blocked, never as a pass.

Each run costs one model session (default `--model sonnet`; override with `WAYFINDER_FIXTURE_MODEL`).
