"""One-hot encode a categorical column into multiple binary columns."""
from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class EncodeColResult:
    input_file: str
    column: str
    new_columns: List[str] = field(default_factory=list)
    rows_processed: int = 0
    dropped_original: bool = False
    error: Optional[str] = None

    def success(self) -> bool:
        return self.error is None


def summary(result: EncodeColResult) -> str:
    if not result.success():
        return f"[ERROR] {result.error}"
    lines = [
        f"One-hot encode: {result.input_file}",
        f"  Column      : {result.column}",
        f"  New columns : {', '.join(result.new_columns)}",
        f"  Rows        : {result.rows_processed}",
        f"  Drop original: {result.dropped_original}",
    ]
    return "\n".join(lines)


def onehot_encode_csv(
    input_path: str,
    output_path: str,
    column: str,
    prefix: str = "",
    drop_original: bool = False,
) -> EncodeColResult:
    result = EncodeColResult(input_file=input_path, column=column, dropped_original=drop_original)

    src = Path(input_path)
    if not src.exists():
        result.error = f"File not found: {input_path}"
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.error = "Empty or invalid CSV"
            return result
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    if column not in fieldnames:
        result.error = f"Column '{column}' not found"
        return result

    unique_vals = sorted({r[column] for r in rows if r[column] not in ("", None)})
    col_prefix = prefix if prefix else column
    new_cols = [f"{col_prefix}_{v}" for v in unique_vals]
    result.new_columns = new_cols

    out_fields = list(fieldnames)
    if drop_original:
        out_fields.remove(column)
    out_fields.extend(new_cols)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            val = row[column]
            for v in unique_vals:
                row[f"{col_prefix}_{v}"] = "1" if val == v else "0"
            if drop_original:
                del row[column]
            writer.writerow(row)
            result.rows_processed += 1

    return result
