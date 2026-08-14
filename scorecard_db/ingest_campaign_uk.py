"""Ingest the campaign's UK compute batch as PE results + exhibits.

The sibling of scorecard_db/ingest_campaign.py (which attaches the
campaign's day-1 US families from sources/campaign-20260802/us/ and is
canonical there). This module lands the UK side, which that module
deliberately deferred until the UK harvest ingest existed. It reads the
vendored raw run files (sources/campaign-20260802/uk_runs/ — full bundle
provenance; .npz world arrays and logs stay outside) and RECOMPUTES each
delta from run + baseline aggregates, cross-checking against the
campaign's own collations before landing; joins resolve claims by DB
query with exactly-one-match asserted.

The campaign's staged UK descriptor files (sources/campaign-20260802/
uk/*.jsonl) are deliberately superseded rather than attached: they cover
a strict subset (14 tranche-2 reckoner rows vs all 23 runs here, 16
computed free-joins vs 25 incl. the scoping skips, uprating as
unattached exhibits vs real RF-claim joins here) and their reckoner
descriptors are under-determined against the normalized DB vocabulary
(no measure key — several reckoner lines share a section × year). The
one thing taken from that staging is its two-child PENTAGON attachments
(uk/two_child.jsonl): three cross-model rows joining PE's removal run to
the RF-cited government claims and UKMOD's net-package leg —
descriptive statuses verbatim, per-leg concept deltas in annotations.

Join families:

1. **UK ready reckoner** (23 runs ↔ hmrc RR claims): computed_value is
   the |head-delta| magnitude (HMRC publishes per-direction magnitudes;
   the signed PE delta and heads ride annotations), cross-checked
   against t2_collation.csv / uk_scorecard_first.csv.
2. **UK free joins** (free_joins.csv ↔ OBR EFO revenue levels and DWP
   BECL forecast lines by line/value match); skipped rows land as
   not_computed with the scoping reason verbatim.
3. **OBR measure reversals** (obr_measures_collation.csv ↔ measures-
   database claims; the external anchor is the measure's per-head
   component SUM — the result anchors to the dominant component with
   the aggregation named).
4. **April-2026 uprating checks** (uprating_check_april2026.json ↔ RF
   benefit_uprating claims — the one `comparable` family: pure
   parameter-tree checks, no data artifact involved).
5. **Two-child pentagon attachments** (their staged rows, translated).

Also here: the descriptive-register diagnoses for the campaign's CPSP
CTC level rows (methodological_difference, populace#593 EHS sub-channel
in the rationale) — the results themselves attach via ingest_campaign.

PE-only counterfactuals — the two-child-limit removal family (floating/
fixed line × calibrated/entitlements take-up, plus the absolute-line
continuity pair) — land in pe_exhibits with reform
two_child_limit_removal against the registered pre_ab2025 baseline
(direction explicit, issue #13 point 5).
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

CAMPAIGN = REPO / "sources" / "campaign-20260802"
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
    "additional_rate_1p": ("Increase additional rate by 1p (yield)", ("income_tax",)),
    "basic_rate_1p": ("Change basic rate by 1p", ("income_tax",)),
    "brl_10pct": ("Increase basic rate limit by 10% (cost)", ("income_tax",)),
    "brl_1pct": ("Change basic rate limit by 1%", ("income_tax",)),
    "cb_additional_1pw": (
        "Increase subsequent child rate by £1 per week (cost)",
        ("child_benefit",),
    ),
    "cb_first_1pw": (
        "Increase first child rate by £1 per week (cost)",
        ("child_benefit",),
    ),
    "class4_1pp": (
        "Change Class 4 main rate by 1 percentage point",
        ("national_insurance",),
    ),
    "dividend_allowance_100": ("Change dividend allowance by £100", ("income_tax",)),
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
    "ni_lpl_104": (
        "Change lower profits limit by £104 per year",
        ("national_insurance",),
    ),
    "ni_pt_2pw": (
        "Change employee entry threshold by £2 per week",
        ("national_insurance",),
    ),
    "ni_st_2pw": ("Change employer threshold by £2 per week", ("ni_employer",)),
    "ni_uel_10pw": (
        "Change upper earnings limit by £10 per week",
        ("national_insurance",),
    ),
    "ni_upl_520": (
        "Change upper profits limit by £520 per year",
        ("national_insurance",),
    ),
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
    base = _load("uk_runs/baseline_2026.json")["aggregates_gbp"]
    t2 = {r["key"]: r for r in _rows("uk_runs/t2_collation.csv")}
    t1 = {r["reform"]: r for r in _rows("uk_runs/uk_scorecard_first.csv")}
    results, skipped = [], []
    for key, (hint, heads) in RECKONER.items():
        run = _load(f"uk_runs/{key}_2026.json")
        delta = sum(run["aggregates_gbp"][h] - base[h] for h in heads)
        # Cross-check against the campaign's own collation of this run.
        if key in t2:
            recorded = float(t2[key]["pe_delta_gbp"])
            if abs(delta - recorded) > 1e-3 * max(1.0, abs(recorded)):
                raise ValueError(f"campaign: {key} delta {delta} != t2 {recorded}")
        elif key in t1:
            recorded = abs(float(t1[key]["pe_gbp_m"])) * 1e6
            if abs(abs(delta) - recorded) > 5e5:
                raise ValueError(
                    f"campaign: {key} |delta| {abs(delta)} != tranche-1 {recorded}"
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
                " AND json_extract(conditions,'$.measure')=?" + section_filter,
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
    agg = _load("uk_runs/aggregates_2026.json")
    bundle = agg.get("bundle") or _load("uk_runs/baseline_2026.json")["bundle"]
    engine, data = _bundle_meta(bundle)
    results = []
    attached: set[str] = set()
    for row in _rows("uk_runs/free_joins.csv"):
        period = int(row["period"])
        value = float(row["external_value"])
        claims, vintage_caveat = _match_free_join_claims(
            db, row["source"], row["label"], period, value
        )
        computed = row["status"] == "computed"
        if computed and len(claims) != 1:
            raise ValueError(
                f"campaign: free-join {row['label']!r}: {len(claims)} claims"
            )
        if not claims:
            raise ValueError(f"campaign: free-join {row['label']!r}: no claim")
        # The CSV lists some skipped heads once per source table; a value
        # identical across tables (Self assessment) would otherwise attach
        # the same reason to the same claim twice.
        claims = [c for c in claims if c not in attached]
        attached.update(claims)
        for cid in claims:
            annotations = [
                a
                for a in (row["conventions"], row["status"], vintage_caveat)
                if a and a != "computed"
            ]
            results.append(
                PEResult(
                    claim_id=cid,
                    computed_value=(float(row["pe_value"]) if computed else None),
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
        "High Income Child Benefit Charge: increase income threshold to £60,000"
    ),
    "ee_ni_p2": "2 percentage point cut to the main rate",
    "ee_ni_p4": "2p cut to the main rate of Class 1 employ",
    "class4_p3": "1p cut to the main rate of Class 4",
    "class2_reinstate": "abolish Class 2 self-employed NICs",
    "employer_ab2024": (
        "Employer National Insurance contributions: Increase rate by 1.2 ppts"
    ),
    "art_as2022": "reduce additional rate threshold from £150,000",
    "div_ab2021": "Increase rates of dividend tax by 1.25%",
    "cgt_ab2024": "Increase the main rates of CGT to 18% and 24%",
    "pt_lpl_ss2022": ("increase annual primary threshold and lower profits limit"),
}


def obr_measure_results(db: ScorecardDB) -> list[PEResult]:
    results = []
    for row in _rows("uk_runs/obr_measures_collation.csv"):
        if row["status"] != "computed":
            raise ValueError(f"campaign: obr measure {row['key']}: {row['status']!r}")
        run = _load(f"uk_runs/obr_measures/{row['key']}_2026.json")
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
            raise ValueError(f"campaign: obr measure {row['key']}: no component claims")
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
        "inflation-linked benefits",
        "uc_child_element",
        "checked via the UC child element, a CPI-linked parameter",
    ),
    "state_pension_triple_lock_earnings": (
        "State Pension (triple lock: earnings growth)",
        "state_pension_new",
        "checked via the new State Pension weekly amount",
    ),
    "uc_standard_allowance": (
        "UC standard allowance",
        "uc_standard_single_25plus",
        "checked via the single-25+ standard allowance (couples uprate "
        "identically in the tree probe)",
    ),
    "uc_standard_allowance_u25": (
        "UC standard allowance, under-25s",
        "uc_standard_single_u25",
        "checked via the single-under-25 standard allowance",
    ),
    "uc_health_element_existing": (
        "UC health element, existing recipients",
        None,
        "not comparable to a single tree parameter: the probe's LCWRA "
        "amount change (−48.7%) is the AB2025 new-claimant halving, not "
        "the existing-recipient uprating RF states — the new/existing "
        "split needs its encoding mapped first (check note verbatim)",
    ),
    "lha_frozen": (
        "Local Housing Allowance (frozen)",
        None,
        "LHA rates are data-driven per BRMA in policyengine-uk; freeze "
        "verification needs the LHA parameter/dataset mechanism (check "
        "note verbatim)",
    ),
}


def uprating_results(db: ScorecardDB) -> tuple[list[PEResult], list[str]]:
    check = _load("uk_runs/uprating_check_april2026.json")
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


# -- CPSP descriptive-register diagnoses -----------------------------------
# The campaign's CPSP CTC level results attach via ingest_campaign (US
# families); the register adjudication for those LEVEL rows lands here:
# methodological_difference, strictly descriptive (issue #9), with the
# populace#593 EHS sub-channel named in the rationale.
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
    "decomposition in sources/campaign-20260802/SPM_NOTES.md). "
    "A named sub-channel: Early Head Start at engine-default 100% "
    "take-up flows inside household_net_income "
    "(populace#593). Change metrics between CTC worlds are the "
    "same-assumptions surface and are directionally consistent."
)


def cpsp_diagnoses(db: ScorecardDB) -> list[tuple]:
    diagnoses = []
    for scenario, reform_like in _CPSP_SCENARIO_REFORM.items():
        for subgroup in ("children_under_18", "children_under_6"):
            cid = _one(
                db,
                f"cpsp {scenario} {subgroup}",
                "SELECT claim_id FROM external_scores WHERE source='cpsp'"
                " AND metric='poverty_rate' AND period=2024"
                " AND json_extract(conditions,'$.subgroup')=?"
                " AND reform_json LIKE ?",
                (subgroup, reform_like),
            )
            diagnoses.append(
                (
                    cid,
                    "methodological_difference",
                    _CPSP_LEVEL_RATIONALE,
                    "https://github.com/PolicyEngine/populace/issues/593",
                )
            )
    return diagnoses


# -- Two-child pentagon attachments ----------------------------------------
# The three cross-model rows from the campaign's staged
# uk/two_child.jsonl, translated into the normalized DB vocabulary and
# pinned to exactly-one claim each. The fourth staged row is exhibit:true
# without exhibit_meta (their contract would defer it) — the full
# convention grid lands as this module's pe_exhibits instead. PE executed
# the reinstated counterfactual as its baseline: pre_ab2025 (#13).
_PENTAGON_TARGETS = {
    # staged row index -> (label, SQL predicate, args builder)
    0: (
        "RF-cited government −450k claim (FY2029-30)",
        "SELECT claim_id FROM external_scores"
        " WHERE source='resolution_foundation'"
        " AND metric='poverty_count_change' AND period=2029"
        " AND json_extract(conditions,'$.attribution')="
        "'Government estimate cited by RF'",
    ),
    1: (
        "RF-cited HMT Budget-2025 two-child costing (FY2026-27)",
        "SELECT claim_id FROM external_scores"
        " WHERE source='resolution_foundation'"
        " AND metric='exchequer_impact' AND period=2026"
        " AND json_extract(conditions,'$.attribution')="
        "'HM Treasury, Budget 2025 Table 4.1 (cited by RF)'"
        " AND json_extract(conditions,'$.measure') LIKE"
        " 'repeal two-child limit%'",
    ),
    2: (
        "UKMOD CeMPA net-package children leg (FY2026-27)",
        "SELECT claim_id FROM external_scores WHERE source='ukmod'"
        " AND metric='poverty_count_change' AND period=2026"
        " AND json_extract(conditions,'$.subgroup')='Children'"
        " AND json_extract(conditions,'$.geography')='UK'"
        " AND json_extract(conditions,'$.scenario')="
        "'reform_minus_baseline'",
    ),
}


def pentagon_results(db: ScorecardDB) -> tuple[list[PEResult], int]:
    staged = [
        json.loads(line)
        for line in (CAMPAIGN / "uk" / "two_child.jsonl").read_text().splitlines()
        if line.strip()
    ]
    results, deferred = [], 0
    for i, row in enumerate(staged):
        if row.get("exhibit"):
            deferred += 1  # superseded by this module's full exhibit grid
            continue
        label, sql = _PENTAGON_TARGETS[i]
        cid = _one(db, f"pentagon {label}", sql, ())
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=row["pe_value"],
                status=ComparisonStatus(row["status"]),
                engine_version=row["engine_version"],
                data_bundle=row["data_bundle"],
                pe_construction=row["pe_construction"],
                # Own namespace (the staged rows carry campaign-20260802-
                # two-child; ingest_campaign's committed-DB provenance
                # checks reserve the campaign-% prefix for the US bundle).
                run_id="uk-two-child-pentagon-2026",
                computed_at=row["computed_at"],
                annotations=row["annotations"],
                baseline_key=PRE_AB2025_KEY,
            )
        )
    return results, deferred


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

    def add(
        metric,
        unit,
        value,
        baseline_value,
        conditions,
        engine,
        data,
        run_id,
        extra_note="",
    ):
        delta = value - baseline_value if baseline_value is not None else None
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
        ("calibrated", "uk_runs/two_child_fixed_line_2026.json"),
        ("entitlements_basis", "uk_runs/two_child_fixed_line_fulltakeup_2026.json"),
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
                        "relative AHC 60% median, person-weighted, floating"
                    ),
                    "fy": "2026-27",
                },
                engine,
                data,
                f"uk-two-child-{takeup}-2026",
            )
        add(
            "poverty_rate_change",
            "percentage_points",
            res["without_limit"]["hbai_dep"]["rate"] * 100,
            res["with_limit"]["hbai_dep"]["rate"] * 100,
            {
                "takeup": takeup,
                "child_definition": "hbai_dep",
                "poverty_line": ("relative AHC 60% median, person-weighted, floating"),
                "fy": "2026-27",
            },
            engine,
            data,
            f"uk-two-child-{takeup}-2026",
        )
        add(
            "benefit_cost",
            "gbp",
            run["worlds"]["without_limit"]["aggregates_gbp"]["universal_credit"],
            run["worlds"]["with_limit"]["aggregates_gbp"]["universal_credit"],
            {"takeup": takeup, "measure": "uc_cost_of_removal", "fy": "2026-27"},
            engine,
            data,
            f"uk-two-child-{takeup}-2026",
            extra_note=(f"UC cost of removal {run['uc_cost_of_removal_gbp']:.0f} GBP."),
        )

    # Absolute-AHC continuity pair (the first-cut construction).
    removal = _load("uk_runs/two_child_limit_removal_2026.json")
    reinstate = _load("uk_runs/two_child_reinstate_2026.json")
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
        engine,
        data,
        "uk-two-child-absline-2026",
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
    pentagon, pentagon_deferred = pentagon_results(db)

    all_results = reckoner + free_joins + measures + uprating + pentagon
    stats["results"] = {
        "uk_reckoner": len(reckoner),
        "uk_free_joins": len(free_joins),
        "uk_obr_measures": len(measures),
        "uk_uprating": len(uprating),
        "two_child_pentagon": len(pentagon),
        "total": len(all_results),
    }
    stats["skipped"] = reckoner_skips + uprating_skips
    stats["pentagon_exhibit_rows_superseded"] = pentagon_deferred

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

    diagnoses = cpsp_diagnoses(db)
    for cid, cls, rationale, link in diagnoses:
        db.diagnose(cid, cls, rationale, link)
    stats["diagnoses"] = len(diagnoses)

    exhibits = two_child_exhibits()
    with db.conn:
        db.conn.execute("DELETE FROM pe_exhibits WHERE exhibit='uk-two-child-limit'")
    stats["exhibits"] = db.add_exhibits(exhibits)

    stats["baselines_registered"] = register_baselines(db)

    joined_lanes = (
        "hmrc-personal-tax",
        "obr-measures",
        "obr-welfare",
        "dwp-takeup",
        "rf-outlook",
        "ukmod-stats",
    )
    for lane in joined_lanes:
        row = db.conn.execute(
            "SELECT detail FROM lanes WHERE lane=?", (lane,)
        ).fetchone()
        if row is None:
            raise ValueError(f"campaign-uk: lane {lane} missing")
        db.set_lane(lane, "computed", row["detail"], COMPUTED_AT[:10])
    db.set_lane(
        "campaign-uk-2026-08-02",
        "computed",
        f"{len(all_results)} UK PE results joined "
        f"({stats['results']}); {stats['exhibits']} two-child exhibits vs "
        "registered pre_ab2025 baseline; "
        f"{stats['diagnoses']} CPSP register diagnoses; skips: "
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
