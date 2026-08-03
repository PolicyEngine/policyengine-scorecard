"""Ingest the Tax Foundation staged claims (2026-08-02 harvest).

Taxes and Growth model output: OBBBA canonical revenue tables (conv + dyn),
provision-level TCJA-permanence XLSX, universal-tariff options, and the
Tariff Tracker (July-2026 vintage). Revenue values staged verbatim in
billions -> normalized ×1e9 here; distribution tables in percent (PERCENT).

Reform worlds: the enacted OBBBA keys to the same statute world as PWBM's
signed-bill scores (obbba_enacted_pl119_21); the House-passed version keys
to JCX-26-25R's world (obbba_house_passed_20250522). Tariff-tracker rows
are one regime world decomposed by conditions["tariff_policy"].
Calendar-vs-fiscal year is UNSTATED on the OBBBA/TCJA revenue tables —
the per-row staged note rides publication["note"]; do not assume FY.
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
)
from .models import ExternalScore, Metric, TimeBasis, UnitConcept

TRUMP_TARIFFS = "trump_tariffs_2025_2026"

# reform_hint -> policy slug (all scored against current law). TF's
# OBBBA pages model the TAX provisions, so they key to the tax-title
# worlds JCT scores (obbba_enacted_title_vii = JCX-35-25's world,
# obbba_house_passed_tax_provisions = JCX-26-25R's world) — not the
# whole-bill worlds PWBM and Budget Lab score.
REFORMS = {
    "One Big Beautiful Bill Act (P.L. 119-21, enacted 2025-07-04)":
        "obbba_enacted_title_vii",
    "One Big Beautiful Bill Act (House-passed version, May 2025)":
        "obbba_house_passed_tax_provisions",
    "TCJA Permanence (making expiring TCJA provisions permanent)":
        "tcja_permanence",
    "Combined TCJA Permanence": "tcja_permanence",
    "TCJA Individual Permanence": "tcja_permanence_individual",
    "TCJA Estate Tax Permanence": "tcja_permanence_estate",
    "TCJA Business Permanence": "tcja_permanence_business",
    "10 percent universal tariff (US baseline, April 2025)":
        "universal_tariff_10pct",
    "15 percent universal tariff (US baseline, April 2025)":
        "universal_tariff_15pct",
    "20 percent universal tariff (US baseline, April 2025)":
        "universal_tariff_20pct",
    "2025-2026 Trump tariffs (All Tariffs)": TRUMP_TARIFFS,
}
# Tariff Tracker rows: one regime world; the component rides
# conditions["tariff_policy"] (staged alongside the hint).
_TRACKER_PREFIX = "2025-2026 Trump tariffs: "

_KNOWN_FIELDS = frozenset(
    {
        "source", "source_model", "proposed_metric", "proposed_unit",
        "value", "value_verbatim", "period", "time_basis", "conditions",
        "reform_hint", "source_column", "publication",
        "calibration_relationship", "value_kind", "status", "note",
    }
)
_KNOWN_CONDITIONS = frozenset(
    {
        "scoring", "tariff_policy", "income_group", "income_measure",
        "window", "retaliation", "provision", "provision_section",
    }
)


def _reform_slug(hint: str) -> str:
    if hint in REFORMS:
        return REFORMS[hint]
    if hint.startswith(_TRACKER_PREFIX):
        return TRUMP_TARIFFS
    raise ValueError(f"tax_foundation: unmapped reform_hint {hint!r}")


def stage_scores() -> list[ExternalScore]:
    scores = []
    for row in load_staged("tax_foundation"):
        require_fields(row, _KNOWN_FIELDS, "tax_foundation")
        staged_conds = row["conditions"]
        unknown = set(staged_conds) - _KNOWN_CONDITIONS
        if unknown:
            raise ValueError(
                f"tax_foundation: unmapped conditions {sorted(unknown)}"
            )
        if row["calibration_relationship"] != "held_out":
            raise ValueError("tax_foundation: unexpected relationship")

        metric_name = row["proposed_metric"]
        unit_name = row["proposed_unit"]
        if metric_name == "revenue_change" and unit_name == "usd_billion":
            metric, unit = Metric.REVENUE_CHANGE, UnitConcept.USD
            value = billions(row["value"])
            value_kind = "usd"
        elif (
            metric_name == "pct_change_after_tax_income"
            and unit_name == "percent"
        ):
            metric = Metric.PCT_CHANGE_AFTER_TAX_INCOME
            unit = UnitConcept.PERCENT
            value = row["value"]
            value_kind = "share"
        else:
            raise ValueError(
                f"tax_foundation: unmapped metric/unit "
                f"{metric_name}/{unit_name}"
            )

        conditions = {"geography": "US"}
        for key in (
            "scoring", "tariff_policy", "income_group", "retaliation",
            "provision", "provision_section",
        ):
            if key in staged_conds:
                conditions[key] = staged_conds[key]
        if "income_measure" in staged_conds:
            conditions["income_axis"] = staged_conds["income_measure"]

        period_start = period_end = None
        if "window" in staged_conds:
            period_start, period_end = parse_window(staged_conds["window"])
            if row["period"] != period_end:
                raise ValueError(
                    f"tax_foundation: window row period {row['period']} != "
                    f"end {period_end}"
                )
            conditions["window_kind"] = "total"

        publication = dict(row["publication"])
        publication["value_verbatim"] = row["value_verbatim"]
        if row.get("note"):
            publication["note"] = row["note"]

        scores.append(
            ExternalScore(
                source="tax_foundation",
                source_model=row["source_model"],
                metric=metric,
                unit_concept=unit,
                period=row["period"],
                time_basis=TimeBasis(row["time_basis"]),
                value=value,
                conditions=conditions,
                reform=policy_ref(_reform_slug(row["reform_hint"])),
                source_column=row["source_column"],
                publication=publication,
                value_kind=value_kind,
                status=row["status"],
                period_start=period_start,
                period_end=period_end,
            )
        )
    # TF publishes some tables twice — rounded on the HTML page, full
    # precision in the companion XLSX (e.g. the House-bill conventional
    # total: -$4,006.5B page vs -4006.51028…B workbook).
    merged = merge_republications(
        scores,
        "tax_foundation",
        precision=_verbatim_decimals,
        tolerance=lambda coarse: (
            (1e9 if coarse.value_kind == "usd" else 1.0)
            * 0.55
            * 10 ** -_verbatim_decimals(coarse)
        ),
    )
    return finish(merged, "tax_foundation")


def _verbatim_decimals(score: ExternalScore) -> int:
    verbatim = str(score.publication["value_verbatim"])
    digits = verbatim.replace("$", "").replace(",", "").lstrip("-")
    return len(digits.split(".")[1]) if "." in digits else 0


def ingest(db_path: Path) -> dict:
    scores = stage_scores()
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.set_lane(
        "tax-foundation-scores",
        "ingested",
        f"{n} claims: OBBBA conv/dyn revenue + provision-level TCJA "
        "permanence + tariff tracker (July-2026 vintage); state/district "
        "Datawrapper CSVs pending follow-up fetch",
        "2026-08-02",
    )
    db.close()
    return {"scores": n}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
