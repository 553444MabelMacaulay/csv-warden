"""Apply a shell command or Python expression to each value in a column."""
from __future__ import annotations

import csv
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RunResult:
    input_path: str
    output_path: str
    column: str
    rows_processed: int = 0
    rows_failed: int = 0
    errors: list[str] = field(default_factory=list)


def summary(r: RunResult) -> str:
    lines = [
        f"Input : {r.input_path}",
        f"Output: {r.output_path}",
        f"Column: {r.column}",
        f"Processed: {r.rows_processed}  Failed: {r.rows_failed}",
    ]
    if r.errors:
        lines.append("Errors:")
        for e in r.errors[:5]:
            lines.append(f"  {e}")
    return "\n".join(lines)


def run_column(
    input_path: str,
    output_path: str,
    column: str,
    cmd_template: str,
    new_column: Optional[str] = None,
    shell: bool = False,
) -> RunResult:
    """For each row, substitute {value} in cmd_template and run it.
    The stdout of the command becomes the new cell value.
    If new_column is given, the result is placed in a new column.
    """
    src = Path(input_path)
    if not src.exists():
        r = RunResult(input_path, output_path, column)
        r.errors.append(f"File not found: {input_path}")
        return r

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            r = RunResult(input_path, output_path, column)
            r.errors.append("Empty or header-less file.")
            return r
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            r = RunResult(input_path, output_path, column)
            r.errors.append(f"Column '{column}' not found.")
            return r

        target = new_column or column
        out_fields = fieldnames if target in fieldnames else fieldnames + [target]

        rows_out = []
        result = RunResult(input_path, output_path, column)
        for row in reader:
            value = row[column]
            cmd = cmd_template.replace("{value}", value)
            try:
                proc = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=10
                )
                row[target] = proc.stdout.strip()
                result.rows_processed += 1
            except Exception as exc:  # noqa: BLE001
                row[target] = value
                result.rows_failed += 1
                result.errors.append(f"Row error: {exc}")
            rows_out.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows_out)

    return result
