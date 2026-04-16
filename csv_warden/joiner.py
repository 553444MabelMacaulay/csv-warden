from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class JoinResult:
    left_rows: int = 0
    right_rows: int = 0
    output_rows: int = 0
    join_type: str = "inner"
    errors: List[str] = field(default_factory=list)


def summary(r: JoinResult) -> str:
    lines = [
        f"Join type   : {r.join_type}",
        f"Left rows   : {r.left_rows}",
        f"Right rows  : {r.right_rows}",
        f"Output rows : {r.output_rows}",
    ]
    if r.errors:
        lines.append("Errors:")
        lines.extend(f"  - {e}" for e in r.errors)
    return "\n".join(lines)


def _read(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        headers = reader.fieldnames or []
    return list(headers), rows


def join_csv(
    left_path: Path,
    right_path: Path,
    key: str,
    output_path: Path,
    join_type: str = "inner",
) -> JoinResult:
    result = JoinResult(join_type=join_type)

    if not left_path.exists():
        result.errors.append(f"Left file not found: {left_path}")
        return result
    if not right_path.exists():
        result.errors.append(f"Right file not found: {right_path}")
        return result

    left_headers, left_rows = _read(left_path)
    right_headers, right_rows = _read(right_path)
    result.left_rows = len(left_rows)
    result.right_rows = len(right_rows)

    if key not in left_headers:
        result.errors.append(f"Key '{key}' not in left file columns")
        return result
    if key not in right_headers:
        result.errors.append(f"Key '{key}' not in right file columns")
        return result

    right_index: dict[str, list[dict]] = {}
    for row in right_rows:
        k = row[key]
        right_index.setdefault(k, []).append(row)

    extra_cols = [c for c in right_headers if c != key]
    out_headers = left_headers + extra_cols
    out_rows: list[dict] = []

    for lrow in left_rows:
        k = lrow[key]
        matches = right_index.get(k, [])
        if matches:
            for rrow in matches:
                merged = {**lrow, **{c: rrow[c] for c in extra_cols}}
                out_rows.append(merged)
        elif join_type == "left":
            merged = {**lrow, **{c: "" for c in extra_cols}}
            out_rows.append(merged)

    if join_type == "right":
        left_keys = {r[key] for r in left_rows}
        left_cols = [c for c in left_headers if c != key]
        for rrow in right_rows:
            if rrow[key] not in left_keys:
                merged = {**{c: "" for c in left_cols}, **rrow}
                out_rows.append(merged)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_headers)
        writer.writeheader()
        writer.writerows(out_rows)

    result.output_rows = len(out_rows)
    return result
