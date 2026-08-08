"""Adapter: TPC Tracking Trump Tariffs chart data -> tidy external rows.

Inputs: raw/aO4iG_v44_all_goods_daily.csv (average statutory rate, All
        Goods + select-goods categories, PERCENT) and
        raw/MC81F_v43_by_type_daily.csv (by authority type, PERCENT).
Output: data/externals/tpc-tariffs.json — tidy rows (fractions).

Daily -> monthly means (annotated: tpc-monthly-mean-of-daily). The All
Goods column is the headline series (subgroup total); by-type columns
become subgroup rows under the same metric and variant. Select-goods
category columns from aO4iG are deliberately not adapted: their covered-
product universes are chart-specific and unmatched to any construct we
compute.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "tpc-tariffs"
VARIANT = "statutory_fixed2025_weights_ex_adcvd"
TYPE_SUBGROUPS = {
    "Other": "other_incl_mfn",
    "Section 232 Vehicles": "section_232_vehicles",
    "Section 232 Materials": "section_232_materials",
    "IEEPA": "ieepa",
    "Section 122": "section_122",
    "Section 301": "section_301",
    "Section 338": "section_338",
}


def monthly_means(path, columns):
    by_month = defaultdict(lambda: defaultdict(list))
    with open(path) as handle:
        reader = csv.DictReader(handle)
        date_key = "Date" if "Date" in reader.fieldnames else "date"
        for record in reader:
            month = record[date_key][:7]
            for column in columns:
                value = record.get(column, "")
                if value not in ("", None):
                    by_month[month][column].append(float(value) / 100.0)
    return by_month


def main():
    rows = []
    overall = monthly_means(
        HERE / "raw" / "aO4iG_v44_all_goods_daily.csv", ["All Goods"]
    )
    for month in sorted(overall):
        values = overall[month]["All Goods"]
        rows.append(
            {
                "source": SOURCE_ID,
                "program": "tariff",
                "metric": "average_tariff_rate",
                "subgroup": "total",
                "variant": VARIANT,
                "geography": "us",
                "unit_concept": "fraction_of_customs_value_fixed2025_weights",
                "period": month,
                "value": sum(values) / len(values),
                "n_days": len(values),
            }
        )

    by_type = monthly_means(
        HERE / "raw" / "MC81F_v43_by_type_daily.csv", list(TYPE_SUBGROUPS)
    )
    for month in sorted(by_type):
        for column, subgroup in TYPE_SUBGROUPS.items():
            values = by_type[month].get(column)
            if not values:
                continue
            rows.append(
                {
                    "source": SOURCE_ID,
                    "program": "tariff",
                    "metric": "average_tariff_rate",
                    "subgroup": subgroup,
                    "variant": VARIANT,
                    "geography": "us",
                    "unit_concept": "fraction_of_customs_value_fixed2025_weights",
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
