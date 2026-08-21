"""Closed identity registry for the JRC EUROMOD-BE source.

Every source-shaped identity passes through ``canon``. Unknown values raise;
the adapter never accepts a new metric, series, table, geography, unit, or
model label merely because it happens to parse.
"""

SOURCE = "jrc_euromod"

_R: dict[tuple[str, str, str], str] = {}


def _identity(axis: str, values: tuple[str, ...]) -> None:
    for value in values:
        _R[(SOURCE, axis, value)] = value


def _alias(axis: str, source_value: str, canonical: str) -> None:
    _R[(SOURCE, axis, source_value)] = canonical


_identity("geography", ("BE",))
_identity("publisher", (SOURCE,))
_identity("series", ("euromod", "external", "ratio"))
_identity("table", ("A3.4", "A3.6", "A3.7", "A3.8"))
_identity(
    "metric",
    (
        "national_income_tax",
        "employee_social_insurance_contributions",
        "child_benefits",
        "unemployment_benefits",
        "gini",
        "at_risk_poverty_60_median_total",
    ),
)
_identity("unit", ("eur_millions", "gini_x100", "percent_share"))
_identity("model", ("EUROMOD BE_2025 (J2.0+)",))
_identity("assessment_level", ("individual",))
_identity(
    "population_scope",
    (
        "national_all_taxpayers",
        "national_all_employees",
        "national_all_recipients",
        "total_person_population",
    ),
)
_identity("tax_scope", ("national_income_tax",))
_identity("contribution_payer", ("employee",))
_identity("benefit_scope", ("child_benefits", "unemployment_benefits"))
_identity("income_concept", ("equivalised_household_standard_disposable_income",))
_identity("housing_costs", ("not_deducted",))
_identity("equivalisation", ("modified_oecd",))
_identity("poverty_line", ("relative_60_median",))
_identity(
    "source_scale",
    (
        "millions",
        "times_100",
        "percent",
    ),
)
_identity("data_vintage", ("euromod_be_country_report_2025",))
_identity("subgroup", ("total",))

_alias("program", "national_income_tax", "national_income_tax")
_alias(
    "program",
    "employee_social_insurance_contributions",
    "employee_social_insurance_contributions",
)
_alias("program", "child_benefits", "child_benefit")
_alias("program", "unemployment_benefits", "unemployment_benefit")
_alias("program", "child_benefit", "child_benefit")
_alias("program", "unemployment_benefit", "unemployment_benefit")


def canon(source: str, axis: str, value: str) -> str:
    """Return the registered canonical identity; fail on every unknown."""
    try:
        return _R[(source, axis, value)]
    except KeyError:
        raise ValueError(
            f"unregistered {axis} value {value!r} for source {source!r} — "
            "add it to be/aliases.py deliberately"
        ) from None


def known(axis: str) -> frozenset[str]:
    return frozenset(
        value
        for source, registered_axis, value in _R
        if source == SOURCE and registered_axis == axis
    )
