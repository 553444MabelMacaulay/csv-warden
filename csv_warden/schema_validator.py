"""Schema validation for CSV files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import csv

COLUMN_TYPES = {"int", "float", "str", "bool"}


@dataclass
class SchemaResult:
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    rows_checked: int = 0

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.valid = False

    def summary(self) -> str:
        status = "PASS" if self.valid else "FAIL"
        lines = [f"Schema validation: {status}", f"  Rows checked : {self.rows_checked}"]
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        return "\n".join(lines)


def _cast(value: str, typ: str) -> bool:
    try:
        if typ == "int":
            int(value)
        elif typ == "float":
            float(value)
        elif typ == "bool":
            if value.lower() not in {"true", "false", "1", "0"}:
                return False
        return True
    except ValueError:
        return False


def validate_schema(
    input_path: str,
    schema: Dict[str, str],
    required: Optional[List[str]] = None,
) -> SchemaResult:
    """Validate CSV rows against a column-type schema."""
    result = SchemaResult()
    required = required or []

    for col, typ in schema.items():
        if typ not in COLUMN_TYPES:
            result.add_error(f"Unknown type '{typ}' for column '{col}'")
    if not result.valid:
        return result

    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                result.add_error("File is empty or has no header")
                return result
            headers = list(reader.fieldnames)
            for col in required:
                if col not in headers:
                    result.add_error(f"Required column '{col}' is missing")
            for row_num, row in enumerate(reader, start=2):
                result.rows_checked += 1
                for col, typ in schema.items():
                    if col not in row:
                        continue
                    val = (row[col] or "").strip()
                    if val == "":
                        if col in required:
                            result.add_error(f"Row {row_num}: required column '{col}' is empty")
                        continue
                    if not _cast(val, typ):
                        result.add_error(f"Row {row_num}: '{col}' value '{val}' is not {typ}")
    except FileNotFoundError:
        result.add_error(f"File not found: {input_path}")
    return result
