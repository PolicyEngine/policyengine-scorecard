"""Adapter: ONS "Effects of taxes and benefits on household income" (#90).

Input:  raw/tax-benefits-statistics-time-series-v3.csv — the ONS
        customise-my-data V4 CSV for dataset `tax-benefits-statistics`,
        edition `time-series`, version 3 (see raw/README.md for URLs and
        SHA-256 pins).
Output: data/externals/ons-etb.json — tidy rows.

This is the distributional-incidence population #61/#68 went looking for
and could not have: HM Treasury publishes its decile impacts as unlabeled
chart bars (132 marks, zero digitizable values, which that lane declares
rather than digitizes). ONS publishes observations.

The publication's five income concepts are the point of it — each is the
running total after another stage of the tax-benefit system:

    original    market income before any state intervention
    gross       + cash benefits
    disposable  - direct taxes
    post-tax    - indirect taxes
    final       + benefits in kind (health, education, housing subsidy)

They are FIVE quantities, not one with a qualifier, and the adapter keeps
them apart: summing or comparing across them is a category error, and
"final income" in particular includes a benefits-in-kind allocation that
PolicyEngine-UK has no counterpart for at all.

Two identity facts this source forces, both read out of the data rather
than assumed:

1. **The time dimension is genuinely mixed.** ONS's own code list is
   called `financial-and-calendar-years`, and it means it: 1977-1993 are
   CALENDAR years and 1994-95 onward are FINANCIAL years. A calendar-1990
   observation and a financial-2020-21 observation are different time
   bases and must not share one. Each row's basis is derived from the
   label's shape, and a financial year keys its END year — the convention
   of every live UK claim in this repo.

2. **Deflated rows are dropped, tallied, with a reason.** The dataset
   carries a `value-deflation` dimension with `Deflated value` and
   `Undeflated value`, and NOTHING in the dataset, its CSVW metadata or
   the `value-deflation` code list states the price base the deflated
   figures are expressed in. A real-terms figure whose base year is
   unknown cannot be reproduced or compared with anything PolicyEngine
   computes. The 2024 BULLETIN says incomes are adjusted using CPIH
   excluding Council Tax — but that is a different release from this
   version-3 dataset, and attributing its deflator here would be
   laundering one publication's methodology onto another's numbers. So
   the nominal (undeflated) half is emitted and the deflated half is a
   declared drop; the build reconciles 5,280 = 2,640 + 2,640.

Ranking: ONS ranks households by EQUIVALISED DISPOSABLE income. That is
not HBAI's BHC/AHC net-income ranking and not HMT's, so the quintile
identities are registered per source and recorded DISTINCT downstream —
a quintile of one publisher's distribution is not a quintile of
another's.
"""

import csv
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "ons-etb"

# file -> sha256 of the exact bytes this adapter was written against.
SHA256 = {
    "tax-benefits-statistics-time-series-v3.csv": (
        "b7936b1148431d41818a28a1b173db4fcf30d6e69348accb056c872478132a3a"
    ),
    "tax-benefits-statistics-time-series-v3.csv-metadata.json": (
        "87c457f3ce188b8c409de392315847c3764be03d4c455ea3cd5589d95662de5e"
    ),
}

DATASET = "tax-benefits-statistics"
EDITION = "time-series"
VERSION = "3"

# The five published income concepts, in the order the system applies
# them. Closed: an unrecognised concept raises rather than landing under
# a label nobody decided.
INCOME_CONCEPTS = {
    "Original": "original",
    "Gross": "gross",
    "Disposable": "disposable",
    "Post-tax": "post_tax",
    "Final": "final",
}

QUINTILES = {
    "1st": "q1",
    "2nd": "q2",
    "3rd": "q3",
    "4th": "q4",
    "5th": "q5",
    "All": "all",
}

STATISTICS = {"Mean": "mean", "Median": "median"}

# The deflation states, and what this adapter does with each.
EMITTED_DEFLATION = "Undeflated value"
DROPPED_DEFLATION = "Deflated value"
DEFLATION_DROP_REASON = (
    "The price base of the deflated series is not stated in the dataset, "
    "its CSVW metadata, or the `value-deflation` code list. A real-terms "
    "figure whose base year is unknown cannot be reproduced or compared "
    "with a PolicyEngine result. The 2024 bulletin names CPIH excluding "
    "Council Tax, but that is a different release from this version-3 "
    "dataset and attributing its deflator here would launder one "
    "publication's methodology onto another's numbers."
)

GEOGRAPHY = "United Kingdom"

# 1977..1993 are calendar years; 1994-95 onward are financial years.
_CALENDAR = re.compile(r"^(\d{4})$")
_FINANCIAL = re.compile(r"^(\d{4})-(\d{2})$")


def _check_sha(fname):
    digest = hashlib.sha256((RAW / fname).read_bytes()).hexdigest()
    if digest != SHA256[fname]:
        raise RuntimeError(
            f"{fname}: sha256 {digest} != pinned {SHA256[fname]} — the raw "
            "file drifted from the bytes this adapter was written against"
        )


def _closed(registry, key, what):
    try:
        return registry[key]
    except KeyError:
        raise RuntimeError(
            f"unregistered {what}: {key!r} — the published dimension gained a "
            "value. Register it deliberately, never pass it through"
        ) from None


def parse_period(label):
    """(period, time_basis, fy_label) for an ONS time label.

    A financial year keys its END year, the convention of every live UK
    claim in this repo; a calendar year keys itself. Anything else raises
    rather than being coerced into one of them.
    """
    if m := _CALENDAR.match(label):
        return int(m.group(1)), "annual", None
    if m := _FINANCIAL.match(label):
        start = int(m.group(1))
        if (start + 1) % 100 != int(m.group(2)):
            raise RuntimeError(f"financial-year label {label!r}: suffix is not start+1")
        return start + 1, "fiscal_year", f"{start}-{m.group(2)}"
    raise RuntimeError(
        f"unparseable ONS time label {label!r} — the dimension mixes "
        "calendar and financial years and each shape is handled explicitly"
    )


def build():
    for fname in SHA256:
        _check_sha(fname)
    path = RAW / f"{DATASET}-{EDITION}-v{VERSION}.csv"
    rows = []
    drops = {}
    read = 0
    with open(path, newline="") as f:
        for rec in csv.DictReader(f):
            read += 1
            if rec["Geography"] != GEOGRAPHY:
                raise RuntimeError(f"unexpected geography {rec['Geography']!r}")
            deflation = rec["Deflation"]
            if deflation == DROPPED_DEFLATION:
                entry = drops.setdefault(
                    "price_base_unpublished",
                    {"cells": 0, "reason": DEFLATION_DROP_REASON},
                )
                entry["cells"] += 1
                continue
            if deflation != EMITTED_DEFLATION:
                raise RuntimeError(f"unregistered deflation state {deflation!r}")
            period, basis, fy = parse_period(rec["Time"])
            rows.append(
                {
                    "source": SOURCE_ID,
                    "country": "UK",
                    "geography": "UK",
                    "program": "household_income",
                    "metric": "income_statistic",
                    "income_concept": _closed(
                        INCOME_CONCEPTS, rec["Income"], "income concept"
                    ),
                    "quantile": _closed(QUINTILES, rec["Quintile"], "quintile"),
                    "statistic": _closed(
                        STATISTICS, rec["AveragesAndPercentiles"], "statistic"
                    ),
                    "unit_concept": "gbp_nominal",
                    "period": period,
                    "time_basis": basis,
                    "fy": fy,
                    "value": float(rec["v4_0"]),
                    "status": "ok",
                    "source_column": (
                        f"{rec['Income']}/{rec['AveragesAndPercentiles']}/"
                        f"{rec['Quintile']}/{rec['Time']}"
                    ),
                    "dataset_version": f"{DATASET}/{EDITION}/v{VERSION}",
                }
            )
    dropped = sum(d["cells"] for d in drops.values())
    if len(rows) + dropped != read:
        raise RuntimeError(
            f"reconciliation does not close: {len(rows)} + {dropped} != {read}"
        )
    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    reconciliation = {
        "observations_read": read,
        "claims": len(rows),
        "deliberate_drops": dropped,
        "drops": drops,
    }
    print(f"wrote {len(rows)} rows -> {out}")
    print(
        f"  reconciliation: {read} observations = {len(rows)} claims "
        f"+ {dropped} deliberate drops"
    )
    for key, d in drops.items():
        print(f"    drop {key}: {d['cells']} cells")
    return rows, reconciliation


if __name__ == "__main__":
    build()
