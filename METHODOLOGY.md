# Methodology

## Principles

1. **Accuracy and traceability over coverage.** A missing value stays blank.
2. **Never estimate, interpolate, or invent a number.**
3. **Copy numbers exactly as published**, including decimal places.
4. **Record the reading date the source gives**, not the collection date.
5. **If a source is unavailable or a value is missing**, leave
   `price_usd_per_gal` blank and explain in `notes`. Do not fill it from
   another source.
6. **One source per row.** EIA rows come only from EIA, AAA rows only from AAA.
7. **Exact source URL per row** in `source_url`.

## Source order

1. EIA — Gasoline and Diesel Fuel Update — primary, weekly.
2. AAA Gas Prices — cross-check only, daily national + state averages.

No other sources are used. In particular: no gas-station sites, no
price-comparison apps, no login-walled sites, no sites that forbid
automated access.

## Weekly procedure

1. Open the EIA page. Note the most recent weekly date column.
2. Transcribe national regular, national diesel, and the nine regional
   regular rows for that date, with the “week ago” change into
   `change_vs_prior_week_usd` and the “year ago” change into
   `change_vs_year_ago_usd`. (EIA's table also has a “2 year ago” column —
   it is not collected.)
3. Open AAA. Transcribe the national regular average with the
   “Price as of” date shown on the page.
4. Open AAA's State Gas Price Averages page. Transcribe up to 10 states,
   regular gasoline only, in the order shown, skipping non-states
   (e.g. District of Columbia).
5. Name the file by the EIA reading date: `data/incoming/YYYY-MM-DD.csv`.
6. Run `python3 scripts/validate_csv.py` on the file. Fix every error.
7. Open a pull request (see CONTRIBUTING.md) with the summary:
   row count and blank count, both reading dates and whether they differ
   by more than 2 days, any EIA-vs-AAA difference over 10 cents with both
   numbers, and any unavailable source.

## Worked example — week of 2026-10-19

- EIA reading date 2026-10-19, released 2026-10-20.
  US regular 4.284 (−0.047 week, +1.265 year), US diesel 6.276 (+0.097, +2.656).
- AAA reading date 2026-10-23. US regular 4.2926.
- Date gap: 4 days (> 2). National difference: 0.0086 (< 10 cents).
- Both sources available. 22 rows, 0 blank prices.
