"""Reverse the string values in one or more CSV columns."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ReverseResult:
    input_path: str
    output_path: str
    columns: List[str]
    rows_processed: int = 0
    rows_affected: int = 0
    skipped_columns: List[str] = field(default_factory=list)
    error: Optional[str] = None


def summary(result: ReverseResult) -> str:
    lines = [
        f"Input : {result.input_path}",
        f"Output: {result.output_path}",
        f"Target columns : {', '.join(result.columns)}",
    ]
    if result.skipped_columns:
        lines.append(f"Skipped (not found): {', '.join(result.skipped_columns)}")
    if result.error:
        lines.append(f"Error: {result.error}")
    else:
        lines.append(f"Rows processed : {result.rows_processed}")
        lines.append(f"Rows affected  : {result.rows_affected}")
    return "\n".join(lines)


def reverse_csv(
    input_path: str,
    output_path: str,
    columns: List[str],
) -> ReverseResult:
    src = Path(input_path)
    result = ReverseResult(
        input_path=input_path,
        output_path=output_path,
        columns=columns,
    )

    if not src.exists():
        result.error = f"File not found: {input_path}"
        return result

    try:
        with src.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                result.error = "CSV file has no headers."
                return result

            headers = list(reader.fieldnames)
            active = [c for c in columns if c in headers]
            result.skipped_columns = [c for c in columns if c not in headers]

            rows = list(reader)

        out_rows = []
        for row in rows:
            new_row = dict(row)
            changed = False
            for col in active:
                original = row[col]
                reversed_val = original[::-1]
                new_row[col] = reversed_val
                if reversed_val != original:
                    changed = True
            out_rows.append(new_row)
            result.rows_processed += 1
            if changed:
                result.rows_affected += 1

        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=headers)
            writer.writeheader()
            writer.writerows(out_rows)

    except Exception as exc:  # noqa: BLE001
        result.error = str(exc)

    return result
