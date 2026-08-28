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

# Belgian PIT-reform score baselines. The two official documents do not
# expose executable baseline specifications, so their descriptors name that
# opacity instead of silently treating them as the registry's current-law
# world. The Axiom descriptor names the one same-year indexed baseline family;
# the claim period and assessment_year condition identify its annual member.
SPF_FINANCES_PIT_REFORM_2026_BASELINE = {
    "policy": "spf_finances_internal_pit_baseline_2026",
    "data_vintage": "assessment_year_2023_microdata",
}

COUR_DES_COMPTES_PIT_REFORM_2026_BASELINE = {
    "policy": "cour_des_comptes_pit_baseline_2026_unspecified",
}

AXIOM_BE_PIT_REFORM_2026_BASELINE = {
    "policy": "axiom_be_same_year_indexed_current_law_v05h",
    "population": "microcosm_be_v05_2025",
    "source_commit": "3d9f690",
}

EUROMOD_WORLD_BY_PERIOD = {
    2022: EUROMOD_BE_2022_WORLD,
    2023: EUROMOD_BE_2023_WORLD,
}
