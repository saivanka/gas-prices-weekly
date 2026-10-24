# Data Dictionary

One row = one published price reading.

| Column | Type | Required | Description |
|---|---|---|---|
| `reading_date` | date `YYYY-MM-DD` | yes | Date the source gives for the reading. For EIA this is the Monday of the weekly reading (e.g. `2026-10-19`). For AAA this is the “Price as of” date shown on the page (e.g. `2026-10-23`). Never the collection date. |
| `source` | enum | yes | `EIA` or `AAA`. |
| `area` | text | yes | `United States`, a PADD region name exactly as listed in the methodology, or a state name exactly as shown by AAA. |
| `area_type` | enum | yes | `national`, `region`, or `state`. |
| `fuel_type` | enum | yes | `regular` or `diesel`. Diesel rows are currently EIA national only. |
| `price_usd_per_gal` | decimal or blank | yes (blank allowed) | Price in US dollars per gallon, no `$` sign, no commas. Keep the source's decimal places: EIA 3, AAA 4. Blank only when the source did not publish the value — and then `notes` must explain why. |
| `change_vs_prior_week_usd` | decimal or blank | no | EIA only. Copied exactly as published in EIA's “week ago” change column. Blank for all AAA rows. |
| `change_vs_year_ago_usd` | decimal or blank | no | EIA only. Copied exactly as published in EIA's “year ago” change column. Blank for all AAA rows. |
| `source_url` | URL | yes | The exact page read. EIA: `https://www.eia.gov/petroleum/gasdiesel/` · AAA national: `https://gasprices.aaa.com/` · AAA states: `https://gasprices.aaa.com/state-gas-price-averages/` |
| `captured_at_utc` | timestamp | yes | When the value was captured, ISO 8601 UTC with `Z`, e.g. `2026-10-24T04:37:57Z`. Same timestamp for all rows captured in one run. |
| `notes` | text or blank | no | Short explanation for a blank or unusual value. Blank when there is nothing to explain. |

## Uniqueness

`(reading_date, source, area, fuel_type)` is unique in every file.

## Regions collected (EIA, regular gasoline)

- East Coast (PADD 1)
- New England (1A)
- Central Atlantic (1B)
- Lower Atlantic (1C)
- Midwest (PADD 2)
- Gulf Coast (PADD 3)
- Rocky Mountain (PADD 4)
- West Coast (PADD 5)
- West Coast less California
