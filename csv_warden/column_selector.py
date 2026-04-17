from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SelectResult:
    input_path: str
    output_path: str
    selected_columns: List[str] = field(default_factory=list)
    missing_columns: List[str] = field(default_factory=list)
    rows_written: int = 0
    error: Optional[str] = None

    def success(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        lines = [
            f"Input:    {self.input_path}",
            f"Output:   {self.output_path}",
            f"Selected: {', '.join(self.selected_columns)}",
            f"Rows:     {self.rows_written}",
        ]
        if self.missing_columns:
            lines.append(f"Skipped (not found): {', '.join(self.missing_columns)}")
        return "\n".join(lines)


def select_columns(input_path: str, output_path: str, columns: List[str]) -> SelectResult:
    result = SelectResult(input_path=input_path, output_path=output_path)
    src = Path(input_path)
    if not src.exists():
        result.error = f"File not found: {input_path}"
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.error = "Empty or invalid CSV file"
            return result

        existing = list(reader.fieldnames)
        keep = [c for c in columns if c in existing]
        result.missing_columns = [c for c in columns if c not in existing]
        result.selected_columns = keep

        if not keep:
            result.error = "None of the specified columns exist in the file"
            return result

        rows = [{col: row[col] for col in keep} for row in reader]

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keep)
        writer.writeheader()
        writer.writerows(rows)

    result.rows_written = len(rows)
    return result
