#!/usr/bin/env python3
"""Build bronze / silver / gold layers from data/incoming/*.csv.

No values are estimated or invented. Bronze is a byte-identical copy of
the incoming file. Silver is the same 22 rows, validated and sorted
deterministically, with values unchanged. Gold tables are computed
exactly from silver with plain arithmetic (differences and ranks only).

Usage: python3 scripts/build_layers.py
Rebuilds data/bronze/, data/silver/ and data/gold/ for every file in
data/incoming/. Safe to re-run: outputs are overwritten deterministically.
"""
import csv
import shutil
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCOMING = ROOT / "data" / "incoming"
BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold"

# PADD order for deterministic silver sorting of regional rows.
REGION_ORDER = [
    "East Coast (PADD 1)", "New England (1A)", "Central Atlantic (1B)",
    "Lower Atlantic (1C)", "Midwest (PADD 2)", "Gulf Coast (PADD 3)",
    "Rocky Mountain (PADD 4)", "West Coast (PADD 5)",
    "West Coast less California",
]
AREA_TYPE_ORDER = {"national": 0, "region": 1, "state": 2}


def dec(value: str) -> Decimal:
    return Decimal(value)


def fmt(value: Decimal, places: int) -> str:
    return format(value, f".{places}f")


def silver_sort_key(row: dict) -> tuple:
    # EIA first (national, then regions in PADD order), then AAA
    # (national, then states alphabetically).
    if row["source"] == "EIA":
        if row["area_type"] == "national":
            # Regular first, then diesel (not alphabetical).
            area_key = (0, 0 if row["fuel_type"] == "regular" else 1)
        else:
            area_key = (1, REGION_ORDER.index(row["area"]))
        return (0, AREA_TYPE_ORDER[row["area_type"]], area_key)
    return (1, AREA_TYPE_ORDER[row["area_type"]], row["area"])


def build_week(incoming: Path) -> None:
    with incoming.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        rows = list(reader)
    assert header, f"{incoming}: empty file"
    assert len(rows) == 22, f"{incoming}: expected 22 rows, got {len(rows)}"
    assert all(r["price_usd_per_gal"] for r in rows), "blank price in silver input"

    stem = incoming.stem  # e.g. 2026-10-19 (the EIA reading date)

    # --- Bronze: byte-identical copy -----------------------------------
    bronze = BRONZE / incoming.name
    shutil.copyfile(incoming, bronze)

    # --- Silver: same rows, validated, deterministically sorted --------
    silver_rows = sorted(rows, key=silver_sort_key)
    silver = SILVER / incoming.name
    with silver.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(silver_rows)

    # --- Gold -----------------------------------------------------------
    by = {(r["source"], r["area"], r["fuel_type"]): r for r in silver_rows}
    eia_reg = dec(by[("EIA", "United States", "regular")]["price_usd_per_gal"])
    eia_die = dec(by[("EIA", "United States", "diesel")]["price_usd_per_gal"])
    aaa_reg = dec(by[("AAA", "United States", "regular")]["price_usd_per_gal"])
    eia_date = by[("EIA", "United States", "regular")]["reading_date"]
    aaa_date = by[("AAA", "United States", "regular")]["reading_date"]

    # 1. National summary: one row, all values computed from silver.
    with (GOLD / f"national_summary_{stem}.csv").open(
            "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "eia_reading_date", "aaa_reading_date", "eia_regular_usd_per_gal",
            "eia_diesel_usd_per_gal", "diesel_minus_regular_usd_per_gal",
            "aaa_regular_usd_per_gal", "aaa_minus_eia_regular_usd_per_gal",
            "eia_regular_week_change_usd", "eia_regular_year_change_usd",
            "eia_diesel_week_change_usd", "eia_diesel_year_change_usd",
            "notes",
        ])
        writer.writeheader()
        writer.writerow({
            "eia_reading_date": eia_date,
            "aaa_reading_date": aaa_date,
            "eia_regular_usd_per_gal": fmt(eia_reg, 3),
            "eia_diesel_usd_per_gal": fmt(eia_die, 3),
            "diesel_minus_regular_usd_per_gal": fmt(eia_die - eia_reg, 3),
            "aaa_regular_usd_per_gal": fmt(aaa_reg, 4),
            "aaa_minus_eia_regular_usd_per_gal": fmt(aaa_reg - eia_reg, 4),
            "eia_regular_week_change_usd":
                by[("EIA", "United States", "regular")]["change_vs_prior_week_usd"],
            "eia_regular_year_change_usd":
                by[("EIA", "United States", "regular")]["change_vs_year_ago_usd"],
            "eia_diesel_week_change_usd":
                by[("EIA", "United States", "diesel")]["change_vs_prior_week_usd"],
            "eia_diesel_year_change_usd":
                by[("EIA", "United States", "diesel")]["change_vs_year_ago_usd"],
            "notes": "EIA and AAA reading dates differ; see reading_date columns. "
                     "Differences are exact arithmetic on published prices.",
        })

    # 2. Regional ranking: cheapest to most expensive, vs US average.
    regions = [r for r in silver_rows
               if r["source"] == "EIA" and r["area_type"] == "region"]
    regions.sort(key=lambda r: dec(r["price_usd_per_gal"]))
    with (GOLD / f"regional_ranking_{stem}.csv").open(
            "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rank_cheapest_to_most_expensive", "region",
            "regular_usd_per_gal", "diff_vs_us_regular_usd_per_gal",
            "week_change_usd", "year_change_usd", "reading_date",
        ])
        writer.writeheader()
        for i, r in enumerate(regions, start=1):
            price = dec(r["price_usd_per_gal"])
            writer.writerow({
                "rank_cheapest_to_most_expensive": i,
                "region": r["area"],
                "regular_usd_per_gal": fmt(price, 3),
                "diff_vs_us_regular_usd_per_gal": fmt(price - eia_reg, 3),
                "week_change_usd": r["change_vs_prior_week_usd"],
                "year_change_usd": r["change_vs_year_ago_usd"],
                "reading_date": r["reading_date"],
            })

    # 3. State snapshot: AAA states, cheapest to most expensive, vs AAA US.
    states = [r for r in silver_rows
              if r["source"] == "AAA" and r["area_type"] == "state"]
    states.sort(key=lambda r: dec(r["price_usd_per_gal"]))
    with (GOLD / f"state_snapshot_{stem}.csv").open(
            "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rank_cheapest_to_most_expensive", "state",
            "regular_usd_per_gal", "diff_vs_aaa_us_average_usd_per_gal",
            "reading_date",
        ])
        writer.writeheader()
        for i, r in enumerate(states, start=1):
            price = dec(r["price_usd_per_gal"])
            writer.writerow({
                "rank_cheapest_to_most_expensive": i,
                "state": r["area"],
                "regular_usd_per_gal": fmt(price, 4),
                "diff_vs_aaa_us_average_usd_per_gal": fmt(price - aaa_reg, 4),
                "reading_date": r["reading_date"],
            })

    print(f"{stem}: bronze 22 rows, silver 22 rows, "
          f"gold national 1 row, regions {len(regions)} rows, "
          f"states {len(states)} rows")


def main() -> None:
    for d in (BRONZE, SILVER, GOLD):
        d.mkdir(parents=True, exist_ok=True)
    files = sorted(INCOMING.glob("*.csv"))
    assert files, "no files in data/incoming/"
    for f in files:
        build_week(f)
    print(f"OK: built layers for {len(files)} week(s)")


if __name__ == "__main__":
    main()
