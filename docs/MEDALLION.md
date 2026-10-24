# Bronze, Silver, Gold — How to Use This Dataset

This dataset is published in three layers. Start with **Gold** if you
just want answers, **Silver** if you want to analyse, and **Bronze**
if you want to audit. All three are built from the same weekly file in
`data/incoming/` by `scripts/build_layers.py` — re-running that script
reproduces them exactly.

```
data/incoming/YYYY-MM-DD.csv   weekly file, as collected (landing)
  └─► data/bronze/YYYY-MM-DD.csv      raw, archived
  └─► data/silver/YYYY-MM-DD.csv      cleaned, validated
        └─► data/gold/national_summary_YYYY-MM-DD.csv
        └─► data/gold/regional_ranking_YYYY-MM-DD.csv
        └─► data/gold/state_snapshot_YYYY-MM-DD.csv
```

On Kaggle the same files appear with layer prefixes, because Kaggle's
file list is flat:
`bronze_YYYY-MM-DD.csv`, `silver_YYYY-MM-DD.csv`,
`gold_national_summary_YYYY-MM-DD.csv`,
`gold_regional_ranking_YYYY-MM-DD.csv`,
`gold_state_snapshot_YYYY-MM-DD.csv`.

## Bronze — raw, exactly as published

- **File:** `data/bronze/YYYY-MM-DD.csv`
- **What it is:** a byte-identical copy of the incoming weekly file.
- **Schema:** the same 11 columns as the incoming file
  (see [DATA_DICTIONARY.md](DATA_DICTIONARY.md)).
- **Use it for:** audit and traceability. If a number is ever disputed,
  bronze is the evidence — it has not been touched by any cleaning step.
- **Rule:** never edit bronze by hand. If the incoming file changes,
  rebuild it with `scripts/build_layers.py`.

## Silver — cleaned, validated, same values

- **File:** `data/silver/YYYY-MM-DD.csv`
- **What changes:** nothing about the values. Silver is the same 22 rows
  with the same prices, changes, source URLs and notes, only:
  - validated (header, dates, allowed values, numeric-or-blank prices,
    EIA-only change columns, full https source URLs, row uniqueness —
    the same checks as `scripts/validate_csv.py`), and
  - sorted deterministically: EIA national (regular, then diesel),
    EIA regions in PADD order, AAA national, then AAA states
    alphabetically.
- **What does NOT change:** no row is added, dropped, imputed or
  corrected; no price is rounded, converted or filled from the other
  source. A blank price in bronze is still blank in silver.
- **Use it for:** analysis, joins and charts. This is the table to load
  in pandas, DuckDB or a spreadsheet.

```python
import pandas as pd
silver = pd.read_csv("silver_2026-10-19.csv", parse_dates=["reading_date"])
silver[silver.source == "EIA"].sort_values("price_usd_per_gal")
```

## Gold — curated, ready to read

Gold tables contain **only** exact arithmetic on silver: differences
and ranks. No modelling, no forecasting, no seasonal adjustment.

### 1. National summary — `gold/national_summary_YYYY-MM-DD.csv` (1 row)

| Column | Meaning |
|---|---|
| `eia_reading_date`, `aaa_reading_date` | The two reading dates (they differ — EIA weekly vs AAA daily) |
| `eia_regular_usd_per_gal`, `eia_diesel_usd_per_gal` | Published EIA national prices |
| `diesel_minus_regular_usd_per_gal` | Diesel minus regular (this week: 1.992) |
| `aaa_regular_usd_per_gal` | Published AAA national regular |
| `aaa_minus_eia_regular_usd_per_gal` | AAA minus EIA regular (this week: 0.0086 — under 1 cent) |
| `eia_regular_week_change_usd`, `eia_regular_year_change_usd`, `eia_diesel_week_change_usd`, `eia_diesel_year_change_usd` | Published EIA changes, copied through |

### 2. Regional ranking — `gold/regional_ranking_YYYY-MM-DD.csv` (9 rows)

Cheapest to most expensive EIA region, with each region's difference
from the US regular average and its published week/year changes.
This week: cheapest is Gulf Coast (PADD 3) at 3.784 (−0.500 vs US);
most expensive is West Coast (PADD 5) at 5.557 (+1.273 vs US).

| Column | Meaning |
|---|---|
| `rank_cheapest_to_most_expensive` | 1 = cheapest region |
| `region` | PADD region name |
| `regular_usd_per_gal` | Published EIA regional regular price |
| `diff_vs_us_regular_usd_per_gal` | Region minus US regular (3 decimals) |
| `week_change_usd`, `year_change_usd` | Published EIA changes |
| `reading_date` | EIA reading date |

### 3. State snapshot — `gold/state_snapshot_YYYY-MM-DD.csv` (10 rows)

Cheapest to most expensive AAA state in this week's file, with each
state's difference from the AAA US average.
This week: cheapest is Georgia at 3.6859 (−0.6067 vs US average);
most expensive is California at 6.0587 (+1.7661 vs US average).

| Column | Meaning |
|---|---|
| `rank_cheapest_to_most_expensive` | 1 = cheapest state in the file |
| `state` | State name |
| `regular_usd_per_gal` | Published AAA state regular price (4 decimals) |
| `diff_vs_aaa_us_average_usd_per_gal` | State minus AAA US average (4 decimals) |
| `reading_date` | AAA reading date |

**Read the gold tables with care:** regional and state ranks are
within this week's file only (9 regions, 10 states). A state ranked
10th here is the most expensive *of the 10 states in the file*, not
of all 50 states. The EIA and AAA dates differ, so do not present an
EIA-vs-AAA difference as a same-day comparison.

## Rebuilding

```bash
python3 scripts/validate_csv.py data/incoming/*.csv
python3 scripts/build_layers.py
```

The build script asserts 22 rows per week, no blank prices in the
current file, and recomputes nothing beyond the documented differences
and ranks. Gold values are verified in the build output, not by hand.

## Weekly workflow

1. Add the new weekly file to `data/incoming/YYYY-MM-DD.csv`.
2. Run the validator, then `scripts/build_layers.py`.
3. Commit bronze, silver and gold for that week together.
4. Merging to `main` publishes all layers to Kaggle automatically
   (see [KAGGLE_SETUP.md](KAGGLE_SETUP.md)).
