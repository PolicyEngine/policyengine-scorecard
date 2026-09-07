# ons-etb raw artifacts

Fetched 2026-08-24 from the ONS **customise-my-data API**, which is the
machine-readable form of this publication — not the bulletin page, which
carries no downloadable tables, and not the legacy
`averageincomestaxesandbenefitsbydecilegroupsofallhouseholds` dataset
page, whose "current" file is a 2015-saved BIFF `.xls` from a
discontinued series (surveyed and deliberately NOT kept; see below).

| file | source URL | sha256 |
|---|---|---|
| tax-benefits-statistics-time-series-v3.csv | https://static.ons.gov.uk/datasets/tax-benefits-statistics-time-series-v3.csv | b7936b1148431d41818a28a1b173db4fcf30d6e69348accb056c872478132a3a |
| tax-benefits-statistics-time-series-v3.csv-metadata.json | https://static.ons.gov.uk/datasets/tax-benefits-statistics-time-series-v3.csv-metadata.json | 87c457f3ce188b8c409de392315847c3764be03d4c455ea3cd5589d95662de5e |

Both are served from `download.ons.gov.uk/downloads/datasets/tax-benefits-statistics/editions/time-series/versions/3.csv[-metadata.json]`,
which 301-redirects to the `static.ons.gov.uk` URLs above. The redirect
target is what is pinned, because that is what the bytes came from.

## What this version is

- dataset `tax-benefits-statistics`, edition `time-series`, **version 3**
- `dct:issued` 2022-09-09 (from the CSVW metadata)
- 5,280 observations = 44 time periods x 6 quintile groups x 2 statistics
  x 5 income concepts x 2 deflation states
- dimensions: `financial-and-calendar-years`, `uk-only`, `quintile`,
  `averages-and-percentiles`, `income-type`, `value-deflation`

The version is pinned deliberately. ONS has published bulletins more
recent than this dataset version (the latest bulletin edition is 2024),
so **the API dataset lags the bulletin** — a later harvest should bump
the version explicitly rather than silently following `latest_version`,
because the observations, not the commentary, are what the claims are.

## What was surveyed and deliberately NOT kept

- The **bulletin page** (`.../bulletins/theeffectsoftaxesandbenefitsonhouseholdincome/2024`)
  carries no `.xlsx`/`.csv`/`.ods` links at all — it is commentary.
- `.../datasets/averageincomestaxesandbenefitsbydecilegroupsofallhouseholds`
  offers `table14oecdtcm77407927.xls`, a Composite Document (BIFF) file
  last saved **2015-06-18**. It is the decile table this lane originally
  wanted, but it belongs to a discontinued series and is nine years older
  than the API dataset. Vendoring it would have bought deciles at the
  price of a decade of staleness and an undocumented layout. The API
  dataset's **quintiles** are the honest current grain, and the lane says
  so rather than implying decile coverage it does not have.
