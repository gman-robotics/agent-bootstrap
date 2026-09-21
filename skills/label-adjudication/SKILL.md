---
name: label-adjudication
description: >-
  Use for "adjudicate labels", "label adjudication", "two-model label", or
  "curate dataset labels" when building labeled JSONL with two independent
  upper-frontier labelers and a third adjudicator on disagreements only.
version: 1.0.0
---

# label-adjudication

**Purpose**
Curate labeled JSONL datasets (e.g. home-50 and larger sets) with two independent
upper-frontier labeler models, accept agreements without a third call, and run an
adjudicator only on disagreements. Emit provenance-rich artifacts for a human stamp
step — never silently skip conflicts.

**Trigger**
"adjudicate labels", "label adjudication", "two-model label", "curate dataset labels",
or when building/curating labeled JSONL with multi-model agreement.

**Do not use for**
- Pull request or code review → `interrogate` or `expert-pr-review`
- Competing design sketches before implementation → `arena` or `architect`

## Companions

| Skill | Role here |
|---|---|
| `subagent-routing` | Spawn labeler A, labeler B, and adjudicator with appropriate model tiers |
| `write-tests` | Red/green tests for any custom normalization or merge helpers you add around the hub CLI |
| `technical-writing` | `summary.md` and human-facing curation notes |

**Verification**
- Labeler A and B used the same prompt template with no shared chain-of-thought
- Every disagreeing `id` has an adjudicator row or the merge CLI exits non-zero
- `adjudication.jsonl` and `final.jsonl` exist with expected `resolution` and `label_status`
- `python3 scripts/adjudicate_labels.py` (or the skill black-box fixture) reports `agree=` and `adjudicated=` on stdout
- Human stamp recorded for overrides; conflicts never dropped

---

## Step 1 — Define inputs

Collect:

| Input | Required | Notes |
|---|---|---|
| Source JSONL | Yes | Unlabeled or draft-labeled rows; each row must have stable `id` |
| `label_field` name | Yes | Field name to write on output (default conceptually `label`) |
| Label vocabulary | Yes | Closed set of allowed labels, or free-form with explicit normalize rules |
| Model ids | Yes | Configurable per harness — **do not** assume a single vendor slug; record in provenance |
| Output directory | Yes | Writable workspace for all artifacts |

Document normalize rules (trim, lowercase, map synonyms) before any model runs.

## Step 2 — Independent labeling (A and B)

1. Fill `references/labeler-prompt.md` for both labelers with the same template.
2. Spawn labeler **A** and labeler **B** in **separate** harness calls — no peeking at the other's labels or rationale.
3. Require JSONL output with at least `id` and `label`; optional `rationale` per row.
4. Save as `labels_a.jsonl` and `labels_b.jsonl` in the output directory.

Optional: batch by `id` ranges; on resume, skip ids already present in partial JSONL (idempotent append).

## Step 3 — Deterministic merge scan

Run the hub merge CLI (no LLM):

```bash
python3 scripts/adjudicate_labels.py \
  --labels-a labels_a.jsonl \
  --labels-b labels_b.jsonl \
  --items source.jsonl \
  --adjudicator-jsonl adjudicator.jsonl \
  --adjudication-out adjudication.jsonl \
  --final-out final.jsonl \
  --model-a "<labeler-a-model-id>" \
  --model-b "<labeler-b-model-id>" \
  --model-adjudicator "<adjudicator-model-id>"
```

Rules:

- **Agree** (`label` exact match after any documented normalization applied *before* merge): `resolution=agree`, `final_label` = shared label.
- **Disagree**: requires a row in `adjudicator.jsonl` with `id`, `final_label`, optional `rationale`. If any disagreeing id lacks a row, the CLI **exits 1** and lists unresolved ids — it does not invent labels.

## Step 4 — Adjudicator on disagreements only

For each disagreeing id (from a dry-run list or a failed merge):

1. Fill `references/adjudicator-prompt.md` with item context + both labels and rationales.
2. Spawn the adjudicator model once per disagreeing item (or batched per harness limits).
3. Append rows to `adjudicator.jsonl`.
4. Re-run Step 3 until exit code 0.

## Step 5 — Output artifacts

| Artifact | Contents |
|---|---|
| `labels_a.jsonl` / `labels_b.jsonl` | Raw labeler outputs |
| `adjudication.jsonl` | One row per id: `id`, `label_a`, `label_b`, `final_label`, `resolution` (`agree` \| `adjudicated`), `adjudicator_rationale` (null on agree), `models` |
| `final.jsonl` | Source rows (when `--items` given) plus `label` and `label_status` (`agreed_pending_human` or `adjudicated_pending_human`) |
| `summary.md` | Agree count, disagree count, per-label distribution, model ids used |

## Step 6 — Human stamp

A human reviewer may override any `final_label` in `final.jsonl`. Record overrides in a sidecar or amended `summary.md` (who, when, old → new). Never silently accept adjudicator output on high-stakes classes without review. Disagreements must remain visible in `adjudication.jsonl` even after human override.

## Step 7 — Scaling and resume

- **Batching**: shard by `id` prefix or line ranges; merge CLI requires identical id sets in A and B — complete both shards before merge.
- **Resume**: if `labels_a.jsonl` exists, append only missing ids; same for B and adjudicator.
- **Idempotent re-run**: re-running merge with the same inputs overwrites `adjudication.jsonl` and `final.jsonl` deterministically.

---

## Verification Checklist

- [ ] Same labeler prompt template for A and B; no shared CoT
- [ ] `scripts/adjudicate_labels.py` exit 0 with full adjudicator coverage
- [ ] `summary.md` counts match stdout `agree=` / `adjudicated=` line
- [ ] Human stamp step scheduled or completed for `*_pending_human` rows
- [ ] Black-box fixture pass captured in `black-box-run.json` (`check_skill_live.py label-adjudication` → 0)

---

Last updated: 2026-09-21
