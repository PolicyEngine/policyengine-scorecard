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

import re

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
            # the OBR's prose on one behavioural part of a measure's yield
            # (paragraph 3.16's banks moving profits abroad), as "reduction
            # in yield" above
            "behavioural erosion of yield",
            # a transfer of business rates within the public sector
            "flowing to local government",
        ),
        (
            "positive = cost",
            "increase in borrowing",
            "a negative figure means a reduction in psnb",
            "positive = higher spending",
            "positive = receipts lost",
            "positive = revenue forgone",
            # the OBR's prose costings in the October 2026 EFO
            "positive = net cost",
            "positive = reduction in receipts",
            "positive = spending cost",
            "positive = additional spending",
            "positive = ame increase",
            "positive = pension spending increase",
            # OBR paragraph 3.43's continued fuel duty freeze, which the
            # AB2026 ingest carries on revenue_change
            "borrowing increase",
        ),
        (
            "positive_gain_to_exchequer",
            "gain to the exchequer",
            "positive = yield",
            "positive = revenue yield",
            "(positive = yield",
            "(positive = increase in yield)",
            "reduction in borrowing",
            "reduces borrowing",
            "higher government revenue",
            "here we present higher taxes as positive numbers",
            "reduction in public spending",
            "reduction in welfare spending",
            "positive = saving to the exchequer",
            # a cost saving is a yield, though "positive = cost" also matches
            # the same words: the reading conflicts, so it is unknown
            "cost saving",
            "positive = saving against the current budget rule",
            "positive = fiscal tightening",
            # the OBR's Table 1.1 workbook legend
            "a negative sign implies a loss to the exchequer",
            # IFS's chart of the Budget's tax change at the forecast horizon
            "positive = increase in net tax",
            # the OBR's prose savings in the October 2026 EFO
            "positive = reduction in spending",
            "positive = reduction in resource spending",
            "spending reduction",
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
        # a printed total that adds rows under two conventions, or an
        # average of absolute values, which has no direction
        ("mixed:", "no directional sign"),
        (
            "reduction in borrowing",
            "reduces borrowing",
            "borrowing reduction",
            "positive = yield",
            "a negative sign implies a loss to the exchequer",
            "positive = increase in net tax",
            "positive = additional investment income",
            # HM Treasury's Table 6.2 cash effects, which the AB2026 ingest
            # carries on cash_requirement_change
            "positive = cash inflow",
            "improves the public sector's cash position",
        ),
        (
            "increase in borrowing",
            "borrowing increase",
            "positive = increase in psnb",
            "positive = cost",
            # OBR paragraph 3.20's rise in the financing requirement, on
            # cash_requirement_change
            "increase in the financing requirement",
        ),
    ),
    "household_gain": (
        ("reduction in benefit entitlement from the two-child limit",),
        ("loss to households", "positive = decrease in real"),
        (
            "positive = gain to",
            "higher mean household income",
            "positive = growth",
            "positive = real income growth",
            "positive = higher real",
        ),
    ),
    "tax_increase": (
        (),
        # the red book's per-person savings, which the AB2026 ingest carries
        # on average_tax_change
        ("positive = saving or gain",),
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
        # RF prints only the negative side: "negative = reduction in the
        # typical household's annual bill"
        ("positive = higher", "positive = increase", "negative = reduction in"),
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
        ("higher gdp", "higher real gdp", "addition to gdp", "real gdp increase"),
    ),
    "higher_inflation": (
        # a bound on the effect's size with no direction (OBR paragraph 3.6)
        ("no direction given",),
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
# A phrase's negative leg ("...; negative = loss to households") states the
# same direction from the other side, so a deciding fragment found only
# there says nothing about what a positive value means (review A H-4).
_NEGATIVE_LEG = re.compile(r"\bnegative\s*(?:=|implies|means)[^;]*")
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
        positive = _NEGATIVE_LEG.sub(" ", text)

        def spans(phrases):
            # a phrase that names the negative side itself ("a negative sign
            # implies a loss ...") is read where it stands
            out = []
            for p in phrases:
                where = text if "negative" in p else positive
                i = where.find(p)
                while i >= 0:
                    out.append((i, i + len(p), where is text))
                    i = where.find(p, i + 1)
            return out

        opp, sam = spans(opposite), spans(same)
        # one stretch of text read both ways ("positive = cost saving ...")
        if any(
            a0 < b1 and b0 < a1 and wa == wb for a0, a1, wa in opp for b0, b1, wb in sam
        ):
            return UNKNOWN, f"stated:{family}:conflicting"
        if opp:
            return OPPOSITE, f"stated:{family}:opposite"
        if sam:
            return SAME, f"stated:{family}:same"
        if any(p in text for p in opposite + same):
            return UNKNOWN, f"stated:{family}:negative_leg"
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
