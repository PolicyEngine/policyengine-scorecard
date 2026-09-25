"""Ingest every Autumn Budget 2025 score (#136).

The 2026-09-24 harvest at ``sources/harvest-uk-ab2025-2026-09-24/`` stages
8,194 rows from 25 families (50 producers): HM Treasury's and the OBR's own
costing legs, seven independent microsimulation shops, thirteen
administrative-data and own-computation shops, and the commercial firms'
single-household worked examples. This module is the ingest: every row is
either a claim in the DB or a tallied drop with a written reason, and the
accounting at the bottom pins ``read = ingested + dropped`` per family so
nothing can shrink or grow silently.

What every claim carries, so the same material can be pulled by producer,
by measure or by event (the issue's three retrieval axes):

- ``source``                 the producer (one slug per publisher)
- ``conditions.measure_key`` the registry key (data/uk/ab2025_measures.json)
                             on every reform score, shared across producers
- ``conditions.fiscal_event`` the slug ``autumn_budget_2025``
- ``conditions.benchmark_class`` different_model | administrative_fact |
                             same_assumptions — the first UK use of the
                             cross-model epistemics ruling of 2026-08-02
- ``conditions.pe_expressibility`` / ``pe_missing`` / ``action_link``
                             the registry's verdict on the row's measure
                             (the ONS ETB pattern): a row on a measure the
                             engine cannot express says so on the row
- ``publication.publish_without_result``
                             true for every national-grain row, so the
                             claims reach the page before counterparts
                             land (the NZ precedent); the 2,991
                             constituency-grain Tax Policy Associates
                             rows stay in the DB and out of the feed
                             until a constituency view exists

Four drops the harvest contract anticipates, tallied here rather than
omitted there: re-published official figures (attribution ``restated``,
the #86 rule — 342 rows, their originators' claims); single-household
worked examples (mode-3 material for #63, the whole commercial family
plus every specimen-household row elsewhere); categorical uncertainty
ratings; and the assumptions, tax bases, macro-fiscal aggregates and
derived ratios that are not scores of a household quantity. Every other
proposed metric is DECIDED in ``DISPOSITIONS`` (mapped to a registered
Metric) or ``DROPS`` (tallied with a reason); an unlisted proposal raises.

The ``pe_gap`` verdicts (``ingest_verdicts``) are a second build step: for
every claim on a ``not_expressible`` measure, one ``pe_results`` row with
status ``pe_gap`` (the comparisons view's row verdict) AND one ``diagnoses``
row of class ``pe_gap`` carrying the registry's ``action_link`` (the only
place the schema holds the link, gated by the descriptive register #9), so
"every pe_gap row carries its action_link" is a fact of the DB, not of a
convention.

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_uk_ab2025 data/scorecard.db
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from .baselines import BASELINES
from .db import DIAGNOSES_SQL, LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .engines import ENGINES, engine_of, known_release, split_release
from .harvest import (
    REPO,
    finish,
    merge_republications,
    policy_ref,
    with_baseline_condition,
)
from .models import (
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    ReformRef,
    TimeBasis,
    UnitConcept,
)
from .relationships import uk_relationship
from .uk_aliases import canon, known

HARVEST = REPO / "sources" / "harvest-uk-ab2025-2026-09-24"
REGISTRY_PATH = REPO / "data" / "uk" / "ab2025_measures.json"
BUNDLE_PATH = REPO / "data" / "uk" / "certified_bundle.json"

REGISTRY_MARK = "uk_ab2025"
FISCAL_EVENT = "autumn_budget_2025"
# The UK family's shared top-level feed literal (sync_lane_feed's
# contract: every caller in a build passes the same one).
FEED_UPDATED = "2026-08-19"
LANE_UPDATED = "2026-09-24"
VERDICT_RUN_ID = "ab2025-verdicts-2026-09-24"
VERDICT_COMPUTED_AT = "2026-09-24T00:00:00+00:00"

# Macro-fiscal claims (#55): whatever measure or package they are keyed to,
# the household model has no lever for a headroom, GDP or CPI call, so the
# claim carries its own out-of-scope verdict and the lane's link.
MACRO_METRICS = frozenset(
    {
        Metric.FISCAL_HEADROOM,
        Metric.GDP_LEVEL_EFFECT,
        Metric.CPI_INFLATION_EFFECT,
        Metric.DECISIONS_EFFECT_ON_BORROWING,
    }
)
MACRO_LINK = "https://github.com/PolicyEngine/policyengine-scorecard/issues/55"
MACRO_MISSING = (
    "macro-fiscal quantity: the household model has no forecast, no fiscal "
    "rule, no headroom and no GDP or CPI channel; the Macro entry point (#55) "
    "answers it"
)

LANES = {
    "uk-ab2025-official": {
        "source": "HM Treasury, HMRC and OBR (Autumn Budget 2025 legs)",
        "area": "official costings, TIINs and EFO tables for the Budget's measures",
        "mode": 2,
        "country": "UK",
    },
    "uk-ab2025-microsim": {
        "source": "IFS, RF, JRF, IPPR, CPAG, FAI/SFC, WBG (Autumn Budget 2025)",
        "area": "independent microsimulation of the Budget's measures and options",
        "mode": 2,
        "country": "UK",
    },
    "uk-ab2025-admin-other": {
        "source": "CenTax, TPA, PiP, NEF, NIESR and the smaller shops (Autumn Budget 2025)",
        "area": "administrative-data and own-computation scores of the Budget's measures",
        "mode": 2,
        "country": "UK",
    },
    "uk-ab2025-macro": {
        "source": "Capital Economics, Goldman Sachs, Deutsche Bank, Barclays, Société Générale, Oxford Economics, EY ITEM Club and NIESR NiGEM (Autumn Budget 2025)",
        "area": "macro and fiscal-aggregate calls on the Budget package — the #55 lane, out of the household model's scope",
        "mode": 2,
        "country": "UK",
    },
    "uk-ab2025-cases": {
        "source": "commercial firms and platforms (Autumn Budget 2025 worked examples)",
        "area": "single-household worked examples, staged for the mode-3 tally (#63)",
        "mode": 3,
        "country": "UK",
    },
}

# harvest family dir -> (lane, allowed source slugs)
FAMILIES: dict[str, tuple[str, frozenset[str]]] = {
    "uk_hmt_costings": ("uk-ab2025-official", frozenset({"hm_treasury"})),
    "uk_hmt_redbook": ("uk-ab2025-official", frozenset({"hm_treasury"})),
    "uk_hmrc_tiins": ("uk-ab2025-official", frozenset({"uk_hmrc"})),
    "uk_obr_tables": ("uk-ab2025-official", frozenset({"obr_efo"})),
    "uk_ifs_ab2025": ("uk-ab2025-microsim", frozenset({"ifs"})),
    "uk_rf_ab2025": ("uk-ab2025-microsim", frozenset({"resolution_foundation"})),
    "uk_jrf": ("uk-ab2025-microsim", frozenset({"jrf"})),
    "uk_ippr": ("uk-ab2025-microsim", frozenset({"ippr"})),
    "uk_cpag": ("uk-ab2025-microsim", frozenset({"cpag"})),
    "uk_fai_sfc": (
        "uk-ab2025-microsim",
        frozenset({"fraser_of_allander", "scottish_fiscal_commission"}),
    ),
    "uk_wbg": ("uk-ab2025-microsim", frozenset({"wbg"})),
    "uk_ukmod_ab2025": ("uk-ab2025-microsim", frozenset({"ukmod"})),
    "uk_macro_calls": (
        "uk-ab2025-macro",
        frozenset(
            {
                "barclays",
                "capital_economics",
                "deutsche_bank",
                "ey_item_club",
                "goldman_sachs",
                "niesr",
                "oxford_economics",
                "societe_generale",
            }
        ),
    ),
    "uk_centax": ("uk-ab2025-admin-other", frozenset({"centax"})),
    "uk_tpa": ("uk-ab2025-admin-other", frozenset({"tax_policy_associates"})),
    "uk_pip": ("uk-ab2025-admin-other", frozenset({"policy_in_practice"})),
    "uk_entitledto": ("uk-ab2025-admin-other", frozenset({"entitledto"})),
    "uk_nef": ("uk-ab2025-admin-other", frozenset({"nef"})),
    "uk_cebr": ("uk-ab2025-admin-other", frozenset({"cebr"})),
    "uk_smf": ("uk-ab2025-admin-other", frozenset({"smf"})),
    "uk_publicfirst": ("uk-ab2025-admin-other", frozenset({"public_first"})),
    "uk_demos": ("uk-ab2025-admin-other", frozenset({"demos"})),
    "uk_fabians": ("uk-ab2025-admin-other", frozenset({"fabian_society"})),
    "uk_thinktank_misc": (
        "uk-ab2025-admin-other",
        frozenset(
            {
                "taxpayers_alliance",
                "cps",
                "onward",
                "tax_justice_uk",
                "iea",
                "policy_exchange",
                "ppi",
                "loughborough_crsp",
            }
        ),
    ),
    "uk_trussell_wpi": ("uk-ab2025-admin-other", frozenset({"trussell_wpi"})),
    "uk_niesr": ("uk-ab2025-admin-other", frozenset({"niesr"})),
    "uk_cases_commercial": (
        "uk-ab2025-cases",
        frozenset(
            {
                "deloitte",
                "ey",
                "aj_bell",
                "hargreaves_lansdown",
                "quilter",
                "fidelity",
                "royal_london",
                "aegon",
                "rsm",
                "moore_kingston_smith",
                "blick_rothenberg",
                "kpmg",
                "which",
                "moneyweek",
                "investengine",
                "ig",
                "rathbones",
                "evelyn_partners",
                "pwc",
            }
        ),
    ),
}

# sha256 of each family's claims_staged.jsonl.gz as vendored (NZ precedent:
# the ingest refuses a silently edited file). Regenerate from
# sources/harvest-uk-ab2025-2026-09-24/COUNTS.json when a family is
# deliberately re-staged.
CLAIMS_SHA256: dict[str, str] = json.loads((HARVEST / "COUNTS.json").read_text())
CLAIMS_SHA256 = {
    fam: entry["claims_sha256"]
    for fam, entry in CLAIMS_SHA256.items()
    if not fam.startswith("_")
}

# --- the disposition table --------------------------------------------------
# Every metric name the staging can present — its own registered `metric`
# or, where that is null, its `proposed_metric` — maps to exactly one of a
# Metric (ingest under it) or a DROP reason key (tally it). An unlisted
# name raises: a proposal is a suggestion from the harvest; this table is
# where it becomes a decision.
DISPOSITIONS: dict[str, Metric] = {
    # registered metrics carried straight through
    **{m.value: m for m in Metric},
    # counts and shares of the affected population
    "affected_count": Metric.AFFECTED_COUNT,
    "affected_share": Metric.AFFECTED_SHARE,
    "share_of_affected_households": Metric.AFFECTED_SHARE,
    "share_of_affected_properties": Metric.AFFECTED_SHARE,
    "share_of_affected_contributions": Metric.AFFECTED_SHARE,
    "share_of_additional_nics_liability": Metric.AFFECTED_SHARE,
    "taxpayer_share_higher_or_additional_rate": Metric.AFFECTED_SHARE,
    # exchequer legs: a static leg is a revenue change with
    # scoring_method static; the published sign rides in conditions and
    # the value is NOT re-signed here
    "exchequer_impact_static": Metric.REVENUE_CHANGE,
    # The #55 lane (tranche 4): headroom calls and package-size calls from
    # the banks, NIESR and the think tanks. Out of the household model's
    # scope on every claim (MACRO_METRICS), never a registry verdict.
    "fiscal_headroom": Metric.FISCAL_HEADROOM,
    "package_tax_rise_size": Metric.REVENUE_CHANGE,
    "package_spending_change": Metric.REVENUE_CHANGE,
    # UKMOD's fiscal overview (CeMPA WP 3/26): the change in benefit
    # expenditure and the net fiscal impact (revenue change minus
    # expenditure change), the latter carried as an exchequer impact
    # with the fiscal measure named on the claim
    "expenditure_change": Metric.BENEFIT_COST_CHANGE,
    "net_fiscal_impact": Metric.REVENUE_CHANGE,
    "levy_yield": Metric.REVENUE_CHANGE,
    "revenue_share": Metric.REVENUE_SHARE,
    # per-unit tax changes
    "employee_tax_liability_change": Metric.AVERAGE_TAX_CHANGE,
    "average_additional_nics_per_employee": Metric.AVERAGE_TAX_CHANGE,
    "average_tax_change": Metric.AVERAGE_TAX_CHANGE,
    "household_tax_change": Metric.AVERAGE_TAX_CHANGE,
    "employer_nics_change": Metric.AVERAGE_TAX_CHANGE,
    # income changes and levels
    "household_income_change": Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
    "average_income_change_among_affected": Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
    "real_income_change": Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
    "real_purchasing_power_change": Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
    "discretionary_income_change": Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
    "real_income_level": Metric.INCOME_STATISTIC,
    "pct_change_after_tax_income_component": Metric.PCT_CHANGE_AFTER_TAX_INCOME,
    "share_no_change": Metric.SHARE_NO_CHANGE,
    "benefit_loss_per_child": Metric.AVERAGE_ANNUAL_GAIN,
    "average_annual_loss": Metric.AVERAGE_ANNUAL_GAIN,
    "saving_per_person": Metric.AVERAGE_ANNUAL_GAIN,
    "effective_tax_rate": Metric.AVERAGE_TAX_RATE,
    # participation
    "salary_sacrifice_share": Metric.PARTICIPATION_RATE,
    # poverty and hardship (WPI's measure stays DISTINCT through
    # conditions.poverty_measure)
    "severe_hardship_count_change": Metric.POVERTY_COUNT_CHANGE,
    "poverty_depth_reduction_count": Metric.POVERTY_COUNT_CHANGE,
    # energy bills
    "energy_bill_saving_quartile": Metric.ENERGY_BILL_CHANGE,
    "average_energy_bill_change": Metric.ENERGY_BILL_CHANGE,
    "median_energy_bill_saving": Metric.ENERGY_BILL_CHANGE,
    "average_bill_change": Metric.ENERGY_BILL_CHANGE,
    "bill_change_pct": Metric.ENERGY_BILL_CHANGE,
    "household_energy_bill_change": Metric.ENERGY_BILL_CHANGE,
    "energy_price_cap_change": Metric.ENERGY_BILL_CHANGE,
    # a tax base in GBP is an aggregate of income the engine can total
    "tax_base": Metric.INCOME_AGGREGATE,
}

DROPS: dict[str, str] = {
    "restated_official_figure": (
        "The row carries attribution=restated: an OBR, HM Treasury, DWP or "
        "another producer's figure the publisher repeats. Staging it under "
        "the publisher would attribute a government number to a think tank "
        "and let a PE divergence read as disagreement with a model that "
        "never produced it (#86). The originator's own rows are in this "
        "harvest under the originator; these are tallied so the harvest is "
        "complete without the DB being wrong."
    ),
    "mode3_worked_example": (
        "A single-household worked example (a stated income, a stated "
        "result) from a commercial firm or platform. It is inputs -> outputs "
        "on stated rates, i.e. mode-3 material for the household cases "
        "battery (#63), not a mode-2 score of a population quantity; it is "
        "staged so the tally is complete and waits for the mode-3 table."
    ),
    "mode3_specimen_household": (
        "A specimen family or individual (conditions name the household "
        "type or its inputs) whose result is a single case, not a population "
        "average: RF's Stairway Table 1 families, IFS's basic-rate and "
        "higher-rate taxpayer examples, CPAG's capped lone parent. Mode-3 "
        "material for #63, same disposition as the commercial examples."
    ),
    "categorical_rating_not_a_value": (
        "The OBR's costing uncertainty rating is a category (low / medium / "
        "high and their intermediates), staged with value 0 and the rating "
        "in value_raw so the sheet is tallied; a category is not a number a "
        "microsimulation can reproduce."
    ),
    "assumption_or_base_not_a_score": (
        "A behavioural parameter (an elasticity, a take-up uplift, a "
        "pass-through share) or a non-monetary tax-base count (cars, "
        "miles, transactions, properties in a costing note) is an INPUT to "
        "a costing, not a score. These belong beside the divergence axes "
        "(data/uk/obr_divergence_axes.json) when a measure's decomposition "
        "is sized, not in the claims table as comparators."
    ),
    "unit_no_household_concept": (
        "The unit is not a household, person or money quantity the "
        "scorecard registers (businesses, council tax reduction schemes, "
        "UC child elements, claims, hours, pence per kilometre, a "
        "percentile): one or two rows do not justify minting a unit "
        "concept, and mapping them to a near-neighbour would misstate what "
        "was counted."
    ),
    "macro_fiscal_or_out_of_scope": (
        "A macro-fiscal aggregate (headroom, borrowing, consolidation "
        "requirements, shares of GDP, departmental spending paths) or a "
        "quantity outside a household model (central-bank losses, business "
        "investment, retailer windfalls, compliance costs, vehicle sales, "
        "house-price and rent level effects, block-grant arithmetic). "
        "Headroom and borrowing calls are the #55 lane (tranche 4 of "
        "#136); the rest are out of the household model's scope and are "
        "tallied rather than carried."
    ),
    "ratio_or_derived_quantity": (
        "A ratio of two other published quantities (cost per child lifted "
        "out of poverty, a saving as a share of spending, a share of the "
        "tax wedge, retention per pound, entries per day). PolicyEngine "
        "could only 'answer' it by dividing two of its own numbers, which "
        "would make agreement mechanical; the inputs are staged as claims "
        "in their own right where the producer printed them."
    ),
    "share_level_no_registered_metric": (
        "A share of a population at a level (the share of pensioners who "
        "are taxpayers, the share owning a home, a beneficiary share) with "
        "no registered metric and too few rows to mint one deliberately; "
        "deferred rather than mapped to affected_share, which it is not."
    ),
    "parameter_or_threshold_level": (
        "A statutory parameter, threshold or benchmark level (a frozen "
        "threshold's real value, a counterfactual threshold gap, a poverty "
        "line level, a Minimum Income Standard budget, a projection "
        "input): the world's settings, not a score of what the world does "
        "to households. Registered worlds carry these in baselines.py; "
        "MIS budgets are the context lane."
    ),
    "in_kind_series_deferred": (
        "Benefits in kind (public-service spending allocated to "
        "households) are outside the HBAI income concept every other row "
        "uses; the HMT distributional lane (#61) decides how an in-kind "
        "series is carried, and until it does these RF Figure 22 readings "
        "are tallied, not compared."
    ),
    "scheme_average_award_no_metric": (
        "Onward's table of average award per claimant across 25 passported "
        "schemes (broadband tariffs, Cold Weather Payments, ...): an annual "
        "average award per scheme has no registered metric "
        "(average_weekly_benefit and average_monthly_benefit are period-"
        "specific) and the schemes are mostly outside the engine."
    ),
    "mtr_no_registered_metric": (
        "A marginal or effective tax rate CHANGE (or a marginal rate level) "
        "with no registered metric; five rows across two producers do not "
        "justify minting one, and average_tax_rate is a level."
    ),
    "energy_levy_level_no_metric": (
        "The level of policy costs on a household energy bill (an energy "
        "tax per household, a policy cost per household): a level, not the "
        "change energy_bill_change records; two rows, deferred."
    ),
    "republished_twin_merged": (
        "The same statistic printed twice by one producer (a figure and its "
        "companion table, or two figures sharing a row): one claim, two "
        "artifacts. merge_republications keeps the more precise rendering "
        "and records the twin under publication.also_published; a pair that "
        "disagrees beyond rounding raises instead of merging."
    ),
    "no_registered_metric": (
        "A published quantity that fits no registered metric and recurs "
        "once (a caseload change in children, a count of homes freed up, "
        "a share of property sales over GBP 2m): tallied and deferred "
        "rather than forced onto a near-neighbour."
    ),
}

# proposed metric -> drop reason key, for proposals that are never claims
_DROP_BY_NAME: dict[str, str] = {
    "costing_uncertainty_rating": "categorical_rating_not_a_value",
    "behavioural_parameter": "assumption_or_base_not_a_score",
    "projection_input_assumption": "parameter_or_threshold_level",
    "income_component_change": "parameter_or_threshold_level",
    "tax_threshold_level": "parameter_or_threshold_level",
    "threshold_real_value_change": "parameter_or_threshold_level",
    "threshold_real_value": "parameter_or_threshold_level",
    "threshold_real_rise_reversed_share": "parameter_or_threshold_level",
    "counterfactual_threshold_gap": "parameter_or_threshold_level",
    "poverty_line_level": "parameter_or_threshold_level",
    "taxable_savings_balance_threshold": "parameter_or_threshold_level",
    "threshold_salary": "parameter_or_threshold_level",
    "threshold_savings": "parameter_or_threshold_level",
    "break_even_income": "parameter_or_threshold_level",
    "nics_saving_cap": "parameter_or_threshold_level",
    "revenue_neutral_allowance": "parameter_or_threshold_level",
    "benefit_rate_real_change": "parameter_or_threshold_level",
    "minimum_cost_of_education": "parameter_or_threshold_level",
    "cost_of_a_child_to_18": "parameter_or_threshold_level",
    "mis_cost_coverage_share": "parameter_or_threshold_level",
    "mis_weekly_shortfall": "parameter_or_threshold_level",
    "scheme_count": "unit_no_household_concept",
    "measure_count": "unit_no_household_concept",
    "weekly_hours_at_minimum_wage_to_pay_income_tax": "unit_no_household_concept",
    "motoring_externality_cost": "unit_no_household_concept",
    "debt_outcome_percentile_covered": "unit_no_household_concept",
    "bank_rate_level": "macro_fiscal_or_out_of_scope",
    # uk_macro_calls (tranche 4): forecast LEVELS and forecast revisions the
    # houses print beside their calls on the package (#55 answers the calls;
    # the levels are context)
    "gdp_growth": "macro_fiscal_or_out_of_scope",
    "cpi_inflation": "macro_fiscal_or_out_of_scope",
    "unemployment_rate": "macro_fiscal_or_out_of_scope",
    "output_gap": "macro_fiscal_or_out_of_scope",
    "gilt_yield_10y": "macro_fiscal_or_out_of_scope",
    "bank_rate_change": "macro_fiscal_or_out_of_scope",
    "gilt_remit_revision": "macro_fiscal_or_out_of_scope",
    "fiscal_impulse": "macro_fiscal_or_out_of_scope",
    "current_budget_balance_contribution": "macro_fiscal_or_out_of_scope",
    "debt_interest_change": "macro_fiscal_or_out_of_scope",
    "forecast_nominal_gdp_change": "macro_fiscal_or_out_of_scope",
    "forecast_employment_change": "macro_fiscal_or_out_of_scope",
    "forecast_participation_rate_change": "macro_fiscal_or_out_of_scope",
    "psnd_share_of_gdp": "macro_fiscal_or_out_of_scope",
    "psnfl_share_of_gdp": "macro_fiscal_or_out_of_scope",
    "debt_ratio_effect": "macro_fiscal_or_out_of_scope",
    "forecast_spending_change": "macro_fiscal_or_out_of_scope",
    "forecast_borrowing_change": "macro_fiscal_or_out_of_scope",
    "forecast_revenue_change": "macro_fiscal_or_out_of_scope",
    "revenue_level": "macro_fiscal_or_out_of_scope",
    # UKMOD WP 3/26 fiscal overview: total revenue / expenditure LEVELS of
    # the baseline and reform worlds (the changes are staged)
    "government_revenue": "macro_fiscal_or_out_of_scope",
    "government_expenditure": "macro_fiscal_or_out_of_scope",
    "fiscal_consolidation_requirement": "macro_fiscal_or_out_of_scope",
    "policy_change_vs_previous_government_plans": "macro_fiscal_or_out_of_scope",
    "fiscal_gap": "macro_fiscal_or_out_of_scope",
    "share_of_gdp": "macro_fiscal_or_out_of_scope",
    "spending_share_of_headroom_increase": "macro_fiscal_or_out_of_scope",
    "backloading_share": "macro_fiscal_or_out_of_scope",
    "cuts_relative_to_austerity_average": "macro_fiscal_or_out_of_scope",
    "real_spending_change_per_person": "macro_fiscal_or_out_of_scope",
    "departmental_spending_change": "macro_fiscal_or_out_of_scope",
    "central_bank_loss_transfer": "macro_fiscal_or_out_of_scope",
    "net_fiscal_benefit": "macro_fiscal_or_out_of_scope",
    "fiscal_and_economic_benefit": "macro_fiscal_or_out_of_scope",
    "investment_change": "macro_fiscal_or_out_of_scope",
    "compliance_cost": "macro_fiscal_or_out_of_scope",
    "excess_cash_savings": "macro_fiscal_or_out_of_scope",
    "retailer_windfall": "macro_fiscal_or_out_of_scope",
    "energy_policy_costs_total": "macro_fiscal_or_out_of_scope",
    "aggregate_household_saving": "macro_fiscal_or_out_of_scope",
    "gross_earnings_change": "macro_fiscal_or_out_of_scope",
    "vehicle_sales_change": "macro_fiscal_or_out_of_scope",
    "property_value_change": "macro_fiscal_or_out_of_scope",
    "house_price_level_effect": "macro_fiscal_or_out_of_scope",
    "rent_level_effect": "macro_fiscal_or_out_of_scope",
    "estimation_error_share": "macro_fiscal_or_out_of_scope",
    "congestion_cost_share": "macro_fiscal_or_out_of_scope",
    "modelling_coverage_share": "macro_fiscal_or_out_of_scope",
    "block_grant_effect": "macro_fiscal_or_out_of_scope",
    "net_devolved_saving": "macro_fiscal_or_out_of_scope",
    "employer_cost_per_employee_change": "macro_fiscal_or_out_of_scope",
    "average_charge_per_vehicle": "macro_fiscal_or_out_of_scope",
    "cost_per_child_lifted_out_of_poverty": "ratio_or_derived_quantity",
    "cost_per_child_gaining": "ratio_or_derived_quantity",
    "poverty_entries_per_day": "ratio_or_derived_quantity",
    "median_energy_bill_saving_share_of_spending": "ratio_or_derived_quantity",
    "bill_saving_share_of_spending": "ratio_or_derived_quantity",
    "council_tax_share_of_income": "ratio_or_derived_quantity",
    "average_loss_share_of_disposable_income": "ratio_or_derived_quantity",
    "tax_wedge_gap_ratio": "ratio_or_derived_quantity",
    "ni_share_of_tax_wedge": "ratio_or_derived_quantity",
    "income_growth_contribution_share": "ratio_or_derived_quantity",
    "real_value_recovery_share": "ratio_or_derived_quantity",
    "offset_share_of_long_run_fuel_duty_loss": "ratio_or_derived_quantity",
    "living_standards_decline_offset_share": "ratio_or_derived_quantity",
    "electricity_share_of_savings": "ratio_or_derived_quantity",
    "energy_burden_share": "ratio_or_derived_quantity",
    "marginal_retention_per_pound_earned": "ratio_or_derived_quantity",
    "retention_rate": "ratio_or_derived_quantity",
    "poverty_rate_gap": "ratio_or_derived_quantity",
    "poverty_rate_headroom": "ratio_or_derived_quantity",
    "real_income_growth_difference": "ratio_or_derived_quantity",
    "taxpayer_share": "share_level_no_registered_metric",
    "share_of_property_sales_over_2m": "share_level_no_registered_metric",
    "ownership_share": "share_level_no_registered_metric",
    "beneficiary_share": "share_level_no_registered_metric",
    "support_lost_share": "share_level_no_registered_metric",
    "food_parcel_share": "share_level_no_registered_metric",
    "in_kind_benefit_change": "in_kind_series_deferred",
    "in_kind_benefit_share_of_income": "in_kind_series_deferred",
    "average_award": "scheme_average_award_no_metric",
    "marginal_tax_rate": "mtr_no_registered_metric",
    # UKMOD WP 3/26: per-capita net fiscal impact (net impact / population),
    # the S80/S20 ratio and its change, and the Gini change — derived from
    # or ratios of quantities that are staged as levels
    "net_fiscal_impact_per_capita": "ratio_or_derived_quantity",
    "s80_s20_ratio": "ratio_or_derived_quantity",
    "s80_s20_ratio_change": "ratio_or_derived_quantity",
    "gini_coefficient_change": "ratio_or_derived_quantity",
    "effective_tax_rate_change": "mtr_no_registered_metric",
    "marginal_effective_tax_rate_change": "mtr_no_registered_metric",
    "energy_tax_per_household": "energy_levy_level_no_metric",
    "energy_policy_cost_per_household": "energy_levy_level_no_metric",
    "caseload_change": "no_registered_metric",
    "homes_freed_up": "no_registered_metric",
    # single-case quantities that only ever appear on specimen rows; the
    # specimen check drops them first, this entry catches a stray one
    "take_home_pay": "mode3_specimen_household",
    "take_home_pay_change": "mode3_specimen_household",
    "household_income_tax_bill": "mode3_specimen_household",
    "household_post_rent_income": "mode3_specimen_household",
    "employee_nics": "mode3_specimen_household",
    "pension_pot_projection": "mode3_specimen_household",
}

_ADOPTED = frozenset(DISPOSITIONS)
_DROPPED = frozenset(_DROP_BY_NAME)
assert not (_ADOPTED & _DROPPED), "a metric is adopted or dropped, never both"
assert set(_DROP_BY_NAME.values()) <= set(DROPS), "every drop key has a reason"

# Proposed units that are never a claim's unit (tallied by reason)
_UNIT_DROPS: dict[str, str] = {
    "rating_category": "categorical_rating_not_a_value",
    "elasticity": "assumption_or_base_not_a_score",
    "years": "assumption_or_base_not_a_score",
    "cars": "assumption_or_base_not_a_score",
    "vehicles": "assumption_or_base_not_a_score",
    "miles_per_car_per_year": "assumption_or_base_not_a_score",
    "transactions": "assumption_or_base_not_a_score",
    "transactions_per_year": "assumption_or_base_not_a_score",
    "businesses": "unit_no_household_concept",
    "uc_child_elements": "unit_no_household_concept",
    "ctr_schemes": "unit_no_household_concept",
    "claims": "unit_no_household_concept",
    "measures": "unit_no_household_concept",
    "hours_per_week": "unit_no_household_concept",
    "pence_per_km": "unit_no_household_concept",
    "percentile": "unit_no_household_concept",
    "average_hours_equivalent": "unit_no_household_concept",
    "percent_of_gdp": "macro_fiscal_or_out_of_scope",
}

# Staged unit label -> DB unit concept. Closed: an unregistered unit raises.
UNITS: dict[str, UnitConcept] = {
    **{u.value: u for u in UnitConcept},
    "dwellings": UnitConcept.PROPERTIES,
}

TIME_BASES = {
    "annual": TimeBasis.ANNUAL,
    "fiscal_year": TimeBasis.FISCAL_YEAR,
    "point_in_time": TimeBasis.POINT_IN_TIME,
}

# Rows whose conditions name a single household are specimens, not
# population statistics, when the quantity is a household-level one.
_SPECIMEN_KEYS = frozenset(
    {"household_type", "household", "employment_income", "existing_pension_pot"}
)
_SPECIMEN_METRICS = frozenset(
    {
        "household_income_change",
        "household_tax_change",
        "employee_tax_liability_change",
        "employer_nics_change",
        "employee_nics",
        "household_income_tax_bill",
        "household_post_rent_income",
        "take_home_pay",
        "take_home_pay_change",
        "pension_pot_projection",
        "effective_tax_rate",
        "real_income_change",
        "real_purchasing_power_change",
        "discretionary_income_change",
        "break_even_income",
        "nics_saving_cap",
        "threshold_salary",
        "average_tax_change",
        "average_annual_gain",
    }
)

# Staged fields this module understands (the README row contract). An
# unknown field raises: a new harvest column is handled here deliberately.
_KNOWN_FIELDS = frozenset(
    {
        "attribution",
        "baseline_policy",
        "benchmark_class",
        "conditions",
        "local_artifact",
        "measure_key",
        "metric",
        "normalization",
        "note",
        "parse_confidence",
        "period",
        "proposed_baseline",
        "proposed_metric",
        "proposed_unit",
        "publication",
        "quote",
        "reform_hint",
        "source",
        "source_column",
        "source_model",
        "source_table",
        "status",
        "time_basis",
        "unit_concept",
        "value",
        "value_kind",
        "value_raw",
    }
)

# Condition keys whose values are closed identities (uk_aliases). program
# is canonicalised only where the producer's value is a registered slug;
# a prose programme label travels verbatim as program_verbatim, so the
# indexed `program` column never holds an unregistered value.
_CANONICALISED = ("geography", "income_group")

# A producer's own world, quoted in the staging as `proposed_baseline`,
# maps to the label registered for it in baselines.py by its opening words
# (quotes normalised; the full quote stays on the claim as
# conditions.counterfactual). Closed: an unlisted definition raises (the
# #13 rule: no row keyed to an unnamed world lands).
_PROPOSED_BASELINE_PREFIXES: dict[str, str] = {
    "the previous Government's spending plans (Spring 2024)": "rf_previous_government_spending_plans_spring_2024",
    "thresholds uprated in line with inflation (Box 3.3": "obr_box_3_3_thresholds_indexed_with_inflation",
    "IHT thresholds increased with CPI": "hmrc_tiin_iht_thresholds_cpi_indexed",
    "thresholds indexed with CPI from 2028 to 2029 onwards": "hmrc_tiin_thresholds_cpi_indexed_from_2028_29",
    "fuel duty rates uprated in line with RPI inflation since 2010-11": "obr_fuel_duty_rpi_uprated_since_2010_11",
    "RF case-study counterfactual: policy before the key measures announced since Autumn Budget 2024": "rf_case_study_counterfactual_pre_ab2024_measures",
    "WPI Economics projection of hunger and hardship to 2026/27": "wpi_hunger_and_hardship_projection_2026_27",
    "JRF post-Budget projection: current policy after Autumn Budget 2025 on the OBR November 2025 EFO central": "jrf_post_ab2025_projection_obr_nov2025_central",
    "RF 'current policy' projection at 30 Oct 2025": "rf_current_policy_projection_2025_10_30",
    "JRF post-Budget projection path: Autumn Budget 2025 policy on the OBR November 2025 forecast": "jrf_post_ab2025_projection_path_nov_to_nov",
    "IFS 'no freezes at all' world": "ifs_no_freezes_april_2021_thresholds_uprated",
    "JRF post-Spring-Forecast-2026 projection path": "jrf_post_spring_forecast_2026_projection_path",
    "RF projection without the Child Poverty Strategy policies": "rf_projection_without_child_poverty_strategy",
    "JRF post-Budget projection path with the two-child limit retained": "jrf_post_ab2025_two_child_limit_retained",
    "NIESR pre-measures forecast (Autumn 2025 Outlook, completed 27 Oct 2025)": "niesr_pre_measures_autumn_2025_outlook",
}


def _normalise_quotes(text: str) -> str:
    return (
        text.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


_BASELINE_BY_LABEL: dict[str, dict] = {label: desc for desc, label, *_ in BASELINES}


def _registry() -> dict[str, dict]:
    reg = json.loads(REGISTRY_PATH.read_text())
    return {m["measure_key"]: m for m in reg["measures"]}


REGISTRY = _registry()
BUNDLE = json.loads(BUNDLE_PATH.read_text())
ENGINE_PIN = BUNDLE["compatible_model_packages"][0]["specifier"].lstrip("=")


def _load(family: str) -> list[dict]:
    path = HARVEST / family / "claims_staged.jsonl.gz"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — the harvest family is not vendored")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != CLAIMS_SHA256[family]:
        raise ValueError(
            f"{family}: claims_staged.jsonl.gz sha256 {digest[:12]} != pinned "
            f"{CLAIMS_SHA256[family][:12]} — the vendored file changed; "
            "re-pin COUNTS.json deliberately"
        )
    rows = []
    for line in gzip.open(path, "rt"):
        row = json.loads(line)
        unknown = sorted(set(row) - _KNOWN_FIELDS)
        if unknown:
            raise ValueError(
                f"{family}: unhandled staged fields {unknown} — handle them "
                "deliberately or not at all"
            )
        rows.append(row)
    return rows


def _metric_name(row: dict) -> str:
    name = row.get("metric") or row.get("proposed_metric")
    if not name:
        raise ValueError(
            f"staged row carries neither metric nor proposed_metric: "
            f"{row.get('source_column')!r}"
        )
    return name


def _baseline(row: dict, source: str) -> dict | None:
    """The world the row is scored against, as a registered descriptor."""
    label = row.get("baseline_policy")
    proposed = row.get("proposed_baseline")
    if label and proposed:
        raise ValueError(f"{source}: both baseline_policy and proposed_baseline set")
    if proposed:
        label = None
        text = _normalise_quotes(proposed)
        for prefix, lab in _PROPOSED_BASELINE_PREFIXES.items():
            if text.startswith(_normalise_quotes(prefix)):
                label = lab
                break
        if label is None:
            raise ValueError(
                f"{source}: proposed_baseline is not a registered world: "
                f"{proposed[:100]!r} — register it in baselines.py and map it "
                "here (#13), never default to current law"
            )
    if not label:
        return None
    if label not in _BASELINE_BY_LABEL:
        raise ValueError(
            f"{source}: baseline label {label!r} is not registered in baselines.py"
        )
    return _BASELINE_BY_LABEL[label]


def _reform(row: dict, source: str, baseline: dict | None) -> ReformRef:
    """The world the row scores.

    A row keyed to a registry measure names that measure as its policy
    slug, so every producer's rows on one measure share a reform key; an
    unkeyed reform score keeps the producer's own words; a row with no
    reform_hint is a level or projection of the (baseline) world.
    """
    key = row.get("measure_key")
    hint = row.get("reform_hint")
    if key:
        return policy_ref(key, baseline=baseline)
    if hint:
        return policy_ref(f"{source}:{hint[:120]}", baseline=baseline)
    return ReformRef(baseline=baseline)


def _source_model(source: str, row: dict) -> str:
    """The ENGINE behind a claim (#132), which lives on the CLAIM.

    A source with a registered engine may declare that engine, a versioned
    spelling of it (``ukmod_b1.13``) or a non-model method the harvest
    verified for that row (``arithmetic``, ``survey_microdata``,
    ``administrative_data``): the IFS publishes TAXBEN output beside plain
    arithmetic on HMRC statistics, and the engines registry says the
    engine belongs on the claim for exactly that reason. What it may NOT
    do is name a DIFFERENT registered engine — that contradicts the
    registry and raises. A versioned spelling must be a release
    ENGINE_RELEASES records for this publisher: one engine at several
    releases is a fact the ledger holds, not one a row may introduce. A
    source without a registered engine must say what produced the number."""
    declared = row.get("source_model")
    engine = engine_of(source)
    if engine is not None and declared in (None, "", source):
        return engine
    if not declared:
        raise ValueError(f"{source}: no source_model declared and no engine registered")
    named, _release = split_release(declared)
    if engine is not None and named in ENGINES and named != engine:
        raise ValueError(
            f"{source}: staged source_model {declared!r} names a different "
            f"engine from the registered {engine!r}"
        )
    if not known_release(source, declared):
        raise ValueError(
            f"{source}: staged source_model {declared!r} names a release that "
            "ENGINE_RELEASES does not record for this publisher — extend the "
            "ledger deliberately rather than letting a row introduce one"
        )
    return declared


def _relationship_kind(source: str) -> str | None:
    return "tiin" if source == "uk_hmrc" else None


def _is_specimen(row: dict, name: str) -> bool:
    cond = row.get("conditions") or {}
    return name in _SPECIMEN_METRICS and any(k in cond for k in _SPECIMEN_KEYS)


def _score(row: dict, family: str, source: str, metric: Metric) -> ExternalScore:
    unit_label = row.get("unit_concept") or row.get("proposed_unit")
    if unit_label not in UNITS:
        raise ValueError(f"{source}: unregistered unit {unit_label!r}")
    unit = UNITS[unit_label]

    staged = dict(row.get("conditions") or {})
    cond: dict[str, str] = {"country": "UK"}
    for key, value in staged.items():
        if key in _CANONICALISED:
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
    # a bound of a published range, a central estimate or a chart reading
    # is part of the claim's identity: the low and high of one range are
    # two claims, not one
    if row.get("value_kind") and row["value_kind"] != "point":
        cond["estimate_kind"] = row["value_kind"]
    if row.get("proposed_metric") == "exchequer_impact_static":
        cond.setdefault("scoring_method", "static")
    if row.get("proposed_metric") == "net_fiscal_impact":
        cond["fiscal_measure"] = "net_fiscal_impact"
    if row.get("proposed_metric") == "tax_base":
        cond["aggregate"] = "tax_base"
    if row.get("reform_hint"):
        cond["reform_hint"] = row["reform_hint"]
    if row.get("proposed_baseline"):
        cond["counterfactual"] = row["proposed_baseline"]
    key = row.get("measure_key")
    if key:
        m = REGISTRY[key]
        cond["measure_key"] = key
        cond["pe_expressibility"] = m["computability"]
        gap = m.get("missing") or m.get("why")
        if gap:
            cond["pe_missing"] = gap
        if m.get("action_link"):
            cond["action_link"] = m["action_link"]
    if metric in MACRO_METRICS:
        cond["pe_expressibility"] = "not_expressible"
        cond["pe_missing"] = MACRO_MISSING
        cond["action_link"] = MACRO_LINK
    if row.get("proposed_metric") in (
        "package_tax_rise_size",
        "package_spending_change",
    ):
        cond["fiscal_measure"] = row["proposed_metric"]

    basis = TIME_BASES.get(row.get("time_basis"))
    if basis is None:
        raise ValueError(f"{source}: unregistered time_basis {row.get('time_basis')!r}")

    baseline = _baseline(row, source)
    reform = _reform(row, source, baseline)
    with_baseline_condition(cond, reform)

    pub = dict(row.get("publication") or {})
    pub.update(
        {
            "registry": REGISTRY_MARK,
            "family": family,
            "table": row.get("source_table"),
            "quote": row.get("quote"),
            "attribution": row["attribution"],
            # every national-grain row reaches the page before a
            # counterpart lands (NZ precedent); constituency-grain rows
            # wait for a constituency view
            "publish_without_result": not _constituency_grain(row),
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
        calibration_relationship=uk_relationship(
            source, metric, kind=_relationship_kind(source)
        )[0],
        source_model=_source_model(source, row),
        source_column=row.get("source_column") or "",
        publication=pub,
        value_kind=row.get("value_kind") or unit.value,
        status="ok",
    )


def _constituency_grain(row: dict) -> bool:
    return row["source"] == "tax_policy_associates" and (
        row.get("conditions") or {}
    ).get("geography") not in (None, "UK", "England", "London")


def stage() -> tuple[list[ExternalScore], dict]:
    """Stage every ingestible row; nothing touches the DB here.

    Returns (scores, accounting) where accounting reconciles EVERY staged
    row per family: read = ingested + dropped, by reason.
    """
    scores: list[ExternalScore] = []
    acct = {"read": 0, "ingested": 0, "dropped": 0, "by_family": {}, "drops": {}}
    for family, (lane, sources) in FAMILIES.items():
        rows = _load(family)
        fam = {"read": len(rows), "ingested": 0, "dropped": 0, "lane": lane}
        acct["read"] += len(rows)
        for row in rows:
            source = row["source"]
            if source not in sources:
                raise ValueError(
                    f"{family}: row source {source!r} is not in {sorted(sources)}"
                )
            name = _metric_name(row)
            # attribution BEFORE the metric disposition: a re-published
            # figure cannot smuggle itself in on a registered metric
            if row["attribution"] == "restated":
                _drop(acct, fam, "restated_official_figure")
                continue
            if family == "uk_cases_commercial":
                _drop(acct, fam, "mode3_worked_example")
                continue
            if row.get("value_kind") == "categorical":
                _drop(acct, fam, "categorical_rating_not_a_value")
                continue
            if _is_specimen(row, name):
                _drop(acct, fam, "mode3_specimen_household")
                continue
            if name in _DROP_BY_NAME:
                _drop(acct, fam, _DROP_BY_NAME[name])
                continue
            unit_label = row.get("unit_concept") or row.get("proposed_unit")
            if unit_label in _UNIT_DROPS:
                _drop(acct, fam, _UNIT_DROPS[unit_label])
                continue
            if name not in DISPOSITIONS:
                raise ValueError(
                    f"{family}: metric {name!r} has no disposition — decide it "
                    "in DISPOSITIONS or _DROP_BY_NAME deliberately; a proposal "
                    "is not a decision"
                )
            metric = DISPOSITIONS[name]
            # WPI's severe-hardship rate is a poverty RATE change; the
            # count is a count change
            if name == "severe_hardship_count_change" and unit_label == "percent":
                metric = Metric.POVERTY_RATE_CHANGE
            scores.append(_score(row, family, source, metric))
            fam["ingested"] += 1
            acct["ingested"] += 1
        acct["by_family"][family] = fam
    # The same statistic printed twice by one producer (a figure and its
    # companion table, two figures sharing a row) is ONE claim, two
    # artifacts: merge_republications keeps the more precise rendering,
    # records the twin under publication.also_published, and raises when
    # the pair disagrees beyond rounding. Merged twins are tallied.
    merged: list[ExternalScore] = []
    for source in sorted({s.source for s in scores}):
        mine = [s for s in scores if s.source == source]
        kept = merge_republications(
            mine,
            source,
            precision=lambda s: len(s.conditions.get("value_verbatim", "")),
            tolerance=lambda s: max(abs(s.value) * 0.005, 1e-9),
        )
        twins = len(mine) - len(kept)
        if twins:
            fam_of = {s.claim_id(): s.publication["family"] for s in mine}
            kept_ids = {s.claim_id() for s in kept}
            for s in mine:
                if s.claim_id() in kept_ids and s is not next(
                    k for k in kept if k.claim_id() == s.claim_id()
                ):
                    fam = acct["by_family"][fam_of[s.claim_id()]]
                    _drop(acct, fam, "republished_twin_merged")
                    acct["ingested"] -= 1
                    fam["ingested"] -= 1
        merged.extend(kept)
    acct["dropped"] = acct["read"] - acct["ingested"]
    if acct["ingested"] + acct["dropped"] != acct["read"]:  # pragma: no cover
        raise ValueError("accounting does not close")
    return finish(merged, REGISTRY_MARK), acct


def _drop(acct: dict, fam: dict, reason_key: str) -> None:
    entry = acct["drops"].setdefault(
        reason_key, {"rows": 0, "reason": DROPS[reason_key]}
    )
    entry["rows"] += 1
    fam["dropped"] += 1
    fam.setdefault("drops", {})
    fam["drops"][reason_key] = fam["drops"].get(reason_key, 0) + 1


# Exact accounting for the committed harvest. A drifted re-stage must fail
# HERE, never grow or shrink the catalog silently. Pinned from the first
# staging on 2026-09-24; a family that is deliberately re-staged changes
# its line here in the same commit.
_EXPECTED_PATH = Path(__file__).parent / "ingest_uk_ab2025_expected.json"


def expected() -> dict:
    return json.loads(_EXPECTED_PATH.read_text())


def check_accounting(acct: dict) -> None:
    _EXPECTED = expected()
    got = {
        "read": acct["read"],
        "ingested": acct["ingested"],
        "dropped": acct["dropped"],
        "by_family": {
            fam: {"read": v["read"], "ingested": v["ingested"], "dropped": v["dropped"]}
            for fam, v in acct["by_family"].items()
        },
        "drops": {k: v["rows"] for k, v in acct["drops"].items()},
    }
    if got != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {got} != {_EXPECTED}")


ALL_SOURCES = frozenset(s for _, srcs in FAMILIES.values() for s in srcs)


def ingest(db_path: Path) -> dict:
    """Stage and validate first; then ONE transaction replaces every
    AB2025 claim wholesale (by registry mark, never by source: ifs,
    resolution_foundation, hm_treasury and uk_hmrc also carry other
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
            stage_ = "ingested" if ing else "cataloged"
            detail = (
                f"{ing} claims from {len(fams)} families ({read} staged rows = "
                f"{ing} ingested + {read - ing} tallied drops)"
            )
            db.conn.execute(LANE_SQL, (lane, stage_, detail, LANE_UPDATED))
    sync_lane_feed(db, REPO / "data" / "lanes.json", FEED_UPDATED, lanes=LANES)
    db.close()
    return {
        "claims": len(rows),
        "read": acct["read"],
        "ingested": acct["ingested"],
        "dropped": acct["dropped"],
        "drops": {k: v["rows"] for k, v in acct["drops"].items()},
    }


# --- lanes after the counterpart run (#136 tranche 3) -------------------------


def advance_lanes(db_path: Path, feed_path: Path | None = None) -> dict:
    """Move each AB2025 lane whose claims now carry a computed PolicyEngine
    counterpart (a comparable or constructed result) from ``ingested`` to
    ``computed``, naming how many claims are answered. A lane with no
    counterpart yet keeps its stage; nothing here creates or removes a
    lane, and the pe_gap verdict rows do not count as counterparts."""
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
            detail = f"{base} — {answered} claims with a PolicyEngine counterpart on the certified bundle"
            db.conn.execute(LANE_SQL, (lane, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db, feed_path or REPO / "data" / "lanes.json", FEED_UPDATED, lanes=LANES
    )
    db.close()
    return out


# --- pe_gap verdicts ----------------------------------------------------------


def verdict_rows(db: ScorecardDB) -> tuple[list[tuple], list[tuple]]:
    """One pe_gap result and one pe_gap diagnosis per AB2025 claim whose
    measure the certified engine cannot express, from the registry."""
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
        if c["metric"] in {m.value for m in MACRO_METRICS}:
            # the claim's own verdict (#55): no registry lever exists for a
            # macro-fiscal quantity, whatever measure it is keyed to
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
                    data_bundle=BUNDLE["revision"],
                    pe_construction=f"pe_gap:not_expressible:{gap_key}",
                    run_id=VERDICT_RUN_ID,
                    computed_at=VERDICT_COMPUTED_AT,
                    annotations=[
                        m["why"],
                        m["name_search"],
                        "no run executed: the verdict is the registry's, stated "
                        f"against the certified engine {ENGINE_PIN}",
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
