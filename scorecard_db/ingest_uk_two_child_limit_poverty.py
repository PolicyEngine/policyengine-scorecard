"""Ingest the two-child limit poverty benchmarks and their PolicyEngine
counterparts on the certified Microcosm pair (lane uk-two-child-limit-poverty).

The comparison PolicyEngine published on policyengine-uk's docs page
(docs/book/validation/child-poverty-tcl.md, corrected by
PolicyEngine/policyengine-uk#1724) lives here instead, recomputed and
concept-annotated. Three publishers:

    sources/dwp-two-child-limit-poverty   DWP's Budget 2025 note: Tables 1-4
        (relative and absolute low income, AHC and BHC, children,
        working-age adults and individuals, FYE 2027-FYE 2031), the FYE 2026
        figure and children in gaining households. This lane mints these
        123 claims (registry uk_two_child_limit_poverty).
    sources/rf-no-half-measures           Resolution Foundation, 30 October
        2025: 480,000 and £3.5 billion in 2029-30, 330,000 "today", the
        further 150,000, a three-child limit. These are claims of the
        Autumn Budget 2025 harvest (registry uk_ab2025); the adapter's rows
        are matched to them one for one and this lane only attaches results.
    HM Treasury's Budget 2025 policy costings  the static and post-
        behavioural Exchequer impact, 2025-26 to 2030-31, also uk_ab2025
        claims; this lane attaches results to them.

Inputs: data/externals/<source>.json (the adapters' QC'd rows), the two
sources' annotations.json, results/uk/two_child_limit_poverty/
construction_annotations.json, the certified-pair artifact
results/uk/two_child_limit_poverty/<pair_id>.json
(pipeline/compute_uk_two_child_limit_poverty.py certified, on PAIR_ID, a
certified pair in data/uk/certified_pairs.json) and its
diagnostics/ (the September-to-October decomposition, recorded as notes).

Counterparts, oriented to each claim's own sign rule:

    DWP Tables 1-4     current law minus the with-limit world, the group's
                       count below the line (a number) or its rate change
                       (percentage points); relative rows on each world's
                       own median, absolute rows on the constructed FYE 2011
                       line
    DWP FYE 2026       current law minus the 2025-26 removal (positive =
                       fewer children in poverty, as worded)
    DWP gainers        dependent children in households whose HBAI income
                       rises, FYE 2030
    DWP deep material  pe_gap (no material-deprivation variable)
    RF scrap / today   with-limit minus current law (2029-30); current law
                       minus the 2025-26 removal (2025-26)
    RF further         the difference of those two
    RF three-child     with-limit minus the three-child world
    RF cost            change in gov_spending less change in gov_tax
    HMT costings       change in gov_tax less change in gov_spending

Each result's status comes from exactly one status-setting annotation,
matched on facets computed per result (FACETS), including ``spread``: where
a source leaves a convention unstated (the median a policy scenario's
relative line uses; a gainer's threshold) PolicyEngine computes both
readings, and the result is ``comparable`` only while they differ by no
more than half the source's rounding unit.

calibration_relationship: held out (poverty metrics are permanent holdouts;
reform estimates are never targets).

    PYTHONPATH=. python -m scorecard_db.ingest_uk_two_child_limit_poverty data/scorecard.db
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields, with_baseline_condition
from .ingest_uk_childcare_100k import run_records
from .models import (
    BASELINE,
    STANDARD_CONDITIONS,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    TimeBasis,
    UnitConcept,
    baseline_key,
)
from .relationships import uk_relationship

EXTERNALS = REPO / "data" / "externals"
DWP_DIR = REPO / "sources" / "dwp-two-child-limit-poverty"
RF_DIR = REPO / "sources" / "rf-no-half-measures"
RESULTS_DIR = REPO / "results" / "uk" / "two_child_limit_poverty"
# policyengine.py 6.11.0's certified bundle (data/uk/certified_pairs.json);
# pipeline/compute_uk_two_child_limit_poverty.DEFAULT_PAIR (a test checks).
PAIR_ID = (
    "pair-pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71"
)
OWNED = REPO / "data" / "uk" / "two_child_limit_poverty" / "owned_claims.json"
HISTORY = RESULTS_DIR / "history_ab2025_campaign_20260925.jsonl"
HISTORY_RUN = "campaign-20260925-uk-ab2025"

LANE_ID = "uk-two-child-limit-poverty"
LANE_UPDATED = "2026-10-23"
# The UK family's shared top-level feed literal (sync_lane_feed's contract).
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "DWP + Resolution Foundation + HM Treasury",
    "area": "Two-child limit: child poverty and cost (relative and absolute low income)",
    "mode": 2,
    "country": "UK",
}
REGISTRY_MARK = "uk_two_child_limit_poverty"
AB2025_REGISTRY = "uk_ab2025"
MEASURE = "ab2025__uc_child_element_remove_two_child_limit"
PRE_AB2025 = {"policy": "pre_ab2025"}
EXECUTED_WITH_LIMIT = baseline_key(PRE_AB2025)
EXECUTED_CURRENT_LAW = BASELINE.baseline_key()
UC_VARIABLES = ["universal_credit"]

DWP_PUBLICATIONS = {
    "budget_2025_note": {
        "title": "Removing the two-child limit on Universal Credit: Impact on low income poverty levels in the United Kingdom",
        "publisher": "Department for Work and Pensions",
        "url": "https://www.gov.uk/government/publications/poverty-impacts-of-social-security-changes-at-budget-2025/removing-the-two-child-limit-on-universal-credit-impact-on-low-income-poverty-levels-in-the-united-kingdom",
        "date": "2025-11-26",
        "vintage": "as published 26 November 2025, corrected 27 November 2025 (fetched 2026-10-23)",
    },
    "child_poverty_strategy_note": {
        "title": "Child Poverty Strategy: Impact on low income poverty levels and children gaining in the UK: December 2025",
        "publisher": "Department for Work and Pensions",
        "url": "https://www.gov.uk/government/publications/child-poverty-strategy-impact-on-low-income-poverty-levels-and-children-gaining-in-the-uk-december-2025/child-poverty-strategy-impact-on-low-income-poverty-levels-and-children-gaining-in-the-uk-december-2025",
        "date": "2025-12-05",
        "vintage": "as published 5 December 2025 (fetched 2026-10-23)",
    },
}
DWP_SIGN_TABLES = (
    "as published: 'Change in ... compared to baseline'; negative = reduction "
    "in the number in low income"
)
DWP_SIGN_TEXT = "as worded: 'fewer children in poverty' (positive = fewer)"
GROUPS = {
    # DWP group -> (unit concept, subgroup condition, artifact group)
    "children": (UnitConcept.CHILDREN, "children", "children"),
    "working_age_adults": (
        UnitConcept.PERSONS,
        "working_age_adults",
        "working_age_adults",
    ),
    "individuals": (UnitConcept.PERSONS, "individuals", "people"),
    "children_in_deep_material_poverty": (
        UnitConcept.CHILDREN,
        "children_in_deep_material_poverty",
        None,
    ),
}
LINES = {"relative": "relative_moving", "absolute": "absolute_fye2011"}
# half the source's rounding unit, by (source, metric)
HALF_ROUNDING = {
    ("dwp", "poverty_count_change"): 25_000,
    ("dwp", "poverty_rate_change"): 0.05,
    ("dwp", "gainer_count"): 50_000,
    ("resolution_foundation", "poverty_count_change"): 5_000,
}
FACETS = frozenset(
    {
        "sources",
        "measures",
        "metrics",
        "lines",
        "bases",
        "groups",
        "periods",
        "tables",
        "items",
        "scoring",
        "spread",
        "results",
    }
)
_DWP_FIELDS = frozenset(
    {
        "source",
        "country",
        "republished_as",
        "publication",
        "table",
        "metric",
        "group",
        "poverty_line",
        "housing_costs",
        "fye",
        "fy",
        "period",
        "value",
        "value_verbatim",
        "rounding",
        "status",
        "source_column",
    }
)
_RF_FIELDS = frozenset(
    {
        "source",
        "country",
        "measure_key",
        "metric",
        "fy",
        "period",
        "value",
        "value_verbatim",
        "page",
        "unit_concept",
        "status",
        "source_column",
    }
)
# RF row (measure_key, metric, fy, value) -> item
RF_ITEMS = {
    (
        "ab2025_option__scrap_two_child_limit",
        "poverty_count_change",
        "2029-30",
        480_000,
    ): "scrap_2029_30",
    (
        "ab2025_option__scrap_two_child_limit",
        "benefit_cost_change",
        "2029-30",
        3_500_000_000,
    ): "scrap_cost_2029_30",
    (
        "ab2025_option__scrap_two_child_limit",
        "poverty_count_change",
        "2025-26",
        330_000,
    ): "scrap_today",
    (
        "ab2025_option__scrap_two_child_limit",
        "poverty_count_change",
        "2029-30",
        150_000,
    ): "scrap_further_by_2029_30",
    (
        "ab2025_option__three_child_limit",
        "poverty_count_change",
        "2029-30",
        350_000,
    ): "three_child_limit",
}
RF_UNATTACHED = {
    "ab2025_option__two_child_limit_partial_child_element_for_third_plus_children": (
        "a reduced child element for third and later children needs a per-rank "
        "amount the engine's element formula does not have (registry: partial)"
    ),
    "ab2025_option__two_child_limit_exempt_working_families": (
        "an in-work exemption from the limit is a formula construction, not a "
        "parameter (registry: partial)"
    ),
}


# --- staging -------------------------------------------------------------------


def _load(name: str, known: frozenset) -> list[dict]:
    path = EXTERNALS / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run python sources/{name}/adapter.py"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, known, name)
        if row["source"] != name or row["country"] != "UK":
            raise ValueError(f"{name}: unexpected row identity {row}")
    return rows


def _check_conditions(cond: dict) -> dict:
    unknown = set(cond) - STANDARD_CONDITIONS
    if unknown:
        raise ValueError(f"conditions outside STANDARD_CONDITIONS: {sorted(unknown)}")
    return cond


def _dwp_claim(row: dict) -> ExternalScore:
    metric = Metric(row["metric"])
    unit, subgroup, _ = GROUPS[row["group"]]
    if metric == Metric.POVERTY_RATE_CHANGE:
        unit = UnitConcept.PERCENTAGE_POINTS
    reform = policy_ref(MEASURE, baseline=PRE_AB2025)
    cond = {
        "country": "UK",
        "geography": "UK",
        "fy": row["fy"],
        "measure_key": MEASURE,
        "fiscal_event": "autumn_budget_2025",
        "benchmark_class": "different_model",
        "pe_expressibility": "expressible",
        "subgroup": subgroup,
        "scoring_method": "static",
        "value_verbatim": row["value_verbatim"],
    }
    if row["poverty_line"] is not None:
        cond["poverty_line"] = row["poverty_line"]
        cond["housing_costs"] = row["housing_costs"]
        if row["poverty_line"] == "absolute":
            cond["poverty_line_anchor"] = "fye_2011"
    if metric in (Metric.POVERTY_COUNT_CHANGE, Metric.POVERTY_RATE_CHANGE):
        cond["sign_convention"] = DWP_SIGN_TEXT if row["value"] > 0 else DWP_SIGN_TABLES
    if metric == Metric.GAINER_COUNT:
        cond["statistic"] = "children living in households whose income increases"
    if row["group"] == "children_in_deep_material_poverty":
        cond["pe_missing"] = (
            "deep material poverty: policyengine-uk has no material-deprivation variable"
        )
    if row["republished_as"]:
        cond["note"] = f"republished differently: {row['republished_as']}"
    relationship, _ = uk_relationship("dwp", metric)
    pub = DWP_PUBLICATIONS[row["publication"]]
    return ExternalScore(
        source="dwp",
        source_model="dwp_policy_simulation_model",
        metric=metric,
        unit_concept=unit,
        period=int(row["period"]),
        time_basis=TimeBasis.FISCAL_YEAR,
        value=float(row["value"]),
        conditions=_check_conditions(with_baseline_condition(cond, reform)),
        reform=reform,
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication={
            **pub,
            "table": row["table"],
            "rounding": row["rounding"],
            "registry": REGISTRY_MARK,
            "publish_without_result": True,
        },
        value_kind="percent" if metric == Metric.POVERTY_RATE_CHANGE else "count",
        status=row["status"],
    )


def stage_dwp() -> tuple[list[ExternalScore], dict[str, dict]]:
    """(claims, {claim_id: the adapter row})."""
    scores, rows = [], {}
    for row in _load("dwp-two-child-limit-poverty", _DWP_FIELDS):
        s = _dwp_claim(row)
        scores.append(s)
        rows[s.claim_id()] = row
    return finish(scores, LANE_ID), rows


def rf_targets(db: ScorecardDB) -> tuple[dict[str, dict], list[str]]:
    """Each RF adapter row matched to exactly one uk_ab2025 claim:
    ({claim_id: {"row", "item"}}, notes on the rows not attached)."""
    out, unattached = {}, []
    for row in _load("rf-no-half-measures", _RF_FIELDS):
        hits = db.conn.execute(
            "SELECT claim_id, value FROM external_scores"
            " WHERE source = 'resolution_foundation'"
            " AND json_extract(publication, '$.registry') = ?"
            " AND json_extract(conditions, '$.measure_key') = ?"
            " AND metric = ? AND period = ? AND value = ?"
            " AND json_extract(publication, '$.url') LIKE '%No-half-measures%'",
            (
                AB2025_REGISTRY,
                row["measure_key"],
                row["metric"],
                row["period"],
                row["value"],
            ),
        ).fetchall()
        if len(hits) != 1:
            raise ValueError(
                f"RF row {row['measure_key']} {row['metric']} {row['fy']} "
                f"{row['value']:g}: {len(hits)} uk_ab2025 claims, want 1"
            )
        key = (row["measure_key"], row["metric"], row["fy"], int(row["value"]))
        if key in RF_ITEMS:
            out[hits[0]["claim_id"]] = {"row": row, "item": RF_ITEMS[key]}
        elif row["measure_key"] in RF_UNATTACHED:
            unattached.append(
                f"{row['measure_key']}: {RF_UNATTACHED[row['measure_key']]}"
            )
        else:
            raise ValueError(f"RF row {key} has no decided attachment")
    return out, unattached


def hmt_targets(db: ScorecardDB) -> list[dict]:
    """The HM Treasury costing claims for the measure, both legs, every year."""
    rows = db.conn.execute(
        "SELECT claim_id, period, value, conditions FROM external_scores"
        " WHERE source = 'hm_treasury' AND metric = 'revenue_change'"
        " AND json_extract(publication, '$.registry') = ?"
        " AND json_extract(publication, '$.family') = 'uk_hmt_costings'"
        " AND json_extract(conditions, '$.measure_key') = ?",
        (AB2025_REGISTRY, MEASURE),
    ).fetchall()
    out = []
    for r in rows:
        cond = json.loads(r["conditions"])
        out.append(
            {
                "claim_id": r["claim_id"],
                "period": r["period"],
                "value": r["value"],
                "scoring": cond["scoring_method"],
                "sign_convention": cond["sign_convention"],
            }
        )
    return sorted(out, key=lambda x: (x["period"], x["scoring"]))


# --- the artifact --------------------------------------------------------------


def check_artifact(art: dict, path: Path, pair: dict) -> None:
    """The artifact ran on exactly its pair's certified pairing: the wheels
    and packaged manifest the preflight verified, the runtime release
    bundle, the dataset each world read and its years (the checks
    ingest_uk_childcare_100k.check_artifact makes for that lane)."""
    identity = pair["identity"]
    dataset = identity["dataset"]
    got = {
        "pair_id": (art["pair_id"], path.stem),
        "variant_identity_sha256": art["variant_identity_sha256"],
        "packages": art["packages"],
        "packaged_bundle_manifest_sha256": art["packaged_bundle_manifest_sha256"],
        "release_bundle": art["release_bundle"],
        "dataset": (art["dataset"]["revision"], art["dataset"]["sha256"]),
        "data_years": art["data_years"],
        "python": art["python"].split(".")[:2],
    }
    want = {
        "pair_id": (pair["variant_id"], pair["variant_id"]),
        "variant_identity_sha256": pair["identity_sha256"],
        "packages": {
            name: {f: pkg[f] for f in ("version", "record_sha256")}
            for name, pkg in identity["packages"].items()
        },
        "packaged_bundle_manifest_sha256": identity["packaged_bundle_manifest_sha256"],
        "release_bundle": identity["release_bundle"],
        "dataset": (dataset["revision"], dataset["sha256"]),
        "data_years": pair["data_years"],
        "python": identity["python"].split("."),
    }
    wrong = sorted(k for k in want if got[k] != want[k])
    if wrong:
        raise ValueError(f"{path.name}: not {pair['variant_id']}'s pairing: {wrong}")
    if art["dataset_sha256"] != dataset["sha256"]:
        raise ValueError(f"{path.name}: dataset digest is not the certified one")
    for name, world in art["worlds"].items():
        if not (
            world["dataset_sha256_before"]
            == world["dataset_sha256_after"]
            == dataset["sha256"]
        ):
            raise ValueError(f"{path.name} {name}: dataset digest changed")
        if world["dataset_years"] != pair["data_years"]:
            raise ValueError(f"{path.name} {name}: dataset years are not the pair's")
    if art["behavioural_response"] != "none (static)":
        raise ValueError(f"{path.name}: artifact is not a static run")


def load_artifact() -> tuple[dict, Path]:
    pair = run_records().get(PAIR_ID)
    if pair is None:
        raise ValueError(f"{PAIR_ID} is not a certified pair in certified_pairs.json")
    path = RESULTS_DIR / f"{PAIR_ID}.json"
    art = json.loads(path.read_text())
    check_artifact(art, path, pair)
    return art, path


def _y(art: dict, world: str, year: int) -> dict:
    return art["worlds"][world]["years"][str(year)]


def _below(art, world, year, basis, line, group) -> float:
    return _y(art, world, year)["below"][basis][line][group]


def _pop(art, world, year, group) -> float:
    return _y(art, world, year)["population"][group]


def _rate(art, world, year, basis, line, group) -> float:
    return (
        100.0
        * _below(art, world, year, basis, line, group)
        / _pop(art, world, year, group)
    )


def _effect(art, a, b, year_a, year_b, basis, line, group, metric) -> float:
    """world a minus world b (counts, or rate change in percentage points)."""
    if metric == "poverty_rate_change":
        return _rate(art, a, year_a, basis, line, group) - _rate(
            art, b, year_b, basis, line, group
        )
    return _below(art, a, year_a, basis, line, group) - _below(
        art, b, year_b, basis, line, group
    )


def _exchequer(art: dict, year: int) -> float:
    """current law minus with-limit, gov_tax less gov_spending (negative = cost)."""
    cl, wl = (
        _y(art, "current_law", year)["sums_gbp"],
        _y(art, "with_limit", year)["sums_gbp"],
    )
    return (cl["gov_tax"] - wl["gov_tax"]) - (cl["gov_spending"] - wl["gov_spending"])


def _uc_change(art: dict, year: int) -> float:
    return (
        _y(art, "current_law", year)["sums_gbp"]["universal_credit"]
        - _y(art, "with_limit", year)["sums_gbp"]["universal_credit"]
    )


def _k(x: float) -> str:
    return f"{x / 1e3:,.0f}k"


def _bn(x: float) -> str:
    return f"£{x / 1e9:.3f}bn"


# --- annotations ---------------------------------------------------------------


def _spec(path: Path) -> list[dict]:
    spec = json.loads(path.read_text())
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
        unknown = set(a["applies_to"]) - FACETS
        if unknown:
            raise ValueError(f"annotation {a['id']}: unknown facets {sorted(unknown)}")
    return spec["annotations"]


def annotation_specs() -> list[dict]:
    return [
        *_spec(DWP_DIR / "annotations.json"),
        *_spec(RF_DIR / "annotations.json"),
        *_spec(RESULTS_DIR / "construction_annotations.json"),
    ]


def match_annotations(
    facets: dict, spec: list[dict]
) -> tuple[list[str], ComparisonStatus]:
    texts, statuses = [], []
    for a in spec:
        if any(
            v is not None and facets.get(k) not in v for k, v in a["applies_to"].items()
        ):
            continue
        texts.append(a["text"])
        if "status" in a:
            statuses.append((a["id"], a["status"]))
    if len(statuses) != 1:
        raise ValueError(
            f"{facets}: status-setting annotations {statuses} (want exactly one)"
        )
    return texts, ComparisonStatus(statuses[0][1])


def _spread(source: str, metric: str, a: float, b: float) -> str:
    half = HALF_ROUNDING[(source, metric)]
    return "within_rounding" if abs(a - b) <= half else "beyond_rounding"


# --- results -------------------------------------------------------------------


def _result(
    art, path, claim_id, value, facets, spec, construction, notes, executed, variables
):
    texts, status = match_annotations({**facets, "results": "certified"}, spec)
    return PEResult(
        claim_id=claim_id,
        computed_value=value,
        status=status,
        engine_version=art["installed"]["policyengine-uk"],
        data_bundle=art["dataset"]["revision"],
        pe_construction=f"{construction}; artifact {path.relative_to(REPO)}",
        run_id=art["run_id"],
        computed_at=art["computed_at"],
        annotations=[*texts, *notes],
        baseline_key=executed,
        policyengine_variables=variables,
    )


def dwp_results(art, path, scores, rows, spec, history) -> list[PEResult]:
    out = []
    for s in scores:
        row = rows[s.claim_id()]
        group = row["group"]
        _, _, art_group = GROUPS[group]
        metric = row["metric"]
        facets = {
            "sources": "dwp",
            "measures": MEASURE,
            "metrics": metric,
            "lines": row["poverty_line"] or "none",
            "bases": row["housing_costs"] or "none",
            "groups": group,
            "periods": s.period,
            "tables": row["table"],
            "items": "none",
            "scoring": "static",
        }
        if art_group is None:
            facets["spread"] = "na"
            texts, status = match_annotations({**facets, "results": "certified"}, spec)
            out.append(
                PEResult(
                    claim_id=s.claim_id(),
                    computed_value=None,
                    status=status,
                    engine_version=art["installed"]["policyengine-uk"],
                    data_bundle=art["dataset"]["revision"],
                    pe_construction="no construction: no material-deprivation variable",
                    run_id=art["run_id"],
                    computed_at=art["computed_at"],
                    annotations=texts,
                    baseline_key=EXECUTED_WITH_LIMIT,
                    policyengine_variables=[],
                )
            )
            continue
        year = s.period - 1
        if metric == "gainer_count":
            g = _y(art, "current_law", year)["gainers_vs_with_limit"]
            value = g["hbai_income_over_0"][art_group]
            other = g["hbai_income_over_1_a_week"][art_group]
            facets["spread"] = _spread("dwp", metric, value, other)
            notes = [
                f"Measured: {value / 1e6:.2f}m dependent children in households whose HBAI income rises at all; "
                f"{other / 1e6:.2f}m by more than £1 a week; households gaining {g['hbai_income_over_0']['households'] / 1e6:.2f}m; "
                f"benefit units whose Universal Credit rises {g['benunits_uc_rises'] / 1e6:.2f}m.",
            ]
            falls = g["hbai_income_falls"]
            if falls["households"]:
                notes.append(
                    f"About {falls['households']:,.0f} households are worse off (largest loss "
                    f"£{falls['largest_loss_gbp_year']:,.0f} a year). In each, a Universal Credit "
                    "award begins and the household's Tax-Free Childcare ends: the model makes a UC "
                    "award disqualify Tax-Free Childcare (gov.hmrc.tax_free_childcare."
                    "disqualifying_benefits), and whether a family claims UC is a data input "
                    "(would_claim_uc), so the model does not weigh the childcare it gives up "
                    "(results/uk/two_child_limit_poverty/diagnostics/losers.json)."
                )
            notes.append("PE oriented to it: a count of children, no sign.")
            out.append(
                _result(
                    art,
                    path,
                    s.claim_id(),
                    value,
                    facets,
                    spec,
                    f"gainers: is_hbai_dependent_child in households whose hbai_household_net_income is higher in current law than in the with-limit world, engine period {year}",
                    notes,
                    EXECUTED_WITH_LIMIT,
                    ["hbai_household_net_income", "is_hbai_dependent_child"],
                )
            )
            continue
        basis = row["housing_costs"]
        line = LINES[row["poverty_line"]]
        if row["period"] == 2026:  # the FYE 2026 text figure: removal in 2025-26
            value = _effect(
                art,
                "current_law",
                "removed_2025",
                year,
                year,
                basis,
                line,
                art_group,
                metric,
            )
            alt = _effect(
                art,
                "current_law",
                "removed_2025",
                year,
                year,
                basis,
                "relative_fixed_at_with_limit",
                art_group,
                metric,
            )
            construction = f"current law minus the 2025-26 removal (removed_2025), {line} {basis}, {art_group}, engine period {year}"
            executed = EXECUTED_CURRENT_LAW
        else:
            value = _effect(
                art,
                "current_law",
                "with_limit",
                year,
                year,
                basis,
                line,
                art_group,
                metric,
            )
            alt = _effect(
                art,
                "current_law",
                "with_limit",
                year,
                year,
                basis,
                "relative_fixed_at_with_limit",
                art_group,
                metric,
            )
            construction = f"current law minus the with-limit world, {line} {basis}, {art_group}, engine period {year}"
            executed = EXECUTED_WITH_LIMIT
        facets["spread"] = (
            _spread("dwp", metric, value, alt)
            if row["poverty_line"] == "relative"
            else "na"
        )
        unit = "pp" if metric == "poverty_rate_change" else ""
        fmt = (lambda x: f"{x:+.2f}pp") if unit else (lambda x: f"{x / 1e3:+,.0f}k")
        notes = [
            f"Measured ({row['fy']}, engine period {year}): {fmt(value)} on each world's own "
            f"{'median' if row['poverty_line'] == 'relative' else 'FYE 2011 line'}; "
            f"{fmt(alt)} with the relative line held at the with-limit world's median.",
        ]
        if row["poverty_line"] == "absolute":
            served = (
                _effect(
                    art,
                    "current_law",
                    "with_limit",
                    year,
                    year,
                    basis,
                    "absolute_served",
                    art_group,
                    metric,
                )
                if row["period"] != 2026
                else _effect(
                    art,
                    "current_law",
                    "removed_2025",
                    year,
                    year,
                    basis,
                    "absolute_served",
                    art_group,
                    metric,
                )
            )
            lines = _y(art, "with_limit", year)["lines_gbp_year"][basis]
            notes.append(
                f"On the absolute line the engine serves (FYE 2025 reference, £{lines['absolute_served']:,.0f} a year "
                f"for a couple without children) the change is {fmt(served)}; the constructed FYE 2011 line is "
                f"£{lines['absolute_fye2011']:,.0f}."
            )
        notes.append(
            f"PE oriented to it: {'positive = fewer, as the text words it' if row['value'] > 0 else 'negative = fewer in low income, as the tables print it'}."
        )
        hist = history.get((art_group, basis, row["poverty_line"], s.period))
        if hist:
            notes.append(hist)
        out.append(
            _result(
                art,
                path,
                s.claim_id(),
                value,
                facets,
                spec,
                construction,
                notes,
                executed,
                [
                    "in_relative_poverty_" + basis
                    if row["poverty_line"] == "relative"
                    else f"equiv_hbai_household_net_income{'_ahc' if basis == 'ahc' else ''}",
                    "is_hbai_dependent_child"
                    if art_group == "children"
                    else (
                        "is_hbai_working_age_adult"
                        if art_group == "working_age_adults"
                        else "household_count_people"
                    ),
                ],
            )
        )
    return out


def rf_results(art, path, targets, spec, history) -> list[PEResult]:
    out = []
    y29, y25 = 2029, 2025
    for claim_id, t in sorted(targets.items(), key=lambda kv: kv[1]["item"]):
        item, row = t["item"], t["row"]
        facets = {
            "sources": "resolution_foundation",
            "measures": row["measure_key"],
            "metrics": row["metric"],
            "lines": "relative" if row["metric"] == "poverty_count_change" else "none",
            "bases": "ahc" if row["metric"] == "poverty_count_change" else "none",
            "groups": "children" if row["metric"] == "poverty_count_change" else "none",
            "periods": row["period"],
            "tables": "none",
            "items": item,
            "scoring": "static",
        }

        def fewer(a, b, ya, yb, line="relative_moving"):
            # world a minus world b children below the AHC line: positive = fewer in b
            return _below(art, a, ya, "ahc", line, "children") - _below(
                art, b, yb, "ahc", line, "children"
            )

        if item == "scrap_cost_2029_30":
            value = -_exchequer(art, y29)
            facets["spread"] = "na"
            notes = [
                f"Measured (2029-30, engine period 2029): Exchequer cost {_bn(value)} "
                f"(change in gov_spending less change in gov_tax); Universal Credit rises {_bn(_uc_change(art, y29))}.",
                "PE oriented to it: positive = cost to the Exchequer.",
            ]
            construction = "current law minus the with-limit world, gov_spending less gov_tax, engine period 2029"
            executed, variables = (
                EXECUTED_WITH_LIMIT,
                ["gov_spending", "gov_tax", "universal_credit"],
            )
        else:
            if item == "scrap_2029_30":
                pair = ("with_limit", "current_law", y29, y29)
                construction = "with-limit world minus current law, children below 60% of each world's own AHC median, engine period 2029"
                executed = EXECUTED_WITH_LIMIT
            elif item == "scrap_today":
                pair = ("current_law", "removed_2025", y25, y25)
                construction = "current law minus the 2025-26 removal, children below 60% of each world's own AHC median, engine period 2025"
                executed = EXECUTED_CURRENT_LAW
            elif item == "three_child_limit":
                pair = ("with_limit", "three_child_limit", y29, y29)
                construction = "with-limit world (2 children) minus the three-child world, children below 60% of each world's own AHC median, engine period 2029"
                executed = EXECUTED_WITH_LIMIT
            if item == "scrap_further_by_2029_30":
                value = fewer("with_limit", "current_law", y29, y29) - fewer(
                    "current_law", "removed_2025", y25, y25
                )
                alt = fewer(
                    "with_limit",
                    "current_law",
                    y29,
                    y29,
                    "relative_fixed_at_with_limit",
                ) - fewer(
                    "current_law",
                    "removed_2025",
                    y25,
                    y25,
                    "relative_fixed_at_with_limit",
                )
                construction = "(with-limit minus current law, 2029) minus (current law minus the 2025-26 removal, 2025), children below 60% of each world's own AHC median"
                executed = EXECUTED_WITH_LIMIT
            else:
                value = fewer(*pair)
                alt = fewer(*pair, line="relative_fixed_at_with_limit")
            facets["spread"] = _spread(
                "resolution_foundation", "poverty_count_change", value, alt
            )
            notes = [
                f"Measured: {_k(value)} fewer children on each world's own median; {_k(alt)} with the line held at the with-limit world's median.",
                "PE oriented to it: positive = fewer children in poverty.",
            ]
            hist = (
                history.get(("children", "ahc", "relative", row["period"]))
                if item == "scrap_2029_30"
                else None
            )
            if hist:
                notes.append(hist)
            variables = ["in_relative_poverty_ahc", "is_hbai_dependent_child"]
        out.append(
            _result(
                art,
                path,
                claim_id,
                value,
                facets,
                spec,
                construction,
                notes,
                executed,
                variables,
            )
        )
    return out


def hmt_results(art, path, targets, spec) -> list[PEResult]:
    out = []
    for t in targets:
        year = t["period"] - 1
        value = _exchequer(art, year)
        facets = {
            "sources": "hm_treasury",
            "measures": MEASURE,
            "metrics": "revenue_change",
            "lines": "none",
            "bases": "none",
            "groups": "none",
            "periods": t["period"],
            "tables": "none",
            "items": "none",
            "scoring": t["scoring"],
            "spread": "na",
        }
        notes = [
            f"Measured (engine period {year}): Exchequer effect {_bn(value)} (change in gov_tax less change in gov_spending); "
            f"Universal Credit changes by {_bn(_uc_change(art, year))}.",
            "claim sign: positive = yield to the Exchequer, PE's own orientation",
        ]
        out.append(
            _result(
                art,
                path,
                t["claim_id"],
                value,
                facets,
                spec,
                f"static: current law minus the with-limit world, gov_tax less gov_spending, engine period {year}",
                notes,
                EXECUTED_WITH_LIMIT,
                ["gov_tax", "gov_spending", "universal_credit"],
            )
        )
    return out


def check_ownership(rf: dict, hmt: list[dict]) -> None:
    """The claims this lane answers on the uk_ab2025 registry are exactly the
    committed owned list, which pipeline/stage_uk_ab2025 reads so it never
    answers them too (one claim, one computed answer)."""
    owned = set(json.loads(OWNED.read_text())["claims"])
    derived = set(rf) | {t["claim_id"] for t in hmt}
    if owned != derived:
        raise ValueError(
            f"owned_claims.json drifted from the lane's targets: "
            f"only listed {sorted(owned - derived)}, only derived {sorted(derived - owned)}"
        )


def history_results() -> list[PEResult]:
    """The answers these claims carried from the 25 September 2026 AB2025
    campaign when this lane took them over, kept as their earlier history:
    each row as campaign_uk_ab2025 staged it, under this lane's history run
    id so the AB2025 run's own count stays its own."""
    owned = json.loads(OWNED.read_text())["claims"]
    out = []
    for line in HISTORY.read_text().splitlines():
        row = json.loads(line)
        claim_id = row["external_claim_match"]["claim_id"]
        if claim_id not in owned or row["run_id"] != HISTORY_RUN:
            raise ValueError(f"history row {claim_id} is not an owned campaign row")
        out.append(
            PEResult(
                claim_id=claim_id,
                computed_value=row["pe_value"],
                status=row["status"],
                engine_version=row["engine_version"],
                data_bundle=row["data_bundle"],
                pe_construction=row["pe_construction"],
                run_id=f"{LANE_ID}-history:{HISTORY_RUN}",
                computed_at=row["computed_at"],
                annotations=[
                    *row["annotations"],
                    f"History: the {HISTORY_RUN} answer (Populace UK 2023, policyengine-uk "
                    f"{row['engine_version']}) this claim carried when lane {LANE_ID} took it over "
                    "on 2026-10-23; the certified Microcosm pair's answer is the later entry.",
                ],
                baseline_key=row["baseline_key"],
                policyengine_variables=row.get("policyengine_variables", []),
            )
        )
    return out


# --- the September-to-October decomposition -------------------------------------


def decomposition_history() -> dict:
    """{(group, basis, line, period): note} from the diagnostics, for the
    rows the decomposition explains (children, relative, FYE 2030)."""
    path = RESULTS_DIR / "DECOMPOSITION.json"
    if not path.exists():
        return {}
    d = json.loads(path.read_text())
    out = {}
    for basis, note in d["notes"].items():
        out[("children", basis, "relative", 2030)] = note
    return out


# --- accounting and ingest -----------------------------------------------------

_EXPECTED = {
    "claims": 123,
    "results": 123 + 5 + 12 + 13,
    "results_by_source": {
        "dwp": 123,
        "resolution_foundation": 5,
        "hm_treasury": 12,
        "history": 13,
    },
}


def accounting(scores, pe_by_source) -> dict:
    return {
        "claims": len(scores),
        "results": sum(len(v) for v in pe_by_source.values()),
        "results_by_source": {k: len(v) for k, v in pe_by_source.items()},
    }


def ingest(db_path: Path) -> dict:
    scores, rows = stage_dwp()
    art, art_path = load_artifact()
    spec = annotation_specs()
    history = decomposition_history()
    db = ScorecardDB(db_path)
    rf, unattached = rf_targets(db)
    hmt = hmt_targets(db)
    check_ownership(rf, hmt)
    pe = {
        "dwp": dwp_results(art, art_path, scores, rows, spec, history),
        "resolution_foundation": rf_results(art, art_path, rf, spec, history),
        "hm_treasury": hmt_results(art, art_path, hmt, spec),
        "history": history_results(),
    }
    counts = accounting(scores, pe)
    if counts != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {counts} != {_EXPECTED}")
    statuses = Counter(r.status.value for v in pe.values() for r in v)
    counts["statuses"] = dict(sorted(statuses.items()))
    counts["rf_unattached"] = unattached

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        old = [
            r[0]
            for r in db.conn.execute(
                "SELECT claim_id FROM external_scores"
                " WHERE json_extract(publication, '$.registry') = ?",
                (REGISTRY_MARK,),
            )
        ]
        for table in ("diagnoses", "pe_results", "external_scores"):
            db.conn.executemany(
                f"DELETE FROM {table} WHERE claim_id = ?", [(c,) for c in old]
            )
        for run_id in (art["run_id"], f"{LANE_ID}-history:{HISTORY_RUN}"):
            db.conn.execute("DELETE FROM pe_results WHERE run_id = ?", (run_id,))
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(
            RESULTS_SQL, [ScorecardDB.result_row(r) for v in pe.values() for r in v]
        )
        register_baselines_txn(db)
        detail = (
            f"{len(scores)} DWP claims (Tables 1-4, FYE 2026, gainers) plus "
            f"{len(pe['resolution_foundation'])} Resolution Foundation and "
            f"{len(pe['hm_treasury'])} HM Treasury AB2025 claims computed on the certified "
            f"Microcosm pair ({art['dataset']['revision']}, policyengine-uk "
            f"{art['installed']['policyengine-uk']}); statuses {counts['statuses']}"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db, REPO / "data" / "lanes.json", FEED_UPDATED, lanes={LANE_ID: LANE_FEED_META}
    )
    db.close()
    return counts


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
