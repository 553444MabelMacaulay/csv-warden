# csv-warden

> A lightweight CLI tool for validating, profiling, and sanitizing CSV files before ingestion into pipelines.

---

## Installation

```bash
pip install csv-warden
```

Or install from source:

```bash
git clone https://github.com/yourname/csv-warden.git && cd csv-warden && pip install .
```

---

## Usage

```bash
# Validate a CSV file against a schema
csv-warden validate data.csv --schema schema.json

# Profile a CSV file (summary stats, null counts, type inference)
csv-warden profile data.csv

# Sanitize a CSV file (trim whitespace, normalize encoding, drop empty rows)
csv-warden sanitize data.csv --output clean_data.csv
```

**Example output:**

```
✔ Columns validated: 12/12
✔ No null violations found
⚠ 3 rows dropped (empty)
✔ Output written to clean_data.csv
```

---

## Features

- Schema-based column and type validation
- Automatic profiling with null counts and data type inference
- Sanitization with configurable rules
- Fast and dependency-light — works great in CI/CD pipelines

---

## License

This project is licensed under the [MIT License](LICENSE).