"""Baseline-world descriptors used by Belgium claims and computations.

These constants intentionally have no scorecard imports so the central
baseline registry can import them without creating an ingest cycle.
"""

EUROMOD_BE_2022_WORLD = {
    "policy": "euromod_be_current_law",
    "system": "BE_2022",
    "period": "2022",
}

EUROMOD_BE_2023_WORLD = {
    "policy": "euromod_be_current_law",
    "system": "BE_2023",
    "period": "2023",
}

AXIOM_BE_2026_DEMO_WORLD = {
    "policy": "axiom_be_current_law_demo",
    "period": "2026",
    "rulespec_be": "7c85808ae99f5731b21059e643e5e19b66438904",
}

EUROMOD_WORLD_BY_PERIOD = {
    2022: EUROMOD_BE_2022_WORLD,
    2023: EUROMOD_BE_2023_WORLD,
}
