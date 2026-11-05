"""Ingest every Autumn Budget 2026 score (#230).

The harvest at ``sources/harvest-uk-ab2026-2026-10-29/`` stages 5,952 rows
from 12 families: HM Treasury's tables, costings and red book, the OBR's
October 2026 EFO and policy workbook, Resolution Foundation, IFS, Tax Policy
Associates, CenTax, IPPR, the devolved governments, Trussell and four smaller
producers. This module turns each row into a claim or a tallied drop with a
written reason, and ``check_accounting`` pins ``read = ingested + dropped``
per family against ``ingest_uk_ab2026_expected.json``.

We model it on ``ingest_uk_ab2025`` and keep its behaviour, reusing its
helpers where the two agree:

- the order of drops: restated rows first (#86), then categorical ratings,
  specimen households, the dropped metric and unit names, and only then a
  metric disposition, so a restated figure can't land on a registered metric;
- every AB2025 metric disposition, drop reason and unit, every condition it
  copies or canonicalises, its engine checks (``_source_model``), its
  registered worlds (#13), the macro verdict on macro-fiscal metrics (#55),
  ``publish_without_result`` on every UK row, the merge of one
  producer's twin printings, and the claim-id uniqueness gate;
- the pe_gap verdict rows (``ingest_verdicts``), stated against the engine
  the registry pins.

AB2026 differs in six ways:

1. **Keys.** We stage each row under an AB2026 key, or for a Table 6.4 recosting
   under the earlier event's key named in ``conditions.recosting_of``. A recosting
   takes no registry verdict: AB2025's registry states its verdicts at
   policyengine-uk 2.89.2, and AB2026's counterparts run at 2.151.0, so
   this module writes no verdict for a recosting.
2. **Dispositions.** ``DISPOSITIONS_AB2026`` and ``DROP_BY_NAME_AB2026``
   decide the 66 metric names AB2025's tables don't hold (2 adoptions and
   64 drops). Table 6.2's ``financial_transaction_cash_impact`` lands on
   ``cash_requirement_change``, the PSNCR metric ``models.py`` keeps apart
   from PSNB.
3. **Shares of GDP.** A ``percent`` row with a GDP denominator (IFS's) takes
   the OBR's and TPA's ``percent_of_gdp``, which AB2025 drops as macro-fiscal.
4. **HM Treasury figures staged twice.** The costings print each Table 6.1
   line's exchequer impact, and red book Table 6.3 and its prose repeat some
   Table 6.1 cells. We keep the Table 6.1 or 6.2 claim, record the twin under
   ``publication.also_printed_in``, and tally the twin.
5. **Row calls.** ``ROW_METRICS`` moves one row to another metric, and
   ``ROW_DROPS`` tallies 22 rows under six reasons. Each entry names the row
   and the staged value it expects.
6. **Lanes.** Three lanes: official, microsimulation, and administrative data
   and other producers. ``advance_lanes`` moves a lane to ``computed`` once
   its claims have counterparts, which ``pipeline/stage_uk_ab2026.py``
   stages from the dashboard's Budget-day artifacts (tranche 3) under
   ``STAGED_COUNTERPARTS``.

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_uk_ab2026 data/scorecard.db
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from . import ingest_uk_ab2025 as AB25
from .db import DIAGNOSES_SQL, LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, merge_republications, with_baseline_condition
from .models import (
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
)
from .relationships import uk_relationship
from .uk_aliases import canon, known

HARVEST = REPO / "sources" / "harvest-uk-ab2026-2026-10-29"
REGISTRY_PATH = REPO / "data" / "uk" / "ab2026_measures.json"

REGISTRY_MARK = "uk_ab2026"
# The counterparts pipeline/stage_uk_ab2026.py stages, which
# ingest_campaign attaches claim_id-direct (tranche 3).
STAGED_COUNTERPARTS = REPO / "results" / "uk" / "staged_ab2026"
FISCAL_EVENT = "autumn_budget_2026"
# The UK family's shared top-level feed literal (sync_lane_feed's contract:
# every caller in a build passes the same one).
FEED_UPDATED = AB25.FEED_UPDATED
LANE_UPDATED = "2026-11-05"
VERDICT_RUN_ID = "ab2026-verdicts-2026-11-05"
VERDICT_COMPUTED_AT = "2026-11-05T00:00:00+00:00"

LANES = {
    "uk-ab2026-official": {
        "source": "HM Treasury and the OBR (Autumn Budget 2026)",
        "area": "Tables 6.1, 6.2 and 6.4, the policy costings, the Budget document and the October 2026 EFO",
        "mode": 2,
        "country": "UK",
    },
    "uk-ab2026-microsim": {
        "source": "Resolution Foundation, IFS and IPPR (Autumn Budget 2026)",
        "area": "independent microsimulation of the Budget's measures and options",
        "mode": 2,
        "country": "UK",
    },
    "uk-ab2026-admin-other": {
        "source": "CenTax, TPA, the devolved governments, Trussell and smaller producers (Autumn Budget 2026)",
        "area": "administrative-data and own-computation scores of the Budget's measures",
        "mode": 2,
        "country": "UK",
    },
}

# harvest family dir -> (lane, allowed source slugs)
FAMILIES: dict[str, tuple[str, frozenset[str]]] = {
    # uk_hmt_tables first: its Table 6.1 and 6.2 claims are the ones the
    # costings' and red book's twins attach to
    "uk_hmt_tables": ("uk-ab2026-official", frozenset({"hm_treasury"})),
    "uk_hmt_costings": ("uk-ab2026-official", frozenset({"hm_treasury"})),
    "uk_hmt_redbook": ("uk-ab2026-official", frozenset({"hm_treasury"})),
    "uk_obr_tables": ("uk-ab2026-official", frozenset({"obr_efo"})),
    "uk_rf_ab2026": ("uk-ab2026-microsim", frozenset({"resolution_foundation"})),
    "uk_ifs_ab2026": ("uk-ab2026-microsim", frozenset({"ifs"})),
    "uk_ippr": ("uk-ab2026-microsim", frozenset({"ippr"})),
    "uk_centax": ("uk-ab2026-admin-other", frozenset({"centax"})),
    "uk_tpa": ("uk-ab2026-admin-other", frozenset({"tax_policy_associates"})),
    "uk_devolved_govts": (
        "uk-ab2026-admin-other",
        frozenset({"scottish_government", "welsh_government"}),
    ),
    "uk_thinktank_misc": (
        "uk-ab2026-admin-other",
        frozenset(
            {
                "citizens_advice",
                "cps",
                "institute_for_government",
                "learning_and_work_institute",
            }
        ),
    ),
    "uk_trussell_wpi": ("uk-ab2026-admin-other", frozenset({"trussell_wpi"})),
}

CLAIMS_SHA256: dict[str, str] = {
    fam: entry["claims_sha256"]
    for fam, entry in json.loads((HARVEST / "COUNTS.json").read_text()).items()
    if not fam.startswith("_")
}

# --- dispositions ------------------------------------------------------------
# The metric names AB2025's tables don't hold, decided here. Each maps to one
# Metric or one drop reason; an unlisted name raises.
DISPOSITIONS_AB2026: dict[str, Metric] = {
    # Table 6.2 and the costings' financial transactions: a PSNCR effect
    "financial_transaction_cash_impact": Metric.CASH_REQUIREMENT_CHANGE,
    # the red book's 84% of income tax payers the property and savings
    # rates leave unaffected
    "unaffected_share": Metric.SHARE_NO_CHANGE,
}

DROPS_AB2026: dict[str, str] = {
    "hmt_figure_staged_twice": (
        "HM Treasury prints this figure in Table 6.1 or 6.2 and again in its "
        "policy costings or the Budget document, sometimes rounded or with "
        "the opposite sign; we score the Table 6.1 or 6.2 figure and list "
        "this printing with it."
    ),
    "energy_bill_level_no_metric": (
        "The producer gives the level of a typical household's energy bill "
        "under the price cap (RF's £2,210, for example), and we score changes "
        "in bills, so a level has nothing to compare."
    ),
    "partial_year_household_support": (
        "IFS gives the average support per household from the Budget's "
        "energy and fuel measures over the nine months from October 2026 to "
        "June 2027, and we score changes in household income over a full "
        "year, so the two figures cover different periods."
    ),
    "restated_obr_forecast": (
        "Resolution Foundation takes the cost of continuing the fuel duty "
        "freeze from the OBR's forecasts, as the OBR's constant-duty-rate "
        "receipts less its central receipts, so we score the OBR's figure "
        "once rather than as two producers' estimates."
    ),
    "income_path_not_a_policy_effect": (
        "Resolution Foundation gives how typical real household incomes move "
        "over the Parliament, an outturn or forecast path with no reform to "
        "compare against, and we score the change a policy makes to income."
    ),
    "earlier_estimate_restated": (
        "CenTax restates the revenue gain it estimated in 2024 from taxing "
        "capital gains at income tax rates, an estimate of an earlier event "
        "rather than of this Budget."
    ),
    "single_row_unregistered_world": (
        "The OBR scores this figure against a world it describes once, such "
        "as its uprating rules simulated over 1990-2025 outturn or its CPI "
        "bound against the fuel duty policy, and we compare only against "
        "worlds we can rebuild or current law."
    ),
}

M, R, A, S, P, U, N, X, E = (
    "macro_fiscal_or_out_of_scope",
    "ratio_or_derived_quantity",
    "assumption_or_base_not_a_score",
    "share_level_no_registered_metric",
    "parameter_or_threshold_level",
    "unit_no_household_concept",
    "no_registered_metric",
    "mode3_specimen_household",
    "energy_bill_level_no_metric",
)
DROP_BY_NAME_AB2026: dict[str, str] = {
    # fiscal aggregates and their changes (#55)
    "fiscal_balance_change": M,
    "psnb_share_of_gdp": M,
    "public_sector_net_borrowing": M,
    "public_sector_net_debt": M,
    "public_sector_net_debt_change": M,
    "public_sector_net_financial_liabilities": M,
    "public_debt_change": M,
    "psnd_impact": M,
    "psnfl_impact": M,
    "psnfl_fair_value_impact": M,
    "current_budget_balance": M,
    "primary_balance": M,
    "primary_balance_change": M,
    "tax_revenue_change": M,
    "tax_to_gdp_ratio": M,
    "tax_to_gdp_ratio_change": M,
    "absolute_policy_change": M,
    "fiscal_consolidation_share": M,
    "headroom_share_of_previous": M,
    "share_of_headroom_change": M,
    "current_budget_deficit_revision_risk": M,
    "ten_year_bond_spread_other_g7": M,
    "real_household_disposable_income_index": M,
    "jobs_created_or_supported": M,
    # departmental spending paths
    "real_spending_growth": M,
    "real_spending_growth_revision": M,
    "real_spending_change": M,
    "rdel_change": M,
    "rdel_share_of_gdp": M,
    "real_rdel_per_person_change": M,
    "spending_pressure": M,
    # funding between governments, and business outside the household model
    "devolved_funding_real_terms_change": M,
    "devolved_revenue": M,
    "business_cost_saving": M,
    "bill_change_percent": M,
    # ratios of two published quantities
    "effective_tax_rate_gap": R,
    "income_change_gap": R,
    "tax_gap_share_of_compliance_yield": R,
    "share_of_energy_price_increase_offset": R,
    "bill_rise_offset_share": R,
    "share_of_total_policy_cost": R,
    "revenue_share_by_fiscal_event": R,
    # behavioural responses and pass-through shares: inputs to a costing
    "parents_bunching": A,
    "behavioural_response_share": A,
    "workforce_exit_share": A,
    "incidence_share": A,
    # shares of a population at a level, with no registered metric
    "partner_not_in_work_share": S,
    "female_share": S,
    "share_with_zero_liability": S,
    "share_in_non_gaining_deciles": S,
    "share_in_net_recipient_deciles": S,
    "share_in_top_half_of_expenditure": S,
    # design: the present value of a capital allowance
    "capital_allowance_present_value": P,
    # a business's bill
    "business_rates_bill_change": U,
    # sums over several years per driver or business
    "average_cumulative_gain": N,
    # IFS's maximum gain per beneficiary, a statistic with no registered
    # metric
    "taxpayer_gain": N,
    # single-row quantities
    "housing_supply_change": N,
    "cash_receipts_change": N,
    "unit_rate_change": N,
    # single cases at a stated income
    "marginal_tax_amount": X,
    "marginal_take_home_pay": X,
    "net_weekly_income": X,
    # bill levels
    "typical_energy_bill": E,
    # IFS's support per household over October 2026 to June 2027
    "average_household_support": "partial_year_household_support",
}

DISPOSITIONS: dict[str, Metric] = {**AB25.DISPOSITIONS, **DISPOSITIONS_AB2026}
# AB2025's restatement reason says we stage the originator's rows in the same
# harvest. In AB2026 some don't: the costings restate HMRC's tax gap
# (rows 233 and 234), and the harvest stages no HMRC family.
_RESTATED_AB2026 = (
    "The producer repeats another body's figure (the OBR's, HM Treasury's, "
    "HMRC's or another producer's), and we credit a figure only to the body "
    "that estimated it, so the repetition is tallied, not scored. Where that "
    "body's own figure is in this harvest, we score it under that body."
)
DROPS: dict[str, str] = {
    **AB25.DROPS,
    "restated_official_figure": _RESTATED_AB2026,
    **DROPS_AB2026,
}
_DROP_BY_NAME: dict[str, str] = {**AB25._DROP_BY_NAME, **DROP_BY_NAME_AB2026}
assert not (set(DISPOSITIONS_AB2026) & set(AB25._DROP_BY_NAME))
assert not (set(DROP_BY_NAME_AB2026) & set(AB25.DISPOSITIONS))
assert not (set(DISPOSITIONS) & set(_DROP_BY_NAME)), "adopted or dropped, never both"
assert set(_DROP_BY_NAME.values()) <= set(DROPS), "every drop key has a reason"

# --- row calls ---------------------------------------------------------------
# (family, row number from 0) -> (staged metric, staged value_raw, Metric,
# why). The ingest raises if the staged row doesn't match, so a re-staged
# family can't move a call onto another row.
ROW_METRICS: dict[tuple[str, int], tuple[str, str, Metric, str]] = {
    ("uk_obr_tables", 2740): (
        "decisions_effect_on_borrowing",
        "£4.3 billion",
        Metric.REVENUE_CHANGE,
        "README rule 10 gives decisions_effect_on_borrowing to the effect of "
        "the Budget's decisions on PSNB, and the Government didn't adopt a "
        "continued fuel duty freeze, so the OBR's cost of one is a receipts "
        "effect on revenue_change.",
    ),
}

# (family, row) -> (staged value_raw, drop reason)
ROW_DROPS: dict[tuple[str, int], tuple[str, str]] = {
    ("uk_obr_tables", 2658): (
        "less than a 0.1 percentage point",
        "single_row_unregistered_world",
    ),
    ("uk_obr_tables", 2743): ("1.4 per cent", "single_row_unregistered_world"),
    ("uk_obr_tables", 2744): ("4.4 per cent", "single_row_unregistered_world"),
    # RF's continued fuel duty freeze is the OBR's constant-duty-rate
    # forecast less its central forecast (our notes to RF's rows 154 and
    # 397-401, citing its footnote 27), so the OBR's row 2740 is the one
    # estimate
    ("uk_rf_ab2026", 154): ("£4.3 billion", "restated_obr_forecast"),
    ("uk_rf_ab2026", 397): ("-2.3483484846542702", "restated_obr_forecast"),
    ("uk_rf_ab2026", 398): ("-3.7389555211291317", "restated_obr_forecast"),
    ("uk_rf_ab2026", 399): ("-4.2893363032056087", "restated_obr_forecast"),
    ("uk_rf_ab2026", 400): ("-4.6757828023106249", "restated_obr_forecast"),
    ("uk_rf_ab2026", 401): ("-4.8671109188223411", "restated_obr_forecast"),
    # RF's income paths over the Parliament, with no reform and baseline
    ("uk_rf_ab2026", 20): ("£420", "income_path_not_a_policy_effect"),
    ("uk_rf_ab2026", 22): ("£776", "income_path_not_a_policy_effect"),
    ("uk_rf_ab2026", 39): ("£600", "income_path_not_a_policy_effect"),
    ("uk_rf_ab2026", 40): ("£1,050", "income_path_not_a_policy_effect"),
    ("uk_rf_ab2026", 42): ("£1,000", "income_path_not_a_policy_effect"),
    ("uk_rf_ab2026", 50): ("£1,050", "income_path_not_a_policy_effect"),
    ("uk_rf_ab2026", 90): ("£400", "income_path_not_a_policy_effect"),
    ("uk_rf_ab2026", 199): ("£600", "income_path_not_a_policy_effect"),
    ("uk_rf_ab2026", 202): ("£1,050", "income_path_not_a_policy_effect"),
    # the red book's average gains per pub and per small business, outside
    # the household model as business savings are
    ("uk_hmt_redbook", 222): ("£3,000", "macro_fiscal_or_out_of_scope"),
    ("uk_hmt_redbook", 233): ("£3,000", "macro_fiscal_or_out_of_scope"),
    # CenTax's percentage revenue changes
    ("uk_centax", 19): ("62%", "ratio_or_derived_quantity"),
    ("uk_centax", 20): ("88%", "earlier_estimate_restated"),
}

# A producer's own world, quoted as `proposed_baseline`, by its opening words
# (AB2025's method, ingest_uk_ab2025._PROPOSED_BASELINE_PREFIXES).
_PROPOSED_BASELINE_PREFIXES: dict[str, str] = {
    **AB25._PROPOSED_BASELINE_PREFIXES,
    "OBR pre-measures Autumn Budget 2026 policy parameters": "obr_pre_measures_autumn_budget_2026__policy_parameters",
    # the AB2025 world, as the AB2026 OBR family words it
    "Fuel duty rates increase in line with RPI inflation: stated policy since 2010-11": "obr_fuel_duty_rpi_uprated_since_2010_11",
}

# The geography codes the harvest README allows for the UK and its parts.
# TPA also stages figures for the countries it compares the UK with; those
# claims stay in the DB and off the page (AB2025 held back TPA's
# constituency rows the same way, and AB2026 stages none).
UK_GEOGRAPHIES = frozenset(
    {
        "UK",
        "GB",
        "England",
        "Wales",
        "Scotland",
        "Northern Ireland",
        "England and Wales",
        "UK_excl_scotland",
        "Scotland, Wales and Northern Ireland",
        "not stated",
    }
)


def published(row: dict) -> bool:
    """Whether a claim reaches the page before a counterpart lands."""
    geography = (row.get("conditions") or {}).get("geography")
    return geography is None or geography in UK_GEOGRAPHIES


# The HM Treasury families whose rows can repeat a Table 6.1 or 6.2 cell.
_TWIN_FAMILIES = frozenset({"uk_hmt_costings", "uk_hmt_redbook"})

# Red book rows that repeat a Table 6.1 cell with another sign, a rounding or
# another period, so the exact match in _twin_key can't find them. Each entry
# maps (family, row) to the uk_hmt_tables row it repeats, with the reading
# that decides it. The ingest raises if either row's key no longer matches.
_HEP = (
    "The red book prints the Household Energy Payment's 2026-27 cost as "
    "£2.6 billion, a cost printed positive, and Table 6.1 line 1 prints it "
    "as -2,625 (£ million); £2.6 billion rounds -2,625 once the sign is "
    "normalised."
)
_SPR = (
    "The red book prints Small Producer Relief's support as £10 million a "
    "year, a cost printed positive, and Table 6.1 line 19 prints -10 (£ "
    "million) for 2027-28, the year staged on both rows."
)
_BOOKS = (
    "The red book prints up to £5 million a year for books for young "
    "children, a cost printed positive, and Table 6.1 line 9 prints -5 (£ "
    "million) for 2027-28, the year staged on both rows. The red book dates "
    "the three years from 2027-28 and Table 6.1 from 2026-27; the 2027-28 "
    "amount agrees."
)
_UKRAINE = (
    "The red book prints £500 million of military support for Ukraine's air "
    'defences "this winter", a cost printed positive, and Table 6.1 line 43 '
    "prints -500 (£ million) in 2026-27. The red book names no fiscal year: "
    "the row stages the 2026 announcement year, and the figure is Table 6.1's "
    "2026-27 cell."
)
REVIEWED_TWINS: dict[tuple[str, int], tuple[int, str]] = {
    ("uk_hmt_redbook", 6): (0, _HEP),
    ("uk_hmt_redbook", 179): (0, _HEP),
    ("uk_hmt_redbook", 11): (109, _SPR),
    ("uk_hmt_redbook", 236): (109, _SPR),
    ("uk_hmt_redbook", 220): (49, _BOOKS),
    ("uk_hmt_redbook", 270): (49, _BOOKS),
    ("uk_hmt_redbook", 263): (252, _UKRAINE),
    ("uk_hmt_redbook", 271): (252, _UKRAINE),
    ("uk_hmt_redbook", 272): (252, _UKRAINE),
}


def _is_component(row: dict) -> bool:
    """A part of a measure (rule 9), which is never a twin of the whole."""
    c = row.get("conditions") or {}
    return bool(c.get("component")) or c.get("row_type") == "measure_component"


def _registry() -> dict[str, dict]:
    reg = json.loads(REGISTRY_PATH.read_text())
    return {m["measure_key"]: m for m in reg["measures"]}


REGISTRY_DOC = json.loads(REGISTRY_PATH.read_text())
REGISTRY = _registry()
ENGINE_PIN = REGISTRY_DOC["engine_pin"]["policyengine_uk"]
DATA_REVISION = REGISTRY_DOC["engine_pin"]["budget_day_runs"]["dataset_revision"]


def _load(family: str) -> list[dict]:
    path = HARVEST / family / "claims_staged.jsonl.gz"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — the harvest family is not vendored")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != CLAIMS_SHA256[family]:
        raise ValueError(
            f"{family}: claims_staged.jsonl.gz sha256 {digest[:12]} != pinned "
            f"{CLAIMS_SHA256[family][:12]} — re-pin COUNTS.json deliberately"
        )
    rows = []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            unknown = sorted(set(row) - AB25._KNOWN_FIELDS)
            if unknown:
                raise ValueError(f"{family}: unhandled staged fields {unknown}")
            rows.append(row)
    return rows


def unit_label(row: dict) -> str | None:
    """The staged unit, with a share of GDP on percent_of_gdp: IFS stages
    its shares as `percent` with `conditions.denominator: GDP`, and the OBR
    and TPA propose `percent_of_gdp`."""
    label = row.get("unit_concept") or row.get("proposed_unit")
    denominator = str((row.get("conditions") or {}).get("denominator", ""))
    if label == "percent" and denominator.strip().lower() == "gdp":
        return "percent_of_gdp"
    return label


def _baseline(row: dict, source: str) -> dict | None:
    label = row.get("baseline_policy")
    proposed = row.get("proposed_baseline")
    if label and proposed:
        raise ValueError(f"{source}: both baseline_policy and proposed_baseline set")
    if proposed:
        text = AB25._normalise_quotes(proposed)
        label = next(
            (
                lab
                for prefix, lab in _PROPOSED_BASELINE_PREFIXES.items()
                if text.startswith(AB25._normalise_quotes(prefix))
            ),
            None,
        )
        if label is None:
            raise ValueError(
                f"{source}: proposed_baseline is not a registered world: "
                f"{proposed[:100]!r} — register it in baselines.py (#13)"
            )
    if not label:
        return None
    if label not in AB25._BASELINE_BY_LABEL:
        raise ValueError(f"{source}: baseline label {label!r} is not registered")
    return AB25._BASELINE_BY_LABEL[label]


def _verdict_conditions(row: dict, cond: dict, metric: Metric) -> None:
    key = row.get("measure_key")
    if key:
        cond["measure_key"] = key
        # a recosting's key is an earlier event's (README rule 2); its
        # verdict at that event's engine says nothing about 2.151.0
        if key in REGISTRY and "recosting_of" not in cond:
            m = REGISTRY[key]
            cond["pe_expressibility"] = m["computability"]
            gap = m.get("missing") or m.get("why")
            if gap:
                cond["pe_missing"] = gap
            if m.get("action_link"):
                cond["action_link"] = m["action_link"]
    if metric in AB25.MACRO_METRICS:
        cond["pe_expressibility"] = "not_expressible"
        cond["pe_missing"] = AB25.MACRO_MISSING
        cond["action_link"] = AB25.MACRO_LINK


def _score(row: dict, family: str, source: str, metric: Metric) -> ExternalScore:
    label = unit_label(row)
    if label not in AB25.UNITS:
        raise ValueError(f"{source}: unregistered unit {label!r}")
    unit = AB25.UNITS[label]

    cond: dict[str, str] = {"country": "UK"}
    for key, value in (row.get("conditions") or {}).items():
        if key in AB25._CANONICALISED:
            cond[key] = canon(source, key, value)
            if cond[key] != value:
                cond[f"{key}_verbatim"] = value
        elif key == "program":
            if value in known(source, "program"):
                cond["program"] = canon(source, "program", value)
            else:
                cond["program_verbatim"] = value
        else:
            cond[key] = value
    if cond.get("fiscal_event") != FISCAL_EVENT:
        raise ValueError(f"{source}: fiscal_event {cond.get('fiscal_event')!r}")
    cond["value_verbatim"] = str(row["value_raw"])
    cond["benchmark_class"] = row["benchmark_class"]
    if row.get("value_kind") and row["value_kind"] != "point":
        cond["estimate_kind"] = row["value_kind"]
    staged_metric = row.get("metric") or row.get("proposed_metric")
    if staged_metric != metric.value:
        # the name the producer's figure was staged under, where the ingest
        # decided another (a proposal, or a ROW_METRICS call)
        cond["staged_metric"] = staged_metric
    if row.get("proposed_metric") == "exchequer_impact_static":
        cond.setdefault("scoring_method", "static")
    if row.get("reform_hint"):
        cond["reform_hint"] = row["reform_hint"]
    if row.get("proposed_baseline"):
        cond["counterfactual"] = row["proposed_baseline"]
    _verdict_conditions(row, cond, metric)

    basis = AB25.TIME_BASES.get(row.get("time_basis"))
    if basis is None:
        raise ValueError(f"{source}: unregistered time_basis {row.get('time_basis')!r}")

    baseline = _baseline(row, source)
    reform = AB25._reform(row, source, baseline)
    with_baseline_condition(cond, reform)

    pub = dict(row.get("publication") or {})
    pub.update(
        {
            "registry": REGISTRY_MARK,
            "family": family,
            "table": row.get("source_table"),
            "quote": row.get("quote"),
            "attribution": row["attribution"],
            "publish_without_result": published(row),
        }
    )
    if row.get("note"):
        pub["note"] = row["note"]
    if row.get("parse_confidence") and row["parse_confidence"] != "high":
        pub["parse_confidence"] = row["parse_confidence"]

    return ExternalScore(
        source=source,
        metric=metric,
        unit_concept=unit,
        period=int(row["period"]),
        time_basis=basis,
        value=float(row["value"]),
        conditions=cond,
        reform=reform,
        calibration_relationship=uk_relationship(source, metric)[0],
        source_model=AB25._source_model(source, row),
        source_column=row.get("source_column") or "",
        publication=pub,
        value_kind=row.get("value_kind") or unit.value,
        status="ok",
    )


def _twin_key(row: dict, name: str) -> tuple | None:
    """The identity of one HM Treasury figure across its documents: key,
    staged metric, unit, year and value. A part of a measure (rule 9) is
    never a twin of the whole."""
    if row["source"] != "hm_treasury" or _is_component(row):
        return None
    return (row.get("measure_key"), name, unit_label(row), row["period"], row["value"])


def _precision(s: ExternalScore) -> tuple:
    """merge_republications keeps the higher of two printings: more printed
    digits first, then the printing's provenance, so row order never decides
    which printing a claim cites."""
    pub = s.publication
    return (
        len(s.conditions.get("value_verbatim", "")),
        json.dumps(
            [pub.get("table"), pub.get("locator"), s.source_column, pub.get("quote")],
            default=str,
        ),
    )


def _drop(acct: dict, fam: dict, reason_key: str) -> None:
    entry = acct["drops"].setdefault(
        reason_key, {"rows": 0, "reason": DROPS[reason_key]}
    )
    entry["rows"] += 1
    fam["dropped"] += 1
    fam.setdefault("drops", {})
    fam["drops"][reason_key] = fam["drops"].get(reason_key, 0) + 1


def _check_row_calls(family: str, rows: list[dict]) -> None:
    for (fam, i), (metric, raw, _, _) in ROW_METRICS.items():
        if fam == family:
            r = rows[i]
            if (r.get("metric") or r.get("proposed_metric"), r["value_raw"]) != (
                metric,
                raw,
            ):
                raise ValueError(f"ROW_METRICS {fam} row {i} no longer matches")
    for (fam, i), (raw, _) in ROW_DROPS.items():
        if fam == family and rows[i]["value_raw"] != raw:
            raise ValueError(f"ROW_DROPS {fam} row {i} no longer matches")
    reviewed = {i: t for (fam, i), (t, _) in REVIEWED_TWINS.items() if fam == family}
    if reviewed:
        table = _load("uk_hmt_tables")
        for i, t in reviewed.items():
            r = rows[i]
            if _is_component(r) or _is_component(table[t]):
                raise ValueError(f"REVIEWED_TWINS {family} row {i} is a component")
            if r.get("measure_key") != table[t].get("measure_key"):
                raise ValueError(f"REVIEWED_TWINS {family} row {i} no longer matches")


def stage(families: dict | None = None) -> tuple[list[ExternalScore], dict]:
    """Stage every ingestible row; nothing touches the DB here.

    Returns (scores, accounting): read = ingested + dropped, by family and
    by reason. ``families`` maps a family to (row number, row) pairs, so a
    test can stage a sample and the row calls still find their rows; by
    default each family's pinned claims file, whole."""
    scores: list[ExternalScore] = []
    acct = {"read": 0, "ingested": 0, "dropped": 0, "by_family": {}, "drops": {}}
    canonical: dict[tuple, ExternalScore] = {}
    table_claims: dict[int, ExternalScore] = {}
    for family, (lane, sources) in FAMILIES.items():
        if families is None:
            loaded = _load(family)
            _check_row_calls(family, loaded)
            numbered = list(enumerate(loaded))
        else:
            numbered = list(families.get(family, []))
        fam = {"read": len(numbered), "ingested": 0, "dropped": 0, "lane": lane}
        acct["read"] += len(numbered)
        for i, row in numbered:
            source = row["source"]
            if source not in sources:
                raise ValueError(
                    f"{family}: row source {source!r} not in {sorted(sources)}"
                )
            name = AB25._metric_name(row)
            if row["attribution"] == "restated":
                _drop(acct, fam, "restated_official_figure")
                continue
            if row.get("value_kind") == "categorical":
                _drop(acct, fam, "categorical_rating_not_a_value")
                continue
            if (family, i) in ROW_DROPS:
                _drop(acct, fam, ROW_DROPS[(family, i)][1])
                continue
            if AB25._is_specimen(row, name):
                _drop(acct, fam, "mode3_specimen_household")
                continue
            if name in _DROP_BY_NAME:
                _drop(acct, fam, _DROP_BY_NAME[name])
                continue
            label = unit_label(row)
            if label in AB25._UNIT_DROPS:
                _drop(acct, fam, AB25._UNIT_DROPS[label])
                continue
            if name not in DISPOSITIONS:
                raise ValueError(
                    f"{family}: metric {name!r} has no disposition — decide it "
                    "in DISPOSITIONS_AB2026 or DROP_BY_NAME_AB2026"
                )
            metric = DISPOSITIONS[name]
            if (family, i) in ROW_METRICS:
                metric = ROW_METRICS[(family, i)][2]
            twin = _twin_key(row, name)
            kept = None
            if family in _TWIN_FAMILIES and (family, i) in REVIEWED_TWINS:
                kept = table_claims.get(REVIEWED_TWINS[(family, i)][0])
            elif family in _TWIN_FAMILIES and twin in canonical:
                kept = canonical[twin]
            if kept is not None:
                kept.publication.setdefault("also_printed_in", []).append(
                    {
                        "family": family,
                        "table": row.get("source_table"),
                        "locator": (row.get("publication") or {}).get("locator"),
                        "source_column": row.get("source_column"),
                    }
                )
                _drop(acct, fam, "hmt_figure_staged_twice")
                continue
            score = _score(row, family, source, metric)
            if family == "uk_hmt_tables":
                table_claims[i] = score
                if twin is not None:
                    canonical[twin] = score
            scores.append(score)
            fam["ingested"] += 1
            acct["ingested"] += 1
        acct["by_family"][family] = fam
    # One producer's twin printings within a family (AB2025's merge).
    merged: list[ExternalScore] = []
    for source in sorted({s.source for s in scores}):
        mine = [s for s in scores if s.source == source]
        kept = merge_republications(
            mine,
            source,
            precision=_precision,
            tolerance=lambda s: max(abs(s.value) * 0.005, 1e-9),
        )
        kept_by_id = {k.claim_id(): k for k in kept}
        kept_ids = {id(k) for k in kept}
        for s in mine:
            if id(s) not in kept_ids:
                fam = acct["by_family"][s.publication["family"]]
                _drop(acct, fam, "republished_twin_merged")
                acct["ingested"] -= 1
                fam["ingested"] -= 1
                # the merged-away claim's twin printings stay with its figure
                twins = s.publication.get("also_printed_in")
                if twins:
                    keep = kept_by_id[s.claim_id()].publication
                    keep.setdefault("also_printed_in", []).extend(twins)
        merged.extend(kept)
    for s in merged:
        if "also_printed_in" in s.publication:
            s.publication["also_printed_in"].sort(
                key=lambda t: json.dumps(t, sort_keys=True)
            )
    acct["dropped"] = acct["read"] - acct["ingested"]
    for fam in acct["by_family"].values():
        if fam["read"] != fam["ingested"] + fam["dropped"]:  # pragma: no cover
            raise ValueError("a family's accounting does not close")
    return finish(merged, REGISTRY_MARK), acct


_EXPECTED_PATH = Path(__file__).parent / "ingest_uk_ab2026_expected.json"


def expected() -> dict:
    return json.loads(_EXPECTED_PATH.read_text())


def summarise(acct: dict) -> dict:
    return {
        "read": acct["read"],
        "ingested": acct["ingested"],
        "dropped": acct["dropped"],
        "by_family": {
            fam: {"read": v["read"], "ingested": v["ingested"], "dropped": v["dropped"]}
            for fam, v in acct["by_family"].items()
        },
        "drops": {k: v["rows"] for k, v in sorted(acct["drops"].items())},
    }


def check_accounting(acct: dict) -> None:
    got, want = summarise(acct), expected()
    if got != want:
        raise ValueError(f"claim accounting drifted: {got} != {want}")
    pinned = sum(
        v["rows"]
        for k, v in json.loads((HARVEST / "COUNTS.json").read_text()).items()
        if not k.startswith("_")
    )
    if got["read"] != pinned:
        raise ValueError(f"read {got['read']} rows, COUNTS.json pins {pinned}")


ALL_SOURCES = frozenset(s for _, srcs in FAMILIES.values() for s in srcs)


def ingest(db_path: Path, feed_path: Path | None = None) -> dict:
    """Stage and check first; then one transaction replaces every AB2026
    claim by registry mark (hm_treasury, obr_efo, ifs and others also mark other
    lanes' rows) and runs the baseline-registration gate inside it."""
    scores, acct = stage()
    check_accounting(acct)
    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(s) for s in scores]

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute(
            "DELETE FROM external_scores WHERE"
            " json_extract(publication, '$.registry') = ?",
            (REGISTRY_MARK,),
        )
        db.conn.executemany(SCORES_SQL, rows)
        register_baselines_txn(db)
        for lane in LANES:
            fams = [f for f, (l, _) in FAMILIES.items() if l == lane]
            read = sum(acct["by_family"][f]["read"] for f in fams)
            ing = sum(acct["by_family"][f]["ingested"] for f in fams)
            detail = (
                f"{ing} claims from {len(fams)} families ({read} staged rows = "
                f"{ing} ingested + {read - ing} tallied drops)"
            )
            db.conn.execute(
                LANE_SQL,
                (lane, "ingested" if ing else "cataloged", detail, LANE_UPDATED),
            )
    sync_lane_feed(
        db, feed_path or REPO / "data" / "lanes.json", FEED_UPDATED, lanes=LANES
    )
    db.close()
    return {
        "claims": len(rows),
        "read": acct["read"],
        "ingested": acct["ingested"],
        "dropped": acct["dropped"],
        "drops": {k: v["rows"] for k, v in sorted(acct["drops"].items())},
    }


def advance_lanes(db_path: Path, feed_path: Path | None = None) -> dict:
    """Move each AB2026 lane whose claims now have a PolicyEngine
    counterpart (a comparable or constructed result) from ``ingested`` to
    ``computed``, naming how many claims have one, as AB2025's does. A lane
    with no counterpart keeps its stage, and pe_gap verdicts don't count."""
    from .ingest_harvest import sync_lane_feed

    db = ScorecardDB(db_path)
    out: dict = {}
    with db.conn:
        for lane in LANES:
            fams = [f for f, (l, _) in FAMILIES.items() if l == lane]
            marks = ",".join("?" * len(fams))
            row = db.conn.execute(
                "SELECT stage, detail FROM lanes WHERE lane = ?", (lane,)
            ).fetchone()
            if row is None:
                continue
            answered, claims = db.conn.execute(
                "SELECT COUNT(DISTINCT r.claim_id), COUNT(DISTINCT s.claim_id)"
                " FROM external_scores s LEFT JOIN pe_results r ON r.claim_id = s.claim_id"
                " AND r.status IN ('comparable', 'constructed')"
                " WHERE json_extract(s.publication, '$.registry') = ?"
                f" AND json_extract(s.publication, '$.family') IN ({marks})",
                (REGISTRY_MARK, *fams),
            ).fetchone()
            out[lane] = {"claims": claims, "answered": answered}
            if not answered:
                continue
            base = row["detail"].split(" — ")[0]
            detail = (
                f"{base} — {answered} claims with a PolicyEngine counterpart from "
                "the dashboard's Budget-day runs"
            )
            db.conn.execute(LANE_SQL, (lane, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db, feed_path or REPO / "data" / "lanes.json", FEED_UPDATED, lanes=LANES
    )
    db.close()
    return out


# --- pe_gap verdicts ----------------------------------------------------------


def verdict_rows(db: ScorecardDB) -> tuple[list[tuple], list[tuple]]:
    """One pe_gap result and one pe_gap diagnosis per AB2026 claim whose
    measure the pinned engine can't express, from the registry."""
    claims = db.conn.execute(
        "SELECT claim_id, baseline_key, metric,"
        " json_extract(conditions, '$.measure_key') AS measure_key,"
        " json_extract(conditions, '$.pe_missing') AS pe_missing,"
        " json_extract(conditions, '$.action_link') AS action_link"
        " FROM external_scores"
        " WHERE json_extract(publication, '$.registry') = ?"
        "   AND json_extract(conditions, '$.pe_expressibility') = 'not_expressible'"
        " ORDER BY claim_id",
        (REGISTRY_MARK,),
    ).fetchall()
    results, diagnoses = [], []
    for c in claims:
        if c["metric"] in {m.value for m in AB25.MACRO_METRICS}:
            m = {
                "why": c["pe_missing"],
                "name_search": "Parameters: none searched — a macro-fiscal aggregate names no engine lever; the Macro entry point (#55) answers it",
                "action_link": c["action_link"],
            }
            gap_key = c["measure_key"] or "macro"
        else:
            m = REGISTRY[c["measure_key"]]
            gap_key = c["measure_key"]
            if m["computability"] != "not_expressible":
                raise ValueError(
                    f"{c['claim_id']}: not_expressible on the claim but "
                    f"{m['computability']} in the registry"
                )
        results.append(
            ScorecardDB.result_row(
                PEResult(
                    claim_id=c["claim_id"],
                    computed_value=None,
                    status=ComparisonStatus.PE_GAP,
                    engine_version=ENGINE_PIN,
                    data_bundle=DATA_REVISION,
                    pe_construction=f"pe_gap:not_expressible:{gap_key}",
                    run_id=VERDICT_RUN_ID,
                    computed_at=VERDICT_COMPUTED_AT,
                    annotations=[
                        m["why"],
                        m["name_search"],
                        "no run executed: the verdict is the registry's, stated "
                        f"against the Budget-day engine {ENGINE_PIN}",
                    ],
                    baseline_key=c["baseline_key"],
                    policyengine_variables=[],
                )
            )
        )
        diagnoses.append(
            ScorecardDB.diagnosis_row(
                c["claim_id"], "pe_gap", m["why"], m["action_link"]
            )
        )
    return results, diagnoses


def ingest_verdicts(db_path: Path) -> dict:
    """Second build step: replace this run's verdict rows wholesale."""
    db = ScorecardDB(db_path)
    results, diagnoses = verdict_rows(db)
    with db.conn:
        db.conn.execute("DELETE FROM pe_results WHERE run_id = ?", (VERDICT_RUN_ID,))
        db.conn.execute(
            "DELETE FROM diagnoses WHERE claim_id IN ("
            " SELECT claim_id FROM external_scores"
            " WHERE json_extract(publication, '$.registry') = ?)",
            (REGISTRY_MARK,),
        )
        db.conn.executemany(RESULTS_SQL, results)
        db.conn.executemany(DIAGNOSES_SQL, diagnoses)
    db.close()
    return {"pe_gap_results": len(results), "pe_gap_diagnoses": len(diagnoses)}


if __name__ == "__main__":
    import sys

    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(path), indent=1))
    print(json.dumps(ingest_verdicts(path), indent=1))
