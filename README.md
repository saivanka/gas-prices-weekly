# US Retail Gasoline and Diesel Prices — Weekly

A traceable, source-faithful dataset of US retail gasoline and diesel prices,
collected weekly from official and public sources only.

> **Accuracy and traceability matter more than coverage.**
> If a value is not published, it is left blank. No value in this repository
> is ever estimated, interpolated, or invented.

## What is in this dataset?

One CSV per week, named by the EIA reading date:

```
data/incoming/YYYY-MM-DD.csv
```

Each file contains:

| Section | Source | Coverage |
|---|---|---|
| A | EIA | National weekly regular gasoline — 1 row |
| B | EIA | National weekly diesel — 1 row |
| C | EIA | Regional weekly regular gasoline — 9 rows (PADD regions) |
| D | AAA | National daily regular gasoline — 1 row |
| E | AAA | State regular gasoline — up to 10 rows, only states shown on the AAA page |

Latest file in this repository:

- **`data/incoming/2026-10-19.csv`** — 22 rows, 0 blank prices
  - EIA reading date: **2026-10-19**
  - AAA reading date: **2026-10-23** (4 days later — see *Known differences* below)

## Sources (in order of authority)

1. **U.S. Energy Information Administration (EIA)** — Gasoline and Diesel Fuel Update
   https://www.eia.gov/petroleum/gasdiesel/
   Primary source. Weekly national and regional prices. Most recent weekly
   reading only — never a daily estimate.
2. **AAA Gas Prices**
   https://gasprices.aaa.com/
   Cross-check only. Daily national average and state averages.
   State rows are read from AAA's State Gas Price Averages page:
   https://gasprices.aaa.com/state-gas-price-averages/

No gas-station websites, price-comparison apps, or any site that requires
login or forbids automated access are used.

## Schema

The header is fixed. Do not change, rename, or add columns.

```
reading_date,source,area,area_type,fuel_type,price_usd_per_gal,change_vs_prior_week_usd,change_vs_year_ago_usd,source_url,captured_at_utc,notes
```

| Column | Values |
|---|---|
| `reading_date` | `YYYY-MM-DD`, as published by the source — not the collection date |
| `source` | `EIA` or `AAA` |
| `area` | `United States`, a PADD region name, or a state name |
| `area_type` | `national`, `region`, or `state` |
| `fuel_type` | `regular` or `diesel` |
| `price_usd_per_gal` | Number, no `$` sign, exactly as published (EIA: 3 decimals, AAA: 4 decimals), or blank |
| `change_vs_prior_week_usd` | EIA only, as published, or blank |
| `change_vs_year_ago_usd` | EIA only, as published, or blank |
| `source_url` | The exact page URL the value was read from |
| `captured_at_utc` | ISO 8601 with `Z`, e.g. `2026-10-24T04:37:57Z` |
| `notes` | Short text, or blank |

One unique row per combination of `reading_date, source, area, fuel_type`.

Full definitions: [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md)
Method and rules: [docs/METHODOLOGY.md](docs/METHODOLOGY.md)

## Known differences — latest week

- EIA (2026-10-19) vs AAA (2026-10-23), national regular gasoline:
  EIA **4.284** vs AAA **4.2926** — difference **0.0086** (under 10 cents).
- The two reading dates differ by 4 days, so the files are a weekly
  EIA snapshot cross-checked against a later AAA daily snapshot,
  not two readings of the same day.

## Publishing to Kaggle

This repository is set up to publish to Kaggle from GitHub Actions —
no manual uploads needed once the one-time setup is done.

- Kaggle dataset (created on first successful Action run):
  `https://www.kaggle.com/datasets/saivanka/us-retail-gasoline-and-diesel-prices-weekly`
- Workflow: [`.github/workflows/publish-to-kaggle.yml`](.github/workflows/publish-to-kaggle.yml)
- Publisher script: [`scripts/publish_to_kaggle.py`](scripts/publish_to_kaggle.py)
- Kaggle metadata template: [`kaggle/dataset-metadata.json`](kaggle/dataset-metadata.json)
- **One-time setup — read this first:** [docs/KAGGLE_SETUP.md](docs/KAGGLE_SETUP.md)

The workflow runs the validator before it publishes. A file that fails
validation is never published.

## Validation

```bash
python3 scripts/validate_csv.py data/incoming/2026-10-19.csv
```

Validation checks: exact header, valid dates, allowed `source` / `area_type` /
`fuel_type` values, numeric-or-blank prices with no `$` signs, EIA-only change
columns, full `https` source URLs, and row uniqueness.

The same check runs in CI on every pull request:
[`.github/workflows/validate.yml`](.github/workflows/validate.yml)

## Repository layout

```
.
├── README.md
├── CONTRIBUTING.md
├── data/
│   └── incoming/
│       └── 2026-10-19.csv
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── KAGGLE_SETUP.md
│   └── METHODOLOGY.md
├── kaggle/
│   └── dataset-metadata.json
├── scripts/
│   ├── publish_to_kaggle.py
│   └── validate_csv.py
└── .github/
    └── workflows/
        ├── publish-to-kaggle.yml
        └── validate.yml
```

## Attribution and licence

- EIA data is produced by the U.S. Energy Information Administration,
  a U.S. government agency, and is in the public domain.
- AAA averages are republished here with attribution to AAA Gas Prices
  (https://gasprices.aaa.com/) for research purposes. Check AAA's terms
  before any commercial reuse of the AAA rows.
- The Kaggle metadata therefore uses licence `unknown` rather than
  claiming a single licence over both sources. See the Kaggle setup doc.

## Author

**Sai Satya Pavan Pandu Vanka** — data engineer based in Dallas, TX.
M.S. in Computer Information & Science, University of North Texas;
AWS Certified Data Engineer – Associate (2025).

- GitHub: https://github.com/saivanka
- Hugging Face: https://huggingface.co/saisatyapavanpanduvanka
- LinkedIn: https://www.linkedin.com/in/ssvanka/
- Kaggle: https://www.kaggle.com/saivanka

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: one weekly CSV
per pull request, on a branch named `muse/YYYY-MM-DD`, titled
`Weekly gas prices YYYY-MM-DD`, with the summary described there.
