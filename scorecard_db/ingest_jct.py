"""Ingest the JCT conventional revenue tables (2026-08-02 harvest).

Seven JCX tables, per-provision × FY2025-2034, staged with horizontal
checksums and column-count validation (see sources/harvest-2026-08-02/jct/
NOTES.md). Values are verbatim table cells × 1e6 (tables are in $ millions).

Reform worlds: one policy_ref per bill version. JCX-30-25 and JCX-31-25
score the SAME Senate manager's-amendment text against two baselines —
current policy vs present law — so they share a reform slug and differ in
ReformRef.baseline (the twins the COLLATION calls out). JCX-29-25 is the
third non-current-law-baseline source of the night.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import (
    finish,
    load_staged,
    parse_window,
    policy_ref,
    require_fields,
    with_baseline_condition,
)
from .models import ExternalScore, Metric, TimeBasis, UnitConcept

CURRENT_POLICY = {"policy": "current_policy"}

# JCX id -> (reform slug, baseline descriptor, staged-baseline expectation)
# JCX-35-25 scores the Senate-passed Title VII text, which the House
# passed verbatim and became P.L. 119-21 — the same enacted-Title-VII
# world TPC scores in T25-0229/0236 and T26-0009 (COLLATION's
# "enacted-OBBBA triangle" joins on this key).
BILL_VERSIONS = {
    "JCX-35-25": ("obbba_enacted_title_vii", None, "present_law"),
    "JCX-31-25": ("obbba_senate_managers_20250628", None, "present_law"),
    "JCX-30-25": (
        "obbba_senate_managers_20250628", CURRENT_POLICY, "current_policy",
    ),
    "JCX-29-25": (
        "obbba_senate_finance_substitute", CURRENT_POLICY, "current_policy",
    ),
    # Tax provisions of the House-passed bill — the tax-title slice of
    # the whole-bill world (obbba_house_passed_20250522) PWBM/BL score.
    "JCX-26-25R": ("obbba_house_passed_tax_provisions", None, "present_law"),
    "JCX-22-25R": ("obbba_house_wm_reported_202505", None, "present_law"),
    "JCX-19-25": ("obbba_house_wm_markup_20250513", None, None),
}

_KNOWN_FIELDS = frozenset(
    {
        "source", "source_model", "proposed_metric", "unit_concept",
        "value_kind", "period", "time_basis", "value", "value_verbatim",
        "source_column", "row_kind", "effective_verbatim", "conditions",
        "reform_hint", "publication", "calibration_relationship", "note",
    }
)
_KNOWN_CONDITIONS = frozenset(
    {"provision", "bill_version", "table_section", "baseline", "fy_span"}
)


def stage_scores() -> list[ExternalScore]:
    scores = []
    for row in load_staged("jct"):
        require_fields(row, _KNOWN_FIELDS, "jct")
        staged_conds = row["conditions"]
        unknown = set(staged_conds) - _KNOWN_CONDITIONS
        if unknown:
            raise ValueError(f"jct: unmapped conditions {sorted(unknown)}")
        if row["proposed_metric"] != "revenue_change":
            raise ValueError(f"jct: unmapped metric {row['proposed_metric']}")
        if row["calibration_relationship"] != "held_out":
            raise ValueError("jct: unexpected calibration relationship")

        jcx = staged_conds["bill_version"]
        slug, baseline, expect_baseline = BILL_VERSIONS[jcx]
        staged_baseline = staged_conds.get("baseline")
        if staged_baseline is not None and staged_baseline != expect_baseline:
            raise ValueError(
                f"jct: {jcx} staged baseline {staged_baseline!r} contradicts "
                f"registry {expect_baseline!r}"
            )
        # Descriptor stays minimal (policy-world identity only) so the
        # same world keys identically across sources: JCX-30/31 share the
        # manager's-amendment slug (differing only in baseline), and TPC's
        # manager's-amendment distributions join the JCX-31 reform key.
        reform = policy_ref(slug, baseline=baseline)

        conditions = {
            "geography": "US",
            "provision": staged_conds["provision"],
            "bill_version": jcx,
            "row_kind": row["row_kind"],
        }
        if "table_section" in staged_conds:
            conditions["table_section"] = staged_conds["table_section"]
        with_baseline_condition(conditions, reform)

        period_start = period_end = None
        if "fy_span" in staged_conds:
            period_start, period_end = parse_window(staged_conds["fy_span"])
            if row["period"] != period_end:
                raise ValueError(
                    f"jct: span row period {row['period']} != window end "
                    f"{period_end}"
                )
            conditions["window_kind"] = "total"

        publication = dict(row["publication"])
        publication["value_verbatim"] = row["value_verbatim"]
        if row["effective_verbatim"]:
            publication["effective"] = row["effective_verbatim"]
        if row["note"]:
            publication["note"] = row["note"]

        scores.append(
            ExternalScore(
                source="jct",
                source_model=row["source_model"],
                metric=Metric.REVENUE_CHANGE,
                unit_concept=UnitConcept(row["unit_concept"]),
                period=row["period"],
                time_basis=TimeBasis(row["time_basis"]),
                value=row["value"],
                conditions=conditions,
                reform=reform,
                source_column=row["source_column"],
                publication=publication,
                value_kind=row["value_kind"],
                period_start=period_start,
                period_end=period_end,
            )
        )
    return finish(scores, "jct")


def ingest(db_path: Path) -> dict:
    scores = stage_scores()
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "jct-reform-scores",
        "ingested",
        f"{n} claims across 7 JCX conventional tables (per-provision × "
        "FY2025-34; JCX-29/30 vs current-policy baseline); JCX-45-25 "
        "tax-expenditure report pending coordinate-aware parser",
        "2026-08-02",
    )
    db.close()
    return {"scores": n}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
