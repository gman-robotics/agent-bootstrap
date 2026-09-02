# HoH Schema Steal Plan — Evidence Packet (Et) + Preservation Gate

> **Scope**: This is a **plan-only** document. It names files/skills to add or patch, an Et JSON schema (shown as fenced-block spec, not shipped), a Preservation Gate markdown field, a freeze mechanism, and named black-box fixtures — for a *later* implement-track PR. No validator, schema file, skill, or fixture is shipped live in this PR. Any JSON or Markdown shown below is illustrative spec, not a committed artifact.

**Task name**: `hoh-schema-steal` (stable for this thread's life — reused on the spec-gate card below and in any later `close-out` handoff entry).

**Author model**: claude-sonnet-5. **Next**: Blair grok-4.6 grills this plan. **No implement-track work starts until CoS records a literal Blair APPROVE** on the spec-gate card (see end of this document and the PR description).

**Status**: Draft, plan-track only. Not merged.

---

## 1. What Tom decided (2026-09-02)

Go forward with the steal on **both** Grok Bot and Hermes. **Schema/process only** — this is explicitly not a pick of Harness-of-Harness (HoH) as a product, and not a move toward autonomous no-human development. Every mechanism named below still routes through a human stamp (CoS/Blair spec-gate) and an independent QA role (Kit) that never edits the candidate it is scoring.

## 2. Sources (cited, not recomputed)

- **Wiki**: main `0651e60`, page `[[harness-of-harness]]` = `entities/harness-of-harness.md` (landed via PR #99). Fetched via GitHub for this plan (`https://github.com/Flesymeb/HarnessOfHarness/wiki/harness-of-harness`, which resolves to the repo's README/overview content — the wiki page and the repo `README.md` carry the same HoH overview at the time of this fetch). Repository: [`Flesymeb/HarnessOfHarness`](https://github.com/Flesymeb/HarnessOfHarness) (MIT licensed, `has_wiki: true`, confirmed via `gh api /repos/Flesymeb/HarnessOfHarness`). **Not cloned** — read-only citation only, per this task's constraint.
- **Paper**: arXiv `2609.01481`, *"Harness of Harness: Multi-Day Autonomous Software Development with Continual Improvement"* (Yan, Su, Zhang, Li, Zhang, Zhang, Chen, Bai, Hu). Fetched `https://arxiv.org/abs/2609.01481` for this plan.
  - **Locked ablation (Table 3, GameCraft-Bench, Codex + GPT-5.5 high, $T=3$)** — verified against the fetched paper text, not recomputed:

    | Variant | Score (Δ from Full HoH@3) | Tokens (M) |
    |---|---|---|
    | Full HoH@3 | **71.52** | 8.41 |
    | w/o Plan Update | 63.39 (**−8.13**) | 7.56 |
    | w/o Evidence Feedback | 65.23 (**−6.28**) | 7.46 |
    | w/o Warm-Start | 63.67 (**−7.85**) | 11.12 |

  - The abstract's relative gains (**52.25%**, **82.86%**) are the paper's own summary figures, cited as-is — not recomputed here.
  - **Listing 1** (normalized `E_t`, confirmed against the fetched paper text, reproduced here as spec, not copied verbatim beyond structure):
    ```json
    {
      "iteration": 2,
      "qa_status": "partial",
      "verified_records": [
        {
          "claim_id": "player_control",
          "claim": "Player input changes avatar motion.",
          "execution_records": [
            { "type": "replay", "path": "replays/core_loop.json", "observation": "..." },
            { "type": "runtime_trace", "path": "traces/core_loop.json", "observation": "..." }
          ],
          "status": "verified"
        }
      ],
      "gap_records": [
        {
          "claim_id": "result_state",
          "claim": "Completing the objective produces a visible result.",
          "execution_records": [
            { "type": "screenshot", "path": "screenshots/frame_018.png", "observation": "..." }
          ],
          "status": "gap",
          "player_impact": "Completion is not visible to the player.",
          "recommended_update": "Add and replay a result state."
        }
      ],
      "planner_handoff": {
        "preservation_constraints": ["Preserve verified player movement."],
        "update_targets": ["Implement a visible completion state."],
        "validation_requirements": ["Replay objective completion through the result screen."]
      }
    }
    ```
    The paper's own execution-record types (Listing 1 + surrounding text) are `replay`, `runtime_trace`, `screenshot`. This house steal (§4 below) narrows to `screenshot | runtime_trace | fixture` — dropping `replay` as a fourth type name and folding it into `fixture` (a named, checkable input/expected-output pair per `skills/black-box-agent-qa/SCHEMA.md`, this hub's own existing "replay"-equivalent). Status is `verified | gap` only — the paper's own text is explicit that "outputs that violate the required schema trigger a retry," which is the source for GB-6 below.
  - The paper's three-role split (Project Planner — plans, never edits; Developer — implements, warm-starts from the existing artifact; QA Tester — read-only, evidence-only) is cited directly for H-2 and H-3 below.
- **Scout eval scoreboard** (not contradicted here): already-have three-role split, planner-does-not-write, independent QA, spec-gate, REPEAT→mechanical, Lane screenshot critic, wrap-existing-harnesses, wiki/Linear/git, max-3-then-escalate, swarm-forge envelope. This plan steals **GB-1..6 and H-1..5 only** — nothing else from the scoreboard is touched.
- **Hub contract**: `skills/black-box-agent-qa/SCHEMA.md` + `scripts/run_black_box_fixture.py` is the existing I/O contract this plan extends (§4, §5) rather than replaces. Reading a PR is not a pass; Kit does not pass by reading the PR — this is already this hub's own rule (`skills/black-box-agent-qa/SKILL.md` "Reading is not running"), reused, not reinvented, for evidence-packet claims.

## 3. Home: hub vs. Grok Bot overlay

- **Land on this repo** (`gman-robotics/agent-bootstrap`): the Et JSON schema, the Preservation Gate field definition, the freeze/`head_sha` extension, and the named black-box fixtures. This is shared schema/process — exactly what the hub exists to hold — so Hermes on Eleanor loads it the same way it loads every other skill, via `AGENTS.md` + `skills/INDEX.md` discovery.
- **Grok Bot CoS overlay only** for anything that names Lane/Kit by role identity or wires them into a specific harness invocation — that wiring is local, not hub content, and this plan does not create it.
- **Do not clone** `Flesymeb/HarnessOfHarness`. Nothing in §4–§6 requires the upstream code; HoH-lite is not yet published (see §8 Leftovers) and would not be vendored even if it were — this is a schema/process steal, not a code adoption.
- **Prefer bootstrap fixtures over `arm`.** No file in this plan touches `arm`; every fixture named in §5 lives under a hub `skills/` directory.
- **Do not mint teammate entity pages.** Kit and Lane are referenced below only as already-existing named roles from the Scout scoreboard (independent QA / screenshot critic) that this hub's schema must be *consumable by* — no bio, roster table, or entity file is added here or proposed.

## 4. Preservation from current stack (must stay — verified against the current hub files, not assumed)

Confirmed present in this checkout at `main@b0838a2` before this plan; nothing in §5–§10 below proposes changing any of these:

- Spec-gate literal **Approve**/**Reject** (`skills/reply-contract/SKILL.md` "Gate cards"; "ok" is not Approve).
- Four-field envelope (`type`/`to`/`priority`/`task`) + one stable Name (`skills/multi-harness-coordination/SKILL.md` "Optional: four-field envelope stanza"; `skills/reply-contract/SKILL.md` "Task name").
- REPEAT → mechanical check (lint/test/CI), not another comment (`skills/triage-review-feedback/SKILL.md` Step 3).
- Kit does not pass by reading the PR (`skills/black-box-agent-qa/SKILL.md` "Reading is not running").
- Lane never implements (Scout scoreboard convention; this plan's §6 GB-5 keeps it explicit for the Et schema too).
- Wiki SoT (this plan cites the wiki, does not replace it).
- Linear tickets as the tracker, not GitHub issues (no GitHub issue opened by this plan).
- CoS stays PM (the spec-gate approval at the end of this document is a CoS-recorded stamp, not a self-approval).
- Max-3 adversarial rounds then escalate (`skills/multi-harness-coordination/SKILL.md` "Iteration limit... maximum 3 rounds"; GB-6 below reuses this shape for schema retries, does not raise the cap).

## 5. IN-SCOPE items mapped to concrete implement-track targets

Each row names where the mechanism lands. Nothing in this column is created by this PR — it is the target for the follow-up implement-track PR, after Blair APPROVE.

| Item | What it is | Target file (implement-track, later) | Notes |
|---|---|---|---|
| **GB-1** | Claim-bound evidence packet: typed `execution_records`, status `verified\|gap` only | `skills/evidence-packet-protocol/SKILL.md` (new) + `skills/evidence-packet-protocol/SCHEMA.md` (new) | Schema body in §6 |
| **GB-2** | Preservation Gate field on the plan markdown, distinct from REPEAT | `skills/preservation-gate/SKILL.md` (new, canonical) + one-line pointer in `skills/multi-harness-coordination/SKILL.md` | Field spec in §7; **not** a `reply-contract` patch (see §7 "Placement decision") |
| **GB-3** | Each increment repairs outstanding gaps AND delivers one observable new capability | `skills/evidence-packet-protocol/SKILL.md` — a rule inside the same skill as GB-1 (a `planner_handoff.update_targets` entry must name at least one gap repair *and* the plan's own new-capability line, checked structurally, not by prose promise) | No new file; a rule inside GB-1's skill |
| **GB-4** | Frozen candidate identity: Kit/Lane evidence bound to one git SHA; no edit rights on the candidate | `skills/evidence-packet-protocol/SCHEMA.md` — add optional `head_sha` field at the packet root (§8) | "Hardproof" rhyme only — **Hardproof itself is not installed** (see §10 Leftovers) |
| **GB-5** | Lane screenshots as `execution_records` rows inside `E_t`, not a separate chat CoS must remember | Already the GB-1 schema shape (`type: "screenshot"` rows) — no separate file. Lane still never implements (unchanged Preservation item) | Zero new surface — this is a consequence of GB-1, not a new mechanism |
| **GB-6** | Schema-or-retry once on `Dt`/`Et`, then escalate to CoS — not a T=70 silent reinvoke | `skills/evidence-packet-protocol/SKILL.md` — "Retry-once, then escalate" rule, reusing the max-3 escalation *shape* from `multi-harness-coordination` (but capped at 1 retry, not 3, since this is a schema-validity retry, not a review round) | Fixture: `schema-retry-then-escalate` (§8) |
| **H-1** | Same `E_t` on disk in the repo (`E_t.json`); next planner must read it | `evidence/E_t.json` — lives **next to the product branch** (Hermes/Eleanor or a Grok Bot product PR), **not** inside this hub. The hub only ships the schema/skill that defines the path convention | mem0/`activeContext.md` is explicitly **not** a substitute (paper's own Planner prompt template reads the prior evidence bundle directly, not a summarized memory note) |
| **H-2** | Read-only planner/tester worktree (or frozen SHA); Developer is the single writer | `skills/evidence-packet-protocol/SKILL.md` — a rule naming the three roles' write permissions, modeled on the paper's own role boundaries (Planner: "Do not implement, edit, test, or inspect production code"; QA Tester: "Do not modify production code") | Does **not** steal same-model-for-all-three-roles; keeps Sonnet vs. Grok / Claude Code vs. Codex distinct model pairing, per this hub's existing `subagent-routing`/`delegation-patterns` convention |
| **H-3** | Warm-start developer contract: continue from the artifact present; do not rewrite from empty | `skills/evidence-packet-protocol/SKILL.md` — a rule quoting the paper's own Developer contract line ("Continue from the artifact already present... Preserve verified functionality and repair the next observable gap rather than replacing a working project with a smaller reset") | Directly the mechanism the w/o Warm-Start ablation measures (−7.85, §2) |
| **H-4** | Per-role git commit (plan doc, code, evidence packet) | No new file — a rule inside `skills/evidence-packet-protocol/SKILL.md` naming the convention (one commit per role turn: Planner commits `Dt`, Developer commits code, QA commits `E_t.json`) | Matches this hub's existing `multi-harness-coordination` "Orchestrator Checklist" pattern, extended per-role |
| **H-5** | Progressive-disclosure index, not a full dump | `evidence/INDEX.md` (per product repo, sibling to `evidence/E_t.json`) — modeled on this hub's own `skills/INDEX.md` progressive-disclosure convention | Fixture: `evidence-index-not-full-dump` (§8) |

## 6. Files/skills to add or patch (implement-track — named now, not created in this PR)

1. **`skills/evidence-packet-protocol/SKILL.md`** (new) — defines when/how to produce and consume `E_t.json`: GB-1, GB-3, GB-6, H-1 (path convention), H-2 (role write-permissions), H-3 (warm-start contract), H-4 (per-role commit), H-5 (pointer to the index convention, body lives in `evidence/INDEX.md` per product repo).
2. **`skills/evidence-packet-protocol/SCHEMA.md`** (new) — the Et JSON schema (§7) + the `head_sha` freeze extension (§8), following the same "minimum schema, not a framework" style as `skills/black-box-agent-qa/SCHEMA.md`.
3. **`skills/evidence-packet-protocol/fixtures/<case-name>/`** (new, one dir per fixture named in §9) — `case.json` + `README.md` each, same shape as `skills/black-box-agent-qa/fixtures/`.
4. **`skills/preservation-gate/SKILL.md`** (new, canonical definition) — the exact heading, required list shape, and the explicit distinction from REPEAT (§7).
5. **`skills/multi-harness-coordination/SKILL.md`** (patch, one new subsection only — no rewrite) — a new "Optional: Preservation Gate field" subsection immediately after the existing "Optional: four-field envelope stanza" subsection, pointing at `skills/preservation-gate/SKILL.md` for the full definition. Same pattern already used for the envelope stanza: one paragraph + a pointer, not a copy of the mechanism.
6. **`skills/INDEX.md`** (patch, later — after the new skills each pass their own `black-box-agent-qa` gate per the existing "Adding a New Skill" step 2) — two new entries: `evidence-packet-protocol`, `preservation-gate`.
7. **`scripts/export_codex_skills.py`** (patch, later) — two new `SkillConfig` entries so `.grok/skills/evidence-packet-protocol/` and `.grok/skills/preservation-gate/` export automatically; re-export via the existing `--force` flow.
8. **Not touched, by explicit hub lock**: `skills/plan-code-review-workflow/SKILL.md`, `skills/expert-pr-review/SKILL.md` — no edit, no new pointer added to either in this plan or its implement-track follow-up.
9. **Not touched, by explicit instruction**: `skills/reply-contract/SKILL.md` (this hub's copy is at `1.4.0`; this plan does not add, patch, or reference a Preservation Gate field inside it — see §7 "Placement decision" for why, and the explicit note that this hub's `1.4.0` is a separate lineage from "Eleanor" reply-contract `1.3.0`, named here so neither is mistaken for the other).
10. **Not created anywhere**: `skills/adversarial-review/` — that skill is named in the task instructions as Grok Bot local only, not in the hub tree; this plan does not add it here, and does not reference it from any hub file (it would be a restole of local-overlay content into the hub, which this plan explicitly avoids).

## 7. JSON schema for `E_t` (spec only — fenced block, not a shipped file)

Root object, one `E_t.json` per iteration, path convention: `evidence/E_t.json` next to the product branch (H-1), with prior iterations kept as `evidence/E_<n>.json` and indexed by `evidence/INDEX.md` (H-5) — never overwritten in place, so "next planner must read it" (H-1) always resolves to a real, versioned file.

```jsonc
{
  "iteration": 2,                       // required, integer >= 1
  "head_sha": "a1b2c3d...",             // required — freeze binding, see "Kit/Lane freeze" below (GB-4)
  "qa_status": "partial",               // required, enum: "verified" | "partial" | "blocked"
  "verified_records": [                 // required, array (may be empty)
    {
      "claim_id": "player_control",     // required, string, stable slug
      "claim": "Player input changes avatar motion.",   // required, string
      "execution_records": [            // required, non-empty array — GB-1 "empty is a gap, not a pass"
        {
          "type": "screenshot",         // required, enum: "screenshot" | "runtime_trace" | "fixture"
          "path": "screenshots/frame_018.png",           // required, repo-relative path
          "observation": "..."          // required, string, one sentence
        }
      ],
      "status": "verified"              // required, enum: "verified" | "gap" — never "looks good"
    }
  ],
  "gap_records": [                      // required, array (may be empty)
    {
      "claim_id": "result_state",
      "claim": "Completing the objective produces a visible result.",
      "execution_records": [ /* same shape as above, non-empty */ ],
      "status": "gap",
      "player_impact": "Completion is not visible to the player.",     // required for gap_records only
      "recommended_update": "Add and replay a result state."          // required for gap_records only
    }
  ],
  "planner_handoff": {                  // required object
    "preservation_constraints": ["Preserve verified player movement."],   // required array, may be empty only if iteration == 1
    "update_targets": ["Implement a visible completion state."],          // required array, may be empty only if qa_status == "verified"
    "validation_requirements": ["Replay objective completion through the result screen."]  // required array
  }
}
```

- **Execution-record types**: exactly `screenshot | runtime_trace | fixture` (narrowed from the paper's `replay | runtime_trace | screenshot` — `fixture` replaces `replay` and is the record type used when the evidence is a named `skills/black-box-agent-qa`-style `case.json` run rather than a game replay file; this keeps one vocabulary instead of two "replay-like" types).
- **Status**: `verified | gap` only, at both the packet's `qa_status` and every record's `status`. A validator (implement-track) rejects any other literal string, including `"looks good"` — this is the direct mechanical analog of the spec-gate's "the stamp is the literal word" rule (§4), applied to QA evidence instead of a human approval.
- **Forbidden living PII — a named mechanical check class.** No claim, observation, or handoff string may contain a living person's real name (e.g., a bare first name such as "Lisa" or "Tanya" used as if referring to a real teammate) or a phone number that is not in the reserved fictitious range (`+1555XXXXXXX`, US NANP standard for fictional numbers). This is its own check class (see fixture `et-living-pii`, §9) — if a living-PII pattern already exists as a check somewhere in `arm`/the wiki tooling, treat a second sighting of the *same failure class* as REPEAT (`skills/triage-review-feedback/SKILL.md` Step 3), not as a new finding each time.
- **`head_sha`**: see §8.

## 8. Preservation Gate markdown field

**Exact heading**: `## Preservation Gate` — a required section on every plan/development-document markdown (`Dt`) from iteration 2 onward (iteration 1 has nothing yet to preserve).

**What it lists**: a bullet per `claim_id` (or one-line description) drawn from the *previous* iteration's `E_t.verified_records` that the current iteration's Developer must not regress. Each bullet is a **positive assertion of working behavior**, not a bug report:

```markdown
## Preservation Gate

- Player input changes avatar motion (`player_control`, verified iteration 1).
- Left/right controls navigate the main menu (`menu_nav`, verified iteration 1).
```

**How it is distinct from REPEAT** (this is the exact distinction the task requires, stated once, precisely):

| | Preservation Gate | REPEAT |
|---|---|---|
| **What it tracks** | Verified-**good** behavior from the last loop | A recurring **failure class** across reviews |
| **Where it lives** | The plan/development document (`Dt`), one section per iteration | `skills/triage-review-feedback/SKILL.md` Step 3, inside a PR-feedback triage |
| **Polarity** | Positive — "this works, do not break it" | Negative — "this class of bug keeps happening, block it" |
| **Closes when** | Never — it is carried forward and re-verified every iteration until deliberately superseded | Closed permanently by a mechanical check (lint/test/CI) added in the fix commit |
| **Who reads it** | Developer (must not regress), QA Tester (re-verifies) | Whoever is triaging the next review |

**Placement decision (with reason)**: canonical definition lives in a **new small skill**, `skills/preservation-gate/SKILL.md`, not a patch to `skills/reply-contract/SKILL.md`. Reason: the Preservation Gate is a field on the **plan artifact itself** (`Dt`), consumed by the Developer role before any human approval step — it is not part of the human-stamp mechanism (`spec-gate card` / `clarify card`) that `reply-contract` owns, so folding it into `reply-contract` would conflate "what the plan document must contain" with "how a human approves a held artifact." A **one-line pointer only** (no mechanism copy) is added to `skills/multi-harness-coordination/SKILL.md`, next to the existing four-field-envelope subsection, because that is where this hub already documents optional plan-document conventions for cross-harness handoffs. `skills/reply-contract/SKILL.md` is **not touched** — this sidesteps the "Eleanor reply-contract `1.3.0`" ambiguity entirely (§6 item 9) rather than requiring a hub-vs-overlay judgment call on a file this plan does not need to open.

## 9. Kit/Lane freeze: how

- **`head_sha` on the packet.** `E_t.json`'s root `head_sha` field (§7) is the git SHA of the candidate commit the evidence packet is bound to. Kit and Lane produce evidence against exactly that commit; if the candidate advances (new commit), any existing `E_t.json` for the old SHA is stale and must not be reused as if it covered the new commit.
- **`skill_sha256` already exists for skills — extend to product PRs.** `scripts/check_skill_live.py` already hashes a skill's `SKILL.md` to detect staleness (`skills/black-box-agent-qa/SCHEMA.md`). The implement-track extension adds a sibling check — not a rewrite of the existing script — that hashes/compares a **product PR's** `head_sha` the same way: a new fixture-runnable check (`freeze-sha-mismatch`, §10) that fails when the packet's `head_sha` does not equal the actual candidate commit under test (e.g., `git rev-parse HEAD` in the product repo's worktree, or the PR's reported head SHA).
- **No edit rights on the candidate.** Enforced two ways, both already named in §6 H-2: (1) Kit/Lane operate in a read-only worktree (or a frozen-SHA checkout with no write remote) so there is no tool-level path to editing the candidate; (2) the `head_sha` mechanical check above catches the case where evidence is later presented against a commit the tester never actually held read-only (a rebased or amended candidate, for instance).
- **"Hardproof" rhyme only** — this plan explicitly does **not** install a plugin, package, or tool named or branded "Hardproof." The freeze mechanism above is built entirely from this hub's existing `skill_sha256` pattern, generalized; no new external dependency.

## 10. Named black-box fixtures (implement-track — named now, runner unchanged)

Runner: `scripts/run_black_box_fixture.py` (existing, unchanged) + one `case.json` per fixture, per `skills/black-box-agent-qa/SCHEMA.md`. Each fixture below assumes a new validator script `scripts/validate_evidence_packet.py` (implement-track; not written in this PR) that reads an `E_t.json`-shaped file and a new `scripts/validate_preservation_gate.py` for the `Dt` heading check — both named here as the literal `input.command` argv0/argv1 target, per the existing fixture convention (e.g. `skills/black-box-agent-qa/fixtures/check-skill-live-cli/` already runs a bare script this same way).

| Fixture name | `input.command` (argv) | `expected.exit_code` | `expected.stdout_contains` |
|---|---|---|---|
| `et-schema-valid` | `["python3", "scripts/validate_evidence_packet.py", "skills/evidence-packet-protocol/fixtures/et-schema-valid/E_t.sample.json"]` | `0` | `["valid"]` |
| `et-status-not-verified-or-gap` | `["python3", "scripts/validate_evidence_packet.py", "skills/evidence-packet-protocol/fixtures/et-status-not-verified-or-gap/E_t.sample.json"]` | `1` | `["invalid status"]` |
| `et-missing-execution-record` | `["python3", "scripts/validate_evidence_packet.py", "skills/evidence-packet-protocol/fixtures/et-missing-execution-record/E_t.sample.json"]` | `1` | `["execution_records"]` |
| `et-living-pii` | `["python3", "scripts/validate_evidence_packet.py", "skills/evidence-packet-protocol/fixtures/et-living-pii/E_t.sample.json"]` | `1` | `["living-pii"]` |
| `dt-missing-preservation-gate` | `["python3", "scripts/validate_preservation_gate.py", "skills/preservation-gate/fixtures/dt-missing-preservation-gate/Dt.sample.md"]` | `1` | `["Preservation Gate"]` |
| `freeze-sha-mismatch` | `["python3", "scripts/validate_evidence_packet.py", "--expect-head-sha", "<candidate-sha>", "skills/evidence-packet-protocol/fixtures/freeze-sha-mismatch/E_t.sample.json"]` | `1` | `["head_sha mismatch"]` |
| `schema-retry-then-escalate` | `["python3", "scripts/validate_evidence_packet.py", "--retry-then-escalate", "skills/evidence-packet-protocol/fixtures/schema-retry-then-escalate/invalid-1.json", "skills/evidence-packet-protocol/fixtures/schema-retry-then-escalate/invalid-2.json"]` | `2` | `["ESCALATE"]` |
| `next-planner-reads-et` *(H-1)* | `["python3", "scripts/check_planner_reads_et.py", "skills/evidence-packet-protocol/fixtures/next-planner-reads-et/plan-template.sample.md"]` | `0` | `["evidence/E_t.json"]` |
| `evidence-index-not-full-dump` *(H-5)* | `["python3", "scripts/check_evidence_index_is_progressive.py", "skills/evidence-packet-protocol/fixtures/evidence-index-not-full-dump/INDEX.sample.md"]` | `0` | `["progressive"]` |

Notes on exit-code convention: `0` = pass, `1` = fail (matches `SCHEMA.md`'s existing table). `schema-retry-then-escalate` uses `2`, reusing the existing `"blocked"` verdict code — an escalation is not a pass, and per `skills/black-box-agent-qa/SKILL.md` Step 4, a blocked/escalated run must never be scored as a pass; `2` keeps that invariant literal rather than inventing a fourth verdict.

## 11. Done-when (plan-track only — implement-track done-when is out of this PR)

- [x] This document exists at `docs/projects/agent-bootstrap/hoh-schema-steal-plan.md` and cites wiki `0651e60` + paper `2609.01481` (§2), with the locked ablation numbers verified against the fetched paper text, not recomputed.
- [x] Every GB-1..6 and H-1..5 item is mapped to a named implement-track target (§5, §6).
- [x] All 9 named black-box fixtures have a literal `input.command` argv, `expected.exit_code`, and `expected.stdout_contains` (§10).
- [x] Out-of-scope/skip items are named explicitly (§12), matching the task's own skip list.
- [x] Leftovers are named (§13).
- [ ] Draft PR opened against `main` — done by this same change; not merged.
- [x] No live schema/validator/skill file is shipped in this PR — every JSON/Markdown shown above is a fenced-block spec inside this document only; no `SCHEMA.md`, `SKILL.md`, `case.json`, or `scripts/*.py` file was created.
- [ ] Blair grok-4.6 grills this plan; CoS records a literal **Blair APPROVE** before any implement-track work starts (spec-gate card, end of this document).

## 12. Out of scope / skip (explicit — matches the task's skip list)

Not touched, installed, opened, or started by this plan or its citation research: installing `Flesymeb/HarnessOfHarness` (cloned nowhere); autonomous no-human development (every mechanism above still routes through a human CoS/Blair stamp); same-model write+grade (H-2 explicitly keeps Sonnet vs. Grok / Claude Code vs. Codex distinct); reopening GMA-9 or GMA-14; an unbounded `T=70` loop (GB-6 caps at retry-once-then-escalate, not a silent reinvoke); installing a "Hardproof" plugin (§9, rhyme only); adopting OpenCode as the house harness; any Godot/FPS toolchain; GMA-8/13/14; any AWS apply; living PII or real names (e.g., "Lisa"/"Tanya") in shipped evidence packets (named as a forbidden check class, §7, not permitted content); minting teammate entity pages for Kit/Lane (§3); rewriting `skills/plan-code-review-workflow/SKILL.md` or `skills/expert-pr-review/SKILL.md` (§6 item 8, hub lock respected); restealing swarm-forge cockpit/envelope (already landed at `9259d42`, untouched by this plan); modifying `arm`; touching any of GMA-8/13/14.

## 13. Risks

- **Schema theater without freeze.** A validator that checks `E_t.json`'s JSON shape but is never actually wired to a real `head_sha` check would "look verified" (green fixture output) without proving the evidence is bound to the commit it claims to cover. Mitigation: `freeze-sha-mismatch` (§10) is a named, required fixture in the same implement-track PR as the schema validator — the two ship together, not the schema alone first.
- **CoS overlay drift from hub.** If Grok Bot's local Lane/Kit wiring (kept out of the hub per §3) evolves independently of the hub's `evidence-packet-protocol` schema, the overlay and the hub can silently diverge (e.g., the overlay starts accepting a fourth `execution_records` type the hub schema rejects). Mitigation: name this drift risk explicitly in the new skill's "Common Mistakes" table (implement-track) and treat any overlay-vs-hub schema mismatch as a REPEAT-class finding once it happens twice.
- **PII bus.** Evidence packets that flow into wiki pages, Linear tickets, or git history carry a wider blast radius than a single chat message — a living-PII slip in `E_t.json` persists in git log forever. Mitigation: `et-living-pii` (§10) is a required fixture, not an optional one, and the check class is named explicitly as mechanical (§7), not a style-guide reminder.
- **Same-model temptation.** It is cheaper to run Planner/Developer/QA on one model, and nothing in the JSON schema itself prevents that — the separation is a process rule (H-2), not something the schema can enforce mechanically. Mitigation: name this explicitly as a Preservation item (§4) and as an out-of-scope item (§12); a future fixture idea (not named here, left as an open question) could check that three distinct role-invocation records in a packet's provenance are not byte-identical, but that is not proposed as done-when for this plan.
- **Overbuild into a runtime.** The natural next step after "we have a schema and fixtures" is "let's build an orchestrator that runs the loop automatically" — which would cross directly into the "autonomous no-human development" line Tom's decision explicitly rules out (§1). Mitigation: every file named in §6 is a skill/schema/fixture (markdown + JSON + a validator script), never a scheduler, daemon, or CI trigger; this plan does not name or propose one.

## 14. Leftovers

- **Hardproof not installed.** Named only as a naming-rhyme for the freeze mechanism (§9); no plugin, package, or binary by that name exists in this hub or is proposed.
- **Native-compiled-black-box gap.** `skills/black-box-agent-qa/SCHEMA.md`'s contract is a subprocess argv/exit-code/stdout check — it covers a validator script well, but GameCraft-Bench-style artifacts (a compiled Godot export, a game binary) are not a subprocess with a clean exit code in the same way. This plan's fixtures (§10) all target validator scripts, not compiled game artifacts, so this gap is named but not closed here.
- **HoH-lite unpublished.** The wiki/README (§2) states HoH-lite ("a lightweight implementation of HoH's core workflow") is "Coming soon" — nothing to read or vendor from it yet. Revisit when published; the "do not clone `Flesymeb/HarnessOfHarness`" constraint in this task is scoped to this task, not asserted here as a permanent policy for all future work.
- **GMA-14 fog.** Referenced only as an out-of-scope item (§12) per the task's own instruction; not investigated, opened, or described further here.
- **Eleanor reply-contract `1.3.0`.** This hub's `skills/reply-contract/SKILL.md` is at `1.4.0` and is **not touched** by this plan (§6 item 9, §8 placement decision). "Eleanor" reply-contract `1.3.0` is a separate, named lineage — flagged here explicitly so a future pass does not assume the hub's `1.4.0` supersedes or should overwrite it; that is an overlay-vs-hub reconciliation question for a different task, not resolved here.

---

## Spec-gate card

```text
**Spec gate** — spec → GRILL · hoh-schema-steal

Documents:
- `docs/projects/agent-bootstrap/hoh-schema-steal-plan.md`

Approve · Reject
```

Per `skills/reply-contract/SKILL.md`: only a literal **Approve** or **Reject** from Blair grok-4.6, recorded by CoS, counts as the stamp — "looks good"/"ok"/silence do not. **Reject** → state what changes, then re-present this same card. **Approve** → implement-track work (§6–§10) may start, still gated by `skills/black-box-agent-qa/SKILL.md`'s existing "write it is not ship it" rule for every new skill named in §6.

*Last updated: 2026-09-02 | Plan-track only — do not add implement-track content to this file; open a new document for the implement-track plan once Blair APPROVE is recorded.*
