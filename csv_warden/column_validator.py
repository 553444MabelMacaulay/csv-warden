"""Validate column values against regex patterns or allowed value sets."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ValidateColResult:
    total_rows: int = 0
    errors: List[str] = field(default_factory=list)
    invalid_rows: int = 0

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def summary(result: ValidateColResult) -> str:
    lines = [
        f"Rows checked : {result.total_rows}",
        f"Invalid rows : {result.invalid_rows}",
        f"Status       : {'PASS' if result.success else 'FAIL'}",
    ]
    if result.errors:
        lines.append("Errors:")
        for e in result.errors[:10]:
            lines.append(f"  {e}")
        if len(result.errors) > 10:
            lines.append(f"  ... and {len(result.errors) - 10} more")
    return "\n".join(lines)


def validate_columns(
    input_path: str,
    patterns: Optional[Dict[str, str]] = None,
    allowed: Optional[Dict[str, List[str]]] = None,
) -> ValidateColResult:
    """Validate CSV columns against regex patterns and/or allowed value sets."""
    result = ValidateColResult()
    patterns = patterns or {}
    allowed_sets: Dict[str, Set[str]] = {
        col: set(vals) for col, vals in (allowed or {}).items()
    }
    compiled = {col: re.compile(pat) for col, pat in patterns.items()}

    path = Path(input_path)
    if not path.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result

        for row_num, row in enumerate(reader, start=2):
            result.total_rows += 1
            row_invalid = False

            for col, regex in compiled.items():
                val = row.get(col, "")
                if not regex.fullmatch(val or ""):
                    result.errors.append(
                        f"Row {row_num}: column '{col}' value {val!r} does not match pattern '{patterns[col]}'"
                    )
                    row_invalid = True

            for col, vals in allowed_sets.items():
                val = row.get(col, "")
                if val not in vals:
                    result.errors.append(
                        f"Row {row_num}: column '{col}' value {val!r} not in allowed set"
                    )
                    row_invalid = True

            if row_invalid:
                result.invalid_rows += 1

    return result
