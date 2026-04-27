"""column_smoother.py – apply a moving-average (Gaussian or simple) smoothing to a numeric column."""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SmoothResult:
    input_path: str
    output_path: str
    column: str
    method: str
    window: int
    rows_smoothed: int = 0
    rows_skipped: int = 0
    errors: List[str] = field(default_factory=list)


def summary(r: SmoothResult) -> str:
    lines = [
        f"Input  : {r.input_path}",
        f"Output : {r.output_path}",
        f"Column : {r.column}  method={r.method}  window={r.window}",
        f"Smoothed rows : {r.rows_smoothed}",
        f"Skipped rows  : {r.rows_skipped}",
    ]
    if r.errors:
        lines.append("Errors:")
        lines.extend(f"  {e}" for e in r.errors)
    return "\n".join(lines)


def _gaussian_weights(window: int) -> List[float]:
    """Return normalised Gaussian weights for a given half-window."""
    sigma = window / 2.0
    weights = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-window, window + 1)]
    total = sum(weights)
    return [w / total for w in weights]


def smooth_csv(
    input_path: str,
    output_path: str,
    column: str,
    window: int = 3,
    method: str = "mean",
) -> SmoothResult:
    """Smooth *column* in *input_path* and write to *output_path*.

    Parameters
    ----------
    method : 'mean' | 'gaussian'
    window : half-window size (full window = 2*window+1)
    """
    result = SmoothResult(
        input_path=input_path,
        output_path=output_path,
        column=column,
        method=method,
        window=window,
    )

    src = Path(input_path)
    if not src.exists():
        result.errors.append(f"File not found: {input_path}")
        return result

    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            result.errors.append("Empty or header-less file.")
            return result
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    if column not in fieldnames:
        result.errors.append(f"Column '{column}' not found.")
        return result

    if method not in ("mean", "gaussian"):
        result.errors.append(f"Unknown method '{method}'. Use 'mean' or 'gaussian'.")
        return result

    # Parse numeric values; keep None for non-parseable cells
    values: List[Optional[float]] = []
    for row in rows:
        raw = row[column].strip()
        try:
            values.append(float(raw))
        except (ValueError, AttributeError):
            values.append(None)

    weights = _gaussian_weights(window) if method == "gaussian" else None
    n = len(values)

    for i, row in enumerate(rows):
        if values[i] is None:
            result.rows_skipped += 1
            continue
        lo, hi = max(0, i - window), min(n - 1, i + window)
        segment = values[lo : hi + 1]
        valid = [(j, v) for j, v in enumerate(segment) if v is not None]
        if not valid:
            result.rows_skipped += 1
            continue
        if method == "gaussian" and weights is not None:
            offset = i - lo
            full_len = 2 * window + 1
            w_slice = weights[window - offset : window - offset + len(segment)]
            w_valid = [w_slice[j] for j, _ in valid]
            w_sum = sum(w_valid)
            smoothed = sum(v * w_valid[k] for k, (_, v) in enumerate(valid)) / w_sum
        else:
            smoothed = sum(v for _, v in valid) / len(valid)
        row[column] = f"{smoothed:.6g}"
        result.rows_smoothed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return result
