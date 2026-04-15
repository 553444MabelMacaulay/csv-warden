# csv-warden

A lightweight CLI tool for validating, profiling, and sanitizing CSV files
before ingestion into pipelines.

## Installation

```bash
pip install -e .
```

## Commands

### validate
Check a CSV file for common issues (missing headers, empty file, etc.).
```bash
csv-warden validate data.csv
```

### profile
Display column-level statistics (fill rate, unique values, etc.).
```bash
csv-warden profile data.csv
```

### sanitize
Strip whitespace and optionally drop empty rows.
```bash
csv-warden sanitize data.csv clean.csv
csv-warden sanitize data.csv clean.csv --keep-empty-rows
```

### deduplicate
Remove duplicate rows, optionally scoped to a subset of columns.
```bash
csv-warden deduplicate data.csv deduped.csv
csv-warden deduplicate data.csv deduped.csv --subset id email
```

### merge
Concatenate multiple CSV files with compatible schemas.
```bash
csv-warden merge part1.csv part2.csv part3.csv --output merged.csv
```

### transform
Apply built-in transformations to individual columns.

Available transforms: `upper`, `lower`, `strip`, `title`

```bash
csv-warden transform data.csv out.csv --col name=upper
csv-warden transform data.csv out.csv --col name=title --col email=lower
```

## Running Tests

```bash
pytest
```
