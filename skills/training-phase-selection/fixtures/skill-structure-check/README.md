# skill-structure-check

Runs an inline `python3 -c` check against `skills/training-phase-selection/SKILL.md`. The check needs no third-party package.

It checks these items:
- The frontmatter has `name` (equal to the folder name), a quoted one-line `description`, and `version`.
- The file has the `**Purpose**` and `**Trigger**` markers and a `Last updated:` line.
- The file has no email address and no phone number.
- The file keeps the key principle text of the coaching skill.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/training-phase-selection/fixtures/skill-structure-check \
  --skill training-phase-selection \
  --out skills/training-phase-selection/black-box-run.json
```
