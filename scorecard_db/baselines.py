"""Baseline registry (issue #13): every baseline world, deliberately named.

A score's meaning is its (reform, baseline) pair. ReformRef keeps carrying
the baseline descriptor for claim-id hashing (unchanged); this module is
the queryable projection — one registry row per distinct descriptor, with
the source's own words defining the world. `register_baselines` seeds the
table and fails loudly if any baseline_key referenced by the data is not
described here: extending the registry is a deliberate act.

Convention (mirrors JCT/HMT practice): a costing scored against the law in
force at its own publication is the null baseline `current_law` — the
announcement vintage is a condition (fiscal_event, data_vintage), not a
distinct baseline world. Only genuinely non-current-law worlds (TCJA
extension, JCT current policy, TPC current-law + Senate Title VII, CPSP
counterfactual CTC regimes, PE's pre-AB2025 reinstated two-child limit)
get their own entries.
"""

from __future__ import annotations

from .db import ScorecardDB
from .models import CURRENT_LAW_DESCRIPTOR, baseline_key

# descriptor, label, description, framework, provenance
BASELINES: list[tuple[dict, str, str, str, str]] = [
    (
        CURRENT_LAW_DESCRIPTOR,
        "current_law",
        "Law in force at the source's scoring date (the null baseline; "
        "announcement vintage rides in conditions, not here).",
        "baseline",
        "Default for every claim without an explicit baseline descriptor.",
    ),
    (
        {"policy": "current_policy"},
        "current_policy",
        "JCT current-policy baseline: expiring provisions assumed "
        "continued rather than sunsetting under present law.",
        "policy_ref",
        "JCX-29-25 (manager's amendment scored vs current policy; twin of "
        "JCX-30/31 present-law scoring) — sources/harvest-2026-08-02/jct.",
    ),
    (
        {"policy": "tcja_extension"},
        "tcja_extension",
        "TCJA individual provisions extended past their scheduled 2025 sunset.",
        "policy_ref",
        "PWBM tables scored against a TCJA-extension baseline "
        "(sources/harvest-2026-08-02/pwbm NOTES: conditions."
        "baseline_policy=tcja_extension rows).",
    ),
    (
        {"policy": "current_law_pre_2025_tariffs"},
        "current_law_pre_2025_tariffs",
        "Current law excluding the 2025 tariff actions (Tax Foundation "
        "Tariff Tracker scoring convention).",
        "policy_ref",
        "Tax Foundation Tariff Tracker, July-2026 vintage "
        "(sources/harvest-2026-08-02/tax_foundation).",
    ),
    (
        {"policy": "current_law_plus_senate_obbba_title_vii"},
        "current_law_plus_senate_obbba_title_vii",
        "Current law plus the Senate OBBBA Title VII draft — the baseline "
        "under TPC's CTC options set.",
        "policy_ref",
        "TPC T25-0209/0213/0215 baseline_hint (sources/harvest-2026-08-02/"
        "tpc); draft≈enacted for these provisions per the campaign "
        "conventions note.",
    ),
    (
        {"policy": "no_ctc"},
        "no_ctc",
        "Counterfactual world with the Child Tax Credit removed (CPSP "
        "poverty counterfactual tables, 100% take-up, no behavior).",
        "policy_ref",
        "CPSP CTC counterfactual tables 2023/2024 (sources/harvest-2026-08-02/cpsp).",
    ),
    (
        {"policy": "tcja_ctc"},
        "tcja_ctc",
        "TCJA-parameter CTC world (CPSP counterfactual scenario).",
        "policy_ref",
        "CPSP CTC counterfactual tables (sources/harvest-2026-08-02/cpsp).",
    ),
    (
        {"policy": "tcja_ctc", "take_up": "full"},
        "tcja_ctc_full_takeup",
        "TCJA-parameter CTC world at explicit 100% take-up.",
        "policy_ref",
        "CPSP CTC counterfactual tables (sources/harvest-2026-08-02/cpsp).",
    ),
    (
        {"policy": "bl_ctc_option", "option": "1. TCJA CTC"},
        "bl_ctc_option_1_tcja_ctc",
        "Budget Lab CTC options workbook baseline: option 1 (TCJA CTC) "
        "under the current-law sunset path.",
        "policy_ref",
        "Budget Lab 16-scenario CTC options workbook "
        "(sources/harvest-2026-08-02/budget_lab).",
    ),
    (
        {"policy": "bl_ctc_option_permanent", "option": "1. TCJA Extension"},
        "bl_ctc_option_permanent_1_tcja_extension",
        "Budget Lab CTC options workbook baseline: option 1 under the "
        "TCJA-permanence path.",
        "policy_ref",
        "Budget Lab 16-scenario CTC options workbook "
        "(sources/harvest-2026-08-02/budget_lab).",
    ),
    (
        {"policy": "pre_obbba_current_law"},
        "pre_obbba_current_law",
        "US current law before OBBBA's enactment — the baseline of CBO's "
        "December-2024 revenue-option scores.",
        "policy_ref",
        "populace reform-validation registry: federal.cbo_rates_plus_1pt "
        "is scored against pre-OBBBA current law "
        "(scorecard_db/ingest_reform_validation.py; CBO Options for "
        "Reducing the Deficit, Dec 2024).",
    ),
    (
        {"policy": "pre_obbba_law"},
        "pre_obbba_law",
        "TPC T26-0009's stated counterfactual: 'Law Prior to the 2025 "
        "Budget Reconciliation Act' — a post-enactment scoring of enacted "
        "Title VII against the law it replaced. Distinct from "
        "pre_obbba_current_law (a pre-enactment forward score's baseline) "
        "by source assertion; registry equivalence is a deliberate future "
        "act, never assumed.",
        "policy_ref",
        "TPC T26-0009 by-race tables (published March 2026), re-parsed at "
        "sources/harvest-2026-08-02/tpc/reparse_t26_0009.py; descriptor "
        "set in scorecard_db/ingest_tpc.py (PRE_OBBBA).",
    ),
    (
        {"policy": "ifs_2cl_fp_removal_rolled_out"},
        "ifs_2cl_fp_removal_rolled_out",
        "IFS Green-Budget-2025 options baseline: the current UK "
        "tax-benefit system with the two-child limit and family-premium "
        "removal fully rolled out (steady state).",
        "policy_ref",
        "IFS staged conditions verbatim: 'current tax-benefit system "
        "with two-child limit and family premium removal fully rolled "
        "out' (sources/harvest-uk-2026-08-02/uk_ifs).",
    ),
    (
        {"policy": "pre_ab2025"},
        "pre_ab2025",
        "UK current law with the Autumn Budget 2025 two-child-limit "
        "abolition reversed (limit reinstated at 2 children; born-pre-2017 "
        "exemptions active) — the reinstated counterfactual PE executes as "
        "baseline so 'removal' is measured explicitly, not implied by "
        "sign.",
        "policyengine_uk",
        "Campaign run results/uk/two_child_reinstate_2026.json "
        "(gov.dwp.universal_credit.elements.child.limit.child_count: "
        "inf -> 2); issue #13 grounding artifact.",
    ),
]


def register_baselines(db: ScorecardDB) -> int:
    """Seed the registry, then fail loudly on any baseline_key the data
    references that is not curated above."""
    for descriptor, label, description, framework, provenance in BASELINES:
        db.register_baseline(
            baseline_key(descriptor),
            label,
            description=description,
            framework=framework,
            spec_json=None,
            provenance=provenance,
        )
    missing = db.unregistered_baselines()
    if missing:
        described = []
        for key in missing:
            sample = db.conn.execute(
                "SELECT reform_json FROM external_scores"
                " WHERE baseline_key = ? LIMIT 1",
                (key,),
            ).fetchone()
            described.append(f"{key} (e.g. {sample['reform_json']})" if sample else key)
        raise ValueError(
            "baseline_keys in data but not in the registry (add them to "
            f"scorecard_db/baselines.py deliberately): {described}"
        )
    return len(BASELINES)
