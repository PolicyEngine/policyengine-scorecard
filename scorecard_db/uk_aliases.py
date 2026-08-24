"""Closed identity registry for the UK external sources (#33).

The five UK adapters' vocabularies are source-shaped, not mutually
canonical (the batch review's set-wide finding): DWP counts
benefit_units where UKMOD counts families; HBAI writes poverty_line as
relative|absolute while UKMOD wrote bare median percentages into the
same key; OBR says winter_fuel_payment where UKMOD says
winter_fuel_allowance. This module is the ONE place those identities
are decided — keyed (source, axis, source_value) → canonical value —
and it is CLOSED: an unknown value raises, never passes through, and
near-neighbours that must NOT unify are recorded as DISTINCT so the
decision is visible rather than an accident of naming.

Canonical vocabularies decided here:

poverty_line — a poverty threshold is (basis, percent, median-vintage):
    HBAI relative → "relative_60_median" (60% contemporary median, the
    publication's own definition); HBAI absolute →
    "absolute_60_fye2011_median" (60% of FYE-2011 median, uprated);
    UKMOD 50|60|70 → "relative_{n}_median" (BHC contemporary median per
    the Country Report). HBAI-relative and UKMOD-60 therefore share a
    world by construction, deliberately.

program — canonical slugs are each source's own EXCEPT explicit
    aliases: ukmod winter_fuel_allowance → winter_fuel_payment (same
    benefit, DWP/OBR name). Explicit DISTINCT pairs: dwp_takeup's
    housing_benefit_pensioners never unifies with obr's
    housing_benefit_not_jsa / housing_benefit_on_jsa (pensioner-only
    caseload vs JSA-split whole caseload) nor ukmod's housing_benefit;
    dwp benefit_units never unify with ukmod families (no proof of
    equal family-unit definitions — the batch review's condition).
"""

from __future__ import annotations

# (source, axis, source_value) -> canonical value. Values map to
# themselves unless aliased; absence = unknown = raise.
_R: dict[tuple[str, str, str], str] = {}


def _identity(source: str, axis: str, values: list[str]) -> None:
    for v in values:
        _R[(source, axis, v)] = v


def _alias(source: str, axis: str, source_value: str, canonical: str) -> None:
    _R[(source, axis, source_value)] = canonical


# Pairs that LOOK unifiable and must never be: recorded so the decision
# is auditable and the triangle tests can assert them apart.
DISTINCT: frozenset[tuple[str, str]] = frozenset(
    {
        ("dwp_takeup:housing_benefit_pensioners", "obr:housing_benefit_not_jsa"),
        ("dwp_takeup:housing_benefit_pensioners", "obr:housing_benefit_on_jsa"),
        ("dwp_takeup:housing_benefit_pensioners", "ukmod:housing_benefit"),
        ("dwp_takeup:benefit_units", "ukmod:families"),
        # A decile of one publisher's distribution is not a decile — or a
        # quintile — of another's: different models, different income
        # concepts, different cut points. Never aliased.
        ("ifs:decile_1", "ukmod:q1"),
        ("ifs:decile_10", "ukmod:q5"),
        ("resolution_foundation:quintile_1", "ukmod:q1"),
        ("resolution_foundation:decile_1", "ifs:decile_1"),
        # And a coverage-restricted geography is not the UK.
        ("ifs:UK_excl_northern_ireland", "ifs:UK"),
        ("ifs:UK_excl_scotland", "ifs:UK"),
    }
)

# --- programs --------------------------------------------------------------
_identity(
    "dwp_takeup",
    "program",
    [
        "pension_credit",
        "guarantee_credit",
        "savings_credit_only",
        "housing_benefit_pensioners",
    ],
)
_identity("dwp_hbai", "program", ["hbai_low_income"])
_identity(
    "uk_hmrc",
    "program",
    [
        "air_passenger_duty",
        "capital_gains_tax",
        "child_benefit",
        "corporation_tax",
        "duties",
        "income_tax",
        "inheritance_tax",
        "insurance_premium_tax",
        "national_insurance",
        "stamp_duty_land_tax",
        "vat",
        "vehicle_excise_duty",
    ],
)
_identity(
    "obr",
    "program",
    [
        "armed_forces_independence_payment",
        "attendance_allowance",
        "bereavement_benefits",
        "carers_allowance",
        "child_benefit",
        "christmas_bonus",
        "cold_weather_payments",
        "dla_and_pip",
        "dwp_social_security",
        "financial_assistance_scheme",
        "housing_benefit_not_jsa",
        "housing_benefit_on_jsa",
        "incapacity_benefits",
        "income_support_non_incapacity",
        "industrial_injuries_benefits",
        "jobseekers_allowance",
        "maternity_allowance",
        "ni_social_security",
        "other_dwp",
        "paternity_pay",
        "pension_credit",
        "personal_tax_credits",
        "smi_loan_writeoffs",
        "state_pension",
        "statutory_maternity_pay",
        "statutory_sick_pay",
        "tax_credits_transferred_debt",
        "tax_free_childcare",
        "total_welfare",
        "universal_credit",
        "winter_fuel_payment",
    ],
)
_identity(
    "ukmod",
    "program",
    [
        "benefit_cap_housing_benefit",
        "benefit_cap_universal_credit",
        "best_start_grant_and_foods",
        "child_and_working_tax_credits",
        "child_benefit",
        "council_tax_reduction",
        "esa_income_based",
        "free_school_meals",
        "healthy_start_food",
        "housing_benefit",
        "income_distribution",
        "income_support",
        "income_tax",
        "income_tax_non_devolved",
        "income_tax_scottish",
        "income_tax_welsh",
        "jsa_contribution_based",
        "nic_all",
        "nic_employees",
        "nic_employers",
        "nic_self_employed",
        "pension_credit",
        "poverty",
        "school_clothing_grant",
        "scottish_carers_allowance_supplement",
        "scottish_child_payment",
        "scottish_child_winter_heating",
        "sure_start_maternity_grant",
        "universal_credit",
    ],
)
_alias("ukmod", "program", "winter_fuel_allowance", "winter_fuel_payment")

# --- poverty lines ----------------------------------------------------------
_alias("dwp_hbai", "poverty_line", "relative", "relative_60_median")
# Absolute low income = 60% of a FIXED median; WHICH median is
# year-dependent (Notes sheet Note 3: FYE-2025 anchor for 2021/22 on,
# FYE-2011 before) and rides conditions["poverty_line_anchor"], set by
# the stager per row — never baked into the line label.
_alias("dwp_hbai", "poverty_line", "absolute", "absolute_60_fixed_median")
for _n in ("50", "60", "70"):
    _alias("ukmod", "poverty_line", _n, f"relative_{_n}_median")

# --- housing-cost basis ------------------------------------------------------
for _src in ("dwp_hbai", "ukmod"):
    _identity(_src, "housing_costs", ["bhc", "ahc"])

# --- geographies -------------------------------------------------------------
_UK_REGIONS = [
    "East",
    "East Midlands",
    "England",
    "London",
    "North East",
    "North West",
    "Northern Ireland",
    "Scotland",
    "South East",
    "South West",
    "Wales",
    "West Midlands",
    "Yorkshire and the Humber",
]
_identity("dwp_takeup", "geography", ["GB"])
_identity("dwp_hbai", "geography", ["UK", "GB"] + _UK_REGIONS)
_identity("uk_hmrc", "geography", ["UK"])
_identity("obr", "geography", ["UK", "GB"])
# OBR's NI social-security rows are Northern Ireland — same geography as
# HBAI's region label; one canonical name.
_alias("obr", "geography", "NI", "Northern Ireland")
_identity("ukmod", "geography", ["UK"])

# --- subgroups ---------------------------------------------------------------
_identity(
    "dwp_takeup",
    "subgroup",
    [
        "total",
        "couples",
        "single_male",
        "single_female",
        "age_under_75",
        "age_75_plus",
    ],
)
_identity("dwp_hbai", "subgroup", ["total", "children", "pensioners", "working_age"])
_identity(
    "ukmod",
    "subgroup",
    [
        "total",
        "children",
        "children_covered",
        "men",
        "women",
        "over_spa",
        "q1",
        "q2",
        "q3",
        "q4",
        "q5",
        "starter_rate",
        "basic_rate",
        "intermediate_rate",
        "higher_rate",
        "advanced_rate",
        "additional_rate",
        "top_rate",
        "savers_rate",
    ],
)
_identity("obr", "subgroup", ["total"])
# uk_hmrc LEVEL rows carry identity-bearing bands and demographics;
# the reckoner's 75 verbatim change descriptions never route through
# this registry (their identity is the derived reform world, kept
# verbatim in conditions["option"]).
_identity(
    "uk_hmrc",
    "subgroup",
    [
        "total",
        "all_bands",
        "lower_or_starting_rate",
        "basic_rate",
        "higher_rate",
        "additional_rate",
        "savers_rate",
        "age_under_65",
        "age_65_plus",
        "state_pension_age",
        "male",
        "female",
    ],
)

# --- UC-deductions FRR family (#39; sources are fiscal-event documents,
# not statistical adapters — same closed-registry rule) ----------------------
for _src in ("hm_treasury", "dwp"):
    _identity(_src, "program", ["universal_credit"])
    _identity(_src, "subgroup", ["families_with_children"])
    _identity(_src, "geography", ["GB"])

# --- units (adapter unit_concept vocabulary; DB units mapped in ingest) ------
_identity(
    "dwp_takeup",
    "unit",
    ["benefit_units", "gbp_annual_nominal", "gbp_per_week_nominal"],
)
_identity(
    "dwp_hbai", "unit", ["persons", "children", "pensioners", "working_age_adults"]
)
_identity("uk_hmrc", "unit", ["individuals", "gbp_nominal", "fraction_of_income"])
_identity("obr", "unit", ["gbp_nominal"])
_identity(
    "ukmod",
    "unit",
    [
        "families",
        "households",
        "individuals",
        "children",
        "fraction",
        "gbp_nominal",
        "gbp_per_month_equivalised",
    ],
)
for _src in ("hm_treasury", "dwp"):
    _identity(_src, "unit", ["gbp", "households"])


# --- UK think tanks (#86: IFS, Resolution Foundation) ------------------------
# Both publish PROSE identities — "UK excluding Northern Ireland (note
# verbatim: ...)", "Decile Poorest", "poorest fifth (quintile 1)" — so
# closing them is the whole identity job for this lane. Two rules drive it:
#
# 1. A coverage-restricted geography is NOT the UK. IFS's Scotland- and
#    NI-excluding analyses get their own values; aliasing them to "UK"
#    would file an England-and-Wales figure as a UK one, the exact
#    fail-open this registry exists to stop. The publication's verbatim
#    wording stays on the claim as a geography_note.
# 2. A decile of one publisher's distribution is not a decile of
#    another's. The IFS and RF groups are registered per source and
#    recorded DISTINCT from UKMOD's quintiles and HBAI's deciles.
_identity(
    "ifs",
    "geography",
    ["UK", "England", "UK_excl_northern_ireland", "UK_excl_scotland"],
)
_alias("ifs", "geography", "UK excluding Northern Ireland", "UK_excl_northern_ireland")
_alias(
    "ifs",
    "geography",
    "UK excluding Northern Ireland (note verbatim: 'Northern Ireland is not "
    "included in this analysis')",
    "UK_excl_northern_ireland",
)
_alias(
    "ifs",
    "geography",
    "UK excluding Scotland (note verbatim: 'Excludes Scotland')",
    "UK_excl_scotland",
)
_identity("resolution_foundation", "geography", ["UK", "GB", "Scotland"])

_identity("ifs", "program", ["universal_credit"])
_identity(
    "ifs",
    "income_group",
    [f"decile_{_i}" for _i in range(1, 11)] + ["all"],
)
for _i, _label in enumerate(
    ["Decile Poorest"] + [f"Decile {_n}" for _n in range(2, 10)] + ["Decile Richest"],
    start=1,
):
    _alias("ifs", "income_group", _label, f"decile_{_i}")
_alias("ifs", "income_group", "All", "all")

# Resolution Foundation mixes quintiles, deciles and halves in one
# publication, so the vocabulary carries all three shapes explicitly
# rather than forcing them onto one grid.
_identity(
    "resolution_foundation",
    "income_group",
    [
        "quintile_1",
        "quintile_5",
        "decile_1",
        "decile_10",
        "bottom_half",
        "top_half",
        "decile_1_vs_decile_10",
    ],
)
for _src_value, _canon in (
    ("poorest fifth (quintile 1)", "quintile_1"),
    ("richest fifth (quintile 5)", "quintile_5"),
    ("poorest decile (decile 1)", "decile_1"),
    ("richest tenth (decile 10)", "decile_10"),
    ("richest decile (decile 10)", "decile_10"),
    ("bottom half", "bottom_half"),
    ("top half", "top_half"),
    ("lowest income decile vs highest income decile", "decile_1_vs_decile_10"),
):
    _alias("resolution_foundation", "income_group", _src_value, _canon)

# RF names the benefit in prose; these are the instruments, closed.
_identity(
    "resolution_foundation",
    "benefit",
    [
        "universal_credit_standard_allowance",
        "universal_credit_standard_allowance_under_25",
        "universal_credit_health_element",
        "local_housing_allowance",
        "state_pension",
        "inflation_linked_benefits",
    ],
)
for _src_value, _canon in (
    ("Universal Credit standard allowance", "universal_credit_standard_allowance"),
    ("UC standard allowance", "universal_credit_standard_allowance"),
    (
        "basic rate of unemployment benefits (UC standard allowance)",
        "universal_credit_standard_allowance",
    ),
    (
        "UC standard allowance, under-25s",
        "universal_credit_standard_allowance_under_25",
    ),
    ("UC health element, existing recipients", "universal_credit_health_element"),
    ("UC health element (new claimants)", "universal_credit_health_element"),
    ("Local Housing Allowance (frozen)", "local_housing_allowance"),
    ("State Pension (triple lock: earnings growth)", "state_pension"),
    ("inflation-linked benefits", "inflation_linked_benefits"),
):
    _alias("resolution_foundation", "benefit", _src_value, _canon)

_identity(
    "ifs",
    "unit",
    [
        "gbp",
        "gbp_per_year",
        "share",
        "percent",
        "percentage_points",
        "persons",
        "children_under_18",
        "families",
    ],
)
_identity(
    "resolution_foundation",
    "unit",
    [
        "gbp",
        "share",
        "percent",
        "percentage_points",
        "persons",
        "children_under_18",
        "families",
    ],
)


def canon(source: str, axis: str, value: str) -> str:
    """Canonical value for (source, axis, source_value); unknown raises."""
    try:
        return _R[(source, axis, value)]
    except KeyError:
        raise ValueError(
            f"unregistered {axis} value {value!r} for source {source!r} — "
            "add it to scorecard_db/uk_aliases.py deliberately (identity, "
            "alias, or DISTINCT), never pass it through"
        ) from None


def known(source: str, axis: str) -> frozenset[str]:
    """All source-side values registered for (source, axis)."""
    return frozenset(v for (s, a, v) in _R if s == source and a == axis)
