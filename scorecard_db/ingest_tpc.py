"""Ingest the TPC T-series staged claims (2026-08-02 harvest).

35 tables staged; the 468 "tax benefit of provision X" family rows
(aggregate/avg/share-of benefit) are beyond the validation vocabulary and
are DROPPED with a tally, per the harvest flag (beyond_mission_vocab).

Reform registry is keyed on table_id, with three file-internal-truth
overrides verified against the sha256-manifested workbooks:

- T26-0010: the taxpolicycenter.org page titles it "Options to Expand the
  Child Tax Credit"; the workbook it serves is internally "T26-0010 —
  Trump Administration Tariffs Announced From January 20, 2025 Through
  April 02, 2026, Baseline: Current Law with Pre-2025 Tariffs". Rows are
  tariff rows; the registry follows the FILE. (External-issue diagnosis
  seed: TPC page/file mismatch.)
- T26-0112 / T26-0113: staged baseline_hint says "assumed, not stated" —
  the workbooks state "Baseline: Current Law With Pre-2025 Tariffs".

Cross-source reform keys: JCX-35-25 / T25-0229 / T25-0236 / T26-0009 all
score the enacted Title VII text (obbba_enacted_title_vii); the
manager's-amendment distributions join JCX-31-25's world
(obbba_senate_managers_20250628).
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import (
    finish,
    load_staged,
    merge_republications,
    parse_window,
    policy_ref,
    require_fields,
    with_baseline_condition,
)
from .models import ExternalScore, Metric, TimeBasis, UnitConcept

SENATE_VII = {"policy": "current_law_plus_senate_obbba_title_vii"}
PRE_OBBBA = {"policy": "pre_obbba_law"}
PRE_2025_TARIFFS = {"policy": "current_law_pre_2025_tariffs"}

MANAGERS = "obbba_senate_managers_20250628"
ENACTED_VII = "obbba_enacted_title_vii"

# table_id -> (slug, baseline descriptor, descriptor detail,
#              expected staged baseline_hint prefix)
TABLES = {
    "T25-0209": (
        "obbba_senate_ctc_top_rate_options",
        SENATE_VII,
        None,
        "Baseline: Current Law Plus Enactment",
    ),
    "T25-0215": (
        "ctc_2500_max_refundable_2000_indexed",
        SENATE_VII,
        None,
        "Baseline: Current Law Plus Enactment",
    ),
    **{
        f"T25-{n:04d}": (MANAGERS, None, None, "Baseline: Current Law")
        for n in range(217, 227)
    },
    "T25-0227": (
        MANAGERS,
        None,
        {"scope": "provisions_effective_2025"},
        "Baseline: Current Law",
    ),
    "T25-0229": (ENACTED_VII, None, None, "Baseline: Current Law"),
    "T25-0236": (ENACTED_VII, None, None, "Baseline: Current Law"),
    "T25-0366": (
        "trump_tariffs_announced_20250120_20251023",
        PRE_2025_TARIFFS,
        None,
        "Baseline: Current Law with Pre-2025 Tariffs",
    ),
    "T26-0010": (
        # File-internal truth (see module docstring); page title is wrong.
        "trump_tariffs_announced_20250120_20260402",
        PRE_2025_TARIFFS,
        None,
        "Baseline: Current Law (assumed, not stated)",
    ),
    "T26-0014": ("family_first_act", None, None, "Baseline: Current Law"),
    "T26-0016": ("family_first_act", None, None, "Baseline: Current Law"),
    "T26-0022": ("wptra", None, None, "Baseline: Current Law"),
    "T26-0024": ("wptra", None, None, "Baseline: Current Law"),
    "T26-0027": (
        "wptra_plus_min_eitc_under4",
        None,
        None,
        "Baseline: Current Law",
    ),
    "T26-0028": (
        "wptra_plus_min_eitc_under4",
        None,
        None,
        "Baseline: Current Law",
    ),
    "T26-0029": (
        "american_family_act_119th",
        None,
        None,
        "Baseline: Current Law",
    ),
    "T26-0030": (
        "american_family_act_119th",
        None,
        None,
        "Baseline: Current Law",
    ),
    "T26-0031": (
        "american_family_act_119th",
        None,
        None,
        "Baseline: Current Law",
    ),
    "T26-0087": (
        "obbba_extend_certain_provisions",
        None,
        None,
        "Baseline: Current Law",
    ),
    "T26-0112": (
        # Workbook states the baseline; staged hint said "assumed".
        "trump_tariffs_announced_20250120_20260723",
        PRE_2025_TARIFFS,
        None,
        "Baseline: Current Law (assumed, not stated)",
    ),
    "T26-0113": (
        "trump_tariffs_announced_20250120_20260723",
        PRE_2025_TARIFFS,
        None,
        "Baseline: Current Law (assumed, not stated)",
    ),
    "T26-0126": (
        "obbba_extend_salt_limit_increase",
        None,
        None,
        "Baseline: Current Law",
    ),
}

# Staged rows verified DEFECTIVE against the manifested artifact — held
# out of the DB pending re-harvest, never ingested wrong.
EXCLUDED_TABLES = {
    "T26-0009": (
        "workbook is the OBBBA-by-racial/ethnic-group set (five sheets: "
        "All + White/Black/Hispanic/Additional Races, each a baseline "
        "panel plus a tax-change panel); staging collapsed the race axis "
        "and mixed dollar columns into pct rows (e.g. 1020.0 staged as "
        "percent). Needs a per-sheet coordinate-aware re-parse."
    ),
}

INCOME_AXES = {
    "Expanded Cash Income Percentile 2,": "Expanded Cash Income Percentile",
    "Tax Units with a Tax Increase or Tax Cut, by Expanded Cash Income"
    " Percentile, 2025": "Expanded Cash Income Percentile",
    "Distribution of Federal Tax Change by Expanded Cash Income"
    " Percentile,": "Expanded Cash Income Percentile",
    "Expanded Cash Income Level (thousands of 2025 dollars)": "Expanded Cash Income Level (thousands of 2025 dollars)",
}

METRICS = {
    ("revenue_change", "usd_billions"): (
        Metric.REVENUE_CHANGE,
        UnitConcept.USD,
        1e9,
        "usd",
    ),
    ("avg_tax_change_usd", "usd_per_tax_unit"): (
        Metric.AVG_TAX_CHANGE_USD,
        UnitConcept.USD_PER_TAX_UNIT,
        1,
        "usd",
    ),
    ("pct_change_after_tax_income", "percent"): (
        Metric.PCT_CHANGE_AFTER_TAX_INCOME,
        UnitConcept.PERCENT,
        1,
        "share",
    ),
    ("share_with_tax_cut", "percent_of_tax_units"): (
        Metric.SHARE_WITH_TAX_CUT,
        UnitConcept.PERCENT,
        1,
        "share",
    ),
}

_KNOWN_FIELDS = frozenset(
    {
        "proposed_metric",
        "proposed_unit",
        "value",
        "conditions",
        "source_column",
        "value_unrounded",
        "period",
        "time_basis",
        "source",
        "source_model",
        "table_id",
        "reform_hint",
        "baseline_hint",
        "calibration_relationship",
        "publication",
        "beyond_mission_vocab",
        "period_span",
    }
)
_KNOWN_CONDITIONS = frozenset(
    {"geography", "income_group", "income_axis", "provision_row", "option"}
)


def stage_scores() -> tuple[list[ExternalScore], dict]:
    scores = []
    dropped = {"benefit_family": 0, "defective_staging": 0}
    for row in load_staged("tpc"):
        require_fields(row, _KNOWN_FIELDS, "tpc")
        if row.get("beyond_mission_vocab"):
            dropped["benefit_family"] += 1
            continue
        if row["table_id"] in EXCLUDED_TABLES:
            dropped["defective_staging"] += 1
            continue
        staged_conds = dict(row["conditions"])
        unknown = set(staged_conds) - _KNOWN_CONDITIONS
        if unknown:
            raise ValueError(f"tpc: unmapped conditions {sorted(unknown)}")
        if row["calibration_relationship"] != "held_out":
            raise ValueError("tpc: unexpected calibration relationship")
        if staged_conds.pop("geography") != "US":
            raise ValueError("tpc: unexpected geography")

        table_id = row["table_id"]
        slug, baseline, detail, expected_hint = TABLES[table_id]
        if not row["baseline_hint"].startswith(expected_hint):
            raise ValueError(
                f"tpc: {table_id} baseline_hint drifted: {row['baseline_hint']!r}"
            )
        detail = dict(detail or {})
        if "option" in staged_conds:
            detail["option"] = staged_conds["option"]
        reform = policy_ref(slug, baseline=baseline, **detail)

        metric, unit, scale, value_kind = METRICS[
            (row["proposed_metric"], row["proposed_unit"])
        ]

        conditions = {"geography": "US"}
        if "income_group" in staged_conds:
            conditions["income_group"] = staged_conds["income_group"]
            conditions["income_axis"] = INCOME_AXES[staged_conds["income_axis"]]
        if "provision_row" in staged_conds:
            conditions["provision"] = staged_conds["provision_row"]
        if "option" in staged_conds:
            conditions["option"] = staged_conds["option"]
        with_baseline_condition(conditions, reform)

        period = row["period"]
        period_start = period_end = None
        if row.get("period_span"):
            period_start, period_end = parse_window(row["period_span"])
            # FY-total rows stage period as None (or a stray pub-year
            # anchor below the window, e.g. T25-0366's 2025).
            if period is not None and period != period_end:
                if period >= period_start:
                    raise ValueError(
                        f"tpc: span row period {period} inside window "
                        f"{row['period_span']}"
                    )
            period = period_end
            conditions["window_kind"] = "total"

        publication = dict(row["publication"])
        publication["table_id"] = table_id
        if row.get("value_unrounded") is not None:
            publication["value_unrounded"] = row["value_unrounded"]

        scores.append(
            ExternalScore(
                source="tpc",
                source_model=row["source_model"],
                metric=metric,
                unit_concept=unit,
                period=period,
                time_basis=TimeBasis(row["time_basis"]),
                value=row["value"] * scale,
                conditions=conditions,
                reform=reform,
                source_column=row["source_column"],
                publication=publication,
                value_kind=value_kind,
                period_start=period_start,
                period_end=period_end,
            )
        )
    # The Senate-OBBBA block publishes average tax change twice per
    # (axis, period): once in the distribution table, once in the
    # cut/increase table. Same statistic, same published value — keep the
    # row that carries TPC's unrounded twin.
    merged = merge_republications(
        scores,
        "tpc",
        precision=lambda s: (
            "value_unrounded" in s.publication,
            s.publication["table_id"],
        ),
        tolerance=lambda coarse: 0.0,
    )
    return finish(merged, "tpc"), dropped


def ingest(db_path: Path) -> dict:
    scores, dropped = stage_scores()
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "tpc-distribution",
        "ingested",
        f"{n} claims from 21 T-series tables (Senate-OBBBA distributions, "
        f"CTC/AFA/WPTRA sets, tariffs); dropped: "
        f"{dropped['benefit_family']} tax-benefit-family rows (beyond "
        f"vocab), {dropped['defective_staging']} T26-0009 rows (by-race "
        "workbook, staging defect — re-harvest); T26-0010 page/file "
        "mismatch keyed off workbook-internal table (external-issue seed)",
        "2026-08-02",
    )
    db.close()
    return {"scores": n, "dropped": dropped}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
