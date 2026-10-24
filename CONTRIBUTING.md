# Contributing a Weekly Update

## Branch and pull request

- Branch: `muse/YYYY-MM-DD` where the date is the EIA reading date.
- File: `data/incoming/YYYY-MM-DD.csv` (same date).
- Pull request title: `Weekly gas prices YYYY-MM-DD`
- Do not push a weekly file directly to `main`.

## Pull request summary — required

Every weekly PR must state:

1. Number of rows, and how many have a blank price.
2. The EIA reading date and the AAA reading date, and whether they
   differ by more than 2 days.
3. Any value where EIA and AAA differ by more than 10 cents,
   with both numbers.
4. Any source that was unavailable, and what was done instead
   (blank + note — never a substitute source).

## Rules that are never waived

- Copy numbers exactly as published; keep the source's decimal places.
- Reading date = the source's date, not the collection date.
- Missing = blank price + explanation in `notes`. No estimating,
  interpolating, inventing, or cross-filling from the other source.
- Do not change, rename, or add columns.
- `source_url` = the exact page read.
- One unique row per `(reading_date, source, area, fuel_type)`.

See `docs/METHODOLOGY.md` for the full procedure and
`docs/DATA_DICTIONARY.md` for column definitions.

## Before opening the PR

```bash
python3 scripts/validate_csv.py data/incoming/YYYY-MM-DD.csv
```

It must pass. CI runs the same check.
