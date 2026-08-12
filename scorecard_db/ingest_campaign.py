"""Ingest the 2026-08-02 campaign compute batch as PE results + exhibits.

Inputs are vendored under sources/campaign-2026-08-02/ (run JSONs with
full bundle provenance, the campaign's own collation CSVs, and CPSP's
pre-staged result rows; .npz world arrays and logs stay outside, named
in the run metas). Every result row records the baseline the run
actually executed (issue #13) and joins to an existing claim by DB
query — exactly-one-match is asserted, so vocabulary drift fails
loudly, never silently misattaches.

Join families:

1. **UK ready reckoner** (23 runs ↔ hmrc RR claims via slugified staged
   hint): computed_value is the |head-delta| magnitude (HMRC publishes
   per-direction magnitudes; the signed PE delta and heads ride
   annotations), cross-checked against the campaign's own collations
   (t2_collation.csv, uk_scorecard_first.csv) before landing.
2. **UK free joins** (free_joins.csv ↔ OBR EFO revenue levels and DWP
   BECL forecast lines by line/value match); skipped rows land as
   not_computed with the scoping reason verbatim.
3. **OBR measure reversals** (obr_measures_collation.csv ↔ measures-
   database claims by (value, period) with head disambiguation).
4. **April-2026 uprating checks** (uprating_check_april2026.json ↔ RF
   benefit_uprating claims — the one `comparable` family here: pure
   parameter-tree checks, no data artifact involved).
5. **TPC T25-0209 / T26-0029** (16 runs; income-tax deltas vs the
   vendored same-bundle baselines; the AFA floor ambiguity lands as TWO
   results on one claim — both constructions preserved).
6. **PWBM SS-benefits-tax elimination** (FY2025/FY2026 claims).
7. **CPSP CTC counterfactual levels** (pre-staged rows ↔ cpsp claims;
   plus the descriptive-register diagnoses: methodological_difference
   with the populace#593 EHS sub-channel in the rationale).
8. **JCT OBBBA CTC-extension provision** (expiry-counterfactual delta
   vs JCX-35-25 Chapter-1 provision 4, sequential-stack caveat named).
9. **US CBO free joins** (free_joins_cbo.csv ↔ cbo claims by
   program/metric/period/source_column).

PE-only counterfactuals — the two-child-limit removal family (floating/
fixed line × calibrated/entitlements take-up, plus the absolute-line
continuity pair) — have no external claim at their construction and
land in pe_exhibits with reform two_child_limit_removal against the
registered pre_ab2025 baseline (direction explicit, #13 point 5).

Statuses follow the descriptive register: cross-convention comparisons
are `constructed` with named deltas; scoping skips are `not_computed`
with reasons; nothing here is `pe_gap` (no capability claims).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .baselines import register_baselines
from .db import ScorecardDB
from .harvest import REPO
from .models import (
    BASELINE,
    ComparisonStatus,
    PEResult,
    baseline_key,
)
from .uk import slugify

CAMPAIGN = REPO / "sources" / "campaign-2026-08-02"
COMPUTED_AT = "2026-08-02T20:00:00"
CURRENT_LAW_KEY = BASELINE.baseline_key()
PRE_AB2025_KEY = baseline_key({"policy": "pre_ab2025"})


def _load(rel: str):
    return json.loads((CAMPAIGN / rel).read_text())


def _rows(rel: str) -> list[dict]:
    with (CAMPAIGN / rel).open() as f:
        return list(csv.DictReader(f))


def _one(db: ScorecardDB, what: str, sql: str, args: tuple) -> str:
    hits = [r["claim_id"] for r in db.conn.execute(sql, args)]
    if len(hits) != 1:
        raise ValueError(f"campaign: {what}: {len(hits)} claims matched")
    return hits[0]


def _bundle_meta(bundle: dict) -> tuple[str, str]:
    return bundle["model_version"], bundle["certified_data_build_id"]


# -- 1. UK ready reckoner ------------------------------------------------
# run key -> (staged HMRC hint — verbatim, verified against the 74 staged
# reckoner lines — and the PE aggregate heads whose delta scores it).
RECKONER = {
    "additional_rate_1p": ("Increase additional rate by 1p (yield)",
                           ("income_tax",)),
    "basic_rate_1p": ("Change basic rate by 1p", ("income_tax",)),
    "brl_10pct": ("Increase basic rate limit by 10% (cost)",
                  ("income_tax",)),
    "brl_1pct": ("Change basic rate limit by 1%", ("income_tax",)),
    "cb_additional_1pw": (
        "Increase subsequent child rate by £1 per week (cost)",
        ("child_benefit",),
    ),
    "cb_first_1pw": ("Increase first child rate by £1 per week (cost)",
                     ("child_benefit",)),
    "class4_1pp": ("Change Class 4 main rate by 1 percentage point",
                   ("national_insurance",)),
    "dividend_allowance_100": ("Change dividend allowance by £100",
                               ("income_tax",)),
    "employee_additional_1pp": (
        "Change Class 1 employee additional rate by 1 percentage point",
        ("national_insurance",),
    ),
    "employee_ni_1pp": (
        "Change Class 1 employee main rate by 1 percentage point",
        ("national_insurance",),
    ),
    "employer_ni_1pp": (
        "Change Class 1 employer rate by 1 percentage point",
        ("ni_employer",),
    ),
    "higher_rate_1p": ("Change higher rate by 1p", ("income_tax",)),
    "ni_lpl_104": ("Change lower profits limit by £104 per year",
                   ("national_insurance",)),
    "ni_pt_2pw": ("Change employee entry threshold by £2 per week",
                  ("national_insurance",)),
    "ni_st_2pw": ("Change employer threshold by £2 per week",
                  ("ni_employer",)),
    "ni_uel_10pw": ("Change upper earnings limit by £10 per week",
                    ("national_insurance",)),
    "ni_upl_520": ("Change upper profits limit by £520 per year",
                   ("national_insurance",)),
    "pa_100": ("Change personal allowance by £100", ("income_tax",)),
    "pa_10pct": ("Change personal allowance by 10%", ("income_tax",)),
    "pa_1pct": ("Change personal allowance by 1%", ("income_tax",)),
    "psa_100_50": (
        "Change Savings allowance by £100 for BR and £50 for HR taxpayers",
        ("income_tax",),
    ),
    "srl_100": (
        "Change starting rate limit for savings income by £100",
        ("income_tax",),
    ),
    "vat_1pp": ("Change standard rate by 1 percentage point", ("vat",)),
}
_RECKONER_CONVENTIONS = (
    "PE CY2026 static accrual vs HMRC projected FY2026-27 direct effects "
    "(first-year cash vs fuller-year; TIE/behavioural response in the "
    "HMRC reckoner per their methodology notes); magnitude comparison — "
    "HMRC publishes per-direction magnitudes, signed PE delta in "
    "annotations"
)


def reckoner_results(db: ScorecardDB) -> tuple[list[PEResult], list[str]]:
    base = _load("uk/baseline_2026.json")["aggregates_gbp"]
    t2 = {r["key"]: r for r in _rows("uk/t2_collation.csv")}
    t1 = {r["reform"]: r for r in _rows("uk/uk_scorecard_first.csv")}
    results, skipped = [], []
    for key, (hint, heads) in RECKONER.items():
        run = _load(f"uk/{key}_2026.json")
        delta = sum(
            run["aggregates_gbp"][h] - base[h] for h in heads
        )
        # Cross-check against the campaign's own collation of this run.
        if key in t2:
            recorded = float(t2[key]["pe_delta_gbp"])
            if abs(delta - recorded) > 1e-3 * max(1.0, abs(recorded)):
                raise ValueError(
                    f"campaign: {key} delta {delta} != t2 {recorded}"
                )
        elif key in t1:
            recorded = abs(float(t1[key]["pe_gbp_m"])) * 1e6
            if abs(abs(delta) - recorded) > 5e5:
                raise ValueError(
                    f"campaign: {key} |delta| {abs(delta)} != "
                    f"tranche-1 {recorded}"
                )
        else:
            raise ValueError(f"campaign: {key} missing from collations")

        section_filter = (
            " AND json_extract(conditions,'$.tax_section')='VAT'"
            if key == "vat_1pp"
            else ""
        )
        hits = [
            r["claim_id"]
            for r in db.conn.execute(
                "SELECT claim_id FROM external_scores WHERE source='hmrc'"
                " AND source_model='hmrc' AND period=2026"
                " AND json_extract(conditions,'$.measure')=?"
                + section_filter,
                (hint,),
            )
        ]
        if len(hits) > 1:
            raise ValueError(f"campaign: {key}: {len(hits)} RR claims")
        if not hits:
            skipped.append(
                f"{key}: no FY2026-27 claim for {hint!r} (reckoner line "
                "publishes later years only)"
            )
            continue
        engine, data = _bundle_meta(run["bundle"])
        results.append(
            PEResult(
                claim_id=hits[0],
                computed_value=abs(delta),
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=engine,
                data_bundle=data,
                pe_construction=(
                    f"{run['pe_construction']}; heads={'+'.join(heads)}; "
                    f"reform={run['reform_json']}"
                ),
                run_id="uk-reckoner-2026",
                computed_at=COMPUTED_AT,
                annotations=[
                    f"signed PE delta {delta:.0f} GBP",
                    _RECKONER_CONVENTIONS,
                ],
                baseline_key=CURRENT_LAW_KEY,
            )
        )
    return results, skipped


# -- 2. UK free joins ----------------------------------------------------
def _match_free_join_claims(db, source, label, period, value):
    """Resolve a free-join row to claim ids plus any vintage caveat.

    The campaign runner selected staged rows by the staged period ints,
    which for DWP BECL were END-year keyed — so its "2026" DWP values
    are the FY2025-26 cells. The published value is the strong key:
    match on it, and when the claim's (re-derived, start-year) period
    disagrees with the CSV's, say so on the result rather than
    misattach or hide it."""
    if source == "uk_obr":
        sql = (
            "SELECT claim_id, period, value FROM external_scores"
            " WHERE source='obr' AND metric='revenue_level'"
            " AND json_extract(conditions,'$.line_item')=?"
        )
    elif source == "uk_dwp":
        sql = (
            "SELECT claim_id, period, value FROM external_scores"
            " WHERE source='dwp' AND source_model='dwp_becl'"
            " AND metric='benefit_cost'"
            " AND json_extract(conditions,'$.program')=?"
        )
    else:
        raise ValueError(f"campaign: free-join source {source!r}")
    rows = [
        r
        for r in db.conn.execute(sql, (label,))
        if abs(r["value"] - value) <= 1e-6 * max(1.0, abs(value))
    ]
    caveats = [
        f"claim describes FY starting {r['period']}, not the runner's "
        f"nominal {period} — the campaign selected DWP rows by the "
        "staged end-year ints (PE CY2026 vs this FY, named)"
        for r in rows
        if r["period"] != period
    ]
    return [r["claim_id"] for r in rows], (caveats[0] if caveats else None)


def free_join_results(db: ScorecardDB) -> list[PEResult]:
    agg = _load("uk/aggregates_2026.json")
    bundle = agg.get("bundle") or _load("uk/baseline_2026.json")["bundle"]
    engine, data = _bundle_meta(bundle)
    results = []
    for row in _rows("uk/free_joins.csv"):
        period = int(row["period"])
        value = float(row["external_value"])
        claims, vintage_caveat = _match_free_join_claims(
            db, row["source"], row["label"], period, value
        )
        computed = row["status"] == "computed"
        if computed and len(claims) != 1:
            raise ValueError(
                f"campaign: free-join {row['label']!r}: "
                f"{len(claims)} claims"
            )
        if not claims:
            raise ValueError(
                f"campaign: free-join {row['label']!r}: no claim"
            )
        for cid in claims:
            annotations = [
                a
                for a in (row["conventions"], row["status"],
                          vintage_caveat)
                if a and a != "computed"
            ]
            results.append(
                PEResult(
                    claim_id=cid,
                    computed_value=(
                        float(row["pe_value"]) if computed else None
                    ),
                    status=(
                        ComparisonStatus.CONSTRUCTED
                        if computed
                        else ComparisonStatus.NOT_COMPUTED
                    ),
                    engine_version=engine,
                    data_bundle=data,
                    pe_construction=row["pe_construction"],
                    run_id="uk-free-joins-2026",
                    computed_at=COMPUTED_AT,
                    annotations=annotations,
                    baseline_key=CURRENT_LAW_KEY,
                )
            )
    return results


# -- 3. OBR measure reversals --------------------------------------------
# key -> the hint substring the campaign runner matched (its external
# anchor is the SUM of the measure's per-head component rows at the
# period — OBR decomposes each measure across tax heads, and the 3.17
# re-estimate rows join the same titles).
_MEASURE_SUBSTRINGS = {
    "hicbc_sb2024": (
        "High Income Child Benefit Charge: increase income threshold to "
        "£60,000"
    ),
    "ee_ni_p2": "2 percentage point cut to the main rate",
    "ee_ni_p4": "2p cut to the main rate of Class 1 employ",
    "class4_p3": "1p cut to the main rate of Class 4",
    "class2_reinstate": "abolish Class 2 self-employed NICs",
    "employer_ab2024": (
        "Employer National Insurance contributions: Increase rate by "
        "1.2 ppts"
    ),
    "art_as2022": "reduce additional rate threshold from £150,000",
    "div_ab2021": "Increase rates of dividend tax by 1.25%",
    "cgt_ab2024": "Increase the main rates of CGT to 18% and 24%",
    "pt_lpl_ss2022": (
        "increase annual primary threshold and lower profits limit"
    ),
}


def obr_measure_results(db: ScorecardDB) -> list[PEResult]:
    results = []
    for row in _rows("uk/obr_measures_collation.csv"):
        if row["status"] != "computed":
            raise ValueError(
                f"campaign: obr measure {row['key']}: {row['status']!r}"
            )
        run = _load(f"uk/obr_measures/{row['key']}_2026.json")
        total = float(row["obr_value_gbp"])
        period = int(row["obr_period"])
        sub = _MEASURE_SUBSTRINGS[row["key"]].lower()
        components = list(
            db.conn.execute(
                "SELECT claim_id, value FROM external_scores"
                " WHERE source='obr' AND metric='revenue_change'"
                " AND period=? AND instr(lower(json_extract(conditions,"
                "'$.measure')), ?) > 0",
                (period, sub),
            )
        )
        if not components:
            raise ValueError(
                f"campaign: obr measure {row['key']}: no component claims"
            )
        got = sum(r["value"] for r in components)
        if abs(got - total) > 1e-3 * max(1.0, abs(total)):
            raise ValueError(
                f"campaign: obr measure {row['key']}: component sum "
                f"{got} != collated anchor {total}"
            )
        # Anchor the result to the dominant component row; the external
        # anchor is the component SUM, named in annotations (a
        # per-component ratio would be meaningless).
        anchor = max(components, key=lambda r: abs(r["value"]))
        engine, data = _bundle_meta(run["bundle"])
        results.append(
            PEResult(
                claim_id=anchor["claim_id"],
                computed_value=abs(float(row["pe_measure_effect_gbp"])),
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=engine,
                data_bundle=data,
                pe_construction=(
                    f"reversal of enacted measure on certified 2026 world: "
                    f"{run['pe_construction']}; reform={run['reform_json']}"
                ),
                run_id="uk-obr-measure-reversals-2026",
                computed_at=COMPUTED_AT,
                annotations=[
                    f"signed PE effect "
                    f"{float(row['pe_measure_effect_gbp']):.0f} GBP "
                    "(measure direction, magnitude compared)",
                    f"external anchor = sum of the measure's "
                    f"{len(components)} component rows at FY{period} "
                    f"({total:.0f} GBP); this result anchors to the "
                    "largest component — compare against the annotated "
                    "total, not this row's value",
                    row["conventions"],
                    f"confidence: {row['confidence']}",
                ],
                baseline_key=CURRENT_LAW_KEY,
            )
        )
    return results


# -- 4. RF April-2026 uprating parameter checks --------------------------
# uprating_check key -> (RF conditions.program value, tree_changes key or
# None when the check itself found no comparable single parameter, and a
# construction note).
UPRATING_MAP = {
    "inflation_linked_benefits": (
        "inflation-linked benefits", "uc_child_element",
        "checked via the UC child element, a CPI-linked parameter",
    ),
    "state_pension_triple_lock_earnings": (
        "State Pension (triple lock: earnings growth)",
        "state_pension_new",
        "checked via the new State Pension weekly amount",
    ),
    "uc_standard_allowance": (
        "UC standard allowance", "uc_standard_single_25plus",
        "checked via the single-25+ standard allowance (couples uprate "
        "identically in the tree probe)",
    ),
    "uc_standard_allowance_u25": (
        "UC standard allowance, under-25s", "uc_standard_single_u25",
        "checked via the single-under-25 standard allowance",
    ),
    "uc_health_element_existing": (
        "UC health element, existing recipients", None,
        "not comparable to a single tree parameter: the probe's LCWRA "
        "amount change (−48.7%) is the AB2025 new-claimant halving, not "
        "the existing-recipient uprating RF states — the new/existing "
        "split needs its encoding mapped first (check note verbatim)",
    ),
    "lha_frozen": (
        "Local Housing Allowance (frozen)", None,
        "LHA rates are data-driven per BRMA in policyengine-uk; freeze "
        "verification needs the LHA parameter/dataset mechanism (check "
        "note verbatim)",
    ),
}


def uprating_results(db: ScorecardDB) -> tuple[list[PEResult], list[str]]:
    check = _load("uk/uprating_check_april2026.json")
    tree = check["tree_changes"]
    results, skipped = [], []
    for key, staged in check["rf_staged_claims"].items():
        program, tree_key, note = UPRATING_MAP[key]
        cid = _one(
            db,
            f"uprating {key}",
            "SELECT claim_id FROM external_scores"
            " WHERE source='resolution_foundation'"
            " AND metric='benefit_uprating' AND period=2026"
            " AND json_extract(conditions,'$.program')=?"
            " AND json_extract(conditions,'$.component') IS NULL",
            (program,),
        )
        entry = tree.get(tree_key) if tree_key else None
        if entry is None:
            skipped.append(f"{key}: {note} (RF staged {staged})")
            results.append(
                PEResult(
                    claim_id=cid,
                    computed_value=None,
                    status=ComparisonStatus.NOT_COMPUTED,
                    engine_version=check["tree_package"],
                    data_bundle="parameter-tree-only",
                    pe_construction="",
                    run_id="uk-uprating-check-2026",
                    computed_at=COMPUTED_AT,
                    annotations=[note, f"RF staged {staged}"],
                    baseline_key=CURRENT_LAW_KEY,
                )
            )
            continue
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=entry["pct"],
                status=ComparisonStatus.COMPARABLE,
                engine_version=check["tree_package"],
                data_bundle="parameter-tree-only",
                pe_construction=(
                    f"{entry['path']}: {entry['before']} -> "
                    f"{entry['after']} across "
                    f"{check['windows']['before']}→"
                    f"{check['windows']['after']}"
                ),
                run_id="uk-uprating-check-2026",
                computed_at=COMPUTED_AT,
                annotations=[
                    "pure parameter check (no data artifact); April-2026 "
                    "uprating in the installed policyengine-uk tree vs "
                    "RF's published parameter set",
                    note,
                ],
                baseline_key=CURRENT_LAW_KEY,
            )
        )
    return results, skipped


# -- 5/6. TPC and PWBM revenue legs --------------------------------------
_TPC_CONVENTIONS = (
    "PE calendar-year 2026 liability vs TPC fiscal-year cash; PE static "
    "vs TPC conventional (T25-0209) / microdynamic (T26-0029); PE "
    "baseline = enacted-OBBBA current law vs claim baseline as labeled "
    "(draft≈enacted for these provisions — named delta, view guard "
    "applies)"
)
# run key -> (period, provision-match SQL fragment, option or None)
_TPC_RUNS = [
    ("ctc_opt1", 2025, "Increase child tax credit%", "Option 1"),
    ("ctc_opt2", 2025, "Increase CTC amount to $2,500 and CTC maximum%",
     "Option 2"),
    ("ctc_opt3", 2025, "Increase CTC amount to $2,500 and CTC maximum%",
     "Option 3"),
    ("ctc_opt1", 2026, "Increase child tax credit%", "Option 1"),
    ("ctc_opt2", 2026, "Increase CTC amount to $2,500 and CTC maximum%",
     "Option 2"),
    ("ctc_opt3", 2026, "Increase CTC amount to $2,500 and CTC maximum%",
     "Option 3"),
    ("toprate_opt1", 2026, "Increase top individual income tax rate%",
     "Option 1"),
    ("toprate_opt2", 2026, "Increase top individual income tax rate%",
     "Option 2"),
    ("toprate_opt3", 2026, "Increase top individual income tax rate%",
     "Option 3"),
    ("total_opt1", 2026, "Total for both provisions", "Option 1"),
    ("total_opt2", 2026, "Total for both provisions", "Option 2"),
    ("total_opt3", 2026, "Total for both provisions", "Option 3"),
]


def _income_tax_delta(run: dict, year: int) -> float:
    base = _load(f"us/tpc_ctc/baseline_{year}.json")["aggregates_usd"]
    return run["aggregates_usd"]["income_tax"] - base["income_tax"]


def tpc_results(db: ScorecardDB) -> list[PEResult]:
    results = []
    for key, year, provision_like, option in _TPC_RUNS:
        run = _load(f"us/tpc_ctc/{key}_{year}.json")
        cid = _one(
            db,
            f"tpc {key} {year}",
            "SELECT claim_id FROM external_scores WHERE source='tpc'"
            " AND metric='revenue_change' AND period=?"
            " AND json_extract(conditions,'$.option')=?"
            " AND json_extract(conditions,'$.provision') LIKE ?"
            " AND reform_json LIKE '%obbba_senate_ctc_top_rate_options%'",
            (year, option, provision_like),
        )
        engine, data = _bundle_meta(run["bundle"])
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=_income_tax_delta(run, year),
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=engine,
                data_bundle=data,
                pe_construction=(
                    "; ".join(run["pe_construction"])
                    + f"; reform={run['reform_json']}"
                ),
                run_id=f"tpc-t25-0209-{key}-{year}",
                computed_at=COMPUTED_AT,
                annotations=[_TPC_CONVENTIONS],
                baseline_key=CURRENT_LAW_KEY,
            )
        )
    # AFA: the bill's $2,000 floor vs the onto-OBBBA $2,200 reading —
    # both constructions land on the one T26-0029 claim (history table).
    for key, note in (
        ("afa_bill_floor", "bill $2,000 floor construction"),
        ("afa_onto_obbba", "onto-OBBBA $2,200 mid-tier construction"),
    ):
        run = _load(f"us/tpc_ctc/{key}_2026.json")
        cid = _one(
            db,
            f"tpc {key}",
            "SELECT claim_id FROM external_scores WHERE source='tpc'"
            " AND metric='revenue_change' AND period=2026"
            " AND json_extract(conditions,'$.provision')="
            "'American Family Act'",
            (),
        )
        engine, data = _bundle_meta(run["bundle"])
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=_income_tax_delta(run, 2026),
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=engine,
                data_bundle=data,
                pe_construction=(
                    "; ".join(run["pe_construction"])
                    + f"; reform={run['reform_json']}"
                ),
                run_id=f"tpc-t26-0029-{key}",
                computed_at=COMPUTED_AT,
                annotations=[
                    f"AFA floor ambiguity bound: {note} (width ≈ $1.8B)",
                    _TPC_CONVENTIONS,
                ],
                baseline_key=CURRENT_LAW_KEY,
            )
        )
    return results


def pwbm_results(db: ScorecardDB) -> list[PEResult]:
    results = []
    for year in (2025, 2026):
        run = _load(f"us/pwbm_ss/ss_notax_{year}.json")
        cid = _one(
            db,
            f"pwbm ss {year}",
            "SELECT claim_id FROM external_scores WHERE source='pwbm'"
            " AND metric='revenue_change' AND period=?"
            " AND json_extract(conditions,'$.provision')="
            "'Ending taxation of Social Security benefits'"
            " AND json_extract(conditions,'$.scoring')='conventional'",
            (year,),
        )
        engine, data = _bundle_meta(run["bundle"])
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=_income_tax_delta(run, year),
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=engine,
                data_bundle=data,
                pe_construction=(
                    "; ".join(run["pe_construction"])
                    + f"; reform={run['reform_json']}"
                ),
                run_id=f"pwbm-ss-notax-{year}",
                computed_at=COMPUTED_AT,
                annotations=[
                    "PE CY liability vs PWBM FY cash (named); taxable SS "
                    "verified 0.0 exactly under the construction; senior-"
                    "deduction baseline vintage is a named axis",
                ],
                baseline_key=CURRENT_LAW_KEY,
            )
        )
    return results


# -- 7. CPSP CTC counterfactual levels ------------------------------------
_CPSP_SCENARIO_REFORM = {
    "TCJA CTC": '%"tcja_ctc"%',
    "No CTC": '%"no_ctc"%',
    "OBBBA CTC": '%"obbba_ctc"%',
    "AFA CTC": '%"afa_ctc"%',
}
_CPSP_LEVEL_RATIONALE = (
    "Level comparison vs an ASEC-anchored series: Populace CALCULATES "
    "benefits and recalibrates where the ASEC carries reported "
    "attributes, and treats thresholds differently (descriptive "
    "decomposition in sources/campaign-2026-08-02/us/SPM_NOTES.md). "
    "A named sub-channel: Early Head Start at engine-default 100% "
    "take-up flows inside household_net_income "
    "(populace#593). Change metrics between CTC worlds are the "
    "same-assumptions surface and are directionally consistent."
)


def cpsp_results(db: ScorecardDB) -> tuple[list[PEResult], list[tuple]]:
    results, diagnoses = [], []
    staged_path = CAMPAIGN / "us/cpsp_ctc/staged_rows_2024.jsonl"
    for line in staged_path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        match = row["external_claim_match"]
        conds = match["conditions"]
        if conds["poverty_threshold"] != "100pct_spm":
            raise ValueError(
                f"campaign: cpsp threshold {conds['poverty_threshold']!r}"
            )
        # The ingested counterfactual claims carry geography+subgroup
        # only (100%-SPM is the tables' single threshold); the scenario
        # world rides the reform descriptor.
        cid = _one(
            db,
            f"cpsp {conds['policy_scenario']} {conds['subgroup']}",
            "SELECT claim_id FROM external_scores WHERE source='cpsp'"
            " AND metric='poverty_rate' AND period=2024"
            " AND json_extract(conditions,'$.subgroup')=?"
            " AND reform_json LIKE ?",
            (
                conds["subgroup"],
                _CPSP_SCENARIO_REFORM[conds["policy_scenario"]],
            ),
        )
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=row["pe_value"],
                status=ComparisonStatus.CONSTRUCTED,
                engine_version="policyengine-us 1.764.6",
                data_bundle=_load("run_meta.json")["bundle"][
                    "certified_data_build_id"
                ],
                pe_construction=(
                    "; ".join(row["pe_construction"])
                    + f"; reform={row['reform_json']}; baseline executed: "
                    + row["baseline_executed"]
                ),
                run_id="cpsp-ctc-counterfactuals-2024",
                computed_at=COMPUTED_AT,
                annotations=[
                    "CPSP stated basis: 100% take-up, no behavior — "
                    "credit take-up flags forced to match",
                ],
                baseline_key=CURRENT_LAW_KEY,
            )
        )
        diagnoses.append(
            (
                cid,
                "methodological_difference",
                _CPSP_LEVEL_RATIONALE,
                "https://github.com/PolicyEngine/populace/issues/593",
            )
        )
    return results, diagnoses


# -- 8. JCT OBBBA CTC-extension provision ---------------------------------
def obbba_results(db: ScorecardDB) -> list[PEResult]:
    run = _load("us/obbba_family/ctc_ext_2026.json")
    base = _load("us/tpc_ctc/baseline_2026.json")["aggregates_usd"]
    # Extension effect on receipts = current law (extension in force)
    # minus the expiry counterfactual this run executed: the expiry
    # world collects MORE income tax, so the effect is negative (a
    # revenue cost), matching JCT's sign convention.
    delta = base["income_tax"] - run["aggregates_usd"]["income_tax"]
    cid = _one(
        db,
        "jct ctc extension provision",
        "SELECT claim_id FROM external_scores WHERE source='jct'"
        " AND period=2026"
        " AND json_extract(conditions,'$.bill_version')='JCX-35-25'"
        " AND json_extract(conditions,'$.provision')="
        "'4. Extension and enhancement of increased child tax credit [1]'",
        (),
    )
    engine, data = _bundle_meta(run["bundle"])
    return [
        PEResult(
            claim_id=cid,
            computed_value=delta,
            status=ComparisonStatus.CONSTRUCTED,
            engine_version=engine,
            data_bundle=data,
            pe_construction=(
                "; ".join(run["pe_construction"])
                + f"; expiry world: {run['world']}"
            ),
            run_id="obbba-family-ctc-ext-2026",
            computed_at=COMPUTED_AT,
            annotations=[
                "JCT scores provisions SEQUENTIALLY (each conditional on "
                "the prior stack); this is a single-provision "
                "marginal-vs-current-law run — interaction terms are a "
                "named convention delta (RUNNABILITY.md)",
                "PE CY2026 liability vs JCT FY2026 cash (named)",
            ],
            baseline_key=CURRENT_LAW_KEY,
        )
    ]


# -- 9. US CBO free joins --------------------------------------------------
def cbo_free_join_results(db: ScorecardDB) -> list[PEResult]:
    meta = _load("run_meta.json")["bundle"]
    engine, data = meta["model_version"], meta["certified_data_build_id"]
    results = []
    for row in _rows("us/free_joins_cbo.csv"):
        computed = row["status"] == "computed"
        cbo_value = float(row["cbo_value"])
        sql = (
            "SELECT claim_id, value FROM external_scores"
            " WHERE source='cbo' AND metric=? AND period=?"
            " AND source_column=?"
        )
        args: list = [row["metric"], int(row["period"]),
                      row["source_column"]]
        if row["program"]:
            sql += " AND json_extract(conditions,'$.program')=?"
            args.append(row["program"])
        hits = [
            r["claim_id"]
            for r in db.conn.execute(sql, args)
            if abs(r["value"] - cbo_value)
            <= 1e-6 * max(1.0, abs(cbo_value))
        ]
        if len(hits) != 1:
            raise ValueError(
                f"campaign: cbo free-join {row['program']}/{row['metric']}"
                f"/{row['period']}: {len(hits)} claims"
            )
        annotations = [row["conventions"]]
        if not computed:
            annotations.append(row["status"])
        results.append(
            PEResult(
                claim_id=hits[0],
                computed_value=(
                    float(row["pe_value"]) if computed else None
                ),
                status=(
                    ComparisonStatus.CONSTRUCTED
                    if computed
                    else ComparisonStatus.NOT_COMPUTED
                ),
                engine_version=engine,
                data_bundle=data,
                pe_construction=row["pe_construction"],
                run_id="us-cbo-free-joins-2026",
                computed_at=COMPUTED_AT,
                annotations=[a for a in annotations if a],
                baseline_key=CURRENT_LAW_KEY,
            )
        )
    return results


# -- exhibits: the two-child-limit counterfactual family -------------------
_TWO_CHILD_REFORM = {
    "framework": "policy_ref",
    "reform": {"policy": "two_child_limit_removal"},
    "baseline": {"policy": "pre_ab2025"},
    "rulespec_ref": None,
}
_TWO_CHILD_NOTE = (
    "PE 2026 current law already abolishes the UC two-child limit "
    "(AB2025 encoded), so removal is measured against an executed "
    "reinstated counterfactual (gov.dwp.universal_credit.elements.child."
    "limit.child_count: inf -> 2, born-pre-2017 exemptions active — the "
    "actual partially-rolled-in 2026 law). Line convention contributes "
    "zero (person-weighted medians identical between worlds); take-up "
    "quantified at +34k via the entitlements-basis pair."
)


def two_child_exhibits() -> list[dict]:
    reform_json = json.dumps(_TWO_CHILD_REFORM, sort_keys=True)
    reform_key_ = "two-child-removal-vs-pre-ab2025"
    rows = []

    def add(metric, unit, value, baseline_value, conditions, engine, data,
            run_id, extra_note=""):
        delta = (
            value - baseline_value if baseline_value is not None else None
        )
        rows.append(
            {
                "exhibit": "uk-two-child-limit",
                "reform_key": reform_key_,
                "reform_json": reform_json,
                "metric": metric,
                "unit_concept": unit,
                "period": 2026,
                "time_basis": "fiscal_year",
                "conditions": conditions,
                "geography": "UK",
                "program": "universal_credit",
                "value": value,
                "baseline_value": baseline_value,
                "delta": delta,
                "engine_version": engine,
                "data_bundle": data,
                "run_id": run_id,
                "computed_at": COMPUTED_AT,
                "note": (_TWO_CHILD_NOTE + (" " + extra_note).rstrip()),
                "baseline_key": PRE_AB2025_KEY,
            }
        )

    for takeup, fname in (
        ("calibrated", "uk/two_child_fixed_line_2026.json"),
        ("entitlements_basis", "uk/two_child_fixed_line_fulltakeup_2026.json"),
    ):
        run = _load(fname)
        engine, data = _bundle_meta(run["worlds"]["with_limit"]["bundle"])
        res = run["results"]["floating"]
        for group in ("hbai_dep", "u16", "all"):
            add(
                "poverty_count_change",
                "persons" if group == "all" else "children_under_18",
                res["without_limit"][group]["count"],
                res["with_limit"][group]["count"],
                {
                    "takeup": takeup,
                    "child_definition": group,
                    "poverty_line": (
                        "relative AHC 60% median, person-weighted, "
                        "floating"
                    ),
                    "fy": "2026-27",
                },
                engine, data, f"uk-two-child-{takeup}-2026",
            )
        add(
            "poverty_rate_change",
            "percentage_points",
            res["without_limit"]["hbai_dep"]["rate"] * 100,
            res["with_limit"]["hbai_dep"]["rate"] * 100,
            {
                "takeup": takeup,
                "child_definition": "hbai_dep",
                "poverty_line": (
                    "relative AHC 60% median, person-weighted, floating"
                ),
                "fy": "2026-27",
            },
            engine, data, f"uk-two-child-{takeup}-2026",
        )
        add(
            "benefit_cost",
            "gbp",
            run["worlds"]["without_limit"]["aggregates_gbp"][
                "universal_credit"
            ],
            run["worlds"]["with_limit"]["aggregates_gbp"][
                "universal_credit"
            ],
            {"takeup": takeup, "measure": "uc_cost_of_removal",
             "fy": "2026-27"},
            engine, data, f"uk-two-child-{takeup}-2026",
            extra_note=(
                f"UC cost of removal "
                f"{run['uc_cost_of_removal_gbp']:.0f} GBP."
            ),
        )

    # Absolute-AHC continuity pair (the first-cut construction).
    removal = _load("uk/two_child_limit_removal_2026.json")
    reinstate = _load("uk/two_child_reinstate_2026.json")
    engine, data = _bundle_meta(removal["bundle"])
    add(
        "poverty_count_change",
        "children_under_18",
        removal["poverty"]["count_child_u16"],
        reinstate["poverty"]["count_child_u16"],
        {
            "takeup": "calibrated",
            "child_definition": "u16",
            "poverty_line": "absolute AHC (parameter threshold)",
            "fy": "2026-27",
        },
        engine, data, "uk-two-child-absline-2026",
        extra_note="Absolute-line continuity check (reproduces 181k u16).",
    )
    return rows


# -- runner ---------------------------------------------------------------
def ingest(db_path: Path) -> dict:
    db = ScorecardDB(db_path)
    stats: dict = {}

    reckoner, reckoner_skips = reckoner_results(db)
    free_joins = free_join_results(db)
    measures = obr_measure_results(db)
    uprating, uprating_skips = uprating_results(db)
    tpc = tpc_results(db)
    pwbm = pwbm_results(db)
    cpsp, cpsp_diagnoses = cpsp_results(db)
    obbba = obbba_results(db)
    cbo = cbo_free_join_results(db)

    all_results = (
        reckoner + free_joins + measures + uprating + tpc + pwbm + cpsp
        + obbba + cbo
    )
    stats["results"] = {
        "uk_reckoner": len(reckoner),
        "uk_free_joins": len(free_joins),
        "uk_obr_measures": len(measures),
        "uk_uprating": len(uprating),
        "tpc": len(tpc),
        "pwbm": len(pwbm),
        "cpsp": len(cpsp),
        "jct_obbba": len(obbba),
        "cbo_free_joins": len(cbo),
        "total": len(all_results),
    }
    stats["skipped"] = reckoner_skips + uprating_skips
    # Idempotent re-ingest: this batch owns its run ids.
    run_ids = sorted({r.run_id for r in all_results})
    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_results WHERE run_id IN ("
            + ",".join("?" * len(run_ids))
            + ")",
            run_ids,
        )
    db.add_results(all_results)

    for cid, cls, rationale, link in cpsp_diagnoses:
        db.diagnose(cid, cls, rationale, link)
    stats["diagnoses"] = len(cpsp_diagnoses)

    exhibits = two_child_exhibits()
    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_exhibits WHERE exhibit='uk-two-child-limit'"
        )
    stats["exhibits"] = db.add_exhibits(exhibits)

    stats["baselines_registered"] = register_baselines(db)

    joined_lanes = (
        "hmrc-personal-tax", "obr-measures", "obr-welfare", "dwp-takeup",
        "rf-outlook", "cpsp-poverty", "tpc-distribution",
        "pwbm-reform-scores", "jct-reform-scores", "cbo-baseline",
    )
    for lane in joined_lanes:
        row = db.conn.execute(
            "SELECT detail FROM lanes WHERE lane=?", (lane,)
        ).fetchone()
        if row is None:
            raise ValueError(f"campaign: lane {lane} missing")
        db.set_lane(lane, "computed", row["detail"], COMPUTED_AT[:10])
    db.set_lane(
        "campaign-compute-2026-08-02",
        "computed",
        f"{len(all_results)} PE results joined "
        f"({stats['results']}); {len(exhibits)} two-child exhibits vs "
        "registered pre_ab2025 baseline; skips: "
        + ("; ".join(stats["skipped"]) or "none"),
        COMPUTED_AT[:10],
    )
    stats["coverage"] = db.coverage()
    db.close()
    return stats


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
