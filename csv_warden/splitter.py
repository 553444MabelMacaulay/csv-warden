"""Split a CSV file into multiple files based on a column value or row count."""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    input_file: str
    output_files: List[str] = field(default_factory=list)
    rows_written: int = 0
    chunks: int = 0
    errors: List[str] = field(default_factory=list)


def summary(result: SplitResult) -> str:
    lines = [
        f"Input : {result.input_file}",
        f"Chunks: {result.chunks}",
        f"Rows written: {result.rows_written}",
    ]
    if result.output_files:
        lines.append("Output files:")
        for f in result.output_files:
            lines.append(f"  {f}")
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)


def split_csv(
    input_path: str,
    output_dir: str,
    *,
    column: Optional[str] = None,
    chunk_size: Optional[int] = None,
) -> SplitResult:
    """Split *input_path* into multiple CSV files.

    Exactly one of *column* or *chunk_size* must be provided.
    - column    : one output file per unique value in that column.
    - chunk_size: one output file per N rows (header excluded).
    """
    result = SplitResult(input_file=input_path)

    if not Path(input_path).exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if column is None and chunk_size is None:
        result.errors.append("Provide either 'column' or 'chunk_size'.")
        return result

    if column is not None and chunk_size is not None:
        result.errors.append("Provide only one of 'column' or 'chunk_size', not both.")
        return result

    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("CSV has no header row.")
            return result
        headers = list(reader.fieldnames)
        rows = list(reader)

    if column is not None:
        if column not in headers:
            result.errors.append(f"Column '{column}' not found in CSV.")
            return result
        buckets: Dict[str, List[dict]] = {}
        for row in rows:
            key = row[column]
            buckets.setdefault(key, []).append(row)
        for key, bucket_rows in buckets.items():
            safe_key = key.replace(os.sep, "_").replace(" ", "_")
            out_path = os.path.join(output_dir, f"{safe_key}.csv")
            _write_rows(out_path, headers, bucket_rows)
            result.output_files.append(out_path)
            result.rows_written += len(bucket_rows)
        result.chunks = len(buckets)
    else:
        assert chunk_size is not None
        if chunk_size < 1:
            result.errors.append("chunk_size must be >= 1.")
            return result
        chunk_index = 0
        for i in range(0, len(rows), chunk_size):
            chunk_rows = rows[i : i + chunk_size]
            out_path = os.path.join(output_dir, f"chunk_{chunk_index:04d}.csv")
            _write_rows(out_path, headers, chunk_rows)
            result.output_files.append(out_path)
            result.rows_written += len(chunk_rows)
            chunk_index += 1
        result.chunks = chunk_index

    return result


def _write_rows(out_path: str, headers: List[str], rows: List[dict"Write *rows* to *out_path* as a CSV file with the given *headers*."""
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
