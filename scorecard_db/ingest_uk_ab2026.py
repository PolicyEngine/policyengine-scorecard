"""Ingest every Autumn Budget 2026 score (#230).

We stage 5,959 rows in ``sources/harvest-uk-ab2026-2026-10-29/`` from 12
families: HM Treasury's tables, costings and red book, the OBR's
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

The AB2026 ingest adds six steps:

1. **Keys.** We stage a keyed row under an AB2026 key, or for a Table 6.4
   recosting under the earlier event's key named in
   ``conditions.recosting_of``. We keep keyless quantities where no producer
   identifies one measure. The ingest gives a recosting no registry verdict,
   since we assessed AB2025's registry at policyengine-uk 2.89.2 and run
   AB2026's counterparts at 2.151.0.
2. **Dispositions.** We decide the 66 metric names AB2025's tables don't
   hold in ``DISPOSITIONS_AB2026`` and ``DROP_BY_NAME_AB2026`` (2 adoptions
   and 64 drops). Table 6.2's ``financial_transaction_cash_impact`` lands on
   ``cash_requirement_change``, the PSNCR metric ``models.py`` keeps apart
   from PSNB.
3. **Shares of GDP.** We put a ``percent`` row with a GDP denominator (IFS's)
   on the OBR's and TPA's ``percent_of_gdp``, which AB2025 drops as
   macro-fiscal.
4. **Figures a producer prints more than once.** HM Treasury repeats 408
   Table 6.1 cells in the costings and 24 in red book Table 6.3 and its
   prose. We keep the Table 6.1 or 6.2 claim, list each repetition under
   ``publication.also_printed_in`` and tally it. We match a repetition by
   key, staged metric, unit, year and value. We also record nine reviewed red
   book printings in ``REVIEWED_TWINS``, where HM Treasury repeats a cell with
   the opposite sign, a rounding or another year. In ``REPEATED_PRINTINGS``
   we merge 176 more rows on which a producer prints a figure it prints
   elsewhere: in the same family, or for 60 rows of HM Treasury's costings,
   in red book Table 6.3. We keep the most precise printing, and a point
   value over a bound.
5. **Row calls.** We move IFS row 46 to another metric in ``ROW_METRICS``,
   give it a per-household unit in ``ROW_UNITS``, and tally 22 rows under six
   reasons in ``ROW_DROPS``. In ``ROW_TIME_BASES`` we give three red book
   rows the time basis on which we stage another printing of their figure.
   With each entry we record the staged value we expect on that row.
6. **Lanes.** We add three lanes: official, microsimulation, and
   administrative data and other producers. ``advance_lanes`` moves a lane to
   ``computed`` once its claims have counterparts, which
   ``pipeline/stage_uk_ab2026.py`` stages from the dashboard's Budget-day
   artifacts (tranche 3) under ``STAGED_COUNTERPARTS``.

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_uk_ab2026 data/scorecard.db
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import re
from pathlib import Path

from . import ingest_uk_ab2025 as AB25
from . import signs
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
        "costings or Budget document, sometimes rounded or with the opposite "
        "sign. We score the table figure and list this printing with it."
    ),
    "figure_printed_again": (
        "The producer prints this figure more than once: in prose and in a "
        "table, a chart or its workbook, in two tables, or in two of its "
        "documents. It sometimes rounds or bounds the figure, or gives it the "
        "opposite sign. We score its most precise printing, and a point value "
        "over a bound, and list this one with it."
    ),
    "energy_bill_level_no_metric": (
        "The producer gives the level of a typical household's energy bill "
        "under the price cap (RF's £2,210, for example), and we score changes "
        "in bills, so a level has nothing to compare."
    ),
    "partial_year_household_support": (
        "IFS gives average support from the Budget's energy and fuel measures "
        "over October 2026 to June 2027. We score annual income changes, so we "
        "tally these partial-year figures."
    ),
    "restated_obr_forecast": (
        "Resolution Foundation computes the cost of continuing the fuel duty "
        "freeze from two OBR forecasts, the constant-duty-rate receipts less "
        "the central receipts. We keep the OBR's own figures: its effect on "
        "borrowing in 2029-30 (paragraph 3.43) and its average cut in receipts "
        "from 2027-28 to 2031-32 (paragraph 4.30)."
    ),
    "income_path_not_a_policy_effect": (
        "Resolution Foundation gives the change in real household incomes, per "
        "person or for a typical household, over a period in pounds, with no "
        "reform to compare against, and we score income paths only as "
        "percentage growth."
    ),
    "earlier_estimate_restated": (
        "CenTax restates the revenue gain it estimated in 2024 from taxing "
        "capital gains at income tax rates, an estimate of an earlier event "
        "rather than of this Budget."
    ),
    "no_registered_metric": (
        "The producer publishes a quantity that fits no registered metric, "
        "such as a gain summed over several years per driver or per business, "
        "or a change in the supply of homes, and we tally it."
    ),
    "mtr_no_registered_metric": (
        "The producer gives a marginal tax rate, and we register a metric only "
        "for average rates, average_tax_rate."
    ),
    "single_row_unregistered_world": (
        "The OBR compares this figure with a world it describes once: its "
        "uprating rules over 1990-2025 outturn or its CPI bound against fuel "
        "duty policy. We compare against worlds we can rebuild or current law."
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
    # IFS's support per household over October 2026 to June 2027, apart from
    # row 46, which we adopt through ROW_METRICS
    "average_household_support": "partial_year_household_support",
}

DISPOSITIONS: dict[str, Metric] = {**AB25.DISPOSITIONS, **DISPOSITIONS_AB2026}
# AB2025's restatement reason says we stage the originator's rows in the same
# harvest. In AB2026 we don't always: in its costings, HM Treasury restates
# HMRC's tax gap (rows 233 and 234), and we stage no HMRC family.
_RESTATED_AB2026 = (
    "The producer repeats another body's figure (the OBR's, HM Treasury's, "
    "HMRC's or another producer's), and we credit the estimate to that body "
    "and tally this repetition."
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
    ("uk_ifs_ab2026", 46): (
        "average_household_support",
        "£80",
        Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
        "IFS averages January 2027's one-off Household Energy Payment across "
        "households in England. The whole payment falls in 2026-27, so the "
        "figure needs no annualising.",
    ),
}

# (family, row) -> the unit the ingest stores in place of the staged one, for a
# row we reassign through ROW_METRICS. We stage IFS row 46 in gbp; we distinguish
# per-household averages from totals in models.py.
ROW_UNITS: dict[tuple[str, int], str] = {("uk_ifs_ab2026", 46): "gbp_per_household"}
assert set(ROW_UNITS) <= set(ROW_METRICS)

# (family, row) -> (staged time basis, staged value_raw, the time basis the
# ingest stores, why). HM Treasury prints each of these figures on another row,
# where we stage it on the other basis, and we merge the two printings in
# REPEATED_PRINTINGS.
_ANNUAL_CAP = (
    "HM Treasury expects the government to take around £50 off the annual Ofgem "
    "price cap in April 2027 by extending the VAT cut, a saving we stage as "
    "annual on rows 188, 190 and 197."
)
_PAID_IN_JANUARY = (
    "HM Treasury counts up to 20 million households that the government pays "
    "the Household Energy Payment from January 2027, a count we stage at that "
    "point in time on row 7."
)
ROW_TIME_BASES: dict[tuple[str, int], tuple[str, str, str, str]] = {
    ("uk_hmt_redbook", 5): ("point_in_time", "around £50", "annual", _ANNUAL_CAP),
    ("uk_hmt_redbook", 180): (
        "annual",
        "20 million",
        "point_in_time",
        _PAID_IN_JANUARY,
    ),
    ("uk_hmt_redbook", 189): (
        "annual",
        "20 million",
        "point_in_time",
        _PAID_IN_JANUARY,
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
    # RF computes its continued fuel duty freeze as the OBR's constant-duty-
    # rate forecast less its central forecast (our notes to RF's rows 154 and
    # 397-401, citing its footnote 27), so we keep only the OBR's row 2740
    ("uk_rf_ab2026", 154): ("£4.3 billion", "restated_obr_forecast"),
    ("uk_rf_ab2026", 397): ("-2.3483484846542702", "restated_obr_forecast"),
    ("uk_rf_ab2026", 398): ("-3.7389555211291317", "restated_obr_forecast"),
    ("uk_rf_ab2026", 399): ("-4.2893363032056087", "restated_obr_forecast"),
    ("uk_rf_ab2026", 400): ("-4.6757828023106249", "restated_obr_forecast"),
    ("uk_rf_ab2026", 401): ("-4.8671109188223411", "restated_obr_forecast"),
    # RF's income paths, with no reform and baseline
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
    # the OBR's costings of a continued fuel duty freeze (paragraphs 3.43, 4.30)
    "OBR October 2026 forecast, on the assumption that the latest policy is implemented": "obr_october_2026_budget_forecast__policy_parameters",
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
# that decides it. The ingest raises if the two rows' keys differ, if their
# magnitudes differ by more than half the red book's last printed digit, or if
# their years differ anywhere but Ukraine's three rows (_ANNOUNCEMENT_YEARS).
_HEP = (
    "HM Treasury prints the Household Energy Payment's 2026-27 cost in the red "
    "book as £2.6 billion, a positive cost, and in Table 6.1 line 1 as -2,625 "
    "(£ million). £2.6 billion rounds -2,625 once we normalise the sign."
)
_SPR = (
    "HM Treasury prints Small Producer Relief's support in the red book as £10 "
    "million a year, a positive cost, and in Table 6.1 line 19 as -10 (£ million) "
    "for 2027-28, the year we stage on both rows."
)
_BOOKS = (
    "HM Treasury prints up to £5 million a year for books for young children "
    "in the red book, a positive cost, and -5 (£ million) in Table 6.1 line 9 "
    "for 2027-28, the year we stage on both rows. HM Treasury dates the prose "
    "support's three years from 2027-28 and the table's from 2026-27; the "
    "2027-28 amount agrees."
)
_UKRAINE = (
    "HM Treasury prints £500 million of military support for Ukraine's air "
    'defences "this winter" in the red book, a positive cost, and -500 '
    "(£ million) in Table 6.1 line 43 in 2026-27. HM Treasury names no fiscal "
    "year in the red book, so we stage the 2026 announcement year on the row "
    "and match the figure to the table's 2026-27 cell."
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
# (family, row) -> (the row's period, its uk_hmt_tables row, that row's period)
# for the rows on which we stage an announcement year.
_ANNOUNCEMENT_YEARS: dict[tuple[str, int], tuple[int, int, int]] = {
    ("uk_hmt_redbook", i): (2026, 252, 2027) for i in (263, 271, 272)
}

# Rows on which a producer prints a figure it prints elsewhere: in prose and in
# a table, a chart or the chart's workbook, in two tables, or in two of its
# documents. We map each (family, row) to the row whose claim we keep, and to
# our reading of the pair. We name the kept row's family where it differs from
# the repeat's, as for HM Treasury's costings and red book. The ingest raises
# if the two claims differ in key, metric, unit, year or time basis, or if the
# producer costs part of a measure in one and the whole measure in the other.
# It also raises if they differ in any condition outside ``_PER_PRINTING``,
# such as geography, population or scenario, unless we list the two wordings
# for that repeat in ``_SAME_READING``. Of two point values we keep the more
# precise, and the ingest raises if we keep the coarser, or if they differ by
# more than half the coarser printing's last digit. It also raises if they
# differ in estimate kind, as when the producer sums several years in one
# printing and gives one year in the other. Where the producer states each
# printing's sign convention, it compares the values in PolicyEngine's
# orientation, and otherwise it compares their magnitudes. Where a producer
# bounds a figure that it prints elsewhere as a point value, we keep the point
# value, and the ingest raises if we keep the bound. It compares the producer's
# own values, and raises if the two printings differ in sign convention, or if
# the point value lies more than half its last digit outside the bound. It also
# raises on two bounds of opposite directions.
_CENTAX_640 = (
    "CenTax prints the £640 million cost of removing the £100,000 childcare "
    "threshold in two documents: the key findings of Taxes at the top, and "
    "its reaction to the Budget."
)
_CENTAX_197 = (
    "CenTax estimates that the government would raise £19.7 billion in 2030 "
    "if it reformed capital gains tax and taxed gains at income tax rates. "
    "CenTax prints the estimate in the key findings of Taxes at the top, and "
    "again in footnote 9 of its Unicorn Relief paper."
)
_CENTAX_14 = (
    "CenTax prints its 2024 estimate, £14 billion in 2026, in section 3.1 of "
    "Taxes at the top, and again in footnote 9 of its Unicorn Relief paper."
)
_CENTAX_TABLE = "CenTax rounds Table 1's shares in the text of section 3.2."
_CENTAX_BOUND = (
    "In section 3.2 of Taxes at the top, CenTax says the bottom 50% would pay "
    "less than 0.5% of the revenue from NICs on partnerships, and in Table 1 it "
    "prints their share as 0.40%."
)
_HMT_30 = (
    "In its executive summary and Box 3.A, HM Treasury estimates that "
    "billpayers save around £30 by 2030 under the Energy Debt Circuit Breaker. "
    "In paragraph 3.8 it puts a typical household's saving under the same debt "
    "strategy at almost £30 by 2030. We read one estimate of the saving."
)
_HMT_70K = (
    "In its executive summary HM Treasury expects the government to help "
    "70,000 households onto the housing ladder through Your First Home, and in "
    "paragraph 5.5 around 70,000 households in England."
)
_HMT_AI = (
    "In paragraph 2.15 the government puts £50 million into a Civil Service AI "
    "transformation fund, and in paragraph 6.6 it funds the same £50 million "
    "from savings in administration budgets."
)
_HMT_GAP = (
    "In footnote 73 HM Treasury counts £2.3 billion from this Budget's tax-gap "
    "measures, rounding the +2,250m it prints in Table 6.3 for the subtotal "
    "including the memo line in 2029-30."
)
_HMT_35M = (
    "HM Treasury counts 35 million motorists in paragraph 3.3 and again in "
    "paragraph 3.13."
)
_HMT_50 = (
    "In its executive summary, in paragraphs 3.4 and 3.5 and in Box 3.A, HM "
    "Treasury expects the government to take around £50 off the annual Ofgem "
    "price cap in April 2027 by extending the VAT cut on domestic electricity."
)
_HMT_20M = (
    "HM Treasury counts up to 20 million households in England that the "
    "government pays the Household Energy Payment, in its executive summary "
    "and in paragraphs 2.48 and 3.5."
)
_HMT_15M = (
    "In paragraph 5.12 and again in paragraph 6.77, the government gives the "
    "Office for the Impact Economy £15 million."
)
_HMT_DECILE = (
    "For its example in paragraph 2.10, HM Treasury gives a household of two "
    "adults a gross income of £33,500, the figure it prints in Table 2.C for "
    "two adults in the third decile."
)
_HMT_NADIA = (
    "In its worked example HM Treasury prints Nadia's £166 of income tax "
    "twice, as the tax she owes and the tax she pays."
)
_HMT_TAX_GAP = (
    "HM Treasury prints each tax-gap measure's yield from 2026-27 to 2031-32 "
    "in its policy costings and again in red book Table 6.3, where we keep it."
)
_IFS_80 = (
    "IFS prints one share, around 80% of households in England, in both its "
    "initial response and Helen Miller's opening remarks."
)
_OBR_TOTAL = (
    "The OBR rounds the measure's Table 1.1 total for the year in its chapter 3 "
    "text, to £0.1 billion or to £1 billion."
)
_OBR_T31 = (
    "The OBR prints this line in £ billion in Table 3.1, with a positive sign "
    "for higher borrowing, and in £ million in Table 1.1 of its policy "
    "workbook, with a negative sign for a cost to the Exchequer."
)
_OBR_T33 = (
    "The OBR prints the online marketplace measure's yield from 2027-28 to "
    "2031-32 in Table 3.3, under the tax head, and in Table 1.1. It costs the "
    "measure in VAT receipts alone, so it prints the same figures in both "
    "tables, with opposite signs."
)
_OBR_DIRECT = (
    "In paragraph 3.2 the OBR puts the direct effect of policy measures at a "
    "£12 billion cut in borrowing in 2031-32, rounding the 11,681 (£ million) "
    "it prints in Table 1.1."
)
_OBR_DEPARTMENTS = (
    "In paragraph 3.11 the OBR rounds 2026-27's 5.4 (£ billion) on Table "
    "3.1's line for other departmental spending changes to £5 billion."
)
_OBR_VAT = (
    "In paragraph 3.19 the OBR costs the VAT cut on domestic electricity at "
    "£0.7 billion in 2026-27 and £0.3 billion in 2027-28, rounding the VAT "
    "line of measure 2 in Table 1.1 (-734 and -296, £ million)."
)
_OBR_FOUNDERS = (
    "The OBR gives Founders' Relief's 2029-30 effect as a £0.3 billion cut in "
    "receipts in paragraph 3.18, and as -261 (£ million) in Table 1.1, where "
    "it prints a loss to the Exchequer as negative."
)
_RF_AGAIN = (
    "Resolution Foundation prints the figure, with the same meaning, in more "
    "than one of its documents."
)
_RF_BOUND = (
    'Resolution Foundation bounds the figure in one printing ("under £145", '
    '"over £130") and gives it in another; we keep the point value.'
)
_RF_WORKBOOK = (
    "Resolution Foundation rounds the figure in its text or on its chart, and "
    "gives the unrounded value in the chart's workbook."
)
_RF_3PC = (
    "Resolution Foundation expects typical non-pensioner incomes to fall by 3 "
    "per cent between 2026-27 and 2028-29 in a press release, and by 3.0 per "
    "cent on its publication page."
)
_RF_HALF = (
    "On its publication page Resolution Foundation says just over half of the "
    "cost of living support goes to the poorer half of households, and on "
    "page 19 of its briefing it estimates 52 per cent."
)
_RF_MILLION = (
    "Resolution Foundation says over a million private renting families lose "
    "out from the LHA freeze, and in its workbook for Figure 9 it counts "
    "1,572,152 families who would gain if the government unfroze LHA."
)
_TPA_1BN = (
    "Tax Policy Associates gives the 2028/29 yield of Table 6.1 lines 61 and 62 "
    "as £1.1bn, and calls it about £1bn in its section on savers and landlords."
)
_TPA_700M = (
    "Tax Policy Associates sums its groups to £700m in footnote 5, and prints "
    "£0.7bn in its chart's description."
)
_TPA_19BN = (
    "Tax Policy Associates prints the real-terms total as £19.1bn in footnote 7 "
    "and in its chart's description, and rounds it to £19bn in the text."
)
_TPA_6BN = (
    "Tax Policy Associates says only about £6bn of the 2030-31 tax rises in "
    "2026 money comes from this Budget, and plots £5.9bn for it on its chart of "
    "tax rises by fiscal event."
)
_TPA_CHART = (
    "Tax Policy Associates gives each group's 2027/28 value in two charts: it "
    "labels the value on its chart of the 2027/28 measures by tax, and plots "
    "it again on its chart of the changes by year."
)
REPEATED_PRINTINGS: dict[tuple[str, int], tuple[int | tuple[str, int], str]] = {
    ("uk_centax", 25): (1, _CENTAX_640),
    ("uk_centax", 107): (21, _CENTAX_197),
    ("uk_centax", 108): (58, _CENTAX_14),
    ("uk_centax", 62): (82, _CENTAX_TABLE),
    ("uk_centax", 64): (67, _CENTAX_TABLE),
    ("uk_centax", 65): (66, _CENTAX_BOUND),
    ("uk_hmt_redbook", 194): (9, _HMT_30),
    ("uk_hmt_redbook", 201): (9, _HMT_30),
    ("uk_hmt_redbook", 256): (14, _HMT_70K),
    ("uk_hmt_redbook", 265): (176, _HMT_AI),
    ("uk_hmt_redbook", 181): (354, _HMT_GAP),
    ("uk_hmt_redbook", 202): (187, _HMT_35M),
    ("uk_hmt_redbook", 190): (188, _HMT_50),
    ("uk_hmt_redbook", 197): (188, _HMT_50),
    ("uk_hmt_redbook", 268): (258, _HMT_15M),
    ("uk_hmt_redbook", 362): (400, _HMT_DECILE),
    ("uk_hmt_redbook", 423): (422, _HMT_NADIA),
    ("uk_hmt_redbook", 5): (188, _HMT_50),
    ("uk_hmt_redbook", 180): (7, _HMT_20M),
    ("uk_hmt_redbook", 189): (7, _HMT_20M),
    # each measure's six years, from row 191 of the costings and row 273 of
    # the red book
    **{
        ("uk_hmt_costings", c + y): (("uk_hmt_redbook", t + y), _HMT_TAX_GAP)
        for c, t in (
            (191, 273),
            (197, 279),
            (203, 285),
            (209, 291),
            (215, 297),
            (221, 303),
            (227, 309),
            (235, 315),
            (241, 321),
            (247, 327),
        )
        for y in range(6)
    },
    ("uk_ifs_ab2026", 97): (91, _IFS_80),
    ("uk_obr_tables", 2674): (537, _OBR_FOUNDERS),
    ("uk_obr_tables", 2672): (1005, _OBR_TOTAL),
    ("uk_obr_tables", 2667): (1167, _OBR_TOTAL),
    ("uk_obr_tables", 2531): (1183, _OBR_TOTAL),
    ("uk_obr_tables", 2673): (1347, _OBR_TOTAL),
    ("uk_obr_tables", 2526): (2171, _OBR_TOTAL),
    ("uk_obr_tables", 2520): (2501, _OBR_DIRECT),
    ("uk_obr_tables", 2655): (2570, _OBR_DEPARTMENTS),
    ("uk_obr_tables", 2680): (18, _OBR_VAT),
    ("uk_obr_tables", 2681): (19, _OBR_VAT),
    # Table 3.1's lines in 2026-27 to 2031-32, from its row to Table 1.1's
    **{
        ("uk_obr_tables", t31 + y): (t11 + y, _OBR_T31)
        for t31, t11 in (
            (2540, 2352),  # the direct effect of spending measures
            (2552, 2514),  # indirect effects of Government decisions
            (2558, 2496),  # direct effects of Government decisions
            (2564, 6),  # the council tax rebate, measure 1
            (2576, 2184),  # the net impact of the unfunded pensions valuation
            (2630, 2502),  # decisions on HM Treasury's policy decisions table
            (2636, 2508),  # decisions not on that table
        )
        for y in range(6)
    },
    **{("uk_obr_tables", 2712 + y): (943 + y, _OBR_T33) for y in range(5)},
    ("uk_rf_ab2026", 177): (13, _RF_AGAIN),
    ("uk_rf_ab2026", 28): (74, _RF_BOUND),
    ("uk_rf_ab2026", 29): (76, _RF_BOUND),
    ("uk_rf_ab2026", 54): (34, _RF_AGAIN),
    ("uk_rf_ab2026", 127): (34, _RF_AGAIN),
    ("uk_rf_ab2026", 93): (47, _RF_AGAIN),
    ("uk_rf_ab2026", 61): (56, _RF_AGAIN),
    ("uk_rf_ab2026", 63): (57, _RF_AGAIN),
    ("uk_rf_ab2026", 133): (4, _RF_AGAIN),
    ("uk_rf_ab2026", 153): (12, _RF_AGAIN),
    ("uk_rf_ab2026", 41): (49, _RF_3PC),
    ("uk_rf_ab2026", 48): (130, _RF_HALF),
    ("uk_rf_ab2026", 58): (383, _RF_MILLION),
    ("uk_rf_ab2026", 137): (383, _RF_MILLION),
    ("uk_rf_ab2026", 59): (379, _RF_WORKBOOK),
    ("uk_rf_ab2026", 138): (379, _RF_WORKBOOK),
    ("uk_rf_ab2026", 77): (382, _RF_WORKBOOK),
    ("uk_rf_ab2026", 147): (433, _RF_WORKBOOK),
    ("uk_rf_ab2026", 148): (434, _RF_WORKBOOK),
    ("uk_rf_ab2026", 149): (435, _RF_WORKBOOK),
    ("uk_rf_ab2026", 150): (436, _RF_WORKBOOK),
    ("uk_rf_ab2026", 151): (437, _RF_WORKBOOK),
    ("uk_rf_ab2026", 198): (633, _RF_WORKBOOK),
    ("uk_rf_ab2026", 200): (631, _RF_WORKBOOK),
    ("uk_rf_ab2026", 60): (765, _RF_WORKBOOK),
    ("uk_rf_ab2026", 205): (765, _RF_WORKBOOK),
    ("uk_rf_ab2026", 208): (763, _RF_WORKBOOK),
    ("uk_rf_ab2026", 209): (764, _RF_WORKBOOK),
    ("uk_tpa", 2): (104, _TPA_6BN),
    ("uk_tpa", 8): (6, _TPA_1BN),
    ("uk_tpa", 168): (25, _TPA_700M),
    ("uk_tpa", 4): (27, _TPA_19BN),
    ("uk_tpa", 264): (27, _TPA_19BN),
    ("uk_tpa", 224): (157, _TPA_CHART),
    ("uk_tpa", 206): (158, _TPA_CHART),
    ("uk_tpa", 212): (160, _TPA_CHART),
    ("uk_tpa", 194): (163, _TPA_CHART),
    ("uk_tpa", 176): (166, _TPA_CHART),
}


def _kept_row(family: str, k: int | tuple[str, int]) -> tuple[str, int]:
    """The (family, row) whose claim we keep for a repeat in ``family``."""
    return k if isinstance(k, tuple) else (family, k)


_KEPT_ROWS = {_kept_row(fam, k) for (fam, _), (k, _) in REPEATED_PRINTINGS.items()}
_PRINTING_ROWS = set(REPEATED_PRINTINGS) | _KEPT_ROWS
assert not _KEPT_ROWS & set(REPEATED_PRINTINGS), (
    "we keep a row that we also drop as a repeat"
)
# We read these conditions as belonging to each printing rather than to the
# figure, and the ingest compares every other condition of a repeat and the
# printing we keep. It compares each printing's value, sign convention and
# estimate kind when it checks that the values agree. In the identity it
# compares the reform key, which we take from the registry measure or, for a
# row we don't key to a measure, from the first 120 characters of its reform
# hint (AB25._reform). In the other keys we record where, and in which version
# of a document, the producer prints the figure.
_PER_PRINTING = frozenset(
    {
        "value_verbatim",
        "sign_convention",
        "estimate_kind",
        "reform_hint",
        "table",
        "table_line",
        "table_row",
        "sheet_section",
        "chart_label",
        "costing_leg_heading",
        "heading",
        "paragraph_heading",
        "document_position",
        "document_version",
    }
)
# We read a claim without an income group as covering everyone, and one without
# a component as covering the whole measure.
_UNSTATED = {"income_group": "all", "component": "Total"}


def _rows(family: str, *rows: int | range) -> frozenset[tuple[str, int]]:
    """Return (family, row) for each row we name, and for each row in each range."""
    return frozenset(
        (family, i) for r in rows for i in (r if isinstance(r, range) else (r,))
    )


# HM Treasury costs each of the ten measures in its package to close the tax
# gap in six years, one row a year. On six of the rows it costs the measure
# that expands HMRC's compliance workforce.
_TAX_GAP = _rows("uk_hmt_costings", range(191, 233), range(235, 253))
_TAX_COMPLIANCE = _rows("uk_hmt_costings", range(235, 241))
# For each group of repeats we list the conditions that we stage with one
# wording on the repeat and another on the printing we keep. We write each as
# (key, the repeat's wording, the kept printing's wording), and where we don't
# stage the condition on one printing, we write None for its wording. The
# ingest accepts a wording for the repeats we list it with, and raises on any
# other repeat that differs in it.
_Wording = tuple[str, str | None, str | None]
_READINGS: tuple[tuple[frozenset[tuple[str, int]], tuple[_Wording, ...]], ...] = (
    # On the printing of the £19.7 billion in the key findings of Taxes at the
    # top, we note the OBR's £32 billion baseline forecast for capital gains
    # tax from page 17.
    (
        _rows("uk_centax", 107),
        (
            (
                "baseline_forecast",
                None,
                "OBR baseline forecast of £32 billion for CGT (p. 17)",
            ),
        ),
    ),
    # In each year note we record how we date the printing. CenTax prints a
    # year with one printing of the £640 million and of the £14 billion, but
    # not with the other. It prints no year with either printing of the three
    # shares in section 3.2 and Table 1 of Taxes at the top.
    (
        _rows("uk_centax", 25),
        (
            (
                "year_note",
                "CenTax gives tax years as the later year ('2022 is tax year 2021-22', Taxes at the top fn 2)",
                "'in 2030'; CenTax gives tax years as the later year ('2022 is tax year 2021-22', Taxes at the top fn 2)",
            ),
        ),
    ),
    (
        _rows("uk_centax", 108),
        (
            (
                "year_note",
                "CenTax gives tax years as the later year ('2022 is tax year 2021-22', Taxes at the top fn 2)",
                "the 2024 estimate was for 2026; CenTax gives tax years as the later year ('2022 is tax year 2021-22', Taxes at the top fn 2)",
            ),
        ),
    ),
    (
        _rows("uk_centax", 62, 64, 65),
        (
            (
                "year_note",
                "no year in the sentence; staged with the 2030 costing it describes; CenTax gives tax years as the later year ('2022 is tax year 2021-22', Taxes at the top fn 2)",
                "no year printed with the table; staged with the 2030 costing",
            ),
        ),
    ),
    # HM Treasury costs each of the ten measures in its package to close the
    # tax gap in its policy costings, and prints the same figures in red book
    # Table 6.3. On the costings' rows we record the package's Table 6.1 line,
    # 45, the impact channel and the National Accounts basis that HM Treasury
    # states on page 10. We label the costings' basis a forecast and Table
    # 6.3's post-behavioural, though in both HM Treasury prints the costing
    # after any behavioural effect.
    (
        _TAX_GAP,
        (
            ("basis", "forecast", "post_behavioural"),
            ("impact_channel", "tax_measure", None),
            (
                "national_accounts_basis",
                "All costings are presented on a National Accounts basis (p.10)",
                None,
            ),
            ("table_61_line", "45", None),
        ),
    ),
    # On the costings' rows we also record whether HM Treasury includes a
    # behavioural effect, and quote HM Treasury where it says a measure has
    # none, or has no static impact on taxpayer liabilities.
    (
        _TAX_GAP - _TAX_COMPLIANCE,
        (("behavioural_adjustment", "included (see note)", None),),
    ),
    (
        _TAX_COMPLIANCE,
        (("behavioural_adjustment", "none: 'There is no behavioural effect.'", None),),
    ),
    (
        _rows("uk_hmt_costings", range(191, 197)),
        (
            (
                "static_impact",
                "none: 'The costing has no static impact on taxpayer liabilities.'",
                None,
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(197, 203)),
        (
            (
                "static_impact",
                "none: 'The measure has no static impact on taxpayer liabilities.'",
                None,
            ),
        ),
    ),
    # HM Treasury names each tax-gap measure in full in its costings, and in
    # short in red book Table 6.3.
    (
        _rows("uk_hmt_costings", range(191, 197)),
        (
            (
                "component",
                "E-invoicing: HMRC will require VAT invoices to be issued in a specified electronic format from 1 April 2029",
                "E-invoicing (Table 6.3 row 1)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(197, 203)),
        (
            (
                "component",
                "Employment expenses: Remove the £2,500 Income Tax Self Assessment expenses threshold from 6 April 2028",
                "Reforming employment expenses (Table 6.3 row 2)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(203, 209)),
        (
            (
                "component",
                "More Timely Payment: Require Income Tax Self Assessment taxpayers to pay more of their liabilities in-year from 2029",
                "More timely payment for Self Assessment (Table 6.3 row 3)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(209, 215)),
        (
            (
                "component",
                "VAT and PAYE: Require direct debit arrangements for VAT and PAYE return liabilities from 1 and 6 April 2029 respectively",
                "Direct debit for VAT and PAYE (Table 6.3 row 4)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(215, 221)),
        (
            (
                "component",
                "Real Estate: Participate in a new international agreement to automatically exchange information on real estate from 2029-30",
                "Real estate information exchange (Table 6.3 row 5)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(221, 227)),
        (
            (
                "component",
                "Debt Management: Enable HMRC to recover lower value tax debts from the bank accounts of taxpayers who can afford to pay but repeatedly fail to do so from July 2029",
                "Debt management: recovery from bank accounts (Table 6.3 row 6)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(227, 233)),
        (
            (
                "component",
                "Debt Management: Invest in HMRC's debt management to collect more overdue tax debts",
                "Debt management: investment in HMRC debt collection (Table 6.3 row 7)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(235, 241)),
        (
            (
                "component",
                "Tax Compliance: Expand investment in HMRC's compliance workforce to recruit an additional 670 officers by 2029-30",
                "Tax compliance: additional HMRC compliance officers (Table 6.3 row 8)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(241, 247)),
        (
            (
                "component",
                "Making Tax Digital (MTD) for Income Tax Self Assessment: Introduce a 12 month penalty easement for taxpayers joining MTD for Income Tax from 6 April 2027",
                "MTD for Income Tax Self Assessment penalty easement (Table 6.3 row 9)",
            ),
        ),
    ),
    (
        _rows("uk_hmt_costings", range(247, 253)),
        (
            (
                "component",
                "Image Rights: Delay the implementation of legislation to clarify the tax treatment of image rights by one year to 6 April 2028",
                "Image rights legislation delay (Table 6.3 row 10)",
            ),
        ),
    ),
    # HM Treasury names the annual Ofgem price cap and April 2027 in both
    # printings of the £50. We record them, with a static basis, on the
    # executive summary's printing and not on paragraph 3.4's.
    (
        _rows("uk_hmt_redbook", 5),
        (
            ("basis", "static", None),
            ("date", "April 2027", None),
            ("subgroup", "Ofgem price cap", None),
        ),
    ),
    # In paragraph 3.5 HM Treasury describes a £100 payment to households in
    # council tax bands A to D in England from January 2027. We record the
    # bands, the date and a static basis on the executive summary's count of up
    # to 20 million households, and not on paragraphs 2.48 and 3.5.
    (
        _rows("uk_hmt_redbook", 180, 189),
        (
            ("basis", None, "static"),
            ("date", None, "January 2027"),
            ("subgroup", None, "council tax bands A-D"),
        ),
    ),
    # We record the basis and scoring method on Table 6.3's subtotal including
    # the memo line, and not on footnote 73's £2.3 billion.
    (
        _rows("uk_hmt_redbook", 181),
        (
            ("basis", None, "post_behavioural"),
            ("scoring_method", None, "final"),
        ),
    ),
    # HM Treasury names all billpayers in its executive summary and Box 3.A,
    # and a typical household in paragraph 3.8, and we read the three printings
    # as one estimate of the saving. We record a static basis on the summary's
    # printing, and the comparison without the strategy's measures on paragraph
    # 3.8's.
    (
        _rows("uk_hmt_redbook", 194, 201),
        (("basis", None, "static"),),
    ),
    (
        _rows("uk_hmt_redbook", 194),
        (
            ("comparison", "without strategy measures", None),
            ("subgroup", "typical household", "all billpayers"),
        ),
    ),
    # In both printings HM Treasury expects Your First Home to help about
    # 70,000 households in England onto the housing ladder. On the executive
    # summary's printing we record the scheme's first-time buyers, its lifetime
    # and a static basis, and we note the period differently on the two.
    (
        _rows("uk_hmt_redbook", 256),
        (
            ("basis", None, "static"),
            ("horizon", None, "scheme lifetime"),
            (
                "period_detail",
                None,
                "Budget announcement; period of application as described in quote",
            ),
            (
                "period_interpretation",
                "publication-year policy observation; printed horizon retained without an inferred endpoint",
                None,
            ),
            ("subgroup", None, "first-time buyers"),
        ),
    ),
    # We label chapter 6's printings of the £50 million Civil Service AI
    # transformation fund and the £15 million for misogyny prevention as policy
    # announcements. We date paragraph 6.6's £50 million by paragraph 2.15, and
    # note the period of the £15 million differently on its two printings.
    (
        _rows("uk_hmt_redbook", 265),
        (
            ("basis", "policy_announcement", None),
            (
                "horizon",
                "across 2027-28 and 2028-29 (para 2.15)",
                "across 2027-28 and 2028-29",
            ),
        ),
    ),
    (
        _rows("uk_hmt_redbook", 268),
        (
            ("basis", "policy_announcement", None),
            (
                "period_detail",
                "Budget announcement year; no specific year stated for this quantity in the paragraph",
                None,
            ),
            (
                "period_interpretation",
                None,
                "publication-year policy observation; printed horizon retained without an inferred endpoint",
            ),
        ),
    ),
    # We record the statistic, a median, on Table 2.C's cell and not on
    # paragraph 2.10's example.
    (
        _rows("uk_hmt_redbook", 362),
        (("statistic", None, "median"),),
    ),
    # In its worked example HM Treasury says Nadia owes £166 of income tax, and
    # then that she pays it.
    (
        _rows("uk_hmt_redbook", 423),
        (("quantity", "income tax paid", "income tax liability"),),
    ),
    # We give IFS's initial response a reference date of 28 October and Helen
    # Miller's opening remarks one of 29 October. On the remarks' printing of
    # the 80% we also record council tax bands A to D.
    (
        _rows("uk_ifs_ab2026", 97),
        (
            ("eligibility", "council tax bands A-D", None),
            ("reference_date", "2026-10-29", "2026-10-28"),
        ),
    ),
    # The OBR words two lines of Table 1.1 differently in Table 3.1 and in
    # paragraph 3.2.
    (
        _rows("uk_obr_tables", 2520),
        (
            (
                "component",
                "Direct effect of policy measures (para 3.2)",
                "Direct effect of Government decisions",
            ),
        ),
    ),
    (
        _rows("uk_obr_tables", range(2552, 2558)),
        (
            (
                "component",
                "Indirect effects of Government decisions",
                "Indirect effect of Government decisions",
            ),
        ),
    ),
    (
        _rows("uk_obr_tables", range(2558, 2564)),
        (
            (
                "component",
                "Direct effects of Government decisions",
                "Direct effect of Government decisions",
            ),
        ),
    ),
    # On the rows of the OBR's policy workbook we mark each measure's total,
    # and record the measure's Table 6.1 line and the fiscal head and category
    # that the OBR gives it. We record none of these on the OBR's chapter 3
    # text or its Tables 3.1 and 3.3. The OBR labels two of Table 3.1's lines,
    # the direct effects of decisions on and off HM Treasury's policy decisions
    # table, as memo lines, and we mark their scoring as memo. We mark the
    # scoring of the other rows of these tables and of the workbook as final,
    # and leave the OBR's chapter 3 text unmarked. In Table 3.3 we record that
    # the OBR lists the online marketplace measure under tax and rates the
    # uncertainty of its costing as high.
    (
        _rows(
            "uk_obr_tables",
            2526,
            2531,
            2667,
            range(2564, 2570),
            range(2576, 2582),
            range(2672, 2675),
            range(2712, 2717),
        ),
        (
            ("fiscal_head", None, "Total"),
            ("row_type", None, "measure_total"),
        ),
    ),
    (
        _rows("uk_obr_tables", range(2540, 2546), range(2630, 2642)),
        (("row_type", None, "measure_total"),),
    ),
    (
        _rows("uk_obr_tables", 2680, 2681),
        (
            ("category", None, "VAT"),
            ("fiscal_head", None, "Receipts"),
            ("table_61_line", None, "2"),
        ),
    ),
    (
        _rows("uk_obr_tables", range(2564, 2570)),
        (("table_61_line", None, "1"),),
    ),
    (
        _rows("uk_obr_tables", range(2712, 2717)),
        (
            ("head", "Tax", None),
            ("table_61_line", None, "46"),
            ("uncertainty_rating", "High", None),
        ),
    ),
    (
        _rows("uk_obr_tables", 2531),
        (("table_61_line", None, "55"),),
    ),
    (
        _rows("uk_obr_tables", 2667),
        (("table_61_line", None, "54"),),
    ),
    (
        _rows("uk_obr_tables", 2672),
        (("table_61_line", None, "49"),),
    ),
    (
        _rows("uk_obr_tables", 2673),
        (("table_61_line", None, "60"),),
    ),
    (
        _rows("uk_obr_tables", 2674),
        (("table_61_line", None, "26"),),
    ),
    (
        _rows(
            "uk_obr_tables", 2520, 2526, 2531, 2655, 2667, range(2672, 2675), 2680, 2681
        ),
        (("scoring_method", None, "final"),),
    ),
    (
        _rows("uk_obr_tables", range(2630, 2642)),
        (("scoring_method", "memo", "final"),),
    ),
    # In our notes on these horizons and on the costing basis we cite pages of
    # Spread thin, the briefing by Resolution Foundation (RF). We word each
    # note for the document in which RF prints the figure.
    (
        _rows("uk_rf_ab2026", 127),
        (
            (
                "costing_basis",
                "Fuel Duty counted at the share accruing directly to households (fn 19)",
                "Fuel Duty counted at the share accruing directly to households (Spread thin fn 19)",
            ),
            (
                "horizon",
                "2025-26 and 2026-27 (as printed)",
                "years not printed in the release (Spread thin p.19 prints '2025-26 and 2026-27')",
            ),
        ),
    ),
    (
        _rows("uk_rf_ab2026", 54),
        (
            (
                "horizon",
                "years not printed on the page (Spread thin p.19 prints '2025-26 and 2026-27')",
                "years not printed in the release (Spread thin p.19 prints '2025-26 and 2026-27')",
            ),
        ),
    ),
    (
        _rows("uk_rf_ab2026", 93),
        (
            (
                "horizon",
                "2026-27 and 2027-28 (p.17: £3.4bn and £0.3bn)",
                "2026-27 and 2027-28 (Spread thin p.17: £3.4bn and £0.3bn)",
            ),
        ),
    ),
    # We record Figure 8's notes on where RF models each measure on page 19's
    # 52 per cent, and not on the publication page's 'just over half'.
    (
        _rows("uk_rf_ab2026", 48),
        (
            (
                "modelling_geography",
                None,
                "Council Tax and VAT cuts modelled for Great Britain only; Fuel Duty for the UK (Figure 8 notes)",
            ),
        ),
    ),
    # In its text RF counts the private renting families who lose out when the
    # government extends the LHA freeze. In Figure 9's workbook it labels the
    # same families as those who would gain if the government unfroze LHA. For
    # Your First Home it counts renter households with the resources to access
    # the scheme in its text, and families who could access it in the workbook.
    # On the workbook's cells we record the benefit units that RF counts and
    # its ranking by income after housing costs. On the text's printings we
    # record the halves of the income distribution that RF names, or our note
    # on the freeze.
    (
        _rows("uk_rf_ab2026", 58, 59, 77, 137, 138),
        (("housing_costs", None, "ahc"),),
    ),
    (
        _rows("uk_rf_ab2026", 58, 137),
        (
            (
                "framing",
                "RF: lose out from prolonging the LHA freeze into 2027-28; they would gain if LHA were unfrozen",
                None,
            ),
            (
                "income_axis",
                None,
                "net equivalised household income decile, after housing costs",
            ),
        ),
    ),
    (
        _rows("uk_rf_ab2026", 59, 77, 138),
        (
            (
                "income_axis",
                "household income distribution, split at the median (RF: poorer / richer half)",
                "net equivalised household income decile, after housing costs",
            ),
            ("unit_population", None, "private renting families (benefit units)"),
        ),
    ),
    (
        _rows("uk_rf_ab2026", 59, 138),
        (
            (
                "denominator",
                "private renting families who lose out from the prolonged LHA freeze",
                "private renting families who would benefit if LHA were unfrozen",
            ),
        ),
    ),
    (
        _rows("uk_rf_ab2026", 77),
        (
            (
                "denominator",
                "private renter households with the resources to access Your First Home",
                "private renting families who could access Your First Home",
            ),
        ),
    ),
    # On page 24 of Spread thin RF compares receipts with a path on which the
    # government raised Fuel Duty with RPI from January 2011. In its press
    # release it compares them with the rises the government planned over the
    # past 15 years. We read both as the same path of rates.
    (
        _rows("uk_rf_ab2026", 153),
        (
            (
                "counterfactual",
                "Fuel Duty rates risen in line with RPI since January 2011",
                "planned Fuel Duty rises delivered over the past 15 years",
            ),
        ),
    ),
    # On Figure 23's points we note a change since 2023-24, and on the
    # workbook's cells for 2028-29 a change from 2023-24 to 2028-29.
    (
        _rows("uk_rf_ab2026", 208, 209),
        (("horizon", "change since 2023-24", "2023-24 to 2028-29"),),
    ),
    # We word RF's median and its population in full on the press release's
    # printing of the fall in typical non-pensioner incomes, and in short on
    # the publication page's.
    (
        _rows("uk_rf_ab2026", 41),
        (
            ("statistic", "median real annual disposable income", "median"),
            (
                "unit_population",
                "working-age (non-pensioner) households",
                "non-pensioners",
            ),
        ),
    ),
    # On the press release's printing we record council tax bands E and above
    # for the households in higher-band properties that miss out on the
    # Household Energy Payment.
    (
        _rows("uk_rf_ab2026", 133),
        (
            (
                "subgroup",
                "live in higher-band properties and will miss out on the Household Energy Payment",
                "live in higher-band properties (Council Tax bands E and above) and miss out on the Household Energy Payment",
            ),
        ),
    ),
    # In our notes we trace the £6 billion in the text of Tax Policy Associates
    # (TPA) to Table 6.1's total in today's money. We trace the £5.9 billion on
    # its chart to its grouping of the OBR's costings by fiscal event in 2026
    # money, under the series 'Healey Oct 2026 Budget'.
    (
        _rows("uk_tpa", 2),
        (
            (
                "derived_from",
                "HM Treasury Budget 2026 Table 6.1 total tax policy decisions, in 2026 money",
                "OBR costings of tax measures announced since 2020, grouped by TPA by fiscal event",
            ),
            ("policy_event", None, "Healey Oct 2026 Budget"),
            ("price_basis", "today's money (2026)", "2026 money"),
        ),
    ),
    # TPA prints no year with its 'about £1bn' from savers and landlords, and
    # in a note on that printing we date it at 2028-29, the year that TPA gives
    # with its £1.1 billion.
    (
        _rows("uk_tpa", 8),
        (
            (
                "year_note",
                "no year stated ('it will be permanent'); staged at 2028-29, the first full year of the rise",
                None,
            ),
        ),
    ),
    # TPA sums its groups of Table 6.1's tax rows to £700m in footnote 5 and to
    # £0.7 billion in its chart's description, and we describe the sum in
    # different words on each.
    (
        _rows("uk_tpa", 168),
        (
            (
                "derived_from",
                "HM Treasury Budget 2026 Table 6.1 tax rows, summed by TPA's groups",
                "HM Treasury Budget 2026 Table 6.1, tax rows (53 lines)",
            ),
            ("measure_type", None, "sum of TPA's groups of the Table 6.1 tax rows"),
        ),
    ),
    # We record TPA's deflator on footnote 7's £19.1 billion, and not on the
    # text's £19 billion or the chart description's £19.1 billion. On the
    # text's printing we give the same source and price basis in more words.
    (
        _rows("uk_tpa", 4, 264),
        (
            (
                "deflator",
                None,
                "OBR CPI forecast (EFO Table A.1), 2.0% assumed for 2032",
            ),
        ),
    ),
    (
        _rows("uk_tpa", 4),
        (
            (
                "derived_from",
                "HM Treasury Budget 2026 Table 6.1 tax lines, deflated by the OBR's October 2026 CPI forecast",
                "HM Treasury Budget 2026 Table 6.1 tax rows, deflated",
            ),
            ("price_basis", "2026-27 prices (footnote 7)", "2026-27 prices"),
        ),
    ),
)
_SAME_READING = frozenset(
    (family, i, *wording)
    for repeats, wordings in _READINGS
    for family, i in repeats
    for wording in wordings
)


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
            if cond.get("program") != value:
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
    rest = {k: v for k, v in pub.items() if k != "also_printed_in"}
    return (
        len(s.conditions.get("value_verbatim", "")),
        json.dumps(
            [
                pub.get("table"),
                pub.get("locator"),
                s.source_column,
                pub.get("quote"),
                rest,
            ],
            sort_keys=True,
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


_PRINTED_AMOUNT = re.compile(
    r"£(0|[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)(?:\.(\d+))? (million|billion)"
)
_MULTIPLIERS = {"million": 1e6, "billion": 1e9}


def _printed_unit(row: dict) -> float:
    """Return the place value of the last printed digit: £100m for "£2.6 billion".

    We raise if someone uses another printed form or stores a value that differs
    from the printed amount."""
    printed = _PRINTED_AMOUNT.fullmatch(row["value_raw"])
    if printed is None:
        raise ValueError(f"no printed amount in {row['value_raw']!r}")
    places = printed[2] or ""
    multiplier = _MULTIPLIERS[printed[3]]
    number = float(printed[1].replace(",", "") + "." + (places or "0"))
    if not math.isclose(number * multiplier, abs(row["value"]), rel_tol=1e-9):
        raise ValueError(f"{row['value']} doesn't match printed amount {printed[0]!r}")
    return multiplier / 10 ** len(places)


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
    for (fam, i), (basis, raw, _, _) in ROW_TIME_BASES.items():
        if fam == family and (rows[i]["time_basis"], rows[i]["value_raw"]) != (
            basis,
            raw,
        ):
            raise ValueError(f"ROW_TIME_BASES {fam} row {i} no longer matches")
    reviewed = {i: v for (fam, i), v in REVIEWED_TWINS.items() if fam == family}
    if reviewed:
        table = _load("uk_hmt_tables")
        for i, (t, _) in reviewed.items():
            r = rows[i]
            if _is_component(r) or _is_component(table[t]):
                raise ValueError(f"REVIEWED_TWINS {family} row {i} is a component")
            a, b = abs(r["value"]), abs(table[t]["value"])
            announced = _ANNOUNCEMENT_YEARS.get((family, i))
            if (
                r.get("measure_key") != table[t].get("measure_key")
                or abs(a - b) > _printed_unit(r) / 2
                or (
                    r["period"] != table[t]["period"]
                    and announced != (r["period"], t, table[t]["period"])
                )
            ):
                raise ValueError(f"REVIEWED_TWINS {family} row {i} no longer matches")


_NUMBER = re.compile(r"(\d[\d,]*)(?:\.(\d+))?")


def _printed_place(s: ExternalScore) -> float:
    """Return the place value of a printing's last digit in the claim's units:
    £100m for "£2.6 billion", 0.01 for "91 per cent" on a share. For a
    printing without digits ("over a million"), or a value of zero, we
    return 0.

    We raise unless the value equals the printed number times a power of
    ten. We fold any workbook exponent into that power, so we read the digits
    before "E" and ignore the exponent."""
    printed = _NUMBER.search(s.conditions["value_verbatim"])
    if printed is None or s.value == 0:
        return 0.0
    whole, places = printed.groups()
    number = float(whole.replace(",", "") + "." + (places or "0"))
    if number == 0:
        return 0.0
    scale = abs(s.value) / number
    unit = 10.0 ** round(math.log10(scale))
    if not math.isclose(scale, unit, rel_tol=1e-9):
        raise ValueError(f"{s.value} doesn't match printed {printed[0]!r}")
    return unit * 10.0 ** -len(places or "")


def _relation(s: ExternalScore) -> str:
    """How the producer's sign on this printing relates to PolicyEngine's
    (scorecard_db.signs)."""
    return signs.classify(
        {
            "metric": s.metric.value,
            "conditions": s.conditions,
            "country": "UK",
            "source": s.source,
        }
    )[0]


def _signed_values(a: ExternalScore, b: ExternalScore) -> tuple[float, float]:
    """Return both values in PolicyEngine's orientation where the producer
    states each printing's sign convention (scorecard_db.signs), and
    otherwise both magnitudes."""
    relations = [_relation(s) for s in (a, b)]
    if set(relations) <= {signs.SAME, signs.OPPOSITE}:
        return (
            signs.external_value_pe_sign(a.value, relations[0]),
            signs.external_value_pe_sign(b.value, relations[1]),
        )
    return abs(a.value), abs(b.value)


_BOUNDS = {"range_low", "range_high"}


def _within_half(a: float, b: float, place: float) -> bool:
    """Whether a and b differ by at most half of ``place``. In binary floating
    point, 0.58 - 0.575 = 0.0050000000000000044, so we allow a few units in the
    last place of each operand."""
    slack = 4 * (math.ulp(a) + math.ulp(b) + math.ulp(place))
    return abs(a - b) <= place / 2 + slack


def _within_bound(bound: ExternalScore, point: ExternalScore, place: float) -> bool:
    """Whether a point value printed to ``place`` lies within a bound
    printing: at or above a lower bound ("over a million"), or at or below an
    upper bound ("under £145"). The point may lie up to half its last digit past
    the bound, because the producer may have rounded it across. We compare the
    producer's own values, so the two printings must share a sign convention."""
    if _relation(bound) != _relation(point):
        return False
    inside = (
        point.value >= bound.value
        if bound.conditions["estimate_kind"] == "range_low"
        else point.value <= bound.value
    )
    return inside or _within_half(point.value, bound.value, place)


def _check_printing(family: str, i: int, repeat: ExternalScore, kept: ExternalScore):
    def identity(s: ExternalScore) -> tuple:
        return (
            s.source,
            s.reform.key(),
            s.metric,
            s.unit_concept,
            s.period,
            s.time_basis,
            s.period_start,
            s.period_end,
            s.conditions.get("row_type") == "measure_component",
        )

    a, b = _signed_values(repeat, kept)
    coarse, fine = _printed_place(repeat), _printed_place(kept)
    kinds = [s.conditions.get("estimate_kind") for s in (repeat, kept)]
    bound = [kind in _BOUNDS for kind in kinds]
    if bound == [True, False]:
        agree = _within_bound(repeat, kept, fine)
    elif bound == [False, True]:
        agree = False  # we never keep a bound over a point value
    else:
        agree = kinds[0] == kinds[1] and fine <= coarse and _within_half(a, b, coarse)
    keys = (
        repeat.conditions.keys() | kept.conditions.keys() | _UNSTATED.keys()
    ) - _PER_PRINTING
    first, second = (
        {k: s.conditions.get(k, _UNSTATED.get(k)) for k in keys} for s in (repeat, kept)
    )
    reworded = {
        (family, i, k, first[k], second[k]) for k in keys if first[k] != second[k]
    }
    if identity(repeat) != identity(kept) or reworded - _SAME_READING or not agree:
        raise ValueError(f"REPEATED_PRINTINGS {family} row {i} no longer matches")


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
    printed: dict[tuple[str, int], ExternalScore] = {}
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
            if name in _DROP_BY_NAME and (family, i) not in ROW_METRICS:
                _drop(acct, fam, _DROP_BY_NAME[name])
                continue
            label = unit_label(row)
            if label in AB25._UNIT_DROPS:
                _drop(acct, fam, AB25._UNIT_DROPS[label])
                continue
            if (family, i) in ROW_METRICS:
                metric = ROW_METRICS[(family, i)][2]
            elif name in DISPOSITIONS:
                metric = DISPOSITIONS[name]
            else:
                raise ValueError(
                    f"{family}: metric {name!r} has no disposition — decide it "
                    "in DISPOSITIONS_AB2026 or DROP_BY_NAME_AB2026"
                )
            if (family, i) in ROW_UNITS:
                row = {**row, "unit_concept": ROW_UNITS[(family, i)]}
            if (family, i) in ROW_TIME_BASES:
                row = {**row, "time_basis": ROW_TIME_BASES[(family, i)][2]}
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
            if (family, i) in _PRINTING_ROWS:
                printed[(family, i)] = score
            if family == "uk_hmt_tables":
                table_claims[i] = score
                if twin is not None:
                    canonical[twin] = score
            scores.append(score)
            fam["ingested"] += 1
            acct["ingested"] += 1
        acct["by_family"][family] = fam
    # Figures a producer prints more than once (REPEATED_PRINTINGS). When we
    # stage a sample of rows, as we do in tests, we skip a pair unless we stage
    # both its rows.
    repeats: set[int] = set()
    # a dropped repeat's claim id -> the claims we merged it into
    targets: dict[str, set[int]] = {}
    for (family, i), (k, _) in sorted(REPEATED_PRINTINGS.items()):
        kept_row = _kept_row(family, k)
        repeat, kept = printed.get((family, i)), printed.get(kept_row)
        if repeat is None or kept is None:
            if families is None:
                raise ValueError(
                    f"no claim from REPEATED_PRINTINGS {family} row {i} or its "
                    f"kept row {kept_row[1]}"
                )
            continue
        _check_printing(family, i, repeat, kept)
        kept.publication.setdefault("also_printed_in", []).append(
            {
                "family": family,
                "table": repeat.publication.get("table"),
                "locator": repeat.publication.get("locator"),
                "source_column": repeat.source_column or None,
                "value_verbatim": repeat.conditions["value_verbatim"],
            }
        )
        repeats.add(id(repeat))
        targets.setdefault(repeat.claim_id(), set()).add(id(kept))
        fam = acct["by_family"][family]
        fam["ingested"] -= 1
        acct["ingested"] -= 1
        _drop(acct, fam, "figure_printed_again")
    scores = [s for s in scores if id(s) not in repeats]
    # We raise if a claim we keep shares its id with a repeat we dropped, unless
    # we merged that repeat into the claim itself. Had we kept the repeat,
    # merge_republications would have merged the two, so unless we also list
    # that claim's row in REPEATED_PRINTINGS, we would score the figure twice.
    if any(id(s) not in targets.get(s.claim_id(), {id(s)}) for s in scores):
        raise ValueError("we keep a claim that shares its id with a repeat we dropped")
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
