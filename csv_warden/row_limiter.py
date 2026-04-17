"""Row limiter: keep only the first or last N rows of a CSV file."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class LimitResult:
    input_path: str
    output_path: str
    mode: str  # 'head' or 'tail'
    n: int
    rows_in: int = 0
    rows_out: int = 0
    errors: list[str] = field(default_factory=list)


def summary(result: LimitResult) -> str:
    lines = [
        f"Input  : {result.input_path}",
        f"Output : {result.output_path}",
        f"Mode   : {result.mode} {result.n}",
        f"Rows in: {result.rows_in}",
        f"Rows out: {result.rows_out}",
    ]
    if result.errors:
        lines += [f"ERROR: {e}" for e in result.errors]
    return "\n".join(lines)


def limit_csv(
    input_path: str,
    output_path: str,
    n: int,
    mode: Literal["head", "tail"] = "head",
) -> LimitResult:
    result = LimitResult(
        input_path=input_path,
        output_path=output_path,
        mode=mode,
        n=n,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or missing header.")
            return result
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    result.rows_in = len(rows)

    if mode == "head":
        selected = rows[:n]
    else:
        selected = rows[-n:] if n <= len(rows) else rows

    result.rows_out = len(selected)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selected)

    return result
