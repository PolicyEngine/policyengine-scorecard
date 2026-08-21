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

from .db import BASELINE_SQL, ScorecardDB
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
        "JCX-29-25 (SFC substitute scored vs current policy) and JCX-30-25 "
        "(manager's amendment vs current policy; JCX-31-25 is its "
        "present-law twin) — sources/harvest-2026-08-02/jct/NOTES.md.",
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
        "Current law excluding the 2025 tariff actions.",
        "policy_ref",
        "TPC tariff tables, 161 claims: the baseline is explicit in "
        "sources/harvest-2026-08-02/tpc/manifest.jsonl for T25-0366's 11 "
        "claims (baseline_line) and assigned from the workbook "
        "verification documented in scorecard_db/ingest_tpc.py for "
        "T26-0010/0112/0113 (manifest baseline_line null). Plus PWBM "
        "tariff rows (22 claims). Tax Foundation tracker rows score "
        "current law and do not key this world "
        "(scorecard_db/ingest_tax_foundation.py).",
    ),
    (
        {"policy": "current_law_plus_senate_obbba_title_vii"},
        "current_law_plus_senate_obbba_title_vii",
        "Current law plus the Senate OBBBA Title VII draft — the baseline "
        "under TPC's CTC options set.",
        "policy_ref",
        "TPC T25-0209/T25-0215 baseline_hint (sources/harvest-2026-08-02/"
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
        {"policy": "pre_obbba_expiry_2026"},
        "pre_obbba_expiry_2026",
        "Pre-OBBBA expiry law as executed by the reform-validation "
        "registry's ISOLATED OBBBA scoring (l0-refit and its note's "
        "shared 2,735.78B income-tax baseline): TCJA-era parameters at "
        "their scheduled-expiry values, per provision, one at a time.",
        "policy_ref",
        "l0-refit backfill note (sources/populace-reform-validation/raw/"
        "populace-us-2024-sparse-l0-refit-…json _backfill_note): 'scored "
        "in isolation against pre-OBBBA law'; keys stamped by "
        "scorecard_db/ingest_reform_validation.py.",
    ),
    (
        {"policy": "hmrc_indexed_baseline_spring_2025"},
        "hmrc_indexed_baseline_spring_2025",
        "HMRC's indexed baseline for the June-2025 tax ready reckoner: "
        "the personal-tax-model counterfactual consistent with the OBR "
        "Spring Statement 2025 forecast, with the illustrative change "
        "implemented April 2026. A PE counterpart must run the same "
        "nominal change against a matching indexed baseline and state it "
        "explicitly (issue #13).",
        "policy_ref",
        "sources/hmrc-personal-tax/source.json (baselines.ready_reckoner, "
        "method) and annotations.json reckoner-baseline note; descriptor "
        "set in scorecard_db/ingest_uk_externals.py "
        "(_RECKONER_BASELINE).",
    ),
    (
        {"policy": "pre_frr_uc_deductions"},
        "pre_frr_uc_deductions",
        "UK law before the Fair Repayment Rate: UC deductions capped at "
        "25% of the standard allowance (the FRR lowered the cap to 15% "
        "from 2025-04-30). The counterfactual AB2024's FRR figures score "
        "against — NOT today's current law, which includes the FRR; a PE "
        "counterpart must construct the 25%-cap world explicitly.",
        "policy_ref",
        "AB2024 para 5.134 p.142 + DWP press release 2025-04-30 (both "
        "vendored/linked in sources/harvest-uk-deductions/frr/"
        "VERIFICATION.md); descriptor set in "
        "scorecard_db/ingest_uk_deductions.py (PRE_FRR_BASELINE).",
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
    # --- OBR published policy effects (#55) ---------------------------
    # OBR does NOT score a package against "the law in force" in the
    # abstract: it scores against that EFO round's PRE-MEASURES forecast
    # — a distinct, named world per round, which also fixes the economic
    # determinants the effect is measured off. Two rounds' pre-measures
    # worlds are different worlds, so a PE result computed against
    # current law is NOT comparable to these claims unless it says so.
    # Briefing paper No.10 chapter 2 splits the counterfactual KIND, so
    # the kind is a descriptor key rather than a blurred single world:
    #   policy_parameters  the measures' pre-announcement legislated
    #                      parameters (tax and welfare measures, and every
    #                      package-level chart)
    #   del_activity       the pre-existing DEL activity/spending level —
    #                      a departmental programme's counterfactual is
    #                      the activity already assumed, not a parameter
    #   regulatory         the pre-existing regulatory baseline (the
    #                      National Planning Policy Framework as it stood)
    # Only the (round, kind) pairs the data actually keys are registered;
    # the registry is a record of decisions, not a cross-product.
    (
        {
            "policy": "obr_pre_measures_spring_budget_2023",
            "counterfactual": "policy_parameters",
        },
        "obr_pre_measures_spring_budget_2023__policy_parameters",
        "OBR's pre-measures March 2023 forecast, the world the "
        "Spring Budget 2023 package and its individually scored measures "
        "are measured against; counterfactual kind: the measures' pre-announcement legislated parameters.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_spring_budget_2023",
            "counterfactual": "del_activity",
        },
        "obr_pre_measures_spring_budget_2023__del_activity",
        "OBR's pre-measures March 2023 forecast, the world the "
        "Spring Budget 2023 package and its individually scored measures "
        "are measured against; counterfactual kind: the pre-existing DEL activity/spending baseline.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_autumn_statement_2023",
            "counterfactual": "policy_parameters",
        },
        "obr_pre_measures_autumn_statement_2023__policy_parameters",
        "OBR's pre-measures November 2023 forecast, the world the "
        "Autumn Statement 2023 package and its individually scored measures "
        "are measured against; counterfactual kind: the measures' pre-announcement legislated parameters.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_autumn_statement_2023",
            "counterfactual": "del_activity",
        },
        "obr_pre_measures_autumn_statement_2023__del_activity",
        "OBR's pre-measures November 2023 forecast, the world the "
        "Autumn Statement 2023 package and its individually scored measures "
        "are measured against; counterfactual kind: the pre-existing DEL activity/spending baseline.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_spring_budget_2024",
            "counterfactual": "policy_parameters",
        },
        "obr_pre_measures_spring_budget_2024__policy_parameters",
        "OBR's pre-measures March 2024 forecast, the world the "
        "Spring Budget 2024 package and its individually scored measures "
        "are measured against; counterfactual kind: the measures' pre-announcement legislated parameters.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_autumn_budget_2024",
            "counterfactual": "policy_parameters",
        },
        "obr_pre_measures_autumn_budget_2024__policy_parameters",
        "OBR's pre-measures October 2024 forecast, the world the "
        "Autumn Budget 2024 package and its individually scored measures "
        "are measured against; counterfactual kind: the measures' pre-announcement legislated parameters.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_autumn_budget_2024",
            "counterfactual": "del_activity",
        },
        "obr_pre_measures_autumn_budget_2024__del_activity",
        "OBR's pre-measures October 2024 forecast, the world the "
        "Autumn Budget 2024 package and its individually scored measures "
        "are measured against; counterfactual kind: the pre-existing DEL activity/spending baseline.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_spring_statement_2025",
            "counterfactual": "policy_parameters",
        },
        "obr_pre_measures_spring_statement_2025__policy_parameters",
        "OBR's pre-measures March 2025 forecast, the world the "
        "Spring Statement 2025 package and its individually scored measures "
        "are measured against; counterfactual kind: the measures' pre-announcement legislated parameters.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_spring_statement_2025",
            "counterfactual": "regulatory",
        },
        "obr_pre_measures_spring_statement_2025__regulatory",
        "OBR's pre-measures March 2025 forecast, the world the "
        "Spring Statement 2025 package and its individually scored measures "
        "are measured against; counterfactual kind: the pre-existing regulatory baseline.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_pre_measures_autumn_budget_2025",
            "counterfactual": "policy_parameters",
        },
        "obr_pre_measures_autumn_budget_2025__policy_parameters",
        "OBR's pre-measures November 2025 forecast, the world the "
        "Autumn Budget 2025 package and its individually scored measures "
        "are measured against; counterfactual kind: the measures' pre-announcement legislated parameters.",
        "policy_ref",
        "sources/obr-policy-effects/source.json (baseline_key) plus the "
        "per-row baseline / baseline_counterfactual / baseline_locator "
        "the adapter emits from the vendored workbooks; descriptor "
        "stamped by scorecard_db/ingest_obr_policy_effects.py "
        "(_baseline_descriptor).",
    ),
    (
        {
            "policy": "obr_november_2025_budget_forecast",
            "counterfactual": "policy_parameters",
        },
        "obr_november_2025_budget_forecast__policy_parameters",
        "The OBR's November 2025 Budget forecast — the counterfactual "
        "March 2026 Table B.1 names in its own title ('Total effect of "
        "Government decisions SINCE the November 2025 Budget'). A "
        "post-measures world, deliberately not a pre-measures one.",
        "policy_ref",
        "EFO March 2026, Annex B Table B.1 title, vendored at "
        "sources/obr-policy-effects/raw/efo_march2026_annex_tables.xlsx; "
        "descriptor stamped by "
        "scorecard_db/ingest_obr_policy_effects.py (_baseline_descriptor).",
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


def register_baselines_txn(db: ScorecardDB) -> int:
    """Registration gate with the CALLER owning the transaction: bare
    executes and loud raises, never a commit. Ingests run this INSIDE
    the same write transaction as their claims, so an unregistered
    baseline world rolls the whole replacement back — the gate guards
    persistence itself, not just the state after a commit. (SQLite's
    connection context manager commits the open transaction on exit,
    which is why nothing here may open a nested `with db.conn:`.)"""
    for descriptor, label, description, framework, provenance in BASELINES:
        db.conn.execute(
            BASELINE_SQL,
            (
                baseline_key(descriptor),
                label,
                description,
                framework,
                None,
                provenance,
            ),
        )
    # Convergence: a row this module no longer defines is pruned — but
    # never while data still references it (that would silently orphan
    # provenance; the disavowal must first re-key the data).
    defined = {baseline_key(d) for d, *_ in BASELINES}
    for row in db.conn.execute("SELECT baseline_key, label FROM baselines").fetchall():
        if row["baseline_key"] in defined:
            continue
        referenced = db.conn.execute(
            "SELECT COUNT(*) FROM ("
            "  SELECT baseline_key FROM external_scores"
            "  UNION ALL SELECT baseline_key FROM pe_results"
            "  UNION ALL SELECT baseline_key FROM pe_exhibits)"
            " WHERE baseline_key = ?",
            (row["baseline_key"],),
        ).fetchone()[0]
        if referenced:
            raise ValueError(
                f"registry row {row['label']!r} is no longer defined but "
                f"{referenced} data rows still reference it — re-key the "
                "data before disavowing the world"
            )
        db.conn.execute(
            "DELETE FROM baselines WHERE baseline_key = ?",
            (row["baseline_key"],),
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


def register_baselines(db: ScorecardDB) -> int:
    """Standalone form of the gate: owns its transaction — registry
    upserts and prunes commit on success, roll back together on a gate
    failure."""
    with db.conn:
        return register_baselines_txn(db)


# The stacked OBBBA runs execute one distinct world per (chain,
# provision): current law plus the provisions above that one in that
# chain. Enumerated deliberately from the canonical provision map — 18
# provisions x 2 chains — rather than laundered into a single family key
# (the earlier jcx_stack_position entry is disavowed and removed).
from .ingest_reform_validation import (  # noqa: E402
    OBBBA_PROVISIONS,
    stack_baseline_descriptor,
)

_CHAIN_DESCRIPTIONS = {
    "f0af251": (
        "f0af251's own chained scoring — through the pre-scope-fix "
        "exemption row and a separate senior-deduction link"
    ),
    "jcx_producer": "the buildi+ stacked producer, JCX order",
}
for _chain, _chain_desc in _CHAIN_DESCRIPTIONS.items():
    for _pid in OBBBA_PROVISIONS:
        BASELINES.append(
            (
                stack_baseline_descriptor(
                    {"f0af251": "stacked_chained", "jcx_producer": "jcx_stacked"}[
                        _chain
                    ],
                    _pid,
                ),
                f"obbba_stack_below__{_chain}__{_pid}",
                f"Current law plus the OBBBA provisions above {_pid} in "
                f"{_chain_desc}; the run's construction string carries the "
                "chain position.",
                "policy_ref",
                "Producer stack notes and verified chaining "
                "(sources/populace-reform-validation/raw artifacts; the #24 "
                "review record); stamped by "
                "scorecard_db/ingest_reform_validation.py.",
            )
        )
