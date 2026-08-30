"""PE-side tariff counterparts -> data/pe/tariff_counterparts.json.

Emits our average-tariff-rate rows in the tidy schema. The construct is the
EX-POST collections rate — sum(calculated duty) / sum(customs value), monthly,
on contemporaneous values — computed from the Microcosm import-entry margins
(microcosm #620, exact-reconciled against Census's own control totals; merge
d4b0855157af). Rows cover the US total and Canada (Census 1220 / ISO CA).

Regeneration reads the margins parquet when present (TARIFF_MARGINS_PARQUET
env var or the default runtime path); otherwise it falls back to the
authenticated US and Canada monthly extracts in data/pe/, which were produced
from that parquet and are byte-stable. Stage-1 counterparts (our rates under
each tracker's own construct) plug in here as further variants; see the P5
charter.
"""

import csv
import json
import os
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "pe" / "tariff_counterparts.json"
CSV_FALLBACK = ROOT / "data" / "pe" / "tariff_expost_monthly.csv"
CANADA_CSV_FALLBACK = ROOT / "data" / "pe" / "tariff_expost_canada_monthly.csv"
PARQUET_DEFAULT = (
    Path.home()
    / "PolicyEngine/_laneG-runtime/out/us-import-entry-margins-bulk/margins_hts10_country_month.parquet"
)

VARIANT = "expost_collections_contemporaneous"
MARGINS_PARQUET_SHA256 = (
    "f7f88f5824112d1a9c6beaaf4addc9b15f795f6ba6d6e4447e72957731c29607"
)
EXTRACT_SHA256 = {
    "us": "9e93c1189a3ec32796ac08626cbfcef0c77ae244961c153c107a5b3abc9c3b10",
    "ca": "91d453fb634c39ef89165496cbd7dfb1860d47dd91bdda0d1d29a43f08f53d73",
}
PROVENANCE = {
    "margins_source": "microcosm #620 (merge d4b0855157af996bd367146bc200a2f72ee7d15d)",
    "margins_parquet_sha256": MARGINS_PARQUET_SHA256,
    "construct": "sum(cal_dut_mo)/sum(con_val_mo) monthly on contemporaneous customs values",
    "geography_scope": {
        "us": "all HTS10 x origin rows",
        "ca": "iso2=CA, Census cty_code=1220, country_name=Canada",
    },
    "weighting": "publisher dollar margins only; no synthetic household or survey weights",
    "reconciliation": "exact-integer vs publisher control totals, 3 axes x 18 months, 0 failures",
    "committed_extract_sha256": EXTRACT_SHA256,
    "computed_from": (
        f"Microcosm margins artifact sha256:{MARGINS_PARQUET_SHA256}; "
        "direct parquet or authenticated committed monthly extracts"
    ),
}


def sha256(path: Path) -> str:
    """Return a file's SHA-256 digest."""
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def from_parquet(path: Path) -> Iterator[tuple[str, str, int, int]]:
    """Yield US and Canada monthly totals from the pinned margins parquet."""
    import pandas as pd

    digest = sha256(path)
    if digest != MARGINS_PARQUET_SHA256:
        raise ValueError(f"unexpected Microcosm margins SHA-256: {digest}")
    frame = pd.read_parquet(
        path,
        columns=[
            "period",
            "cty_code",
            "iso2",
            "country_name",
            "cal_dut_mo",
            "con_val_mo",
        ],
    )
    canada = frame.loc[frame["iso2"] == "CA"]
    identities = set(
        canada[["cty_code", "iso2", "country_name"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )
    if identities != {("1220", "CA", "Canada")}:
        raise ValueError(f"unexpected Canada identity rows: {identities}")

    for geography, scoped in (("us", frame), ("ca", canada)):
        grouped = scoped.groupby("period", observed=True)[
            ["cal_dut_mo", "con_val_mo"]
        ].sum()
        for period, record in grouped.sort_index().iterrows():
            yield (
                geography,
                str(period),
                int(record["cal_dut_mo"]),
                int(record["con_val_mo"]),
            )


def from_csv(path: Path, geography: str) -> Iterator[tuple[str, str, int, int]]:
    """Yield one geography's authenticated committed monthly extract."""
    digest = sha256(path)
    if digest != EXTRACT_SHA256[geography]:
        raise ValueError(f"unexpected {geography} extract SHA-256: {digest}")
    with open(path) as handle:
        for record in csv.DictReader(handle):
            if geography == "ca" and (
                record["cty_code"],
                record["iso2"],
                record["country_name"],
            ) != ("1220", "CA", "Canada"):
                raise ValueError(f"unexpected Canada identity row: {record}")
            yield (
                geography,
                record["period"],
                int(record["cal_dut_mo"]),
                int(record["con_val_mo"]),
            )


def main() -> None:
    parquet = Path(os.environ.get("TARIFF_MARGINS_PARQUET", PARQUET_DEFAULT))
    records = basis = None
    if parquet.exists():
        try:
            records = list(from_parquet(parquet))
            basis = f"Microcosm margins parquet sha256:{MARGINS_PARQUET_SHA256}"
        except ImportError:
            records = None  # no pandas in this interpreter; use the extract
    if records is None:
        records = [
            *from_csv(CSV_FALLBACK, "us"),
            *from_csv(CANADA_CSV_FALLBACK, "ca"),
        ]
        basis = "committed US-total and Canada monthly extracts"

    if len(records) != 36 or len({(r[0], r[1]) for r in records}) != 36:
        raise ValueError("expected 18 unique months for each of US and Canada")

    rows = [
        {
            "source": "pe",
            "program": "tariff",
            "metric": "average_tariff_rate",
            "subgroup": "total",
            "variant": VARIANT,
            "geography": geography,
            "unit_concept": "fraction_of_customs_value_contemporaneous",
            "period": period,
            "value": duties / value,
            "numerator_usd": duties,
            "denominator_usd": value,
        }
        for geography, period, duties, value in records
    ]
    OUT.write_text(
        json.dumps(
            {"provenance": PROVENANCE, "rows": rows},
            indent=1,
        )
        + "\n"
    )
    print(f"{OUT}: {len(rows)} rows from {basis}")


if __name__ == "__main__":
    main()
