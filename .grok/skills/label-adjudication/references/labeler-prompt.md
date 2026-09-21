# Labeler prompt template (A and B)

Use the **same** filled template for labeler A and labeler B. Do not share chain-of-thought between runs.

```
You are an independent dataset labeler. Assign exactly one label per item.

Label field: {{label_field}}
Allowed labels: {{allowed_labels_or_normalize_rules}}

For each item, output one JSON object per line (JSONL) with:
- "id": string (copy from input)
- "label": string (must be from the allowed set, or normalized per rules)
- "rationale": string (one short sentence; no references to other labelers)

Items:
{{items_json_or_path_reference}}
```

Harness notes:
- Spawn A and B in separate subagent calls with no shared memory of the other's output.
- Record `model_id` used for each run in run metadata (passed to `scripts/adjudicate_labels.py --model-a` / `--model-b`).
