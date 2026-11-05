"""Stage PolicyEngine counterparts for Autumn Budget 2026 claims (#230, tranche 3).

PolicyEngine published its Budget-day estimates through the UK Autumn Budget
dashboard (PolicyEngine/uk-autumn-budget-dashboard-2026). The registry
(data/uk/ab2026_measures.json) pins each run as a ``pe_modifier`` receipt at
the dashboard commit 1eca3182, on policyengine 6.11.1 and policyengine-uk
2.151.0. This module runs no microsimulation: it reads the published
artifacts we vendor under ``results/uk/ab2026/``, and pairs each AB2026
claim on a ``pe_modifier`` measure with one cell of one artifact, or tallies
it with a written reason.

The scope rule:

- We tally a claim with a written reason when the producer's figure covers a
  base or population our run leaves out and no line of the producer's lets a
  reader size the gap (the Household Energy Payment outside England; fuel
  duty, which HM Treasury scores on every litre of taxable fuel and we
  estimate on the fuel households buy).
- We keep the comparison and annotate it when the producer prints the line
  our run leaves out. The annotation names that line and its amount for that
  year, read from the OBR's component claims at stage time: every nonzero
  line of the OBR's breakdown except the receipts heads ("Receipts:" and
  "Tax head (receipts)") and the welfare line, which gov_balance itself
  counts, such as Scotland's block grant adjustment. The OBR's behavioural
  erosion of the property income yield takes its own sentence, and any
  other line without a reader name or a rule raises. HM Treasury costs
  electricity used by charities, care homes and a small amount of business
  as well as households, so those rows keep their comparison and say so.
- We tally a year when our run shows no change because the measure isn't in
  force, since the row then says nothing about the model: where both sides
  read zero, and the Pension Tax Allowance after it ends on 5 April 2030.

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

    revenue_change, whole measure, UK, one fiscal year, a sign signs.py reads,
    not fuel duty, and not a year with no change on our side
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
        "HM Treasury and the OBR count the UK cost, including the funding the "
        "government gives Scotland, Wales and Northern Ireland, and we estimate "
        "the payment to households in England only."
    ),
    "fuel_duty_base": (
        "HM Treasury scores fuel duty on every litre of taxable fuel in the UK, "
        "and we estimate the duty and VAT on the fuel households buy."
    ),
    "zero_both_sides": (
        "The claim and our run both show zero for this year, so we have nothing "
        "to compare."
    ),
    "measure_ended": (
        "The government ends the allowance on 5 April 2030, so we estimate no "
        "change in this year, while HM Treasury and the OBR count a change in "
        "receipts in it."
    ),
    "exchequer_component": (
        "The claim gives one part of the measure's effect on the public finances "
        "(a tax head, a spending line or a block grant adjustment), and we "
        "estimate only the whole effect."
    ),
    "cumulative_real_terms": (
        "The claim sums 2026-27 to 2031-32 in 2026-27 prices, and we estimate "
        "each year in cash."
    ),
    "vigintile_ahc_breakdown": (
        "The claim splits households into twentieths of income after housing "
        "costs, and we split them into tenths of income before housing costs."
    ),
    "household_count": (
        "The claim counts households the measure reaches, and we publish no "
        "count of households."
    ),
    "share_of_households": (
        "The claim gives the share of households eligible for or reached by the "
        "measure; we estimate the share of people whose household income changes."
    ),
    "typical_bill": (
        "The claim prices one typical household's energy bill, and we estimate "
        "changes in household income, not bills."
    ),
    "worked_example": (
        "The claim works through one example household's tax or income, and we "
        "compare population totals here."
    ),
    "motorists_count": (
        "The claim counts motorists and businesses, and we count no drivers."
    ),
    "benefit_recipients_count": (
        "The claim counts carers who gain Carer's Allowance, and we count only "
        "people whose own taxes or earnings change."
    ),
    "taken_out_of_tax_count": (
        "The claim counts pensioners who stop paying income tax, and we count "
        "everyone whose income tax changes."
    ),
    "no_fiscal_year": (
        "The claim counts people by the end of the Parliament, not in one fiscal year."
    ),
}

FUEL_DUTY = "ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred"
CARERS = "ab2026__carers_allowance_earnings_taper"
PROPERTY = "ab2026__property_income_rates_plus_2pp"
PENSION_TAX_ALLOWANCE = "ab2026__pension_tax_allowance"
# HM Treasury's costing: the allowance runs "from 6 April 2027 until 5 April
# 2030", so our run reads zero after it, where both producers count receipts.
MEASURE_ENDED = {PENSION_TAX_ALLOWANCE: frozenset({"2030-31", "2031-32"})}
SCOTTISH_BGA = "Current AME: Scottish BGA (current)"
SCOTTISH_SFE = "Current AME: Scottish self-financed expenditure"
WELFARE = "Current AME: Welfare inside cap"
ELECTRICITY = "ab2026__electricity_vat_zero_rate_to_july_2027"
# The OBR's breakdown lines our run doesn't model, as a reader names them.
# Receipts heads and the welfare line are what gov_balance itself counts.
UNMODELLED_LINES = {
    SCOTTISH_BGA: "the Scottish block grant adjustment",
    SCOTTISH_SFE: "Scottish self-financed expenditure",
    "Current DEL: PSCE in RDEL": "departmental resource spending",
    "Current AME: Other AME (current)": "other annually managed expenditure",
}
# Lines no annotation reads: gov_balance counts them itself.
RECEIPTS_HEADS = ("Receipts:", "Tax head (receipts)")
# The OBR prints this once, as £0.1 billion a year on average from 2028-29
# (paragraph 3.17); the claim sits on 2031-32.
BEHAVIOURAL = "behavioural erosion of yield"
BEHAVIOURAL_YEARS = {PROPERTY: frozenset({"2028-29", "2029-30", "2030-31", "2031-32"})}
TRADING = "ab2026__trading_allowance_3000"


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


_COMPONENTS: dict | None = None


def components() -> dict[tuple[str, str, str], float]:
    """The OBR's component claims, (measure, fy, component) -> £, from the
    full harvest, so a scope annotation reads its amount from a claim. Two
    claims on one key raise, except on the receipts heads, which no
    annotation reads."""
    global _COMPONENTS
    if _COMPONENTS is None:
        out: dict[tuple[str, str, str], float] = {}
        for c in claims():
            cond = c["conditions"]
            if not (
                c["source"] == "obr_efo"
                and c["metric"] == "revenue_change"
                and cond.get("component")
                and cond.get("row_type") == "measure_component"
            ):
                continue
            k = (c["measure_key"], cond.get("fy"), cond["component"])
            if k in out and not k[2].startswith(RECEIPTS_HEADS):
                raise Unmatched(f"{k}: two OBR claims share this line")
            out.setdefault(k, c["value"])
        _COMPONENTS = out
    return _COMPONENTS


def component(key: str, fy: str, name: str) -> float:
    try:
        return components()[(key, fy, name)]
    except KeyError:
        raise Unmatched(f"{key} {fy}: no OBR claim for {name!r}") from None


def millions(value: float) -> str:
    return f"£{abs(value) / 1e6:,.0f}m"


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


def exchequer_cell(claim: dict, manifest: dict | None = None):
    """(file, column, row) of the budgetary impact cell for the claim's year."""
    manifest = manifest or load_manifest()
    folder = manifest["measures"][claim["measure_key"]]["receipt"].rsplit("/", 1)[0]
    return (
        f"{folder}/budgetary_impact.csv",
        "value",
        {"year": str(fy_start(claim["conditions"]))},
    )


def classify(claim: dict, manifest: dict | None = None) -> tuple[str, str | None]:
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
        if relation not in (signs.SAME, signs.OPPOSITE):
            raise Unmatched(f"{claim['claim_id']}: sign {relation} ({basis})")
        if unit != "gbp" or cond.get("geography") != "UK" or fy_start(cond) is None:
            raise Unmatched(f"{claim['claim_id']}: exchequer claim shape")
        if key == FUEL_DUTY:
            return None, "fuel_duty_base"
        path, column, where = exchequer_cell(claim, manifest)
        ours = float(cell(path, column, where, manifest))
        if ours == 0 and claim["value"] == 0:
            return None, "zero_both_sides"
        if ours == 0:
            if cond["fy"] in MEASURE_ENDED.get(key, ()):
                return None, "measure_ended"
            raise Unmatched(
                f"{claim['claim_id']}: our run reads zero against {claim['value']}"
            )
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


def unmodelled_lines(key: str, fy: str) -> list[tuple[str, float]]:
    """The nonzero lines of the OBR's breakdown for one measure and year that
    our run doesn't model. We skip the receipts heads and the welfare line,
    which gov_balance counts, and the behavioural line, which takes its own
    sentence; any other line without a reader name raises."""
    out = []
    for (k, y, name), value in sorted(components().items()):
        if k != key or y != fy or value == 0:
            continue
        if name.startswith(RECEIPTS_HEADS) or name == WELFARE:
            continue
        if name == BEHAVIOURAL and key in BEHAVIOURAL_YEARS:
            continue
        if name not in UNMODELLED_LINES:
            raise Unmatched(f"{key} {fy}: no reader name for {name!r}")
        out.append((UNMODELLED_LINES[name], value))
    return out


def article(amount_m: int) -> str:
    """'an' where the spoken amount starts with a vowel sound: eight,
    eleven, eighteen, eighty and so on."""
    spoken = str(amount_m)
    lead = int(spoken[:2]) if len(spoken) >= 2 else int(spoken)
    if spoken.startswith("8") or (len(spoken) % 3 == 2 and lead in (11, 18)):
        return "an"
    return "a"


def cost_or_gain(name: str, value: float) -> str:
    """One OBR line as a cost or a gain to the Exchequer, read from the
    OBR's sign: a negative value is a loss."""
    m = round(abs(value) / 1e6)
    kind = "cost" if value < 0 else "gain"
    return f"{article(m)} £{m:,}m {kind} from {name}"


def lines_annotation(key: str, fy: str) -> list[str]:
    lines = unmodelled_lines(key, fy)
    if not lines:
        return []
    parts = [cost_or_gain(name, v) for name, v in lines]
    if len(parts) == 1:
        return [f"The OBR also counts {parts[0]} in this year, which we don't model."]
    listed = ", ".join(parts[:-1]) + " and " + parts[-1]
    tail = "we model neither" if len(parts) == 2 else "we model none of them"
    return [f"The OBR also counts {listed} in this year, and {tail}."]


def behavioural_annotation(key: str, fy: str) -> list[str]:
    if fy not in BEHAVIOURAL_YEARS.get(key, ()):
        return []
    found = [
        v
        for (k, _, name), v in components().items()
        if k == key and name == BEHAVIOURAL
    ]
    if len(found) != 1:
        raise Unmatched(f"{key}: {len(found)} OBR claims for {BEHAVIOURAL!r}")
    return [
        "The OBR expects more tax-motivated incorporation and higher "
        f"non-compliance to cut the yield by £{abs(found[0]) / 1e9:.1f} billion a "
        "year, and we hold incomes fixed."
    ]


def scope_annotations(claim: dict) -> list[str]:
    """What our run covers where the producer's differs, and every line of
    the OBR's breakdown for the claim's year that our run doesn't model,
    with the amount the OBR prints."""
    key, fy = claim["measure_key"], claim["conditions"]["fy"]
    out = []
    if key == CARERS:
        out.append(
            "We apply the taper in England and Wales and leave Northern Ireland's "
            "Carer's Allowance at current law."
        )
    elif key == PROPERTY:
        out.append(
            "We raise property income tax rates in England, Wales and Northern "
            "Ireland, and finance cost relief for landlords across the UK, as the "
            "government does from 6 April 2027."
        )
    elif key == ELECTRICITY:
        out.append(
            "HM Treasury costs the zero rate on household, charity, residential "
            "care and a small amount of business electricity, and we estimate it on "
            "household electricity only."
        )
    elif key == PENSION_TAX_ALLOWANCE:
        if component(key, fy, WELFARE) != 0:
            raise Unmatched(f"{key} {fy}: the OBR shows a welfare change")
        out.append(
            "We net off any change in means-tested benefits that follows from "
            "lower income tax, and the OBR counts no change in welfare spending on "
            "this measure."
        )
    elif key == TRADING:
        out.append(
            "We have no gross trading receipts in our data, so we relieve profits "
            "up to £3,000 in full and give no relief above it. As a result, we may "
            "overstate the cost for some people and understate it for others."
        )
    return out + behavioural_annotation(key, fy) + lines_annotation(key, fy)


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
    if claim["source"] == "obr_efo":
        theirs = "the OBR measures it from its forecast before the Budget's measures"
    else:
        theirs = "HM Treasury's table names no baseline"
    annotations = [
        f"We estimate fiscal year {cond['fy']} from PolicyEngine's static "
        "Budget-day run on the Autumn Budget dashboard, with no behavioural "
        "response.",
        "We measure the change from current law in policyengine-uk 2.151.0, and "
        f"{theirs}.",
    ]
    if rule == "exchequer":
        path, column, where = exchequer_cell(claim, manifest)
        raw = cell(path, column, where, manifest)
        relation, basis = sign_relation(claim)
        sign = 1 if relation == signs.SAME else -1
        value = sign * float(raw) * 1e9
        orient = (
            "Both sides show a cost to the Exchequer as negative (PE's own "
            "orientation)."
            if sign == 1
            else "We reverse our sign to match the claim's (PE oriented to it)."
        )
        annotations += [
            "We estimate the change in government revenue less spending from the "
            "dashboard's budgetary impact table.",
            "We count each year's tax liabilities and benefit payments, while HM "
            "Treasury and the OBR count tax when it reaches the Exchequer, often "
            "in a later year.",
            orient,
        ]
        annotations += scope_annotations(claim)
    elif rule == "income_tax_gainers":
        path = f"{folder}/age_impact.csv"
        column, where = (
            "people_directly_affected",
            {"year": str(year), "age_band": "all"},
        )
        raw = cell(path, column, where, manifest)
        value = float(raw)
        annotations += [
            "We count people whose own income tax, National Insurance, student "
            "loan repayment or earnings change by £1 a year or more, leaving out "
            "households we place in no income decile.",
            "Of the four, the government changes only income tax through this "
            'allowance. HM Treasury counts "pensioners in total benefitting from a '
            'tax reduction" and states no minimum.',
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
        rule, reason = classify(c, manifest)
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


def pairing(rows: list[dict], claim_rows: list[dict]) -> dict[str, dict]:
    """Each computed row's claim id -> the claim's value and the file, column
    and row it reads, so a change in either shows in the pin."""
    value = {c["claim_id"]: c["value"] for c in claim_rows}
    return {
        r["external_claim_match"]["claim_id"]: {
            "claim_value": value[r["external_claim_match"]["claim_id"]],
            "column": r["trace"]["column"],
            "file": r["trace"]["file"],
            "where": r["trace"]["where"],
        }
        for r in sorted(rows, key=lambda r: r["external_claim_match"]["claim_id"])
    }


def check(
    tally: dict, rows: list[dict] | None = None, claim_rows: list[dict] | None = None
) -> None:
    """The accounting closes per measure and in total, and matches the pin;
    with ``rows``, each claim reads the cell the pin names."""
    for bm in (tally, *tally["by_measure"].values()):
        if bm["claims"] != bm["computed"] + sum(bm["reasons"].values()):
            raise ValueError("the counterpart accounting doesn't close")
    want = json.loads(EXPECTED.read_text())
    pinned = want.pop("pairing")
    if tally != want:
        raise ValueError(f"counterpart accounting drifted: {tally} != {want}")
    if rows is not None and pairing(rows, claim_rows or claims()) != pinned:
        raise ValueError("counterpart pairing drifted from the pin")


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
    claim_rows = claims()
    rows, tally, unanswered = stage(claim_rows)
    check(tally, rows, claim_rows)
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
