"""Compute basic statistics for numeric columns in a CSV file."""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ColumnStats:
    name: str
    count: int = 0
    missing: int = 0
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    mean: Optional[float] = None
    stddev: Optional[float] = None


@dataclass
class StatsResult:
    columns: Dict[str, ColumnStats] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def success(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        lines = []
        for col, s in self.columns.items():
            lines.append(
                f"{col}: count={s.count}, missing={s.missing}, "
                f"min={s.min_val}, max={s.max_val}, "
                f"mean={round(s.mean, 4) if s.mean is not None else None}, "
                f"stddev={round(s.stddev, 4) if s.stddev is not None else None}"
            )
        if self.skipped:
            lines.append(f"Skipped (non-numeric): {', '.join(self.skipped)}")
        return "\n".join(lines)


def column_stats(input_path: str, columns: Optional[List[str]] = None) -> StatsResult:
    result = StatsResult()
    path = Path(input_path)
    if not path.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or missing header.")
            return result

        target = columns if columns else list(reader.fieldnames)
        values: Dict[str, List[float]] = {c: [] for c in target}
        missing: Dict[str, int] = {c: 0 for c in target}

        for row in reader:
            for col in target:
                raw = row.get(col, "")
                if raw is None or raw.strip() == "":
                    missing[col] += 1
                else:
                    try:
                        values[col].append(float(raw))
                    except ValueError:
                        if col not in result.skipped:
                            result.skipped.append(col)

    for col in target:
        if col in result.skipped:
            continue
        vals = values[col]
        n = len(vals)
        total_count = n + missing[col]
        mean = sum(vals) / n if n else None
        variance = sum((v - mean) ** 2 for v in vals) / n if n > 1 else 0.0
        result.columns[col] = ColumnStats(
            name=col,
            count=total_count,
            missing=missing[col],
            min_val=min(vals) if vals else None,
            max_val=max(vals) if vals else None,
            mean=mean,
            stddev=math.sqrt(variance) if n > 1 else None,
        )
    return result
