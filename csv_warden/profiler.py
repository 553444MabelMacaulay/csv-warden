"""CSV profiling module: computes basic statistics for each column."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ColumnProfile:
    name: str
    total: int = 0
    missing: int = 0
    unique: int = 0
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    top_values: List[tuple] = field(default_factory=list)

    @property
    def fill_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.total - self.missing) / self.total * 100, 2)


@dataclass
class ProfileReport:
    path: str
    row_count: int
    column_count: int
    columns: Dict[str, ColumnProfile] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Profile: {self.path}",
            f"  Rows   : {self.row_count}",
            f"  Columns: {self.column_count}",
        ]
        for col in self.columns.values():
            lines.append(
                f"  [{col.name}] missing={col.missing} unique={col.unique} "
                f"fill={col.fill_rate}% len={col.min_length}-{col.max_length}"
            )
        return "\n".join(lines)


def profile_csv(path: str, top_n: int = 5) -> ProfileReport:
    """Read *path* and return a :class:`ProfileReport`."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    counters: Dict[str, Counter] = {}
    lengths: Dict[str, List[int]] = {}
    row_count = 0

    with p.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return ProfileReport(path=path, row_count=0, column_count=0)

        headers = list(reader.fieldnames)
        for h in headers:
            counters[h] = Counter()
            lengths[h] = []

        for row in reader:
            row_count += 1
            for h in headers:
                val = row.get(h, "") or ""
                counters[h][val] += 1
                lengths[h].append(len(val))

    columns: Dict[str, ColumnProfile] = {}
    for h in headers:
        c = counters[h]
        missing = c.get("", 0)
        lens = lengths[h]
        col = ColumnProfile(
            name=h,
            total=row_count,
            missing=missing,
            unique=len(c) - (1 if "" in c else 0),
            min_length=min(lens) if lens else None,
            max_length=max(lens) if lens else None,
            top_values=c.most_common(top_n),
        )
        columns[h] = col

    return ProfileReport(
        path=path,
        row_count=row_count,
        column_count=len(headers),
        columns=columns,
    )
