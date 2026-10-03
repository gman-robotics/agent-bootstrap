# skill-structure-check

Runs an inline `python3 -c` check against `skills/asd-ste100-writing/SKILL.md`. The check needs no third-party package.

It checks these items:
- The frontmatter has `name` (equal to the folder name), a quoted one-line `description`, and `version`.
- The file has the `**Purpose**` and `**Trigger**` markers and a `Last updated:` line.
- The file has no email address and no phone number.
- The file keeps the key rule text of the standing rule. It also checks that no sentence is longer than 25 words.

Invoke with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/asd-ste100-writing/fixtures/skill-structure-check \
  --skill asd-ste100-writing \
  --out skills/asd-ste100-writing/black-box-run.json
```
