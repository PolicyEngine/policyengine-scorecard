"""Adapter: Yale tariff-rate-tracker daily overall series -> tidy external rows.

Input:  raw/daily_overall_2026-06-09.csv (recovered at repo commit 39d394d;
        rates are decimal fractions).
Output: data/externals/yale-tariff-tracker.json — tidy rows.

The tracker publishes daily; the scorecard compares at monthly grain, so
each month's value is the unweighted mean of its daily values (annotated:
yale-monthly-mean-of-daily). Two metrics are emitted per month:
average_tariff_rate (weighted_etr) and average_additional_tariff_rate
(weighted_etr_additional). variant carries the construct id so joins can
never cross constructs silently.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "yale-tariff-tracker"
VARIANT = "effective_statutory_fixed2024_weights"
METRICS = {
    "average_tariff_rate": "weighted_etr",
    "average_additional_tariff_rate": "weighted_etr_additional",
}


def main():
    by_month = defaultdict(lambda: defaultdict(list))
    with open(HERE / "raw" / "daily_overall_2026-06-09.csv") as handle:
        for record in csv.DictReader(handle):
            month = record["date"][:7]
            for metric, column in METRICS.items():
                by_month[month][metric].append(float(record[column]))

    rows = []
    for month in sorted(by_month):
        for metric, values in sorted(by_month[month].items()):
            rows.append(
                {
                    "source": SOURCE_ID,
                    "program": "tariff",
                    "metric": metric,
                    "subgroup": "total",
                    "variant": VARIANT,
                    "geography": "us",
                    "unit_concept": "fraction_of_customs_value_fixed2024_weights",
                    "period": month,
                    "value": sum(values) / len(values),
                    "n_days": len(values),
                }
            )

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    print(f"{out}: {len(rows)} rows")


if __name__ == "__main__":
    main()
