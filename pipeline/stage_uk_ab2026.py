"""Stage PolicyEngine counterparts for Autumn Budget 2026 claims (#230, tranche 3).

PolicyEngine published its Budget-day estimates through the UK Autumn Budget
dashboard (PolicyEngine/uk-autumn-budget-dashboard-2026). The registry
(data/uk/ab2026_measures.json) pins each run as a ``pe_modifier`` receipt at
the dashboard commit 1eca3182, on policyengine 6.11.1 and policyengine-uk
2.151.0. This module runs no microsimulation: it reads the published
artifacts we vendor under ``results/uk/ab2026/``, and pairs each AB2026
claim on a ``pe_modifier`` measure with one cell of one artifact, where the
claim and the cell measure the same thing.

Two subcommands:

    vendor  copy the artifacts we use from a dashboard checkout at the pinned
            commit, and write MANIFEST.json (each file's path, sha256 and
            source commit, checked against the receipt and the registry);
    stage   pair the claims and write the campaign staging that
            ``ingest_campaign`` attaches, a tally of every claim we leave
            without a result, and one receipt line per such claim.

What a dashboard column measures, read from the dashboard's code at the pin
(src/uk_budget_data/calculators.py):

    budgetary_impact.csv  value        Δgov_balance summed over households, in
                                       £bn, reform minus baseline
                                       (BudgetaryImpactCalculator); positive
                                       improves the public finances
    age_impact.csv        people_directly_affected, age_band "all"
                                       people whose own income tax, National
                                       Insurance, student loan repayment or
                                       employment income moves by £1 a year or
                                       more (AgeImpactCalculator)

Each receipt labels a year by its fiscal year's start
(execution_receipt.fiscal_year.year_label = start_year), so the dashboard's
2027 is FY 2027-28. Every run executes current law at policyengine-uk 2.151.0
as its baseline (receipt execution_receipt.baseline.kind), statically.

Pairing rules, in the order ``classify`` applies them:

    revenue_change, whole measure, UK, one fiscal year, a sign signs.py reads
        -> budgetary_impact.value × 1e9, oriented to the claim's sign
    gainer_count, persons, on a measure whose only lever is income tax
        -> age_impact people_directly_affected, age_band "all"

Every other claim on a ``pe_modifier`` measure takes one reason from
``REASONS``. A claim shape no rule names raises, so a re-staged harvest
can't slip past the accounting.

    PYTHONPATH=. python pipeline/stage_uk_ab2026.py vendor <dashboard checkout>
    PYTHONPATH=. python pipeline/stage_uk_ab2026.py stage
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scorecard_db import signs  # noqa: E402
from scorecard_db.models import BASELINE  # noqa: E402

REGISTRY_PATH = ROOT / "data" / "uk" / "ab2026_measures.json"
ARTIFACTS = ROOT / "results" / "uk" / "ab2026"
MANIFEST = ARTIFACTS / "MANIFEST.json"
TALLY = ARTIFACTS / "STAGING_TALLY.json"
UNANSWERED = ARTIFACTS / "STAGING_UNANSWERED.jsonl"
STAGED_DIR = ROOT / "results" / "uk" / "staged_ab2026"
STAGED = STAGED_DIR / "ab2026_counterparts.jsonl"
EXPECTED = Path(__file__).with_name("stage_uk_ab2026_expected.json")

ARTIFACT_PREFIX = "public/data/artifacts/"
RUN_ID = "ab2026-dashboard-1eca3182"
CURRENT_LAW = BASELINE.baseline_key()
PAIR_ID = (
    "pair-pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504"
)

# The files a computed pairing reads, per measure. Every receipt is vendored
# too, since the manifest and the pair record check against them.
USED_FILES: dict[str, tuple[str, ...]] = {
    "ab2026__electricity_vat_zero_rate_to_july_2027": ("budgetary_impact.csv",),
    "ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred": (
        "budgetary_impact.csv",
    ),
    "ab2026__carers_allowance_earnings_taper": ("budgetary_impact.csv",),
    "ab2026__trading_allowance_3000": ("budgetary_impact.csv",),
    "ab2026__pension_tax_allowance": ("budgetary_impact.csv", "age_impact.csv"),
    "ab2026__property_income_rates_plus_2pp": ("budgetary_impact.csv",),
}

# The measure whose receipt says its run leaves part of the measure's cost
# out: "Scotland, Wales and Northern Ireland receive a share of the funding
# instead, which is not modelled."
DEVOLVED_SHARE_NOT_MODELLED = frozenset(
    {"ab2026__household_energy_payment_100_bands_a_to_d"}
)
# Measures whose modifier replaces only income tax variables (registry
# pe_modifier.replaced_variables) and only lowers the tax, so the people
# whose own income tax moves are the people who gain from it.
INCOME_TAX_REDUCTION_ONLY = frozenset({"ab2026__pension_tax_allowance"})

REASONS: dict[str, str] = {
    "devolved_share_not_modelled": (
        "the claim counts the UK cost, with the Barnett shares for Scotland, Wales "
        "and Northern Ireland; the dashboard's run pays England's households only, "
        "and its receipt says it doesn't model those shares"
    ),
    "exchequer_component": (
        "the claim gives one part of the measure's exchequer effect (a receipts "
        "head, a spending line or a block grant adjustment); the dashboard "
        "publishes only the whole effect on gov_balance"
    ),
    "cumulative_real_terms": (
        "the claim sums fiscal years 2026-27 to 2031-32 in 2026-27 prices, "
        "deflated by the OBR's CPI forecast; the dashboard publishes each year in "
        "cash and states no deflator"
    ),
    "sign_not_this_quantity": (
        "signs.py reads the claim's convention as a behavioural erosion of the "
        "yield, not the measure's exchequer effect, and the dashboard's static run "
        "has no behavioural part to set against it"
    ),
    "vigintile_ahc_breakdown": (
        "the claim breaks households down by equivalised income vigintile after "
        "housing costs over two years; the dashboard publishes each year's change "
        "by household_income_decile, with no housing-cost basis"
    ),
    "spending_decile_breakdown": (
        "the claim breaks households in England down by spending decile over "
        "October 2026 to June 2027; the dashboard publishes UK fiscal years by "
        "household_income_decile"
    ),
    "household_count": (
        "the claim counts households the measure reaches; the dashboard's artifacts "
        "publish no count of households, only a share of people and counts of people"
    ),
    "share_of_households": (
        "the claim gives a share of households eligible for or reached by the "
        "measure; the dashboard publishes the share of people whose household "
        "income moves, a different population and test"
    ),
    "typical_bill": (
        "the claim prices one typical household's energy bill; the dashboard's "
        "artifacts publish no bill, only changes in household net income"
    ),
    "worked_example": (
        "the claim works through one example household's tax or income; the "
        "dashboard's population artifacts publish aggregates, and no example "
        "household matches the claim's"
    ),
    "motorists_count": (
        "the claim counts motorists and businesses the measure reaches; the "
        "dashboard counts no drivers, and a price change makes no one directly "
        "affected in its age table"
    ),
    "benefit_recipients_count": (
        "the claim counts carers who gain Carer's Allowance; the dashboard's age "
        "table counts only people whose own taxes or earnings move, not benefit "
        "recipients"
    ),
    "taken_out_of_tax_count": (
        "the claim counts pensioners the allowance takes out of income tax "
        "altogether; the dashboard counts everyone whose income tax moves, and "
        "publishes no count of people who stop paying it"
    ),
    "no_fiscal_year": (
        "the claim names no single fiscal year (a count by the end of the "
        "Parliament), so no one year of the dashboard's run answers it"
    ),
}


class Unmatched(ValueError):
    """A claim shape no rule names: decide it here before staging."""


# --- the registry and the vendored artifacts -----------------------------------


def registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text())


def modifier_measures(reg: dict | None = None) -> dict[str, dict]:
    """The registry's measures with a dashboard receipt, by key."""
    reg = reg or registry()
    return {m["measure_key"]: m for m in reg["measures"] if m.get("pe_modifier")}


def local_path(source_path: str) -> str:
    """Where a dashboard artifact lands in this repository."""
    if not source_path.startswith(ARTIFACT_PREFIX):
        raise ValueError(f"{source_path}: not under {ARTIFACT_PREFIX}")
    rel = source_path.removeprefix(ARTIFACT_PREFIX)
    return str((ARTIFACTS / rel).relative_to(ROOT))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def vendor(checkout: Path) -> dict:
    """Copy each receipt and each used file at the pinned commit from a
    dashboard checkout, check them, and write MANIFEST.json."""
    reg = registry()
    measures = modifier_measures(reg)
    commits = {m["pe_modifier"]["receipt"]["commit"] for m in measures.values()}
    if len(commits) != 1:
        raise ValueError(f"the receipts name {len(commits)} commits: {commits}")
    commit = commits.pop()

    def show(path: str) -> bytes:
        return subprocess.run(
            ["git", "show", f"{commit}:{path}"],
            cwd=checkout,
            capture_output=True,
            check=True,
        ).stdout

    files: dict[str, dict] = {}
    by_measure: dict[str, dict] = {}
    for key, m in sorted(measures.items()):
        rec = m["pe_modifier"]["receipt"]
        receipt_bytes = show(rec["path"])
        if sha256(receipt_bytes) != rec["receipt_file_sha256"]:
            raise ValueError(f"{key}: receipt bytes differ from the registry")
        receipt = json.loads(receipt_bytes)
        folder = rec["path"].rsplit("/", 1)[0]
        wanted = {"receipt.json": receipt_bytes}
        for name in USED_FILES.get(key, ()):
            data = show(f"{folder}/{name}")
            if sha256(data) != receipt["dashboard"]["files"][name]:
                raise ValueError(f"{key}: {name} differs from its receipt")
            wanted[name] = data
        for name, data in wanted.items():
            path = local_path(f"{folder}/{name}")
            (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / path).write_bytes(data)
            files[path] = {
                "sha256": sha256(data),
                "source_commit": commit,
                "source_path": f"{folder}/{name}",
            }
        by_measure[key] = {
            "dashboard_key": receipt["dashboard"]["key"],
            "files": sorted(local_path(f"{folder}/{n}") for n in wanted),
            "receipt": local_path(rec["path"]),
            "receipt_file_sha256": rec["receipt_file_sha256"],
        }
    pin = reg["engine_pin"]["budget_day_runs"]
    manifest = {
        "artifacts": {p: f["sha256"] for p, f in sorted(files.items())},
        "data_bundle": pin["dataset_revision"],
        "dataset_sha256": pin["dataset_sha256"],
        "engine_version": reg["engine_pin"]["policyengine_uk"],
        "files": dict(sorted(files.items())),
        "measures": by_measure,
        "pair_id": PAIR_ID,
        "policyengine": pin["policyengine"],
        "run_id": RUN_ID,
        "source": {
            "commit": commit,
            "repo": "PolicyEngine/uk-autumn-budget-dashboard-2026",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return manifest


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def read_file(path: str, manifest: dict | None = None) -> bytes:
    """A vendored file's bytes, checked against the manifest."""
    manifest = manifest or load_manifest()
    data = (ROOT / path).read_bytes()
    if sha256(data) != manifest["artifacts"][path]:
        raise ValueError(f"{path}: bytes differ from MANIFEST.json")
    return data


def receipt(key: str, manifest: dict | None = None) -> dict:
    manifest = manifest or load_manifest()
    return json.loads(read_file(manifest["measures"][key]["receipt"], manifest))


def cell(path: str, column: str, where: dict[str, str], manifest=None) -> str:
    """The one cell of a vendored CSV in ``column`` on the row matching
    ``where``, as the file prints it."""
    text = read_file(path, manifest).decode("utf-8")
    rows = [
        r
        for r in csv.DictReader(io.StringIO(text))
        if all(r[k] == v for k, v in where.items())
    ]
    if len(rows) != 1:
        raise ValueError(f"{path}: {len(rows)} rows match {where}")
    return rows[0][column]


# --- the claims ----------------------------------------------------------------


def claims(scores=None) -> list[dict]:
    """The AB2026 claims on a ``pe_modifier`` measure, from the tranche 2
    ingest's staging (the same claims, ids and conditions the DB holds)."""
    if scores is None:
        from scorecard_db import ingest_uk_ab2026 as ingest

        scores, _ = ingest.stage()
    keys = set(modifier_measures())
    out = []
    for s in scores:
        key = s.conditions.get("measure_key")
        if key not in keys:
            continue
        out.append(
            {
                "claim_id": s.claim_id(),
                "source": s.source,
                "metric": s.metric.value,
                "unit": s.unit_concept.value,
                "period": s.period,
                "value": s.value,
                "conditions": dict(s.conditions),
                "measure_key": key,
            }
        )
    return out


def fy_start(cond: dict) -> int | None:
    m = re.fullmatch(r"(\d{4})-(\d{2})", cond.get("fy") or "")
    return int(m.group(1)) if m else None


def sign_relation(claim: dict) -> tuple[str, str]:
    """How the claim's sign relates to PolicyEngine's orientation for its
    metric, read by signs.py from the convention the claim states."""
    return signs.classify(
        {
            "metric": claim["metric"],
            "conditions": claim["conditions"],
            "country": "UK",
            "source": claim["source"],
        }
    )


def classify(claim: dict) -> tuple[str, str | None]:
    """(rule, None) for a claim a column answers, else (None, reason key)."""
    cond = claim["conditions"]
    key = claim["measure_key"]
    metric, unit = claim["metric"], claim["unit"]
    if cond.get("obr_measure_key"):  # pragma: no cover - none in this harvest
        raise Unmatched(f"{claim['claim_id']}: the OBR costings lane owns it")
    if metric == "revenue_change":
        if key in DEVOLVED_SHARE_NOT_MODELLED:
            return None, "devolved_share_not_modelled"
        if cond.get("estimate_kind") == "cumulative" or cond.get("price_basis"):
            return None, "cumulative_real_terms"
        if cond.get("component") and cond.get("row_type") != "measure_total":
            return None, "exchequer_component"
        relation, basis = sign_relation(claim)
        if basis.endswith(":not_this_quantity"):
            return None, "sign_not_this_quantity"
        if relation not in (signs.SAME, signs.OPPOSITE):
            raise Unmatched(f"{claim['claim_id']}: sign {relation} ({basis})")
        if unit != "gbp" or cond.get("geography") != "UK" or fy_start(cond) is None:
            raise Unmatched(f"{claim['claim_id']}: exchequer claim shape")
        return "exchequer", None
    if metric == "gainer_count":
        if fy_start(cond) is None:
            return None, "no_fiscal_year"
        if key in INCOME_TAX_REDUCTION_ONLY and unit == "persons":
            if cond.get("geography") != "UK":
                raise Unmatched(f"{claim['claim_id']}: gainer geography")
            return "income_tax_gainers", None
        raise Unmatched(f"{claim['claim_id']}: gainers on {key}")
    if metric == "average_household_income_change":
        axis = (cond.get("income_axis") or "").lower()
        if "vigintile" in axis:
            return None, "vigintile_ahc_breakdown"
        if "spending" in axis:
            return None, "spending_decile_breakdown"
        raise Unmatched(f"{claim['claim_id']}: income axis {axis!r}")
    if metric == "affected_count":
        if unit == "households":
            return None, "household_count"
        if key == "ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred":
            return None, "motorists_count"
        if key == "ab2026__carers_allowance_earnings_taper":
            return None, "benefit_recipients_count"
        if key == "ab2026__pension_tax_allowance" and "not pay any tax" in (
            cond.get("subgroup") or ""
        ):
            return None, "taken_out_of_tax_count"
        raise Unmatched(f"{claim['claim_id']}: affected_count on {key}")
    if metric in ("affected_share", "eligibility_rate"):
        return None, "share_of_households"
    if metric == "energy_bill_change":
        return None, "typical_bill"
    if metric in ("tax_liability", "income_statistic"):
        return None, "worked_example"
    raise Unmatched(f"{claim['claim_id']}: no rule for {metric!r}")


def counterpart(claim: dict, rule: str, manifest: dict | None = None) -> dict:
    """The staged row for a claim ``classify`` pairs with ``rule``: the
    value, the cell it comes from, and what differs between the two."""
    manifest = manifest or load_manifest()
    key = claim["measure_key"]
    cond = claim["conditions"]
    year = fy_start(cond)
    rec = receipt(key, manifest)
    folder = manifest["measures"][key]["receipt"].rsplit("/", 1)[0]
    reg = modifier_measures()[key]
    world = cond.get("baseline_policy") or "current_law"
    annotations = [
        f"PolicyEngine's Budget-day run on the dashboard: its year {year} is FY "
        f"{cond['fy']} (the receipt labels a fiscal year by its start); static, "
        "with no behavioural response",
        "executed baseline: current law at policyengine-uk 2.151.0, the "
        f"dashboard's configured baseline; the claim is scored against {world}",
    ]
    if rule == "exchequer":
        path = f"{folder}/budgetary_impact.csv"
        column, where = "value", {"year": str(year)}
        raw = cell(path, column, where, manifest)
        relation, basis = sign_relation(claim)
        sign = 1 if relation == signs.SAME else -1
        value = sign * float(raw) * 1e9
        orient = "PE's own orientation" if sign == 1 else "PE oriented to it"
        annotations += [
            "PE static exchequer effect = Δgov_balance from the dashboard's "
            "budgetary_impact.csv (£bn × 1e9)",
            "timing: the dashboard counts the year's simulated tax liabilities and "
            "payments; the producer scores when receipts reach the Exchequer, "
            "which can fall in a later year",
            f"claim sign: signs.py reads the claim's convention as {relation} "
            f"({basis}); {orient}",
        ]
    elif rule == "income_tax_gainers":
        path = f"{folder}/age_impact.csv"
        column, where = (
            "people_directly_affected",
            {"year": str(year), "age_band": "all"},
        )
        raw = cell(path, column, where, manifest)
        value = float(raw)
        annotations += [
            "people whose own income tax, National Insurance, student loan "
            "repayment or earnings move by £1 a year or more (the dashboard's age "
            "table); the measure moves only income tax, and only down",
        ]
    else:  # pragma: no cover
        raise Unmatched(rule)
    mod = reg["pe_modifier"]
    return {
        "annotations": annotations,
        "baseline_key": CURRENT_LAW,
        "computed_at": rec["dashboard"]["generated_at"],
        "data_bundle": rec["execution_receipt"]["data"]["dataset_revision"],
        "engine_version": rec["execution_receipt"]["model"]["version"],
        "external_claim_match": {"claim_id": claim["claim_id"]},
        "measure_key": key,
        "metric": claim["metric"],
        "pe_construction": (
            f"executed_by_dashboard: {mod['function']} "
            f"(receipt {manifest['measures'][key]['receipt']}, reform_sha256 "
            f"{rec['execution_receipt']['reform']['reform_sha256'][:16]}); cell "
            f"{path} column {column} where "
            + ", ".join(f"{k}={v}" for k, v in where.items())
        ),
        "pe_value": value,
        "run_id": RUN_ID,
        "source": claim["source"],
        "status": "constructed",
        "trace": {"cell": raw, "column": column, "file": path, "where": where},
    }


def stage(claim_rows: list[dict] | None = None, manifest: dict | None = None):
    """(staged rows, tally, unanswered): every claim lands in exactly one
    bucket, a computed row or one reason."""
    claim_rows = claims() if claim_rows is None else claim_rows
    manifest = manifest or load_manifest()
    rows, unanswered = [], []
    tally: dict = {"claims": 0, "computed": 0, "reasons": {}, "by_measure": {}}
    for key in sorted(modifier_measures()):
        tally["by_measure"][key] = {"claims": 0, "computed": 0, "reasons": {}}
    for c in sorted(claim_rows, key=lambda c: c["claim_id"]):
        bm = tally["by_measure"][c["measure_key"]]
        bm["claims"] += 1
        tally["claims"] += 1
        rule, reason = classify(c)
        if rule:
            rows.append(counterpart(c, rule, manifest))
            bm["computed"] += 1
            tally["computed"] += 1
            continue
        bm["reasons"][reason] = bm["reasons"].get(reason, 0) + 1
        tally["reasons"][reason] = tally["reasons"].get(reason, 0) + 1
        unanswered.append(
            {
                "claim_id": c["claim_id"],
                "fy": c["conditions"].get("fy"),
                "measure_key": c["measure_key"],
                "metric": c["metric"],
                "reason": reason,
                "source": c["source"],
            }
        )
    for bm in (tally, *tally["by_measure"].values()):
        bm["reasons"] = dict(sorted(bm["reasons"].items()))
    rows.sort(key=lambda r: (r["measure_key"], r["external_claim_match"]["claim_id"]))
    unanswered.sort(key=lambda r: (r["measure_key"], r["claim_id"]))
    return rows, tally, unanswered


def check(tally: dict) -> None:
    """The accounting closes per measure and in total, and matches the pin."""
    for bm in (tally, *tally["by_measure"].values()):
        if bm["claims"] != bm["computed"] + sum(bm["reasons"].values()):
            raise ValueError("the counterpart accounting doesn't close")
    want = json.loads(EXPECTED.read_text())
    if tally != want:
        raise ValueError(f"counterpart accounting drifted: {tally} != {want}")


def dumps_jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["vendor"]:
        manifest = vendor(Path(argv[1]))
        print(json.dumps({"files": len(manifest["files"])}, indent=1))
        return 0
    if argv[:1] != ["stage"]:
        print(__doc__)
        return 2
    rows, tally, unanswered = stage()
    check(tally)
    STAGED_DIR.mkdir(parents=True, exist_ok=True)
    STAGED.write_text(dumps_jsonl(rows))
    TALLY.write_text(json.dumps(tally, indent=1, sort_keys=True) + "\n")
    UNANSWERED.write_text(dumps_jsonl(unanswered))
    print(
        json.dumps(
            {"computed": tally["computed"], "reasons": tally["reasons"]}, indent=1
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
