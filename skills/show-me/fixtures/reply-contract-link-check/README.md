# Fixture: reply-contract actually loads the real show-me path

**Why this fixture exists**: the task that created `show-me` required a checkable
fact, not a description — `skills/reply-contract/SKILL.md`'s pairing line must name
the real path `skills/show-me/SKILL.md`, not a fictional reference to a skill that
does not exist on disk. This fixture is the black-box-agent-qa evidence for that
fact, plus the supporting invariants that keep `show-me` a real, discoverable,
recipes-only skill.

## Input fixture

Run `python3 -m unittest tests.test_show_me_skill -v` from the repo root.

## Expected output

Exit code `0`, stderr contains `OK` (the real `unittest` summary line).

## Mechanical check

`tests/test_show_me_skill.py` asserts, against the real committed files:

1. `skills/show-me/SKILL.md` exists, with `name: show-me` and `version: 1.0.0` in
   its frontmatter.
2. `skills/reply-contract/SKILL.md` contains the literal string
   `skills/show-me/SKILL.md` and no longer contains the old fictional pairing
   line (`Pair with **show-me** (trees / stacks / diffs).` with no path).
3. `skills/reply-contract/SKILL.md` says it *loads* `skills/show-me/SKILL.md`,
   rather than reimplementing the recipes inline.
4. `skills/reply-contract/references/photon-show-me.md` also references the real
   path, not just the bare skill name.
5. `.grok/skills/show-me/SKILL.md` exists (the dual-tree mirror produced by
   `scripts/export_codex_skills.py --output-dir .grok/skills --force`).
6. `show-me` owns the visual recipes (call tree / file-screen tree / stack) and
   `reply-contract` keeps voice / task-name / spec-gate machinery — neither file
   duplicates the other's headings.

Invoke the black-box-agent-qa run for real with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/show-me/fixtures/reply-contract-link-check \
  --skill show-me \
  --out skills/show-me/black-box-run.json
```
