# Active Context: Multi-Agent Skills Hub

## Current Focus (This Session)
**Task "hoh-schema-steal" — revision after Blair grok-4.6 REVISE** (2026-09-02, cloud agent, same branch `cursor/hoh-schema-steal-plan-aacd`, same [PR #15](https://github.com/gman-robotics/agent-bootstrap/pull/15)). Blair grok-4.6's REVISE at commit `d37a75e4` found 3 must-fix items on the plan-only PR below; all 3 fixed on the same branch/PR, no second PR, still not merged:
1. **REPEAT class, wiki citation**: §2 had cited the upstream `Flesymeb/HarnessOfHarness` product repo's own GitHub wiki as the fetched wiki SoT; the required SoT is `ThomasGinter/tmg-wiki`, `entities/harness-of-harness.md` @ `0651e608fded1c0676951ff16555b97e2671710d` (wiki PR #99) — a **private** repo this run's tools cannot read (`git ls-remote`/GitHub API both 404 without owner credentials), so it is cited by identity, not quoted; the substantive facts (Table 3, Listing 1) are independently cross-checked against arXiv `2609.01481` directly, unaffected by that access gap. Rewrote §2. Per instructions, an instance fix alone does not close a REPEAT class — added a real mechanical check, `tests/test_hoh_plan_wiki_citation.py` (new, 5 tests), scoped to the `## 2. Sources` section only (not the whole doc — a first draft scoped to the whole document self-tripped on §15's own historical description of the bug; re-scoped to just the Sources section, confirmed both the synthetic-fixture red/green and a live mutate-the-real-file-then-restore red/green proof, both recorded in the plan's new §15).
2. **NEW, Et status enum**: the fenced `E_t` schema's `qa_status` example/enum comment allowed `"partial"`/`"blocked"`, contradicting the plan's own prose ("verified|gap only"). Fixed the fenced schema to `"verified" | "gap"` at both packet and record level; the `et-status-not-verified-or-gap` fixture row and its note now require a single sample packet with **both** a bad packet-level `qa_status` and a bad record-level `status` at once, with `expected.stdout_contains` naming both.
3. **NEW, leftover question beside the spec-gate**: §6's GB-4 row and §7 disagreed on whether `head_sha` was optional (GB-4 row) or required (§7 schema comment) — an unresolved ambiguity sitting next to the closing Approve/Reject card. Resolved: `head_sha` is **required**, not optional, everywhere (§6, §7, §9, done-when) — GB-4's freeze is otherwise theater. Spec-gate card re-presented at the end with no leftover question beside it.

Held as already-good and untouched this pass: GB-1..6/H-1..5 mapping, Preservation-Gate-≠-REPEAT distinction, all 9 fixtures' argv+exit+stdout shape, hub-vs-overlay split, no `9259d42` restole, the skip list, the Table 3 numbers, no live `evidence-packet-protocol`/`preservation-gate` skill files (still plan-only — the one new file besides the plan doc, `tests/test_hoh_plan_wiki_citation.py`, is a documentation mechanical lock on this plan's own citation text, not the GB-1 product). `python3 -m unittest discover -s tests`: 45/45 pass (40 pre-existing + 5 new), confirmed both before and after this revision. Did not clone `Flesymeb/HarnessOfHarness`, did not start AWS/GMA-8, did not treat "ok" as Approve. **Next**: Blair grok-4.6 re-grills; no implement-track work starts until CoS records a literal Blair **Approve** with no leftover question beside it.

## Previous Focus (superseded this session) — original plan-only submission
**Task "hoh-schema-steal" — plan-only, initial submission** (2026-09-02, cloud agent, branch `cursor/hoh-schema-steal-plan-aacd`). Per Tom's 2026-09-02 decision to steal HoH's (Harness-of-Harness, [`Flesymeb/HarnessOfHarness`](https://github.com/Flesymeb/HarnessOfHarness), arXiv `2609.01481`) evidence-packet schema and Preservation Gate concept — schema/process only, not the product, not autonomous no-human development — wrote one plan document, `docs/projects/agent-bootstrap/hoh-schema-steal-plan.md`, and nothing else. No skill, schema, validator, or fixture was implemented as live code; every JSON/Markdown shown in the plan is a fenced-block spec. Cites wiki `0651e60` `[[harness-of-harness]]` and paper `2609.01481` Table 3 (locked ablation: Full HoH@3 `71.52`; w/o Plan Update `−8.13`; w/o Evidence Feedback `−6.28`; w/o Warm-Start `−7.85` — verified against the fetched paper text, not recomputed) and Listing 1 (the `E_t` structure). Maps every named steal item (GB-1..6, H-1..5) to a concrete implement-track target: new `skills/evidence-packet-protocol/` (schema + skill), new `skills/preservation-gate/SKILL.md` (canonical Preservation Gate definition, distinct from REPEAT), a one-line pointer patch (not a rewrite) proposed for `skills/multi-harness-coordination/SKILL.md`, and 9 named black-box fixtures (argv + exit code + stdout_contains) for the implement-track PR. Explicitly did not touch `skills/plan-code-review-workflow/SKILL.md`, `skills/expert-pr-review/SKILL.md` (hub lock), or `skills/reply-contract/SKILL.md` (placement decision in the plan explains why — sidesteps the "Eleanor reply-contract 1.3.0 vs. this hub's 1.4.0" ambiguity entirely). Did not clone `Flesymeb/HarnessOfHarness`, did not touch `arm`, did not restale swarm-forge cockpit/envelope (already at `9259d42`), did not mint Kit/Lane entity pages. Opened as one draft PR against `main`. Superseded by Blair grok-4.6's REVISE above — not merged, not self-reviewed (per task instructions).

## Previous Focus (superseded this session)
**Task "show-me-native-skill" — follow-up PR after PR #13 squash-merge** (2026-08-26, cloud agent, branch `cursor/show-me-heading-negation-leak-b2ea`). [PR #13](https://github.com/gman-robotics/agent-bootstrap/pull/13) squash-merged to `main` as `3294849`. A pass-2 adversarial review of the merged state found one REPEAT must-fix (same failure class as the pass-1 "reading Markdown is not a pass" blocker): `find_photon_safe_violations()` joined a unit's nearest heading into its negation-context string, so a heading merely naming an opt-in recipe (`## Recipe: mermaid (opt-in only)`) or a category of bad outcomes (`## Pitfalls`, whose own name contains the substring "pitfall") cancelled a violation in *any* unnegated body line beneath it — reproduced live: `## Recipe: mermaid (opt-in only)` + a bare `Bash(open diagram.html)` body line, and the same body line under `## Pitfalls`, both returned zero violations before the fix. New branch, new PR — #13 itself not reopened, not reverted, not merged again. See `memory-bank/progress.md` 2026-08-26 "heading-negation leak" entry for the full breakdown.

## Superseded Focus (merged) — "show-me-native-skill" PR #13 revision
**Task "show-me-native-skill" — PR #13 revision** (2026-08-26, cloud agent, branch `cursor/show-me-native-skill-6d8c`). Adversarial review of [PR #13](https://github.com/gman-robotics/agent-bootstrap/pull/13) at `b06acbd` found two must-fix blockers: (1) REPEAT — the fixture's captured "live" evidence was a heading/path-grep unittest with no actual content check, so a `SKILL.md` recommending `Bash(open ...html)` or a mermaid/HTML default would still have passed; (2) NEW — `scripts/export_codex_skills.py`'s `reply-contract` `quick_start` still shipped the old pathless "Pair with show-me" line into the generated `.grok/skills/reply-contract/SKILL.md`, even after the canonical file was fixed. Both closed on the same branch/PR: added a markdown-unit-scoped content scanner (`find_photon_safe_violations` in `tests/test_show_me_skill.py`) that fails on a real, committed injection of the old violating shape (proved live: `FAILED (failures=1)` against a temporarily-corrupted real `SKILL.md`, then reverted); fixed and re-exported the exporter quick_start. See `memory-bank/progress.md` 2026-08-26 "PR #13 revision" entry for the full breakdown. Not merged, not self-reviewed, no second PR.

### Previous session on this task (superseded by the revision above)
**Task "show-me-native-skill"** (2026-08-26, cloud agent, branch `cursor/show-me-native-skill-6d8c`). New, independent task — not a follow-up to PR #11/#12 (those stay closed, untouched). Added a new native `show-me` skill (visual recipes only: call tree, file/screen tree, stack, diff of those shapes, opt-in mermaid) and pointed `reply-contract`'s pairing line at the real `skills/show-me/SKILL.md` path instead of the old fictional, path-less mention. See `memory-bank/progress.md` 2026-08-26 "show-me-native-skill" entry for the full breakdown. Opened as one draft PR against `main`; not merged, not self-reviewed.

## Previous Focus (superseded, merged) — "Bootstrap leftover gates" / PR #12

### Revision: leftover 1's frozen+len==20 pin was a same-length swap away from useless (2026-08-26)
Adversary revised **leftover 1 only** (L2/L3 and #11's four blockers stayed closed, re-verified not reopened): `isinstance(frozenset)` + `len() == 20` cannot tell the real `GRANDFATHERED_SKILLS` apart from a same-length swap (one real name removed, one brand-new fake name added). **Reproduced live against the real files first** (temporarily, reverted, not committed): swapped `delegation-patterns` for a fake name in both `scripts/index_skills.py` and the matching `skills/INDEX.md` entry — all 26 prior tests passed, confirming the gap for real (frozenset+len==20 stayed true; `find_ungated_entries` returned `[]` since the swapped-in name is allowlisted-and-skipped and the swapped-out entry no longer exists in INDEX.md to check).
- Fix: added `ORIGINAL_GRANDFATHERED_SKILLS`, an independent pin of the exact 20 names in `tests/test_index_live_binding.py`; `test_grandfathered_skills_is_frozen_at_the_original_twenty` now asserts exact-set equality, not just count. New `test_swapping_one_grandfathered_name_for_a_new_one_is_caught` fixture proves the swap still passes the weaker checks but fails the new equality pin.
- Red-then-green confirmed against the real production files (not just the isolated fixture): swap applied → equality test fails with a clear symmetric-difference message, while the other two INDEX-bind tests stay green (proving they alone don't close this gap); swap reverted → 27/27 green again.
- Should-fix: `scripts/index_skills.py`'s module docstring and the `GRANDFATHERED_SKILLS` code comment no longer imply the module binds AGENTS.md/trigger tables, and no longer read as an invitation to add a name — the set is now described as closed, with the equality pin named as what enforces that.
- Did not touch: `scripts/check_skill_live.py`, `CONTRIBUTING.md`, `skills/close-out/SKILL.md`, any `.grok/` mirror, any `black-box-run.json`, any version footer (no `SKILL.md` edited, so no staleness recapture needed) — leftover 1 was the only thing in scope.
- Verification: `python3 -m unittest discover -s tests` — 27/27 pass. `python3 scripts/index_skills.py` and `check_skill_live.py` for all three live-gated skills still exit `0`, unchanged.

### Earlier this session — original three-leftover pass
- **Leftover 1 (original pass)**: `GRANDFATHERED_SKILLS` was already a `frozenset` of the original 20 names as of `377cfd8` — nothing to fix in the value itself at the time. Added `test_grandfathered_skills_is_frozen_at_the_original_twenty` to pin the type + count — later found insufficient by adversary review (see revision above, which strengthens this to exact-equality).
- **Leftover 2 (closed, not reopened)**: `python3 scripts/index_skills.py` raised `ModuleNotFoundError` with no `PYTHONPATH` (script dir, not repo root, lands on `sys.path[0]`). Fixed with a guarded `sys.path` insert before the `scripts.check_skill_live` import; added a real-subprocess regression test with `PYTHONPATH` stripped.
- **Leftover 3 (closed, not reopened)**: `CONTRIBUTING.md` §1 and `skills/close-out/SKILL.md` Step 9.4 implied the mechanical test enforces AGENTS.md/trigger-table placement too; it only parses `skills/INDEX.md`. The five trigger-list files use three different formats — not a clean parser extension — so took the smaller honest fix: reworded both (+ regenerated the `.grok/skills/close-out` mirror via the real exporter) to scope the claim to `skills/INDEX.md`. `close-out` bumped `1.3.0` → `1.3.1`, black-box run record recaptured, hub version `0.9.0` → `0.9.1`.

## Previous Focus (superseded, merged) — "Bootstrap three locks"
**Task "Bootstrap three locks"** (2026-08-26, cloud agent, branch `cursor/bootstrap-three-locks-dc11`). Skills-only change canonizing three generic process locks that had only existed on an external harness-specific overlay (already forked `close-out` from this hub's v1.0.0) so every harness loading this repo gets them. Opened as one draft PR against `main`, later merged: [PR #11](https://github.com/gman-robotics/agent-bootstrap/pull/11).

### Revision: adversary review found the locks were still prose — made mechanical (2026-08-26)
An adversary review of PR #11 (all four blockers marked NEW, not REPEAT) found the first pass had described the mechanism in Markdown without building it: no fixture backed the REPEAT lock's claim, `black-box-agent-qa` had no runnable contract (SKILL.md only), the PR's own evidence was "unittest + grep" (reading, not a black-box pass), and `close-out`/INDEX never defined what "live" mechanically means. Fixed on the same branch/PR, same 4 blockers:
1. **REPEAT fixture is real**: `skills/triage-review-feedback/fixtures/repeat-exporter-dropped-references/` reproduces the actual failure class logged 3x in this file (2026-08-22 NEW + 2 REPEATs: exporter `--force` dropping hand-added `references/` files) and `tests/test_export_codex_skills.py::test_force_reexport_preserves_hand_added_reference_files` is red without a fix. **Actually fixed the exporter** (`collect_preserved_files` in `scripts/export_codex_skills.py`) so the test goes green — the fix ran for real against `.grok/skills/grill-with-docs/` during this session's own re-export and needed **zero manual restoration** for the first time (verified: `git diff --stat -- .grok/skills/grill-with-docs/` is empty after `--force` re-export).
2. **black-box-agent-qa is runnable**: `SCHEMA.md` (case.json contract), `scripts/run_black_box_fixture.py` (the invoker), and two worked fixtures (`fixtures/repeat-lock-mechanical-check/`, `fixtures/close-out-live-gate-check/`) with `README.md` + `case.json` each. TDD: `tests/test_run_black_box_fixture.py` (6 tests, red before the module existed).
3. **Captured a real run record for this change**: ran `scripts/run_black_box_fixture.py` for real against `black-box-agent-qa`, `triage-review-feedback`, and `close-out` — all three `skills/<name>/black-box-run.json` are genuine captured output (real `stderr_tail`, real `skill_sha256`), not hand-written. `scripts/check_skill_live.py <name>` flipped from exit `1` ("no run record") before capture to exit `0` ("live-eligible") after, for all three.
4. **Live-flip defined + gated**: `scripts/check_skill_live.py` (new; TDD, `tests/test_check_skill_live.py`, 5 tests) is the mechanical live-flip — a skill is live only when it exits `0` against a `black-box-run.json` with `verdict: pass` and a `skill_sha256` matching the *current* `SKILL.md`. Editing the skill afterward (including a silent trajectory refine) invalidates the hash and the gate fails until re-run — proven by `test_fails_when_skill_md_changed_since_the_run_record_was_captured`. `skills/close-out/SKILL.md` Step 9 and `skills/INDEX.md §Adding a New Skill` both now name this exact sequence (write → run the fixture → `check_skill_live.py` exits 0 → only then list it); `CONTRIBUTING.md` §1 gates the same way.
- Should-fix items also landed: worked REPEAT fixture in-tree (item 1 above); minimum I/O contract documented in `SCHEMA.md`; INDEX.md/CONTRIBUTING.md both gate discoverability on the run record; the `.grok` triage wrapper's "goes red on a fixture" claim is now backed by a real fixture pointer (`fixtures/repeat-exporter-dropped-references/`) rather than dropped.
- Versions bumped again: `triage-review-feedback` `1.1.0` → `1.2.0`, `close-out` `1.1.0` → `1.2.0`, `black-box-agent-qa` `1.0.0` → `1.1.0`. Hub version `0.7.0` → `0.8.0`.
- Verification: `python3 -m unittest discover -s tests` — 20/20 pass (9 pre-existing/prior-revision + 11 new: 1 REPEAT regression test + 5 `check_skill_live` tests + 6 `run_black_box_fixture` tests — some counts overlap categories, see `progress.md` for the exact new-test list). Forbidden-name grep on the staged diff: no matches.
- Same branch, same PR (#11) — no second PR opened, per instruction. Not merged.

### Revision (pass 2): the live gate was never bound to the real INDEX.md listing (2026-08-26)
Adversary pass 2 revised with one REPEAT blocker — same failure class as prior blocker #4 (a mechanism that exists but nothing actually runs it): `check_skill_live.py` worked when typed by hand, but 20 of 23 real `skills/INDEX.md` entries were "not live" and nothing caught it — no test, no CI, no hook. Confirmed via `gh api .../actions/workflows` that this repo has **zero CI**, so the bind belongs in `tests/` (the command every session in this file already cites as verification: `python3 -m unittest discover -s tests`).
- New `scripts/index_skills.py`: `find_ungated_entries()` is the real bind — checks every `### <name>` in `skills/INDEX.md` against `check_skill_live`, skipping a named `GRANDFATHERED_SKILLS` allowlist (the 20 pre-gate skills, explicit by name, not silently exempted).
- New `tests/test_index_live_binding.py` — `test_every_non_grandfathered_index_entry_is_live` fails the suite if INDEX lists an ungated skill live. `test_binding_catches_an_index_entry_with_no_run_record` is the REPEAT-class fixture (synthetic INDEX.md entry with no run record, run through the real production function) — confirmed red (`ModuleNotFoundError`) before the module existed, green after. Also reproduced the adversary's exact count for real: `find_ungated_entries` with an empty allowlist against the actual INDEX.md returns exactly 20 failures.
- Should-fix landed: third fixture `fixtures/check-skill-live-cli/` (non-`unittest` CLI invocation) narrows the "unittest is the only demonstrated SUT" concern; `close-out` Step 9's exit-code sentence now names the stale-hash case it previously omitted; `INDEX.md`/`CONTRIBUTING.md` explicitly warn against adding a *new* skill to `GRANDFATHERED_SKILLS` to dodge a failure.
- Live mid-session proof the mechanism works on its own maintainer: editing `close-out`/`black-box-agent-qa` SKILL.md to add these very changes made `test_every_non_grandfathered_index_entry_is_live` fail with "stale — SKILL.md changed since capture" for both, until both run records were re-captured — then green again.
- Versions: `close-out` `1.2.0` → `1.3.0`, `black-box-agent-qa` `1.1.0` → `1.2.0` (`triage-review-feedback` untouched this pass). Hub `0.8.0` → `0.9.0`.
- Verification: `python3 -m unittest discover -s tests` — 24/24 pass. Same branch/PR (#11), no second PR, not merged.
- `skills/triage-review-feedback/SKILL.md` (`1.0.0` → `1.1.0`): every FIX now also tagged **NEW** or **REPEAT** (Step 3). REPEAT = same failure class already called on this repo or product family, a class match not a location match; never closed by an instance fix or another comment/AGENTS.md/skill/style-guide line — closing requires a mechanical check (lint, compiler/type diagnostic, failing-then-green test, or CI rule) added in the Step 4 fix commit. NEW tags get their failure class recorded in Step 7 (`memory-bank/progress.md`) so the next sighting is REPEAT, not re-discovered as NEW.
- New `skills/black-box-agent-qa/SKILL.md` (`1.0.0`): black-box verification for any agent persona, harness config/wiring, verb/command, or skill change — name a literal input fixture + checkable expected output, then actually run it end-to-end against the real system under test. Reading a PR/skill Markdown is not a pass; a mock-only suite is not sufficient proof on its own; an environment-blocked run escalates, it never passes. Hard limits: never authorizes auto-merge, never authorizes a silent refine of harness/agent state from a run's outcome.
- `skills/close-out/SKILL.md` (`1.0.0` → `1.1.0`) Step 9: user Approve on a Step 8 finding authorizes writing/editing the skill file, not shipping it — a new/edited skill goes live only after a `black-box-agent-qa` pass against the I/O case now required on every Step 8 skill proposal. Names the failure class where a run-driven skill edit can institutionalize a shortcut — route it through Step 8 as a candidate pattern, never install it live straight from the run.
- Registered `black-box-agent-qa` for discoverability: `skills/INDEX.md` new entry + updated one-liners for the two touched skills, `AGENTS.md` §4 "Other Key Skills" table, `.cursor/rules/agent-bootstrap.mdc` trigger table, `.clinerules`/`.kilocoderules`/`.cursorrules`/`.openhands_instructions` trigger lists — same dual-tree/trigger-table convention already used for every other skill.
- `scripts/export_codex_skills.py`: new `SkillConfig` for `black-box-agent-qa`, refreshed quick-start bullets for `triage-review-feedback` and `close-out`; re-exported `.grok/skills/` via `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`; restored the two `grill-with-docs/references/{adr-format,context-format}.md` files the exporter's `--force` rmtree drops and does not regenerate (same pre-existing, unrelated exporter gap noted in the prior swarm-forge session).
- `tests/test_export_codex_skills.py`: added an assertion that `black-box-agent-qa` is registered.
- Hard constraints honored (verified by `git diff | grep`): no roster/specialist names, no standing model-pair table, no Prime Agent/IPython RLM install, no Dune-ban or auto-merge authorization, no unrelated skill rewrites, no Slack channel/personal repo/calendar specifics.
- Verification: `python3 -m unittest tests.test_export_codex_skills` — 8/8 pass, run both before and after the `SkillConfig`/re-export changes.
- Not merged, not self-reviewed (draft PR, per no-merge-without-explicit-instruction) — user's own reviewer flow owns the review.

## Previous Focus (superseded)
**GitHub issue #8 — "Rewrite swarm-forge steal set as bootstrap skills"** (2026-08-22, cloud agent, branch `cursor/steal-swarm-forge-skill-updates-a543`). Per the issue and the pasted Scout memo steal list, landed the "full useful steal set" as native in-house skill/doc edits — ideas only from `unclebob/swarm-forge` (no LICENSE on that repo; no files/scripts/prompts/dashboard HTML copied):
- Spec-gate card + clarify card: new `## Gate cards` section in `skills/reply-contract/SKILL.md` (binary Approve/Reject on a held `Documents` list vs. a plain question+Submit — gate ≠ question). Wired into `skills/grill-with-docs/SKILL.md` Step 4.
- Stable task Name: new `## Task name` section in `reply-contract`; referenced from `grill-with-docs` and `skills/close-out/SKILL.md` Step 1.
- Four-field envelope stanza (`type`/`to`/`priority`/`task`) as an **optional** markdown block in `skills/adversarial-coordination-workflow/SKILL.md` and `skills/multi-harness-coordination/SKILL.md` — explicitly excludes `merge_and_process`, SHA identity, outbox paths, stdout `TASK:`/`NO_TASK` helpers, generated bodies.
- Architectural Review Phases checklist **names only** (UI/Core Separation; Dependency Rule; Information Hiding And Encapsulation; Local Code Quality) added to `agents/software-architect.md` and cross-referenced from `skills/codebase-simplification-audit/SKILL.md` — no CRAP/mutation/DRY tool install.
- New-invariant constitution articles: `docs/shared/constitution.md` (5 short articles) + `docs/shared/decisions.md` ADR-004 (provenance/no-vendoring decision) + one-line pointers from `AGENTS.md` §6 and `skills/INDEX.md` (AGENTS.md remains the source of truth, not replaced).
- Quality-slice cleanup pass folded into the existing Engineer role (`agents/software-engineer.md`, bounded to touched files) — no new cleaner/hardener/specifier role, no Gherkin-as-spec.
- Housekeeping: `skills/INDEX.md` entries updated for the 5 touched skills; `.grok/skills/` re-exported via `python3 scripts/export_codex_skills.py --output-dir .grok/skills --force` after adding matching `SKILL_CONFIGS` quick-start bullets in `scripts/export_codex_skills.py`; restored two grill-with-docs `.grok` reference files (`adr-format.md`, `context-format.md`) that the exporter's `--force` rmtree does not regenerate (pre-existing exporter gap, not part of this issue's scope — worth a future skill-gap note).
- Explicitly **not** touched/copied per the issue: `./swarm`, `handoffd`, cockpit/dashboard, `pack_web`/curl\|tar packs, tmux/worktree control plane, CRAP/mutation/DRY tooling, `skills/expert-pr-review/SKILL.md`, `skills/plan-code-review-workflow/SKILL.md` (no rewrite, no pointer added — not needed for this scope).
- Verification: `python3 -m unittest tests.test_export_codex_skills` — 7/7 pass (both before and after the re-export). `git diff --check` flags only pre-existing two-trailing-space markdown line-break style (matches existing ADR/agent file convention, not a real issue).
- Opened as **one draft PR** against `main`; not merged, not self-reviewed (per issue instructions — user's own reviewers, e.g. Blair grok-4.6, own the review).

### Revision after Blair grok-4.6 review (PR #9, 2026-08-22)
Blair's adversarial review verdict: **revise**. Blocker: `docs/shared/constitution.md` Article 1 (binary Approve/Reject, never chat prose) contradicted `AGENTS.md` §4 PLAN's "Plan ready? Switch to Act mode?" and `agents/software-architect.md`'s chat-prose closer, which this PR itself edited. Fix landed on the same branch/PR (`3ec3d90` → new HEAD, see progress.md):
- `agents/software-architect.md`: closer now presents `reply-contract`'s spec-gate card (`Documents:` = plan location, `<next-phase>` = `CODE`) instead of "Does this look good? Switch to Act mode?"; Related Skills lists `reply-contract`.
- `AGENTS.md` §4 PLAN step 1: last bullet now points at the spec-gate card, not the chat-prose question.
- `docs/shared/constitution.md` Article 1: added an explicit **Scope** line (binds only the named `Enforced by` list) + an **Explicitly out of scope** note naming `skills/plan-code-review-workflow/SKILL.md`'s own literal PLAN-step wording as intentionally untouched (Tom lock — not rewritten). Added `agents/software-architect.md` + `AGENTS.md` §4 PLAN to `Enforced by`.
- `skills/plan-code-review-workflow/SKILL.md` — **not touched**, per the lock.
- Should-fix landed too: `skills/reply-contract/SKILL.md` "Task name" now says the card Name **is** the envelope `task:` value (one string, not two identifiers hoping to match) — version bumped 1.2.0 → 1.3.0. Spec-gate card rules gained "no leftover questions beside Approve" and "only the literal word Approve/Reject stamps it" in both `reply-contract` (spec-gate card section, pitfalls, verification checklist) and `grill-with-docs` Step 4 (pitfalls, verification checklist) — `grill-with-docs` version bumped 1.0.0 → 1.1.0. Constitution Article 1 body also states both rules directly.
- `skills/INDEX.md` constitution pointer now states Article 1's scope explicitly and names the `plan-code-review-workflow` exception.
- Re-exported `.grok/skills/grill-with-docs/` and `.grok/skills/reply-contract/` (`python3 scripts/export_codex_skills.py --output-dir .grok/skills --force`); restored the two pre-existing `grill-with-docs/references/{adr-format,context-format}.md` files the `--force` rmtree deletes (same known exporter gap as before). `agents/software-architect.md` needed no re-export — `.grok/agents/software-architect.md` is a symlink to the canonical file.
- Verification: `python3 -m unittest tests.test_export_codex_skills` — 7/7 pass before and after re-export; `git diff --check` clean; `git status --porcelain` clean after restoring the two reference files.
- Not addressed in this revision (not in the user's required-fix list for this pass): Blair's should-fix items on the four-field envelope being "file, not pane chat" (`multi-harness-coordination`) and Article 5's dangling `expert-pr-review` enforcement claim — left for a future pass.
- Pushed to the same branch/PR; still not merged, still not self-reviewed.

### Revision after Blair pass 2 (PR #9, 2026-08-22)
Blair pass 2 blocker: `AGENTS.md` §3's own Architect-role summary bullet (line ~148, distinct from the §4 PLAN bullet fixed in pass 1) still said "End planning by asking: 'Does this plan look good? Shall we switch to Act mode...'" — a leftover chat-prose closer that Article 1 lists `agents/software-architect.md` as already enforcing via the card. Fix (scope-limited to this one bullet, per task instructions — no `plan-code-review-workflow.md` rewrite):
- `AGENTS.md` §3 software-architect.md bullet: now points at `agents/software-architect.md`'s spec-gate card (`skills/reply-contract/SKILL.md` format, `docs/shared/constitution.md` Article 1 cross-ref) instead of the "Does this plan look good?" question — same contract as the §4 PLAN bullet and the persona file: `Documents:` names the held plan, only a literal **Approve**/**Reject** counts as the stamp ("looks good"/"ok"/silence do not), and the card cannot show `Approve` while a leftover question sits beside it.
- No other files touched — `skills/plan-code-review-workflow/SKILL.md` left as-is (out of scope, per the Article 1 note and this task's explicit instruction); grok export does not mirror `AGENTS.md` (`grep` for the old phrase across `.grok/` returns no matches), so no re-export needed.
- Verification: `python3 -m unittest tests.test_export_codex_skills` — 7/7 pass; `git diff --check` clean.
- Pushed to the same branch/PR (#9); still not merged, still not self-reviewed.

## Earlier Focus (superseded)
**Formatting and replay review complete** (2026-06-23). Reviewed the added skill/workflow updates in this checkout and fixed local formatting issues:
- Replaced malformed `skills/agent-bootstrap/SKILL.md` placeholder text with valid skill frontmatter, quick-start steps, and replay guidance.
- Added final trailing newlines to canonical skill Markdown files that were missing them.
- Verification evidence: `python3 -m unittest tests.test_export_codex_skills` passed (6 tests), and `git diff --check` passed.
- Added missing `skills/task-loop-7-phase.md` for the strict OBSERVE -> THINK -> PLAN -> BUILD -> EXECUTE -> VERIFY -> LEARN algorithm, wired it into `skills/INDEX.md`, `AGENTS.md`, harness trigger files, `scripts/export_codex_skills.py`, exporter tests, and regenerated `.grok/skills/task-loop-7-phase/`.

Replay finding for `/Users/tginter/dev/estategururepo/agent-bootstrap`: do not blind cherry-pick the generic gman-robotics commits. That checkout has EstateGuru-specific skills and local history, is `main...origin/main [ahead 1]`, lacks `.grok/`, `scripts/install-grok.sh`, `skills/multi-harness-coordination.md`, and `skills/agent-bootstrap/SKILL.md`, and direct `git apply --check` of the generic v0.5.0 patch fails against multiple customized files. Use a selective replay/merge plan instead.

## Current Plan — Re-implement install-grok.sh + High-Priority Grok Improvements (post-PR #1)

**Context**: After the merged `feat/grok-native-support` PR (now at d02f307 on main), the repo has a solid `.grok/skills/` + `.grok/agents/` tree committed. However, it lacks a first-class installation mechanism for using the bootstrap's skills and agents in *other projects* (the primary value of this hub).

Our earlier session (commit 97874bd) built a good `scripts/install-grok.sh` + richer documentation. User explicitly chose Option B: Re-implement/adapt on top of the current merged structure (respecting its approach), starting with the two high-priority items.

**High Priority (do first)**
1. `scripts/install-grok.sh` — Adapted version that works cleanly with the current committed `.grok/` layout (exporter + current agent files).
2. Enhanced Grok documentation in `AGENTS.md` (and supporting files) for cross-project usage.

**Medium Priority (after high priority) — COMPLETED**
- Improved agent handling in `install-grok.sh`: plugin installs now generate proper Grok frontmatter (model: sonnet, tools list, color, etc.) while --local mode respects the committed structure.
- Enhanced TDD coverage in `InstallGrokScriptTests` (verifies skill count + Grok frontmatter in generated agents for user installs).
- All tests green. Script is production-ready for the two main use cases.

**Principles**
- Respect the merged PR's packaging where reasonable.
- Make the install script solve the "use bootstrap skills/agents in any project" problem.
- Strict TDD for new script code.
- Update memory-bank after significant steps.
- Full self-review + critical checklist before any commit.

---

## Previous Plan — Sync Grok Documentation Across README, AGENTS.md, and Supporting Files (for reference)
**Created by**: Software Architect (following mandatory memory-bank read of all 6 files + AGENTS.md + relevant user-guide/*.md + grep for "Grok" + git show of the feature commit + exploration of .grok/ tree and scripts/export_codex_skills.py).

**Date**: 2026-05-19
**Status**: Approved by user — Act/Engineer executing now (2026-05-19). Progress will be appended below and in progress.md after each major file or logical chunk.

### Goals
- Make the first-class Grok 4.3+ native support (added in commit 6f48582) fully documented and discoverable so Grok CLI/TUI users get the same "clone + zero config" experience as Claude Code, Cline, etc. users.
- Bring documentation parity: Grok currently has only a one-line bullet in AGENTS.md §1 and a footer; README still lists old harnesses and v0.2.0 status.
- Record the packaging decision as a proper ADR (ADR-006) for future maintainers.
- Ensure all "last updated", version strings, and "What's Inside" / compatibility lists are consistent at v0.4.0 / 2026-05-19.
- Preserve KISS, absolute-path discipline, source-of-truth rules (canonical files stay in skills/ + agents/; .grok/ is generated + symlinked).

### Scope (In)
- **Primary files**:
  - README.md (compatibility bullets, What's Inside .grok/ entry, Status/version bump).
  - AGENTS.md (expand Grok entry into a full dedicated subsection parallel to "### Claude Code: Native Agent Spawning", plus any cross-refs).
  - docs/projects/agent-bootstrap/decisions.md (new ADR-006 at the end + update index table).
- **Secondary files** (consistency / discoverability):
  - ONBOARDING.md (add 1-2 sentences on Grok zero-config, no install-agents equivalent needed).
  - CONTRIBUTING.md (add maintenance note for re-exporting .grok/ after skill/agent changes).
  - skills/INDEX.md (note that the 11 skills surface as `/<kebab-name>` in Grok via the .grok/ packaging).
  - docs/README.md and any other docs/*/decisions.md or footers with dates (light touch, only if they claim pre-0.4.0 versions).
- **Process artifacts**: This plan written to activeContext + progress; later execution will also update memory-bank at end per protocol.

### Scope (Out)
- Any change to implementation logic, the export script (beyond docs), .grok/ file contents, or adding bundled/global skills.
- Creating the actual PR or pushing (user responsibility after QA).
- Updates to external Grok user-guide (we only document our side of the integration here).
- Touching empty .grok/personas/ and .grok/roles/ beyond documenting them as intentional placeholders (per Grok's custom roles/personas TOML+md layout in 15-subagents.md).

### Detailed Changes per File (KISS, match existing tone)

1. **README.md**
   - Compatibility section (around line 72-79): Insert **Grok** bullet (prominently, after Cursor or grouped with modern ones):
     ```
     - **Grok** (xAI Grok 4.3+ CLI/TUI and compatible environments) — **Zero-config native support**. The repo includes `.grok/skills/` (11 reusable workflows invocable as `/plan-code-review-workflow`, `/expert-pr-review`, `/memory-bank-protocol`, etc.) and `.grok/agents/` (symlinks for `Engineer`, `Architect`, `QAReviewer`, `SecurityReviewer`, `UIUXEngineer` usable via the `task` tool). AGENTS.md is auto-loaded via project-rules discovery. See AGENTS.md §1 and §3 for details.
     ```
   - What's Inside (after agents/ or memory-bank/ entry): Add a `.grok/` bullet:
     ```
     - **.grok/** — Grok (and Codex) native packaging for zero-config experience:
       - `skills/<name>/SKILL.md` + `references/source.md` (thin trigger frontmatter + authoritative playbook copy of each skill in /skills/).
       - `agents/` — symlinks to the 5 canonical role definitions (enables native `subagent_type` spawning).
       - `personas/` and `roles/` — empty placeholders for future custom persona/role TOML+md definitions (Grok layout convention).
     ```
   - Status section (line ~97): Change to `Current v0.4.0 — Core files, skills, agents, docs/, and first-class Grok 4.3+ native support (.grok/ packaging) in place. Fully functional for immediate use across Claude, Cline, Grok, Cursor, and others.`
   - Update footer date if present.

2. **AGENTS.md**
   - §1 Quick Start harness list: The existing Grok bullet is good; keep or lightly polish for consistency with new details below.
   - After the "### Claude Code: Native Agent Spawning" subsection (around line 190-210), insert a parallel:
     ```
     ### Grok: Native Skills, Agents, and Project Rules (v0.4.0+)

     When using **Grok 4.3+ CLI/TUI** (or compatible), the hub provides first-class native integration with **zero extra configuration**:

     - **Project Rules**: `AGENTS.md` (and CLAUDE.md alias) is auto-discovered and loaded at every level of the repo (see Grok user-guide 11-project-rules.md). The full global rules, memory-bank protocol, and workflows are active immediately.
     - **Skills**: All 11 skills are packaged under `.grok/skills/<name>/`. Grok surfaces them as slash commands (`/plan-code-review-workflow`, `/expert-pr-review`, `/write-tests`, `/memory-bank-protocol`, `/subagent-routing`, `/debug-investigation`, etc.). Each SKILL.md contains minimal frontmatter + quick-start; the complete authoritative steps live in `references/source.md` (kept in sync with the canonical `skills/*.md` files).
     - **Agents / Subagents**: The 5 reusable roles are exposed via `.grok/agents/` symlinks. They appear in `grok inspect`, the subagent catalog (Ctrl+Shift+A), and can be spawned with the `task` tool:
       ```
       task(subagent_type="Engineer", description="...", prompt="...", ...)
       task(subagent_type="Architect", ...)
       task(subagent_type="QAReviewer", ...)
       task(subagent_type="SecurityReviewer", ...)
       task(subagent_type="UIUXEngineer", ...)
       ```
       The YAML frontmatter `name:` in each `agents/*.md` determines the `subagent_type` value. Symlinks + the exporter script guarantee the canonical definitions in `agents/` remain the single source of truth.
     - **Personas / Roles placeholders**: `.grok/personas/` and `.grok/roles/` exist as empty directories to follow Grok's discovered layout for future custom persona or role TOML definitions (see user-guide 15-subagents.md). They are safe to ignore until the hub defines shared custom ones.

     **Maintenance for contributors**:
     - Edit the canonical sources in `skills/*.md` and `agents/*.md` only.
     - After changes: `python scripts/export_codex_skills.py --output-dir .grok/skills --force` (re-generates the 11 thin wrappers) and update any symlinks under `.grok/agents/`.
     - This keeps Grok users in sync without duplication or drift.
     - See `skills/delegation-patterns.md` and `skills/subagent-routing.md` for advanced spawning patterns (Haiku vs Sonnet model selection, parallel calls, worktree isolation).

     The result matches the project vision: clone the repo, open in Grok, everything (roles, workflows, memory-bank, manifest, docs/) just works.
     ```
   - Minor: ensure the skills table in §4 and Getting Started steps mention Grok where natural.
   - Footer already correctly says "now with first-class Grok support" — leave or bump date.

3. **docs/projects/agent-bootstrap/decisions.md**
   - Update the ADR Index table (add row for ADR-006).
   - Append at the very end (before the final *Last updated*):
     ```
     ## ADR-006: First-Class Grok Support via .grok/ Packaging, Exporter, and Symlinks

     **Date**: 2026-05-19  
     **Status**: Accepted  
     **Deciders**: @tginter (implementation), Software Architect (doc plan)

     ### Context
     The agent-bootstrap hub's core value is "clone once, full multi-harness power everywhere with zero per-harness config." Previous harnesses (Claude via ~/.claude/agents + Task(), Cline via .clinerules, etc.) had dedicated integration points. Grok 4.3+ introduced its own conventional locations: `<repo_root>/.grok/skills/<name>/SKILL.md`, `.grok/agents/`, project-rules discovery of AGENTS.md, and the `task` subagent tool. Without packaging the hub's 11 skills + 5 roles into this layout, Grok users would still need manual steps — breaking the "first-class citizen" promise.

     ### Decision
     - Add a `.grok/` tree at repo root (committed).
     - Export the 11 skills using the existing `scripts/export_codex_skills.py` (one-line wording tweak for "Grok (or Codex)") producing thin SKILL.md frontmatter + full source copy under references/.
     - Create symlinks under `.grok/agents/` pointing back to `../../agents/*.md` (DRY, single source of truth).
     - Include empty `personas/` and `roles/` directories as forward-compatible placeholders for Grok's custom role/persona TOML+md discovery.
     - Update AGENTS.md (harness list + new detailed Grok subsection), manifest version, and memory-bank/ only.
     - Document maintenance (re-export + symlink) in AGENTS.md, CONTRIBUTING.md, and this ADR.
     - Treat the generated .grok/skills/.../references/source.md as copies (never hand-edit).

     ### Alternatives Considered
     - Hand-maintained duplicate Markdown in .grok/ (high drift risk, violates KISS/DRY).
     - Post-clone install script or git hook (adds friction; harnesses vary; against "zero config").
     - Make the exporter part of every plan-code-review finalize step (overkill for docs-only changes).
     - Ignore Grok (violates the universal harness-agnostic charter in projectbrief.md).

     ### Consequences
     **Positive**:
     - Grok users get identical experience: AGENTS.md loaded, 11 skills as `/...`, 5 agents spawnable by name, full memory-bank + docs/ + manifest awareness.
     - Symlinks + exporter = no duplication; canonical files stay authoritative.
     - Future-proofs the hub for any Grok persona/role extensions.
     - Self-hosting win: the hub used its own plan-code-review + memory-bank protocol + docs-protocol to land the feature.

     **Negative / Trade-offs / Risks**:
     - Contributors must remember the re-export step after editing skills/agents (mitigated by clear docs in multiple places and the plan-code-review workflow checklist).
     - Generated files bloat the repo (~2000 lines in the initial commit) — acceptable because they are thin + the value of instant Grok usability is high.
     - Empty dirs may confuse (documented here and in AGENTS.md).

     **Mitigations**: The exporter is simple, tested (`tests/test_export_codex_skills.py`), and the whole flow was verified with `grok inspect` in the originating session.
     ```

4. **Secondary consistency updates** (small, high-value):
   - ONBOARDING.md line ~22-27 area: After the Claude install-agents paragraph, add:
     ```
     **Grok users**: No install step required. The `.grok/skills/` and `.grok/agents/` directories (plus AGENTS.md project-rules) are discovered automatically the moment you open the repo in Grok. Skills appear as `/<name>`; roles are available to the `task` tool.
     ```
   - CONTRIBUTING.md under "1. Adding or Improving a Skill" and "2. Adding or Updating an Agent Role": append a bullet:
     ```
     - Re-export the Grok packaging afterwards (`python scripts/export_codex_skills.py --output-dir .grok/skills --force`) and refresh symlinks under `.grok/agents/` so Grok users receive the updates with zero manual steps. See the Grok subsection in AGENTS.md.
     ```
   - skills/INDEX.md (top, after the intro paragraph): Add one sentence:
     ```
     Grok users automatically receive all skills as slash commands (`/<skill-kebab-name>`) thanks to the `.grok/skills/` packaging committed in v0.4.0.
     ```
   - Light footer / date bumps only where a file currently claims a pre-v0.4.0 version and the content is being touched anyway (avoid churn on untouched files).

### Execution Process (Strict — plan-code-review workflow)
1. **PLAN** (this document): Architect writes plan to memory-bank/activeContext.md (this section) + progress.md. User must explicitly approve before any file edit.
2. **CODE / ACT** (Software Engineer):
   - Start by invoking memory-bank-protocol (read all 6 files).
   - For every documentation or ADR change, follow `skills/docs-protocol.md` (choose shared vs project docs, use proper ADR template, etc.).
   - Make the smallest possible, style-matching edits (use existing patterns, absolute paths in examples, > callouts for warnings, friendly/direct tone).
   - After all edits: full self-review (re-read every changed file + run `git diff`).
   - If any exporter or script touch is truly needed (unlikely), the write-tests TDD rule applies.
3. **REVIEW** (QA Critical Reviewer): Full critical pass using the expert-pr-review checklist (correctness, completeness, no duplication of source of truth, harness parity, style, future maintenance, security/none issues since docs). Recommend Approve / Request Changes.
4. **ITERATE** if needed.
5. **FINALIZE**: Update memory-bank/activeContext.md + progress.md with "Grok docs sync complete. All user and agent docs now reflect v0.4.0 Grok support." User confirmation before any commit.

### Verification Steps (in Act phase)
- Re-read all 6 memory-bank files + the edited docs.
- `git diff --stat` + spot-check key sections.
- Optionally run the exporter test suite.
- If Grok harness available: `grok inspect` (or equivalent) to confirm skills/agents still visible after any doc-only changes.
- Confirm no generated .grok/ file was edited by hand.

### Risks & Mitigations
- **Drift risk** between canonical skills/ and .grok/ copies: Mitigated by explicit maintenance steps in 3+ places + ADR.
- **Over-documentation**: Kept KISS — one new subsection, one ADR, small bullets elsewhere.
- **Date/version churn**: Only touch files we are already editing for content reasons.
- **User approval gate**: Explicit in the workflow; this plan itself is the gate.

### Next Action After User Approval
Engineer role takes over, loads this plan from activeContext, executes exactly.

**This plan was created while following every global rule: memory-bank mandatory read, subagent policy considered (none needed for pure planning), KISS, co-create with user, absolute paths, no destructive action, prioritize refactor/doc over new code.**

*End of proposed plan*

**Execution Complete (Act phase)**: 2026-05-19 — All items in the plan executed exactly by Software Engineer + inline QA Reviewer. README, AGENTS (new detailed Grok subsection), decisions.md (ADR-006), ONBOARDING, CONTRIBUTING, skills/INDEX updated per specs. Memory bank updated throughout for thread visibility. Self-review + critical QA passed (Approve).

**User approval received**: 2026-05-19 — "approved the changes. commit them and push them up to the remote." Proceeding to commit + push per explicit instruction (satisfies global rule). Final memory-bank record included in this commit.

## Recent Changes
- 2026-04-28 (v0.2.0): Added `docs/` directory with two-tier structure:
  - `docs/shared/` — team-wide standards (api-contracts, data-models, pipeline-overview, decisions with ADRs)
  - `docs/projects/agent-bootstrap/` — fully populated example project docs
- Added `skills/docs-protocol.md` — full playbook for creating/updating docs, ADR workflow, shared vs project distinction
- Updated `manifest.yaml` v0.2.0: replaced stale `wiki_sections` field with `docs_path`; added full field reference comment
- Updated `AGENTS.md`: added `## 6. Project Documentation (docs/)` section; fixed `## 7. Getting Started` numbering; replaced hardcoded machine paths in manifest example with `<REPO_ROOT>` placeholder
- Fixed `memory-bank/systemPatterns.md`: replaced stale `wiki/` component reference with `docs/`
- Fixed `CONTRIBUTING.md`: removed stale "Karpathy LLM Wiki" footer; added section 4 for adding project docs
- Fixed `README.md`: added `docs/` to "What's Inside"; fixed stale "Karpathy wiki" philosophy line; updated Contributing instructions to include `docs_path`
- Updated `skills/memory-bank-protocol.md`: added `memory-bank/ vs docs/` comparison table and decision rules

## Active Decisions
- **Two-layer documentation model**: `memory-bank/` = agent operational state (mandatory read every session); `docs/` = persistent technical reference (read on demand). These are complementary, never merge.
- **docs_path field**: Added to manifest.yaml as the agent navigation key to project technical docs.
- **docs/projects/agent-bootstrap/** serves as the canonical template for all future project doc folders.
- **ADR format**: Context / Decision / Alternatives Considered / Consequences (positive, negative, risks). Always append, never delete.
- **Machine-specific paths**: `<REPO_ROOT>` placeholder used in AGENTS.md examples; actual paths remain in manifest.yaml (user responsibility per ADR-005).

## Open Questions
- None critical. Ready for team use and further project additions.

## Current Status
**v0.2.0 complete.** All gaps identified in audit have been addressed:
- ✅ `docs/` directory fully created with shared/ and projects/agent-bootstrap/
- ✅ `skills/docs-protocol.md` created
- ✅ `manifest.yaml` updated (wiki_sections → docs_path, v0.2.0)
- ✅ `AGENTS.md` updated (new section 6, fixed numbering, placeholder paths in example)
- ✅ All stale wiki references cleaned up
- ✅ `memory-bank-protocol.md` updated with docs/ vs memory-bank/ guidance

**v0.3.0 (2026-04-29) — Harness Compatibility Audit:**
- ✅ `.clinerules` — created/updated: bootstraps Cline, Roo Code, Kilocode into hub context
- ✅ `.openhands_instructions` — created: auto-loaded by OpenHands; points to AGENTS.md
- ✅ `manifest.template.yaml` — created: team-shareable template with `<YOUR_LOCAL_PATH>` placeholders
- ✅ `.gitignore` — updated: `manifest.yaml` now gitignored (local paths stay local)
- ✅ `AGENTS.md` — updated: per-harness setup for Claude/Cline/Kilocode/OpenHands/Cursor; manifest template step; `docs-protocol.md` added to skill list; version → 0.2.0
- ✅ `README.md` — updated: Quick Start with manifest template; `.clinerules`/`.openhands_instructions` in What's Inside; per-harness Compatibility list; version → 0.2.0
- ✅ `ONBOARDING.md` — updated: Step 2 now explains manifest template copy+sed pattern
- ✅ Stale wiki refs fixed: `projectbrief.md`, `software-engineer.md`, `memory-bank-protocol.md` (version footer → 1.1/v0.2.0)
- ✅ `CONTRIBUTING.md` — fixed: step numbering bug (1,2,3,4,7 → 1,2,3,4,5)

**Next**: Team members can add their projects using the template in `docs/projects/agent-bootstrap/` and `skills/docs-protocol.md` for guidance. No further critical gaps identified.

---

## v0.4.0 — Grok Native Packaging (2026-05-19)

**What was done in this session (initialization + import per user request):**

- Initialized the hub for Grok 4.3+ by reading AGENTS.md + all 6 memory-bank files at session start (per mandatory protocol).
- Created `.grok/` project-scoped configuration directory (standard location per Grok docs for skills, agents, roles/personas).
- **Skills**: Used the hub's own `scripts/export_codex_skills.py` (with a one-line compatibility note improvement) to export all 11 skills into `.grok/skills/<name>/SKILL.md + references/source.md`. The thin SKILL.md files provide trigger descriptions so Grok can auto-invoke or let users run `/plan-code-review-workflow`, `/expert-pr-review`, `/memory-bank-protocol`, etc. The full authoritative playbooks live in the existing `skills/*.md` (referenced from the exported wrappers).
- **Agents / Subagents**: Created symlinks under `.grok/agents/` to the 5 canonical role definitions. Grok now auto-discovers them as project agents: `Engineer`, `Architect`, `QAReviewer`, `SecurityReviewer`, `UIUXEngineer`. These can be spawned via the `task` tool with `subagent_type` matching the `name:` in their frontmatter.
- Verified end-to-end with `grok inspect` (shows both AGENTS.md as loaded project instructions + all 11 skills + 5 agents under the agent-bootstrap repo).
- Ran the exporter's own unit tests (`tests/test_export_codex_skills.py`) — all pass.
- Updated this `activeContext.md` and `progress.md` to record the contribution.

**Impact**: The agent-bootstrap hub is now a first-class, zero-config citizen for Grok users (just like for Claude Code, Cline, Cursor, etc.). Anyone who clones the repo and opens it in a Grok-powered environment immediately gets the full skill catalog and reusable agent personas without extra steps. AGENTS.md is auto-loaded via Grok's project-rules mechanism.

**Files changed**:
- `scripts/export_codex_skills.py` (minor wording for multi-harness clarity)
- New: `.grok/skills/...` (11 exported skill packages)
- New: `.grok/agents/` (5 symlinks to the role .md files)
- `memory-bank/activeContext.md`, `memory-bank/progress.md` (this record)

This change was performed while strictly following the hub's own global rules (absolute paths, memory-bank protocol, self-review, no destructive actions, explicit user instruction for the commit).
