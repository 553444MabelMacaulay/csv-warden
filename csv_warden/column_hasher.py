"""column_hasher.py – hash one or more columns using md5/sha256."""
from __future__ import annotations
import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class HashResult:
    columns: List[str] = field(default_factory=list)
    rows_processed: int = 0
    algorithm: str = "sha256"
    errors: List[str] = field(default_factory=list)


def summary(r: HashResult) -> str:
    lines = [
        f"Algorithm : {r.algorithm}",
        f"Columns   : {', '.join(r.columns)}",
        f"Rows      : {r.rows_processed}",
    ]
    if r.errors:
        lines.append(f"Errors    : {len(r.errors)}")
        lines.extend(f"  {e}" for e in r.errors)
    return "\n".join(lines)


def _hash(value: str, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    h.update(value.encode("utf-8"))
    return h.hexdigest()


def hash_csv(
    input_path: str,
    output_path: str,
    columns: List[str],
    algorithm: str = "sha256",
    suffix: str = "_hashed",
    replace: bool = False,
) -> HashResult:
    result = HashResult(columns=columns, algorithm=algorithm)
    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result
    if algorithm not in hashlib.algorithms_available:
        result.errors.append(f"Unsupported algorithm: {algorithm}")
        return result

    rows: list = []
    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file")
            return result
        fieldnames = list(reader.fieldnames)
        missing = [c for c in columns if c not in fieldnames]
        if missing:
            result.errors.append(f"Columns not found: {', '.join(missing)}")
            return result

        if replace:
            out_fields = fieldnames
        else:
            extra = [c + suffix for c in columns]
            out_fields = fieldnames + extra

        for row in reader:
            new_row = dict(row)
            for col in columns:
                hashed = _hash(row.get(col, ""), algorithm)
                if replace:
                    new_row[col] = hashed
                else:
                    new_row[col + suffix] = hashed
            rows.append(new_row)
            result.rows_processed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    return result
