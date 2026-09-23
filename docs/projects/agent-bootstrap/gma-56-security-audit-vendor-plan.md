# GMA-56 — Vendor Cloudflare `security-audit` Skill into agent-bootstrap (Opt-In)

> **Scope**: This is a **plan-only** document. It names every file to add or patch for the implement-track PR, with concrete house paths verified against this repo's real files and scripts (not assumed or invented). **No vendor code, skill tree, validator script, or fixture is created in this PR.** No full security audit of `agent-bootstrap` is run. GMA-54 is not opened, read, or touched.

**Task name**: `gma-56-security-audit-vendor` (stable for this thread's life; reused on the spec-gate card below).

**Linear**: [GMA-56 — Vendor Cloudflare security-audit skill into agent-bootstrap (opt-in)](https://linear.app/gman-personal-projects/issue/GMA-56/vendor-cloudflare-security-audit-skill-into-agent-bootstrap-opt-in)

**Author model**: claude-sonnet-5. **Next**: Blair re-passes this revised plan against all six blockers below. **No implement-track work starts until CoS records a literal Blair CLEAR/APPROVE** on the spec-gate card at the end of this document, and CoS assigns the implement PR.

**Status**: Draft, plan-track only. Revision addressing Blair's six numbered blockers verbatim, plus SHOULD_FIX items. Not merged.

---

## 1. Status / Gate

**PLAN ONLY.** Held until:
1. Blair grok-4.6 (or the reviewing model) issues a literal **CLEAR** (or **Approve**) on the spec-gate card at the end of this document — "looks good" / "ok" / silence do not count (`skills/reply-contract/SKILL.md` "Gate cards").
2. CoS assigns the implement-track PR to an engineer.

No file under `skills/security-audit/`, no `scripts/validate_security_audit_vendor.py`, no `tests/test_security_audit_vendor_cjs.py`, and no edit to `scripts/validate_pstack_skill.py`, `scripts/export_codex_skills.py`, `scripts/install-grok.sh`, `agents/security-reviewer.md`, `AGENTS.md`, `skills/INDEX.md`, `skills/expert-pr-review/SKILL.md`, `skills/blast-radius/SKILL.md`, or any of the five rule files exists yet. This document is the only artifact this PR ships.

---

## 2. Goal + Non-Goals

**Goal**: Produce an implement-ready plan to vendor Cloudflare's `security-audit-skill` (MIT) into this hub as a new, **opt-in**, narrowly-triggered skill — `skills/security-audit/` — with a house-authored hub-entry `SKILL.md`, a full attribution trail, mechanical companion pointers to `expert-pr-review` and `blast-radius`, a guidance-by-default posture that never silently launches the upstream six-phase full-audit workflow, and house validators proving the vendored `.cjs` files still run.

**Non-goals** (this PR):
- Vendoring any file under `skills/security-audit/`.
- Writing `scripts/validate_security_audit_vendor.py`, `tests/test_security_audit_vendor_cjs.py`, or any fixture.
- Editing `scripts/validate_pstack_skill.py`, `scripts/export_codex_skills.py`, `scripts/install-grok.sh`, `agents/security-reviewer.md`, `AGENTS.md`, `skills/INDEX.md`, `skills/expert-pr-review/SKILL.md`, `skills/blast-radius/SKILL.md`, or the five rule files.
- Running a security audit — full or partial — of `agent-bootstrap` itself.
- Touching GMA-54 in any way (not opened, not read, not referenced beyond this line).
- Adding an ADR to `docs/projects/agent-bootstrap/decisions.md` (see §1's reasoning below — decisions.md's six existing ADRs are all `Status: Accepted`; nothing here is accepted yet, so no ADR row is added by this plan-track PR — this matches the precedent of `hoh-schema-steal-plan.md` and `mem0-lessons-plan.md`, neither of which added a decisions.md row at plan-track time).

---

## 3. Upstream Pin + License/NOTICE

**Upstream**: [`cloudflare/security-audit-skill`](https://github.com/cloudflare/security-audit-skill) (MIT).

**Pinned SHA**: `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` — verified live against the GitHub API during this plan revision:

```text
$ curl -sL "https://api.github.com/repos/cloudflare/security-audit-skill/commits/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8" | ...
sha: c1c8a8c1471069fb0e188eeaff69b8e8db6564a8
date: 2026-09-14T19:28:54Z
message: Clarify guidance and full audit modes

$ curl -sL "https://api.github.com/repos/cloudflare/security-audit-skill/commits?sha=main&per_page=1" | ...
latest tip sha: c1c8a8c1471069fb0e188eeaff69b8e8db6564a8   # confirms this IS the tip of main, not a stale pin

$ curl -sL "https://api.github.com/repos/cloudflare/security-audit-skill" | ...
default_branch: main
license: MIT
```

**Upstream tree at this SHA** (verified via the GitHub Trees API, matches the task brief exactly — `SKILL.md` + 13 domain packs + 2 `.cjs` validators + their 2 `.test.cjs` files + `report-schema.json` + `README.md` + `LICENSE`, all under `skills/security-audit/`):

```
LICENSE
README.md
skills/security-audit/
  SKILL.md
  RECONNAISSANCE.md            HUNTING.md                  ATTACK-CLASSES.md
  MEMORY-SAFETY-AND-BINARY.md  AI-AND-LLM.md                WEB-PROTOCOL-AND-AUTH.md
  CLIENT-SIDE.md               SUPPLY-CHAIN-AND-RELEASE.md  CLOUD-AND-DEPLOYMENT.md
  PROTOCOLS-RPC-AND-MESSAGING.md  RESOURCE-EXHAUSTION-AND-AVAILABILITY.md
  DATA-ISOLATION-AND-LIFECYCLE.md DESKTOP-MOBILE-AND-LOCAL-IPC.md VALIDATION-AND-REPORTING.md
  report-schema.json
  validate-findings.cjs            validate-findings.test.cjs
  validate-coverage-ledger.cjs      validate-coverage-ledger.test.cjs
```

**License**: MIT, `Copyright (c) 2025-2026 Cloudflare, Inc.` — verified by fetching `LICENSE` at the pinned SHA.

**House constitution compliance** (`docs/shared/constitution.md` Article 5, "No vendored runtime from unlicensed sources"): Article 5 restricts vendoring *from repositories with no LICENSE* (its own worked example is `unclebob/swarm-forge`) to ideas-only, no-file-copying. Cloudflare's `security-audit-skill` carries a real MIT LICENSE, so file-level vendoring with attribution — the opposite case from Article 5's example — is explicitly the compliant path here, not an exception to it.

**Implement-track artifacts (named now, not created in this PR)**:
- `skills/security-audit/references/cloudflare/LICENSE` — the upstream MIT LICENSE, vendored verbatim, byte-for-byte from the pinned SHA.
- `skills/security-audit/references/cloudflare/NOTICE.md` — house-authored, containing at minimum:
  ```markdown
  # NOTICE

  Vendored from: https://github.com/cloudflare/security-audit-skill
  Pinned commit:  c1c8a8c1471069fb0e188eeaff69b8e8db6564a8
  Commit date:    2026-09-14T19:28:54Z
  Vendored on:    <implement-track PR date>
  License:        MIT (Copyright (c) 2025-2026 Cloudflare, Inc.) — see ./LICENSE in this directory
  ```

---

## 4. Intended Tree Layout (Hub SKILL.md vs. References Companion)

```
skills/security-audit/
  SKILL.md                              # NEW, house-authored — the hub entry (Blocker 1)
  black-box-run.json                    # captured after the live-gate fixtures below pass
  fixtures/
    vendor-structure-check/case.json    # runs scripts/validate_security_audit_vendor.py
    cjs-tests-pass/case.json            # runs tests/test_security_audit_vendor_cjs.py
  references/
    cloudflare/                        # the entire vendored upstream tree, one unit
      LICENSE
      NOTICE.md
      SKILL.md                          # upstream's own SKILL.md, vendored as companion — NEVER the hub entry
      README.md
      RECONNAISSANCE.md  HUNTING.md  ATTACK-CLASSES.md  ... (all 13 domain packs, verbatim)
      report-schema.json
      validate-findings.cjs  validate-findings.test.cjs
      validate-coverage-ledger.cjs  validate-coverage-ledger.test.cjs
```

Section §5 Blocker 1 covers why the upstream `SKILL.md` must never be the hub entry. Section §5 Blocker 2 covers why the vendored tree is nested one level deeper (`references/cloudflare/`, not a flat `references/cloudflare-SKILL.md`-style naming) and the one exporter-adjacent fix this placement requires.

---

## 5. Numbered Blair Blockers 1–6 — Requirements + Concrete Implement Checklist

### Blocker 1 — Pin + attribution + hub entry shape

**Requirement** (verbatim from the task): Pin tip `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`. Vendor Cloudflare LICENSE + house NOTICE (URL + SHA + date). House wrapper `SKILL.md` is the hub entry. Upstream `SKILL.md` renamed as vendor companion. Do **not** install upstream `SKILL.md` as hub entry (no version; auto-matches security questions).

**Why this matters, verified against the actual upstream file** (fetched at the pinned SHA):

```yaml
---
name: security-audit
description: Security guidance and vulnerability review for codebases, APIs, services,
  CLI tools, libraries, and daemons. Use for security questions, focused reviews,
  vulnerability research, security audits, or pen tests. Run the complete workflow only
  for explicit codebase audit or pen-test requests, full/comprehensive/end-to-end
  reviews, or requested report artifacts.
---
```

This frontmatter has **no `version:` field** (this hub requires `name`/`description`/`version` — see `skills/INDEX.md` "Adding a New Skill" step 1) and its `description:` is written to auto-match on bare phrases like "security questions" and "focused reviews" — exactly the phrasing `expert-pr-review` and `blast-radius` already own in this hub. Installing this file verbatim as `skills/security-audit/SKILL.md` would make it fire on generic PR-review and blast-radius-style prompts, which is the collision Blocker 3's denylist exists to prevent.

**Implement checklist**:
1. Author `skills/security-audit/SKILL.md` from scratch, following this hub's house frontmatter shape (`name`, `description`, `version`) and house sections (`**Purpose**`, `**Trigger**`, `**Do not use for**`, `## Companions`, `**Verification**` — the same shape `scripts/validate_pstack_skill.py`'s `HOUSE_SECTIONS` already enforces for other ported skills, reused here by convention, not by that script's `PSTACK_SKILL_NAMES` gate since this is not a pstack port). Its `description:` frontmatter must be the narrow allowlist from Blocker 3, not upstream's broad one.
2. Vendor upstream's `LICENSE` verbatim to `skills/security-audit/references/cloudflare/LICENSE`.
3. Author `skills/security-audit/references/cloudflare/NOTICE.md` with the exact URL/SHA/date/license block from §3 above.
4. Vendor upstream's own `SKILL.md` verbatim (unmodified) to `skills/security-audit/references/cloudflare/SKILL.md` — a companion reference, never linked from `skills/INDEX.md`, `AGENTS.md`, the exporter's `SkillConfig`, or any rule file as if it were the hub entry.
5. House validator (Blocker 6) mechanically asserts the hub `SKILL.md` frontmatter has all three required fields and that its `description:` does **not** contain the literal upstream broad-match phrase set — this is a hard-fail check, not a convention note.

---

### Blocker 2 — Vendor tree placement

**Requirement**: Prefer vendor tree under `skills/security-audit/references/` (grill-with-docs dual-home pattern). OR extend `export_codex_skills` + install-grok then prove with `assertIn` SkillConfig + dual-home test. Prefer dual-home unless exporter extension is cleaner and tested. Plan must pick one with rationale after investigating exporter behavior for `references/`.

**Decision: dual-home, under `skills/security-audit/references/cloudflare/`** (one subdirectory deeper than the flat `references/*.md` shape `grill-with-docs` uses), **plus one small, explicitly-scoped fix to `scripts/install-grok.sh`** — not an exporter extension. Rationale below is derived from actually running both scripts against a synthetic nested-reference skill during this plan revision, not from reading the code alone.

**What `scripts/export_codex_skills.py` actually does with `references/`** (verified by invocation):
- `export_skills()` never copies a source skill's `references/*` files into the output on a fresh export — `load_source_skills()` only reads `SKILL.md` as a string. The only thing written under `<output>/<skill>/references/` on export is the generated `source.md`.
- `collect_preserved_files()` only protects files **already present in the output directory** across a subsequent `--force` re-export (this is the existing REPEAT-lock fixture's whole point — see `skills/triage-review-feedback/fixtures/repeat-exporter-dropped-references/`). It walks recursively (`skill_dir.rglob("*")`), so once a nested file exists in the output, a `--force` re-export **does** preserve it byte-for-byte, at any depth. Verified live:
  ```text
  $ python3 -c "... export_skills(nested-scratch-skill-source, out, force=True) ..."
  # First export with no prior output: only SKILL.md + references/source.md are written.
  # The source's own references/top.md and references/vendorsub/nested.md are NOT copied.
  ```
- So the exporter alone is not what populates a skill's extra reference files in `.grok/skills/` — ever.

**What actually populates them today**: `scripts/install-grok.sh`'s "Restoring extra skill references" step, which runs *after* the exporter and copies files from the **source** `skills/<name>/references/*` into the **output** `references/`. Verified this loop is **one level deep only**:
```bash
for ref in "${skill_src}/references"/*; do
  [[ -f "$ref" ]] || continue     # <- silently SKIPS directories
  base="$(basename "$ref")"
  [[ "$base" == "source.md" ]] && continue
  cp "$ref" "${dest_ref}/${base}"
done
```
Confirmed this is the real mechanism, not a hypothesis: the committed `.grok/skills/grill-with-docs/references/{adr-format.md,context-format.md}` and `.grok/skills/architect/references/{rationale-template.md,design-red-flags.md,runner-prompt.md}` exist only because a past `install-grok.sh --local` run copied those flat files and the result was committed.

**The gap this plan must fix**: `skills/security-audit/references/cloudflare/` is a **directory**, not a file, sitting directly under `references/`. The loop above's `[[ -f "$ref" ]]` check would skip it entirely — none of the vendored LICENSE, NOTICE, upstream SKILL.md, domain packs, or `.cjs` files would ever reach `.grok/skills/security-audit/references/cloudflare/...` on any `install-grok.sh --local` or plugin install, even though the exporter's own preservation logic (`collect_preserved_files`, already recursive) would happily carry them forward once they exist.

**Why dual-home + a one-line `install-grok.sh` fix beats an `export_codex_skills.py` extension**: the exporter's `SkillConfig` model is built for generating a Grok-native thin-wrapper `SKILL.md` + `source.md` per skill — it has no concept of "also copy this vendor subtree," and inventing one (a new `SkillConfig` field, new export logic, its own test) is strictly more surface than fixing `install-grok.sh`'s existing restore loop to recurse (e.g., swap the one-level glob for a recursive walk that still excludes `source.md`, or `cp -r` each `references/*` entry). The fix is scoped to the one script that already does this job for every other skill's extra reference files — it is not a new mechanism.

**Implement checklist**:
1. Vendor the full Cloudflare tree under `skills/security-audit/references/cloudflare/` (§3, §4).
2. Patch `scripts/install-grok.sh`'s restore loop to recurse into subdirectories of `references/` (excluding `source.md` at any depth), so `references/cloudflare/**` round-trips into `.grok/skills/security-audit/references/cloudflare/**`.
3. Add a dual-home test (new, alongside `tests/test_export_codex_skills.py` or a new `tests/test_install_grok_nested_references.py`) proving, by actual invocation (not by reading the script):
   - `export_codex_skills.py --force` preserves a nested `references/<x>/<y>.md` byte-for-byte across a re-export (already true today — this test locks it, does not fix anything).
   - `install-grok.sh --local --force` (or an equivalent direct call into its restore logic once extracted/testable) copies a nested `references/cloudflare/<file>` into the output — false today, must go green after the fix.
4. Do not extend `SkillConfig` or `export_codex_skills.py`'s export logic itself — no change needed there per the investigation above.

---

### Blocker 3 — Triggers: allowlist / denylist

**Requirement**: Allowlist only: `security-audit`, "run the Cloudflare security audit", full/comprehensive/pen-test asks. Denylist: "security review", "review this PR", "what could this break", generic find-vulnerabilities. Must update: frontmatter, SkillConfig, INDEX Trigger, AGENTS.md §4, five rule lists. Rewrite `security-reviewer.md` standalone-audit sentence so it does not launch six-phase workflow. Explicit: not a substitute for `expert-pr-review` / `blast-radius`.

**Verified the five rule files are exactly five** (per `skills/INDEX.md`'s own "Adding a New Skill" step 5, and confirmed by directory listing in this checkout): `.cursorrules`, `.clinerules`, `.kilocoderules`, `.openhands_instructions`, `.cursor/rules/agent-bootstrap.mdc`. `CLAUDE.md` is a one-line pointer to `AGENTS.md` with no trigger list of its own — it is not a sixth rule file and is not touched.

**Found the standalone-audit sentence** — it exists in **two** files, not one, both needing the same rewrite (they duplicate each other by this hub's own convention of mirroring each `agents/*.md` role into `AGENTS.md` §3):
- `agents/security-reviewer.md`, under "**When to Activate**": *"...Can also be activated directly for standalone security audits."*
- `AGENTS.md` §3 (security-reviewer.md role summary), same sentence verbatim.

**Implement checklist**:
1. `skills/security-audit/SKILL.md` frontmatter `description:` — narrow to the allowlist only, e.g.: *"Use only for the literal request 'security audit', 'run the Cloudflare security audit', or an explicit full/comprehensive/end-to-end/pen-test request against a codebase. Do NOT use for generic 'security review', 'review this PR', 'what could this break', or unscoped find-vulnerabilities requests — those are `expert-pr-review` / `blast-radius`."* Add a `**Do not use for**` section (house convention) listing the denylist phrases with pointers to `expert-pr-review` and `blast-radius`.
2. `scripts/export_codex_skills.py` — new `SkillConfig(security-audit=...)` entry whose `trigger_summary` restates the same narrow allowlist (see Blocker 6 / SHOULD_FIX for `quick_start` content).
3. `skills/INDEX.md` — new `### security-audit` entry; its **Trigger** line uses the same allowlist wording, explicitly excluding the denylist phrases.
4. `AGENTS.md` §4 "Other Key Skills" table — one new row, same allowlist wording.
5. All five rule files — one new trigger line each, matching their existing per-file format (bullet list in `.cursorrules`/`.clinerules`/`.kilocoderules`/`.openhands_instructions`; markdown table row in `.cursor/rules/agent-bootstrap.mdc`).
6. Rewrite the standalone-audit sentence in **both** `agents/security-reviewer.md` and `AGENTS.md` §3 to something in this shape: *"Can also be activated directly for a focused, guidance-mode security review of a diff or question. A full Cloudflare-style audit (six phases, sandboxed execution, report artifacts) is never launched implicitly by this persona — load `skills/security-audit/SKILL.md` explicitly and only after an explicit full-audit/pen-test request (see that skill's guidance-vs-full-audit gate)."* This removes the implication that activating `SecurityReviewer` launches the six-phase workflow, while preserving the persona's existing focused-review capability.
7. The "not a substitute for `expert-pr-review` / `blast-radius`" requirement is satisfied structurally, not by a duplicated sentence — see Blocker 4, whose bidirectional `**Do not use for**` + `## Companions` sections carry this both ways and are mechanically checked.

---

### Blocker 4 — Companions + live-gate order

**Requirement**: `COMPANION_PAIRS` (or house equivalent): `security-audit` ↔ `expert-pr-review` and `security-audit` ↔ `blast-radius`. `blast-radius` is **not** grandfathered — editing its `SKILL.md` requires `black-box-run.json` recapture. Do **not** add `security-audit` to `GRANDFATHERED_SKILLS`. Order: live-gate first, then INDEX/AGENTS/rules/exporter.

**Found the exact house mechanism — it already exists, under a different name than expected**:

`COMPANION_PAIRS` is a real, already-shipped tuple in `scripts/validate_pstack_skill.py`, not a name that needs inventing:
```python
COMPANION_PAIRS: tuple[tuple[str, str], ...] = (
    ("show-me", "show-me-your-work"),
    ("expert-pr-review", "interrogate"),
)
```
`validate_companion_reverse_pointers_for(skill_name)` mechanically checks, for every pair containing `skill_name`, that **both** sides' `**Do not use for**` section names the other skill and **both** sides' `## Companions` table has a row for the other — this already works for skill names outside `PSTACK_SKILL_NAMES` (the function only requires membership in the pairs, not in the pstack set), so `security-audit` can use this exact mechanism with zero new code, only two new tuple entries.

`tests/test_pstack_skills.py::test_companion_reverse_pointers_via_validator` already calls the **no-argument** `validate_companion_reverse_pointers()`, which iterates the **entire** `COMPANION_PAIRS` tuple — so extending the tuple automatically extends this existing test's coverage to the two new pairs, with no new test file required for the reverse-pointer check itself (a same-shape pair of hand-written assertions, mirroring `test_expert_pr_review_companion_points_at_interrogate`, is still added for `security-audit` specifically — see checklist).

**`GRANDFATHERED_SKILLS` — found at `scripts/index_skills.py`, confirmed closed**: it is pinned by *exact equality* in `tests/test_index_live_binding.py::test_grandfathered_skills_is_frozen_at_the_original_twenty` against a second, hand-copied `ORIGINAL_GRANDFATHERED_SKILLS` — any edit to the production set without updating the test's pinned copy in the same diff fails that test. This set does **not** include `security-audit` and this plan does not add it; it also does not include `blast-radius` (verified: `blast-radius` is absent from both the production 20-name set and the pinned test copy) — confirming `blast-radius` is genuinely live-gated today, not grandfathered, which is exactly what makes the next paragraph true.

**Proved the `blast-radius` recapture requirement, not just asserted it**:
```text
$ python3 scripts/check_skill_live.py blast-radius
live-eligible: run record verdict is pass and matches the current SKILL.md
```
`check_skill_live.py`'s `skill_sha256()` hashes only `skill_dir / "SKILL.md"`. Any edit to `skills/blast-radius/SKILL.md` — including adding one `## Companions` row and one `**Do not use for**` line for `security-audit` — changes that hash, so `check_skill_live.py` will report the existing `skills/blast-radius/black-box-run.json` stale (`skill_sha256` mismatch) immediately after the edit, per the exact mechanism documented in `skills/black-box-agent-qa/SKILL.md` "Hard Limits" and `scripts/check_skill_live.py`'s own docstring. `expert-pr-review`, by contrast, **is** in `GRANDFATHERED_SKILLS` — its `SKILL.md` can be edited with no live-gate consequence at all, since `check_skill_live.py` is never consulted for grandfathered names.

**Implement checklist** (numbers match the required order — live-gate first):
1. Vendor the tree + author `skills/security-audit/SKILL.md` (Blockers 1–2).
2. Add `("security-audit", "expert-pr-review")` and `("security-audit", "blast-radius")` to `COMPANION_PAIRS` in `scripts/validate_pstack_skill.py`.
3. Add a `## Companions` row + `**Do not use for**` line for `security-audit` to `skills/expert-pr-review/SKILL.md` (no live-gate consequence — grandfathered) and to `skills/blast-radius/SKILL.md` (live-gate consequence — see next step).
4. **Recapture `skills/blast-radius/black-box-run.json`**: re-run its existing fixture, `python3 scripts/run_black_box_fixture.py --fixture skills/blast-radius/fixtures/skill-structure-check --skill blast-radius --out skills/blast-radius/black-box-run.json`, and confirm `python3 scripts/check_skill_live.py blast-radius` exits `0` again before merging.
5. Add `security-audit`'s own `## Companions` table (rows for `expert-pr-review`, `blast-radius`) and `**Do not use for**` section (pointing back at both, plus the Blocker 3 denylist).
6. Write `scripts/validate_security_audit_vendor.py` + its fixture, and `tests/test_security_audit_vendor_cjs.py` + its fixture (Blocker 6).
7. Run `scripts/run_black_box_fixture.py` for each of `security-audit`'s two fixtures, capturing `skills/security-audit/black-box-run.json` with `"verdict": "pass"`.
8. **Live-gate checkpoint**: `python3 scripts/check_skill_live.py security-audit` must exit `0`. Do not proceed past this point until it does.
9. **Only after step 8 passes**: add the `skills/INDEX.md` entry, the `AGENTS.md` §4 row + §3 sentence rewrite, the five rule-file trigger lines, and the `scripts/export_codex_skills.py` `SkillConfig` entry (Blocker 3), then the `scripts/install-grok.sh` fix + re-export (Blocker 2), then the `agents/security-reviewer.md` rewrite (Blocker 3).
10. Confirm `python3 -m unittest discover -s tests` is still green end to end (123 existing tests today + the new ones from this plan), and `tests/test_index_live_binding.py::test_every_non_grandfathered_index_entry_is_live` passes with `security-audit` now listed and live.

---

### Blocker 5 — Sandbox / guidance default

**Requirement**: Guidance default (no six phases / output dir / artifacts). Full audit only after explicit full-audit/pen-test ask **and** capability-check of the four Cloudflare Universal execution-safety controls before any target-controlled build/test/browser/fuzzer; else `needs_validation` only. Never treat "we have a sandbox" as authorization. Distinct from Cursor/Claude/Grok sandbox and from `expert-pr-review` checkout+build. Name the four controls by reading upstream SKILL.md/README at the pinned SHA.

**The four controls, read directly from upstream `SKILL.md` at the pinned SHA** (section literally titled "## Universal execution safety," applying "in both operating modes"):
1. **No external network** — "no external network; use only an isolated loopback namespace when the check needs local client/server traffic."
2. **Empty, explicitly allowlisted environment** — "an empty environment populated from an explicit allowlist with safe values, with scratch-local `HOME`, temporary directories, and caches."
3. **Read-only target and toolchain, writes confined to `scratch/`** — "a read-only target and toolchain, with the target-controlled process able to write only inside its assigned `scratch/` directory."
4. **Explicit resource limits** — "explicit low CPU, memory, process, file-size, disk, and wall-clock limits."

Upstream's own text is explicit about the consequence of missing any control: *"If every control cannot be enforced, do not execute target code: report the missing sandbox capability as a needs-validation blocker and give a safe validation plan."* — this is the literal source of the "else `needs_validation` only" requirement; it is upstream's own verdict vocabulary (`confirmed` / `needs_validation` / `rejected`), not a house invention.

Upstream is also explicit about mode: *"This skill is guidance by default. Loading it does not authorize the complete audit workflow or file creation."* — guidance mode "does not automatically run all six phases, create an output directory, or write audit artifacts." Full audit mode requires an explicit ask (*"audit or pen-test a codebase," "full, comprehensive, or end-to-end security review," or "report artifacts"*) and, before touching target code, the full four-control capability check above.

**Distinctness this plan must state explicitly** (all three are genuinely different things, and the house wrapper must not conflate any pair):
- **Cursor/Claude/Grok's own agent sandbox** (the harness's own tool-execution isolation) is not the same as, and does not by itself satisfy, the four Universal execution-safety controls above — those four are about the *target-controlled process under audit* (no network, allowlisted env, scratch-only writes, resource limits), not about the harness's own general tool-call safety.
- **`expert-pr-review`'s checkout+build step** (Step 3 of that skill) builds and tests the actual PR branch in the normal development environment specifically to validate the change — it does not (and is not meant to) provide isolated-from-network, allowlisted-env, scratch-write-only, resource-limited execution. Running `expert-pr-review`'s build/test does not satisfy this capability check.
- **A bare assertion of "we have a sandbox"** is not itself a pass — the house wrapper must require a check against each of the four named controls specifically, not a general claim.

**SHOULD_FIX tie-in** (upstream's own default output path is already outside the target): upstream's "Full audit setup" section defaults the output directory to `~/security-audit-skill/<repo-name>/run-<N>` — outside the target repo by default — and only allows an in-repo directory when the user explicitly selects one **and** it is confirmed version-control-ignored. The house wrapper should restate/inherit this default rather than weaken it (see §6 SHOULD_FIX).

**Implement checklist**:
1. `skills/security-audit/SKILL.md` states guidance-mode-by-default in its own words near the top (mirroring, not copying verbatim, upstream's "guidance by default" framing), and states the full-audit trigger condition (explicit full-audit/pen-test/comprehensive-review/report-artifact ask) matches Blocker 3's allowlist.
2. Before Full audit mode executes any target-controlled build/test/process/browser/fuzzer, the house wrapper requires an explicit capability check against the four named controls (network isolation, allowlisted environment, scratch-only writes, resource limits) — cite them by these names, pointing to `references/cloudflare/SKILL.md`'s "Universal execution safety" section for the authoritative detail rather than re-deriving it.
3. If any control cannot be confirmed, the result stays `needs_validation` (upstream's own term) — the house wrapper does not invent a different fallback verdict.
4. Explicitly name the three distinctions above (harness sandbox vs. these four controls; `expert-pr-review` build/test vs. these four controls; assertion vs. verified capability check) so an implementer cannot conflate them.
5. House validator (Blocker 6) asserts the hub `SKILL.md` text names all four controls and the `needs_validation` fallback — this is a mechanical check, not a review-only note.

---

### Blocker 6 — House validators for `.cjs`

**Requirement**: House Python validator (wrapper/opt-in/attribution/companions). Python test that execs `node --test` on both `*.test.cjs` (missing Node = fail, not skip). Pin Node ≥ 18. Note: `check_skill_live` hashes only `SKILL.md` — Markdown-only fixture is insufficient for dropped `.cjs`.

**Confirmed `check_skill_live.py` hashes only `SKILL.md`** — read directly from the script:
```python
def skill_sha256(skill_dir: Path) -> str | None:
    """sha256 of the skill's current SKILL.md, or None if it does not exist."""
    skill_md = skill_dir / "SKILL.md"
    ...
```
No other file under a skill directory participates in the staleness hash. This means a `black-box-run.json` captured only against `skills/security-audit/SKILL.md` text proves nothing about the two vendored `.cjs` files continuing to execute correctly — a completely separate, real-execution check is required, which is exactly what this blocker asks for.

**Node availability in this environment, verified**: `node --version` → `v22.14.0` (≥ 18, satisfies the pin). The environment used to write and, later, capture the implement-track live-gate has a suitable Node; the new test must still assert the version explicitly rather than assuming it.

**Implement checklist**:
1. **New house Python validator**, `scripts/validate_security_audit_vendor.py`, modeled on `scripts/validate_pstack_skill.py`'s structure-check style but standalone (not added to that script's `PSTACK_SKILL_NAMES`, since `security-audit` is a vendor-of-a-real-upstream skill, not a pstack port). It checks, at minimum:
   - `skills/security-audit/SKILL.md` has valid frontmatter with `name`/`description`/`version`, and `description` does not contain the upstream broad-match phrasing (Blocker 1).
   - `skills/security-audit/SKILL.md` has `**Do not use for**` and `## Companions` sections (Blocker 3/4 structure).
   - Opt-in language is present (e.g., the wrapper states it is not invoked automatically by `plan-code-review-workflow`, `expert-pr-review`'s Step 4 `SecurityReviewer` spawn, or any always-on pipeline).
   - `skills/security-audit/references/cloudflare/NOTICE.md` exists and contains the pinned SHA `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` and the upstream URL.
   - `skills/security-audit/references/cloudflare/LICENSE` exists and contains `MIT`.
   - Guidance-default + four-controls + `needs_validation` fallback language is present (Blocker 5).
2. **Fixture**: `skills/security-audit/fixtures/vendor-structure-check/case.json` running `["python3", "scripts/validate_security_audit_vendor.py", "security-audit"]`, expecting exit `0`.
3. **New Python test**, `tests/test_security_audit_vendor_cjs.py`, that:
   - Resolves `node` via `shutil.which("node")`. If `None`: `self.fail(...)`, never `self.skipTest(...)` — a missing Node is a failure, per the requirement, not a soft skip.
   - Parses `node --version` and asserts the major version is `>= 18`; fails (does not skip) if lower.
   - Runs `node --test skills/security-audit/references/cloudflare/validate-findings.test.cjs` and `node --test skills/security-audit/references/cloudflare/validate-coverage-ledger.test.cjs` (both files, per the requirement — one test asserting both, or two focused test methods, either is acceptable as long as both are actually executed) and asserts each subprocess exits `0`.
4. **Fixture**: `skills/security-audit/fixtures/cjs-tests-pass/case.json` running `["python3", "-m", "unittest", "tests.test_security_audit_vendor_cjs", "-v"]`, expecting exit `0` — this is the fixture that actually re-proves the `.cjs` files run, independent of and in addition to the `SKILL.md`-hash-based live gate.
5. Note explicitly in `skills/security-audit/SKILL.md` (or its NOTICE) that `check_skill_live.py`'s staleness hash covers `SKILL.md` only — a future edit to the vendored `.cjs`/domain-pack files does not by itself invalidate the `black-box-run.json`, so the `cjs-tests-pass` fixture must be re-run manually whenever `references/cloudflare/` content changes, not only when `SKILL.md` changes. This is a documented house gap, not something this plan silently papers over.

---

## 6. SHOULD_FIX (Blair)

- **Prefer gitignored output outside target.** Upstream's own default (`~/security-audit-skill/<repo-name>/run-<N>`) already lives outside the target repo. The house wrapper restates this as the default and, if an in-repo output directory is ever explicitly selected, requires it be `.gitignore`d before any write — inheriting, not weakening, upstream's own existing requirement that "version control ignores the whole directory."
- **No `npx skills add` as hub install.** The house wrapper must state installation is via normal hub discovery (`AGENTS.md` + `skills/INDEX.md` + this repo's clone), never via `npx skills add https://github.com/cloudflare/security-audit-skill ...` — that is upstream's own solo/global installation path, not how a hub user gets this skill.
- **`SkillConfig.quick_start` restates guidance-default + sandbox check + not-a-substitute.** The new `security-audit` `SkillConfig` entry's `quick_start` tuple must include at least one bullet for each of: (a) guidance-mode-by-default / full-audit only on explicit ask, (b) the four-controls capability check before any target-controlled execution, (c) not a substitute for `expert-pr-review` or `blast-radius`.
- **Do not full-audit `agent-bootstrap` in the implement PR.** Stated as an explicit "do not do" item in §9 below; the implement engineer proves the vendor works via the Blocker 6 fixtures (structure check + `.cjs` tests), never by running the audit against this repo.
- **Optional `skills/INDEX.md` hub-version bump.** `skills/INDEX.md`'s footer currently reads `Hub version: 0.11.0`. The implement-track PR may bump this per existing convention (e.g., prior feature landings such as ADR-006's Grok packaging bumped a version marker) — optional, not required for this plan to be implementable.

---

## 7. Implement Sequencing

Restated from Blocker 4's checklist as a flat ordered list (live-gate strictly before any surface listing):

1. Vendor tree + author hub `SKILL.md` (Blockers 1, 2).
2. Extend `COMPANION_PAIRS`; patch `expert-pr-review`/`blast-radius` Companions sections; recapture `blast-radius`'s `black-box-run.json` (Blocker 4).
3. Write `scripts/validate_security_audit_vendor.py` + `tests/test_security_audit_vendor_cjs.py` + both fixtures (Blocker 6).
4. Capture `security-audit`'s own `black-box-run.json`; confirm `check_skill_live.py security-audit` exits `0`. **Gate.**
5. Only past step 4: `skills/INDEX.md`, `AGENTS.md` §4 row, five rule files, `export_codex_skills.py` `SkillConfig`.
6. `install-grok.sh` recursive-reference fix + re-export; new dual-home test (Blocker 2).
7. Rewrite `agents/security-reviewer.md` + `AGENTS.md` §3 standalone-audit sentence (Blocker 3).
8. Full suite: `python3 -m unittest discover -s tests` green; `tests/test_index_live_binding.py` green with `security-audit` listed and live.

---

## 8. Test Plan

This repo's actual, verified test invocation (not `pytest`, despite `AGENTS.md`'s general-rule mention of pytest for Python projects — this hub's own historical convention, confirmed by running it, is `unittest`; `pytest` is installed in this environment and is unittest-compatible if a future contributor prefers it, but new tests here should match the existing 14-file `tests/` convention for consistency):

```bash
python3 -m unittest discover -s tests          # full suite; 123/123 pass today, pre-implement
python3 scripts/check_skill_live.py security-audit
python3 scripts/index_skills.py                 # or: python3 -m unittest tests.test_index_live_binding
node --test skills/security-audit/references/cloudflare/validate-findings.test.cjs
node --test skills/security-audit/references/cloudflare/validate-coverage-ledger.test.cjs
```

Implement-track additions to the suite:
- `tests/test_security_audit_vendor_cjs.py` — Node presence/version + both `node --test` runs, fail (not skip) on missing/old Node.
- New assertions in (or alongside) `tests/test_pstack_skills.py`-style tests for `security-audit`'s own reverse-companion pointers (mirroring `test_expert_pr_review_companion_points_at_interrogate`).
- A dual-home nested-reference test proving `export_codex_skills.py --force` preserves `references/cloudflare/**` and, after the `install-grok.sh` fix, that script also copies it.
- `skills/security-audit/fixtures/vendor-structure-check/` and `skills/security-audit/fixtures/cjs-tests-pass/` — both real `black-box-agent-qa` fixtures, run via `scripts/run_black_box_fixture.py`, not merely written.

---

## 9. Explicit "Do Not Do" List (this plan-track PR and the implement-track PR it authorizes)

- Do not vendor any file under `skills/security-audit/` in **this** PR.
- Do not write `scripts/validate_security_audit_vendor.py`, `tests/test_security_audit_vendor_cjs.py`, or any fixture in **this** PR.
- Do not edit `scripts/validate_pstack_skill.py`, `scripts/export_codex_skills.py`, `scripts/install-grok.sh`, `agents/security-reviewer.md`, `AGENTS.md`, `skills/INDEX.md`, `skills/expert-pr-review/SKILL.md`, `skills/blast-radius/SKILL.md`, or any of the five rule files in **this** PR.
- Do not install upstream's `SKILL.md` as the hub entry, ever (implement-track included) — the hub entry is always the house-authored wrapper.
- Do not add `security-audit` to `GRANDFATHERED_SKILLS` (implement-track included) — it gates via `black-box-agent-qa` like every new skill.
- Do not run a full security audit — guidance or full-audit mode — against `agent-bootstrap` in the implement-track PR. Vendor correctness is proven by the structure + `.cjs` fixtures, not by auditing this repo.
- Do not open, read, reference, or otherwise touch GMA-54 anywhere in this plan or the implement-track PR it authorizes.
- Do not use `npx skills add` as an installation instruction anywhere in the house wrapper (SHOULD_FIX).
- Do not treat a general harness sandbox claim, or `expert-pr-review`'s build/test step, as satisfying the four Universal execution-safety controls (Blocker 5).
- Do not self-merge this PR or the implement-track PR it authorizes.

---

## Spec-Gate Card

```text
**Spec gate** — spec → GRILL · gma-56-security-audit-vendor

Documents:
- docs/projects/agent-bootstrap/gma-56-security-audit-vendor-plan.md

Approve · Reject
```

Per `skills/reply-contract/SKILL.md`: only a literal **Approve**/**CLEAR** or **Reject** from Blair, recorded by CoS, counts as the stamp — "looks good"/"ok"/silence do not. **Reject** → state what changes, then re-present this same card. **Approve/CLEAR** → CoS assigns the implement-track PR, gated by §7's sequencing and `skills/black-box-agent-qa/SKILL.md`'s existing "write it is not ship it" rule for the new `security-audit` skill.

*Last updated: 2026-09-23 | Plan-track only — do not add implement-track content to this file; open a new document for the implement-track plan once Blair CLEAR/Approve is recorded.*
