"""Profile a CSV file for common data-quality problems.

Usage: python profile_data.py <path-to-csv>

Uses only the Python standard library, so it runs without installing anything.
Prints facts only; interpreting them is left to the Skill instructions.
"""

import csv
import re
import statistics
import sys
from collections import Counter

MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-", "?"}

DATE_PATTERNS = {
    "YYYY-MM-DD": re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$"),
    "MM/DD/YYYY or DD/MM/YYYY": re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$"),
    "DD-MM-YYYY": re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$"),
    "Month D, YYYY": re.compile(r"^[A-Za-z]{3,9}\.? \d{1,2},? \d{4}$"),
}


def is_missing(value):
    return value.strip().lower() in MISSING_TOKENS


def to_number(value):
    cleaned = value.strip().replace(",", "").replace("$", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def date_format(value):
    for name, pattern in DATE_PATTERNS.items():
        if pattern.match(value.strip()):
            return name
    return None


def profile_column(name, values):
    present = [v for v in values if not is_missing(v)]
    missing = len(values) - len(present)
    lines = [f"\n## Column: {name}"]
    lines.append(f"- Missing: {missing} of {len(values)} ({missing / max(len(values), 1):.1%})")
    if not present:
        lines.append("- Type: entirely empty")
        return lines

    numbers = [to_number(v) for v in present]
    numeric = [n for n in numbers if n is not None]
    dates = [date_format(v) for v in present]
    date_hits = [d for d in dates if d]

    if len(numeric) >= 0.8 * len(present):
        lines.append("- Type: numeric")
        non_numeric = [v for v, n in zip(present, numbers) if n is None]
        if non_numeric:
            sample = ", ".join(repr(v) for v in non_numeric[:5])
            lines.append(f"- Non-numeric values in numeric column: {len(non_numeric)} (e.g. {sample})")
        if len(numeric) >= 4:
            q1, _, q3 = statistics.quantiles(numeric, n=4)
            iqr = q3 - q1
            low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outliers = [n for n in numeric if n < low or n > high]
            lines.append(f"- Range: min {min(numeric):g}, median {statistics.median(numeric):g}, max {max(numeric):g}")
            if outliers:
                sample = ", ".join(f"{n:g}" for n in sorted(outliers)[:5])
                lines.append(f"- Outliers (outside 1.5x IQR): {len(outliers)} (e.g. {sample})")
        negatives = [n for n in numeric if n < 0]
        if negatives:
            lines.append(f"- Negative values: {len(negatives)}")
    elif len(date_hits) >= 0.6 * len(present):
        formats = Counter(date_hits)
        lines.append("- Type: date")
        if len(formats) > 1:
            detail = ", ".join(f"{fmt}: {count}" for fmt, count in formats.most_common())
            lines.append(f"- MIXED date formats: {detail}")
        unparsed = len(present) - len(date_hits)
        if unparsed:
            lines.append(f"- Values not recognized as dates: {unparsed}")
    else:
        lines.append("- Type: text")
        distinct = Counter(v.strip() for v in present)
        lines.append(f"- Distinct values: {len(distinct)}")
        # Same value written with different capitalization or spacing, e.g. "East" vs "east ".
        groups = {}
        for v in distinct:
            groups.setdefault(v.lower(), []).append(v)
        variants = [vs for vs in groups.values() if len(vs) > 1]
        if variants:
            sample = "; ".join(" / ".join(repr(x) for x in vs) for vs in variants[:3])
            lines.append(f"- Inconsistent capitalization: {len(variants)} groups (e.g. {sample})")
        padded = sum(1 for v in present if v != v.strip())
        if padded:
            lines.append(f"- Values with leading/trailing spaces: {padded}")
    return lines


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python profile_data.py <path-to-csv>")
    path = sys.argv[1]
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        sys.exit(f"{path} is empty.")

    header, data = rows[0], rows[1:]
    print(f"# Profile: {path}")
    print(f"- Rows: {len(data)}  |  Columns: {len(header)}")

    ragged = [i + 2 for i, r in enumerate(data) if len(r) != len(header)]
    if ragged:
        print(f"- Rows with wrong number of fields: {len(ragged)} (file lines {ragged[:5]})")

    counts = Counter(tuple(r) for r in data)
    duplicates = sum(c - 1 for c in counts.values() if c > 1)
    print(f"- Exact duplicate rows: {duplicates}")

    blank_headers = [i + 1 for i, h in enumerate(header) if not h.strip()]
    if blank_headers:
        print(f"- Blank column headers at positions: {blank_headers}")

    for i, name in enumerate(header):
        column = [r[i] if i < len(r) else "" for r in data]
        print("\n".join(profile_column(name or f"(column {i + 1})", column)))


if __name__ == "__main__":
    main()
