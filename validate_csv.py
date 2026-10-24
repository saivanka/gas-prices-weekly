#!/usr/bin/env python3
"""Validate weekly gas price CSVs against the fixed schema.

Usage: python3 scripts/validate_csv.py data/incoming/YYYY-MM-DD.csv [more.csv ...]
Exits 0 when every file is valid, 1 otherwise. No third-party dependencies.
"""
import csv
import re
import sys
from datetime import date
from pathlib import Path

HEADER = [
    "reading_date", "source", "area", "area_type", "fuel_type",
    "price_usd_per_gal", "change_vs_prior_week_usd",
    "change_vs_year_ago_usd", "source_url", "captured_at_utc", "notes",
]
SOURCES = {"EIA", "AAA"}
AREA_TYPES = {"national", "region", "state"}
FUEL_TYPES = {"regular", "diesel"}
NUM_RE = re.compile(r"^-?\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != HEADER:
            return [f"{path}: header mismatch: {reader.fieldnames}"]
        seen = set()
        for i, row in enumerate(reader, start=2):
            where = f"{path}:{i}"
            if not DATE_RE.match(row["reading_date"] or ""):
                errors.append(f"{where}: bad reading_date {row['reading_date']!r}")
            else:
                try:
                    date.fromisoformat(row["reading_date"])
                except ValueError:
                    errors.append(f"{where}: invalid date {row['reading_date']!r}")
            if row["source"] not in SOURCES:
                errors.append(f"{where}: bad source {row['source']!r}")
            if row["area_type"] not in AREA_TYPES:
                errors.append(f"{where}: bad area_type {row['area_type']!r}")
            if row["fuel_type"] not in FUEL_TYPES:
                errors.append(f"{where}: bad fuel_type {row['fuel_type']!r}")
            if not row["area"].strip():
                errors.append(f"{where}: blank area")
            price = row["price_usd_per_gal"]
            if price and not NUM_RE.match(price):
                errors.append(f"{where}: bad price {price!r} (number, no $ sign, or blank)")
            if not price and not row["notes"].strip():
                errors.append(f"{where}: blank price requires an explanation in notes")
            for col in ("change_vs_prior_week_usd", "change_vs_year_ago_usd"):
                v = row[col]
                if v and not NUM_RE.match(v):
                    errors.append(f"{where}: bad {col} {v!r}")
                if v and row["source"] != "EIA":
                    errors.append(f"{where}: {col} is EIA only")
            if not (row["source_url"] or "").startswith("https://"):
                errors.append(f"{where}: source_url must be a full https URL")
            if not TS_RE.match(row["captured_at_utc"] or ""):
                errors.append(f"{where}: bad captured_at_utc {row['captured_at_utc']!r}")
            key = (row["reading_date"], row["source"], row["area"], row["fuel_type"])
            if key in seen:
                errors.append(f"{where}: duplicate row key {key}")
            seen.add(key)
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    all_errors: list[str] = []
    for arg in sys.argv[1:]:
        all_errors += validate(Path(arg))
    if all_errors:
        print("\n".join(all_errors))
        print(f"FAILED: {len(all_errors)} error(s)")
        return 1
    print(f"OK: {len(sys.argv) - 1} file(s) valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
