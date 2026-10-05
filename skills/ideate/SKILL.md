---
name: ideate
description: "Use when the direction is not chosen yet. Generate candidates across six frames, tag the basis of each, cut losers with a reason, and write a ranked artifact. Refuse if the idea is already chosen."
version: 1.0.0
---

# ideate — Pick a direction before the grill

**Purpose**
Find a small set of grounded directions before anyone writes a plan. Each candidate must cite a basis. Losers die in writing.

**Trigger**
"Ideate", "what is worth exploring", or a request where the user has a problem and no chosen approach.

**Do not use for**
- An idea already on the table → `grill-with-docs`
- A single adoption verdict → `interrogate` or `why`
- A costly implementation choice with the approach already framed → `arena`
- More than three open questions about one chosen idea → `grill-with-docs` or `blocker-walkthrough`

## Steps
1. Read `STRATEGY.md` if the active project has one. Read overlapping `docs/solutions/` notes. Do not generate against a lesson already captured.
2. Generate candidates across these frames. Cover each frame or say why it does not apply:
   - Pain: what is slow, broken, or annoying.
   - Removal: invert, delete, or automate the painful step.
   - Assumption: treat a fixed constraint as a choice.
   - Leverage: what makes the next change cheaper.
   - Analogy: a structurally similar fix from another domain.
   - Constraint flip: what changes if budget, time, or team size is extreme.
3. Tag each candidate with a basis: a file path, a metric, or a cited source. An untagged candidate is not a candidate.
4. Adversarial cut: critique every candidate. Record why each loser dies. Rank only the survivors.
5. Write `docs/ideation/YYYY-MM-DD-<slug>.md` with the ranked list, the basis tags, and the cut reasons.
6. Stop. Offer `grill-with-docs` on the top survivor. Do not implement.

## Companions

| Skill | Role here |
|---|---|
| `strategy` | Upstream anchor when `STRATEGY.md` exists |
| `grill-with-docs` | Next step after a survivor is chosen |
| `arena` | Use instead when the choice is an implementation shape, not a direction |

## Provenance
Adapted from EveryInc/compound-engineering-plugin `ce-ideate` (MIT, Copyright (c) 2025 Every). Independent rewrite. Frame names restated. No plugin tree copied.

Last updated: 2026-10-05
