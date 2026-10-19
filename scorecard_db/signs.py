"""Sign of a published value relative to PolicyEngine's (issue #198).

Sources state their sign rule in free text (``conditions.sign_convention``:
131 distinct strings, from "positive = gain to households" to "Note
(verbatim): A positive sign implies an increase in borrowing."). A consumer
cannot compare ``external_value`` with the PolicyEngine value without
reading that text, and the HMRC ready reckoner's unsigned magnitudes showed
as a -213% gap where the real one is about +13%.

``classify(row)`` reads one exported row and returns ``(relation, basis)``:

    same       the published value and the PolicyEngine value point the
               same way
    opposite   multiply the published value by -1 to compare
    magnitude  the published value is unsigned (its direction is in the
               label); compare absolute values
    unknown    no rule settles it; the free text stays the record

The reference orientation is the row's PolicyEngine RESULT where the
stager says it oriented that result to the claim (the Autumn Budget 2025
stager annotates "PE oriented to it" / "PE's own orientation"), and
otherwise PolicyEngine's own orientation for the metric (``ORIENTATION``).
Every decision comes from a declared convention, never from comparing the
two signs: a real sign disagreement must stay visible.

Phrasings are matched as lower-case substrings, checked in order: phrases
that make a value unanswerable for the metric (adjustments, forecast
revisions, effects stated for the opposite reform), then opposite, then
same. The exchequer phrasings start from pipeline/stage_uk_ab2025.py's
lists, which classify the same strings for that stager.
"""

from __future__ import annotations

SAME = "same"
OPPOSITE = "opposite"
MAGNITUDE = "magnitude"
UNKNOWN = "unknown"
RELATIONS = (SAME, OPPOSITE, MAGNITUDE, UNKNOWN)

# What a positive value means in PolicyEngine, by change metric. A metric
# not listed is a level (a rate, count, amount or share), whose sign carries
# no direction to normalise.
ORIENTATION = {
    "revenue_change": "exchequer",
    "benefit_cost_change": "spending",
    "operating_cost_change": "spending",
    "decisions_effect_on_borrowing": "borrowing",
    "primary_deficit_change": "borrowing",
    "cash_requirement_change": "borrowing",
    "average_household_income_change": "household_gain",
    "avg_change_after_tax_income_usd": "household_gain",
    "pct_change_after_tax_income": "household_gain",
    "average_annual_gain": "household_gain",
    "real_income_growth": "household_gain",
    "average_tax_change": "tax_increase",
    "avg_tax_change_usd": "tax_increase",
    "energy_bill_change": "bill_increase",
    "poverty_count_change": "more_poverty",
    "poverty_rate_change": "more_poverty",
    "gdp_level_effect": "higher_output",
    "supply_side_impact": "higher_output",
    "cpi_inflation_effect": "higher_inflation",
    "taxpayer_count_change": "more_units",
    "participant_count_change": "more_units",
    "average_monthly_benefit_change": "higher_benefit",
}

# family -> (unanswerable, opposite, same) phrasings
_PHRASES: dict[str, tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]] = {
    "exchequer": (
        (
            "reduction in yield",
            "reduction in the static yield",
            "reduce the static costing",
            "reduction in the £8.3bn yield",
            "brought forward",
            "than in the march 2025 forecast",
            "improvement in the fiscal outlook",
            "british racing",
        ),
        (
            "positive = cost",
            "increase in borrowing",
            "a negative figure means a reduction in psnb",
            "positive = higher spending",
            "positive = receipts lost",
            "positive = revenue forgone",
        ),
        (
            "positive_gain_to_exchequer",
            "gain to the exchequer",
            "positive = yield",
            "positive = revenue yield",
            "(positive = yield",
            "(positive = increase in yield)",
            "reduction in borrowing",
            "higher government revenue",
            "here we present higher taxes as positive numbers",
            "reduction in public spending",
            "reduction in welfare spending",
            "positive = saving to the exchequer",
            "positive = saving against the current budget rule",
            "positive = fiscal tightening",
        ),
    ),
    "spending": (
        ("from the two-child limit",),
        ("positive = saving", "positive = cut"),
        (
            "higher government expenditure",
            "positive = cost to the exchequer",
            "positive = increase in",
        ),
    ),
    "borrowing": (
        (),
        ("reduction in borrowing",),
        ("increase in borrowing",),
    ),
    "household_gain": (
        ("reduction in benefit entitlement from the two-child limit",),
        ("loss to households",),
        (
            "positive = gain to",
            "higher mean household income",
            "positive = growth",
        ),
    ),
    "tax_increase": (
        (),
        (),
        (
            "positive = increase in",
            "positive = tax increase",
            "positive = charge paid",
            "positive = deduction from",
        ),
    ),
    "bill_increase": (
        (),
        ("positive = reduction in", "positive = saving", "positive = gain to"),
        ("positive = higher", "positive = increase"),
    ),
    "more_poverty": (
        (
            "as a result of the two-child limit",
            "because of the two-child limit",
            "kept in poverty by",
        ),
        (
            "lifted out",
            "brought out of poverty",
            "fewer children in poverty",
            "reduction in the child poverty rate",
            "reduction in the number of children in poverty",
            "fall in the number",
            "prevented from being drawn into poverty",
            "depth of poverty is reduced",
        ),
        (
            "more people in poverty",
            "increase in poverty",
            "increase in the number",
            "rise in the",
            "pushed into",
            "negative = reduction in the number",
        ),
    ),
    "higher_output": (
        ("claimants moved into work",),
        ("positive = reduction",),
        ("higher gdp", "higher real gdp", "addition to gdp"),
    ),
    "higher_inflation": (
        (),
        ("reduction in cpi inflation",),
        ("increase in cpi inflation", "higher inflation"),
    ),
    "more_units": (
        ("than in the march 2025 forecast",),
        (),
        ("positive = more", "positive = additional"),
    ),
    "higher_benefit": ((), (), ()),
}

_ORIENTED_TO_CLAIM = ("PE oriented to it", "PE's own orientation")
MAGNITUDE_CONVENTION = "magnitude_with_direction_in_label"


def _latest_annotations(row: dict) -> list[str]:
    return list((row.get("latest") or {}).get("annotations") or [])


def classify(row: dict) -> tuple[str, str]:
    """(relation, basis) for one exported row; see the module docstring."""
    conditions = row.get("conditions") or {}
    text = (conditions.get("sign_convention") or "").lower()
    if any(
        mark in note for note in _latest_annotations(row) for mark in _ORIENTED_TO_CLAIM
    ):
        return SAME, "result_oriented_to_claim"
    if (
        conditions.get("sign_convention") == MAGNITUDE_CONVENTION
        or conditions.get("change_direction") == "unsigned"
    ):
        return MAGNITUDE, "magnitude_in_label"
    family = ORIENTATION.get(row["metric"])
    if family is None:
        return SAME, "level"
    if text:
        unanswerable, opposite, same = _PHRASES[family]
        if any(p in text for p in unanswerable):
            return UNKNOWN, f"stated:{family}:not_this_quantity"
        if any(p in text for p in opposite):
            return OPPOSITE, f"stated:{family}:opposite"
        if any(p in text for p in same):
            return SAME, f"stated:{family}:same"
        return UNKNOWN, f"stated:{family}:unrecognised"
    # US producers publish signed changes, after minus before, which is
    # PolicyEngine's reform-minus-baseline orientation; no US adapter
    # re-signs a value.
    if row.get("country", "US") == "US":
        return SAME, "us_signed_change"
    if row.get("source") == "policyengine":
        return SAME, "policyengine_self"
    return UNKNOWN, "no_stated_convention"


def external_value_pe_sign(value: float | None, relation: str) -> float | None:
    """The published value in the reference orientation; None when it has
    no sign to normalise (magnitude) or no rule (unknown)."""
    if value is None:
        return None
    if relation == SAME:
        return value
    if relation == OPPOSITE:
        return -value
    return None
