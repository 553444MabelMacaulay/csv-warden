from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CountResult:
    input_file: str
    group_column: str
    count_column: Optional[str]
    output_file: str
    rows_in: int = 0
    rows_out: int = 0
    errors: List[str] = field(default_factory=list)

    def success(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = [
            f"Input : {self.input_file}",
            f"Group by : {self.group_column}",
            f"Count column : {self.count_column or '(all rows)'}",
            f"Rows in : {self.rows_in}",
            f"Groups out: {self.rows_out}",
            f"Output : {self.output_file}",
        ]
        if self.errors:
            lines.append("Errors:")
            for e in self.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)


def count_csv(
    input_path: str,
    group_column: str,
    output_path: str,
    count_column: Optional[str] = None,
    result_header: str = "count",
) -> CountResult:
    result = CountResult(
        input_file=input_path,
        group_column=group_column,
        count_column=count_column,
        output_file=output_path,
    )

    p = Path(input_path)
    if not p.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    counts: Dict[str, int] = {}
    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None or group_column not in reader.fieldnames:
                result.errors.append(f"Column '{group_column}' not found in CSV.")
                return result
            if count_column and count_column not in reader.fieldnames:
                result.errors.append(f"Count column '{count_column}' not found in CSV.")
                return result
            for row in reader:
                result.rows_in += 1
                key = row[group_column]
                if count_column:
                    val = row[count_column].strip()
                    if val == "" or val is None:
                        continue
                counts[key] = counts.get(key, 0) + 1
    except Exception as exc:
        result.errors.append(str(exc))
        return result

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=[group_column, result_header])
            writer.writeheader()
            for key, cnt in sorted(counts.items()):
                writer.writerow({group_column: key, result_header: cnt})
        result.rows_out = len(counts)
    except Exception as exc:
        result.errors.append(str(exc))

    return result
