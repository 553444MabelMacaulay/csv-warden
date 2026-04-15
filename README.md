# csv-warden

A lightweight CLI tool for validating, profiling, and sanitizing CSV files before ingestion into pipelines.

## Installation

```bash
pip install -e .
```

## Commands

### validate
```bash
csv-warden validate data.csv [--max-rows N]
```

### profile
```bash
csv-warden profile data.csv
```

### sanitize
```bash
csv-warden sanitize data.csv [--output clean.csv] [--keep-empty-rows]
```

### deduplicate
```bash
csv-warden deduplicate data.csv [--output deduped.csv] [--subset col1 col2]
```

### merge
```bash
csv-warden merge file1.csv file2.csv --output merged.csv
```

### transform
```bash
csv-warden transform data.csv --transform upper [--columns name city] [--output out.csv]
```

Supported transforms: `upper`, `lower`, `strip`, `title`.

### filter
```bash
csv-warden filter data.csv --column status --value active [--output out.csv] [--exclude]
```

### sort
```bash
csv-warden sort data.csv --column score [--output out.csv] [--descending]
```

### aggregate
```bash
csv-warden aggregate data.csv <column> <func>
```

Supported functions: `sum`, `mean`, `min`, `max`, `count`.

**Example**
```bash
csv-warden aggregate sales.csv revenue sum
# Result: 142300.0
```

Non-numeric and empty cells are skipped with a warning.

## Development

```bash
pip install -e .[dev]
pytest
```

## License

MIT
