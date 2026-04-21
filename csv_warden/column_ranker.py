"""Rank values in a numeric column (dense, min, or percent rank)."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

SUPPORTED_METHODS = ("dense", "min", "percent")


@dataclass
class RankResult:
    input_file: str
    output_file: str
    column: str
    method: str
    rows_ranked: int = 0
    rows_skipped: int = 0
    errors: List[str] = field(default_factory=list)


def summary(r: RankResult) -> str:
    lines = [
        f"Input : {r.input_file}",
        f"Output: {r.output_file}",
        f"Column: {r.column}  method={r.method}",
        f"Ranked: {r.rows_ranked}  Skipped: {r.rows_skipped}",
    ]
    if r.errors:
        lines.append("Errors:")
        lines.extend(f"  {e}" for e in r.errors)
    return "\n".join(lines)


def rank_csv(
    input_path: str,
    output_path: str,
    column: str,
    method: str = "dense",
    new_column: Optional[str] = None,
    ascending: bool = True,
) -> RankResult:
    src = Path(input_path)
    result = RankResult(
        input_file=input_path,
        output_file=output_path,
        column=column,
        method=method,
    )

    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if method not in SUPPORTED_METHODS:
        result.errors.append(f"Unsupported method '{method}'. Choose from: {SUPPORTED_METHODS}")
        return result

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    if column not in fieldnames:
        result.errors.append(f"Column '{column}' not found.")
        return result

    rank_col = new_column or f"{column}_rank"

    # Parse numeric values; track indices of parseable rows
    values: List[tuple] = []  # (original_index, float_value)
    for i, row in enumerate(rows):
        raw = row.get(column, "").strip()
        try:
            values.append((i, float(raw)))
        except ValueError:
            result.rows_skipped += 1

    sorted_vals = sorted(values, key=lambda x: x[1], reverse=not ascending)

    rank_map: dict = {}
    if method == "dense":
        rank = 1
        prev: Optional[float] = None
        for idx, (orig_i, val) in enumerate(sorted_vals):
            if prev is None or val != prev:
                rank = len(rank_map) + 1
            rank_map[orig_i] = rank
            prev = val
    elif method == "min":
        # group equal values, assign min position
        pos = 1
        prev = None
        group_start = 1
        for idx, (orig_i, val) in enumerate(sorted_vals):
            if val != prev:
                group_start = pos
            rank_map[orig_i] = group_start
            prev = val
            pos += 1
    elif method == "percent":
        n = len(sorted_vals)
        for pos, (orig_i, _) in enumerate(sorted_vals):
            rank_map[orig_i] = round((pos + 1) / n, 6) if n else 0.0

    out_fieldnames = fieldnames + ([rank_col] if rank_col not in fieldnames else [])
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fieldnames)
        writer.writeheader()
        for i, row in enumerate(rows):
            row[rank_col] = str(rank_map[i]) if i in rank_map else ""
            if i in rank_map:
                result.rows_ranked += 1
            writer.writerow(row)

    return result
