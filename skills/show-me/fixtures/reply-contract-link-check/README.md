# Fixture: reply-contract actually loads the real show-me path, and SKILL.md is photon-safe

**Why this fixture exists**: the task that created `show-me` required a checkable
fact, not a description — `skills/reply-contract/SKILL.md`'s pairing line must name
the real path `skills/show-me/SKILL.md`, not a fictional reference to a skill that
does not exist on disk. This fixture is the black-box-agent-qa evidence for that
fact, plus the supporting invariants that keep `show-me` a real, discoverable,
recipes-only skill.

**Revision (REPEAT finding on adversarial review of PR #13)**: the original version of this fixture
only ever `read_text()`'d Markdown and asserted headings/paths/frontmatter — a
`skills/show-me/SKILL.md` that recommended `Bash(open file.html)` or made mermaid/HTML
the default visual would still have passed every one of those checks. Same failure
class as PR #11 blocker #3 ("reading the skill Markdown is not a pass"). Checks 7 and
8 below close that gap: they are a real, run-it content scanner
(`find_photon_safe_violations` in `tests/test_show_me_skill.py`), not a heading grep,
and check 8 proves the scanner is not vacuous by running it against a synthetic
fixture of the exact violating shape and requiring it to fail loudly.

**Revision (adversarial review pass 2, heading-negation leak, REPEAT of the "reading Markdown is not
a pass" class)**: the scanner's negation check originally joined a unit's nearest
heading into the same negation-context string as the unit itself
(`f"{heading} {unit}"`). A heading merely naming an opt-in recipe
(`## Recipe: mermaid (opt-in only)`) or a category of bad outcomes (`## Pitfalls`,
whose own name contains the substring "pitfall") then cancelled a violation in *any*
unnegated body line beneath it — reproduced live: `## Recipe: mermaid (opt-in only)`
followed by a bare `Bash(open diagram.html)` body line, and the same body line under
`## Pitfalls`, both returned zero violations before this fix. Checks 9 and 10 below
close that gap; negation is now scoped to a unit's own text only, never its heading.
Fixing this also surfaced a real false positive on the committed file itself: Pitfalls
item 4 named the forbidden `Bash(open ...html)` pattern descriptively with no in-unit
negation word (it relied on the heading's "pitfall" to stay green) — reworded to start
with "Never", matching how every other prohibition in this file is already phrased, so
it now carries its own negation marker and the real file stays green under the
stricter, heading-blind check.

## Input fixture

Run `python3 -m unittest tests.test_show_me_skill -v` from the repo root.

## Expected output

Exit code `0`, stderr contains `OK` (the real `unittest` summary line).

## Mechanical check

`tests/test_show_me_skill.py` asserts, against the real committed files:

1. `skills/show-me/SKILL.md` exists, with `name: show-me` and `version: 1.0.1` in
   its frontmatter.
2. `skills/reply-contract/SKILL.md` contains the literal string
   `skills/show-me/SKILL.md` and no longer contains the old fictional pairing
   line (`Pair with **show-me** (trees / stacks / diffs).` with no path).
3. `skills/reply-contract/SKILL.md` says it *loads* `skills/show-me/SKILL.md`,
   rather than reimplementing the recipes inline.
4. `skills/reply-contract/references/photon-show-me.md` also references the real
   path, not just the bare skill name.
5. `.grok/skills/show-me/SKILL.md` **and** `.grok/skills/show-me/references/source.md`
   both exist (the full dual-tree mirror produced by
   `scripts/export_codex_skills.py --output-dir .grok/skills --force`).
6. `show-me` owns the visual recipes (call tree / file-screen tree / stack) and
   `reply-contract` keeps voice / task-name / spec-gate machinery — neither file
   duplicates the other's headings. `show-me` is also asserted to be **absent** from
   `scripts.index_skills.GRANDFATHERED_SKILLS` — it must earn its own live-gate pass,
   never be exempted from it.
7. **Photon-safe content scan** (`find_photon_safe_violations`, run against the real
   `skills/show-me/SKILL.md` text): fails if the file recommends opening a generated
   HTML/browser visual for the human, recommends a `Bash(open ...)` command, or treats
   mermaid/HTML as the *default* visual instead of opt-in. The scanner splits the file
   into markdown units (one bullet/paragraph, tagged with its nearest heading) so one
   bullet's negation word can't mask a violation in a different bullet, then flags any
   unit that matches a forbidden-guidance pattern with no negation marker (`never`,
   `no `, `without`, `opt-in`, `pitfall`, ...) in that unit *itself* — a heading's own
   words never count toward negating a body line beneath it (see checks 9–10).
8. **Proof the scanner is not vacuous**: the same function is run against
   `OLD_FICTIONAL_CASE_SKILL_TEXT`, a synthetic bullet list stating a mermaid/HTML
   default and a `Bash(open diagram.html)` command — check 8 requires this to return
   violations. This was also verified directly against the real, committed
   `skills/show-me/SKILL.md` (not just the synthetic text): temporarily replacing the
   real "opt-in only ... never by default" bullet with that same violating pair of
   bullets made `python3 -m unittest tests.test_show_me_skill -v` fail
   (`FAILED (failures=1)`, exit code `1`) on check 7, before the file was restored.
9. **Heading-negation leak, probe A**: `find_photon_safe_violations` run against a
   synthetic `## Recipe: mermaid (opt-in only)` heading followed by a bare, unnegated
   `Bash(open diagram.html)` body line — must return violations. Reproduced red
   against the unfixed scanner (zero violations) before this fix; permanently red on
   this fixture, permanently green on the real file, afterward.
10. **Heading-negation leak, probe B**: the same bare body line under a `## Pitfalls`
    heading instead — must also return violations, proving the earlier heading-level
    negation leak is closed regardless of which negation word the heading happens to
    contain.

Invoke the black-box-agent-qa run for real with:

```bash
python3 scripts/run_black_box_fixture.py \
  --fixture skills/show-me/fixtures/reply-contract-link-check \
  --skill show-me \
  --out skills/show-me/black-box-run.json
```
