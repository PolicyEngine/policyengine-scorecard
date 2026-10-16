"""Shared event identities and worlds for the November 2025 PMD vintage.

The closed names are the workbook's Event column, in publication order.
Slugs use the inventory builder's own event_key function (lowercase,
non-alphanumeric runs replaced by one underscore). The policy-effects
and replay registry event slugs already follow that rule; preserve their
closed spellings explicitly and fail if a future alias collides.

Before June 2010 these are historical HM Treasury scorecard baselines,
not OBR forecasts. From June 2010 the database contains OBR-scrutinised
costings. The descriptor follows the existing obr_costings lane's
pre-measures policy-parameters world, including on spending measures.
"""

from data.uk.events.build_inventory import assign_measure_keys, event_key

EVENTS = (
    "Budget 1970",
    "Budget 1971",
    "Budget 1972",
    "Budget 1973",
    "Budget 1974",
    "Budget 1975",
    "Budget 1976",
    "Budget 1977",
    "Budget 1978",
    "Budget 1979",
    "Budget 1980",
    "Budget 1981",
    "Budget 1982",
    "Budget 1983",
    "Budget 1984",
    "Budget 1985",
    "Budget 1986",
    "Budget 1987",
    "Budget 1988",
    "Budget 1989",
    "Budget 1990",
    "Budget 1991",
    "Budget 1992",
    "Budget 1993",
    "Budget 1993 #2",
    "Budget 1994",
    "Budget 1995",
    "Budget 1996",
    "Budget 1997",
    "Budget 1998",
    "Budget 1999",
    "Budget 2000",
    "PBR 2000",
    "Budget 2001",
    "PBR 2001",
    "Budget 2002",
    "PBR 2002",
    "Budget 2003",
    "PBR 2003",
    "Budget 2004",
    "PBR 2004",
    "Budget 2005",
    "PBR 2005",
    "Budget 2006",
    "PBR 2006",
    "Budget 2007",
    "PBR 2007",
    "Budget 2008",
    "PBR 2008",
    "Budget 2009",
    "PBR 2009",
    "Budget 2010",
    "Budget 2010 #2",
    "Autumn 2010",
    "Budget 2011",
    "Autumn 2011",
    "Budget 2012",
    "Autumn 2012",
    "Budget 2013",
    "Autumn 2013",
    "Budget 2014",
    "Autumn 2014",
    "Budget 2015",
    "Budget 2015 #2",
    "Autumn 2015",
    "Budget 2016",
    "Autumn 2016",
    "Budget 2017",
    "Autumn Budget 2017",
    "Spring Statement 2018",
    "Budget 2018",
    "Spring Statement 2019",
    "Budget 2020",
    "Spending Review 2020",
    "Spring Budget 2021",
    "Autumn Budget 2021",
    "Spring Statement 2022",
    "Autumn Statement 2022",
    "Spring Budget 2023",
    "Autumn Statement 2023",
    "Spring Budget 2024",
    "Autumn Budget 2024",
    "Spring Statement 2025",
    "Autumn Budget 2025",
)
HISTORICAL_EVENTS = frozenset(EVENTS[:52])
# Existing closed spellings, shared across costings, policy-effects and replay.
_CLOSED_SLUGS = {
    "Spring Budget 2023": "spring_budget_2023",
    "Autumn Statement 2023": "autumn_statement_2023",
    "Spring Budget 2024": "spring_budget_2024",
    "Autumn Budget 2024": "autumn_budget_2024",
    "Spring Statement 2025": "spring_statement_2025",
    "Autumn Budget 2025": "autumn_budget_2025",
}


def event_slug(event: str) -> str:
    """A closed canonical event slug; unknown vintage events fail loudly."""
    if event not in EVENTS:
        raise ValueError(f"obr_pmd: unregistered fiscal event {event!r}")
    return _CLOSED_SLUGS.get(event, event_key(event))


def baseline_descriptor(event: str) -> dict:
    prefix = "hmt" if event in HISTORICAL_EVENTS else "obr"
    return {
        "policy": f"{prefix}_pre_measures_{event_slug(event)}",
        "counterfactual": "policy_parameters",
    }


# The later edition adds an event without extending the frozen November event
# list, inventory, replay keys or registry. These identities serve edition-delta
# claims only; a replay registry for the event is a separate artifact.
MARCH_EVENTS = ("Spring Forecast 2026",)


def march_event_slug(event: str) -> str:
    if event in EVENTS:
        return event_slug(event)
    if event not in MARCH_EVENTS:
        raise ValueError(f"obr_pmd: unregistered March-edition fiscal event {event!r}")
    return event_key(event)


def march_baseline_descriptor(event: str) -> dict:
    if event in EVENTS:
        return baseline_descriptor(event)
    return {
        "policy": f"obr_pre_measures_{march_event_slug(event)}",
        "counterfactual": "policy_parameters",
    }


if len({event_slug(event) for event in EVENTS}) != len(EVENTS):
    raise ValueError("obr_pmd: event slugs must be unique")
