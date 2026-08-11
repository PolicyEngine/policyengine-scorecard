"""PE-side tariff counterparts -> data/pe/tariff_counterparts.json.

Emits our average-tariff-rate rows in the tidy schema. Today that is one
construct: the EX-POST collections rate — sum(calculated duty) /
sum(customs value), monthly, on contemporaneous weights — computed from
the Microcosm import-entry margins (microcosm #620, exact-reconciled
against Census's own control totals; merge d4b0855157af).

Regeneration reads the margins parquet when present (TARIFF_MARGINS_PARQUET
env var or the default runtime path); otherwise it falls back to the
committed monthly extract data/pe/tariff_expost_monthly.csv, which was
produced from that parquet and is byte-stable. Stage-1 counterparts (our
rates under each tracker's own construct) plug in here as further
variants; see the P5 charter.
"""

import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "pe" / "tariff_counterparts.json"
CSV_FALLBACK = ROOT / "data" / "pe" / "tariff_expost_monthly.csv"
PARQUET_DEFAULT = (
    Path.home()
    / "PolicyEngine/_laneG-runtime/out/us-import-entry-margins-bulk/margins_hts10_country_month.parquet"
)

VARIANT = "expost_collections_contemporaneous"
PROVENANCE = {
    "margins_source": "microcosm #620 (merge d4b0855157af996bd367146bc200a2f72ee7d15d)",
    "construct": "sum(cal_dut_mo)/sum(con_val_mo) monthly, all lines x countries",
    "reconciliation": "exact-integer vs publisher control totals, 3 axes x 18 months, 0 failures",
}


def from_parquet(path):
    import pandas as pd

    frame = pd.read_parquet(path, columns=["period", "cal_dut_mo", "con_val_mo"])
    grouped = frame.groupby("period", observed=True)[["cal_dut_mo", "con_val_mo"]].sum()
    for period, record in grouped.iterrows():
        yield str(period), int(record["cal_dut_mo"]), int(record["con_val_mo"])


def from_csv(path):
    with open(path) as handle:
        for record in csv.DictReader(handle):
            yield (
                record["period"],
                int(record["cal_dut_mo"]),
                int(record["con_val_mo"]),
            )


def main():
    parquet = Path(os.environ.get("TARIFF_MARGINS_PARQUET", PARQUET_DEFAULT))
    records = basis = None
    if parquet.exists():
        try:
            records, basis = list(from_parquet(parquet)), str(parquet)
        except ImportError:
            records = None  # no pandas in this interpreter; use the extract
    if records is None:
        records, basis = list(from_csv(CSV_FALLBACK)), str(CSV_FALLBACK)

    rows = [
        {
            "source": "pe",
            "program": "tariff",
            "metric": "average_tariff_rate",
            "subgroup": "total",
            "variant": VARIANT,
            "geography": "us",
            "unit_concept": "fraction_of_customs_value_contemporaneous",
            "period": period,
            "value": duties / value,
            "numerator_usd": duties,
            "denominator_usd": value,
        }
        for period, duties, value in records
    ]
    OUT.write_text(
        json.dumps(
            {"provenance": {**PROVENANCE, "computed_from": basis}, "rows": rows},
            indent=1,
        )
        + "\n"
    )
    print(f"{OUT}: {len(rows)} rows from {basis}")


if __name__ == "__main__":
    main()
