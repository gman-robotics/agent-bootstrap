# Adjudicator prompt template (disagreements only)

Run only for items where labeler A and labeler B disagree after the deterministic merge scan.

```
You are the adjudicator for a labeling disagreement. Labeler A and B saw the same item independently.

Label field: {{label_field}}
Allowed labels: {{allowed_labels_or_normalize_rules}}

Item:
{{item_json}}

Labeler A: label={{label_a}} rationale={{rationale_a}}
Labeler B: label={{label_b}} rationale={{rationale_b}}

Decide the final label. Output one JSON object (JSONL row) with:
- "id": string
- "final_label": string
- "rationale": string (one or two sentences explaining your choice)

Do not defer to majority rules beyond your own reading of the item.
```

Persist adjudicator output as `adjudicator.jsonl`, then merge with `scripts/adjudicate_labels.py`.
