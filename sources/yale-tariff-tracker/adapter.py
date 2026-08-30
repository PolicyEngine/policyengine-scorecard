"""Adapter: Yale tariff-rate-tracker daily series -> tidy external rows.

Input:  raw/daily_overall_2026-06-09.csv (recovered at repo commit 39d394d;
        rates are decimal fractions), plus the authenticated Canada extract
        from raw/daily_by_country_canada_2026-06-09.csv.
Output: data/externals/yale-tariff-tracker.json — tidy rows.

The tracker publishes daily; the scorecard compares at monthly grain, so
each month's value is the unweighted mean of its daily values (annotated:
yale-monthly-mean-of-daily). Two metrics are emitted per month:
average_tariff_rate (weighted_etr) and average_additional_tariff_rate
(weighted_etr_additional). variant carries the construct id so joins can
never cross constructs silently. The country release only publishes
weighted_etr, so Canada gets average_tariff_rate rows only.
"""

import csv
import json
from collections import defaultdict
from decimal import Decimal, localcontext
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
COUNTRY_METRICS = {"average_tariff_rate": "weighted_etr"}


def decimal_mean(values: list[Decimal]) -> float:
    """Return a runtime-stable float from an exact decimal mean."""
    with localcontext() as context:
        context.prec = 50
        return float(sum(values, Decimal(0)) / Decimal(len(values)))


def monthly_rows(
    path: Path,
    geography: str,
    metrics: dict[str, str],
    expected_country: tuple[str, str, str] | None = None,
) -> list[dict]:
    """Aggregate one authenticated daily file to unweighted monthly means."""
    by_month = defaultdict(lambda: defaultdict(list))
    with path.open() as handle:
        records = list(csv.DictReader(handle))
    if expected_country is not None:
        observed = {
            (record["country"], record["country_name"], record["country_abbr"])
            for record in records
        }
        if observed != {expected_country}:
            raise ValueError(f"unexpected country identities in {path}: {observed}")

    for record in records:
        month = record["date"][:7]
        for metric, column in metrics.items():
            by_month[month][metric].append(Decimal(record[column]))

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
                    "geography": geography,
                    "unit_concept": "fraction_of_customs_value_fixed2024_weights",
                    "period": month,
                    "value": decimal_mean(values),
                    "n_days": len(values),
                }
            )
    return rows


def main() -> None:
    rows = monthly_rows(
        HERE / "raw" / "daily_overall_2026-06-09.csv",
        "us",
        METRICS,
    )
    rows.extend(
        monthly_rows(
            HERE / "raw" / "daily_by_country_canada_2026-06-09.csv",
            "ca",
            COUNTRY_METRICS,
            expected_country=("1220", "Canada", "canada"),
        )
    )

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    print(f"{out}: {len(rows)} rows")


if __name__ == "__main__":
    main()
