"""Build the OBR fiscal-event replay inventory (track 2 of #156).

One row per Policy measures database (PMD) row for the 32 fiscal events from
the June 2010 Budget ("Budget 2010 #2") to Autumn Budget 2025, read from the
harvest the repository vendors:

    sources/harvest-uk-2026-08-02/uk_obr/claims_staged.jsonl.gz

That file is the November 2025 PMD vintage staged cell by cell (original
scorecard cells only; the OBR's nominal-GDP extension cells were dropped at
staging, see that family's NOTES.md). Cells are written in workbook order, a
row at a time and fiscal year ascending within a row, so a workbook row is
recovered as a maximal run of cells with the same (table, event, description,
head) whose fiscal years strictly increase. The PMD carries 44 rows that repeat
an earlier row's (event, description, head) key, so the key alone is not an
identity; the run is.

Each row is joined to one classification record from
`data/uk/events/classifications/*.jsonl` (household-model scope and
expressibility in policyengine-uk), and every parameter path a record cites
is resolved against the raw parameter index of the installed engine
(`data/uk/events/pe_uk_parameter_dates_<version>.json.gz`, written by
`index_pe_uk.py`). An unresolvable path fails the build: paths are computed
against the engine, never typed from memory.

Outputs (all deterministic):

    data/uk/events/inventory.jsonl       one row per PMD row
    data/uk/events/event_summary.json    counts and GBP by class, per event

    uv run python data/uk/events/build_inventory.py            # full build
    uv run python data/uk/events/build_inventory.py --base     # rows only,
        written to data/uk/events/base_rows.jsonl for classification work
    uv run python data/uk/events/build_inventory.py --check    # fail on drift
    uv run python data/uk/events/build_inventory.py --validate FILE
        # check one classification file (scope/area vocabularies, cited
        # parameter paths and variables resolve in the engine index)
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HARVEST = (
    ROOT / "sources" / "harvest-uk-2026-08-02" / "uk_obr" / "claims_staged.jsonl.gz"
)
HARVEST_SHA256 = "46117d14c4de7ac10cbc9bc09acef6c5b5060db1605e02334d4a827cf420a3bd"
CLASSIFICATIONS = HERE / "classifications"
OUT = HERE / "inventory.jsonl"
SUMMARY = HERE / "event_summary.json"
BASE = HERE / "base_rows.jsonl"

PMD_TABLES = {
    "Tax Measures (Policy measures database)": "tax",
    "Spending Measures (Policy measures database)": "spending",
}

# The 32 events in PMD order, June 2010 Budget to Autumn Budget 2025. The
# names are the PMD's own `Event` column values, verbatim.
EVENTS = [
    "Budget 2010 #2",
    "Autumn 2010",
    "Budget 2011",
    "Autumn 2011",
    "Budget 2012",
    "Autumn 2012",
    "Budget 2013",
    "Autumn 2013",
    "Budget 2014",
    "Autumn 2014",
    "Budget 2015",
    "Budget 2015 #2",
    "Autumn 2015",
    "Budget 2016",
    "Autumn 2016",
    "Budget 2017",
    "Autumn Budget 2017",
    "Spring Statement 2018",
    "Budget 2018",
    "Spring Statement 2019",
    "Budget 2020",
    "Spending Review 2020",
    "Spring Budget 2021",
    "Autumn Budget 2021",
    "Spring Statement 2022",
    "Autumn Statement 2022",
    "Spring Budget 2023",
    "Autumn Statement 2023",
    "Spring Budget 2024",
    "Autumn Budget 2024",
    "Spring Statement 2025",
    "Autumn Budget 2025",
]

SCOPES = {"in", "out"}
EXPRESSIBILITY = {"expressible", "partial", "not", "not_applicable"}
OUT_REASONS = {
    "business_tax",
    "north_sea_and_energy_producers",
    "financial_sector",
    "compliance_avoidance_and_operational",
    "departmental_spending",
    "devolved_block_grant",
    "local_government_finance",
    "public_sector_pay_and_pensions",
    "student_loans",
    "environmental_and_business_levies",
    "fees_charges_and_other_receipts",
    "accounting_and_classification",
    "indirect_or_behavioural_only",
    "other_non_household",
}
IN_AREAS = {
    "income_tax",
    "dividend_and_savings_tax",
    "nics_class_1_employee",
    "nics_class_1_employer",
    "nics_class_2",
    "nics_class_3",
    "nics_class_4",
    "health_and_social_care_levy",
    "capital_gains_tax",
    "inheritance_tax",
    "pension_tax_relief",
    "savings_and_isa",
    "vat",
    "fuel_duty",
    "alcohol_duty",
    "tobacco_duty",
    "vehicle_excise_duty",
    "air_passenger_duty",
    "insurance_premium_tax",
    "betting_and_gaming",
    "soft_drinks_and_other_excise",
    "stamp_duty_land_tax",
    "lbtt",
    "ltt",
    "stamp_duty_shares",
    "council_tax",
    "domestic_property_other",
    "universal_credit",
    "tax_credits",
    "legacy_benefits",
    "housing_benefit",
    "child_benefit_and_hicbc",
    "state_pension",
    "pension_credit",
    "disability_and_carer_benefits",
    "benefit_cap",
    "benefit_uprating",
    "childcare_support",
    "energy_and_cost_of_living_payments",
    "scottish_and_devolved_benefits",
    "student_loan_repayments",
    "other_household",
}
HISTORY_TAGS = {
    "values_cover_costing_years",
    "values_partly_cover_costing_years",
    "values_start_after_first_costing_year",
    "no_parameter_cited",
}


def fy_start(fy: str) -> int:
    return int(fy[:4])


def event_key(event: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", event.lower())).strip("_")


def slug(text: str, limit: int = 72) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:limit].rstrip("_")


def sha256(path: Path) -> str:
    return hashlib.sha256(gzip.open(path, "rb").read()).hexdigest()


def load_rows() -> list[dict]:
    """Recover PMD rows for the 32 events from the vendored harvest."""
    digest = sha256(HARVEST)
    if digest != HARVEST_SHA256:
        sys.exit(f"harvest digest {digest} != pinned {HARVEST_SHA256}")
    wanted = set(EVENTS)
    rows: list[dict] = []
    cur = None
    with gzip.open(HARVEST, "rt") as fh:
        for line in fh:
            c = json.loads(line)
            table = PMD_TABLES.get(c.get("source_table"))
            if table is None:
                continue
            cond = c["conditions"]
            event = cond["fiscal_event"]
            if event not in wanted:
                cur = None
                continue
            head = cond.get("tax_head") if table == "tax" else cond.get("spending_head")
            key = (table, event, c["reform_hint"], head)
            fy = cond["fy"]
            if (
                cur is None
                or cur["_key"] != key
                or fy_start(fy) <= fy_start(cur["_last_fy"])
            ):
                cur = {"_key": key, "_last_fy": fy, "cells": {}}
                rows.append(cur)
            cur["cells"][fy] = c["value_raw"]
            cur["_last_fy"] = fy
    out = []
    seq = Counter()
    for r in rows:
        table, event, measure, head = r["_key"]
        ek = event_key(event)
        seq[(ek, table)] += 1
        cells = r["cells"]
        out.append(
            {
                "row_id": f"{ek}:{table}:{seq[(ek, table)]:03d}",
                "event": event,
                "event_key": ek,
                "event_index": EVENTS.index(event) + 1,
                "table": table,
                "measure": measure,
                "head": head,
                "costing_gbp_m": cells,
                "first_fy": min(cells),
                "first_nonzero_fy": min((fy for fy, v in cells.items() if v), default=None),
                "last_fy": max(cells),
                "net_gbp_m": round(sum(cells.values()), 6),
                "gross_gbp_m": round(sum(abs(v) for v in cells.values()), 6),
            }
        )
    found = {r["event"] for r in out}
    missing = wanted - found
    if missing:
        sys.exit(f"events missing from harvest: {sorted(missing)}")
    return out


def assign_measure_keys(rows: list[dict]) -> None:
    """Group a measure's heads under one key; keep keys unique per event."""
    used: dict[str, str] = {}
    for r in rows:
        base = f"{r['event_key']}__{slug(r['measure'])}"
        owner = used.get(base)
        if owner is None:
            used[base] = r["measure"]
            r["measure_key"] = base
        elif owner == r["measure"]:
            r["measure_key"] = base
        else:
            n = 2
            while f"{base}_{n}" in used and used[f"{base}_{n}"] != r["measure"]:
                n += 1
            used[f"{base}_{n}"] = r["measure"]
            r["measure_key"] = f"{base}_{n}"


def load_param_index() -> tuple[str, dict[str, dict], set[str]]:
    files = sorted(HERE.glob("pe_uk_parameter_dates_*.json.gz"))
    if len(files) != 1:
        sys.exit(f"expected one parameter index, found {[f.name for f in files]}")
    idx = json.load(gzip.open(files[0], "rt"))
    params = {p["path"]: p for p in idx["parameters"]}
    return idx["policyengine_uk"], params, set(idx.get("variables", []))


def resolve_path(path: str, params: dict) -> dict | None:
    """Resolve a parameter leaf, or a node/scale/bracket prefix, in the index.

    A node resolves to the earliest date key of each leaf beneath it, so a
    history check can tell whole, partial and absent coverage apart.
    """
    if path in params:
        return {"path": path, "node": False, "earliest": [params[path]["earliest"]]}
    leaves = [
        p for k, p in params.items() if k.startswith(path + ".") or k.startswith(path + "[")
    ]
    if leaves:
        return {"path": path, "node": True, "earliest": [p["earliest"] for p in leaves]}
    return None


def load_classifications() -> dict[str, dict]:
    recs: dict[str, dict] = {}
    for f in sorted(CLASSIFICATIONS.glob("*.jsonl")):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            rid = rec["row_id"]
            if rid in recs:
                sys.exit(f"{f.name}:{n}: duplicate classification for {rid}")
            recs[rid] = rec
    return recs


def validate(rec: dict, row: dict, params: dict, variables: set) -> list[str]:
    errs = []
    if rec.get("measure") != row["measure"]:
        errs.append("measure text does not match the PMD row")
    if rec.get("scope") not in SCOPES:
        errs.append(f"scope {rec.get('scope')!r}")
    ex = rec.get("expressibility")
    if ex not in EXPRESSIBILITY:
        errs.append(f"expressibility {ex!r}")
    if rec.get("scope") == "out":
        if rec.get("out_reason") not in OUT_REASONS:
            errs.append(f"out_reason {rec.get('out_reason')!r}")
        if ex != "not_applicable":
            errs.append("out-of-scope rows carry expressibility not_applicable")
    if rec.get("scope") == "in":
        if rec.get("area") not in IN_AREAS:
            errs.append(f"area {rec.get('area')!r}")
        if ex == "not_applicable":
            errs.append("in-scope rows need an expressibility verdict")
        if ex in {"expressible", "partial"} and not rec.get("parameter_paths") and not rec.get("variables"):
            errs.append("expressible/partial rows cite parameter paths or variables")
        if ex in {"partial", "not"} and not rec.get("missing_machinery"):
            errs.append("partial/not rows name the missing machinery")
    for p in rec.get("parameter_paths") or []:
        if resolve_path(p, params) is None:
            errs.append(f"unresolved parameter path {p}")
    for v in rec.get("variables") or []:
        if v not in variables:
            errs.append(f"unknown variable {v}")
    return errs


def history_tag(row: dict, rec: dict, params: dict) -> tuple[str, list[dict]]:
    """Do the cited parameters carry a dated value by the first costed year?

    The test date is 6 April of the first fiscal year with a nonzero costing.
    A leaf covers it when its earliest date key is on or before that day; a
    node covers it when every leaf beneath it does.
    """
    paths = rec.get("parameter_paths") or []
    if not paths:
        return "no_parameter_cited", []
    fy = row["first_nonzero_fy"] or row["first_fy"]
    day = f"{fy_start(fy)}-04-06"
    detail, covered = [], []
    for p in paths:
        hit = resolve_path(p, params)
        dates = [d for d in hit["earliest"]] if hit else [None]
        ok = [d is not None and d <= day for d in dates]
        covered += ok
        known = [d for d in dates if d]
        detail.append(
            {
                "path": p,
                "leaves": len(dates),
                "leaves_covering": sum(ok),
                "earliest_date_key": min(known) if known else None,
                "latest_first_date_key": max(known) if known else None,
            }
        )
    if all(covered):
        tag = "values_cover_costing_years"
    elif any(covered):
        tag = "values_partly_cover_costing_years"
    else:
        tag = "values_start_after_first_costing_year"
    return tag, detail


def summarise(rows: list[dict]) -> dict:
    by_event: dict[str, dict] = {}
    for ev in EVENTS:
        ers = [r for r in rows if r["event"] == ev]
        gross = sum(r["gross_gbp_m"] for r in ers)
        cls = defaultdict(lambda: {"rows": 0, "measures": set(), "gross_gbp_m": 0.0})
        for r in ers:
            k = r["class"]
            cls[k]["rows"] += 1
            cls[k]["measures"].add(r["measure_key"])
            cls[k]["gross_gbp_m"] += r["gross_gbp_m"]
        classes = {
            k: {
                "rows": v["rows"],
                "measures": len(v["measures"]),
                "gross_gbp_m": round(v["gross_gbp_m"], 3),
                "share_of_gross": round(v["gross_gbp_m"] / gross, 6) if gross else None,
            }
            for k, v in sorted(cls.items())
        }

        def share(keys):
            g = sum(r["gross_gbp_m"] for r in ers if r["class"] in keys)
            return round(g / gross, 6) if gross else None

        by_event[ev] = {
            "event_key": event_key(ev),
            "event_index": EVENTS.index(ev) + 1,
            "rows": len(ers),
            "measures": len({r["measure_key"] for r in ers}),
            "scoring_fys": [min(r["first_fy"] for r in ers), max(r["last_fy"] for r in ers)],
            "gross_gbp_m": round(gross, 3),
            "classes": classes,
            "share_in_scope": share({"in:expressible", "in:partial", "in:not"}),
            "share_in_scope_expressible": share({"in:expressible"}),
            "share_in_scope_expressible_or_partial": share({"in:expressible", "in:partial"}),
        }
    return by_event


def build(base_only: bool) -> tuple[str, str]:
    rows = load_rows()
    assign_measure_keys(rows)
    if base_only:
        text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
        return text, ""
    version, params, variables = load_param_index()
    recs = load_classifications()
    errors = []
    ids = {r["row_id"] for r in rows}
    extra = set(recs) - ids
    if extra:
        errors.append(f"classifications for unknown rows: {sorted(extra)[:10]}")
    out_rows = []
    for r in rows:
        rec = recs.get(r["row_id"])
        if rec is None:
            errors.append(f"{r['row_id']}: unclassified")
            continue
        errs = validate(rec, r, params, variables)
        errors += [f"{r['row_id']}: {e}" for e in errs]
        tag, detail = history_tag(r, rec, params)
        cls = f"{rec['scope']}:{rec['expressibility']}" if rec["scope"] == "in" else "out"
        out_rows.append(
            {
                **r,
                "class": cls,
                "scope": rec["scope"],
                "out_reason": rec.get("out_reason"),
                "area": rec.get("area"),
                "scope_note": rec.get("scope_note"),
                "expressibility": rec["expressibility"],
                "parameter_paths": rec.get("parameter_paths") or [],
                "variables": rec.get("variables") or [],
                "missing_machinery": rec.get("missing_machinery"),
                "expressibility_note": rec.get("expressibility_note"),
                "parameter_history": tag,
                "parameter_history_detail": detail,
                "existing_registry_key": rec.get("existing_registry_key"),
                "engine": f"policyengine-uk {version}",
            }
        )
    if errors:
        sys.exit("classification errors:\n  " + "\n  ".join(errors[:200]) + f"\n({len(errors)} total)")
    text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in out_rows)
    summary = {
        "schema_version": 1,
        "source": "sources/harvest-uk-2026-08-02/uk_obr/claims_staged.jsonl.gz (PMD November 2025 vintage, original scorecard cells)",
        "source_sha256": HARVEST_SHA256,
        "engine": f"policyengine-uk {version}",
        "gross_rule": "gross_gbp_m = sum over original scorecard years of |costing|, GBP million; a measure's share is its gross over the event's gross",
        "sign_convention": "positive = gain to the Exchequer (PMD Notes sheet)",
        "events": summarise(out_rows),
    }
    return text, json.dumps(summary, indent=1, sort_keys=True) + "\n"


def validate_file(path: Path) -> None:
    """Validate one classification file against the rows it names."""
    rows = {r["row_id"]: r for r in load_rows()}
    _, params, variables = load_param_index()
    errors, n = [], 0
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        n += 1
        rec = json.loads(line)
        row = rows.get(rec.get("row_id"))
        if row is None:
            errors.append(f"line {i}: unknown row_id {rec.get('row_id')!r}")
            continue
        errors += [f"line {i} {row['row_id']}: {e}" for e in validate(rec, row, params, variables)]
    print(f"{n} records checked, {len(errors)} errors")
    for e in errors:
        print("  " + e)
    sys.exit(1 if errors else 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--validate", type=Path, help="check one classification file")
    a = ap.parse_args()
    if a.validate:
        validate_file(a.validate)
        return
    text, summary = build(a.base)
    targets = [(BASE, text)] if a.base else [(OUT, text), (SUMMARY, summary)]
    if a.check:
        drift = [p.name for p, t in targets if not p.exists() or p.read_text() != t]
        if drift:
            sys.exit(f"out of date: {drift}")
        print("inventory up to date")
        return
    for p, t in targets:
        p.write_text(t)
        print(f"wrote {p.relative_to(ROOT)} ({t.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
