from __future__ import annotations
import csv
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SampleResult:
    input_file: str
    total_rows: int = 0
    sampled_rows: int = 0
    output_file: Optional[str] = None
    errors: List[str] = field(default_factory=list)


def summary(result: SampleResult) -> str:
    lines = [
        f"Input:        {result.input_file}",
        f"Total rows:   {result.total_rows}",
        f"Sampled rows: {result.sampled_rows}",
    ]
    if result.output_file:
        lines.append(f"Output:       {result.output_file}")
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)


def sample_csv(
    input_path: str,
    output_path: str,
    n: Optional[int] = None,
    fraction: Optional[float] = None,
    seed: Optional[int] = None,
) -> SampleResult:
    result = SampleResult(input_file=input_path)
    path = Path(input_path)

    if not path.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    if n is None and fraction is None:
        result.errors.append("Specify either n or fraction.")
        return result

    if fraction is not None and not (0.0 < fraction <= 1.0):
        result.errors.append("fraction must be between 0 (exclusive) and 1 (inclusive).")
        return result

    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    result.total_rows = len(rows)

    rng = random.Random(seed)

    if fraction is not None:
        n = max(1, int(len(rows) * fraction))

    n = min(n, len(rows))  # type: ignore[arg-type]
    sampled = rng.sample(rows, n)
    result.sampled_rows = len(sampled)
    result.output_file = output_path

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sampled)

    return result
