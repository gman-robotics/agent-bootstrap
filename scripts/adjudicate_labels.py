#!/usr/bin/env python3
"""Deterministic merge of two independent labeler JSONL files with optional adjudicator rows.

Used by skills/label-adjudication/SKILL.md after labeler A/B runs complete. Does not call
LLMs — harnesses produce labels_a.jsonl / labels_b.jsonl / adjudicator.jsonl separately.

Usage:
    python3 scripts/adjudicate_labels.py \\
        --labels-a labels_a.jsonl --labels-b labels_b.jsonl \\
        [--items items.jsonl] \\
        [--adjudicator-jsonl adjudicator.jsonl] \\
        --adjudication-out adjudication.jsonl --final-out final.jsonl

Exit codes: 0 = all rows resolved, 1 = schema error or unresolved disagreement.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_LABEL_FIELDS = ("id", "label")
REQUIRED_ADJUDICATOR_FIELDS = ("id", "final_label")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: each row must be a JSON object")
        rows.append(row)
    return rows


def _index_by_id(rows: list[dict[str, Any]], source: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        for field in REQUIRED_LABEL_FIELDS:
            if field not in row:
                raise ValueError(f"{source}: row missing required field '{field}': {row!r}")
        row_id = row["id"]
        if not isinstance(row_id, str) or not row_id:
            raise ValueError(f"{source}: id must be a non-empty string: {row!r}")
        if row_id in index:
            raise ValueError(f"{source}: duplicate id {row_id!r}")
        index[row_id] = row
    return index


def _index_adjudicator(rows: list[dict[str, Any]], source: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        for field in REQUIRED_ADJUDICATOR_FIELDS:
            if field not in row:
                raise ValueError(f"{source}: row missing required field '{field}': {row!r}")
        row_id = row["id"]
        if row_id in index:
            raise ValueError(f"{source}: duplicate id {row_id!r}")
        index[row_id] = row
    return index


def merge_labels(
    labels_a: dict[str, dict[str, Any]],
    labels_b: dict[str, dict[str, Any]],
    adjudicator: dict[str, dict[str, Any]],
    *,
    model_a: str | None = None,
    model_b: str | None = None,
    model_adjudicator: str | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (adjudication_rows, unresolved_ids)."""
    ids_a = set(labels_a)
    ids_b = set(labels_b)
    if ids_a != ids_b:
        only_a = sorted(ids_a - ids_b)
        only_b = sorted(ids_b - ids_a)
        raise ValueError(
            f"label file id mismatch: only in A={only_a!r}, only in B={only_b!r}"
        )

    models: dict[str, str | None] = {
        "labeler_a": model_a,
        "labeler_b": model_b,
        "adjudicator": model_adjudicator,
    }

    adjudication_rows: list[dict[str, Any]] = []
    unresolved: list[str] = []

    for row_id in sorted(ids_a):
        la = labels_a[row_id]["label"]
        lb = labels_b[row_id]["label"]
        if la == lb:
            adjudication_rows.append(
                {
                    "id": row_id,
                    "label_a": la,
                    "label_b": lb,
                    "final_label": la,
                    "resolution": "agree",
                    "adjudicator_rationale": None,
                    "models": models,
                }
            )
            continue

        adj = adjudicator.get(row_id)
        if adj is None:
            unresolved.append(row_id)
            continue
        rationale = adj.get("rationale")
        adjudication_rows.append(
            {
                "id": row_id,
                "label_a": la,
                "label_b": lb,
                "final_label": adj["final_label"],
                "resolution": "adjudicated",
                "adjudicator_rationale": rationale,
                "models": models,
            }
        )

    return adjudication_rows, unresolved


def build_final_rows(
    adjudication_rows: list[dict[str, Any]],
    items_by_id: dict[str, dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    finals: list[dict[str, Any]] = []
    for row in adjudication_rows:
        row_id = row["id"]
        if items_by_id is not None:
            if row_id not in items_by_id:
                raise ValueError(f"items: missing id {row_id!r}")
            base = dict(items_by_id[row_id])
        else:
            base = {"id": row_id}
        base["label"] = row["final_label"]
        if row["resolution"] == "agree":
            base["label_status"] = "agreed_pending_human"
        else:
            base["label_status"] = "adjudicated_pending_human"
        finals.append(base)
    return finals


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--labels-a", type=Path, required=True)
    parser.add_argument("--labels-b", type=Path, required=True)
    parser.add_argument("--items", type=Path, help="optional source rows to merge labels into")
    parser.add_argument(
        "--adjudicator-jsonl",
        type=Path,
        help="required for every disagreeing id; no rows invented",
    )
    parser.add_argument("--adjudication-out", type=Path, required=True)
    parser.add_argument("--final-out", type=Path, required=True)
    parser.add_argument("--model-a", help="provenance: labeler A model id")
    parser.add_argument("--model-b", help="provenance: labeler B model id")
    parser.add_argument("--model-adjudicator", help="provenance: adjudicator model id")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        rows_a = _read_jsonl(args.labels_a)
        rows_b = _read_jsonl(args.labels_b)
        index_a = _index_by_id(rows_a, str(args.labels_a))
        index_b = _index_by_id(rows_b, str(args.labels_b))
        adjudicator_index: dict[str, dict[str, Any]] = {}
        if args.adjudicator_jsonl is not None:
            adj_rows = _read_jsonl(args.adjudicator_jsonl)
            adjudicator_index = _index_adjudicator(adj_rows, str(args.adjudicator_jsonl))

        adjudication_rows, unresolved = merge_labels(
            index_a,
            index_b,
            adjudicator_index,
            model_a=args.model_a,
            model_b=args.model_b,
            model_adjudicator=args.model_adjudicator,
        )
        if unresolved:
            print(
                f"unresolved disagreement ids (need adjudicator row): {', '.join(unresolved)}",
                file=sys.stderr,
            )
            return 1

        items_by_id: dict[str, dict[str, Any]] | None = None
        if args.items is not None:
            item_rows = _read_jsonl(args.items)
            items_by_id = {}
            for item in item_rows:
                if "id" not in item:
                    raise ValueError(f"{args.items}: item row missing id: {item!r}")
                if item["id"] in items_by_id:
                    raise ValueError(f"{args.items}: duplicate id {item['id']!r}")
                items_by_id[item["id"]] = item

        final_rows = build_final_rows(adjudication_rows, items_by_id)

        agree_count = sum(1 for r in adjudication_rows if r["resolution"] == "agree")
        adjudicated_count = sum(
            1 for r in adjudication_rows if r["resolution"] == "adjudicated"
        )

        args.adjudication_out.parent.mkdir(parents=True, exist_ok=True)
        args.final_out.parent.mkdir(parents=True, exist_ok=True)
        with args.adjudication_out.open("w", encoding="utf-8") as fh:
            for row in adjudication_rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        with args.final_out.open("w", encoding="utf-8") as fh:
            for row in final_rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

        print(
            f"resolved {len(adjudication_rows)} items: agree={agree_count} adjudicated={adjudicated_count}"
        )
        return 0
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
