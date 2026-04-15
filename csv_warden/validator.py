"""CSV validation module for csv-warden."""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ValidationResult:
    """Holds the outcome of a CSV validation run."""

    filepath: str
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    row_count: int = 0
    column_count: int = 0

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def summary(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        lines = [
            f"File   : {self.filepath}",
            f"Status : {status}",
            f"Rows   : {self.row_count}  |  Columns: {self.column_count}",
        ]
        if self.errors:
            lines.append("Errors:")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append("Warnings:")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)


def validate_csv(
    filepath: str,
    delimiter: str = ",",
    expected_columns: Optional[int] = None,
    required_headers: Optional[List[str]] = None,
) -> ValidationResult:
    """Validate a CSV file for structural integrity."""
    result = ValidationResult(filepath=filepath)
    path = Path(filepath)

    if not path.exists():
        result.add_error(f"File not found: {filepath}")
        return result

    if path.stat().st_size == 0:
        result.add_error("File is empty.")
        return result

    try:
        with open(filepath, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh, delimiter=delimiter)
            headers = next(reader, None)

            if headers is None:
                result.add_error("File has no header row.")
                return result

            result.column_count = len(headers)

            if required_headers:
                missing = [h for h in required_headers if h not in headers]
                if missing:
                    result.add_error(f"Missing required headers: {missing}")

            if expected_columns and result.column_count != expected_columns:
                result.add_error(
                    f"Expected {expected_columns} columns, found {result.column_count}."
                )

            for line_num, row in enumerate(reader, start=2):
                result.row_count += 1
                if len(row) != result.column_count:
                    result.add_warning(
                        f"Row {line_num} has {len(row)} fields; expected {result.column_count}."
                    )

    except UnicodeDecodeError as exc:
        result.add_error(f"Encoding error: {exc}")
    except csv.Error as exc:
        result.add_error(f"CSV parse error: {exc}")

    return result
