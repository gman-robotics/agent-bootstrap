# demo-mode-e2e

Live gate for `screen-record-feature`. The skill's real-world use needs a browser, a test
environment and a signed-in demo user, which a gate run cannot assume. This fixture instead runs
the skill's own tooling for real, with no app involved:

- `scripts/demoMode.ts`, through `scripts/demoMode.smoke.spec.ts`, in a real headless Chromium with
  Playwright video on;
- `scripts/assemble-segments.sh` on the resulting webm.

Requirements: Node/npm, network access to install `@playwright/test` (version pinned by
`SRF_PLAYWRIGHT_VERSION`, default `1.55.1`, matching the EG QA suite) and Chromium, and a real `ffmpeg` on `PATH` (or
`FFMPEG=/path/to/ffmpeg`). If any is missing, the runner exits `2` (blocked), never `0`.

Run it through the hub runner:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/screen-record-feature/fixtures/demo-mode-e2e \
  --skill screen-record-feature \
  --out skills/screen-record-feature/black-box-run.json
```

The two EstateGuru example recordings in `examples/` were each run end to end on dev (mobile notary 12.9
min, gift-a-plan 11.1 min, both exit 0 with demo mode on) when the skill was written. They are not
part of this gate, because they need EstateGuru VPN/dev access and they create real dev records.
