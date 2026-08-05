"""Ingest the Penn Wharton Budget Model staged claims (2026-08-02 harvest).

OBBBA signed/House scores (incl. Table 3 primary-deficit rows), SS-benefit
taxation elimination, KYPA/WATCA, and option sets scored against a
TCJA-extension baseline (QBI, top-rate, corporate SALT, buybacks, PTC).

Normalizations: distribution percent-changes are staged as fractions
(unit_note "fraction; …") -> ×100 to PERCENT; dollar averages are per
HOUSEHOLD (unit_note "USD per household") -> USD_PER_HOUSEHOLD, with
group-aggregate vs median riding conditions["statistic"]. Revenue and
deficit rows were already normalized from billions by the stager; the
tariff-workbook rows keep their UNITS-INFERRED flag in
publication["unit_note"].
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

TCJA_EXTENSION = {"policy": "tcja_extension"}
PRE_2025_TARIFFS = {"policy": "current_law_pre_2025_tariffs"}

# reform_hint -> (policy slug, baseline descriptor, options come from
# which staged condition key). Option-carrying condition values are folded
# into the reform descriptor (they define distinct worlds) and mirrored to
# conditions["option"].
REFORMS = {
    "One Big Beautiful Bill Act (FY2025 reconciliation bill as signed July 4, 2025)": (
        "obbba_enacted_pl119_21",
        None,
        None,
    ),
    "One Big Beautiful Bill Act (House budget reconciliation proposals, May 2025)": (
        "obbba_house_proposals_202505",
        None,
        None,
    ),
    "One Big Beautiful Bill Act (House reconciliation bill, May 19 2025 version)": (
        "obbba_house_20250519",
        None,
        None,
    ),
    "One Big Beautiful Bill Act (House-passed reconciliation bill, May 22 2025)": (
        "obbba_house_passed_20250522",
        None,
        None,
    ),
    "Eliminate income taxation of Social Security benefits": (
        "ss_benefits_tax_elimination",
        None,
        None,
    ),
    "Keep Your Pay Act (full package including top ordinary rate increase)": (
        "kypa_full_package",
        None,
        None,
    ),
    "Keep Your Pay Act (standard deduction increase + CTC expansion + EITC"
    " expansion)": ("kypa_tax_provisions", None, None),
    "Keep Your Pay Act (three tax-cut provisions, excluding top-rate increase)": (
        "kypa_tax_provisions",
        None,
        None,
    ),
    "Working Americans' Tax Cut Act (alternative maximum tax + millionaire surtax)": (
        "watca",
        None,
        None,
    ),
    "Section 199A QBI deduction reform options (against TCJA-extension baseline)": (
        "qbi_199a_options",
        TCJA_EXTENSION,
        "reform_option",
    ),
    "Top ordinary rate increase options (against TCJA-extension baseline)": (
        "top_rate_increase_options",
        TCJA_EXTENSION,
        "reform_option",
    ),
    "Limit corporate SALT deductions to $10,000 (against TCJA-extension baseline)": (
        "corporate_salt_10k_cap",
        TCJA_EXTENSION,
        "tax_base_variant",
    ),
    "Raise stock buyback excise tax rate (against TCJA-extension baseline)": (
        "buyback_excise_increase",
        TCJA_EXTENSION,
        "reform_option",
    ),
    "Remove limitation on repayment of excess premium tax credits (against"
    " TCJA-extension baseline)": ("ptc_repayment_limit_removal", TCJA_EXTENSION, None),
    "All U.S. tariffs in effect as of June 10, 2025 (vs. pre-2025 tariff policy)": (
        "tariffs_in_effect_20250610",
        PRE_2025_TARIFFS,
        None,
    ),
}

_KNOWN_FIELDS = frozenset(
    {
        "source",
        "source_model",
        "calibration_relationship",
        "publication",
        "table_ref",
        "csv",
        "status",
        "unit_concept",
        "value_kind",
        "period",
        "time_basis",
        "value",
        "conditions",
        "reform_hint",
        "source_column",
        "unit_note",
        "metric",
        "proposed_metric",
    }
)
_KNOWN_CONDITIONS = frozenset(
    {
        "scoring",
        "income_group",
        "income_concept",
        "provision",
        "statistic",
        "baseline_policy",
        "reform_option",
        "package_variant",
        "aggregation",
        "budget_window",
        "tax_base_variant",
        "revenue_type",
        "policy_vintage",
    }
)


def _metric_unit(row) -> tuple[Metric, UnitConcept, float, str]:
    name = row.get("metric") or row["proposed_metric"]
    value, note = row["value"], row["unit_note"]
    if name == "revenue_change":
        return Metric.REVENUE_CHANGE, UnitConcept.USD, value, "usd"
    if name == "primary_deficit_change":
        return Metric.PRIMARY_DEFICIT_CHANGE, UnitConcept.USD, value, "usd"
    if name == "pct_change_after_tax_income":
        if not note.startswith("fraction"):
            raise ValueError(f"pwbm: pct row not staged as fraction: {note}")
        return (
            Metric.PCT_CHANGE_AFTER_TAX_INCOME,
            UnitConcept.PERCENT,
            value * 100.0,
            "share",
        )
    if name in (
        "avg_tax_change_usd",
        "avg_change_after_tax_income_usd",
        "avg_change_after_tax_transfer_income_usd",
    ):
        if "per household" not in note:
            raise ValueError(f"pwbm: avg row unit unclear: {note}")
        metric = (
            Metric.AVG_TAX_CHANGE_USD
            if name == "avg_tax_change_usd"
            else Metric.AVG_CHANGE_AFTER_TAX_INCOME_USD
        )
        return metric, UnitConcept.USD_PER_HOUSEHOLD, value, "usd"
    raise ValueError(f"pwbm: unmapped metric {name}")


def stage_scores() -> list[ExternalScore]:
    scores = []
    for row in load_staged("pwbm"):
        require_fields(row, _KNOWN_FIELDS, "pwbm")
        staged_conds = dict(row["conditions"])
        unknown = set(staged_conds) - _KNOWN_CONDITIONS
        if unknown:
            raise ValueError(f"pwbm: unmapped conditions {sorted(unknown)}")
        if row["calibration_relationship"] != "held_out":
            raise ValueError("pwbm: unexpected calibration relationship")

        slug, baseline, option_key = REFORMS[row["reform_hint"]]
        staged_baseline = staged_conds.pop("baseline_policy", None)
        expects_tcja = baseline is TCJA_EXTENSION
        if (staged_baseline == "tcja_extension") != expects_tcja:
            raise ValueError(
                f"pwbm: staged baseline_policy {staged_baseline!r} "
                f"contradicts registry for {row['reform_hint']!r}"
            )
        detail = {}
        if option_key:
            detail["option"] = staged_conds.pop(option_key)
        reform = policy_ref(slug, baseline=baseline, **detail)

        # package_variant is descriptive of the full-package slug; verify
        # and drop rather than carrying a redundant axis.
        variant = staged_conds.pop("package_variant", None)
        if variant is not None and (
            variant != "with_top_rate_increase" or slug != "kypa_full_package"
        ):
            raise ValueError(f"pwbm: unexpected package_variant {variant}")

        metric, unit, value, value_kind = _metric_unit(row)

        # avg-income-change rows must carry the income concept that the
        # two staged metric names encode.
        if metric is Metric.AVG_CHANGE_AFTER_TAX_INCOME_USD:
            expected = (
                "after_tax_and_transfer_income"
                if row["proposed_metric"].startswith("avg_change_after_tax_transfer")
                else "after_tax_income"
            )
            if staged_conds.get("income_concept") != expected:
                raise ValueError(
                    "pwbm: income_concept missing or inconsistent on "
                    f"{row['proposed_metric']}"
                )

        conditions = {"geography": "US"}
        for key in (
            "scoring",
            "income_group",
            "income_concept",
            "provision",
            "statistic",
            "revenue_type",
            "policy_vintage",
        ):
            if key in staged_conds:
                conditions[key] = staged_conds.pop(key)
        if "option" in detail:
            conditions["option"] = detail["option"]
        with_baseline_condition(conditions, reform)

        period_start = period_end = None
        window = staged_conds.pop("budget_window", None)
        aggregation = staged_conds.pop("aggregation", None)
        if (window is None) != (aggregation is None):
            raise ValueError("pwbm: budget_window and aggregation must pair")
        if window is not None:
            if aggregation != "window_total":
                raise ValueError(f"pwbm: unexpected aggregation {aggregation}")
            period_start, period_end = parse_window(window)
            if row["period"] != period_end:
                raise ValueError(
                    f"pwbm: window row period {row['period']} != end {period_end}"
                )
            conditions["window_kind"] = "total"
        if staged_conds:
            raise ValueError(f"pwbm: unconsumed conditions {sorted(staged_conds)}")

        publication = dict(row["publication"])
        publication["table"] = row["table_ref"]
        publication["staged_csv"] = row["csv"]
        publication["unit_note"] = row["unit_note"]

        scores.append(
            ExternalScore(
                source="pwbm",
                source_model=row["source_model"],
                metric=metric,
                unit_concept=unit,
                period=row["period"],
                time_basis=TimeBasis(row["time_basis"]),
                value=value,
                conditions=conditions,
                reform=reform,
                source_column=row["source_column"],
                publication=publication,
                value_kind=value_kind,
                status=row["status"],
                period_start=period_start,
                period_end=period_end,
            )
        )
    return finish(scores, "pwbm")


def ingest(db_path: Path) -> dict:
    scores = stage_scores()
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "pwbm-reform-scores",
        "ingested",
        f"{n} claims: OBBBA signed/House (incl. primary-deficit Table 3), "
        "SS-benefit-tax elimination, KYPA/WATCA, TCJA-extension-baseline "
        "option sets; distribution income concept is after-tax-and-transfer",
        "2026-08-02",
    )
    db.close()
    return {"scores": n}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
