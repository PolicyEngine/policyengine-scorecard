"""Ingest the Budget Lab (Yale) staged claims (2026-08-02 harvest).

Nine publications, each with its own world structure:

- Reconciliation distributional workbook (F1/F2/AF1): % change in
  after-tax-AND-transfer income by quintile × {Medicaid, SNAP, Taxes, Net}
  — the transfer-side complement nobody else publishes. Whole-bill worlds
  (House-passed; Senate June-28 text; Senate + Scott proposal), average
  annual over 2026-2034.
- Combined tax-provision distribution (2025-06-30, so "Senate" = the
  June-28 text): TCJA-extension-as-reform, full House/Senate tax packages
  vs current law, and changes-on-top-of-TCJA-extension variants (baseline
  tcja_extension as ReformRef.baseline).
- Financial Cost of the Senate-Passed Bill: by-title conventional effects
  for the as-passed world and a made-permanent variant, over three decade
  windows.
- CTC options workbook: 16 scenarios under current law (T2) and as
  permanent variants (T4), plus revised select options (T3/T5) with
  explicit non-current-law baselines (TCJA CTC / TCJA extension) and
  vs-Option-1 increments. Option labels stay verbatim (T3/T5 renumber).
- Standalone OBBBA provision distributions (House/Senate variants).
- KYPA / WATCA (worlds shared with PWBM's kypa_full_package / watca).
- OBBBA + tariffs combined distribution (effects via CBO + TBL tariff
  model).
- Capital-gains basis indexing (prospective / retrospective), whose
  decade windows beyond the budget window are label-only ("Second
  Decade") and stay conditions-only because the workbook does not state
  the years.

Values: revenue rows staged verbatim in billions -> ×1e9; percent rows
already normalized per-row by the stager (value_raw fraction kept in the
vendored staging).
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import (
    billions,
    finish,
    load_staged,
    merge_republications,
    parse_window,
    policy_ref,
    require_fields,
    with_baseline_condition,
)
from .models import ExternalScore, Metric, ReformRef, TimeBasis, UnitConcept

TCJA_EXTENSION = {"policy": "tcja_extension"}
TCJA_CTC = {"policy": "tcja_ctc"}

_KNOWN_FIELDS = frozenset(
    {
        "source", "source_model", "calibration_relationship",
        "geography_note", "proposed_metric", "proposed_unit", "value",
        "value_raw", "normalization", "period", "time_basis", "conditions",
        "reform_hint", "source_column", "source_table", "publication",
        "parse_confidence", "sign_convention", "period_note",
        "period_window", "time_note", "concept_note",
    }
)
_KNOWN_CONDITIONS = frozenset(
    {
        "geography", "estimate_type", "universe", "income_group",
        "scenario", "provision", "period_window", "bill_version",
        "income_measure", "provision_component", "reform_label", "baseline",
        "bill_component", "age_group",
        "average_income_after_transfers_taxes_usd",
    }
)

_INCOME_MEASURES = {
    "AGI-based expanded income, after-tax-and-transfer": (
        "agi_expanded_income", "after_tax_and_transfer_income",
    ),
    "AGI-based expanded income, after-tax": (
        "agi_expanded_income", "after_tax_income",
    ),
    # The combined OBBBA+tariffs figure defines its own denominator; keep
    # the definition verbatim as the axis.
    "household resources as % of current-law income after transfers and"
    " taxes": (
        "household resources as % of current-law income after transfers"
        " and taxes",
        "after_tax_and_transfer_income",
    ),
}

_BASELINES = {
    "Relative to Current Law": None,
    "TCJA extension (current policy)": TCJA_EXTENSION,
    "Relative to TCJA Extension": TCJA_EXTENSION,
    "Relative to TCJA CTC": TCJA_CTC,
}


def _reform(row) -> ReformRef:
    """Resolve the policy world per publication family. Every branch is
    exhaustive for its family; anything unrecognized raises."""
    title = row["publication"]["title"]
    hint = row["reform_hint"]
    conds = row["conditions"]
    baseline_cond = conds.get("baseline")

    if title.startswith("Distributional Effects of Selected Provisions"):
        worlds = {
            "House-passed reconciliation bill (One Big Beautiful Bill Act),"
            " major spending and tax provisions": "obbba_house_passed_20250522",
            "Senate reconciliation bill, major spending and tax provisions":
                "obbba_senate_bill_20250628",
            "Amended Senate reconciliation bill (with Scott proposal), major"
            " spending and tax provisions":
                "obbba_senate_bill_20250628_plus_scott",
        }
        return policy_ref(worlds[hint])

    if title.startswith("Tax Provisions in the Reconciliation Bill"):
        worlds = {
            "Reconciliation bill tax provisions, variant: TCJA Extension:"
            " Total Impact": ("tcja_extension", None),
            "Reconciliation bill tax provisions, variant: House: Total": (
                "obbba_house_passed_tax_provisions", None,
            ),
            "Reconciliation bill tax provisions, variant: Senate: Total": (
                "obbba_senate_managers_20250628", None,
            ),
            "Reconciliation bill tax provisions, variant: House: Changes on"
            " Top of TCJA Extension": (
                "obbba_house_tax_beyond_tcja", TCJA_EXTENSION,
            ),
            "House reconciliation bill: additional tax provisions relative"
            " to TCJA extension": (
                "obbba_house_tax_beyond_tcja", TCJA_EXTENSION,
            ),
            "Reconciliation bill tax provisions, variant: House: Individual"
            " Tax Changes on Top of TCJA Extension": (
                "obbba_house_individual_tax_beyond_tcja", TCJA_EXTENSION,
            ),
            "Reconciliation bill tax provisions, variant: Senate: Changes"
            " on Top of TCJA Extension": (
                "obbba_senate_tax_beyond_tcja", TCJA_EXTENSION,
            ),
            "Senate reconciliation bill: additional tax provisions relative"
            " to TCJA extension": (
                "obbba_senate_tax_beyond_tcja", TCJA_EXTENSION,
            ),
            "Reconciliation bill tax provisions, variant: Senate:"
            " Individual Tax Changes on Top of TCJA Extension": (
                "obbba_senate_individual_tax_beyond_tcja", TCJA_EXTENSION,
            ),
        }
        slug, baseline = worlds[hint]
        if baseline_cond is not None and _BASELINES[baseline_cond] != baseline:
            raise ValueError(
                f"budget_lab: staged baseline {baseline_cond!r} contradicts "
                f"hint mapping for {hint!r}"
            )
        return policy_ref(slug, baseline=baseline)

    if title.startswith("The Financial Cost of the Senate-Passed"):
        if "(As Passed)" in hint or ", as written" in hint:
            variant = "as_passed"
        elif "(Permanent)" in hint or ", permanent" in hint.lower():
            variant = "permanent"
        else:
            raise ValueError(f"budget_lab: unmapped cost hint {hint!r}")
        if hint.startswith("Senate 2025 reconciliation bill") or (
            "— Senate:" in hint
        ):
            slug = (
                "obbba_enacted_pl119_21"
                if variant == "as_passed"
                else "obbba_pl119_21_made_permanent"
            )
        elif "— House:" in hint:
            slug = (
                "obbba_house_passed_20250522"
                if variant == "as_passed"
                else "obbba_house_passed_made_permanent"
            )
        else:
            raise ValueError(f"budget_lab: unmapped cost hint {hint!r}")
        return policy_ref(slug)

    if title.startswith("Options for Expanding the Child Tax Credit"):
        option = conds["scenario"]
        table = row["source_table"].split(":")[0]
        slug = {
            "T2": "bl_ctc_option",
            "T3": "bl_ctc_option",
            "T4": "bl_ctc_option_permanent",
            "T5": "bl_ctc_option_permanent",
        }[table]
        if baseline_cond == "Relative to Option 1":
            baseline = {
                "policy": slug,
                "option": "1. TCJA CTC"
                if slug == "bl_ctc_option"
                else "1. TCJA Extension",
            }
        elif baseline_cond is not None:
            baseline = _BASELINES[baseline_cond]
        else:
            baseline = None
        return policy_ref(slug, baseline=baseline, option=option)

    if title.startswith("Standalone Distributional Effects"):
        return policy_ref(
            "obbba_provision_standalone",
            provision=conds["provision"],
            version=conds["bill_version"],
        )

    if title.startswith("Senator Booker's Keep Your Pay Act"):
        return policy_ref("kypa_full_package")

    if title.startswith("Senator Van Hollen"):
        return policy_ref("watca")

    if title.startswith("Combined Distributional Effects of the One Big"):
        return policy_ref("obbba_enacted_plus_2025_tariffs")

    if title.startswith("Indexing Capital Gains to Inflation"):
        worlds = {
            "Indexing capital gains basis to inflation — Prospective":
                "capgains_basis_indexing_prospective",
            "Indexing capital gains basis to inflation — Retrospective":
                "capgains_basis_indexing_retrospective",
        }
        return policy_ref(worlds[hint])

    raise ValueError(f"budget_lab: unmapped publication {title!r}")


def stage_scores() -> list[ExternalScore]:
    scores = []
    for row in load_staged("budget_lab"):
        require_fields(row, _KNOWN_FIELDS, "budget_lab")
        staged_conds = dict(row["conditions"])
        unknown = set(staged_conds) - _KNOWN_CONDITIONS
        if unknown:
            raise ValueError(
                f"budget_lab: unmapped conditions {sorted(unknown)}"
            )
        if row["calibration_relationship"] != "held_out":
            raise ValueError("budget_lab: unexpected relationship")
        if row.get("period_window") != staged_conds.get("period_window"):
            raise ValueError("budget_lab: period_window field/cond mismatch")

        metric_name = row["proposed_metric"]
        if metric_name == "revenue_change":
            if row["proposed_unit"] != "usd_billions":
                raise ValueError(
                    f"budget_lab: unexpected unit {row['proposed_unit']}"
                )
            metric, unit = Metric.REVENUE_CHANGE, UnitConcept.USD
            value, value_kind = billions(row["value"]), "usd"
            window_kind = "total"
        elif metric_name == "pct_change_after_tax_income":
            if row["proposed_unit"] != "percent":
                raise ValueError(
                    f"budget_lab: unexpected unit {row['proposed_unit']}"
                )
            metric, unit = (
                Metric.PCT_CHANGE_AFTER_TAX_INCOME, UnitConcept.PERCENT,
            )
            value, value_kind = row["value"], "share"
            window_kind = "annual_average"
        else:
            raise ValueError(f"budget_lab: unmapped metric {metric_name}")

        reform = _reform(row)

        conditions = {"geography": "US"}
        if staged_conds.pop("geography") != "us":
            raise ValueError("budget_lab: unexpected geography")
        for key in (
            "income_group", "universe", "provision", "provision_component",
            "bill_component", "bill_version", "age_group",
        ):
            if key in staged_conds:
                conditions[key] = staged_conds.pop(key)
        # Table 2b decomposes the FINANCE title; its "Total" is the Title
        # VII total (-3,296B), not the whole-bill total (-3,062B) — scope
        # its components so the two never share a claim.
        if (
            row["source_table"].startswith("T2b")
            and "bill_component" in conditions
        ):
            conditions["bill_component"] = (
                f"Title VII. Finance / {conditions['bill_component']}"
            )
        # The Financial-Cost and cap-gains scenario labels are consumed by
        # the world mapping (as-passed vs permanent; prospective vs
        # retrospective); the CTC options keep theirs as option below.
        if row["publication"]["title"].startswith(
            ("The Financial Cost", "Indexing Capital Gains")
        ):
            staged_conds.pop("scenario", None)
        if "income_measure" in staged_conds:
            axis, concept = _INCOME_MEASURES[
                staged_conds.pop("income_measure")
            ]
            conditions["income_axis"] = axis
            conditions["income_concept"] = concept
        if "scenario" in staged_conds:
            conditions["option"] = staged_conds.pop("scenario")
        estimate_type = staged_conds.pop("estimate_type", None)
        if estimate_type is not None:
            if not estimate_type.startswith("conventional budget"):
                raise ValueError(
                    f"budget_lab: unmapped estimate_type {estimate_type!r}"
                )
            conditions["scoring"] = "conventional"
            if "Budget Lab estimate" in estimate_type:
                conditions["estimate_attribution"] = "budget_lab"
        staged_conds.pop("reform_label", None)  # consumed by _reform
        staged_conds.pop("baseline", None)  # consumed by _reform
        with_baseline_condition(conditions, reform)

        period = row["period"]
        period_start = period_end = None
        window = staged_conds.pop("period_window", None)
        if window is not None:
            try:
                period_start, period_end = parse_window(window)
            except ValueError:
                # Label-only windows ("Budget Window", "Second Decade",
                # "Third Decade"): the workbook never states the years, so
                # they stay conditions-only rather than fabricated columns.
                conditions["period_window"] = window
                conditions["window_kind"] = "total"
            else:
                if period not in (period_start, period_end):
                    raise ValueError(
                        f"budget_lab: period {period} outside {window}"
                    )
                period = period_end
                conditions["window_kind"] = window_kind

        publication = dict(row["publication"])
        for key in (
            "source_table", "normalization", "sign_convention",
            "period_note", "time_note", "concept_note", "parse_confidence",
        ):
            if row.get(key):
                publication[key] = row[key]
        avg_income = staged_conds.pop(
            "average_income_after_transfers_taxes_usd", None
        )
        if avg_income is not None:
            publication["average_income_after_transfers_taxes_usd"] = (
                avg_income
            )
        if staged_conds:
            raise ValueError(
                f"budget_lab: unconsumed conditions {sorted(staged_conds)}"
            )

        scores.append(
            ExternalScore(
                source="budget_lab",
                source_model=row["source_model"],
                metric=metric,
                unit_concept=unit,
                period=period,
                time_basis=TimeBasis(row["time_basis"]),
                value=value,
                conditions=conditions,
                reform=reform,
                source_column=row["source_column"],
                publication=publication,
                value_kind=value_kind,
                period_start=period_start,
                period_end=period_end,
            )
        )
    merged = merge_republications(
        scores,
        "budget_lab",
        # The combined-distribution publication states the same
        # changes-on-top-of-TCJA comparison in Table 1 and Table 3.
        precision=lambda s: (
            "value_unrounded" in s.publication,
            s.publication.get("source_table", ""),
        ),
        tolerance=lambda coarse: max(1e-9, abs(coarse.value) * 5e-3),
    )
    return finish(merged, "budget_lab")


def ingest(db_path: Path) -> dict:
    scores = stage_scores()
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "budget-lab-scores",
        "ingested",
        f"{n} claims: reconciliation distributional workbook (transfer-"
        "side complement), 16-scenario CTC options under two baselines, "
        "provision-level House-vs-Senate distributions, KYPA/WATCA, "
        "cap-gains indexing; %GDP, $/household and share-of-tax-cut "
        "columns held back (out of vocab)",
        "2026-08-02",
    )
    db.close()
    return {"scores": n}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
