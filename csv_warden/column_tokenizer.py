"""Split a text column into token-count and unique-token-count columns."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TokenizeResult:
    input_path: str
    column: str
    rows_processed: int = 0
    rows_failed: int = 0
    errors: list[str] = field(default_factory=list)


def summary(r: TokenizeResult) -> str:
    lines = [
        f"Input       : {r.input_path}",
        f"Column      : {r.column}",
        f"Processed   : {r.rows_processed}",
        f"Failed      : {r.rows_failed}",
    ]
    if r.errors:
        lines.append("Errors      :")
        for e in r.errors[:5]:
            lines.append(f"  {e}")
    return "\n".join(lines)


def _tokenize(text: str) -> tuple[int, int]:
    tokens = re.findall(r"\b\w+\b", text.lower())
    return len(tokens), len(set(tokens))


def tokenize_csv(
    input_path: str,
    output_path: str,
    column: str,
    count_col: str = "token_count",
    unique_col: str = "unique_token_count",
    encoding: str = "utf-8",
) -> TokenizeResult:
    result = TokenizeResult(input_path=input_path, column=column)
    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding=encoding) as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or unreadable CSV.")
            return result
        fieldnames = list(reader.fieldnames)
        if column not in fieldnames:
            result.errors.append(f"Column '{column}' not found.")
            return result
        fieldnames += [count_col, unique_col]
        rows: list[dict] = []
        for i, row in enumerate(reader, 1):
            val = row.get(column, "") or ""
            try:
                tc, uc = _tokenize(val)
                row[count_col] = str(tc)
                row[unique_col] = str(uc)
                result.rows_processed += 1
            except Exception as exc:  # pragma: no cover
                row[count_col] = ""
                row[unique_col] = ""
                result.rows_failed += 1
                result.errors.append(f"Row {i}: {exc}")
            rows.append(row)

    with open(output_path, "w", newline="", encoding=encoding) as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return result
