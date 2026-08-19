"""Ingest the UK mode-1 external claims into the scorecard DB (#33).

Inputs are the five UK source adapters' tidy outputs under
data/externals/ (built by PRs #43-#47):

    dwp-takeup.json        -> source "dwp_takeup"
    hbai-poverty.json      -> source "dwp_hbai"
    hmrc-personal-tax.json -> source "uk_hmrc"
    obr-welfare.json       -> source "obr"
    ukmod-stats.json       -> source "ukmod"

This is the UK analogue of the 2026-08-02 harvest adapters, under the
same contract (scorecard_db/README.md): FAIL LOUDLY on any unmapped
metric, unknown variant, or unparseable period; deliberate drops return
a tally, nothing disappears silently; values arrive already in raw
units from the adapters and are never re-derived here.

Deliberate drops (tallied, still present in data/externals for the app):
    - DWP range_low/range_high variants (95% CI bounds; the DB row is the
      central estimate)
    - UKMOD official_as_cited / input_data / hbai variants (score against
      the primary publications — several are sibling lanes — never against
      a transcription)

calibration_relationship is NEVER decided here: every claim routes
through relationships.uk_relationship(), the canonical home, which
raises rather than defaulting on an unassigned (source, metric). In
summary it assigns the whole DWP take-up family consumed_as_target
(pe-uk take-up parameters cite the publication, and entitled-
non-recipient counts and unclaimed amounts are algebraic derivatives of
a consumed rate — "nor anything derived from such"), OBR outturn-year
spending consumed_as_target, and HBAI poverty permanently held out by
the 2026-08-02 doctrine. Where the per-parameter audit of pe-uk's
provenance is still owed, the conservative direction is taken:
consumed, not held_out — mislabelling a tautology as a validation win
is the failure the doctrine exists to prevent.

HMRC ready-reckoner rows are REFORM claims, not levels: each carries a
policy_ref reform whose policy slug is derived from the verbatim change
description (also kept as conditions["option"]) — the campaign's
hmrc_reckoner_t2 family attaches against these once its descriptors are
re-emitted with the change label (they currently under-specify: two
personal-allowance rows share identical descriptor conditions).

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_uk_externals data/scorecard.db
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .db import ScorecardDB
from .harvest import REPO, finish, require_fields
from .relationships import uk_relationship
from .models import (
    BASELINE,
    ExternalScore,
    Metric,
    ReformRef,
    TimeBasis,
    UnitConcept,
)

EXTERNALS = REPO / "data" / "externals"


def _fy(label: str) -> tuple[int, str]:
    """UK financial-year label -> (end-year int, canonical fy string).

    'FYE 2024' -> (2024, '2023-24'); '2023-24' -> (2024, '2023-24');
    '2024/25' -> (2025, '2024-25').
    """
    m = re.match(r"^FYE (\d{4})$", label)
    if m:
        end = int(m.group(1))
        return end, f"{end - 1}-{str(end)[2:]}"
    m = re.match(r"^(\d{4})-(\d{2})$", label)
    if m:
        return int(m.group(1)) + 1, label
    m = re.match(r"^(\d{4})/(\d{2})$", label)
    if m:
        start = int(m.group(1))
        return start + 1, f"{start}-{m.group(2)}"
    raise ValueError(f"unparseable UK financial-year label: {label!r}")


# Every top-level field each adapter emits, per file. _load() fails loud
# on anything outside its set (the harvest.py require_fields contract) —
# a new adapter column must be handled or added here DELIBERATELY, never
# silently dropped (the OBR aggregate_level/parent columns slipped
# through exactly this way before the gate existed).
_COMMON_FIELDS = {
    "country",
    "geography",
    "metric",
    "period",
    "program",
    "source",
    "source_column",
    "status",
    "subgroup",
    "unit_concept",
    "value",
    "variant",
}
_KNOWN_FIELDS = {
    "dwp-takeup": frozenset(_COMMON_FIELDS),
    "hbai-poverty": frozenset(_COMMON_FIELDS),
    "hmrc-personal-tax": frozenset(
        _COMMON_FIELDS | {"change_direction", "direction", "sign_convention"}
    ),
    "obr-welfare": frozenset(_COMMON_FIELDS | {"aggregate_level", "parent"}),
    "ukmod-stats": frozenset(_COMMON_FIELDS),
}


def _load(name: str) -> list[dict]:
    path = EXTERNALS / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run the {name} adapter (sources/{name}/) first"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS[name], name)
    return rows


def _base_conditions(row: dict) -> dict:
    cond: dict = {"country": "UK", "geography": row["geography"]}
    if row["subgroup"] != "total":
        cond["subgroup"] = row["subgroup"]
    if row["program"] not in (None, "total"):
        cond["program"] = row["program"]
    return cond


def _score(
    row,
    source,
    metric,
    unit,
    conditions,
    period,
    time_basis,
    value_kind,
    publication,
    reform=BASELINE,
    source_model=None,
    period_start=None,
    period_end=None,
    obr_basis=None,
):
    return ExternalScore(
        source=source,
        metric=metric,
        unit_concept=unit,
        period=period,
        time_basis=time_basis,
        value=row["value"],
        conditions=conditions,
        reform=reform,
        calibration_relationship=uk_relationship(source, metric, obr_basis)[0],
        source_model=source_model,
        source_column=row.get("source_column"),
        publication=publication,
        value_kind=value_kind,
        status=row["status"],
        period_start=period_start,
        period_end=period_end,
    )


# --- DWP income-related benefits take-up ---------------------------------

_DWP_PUB = {
    "title": "Income-related benefits: estimates of take-up, FYE 2024",
    "url": "https://www.gov.uk/government/statistics/income-related-benefits-estimates-of-take-up-financial-year-ending-2024",
    "date": "2025-10-30",
}

_DWP_METRICS = {
    # metric -> (Metric, UnitConcept, value_kind, extra conditions).
    # calibration_relationship is NOT here: it comes from
    # relationships.uk_relationship(), the canonical home.
    "recipients_count": (
        Metric.PARTICIPANT_COUNT,
        UnitConcept.BENEFIT_UNITS,
        "count",
        {},
    ),
    "entitled_nonrecipients_count": (
        Metric.PARTICIPATION_GAP_COUNT,
        UnitConcept.BENEFIT_UNITS,
        "count",
        {},
    ),
    "caseload_takeup_rate": (
        Metric.PARTICIPATION_RATE,
        UnitConcept.SHARE,
        "share",
        {"basis": "caseload"},
    ),
    "expenditure_takeup_rate": (
        Metric.PARTICIPATION_RATE,
        UnitConcept.SHARE,
        "share",
        {"basis": "expenditure"},
    ),
    "mean_weekly_amount_claimed": (
        Metric.AVERAGE_WEEKLY_BENEFIT,
        UnitConcept.GBP,
        "usd",
        {},
    ),
    "mean_weekly_amount_unclaimed": (
        Metric.AVERAGE_WEEKLY_BENEFIT,
        UnitConcept.GBP,
        "usd",
        {"component": "unclaimed"},
    ),
    "median_weekly_amount_unclaimed": (
        Metric.AVERAGE_WEEKLY_BENEFIT,
        UnitConcept.GBP,
        "usd",
        {"component": "unclaimed", "statistic": "median"},
    ),
    "total_amount_claimed": (Metric.BENEFIT_COST, UnitConcept.GBP, "usd", {}),
    "amount_unclaimed": (Metric.UNCLAIMED_BENEFIT_AMOUNT, UnitConcept.GBP, "usd", {}),
}


def stage_dwp_takeup() -> tuple[list[ExternalScore], dict]:
    scores, drops = [], {"range_variants": 0}
    for row in _load("dwp-takeup"):
        if row["variant"] in ("range_low", "range_high"):
            drops["range_variants"] += 1
            continue
        if row["variant"] is not None:
            raise ValueError(f"dwp_takeup: unknown variant {row['variant']!r}")
        metric, unit, value_kind, extra = _DWP_METRICS[row["metric"]]
        period, fy = _fy(row["period"])
        cond = _base_conditions(row) | extra | {"fy": fy}
        scores.append(
            _score(
                row,
                "dwp_takeup",
                metric,
                unit,
                cond,
                period,
                TimeBasis.FISCAL_YEAR,
                value_kind,
                _DWP_PUB,
                source_model="dwp_psm",
            )
        )
    return finish(scores, "dwp_takeup"), drops


# --- DWP HBAI ------------------------------------------------------------

_HBAI_PUB = {
    "title": "Households below average income, FYE 1995 to FYE 2025",
    "url": "https://www.gov.uk/government/statistics/households-below-average-income-for-financial-years-ending-1995-to-2025",
    "date": "2026-03-26",
}

_HBAI_METRICS = {
    "relative_low_income_rate": (
        Metric.POVERTY_RATE,
        UnitConcept.SHARE,
        "share",
        "relative",
    ),
    "absolute_low_income_rate": (
        Metric.POVERTY_RATE,
        UnitConcept.SHARE,
        "share",
        "absolute",
    ),
    "relative_low_income_count": (
        Metric.POVERTY_COUNT,
        UnitConcept.PERSONS,
        "count",
        "relative",
    ),
    "absolute_low_income_count": (
        Metric.POVERTY_COUNT,
        UnitConcept.PERSONS,
        "count",
        "absolute",
    ),
}

_SPAN = re.compile(r"^(\d{4})/(\d{2})-(\d{4})/(\d{2})$")


def stage_hbai() -> tuple[list[ExternalScore], dict]:
    scores = []
    for row in _load("hbai-poverty"):
        metric, unit, value_kind, line = _HBAI_METRICS[row["metric"]]
        if row["variant"] not in ("bhc", "ahc"):
            raise ValueError(f"dwp_hbai: unknown variant {row['variant']!r}")
        cond = _base_conditions(row)
        cond.pop("program", None)  # hbai_low_income is the source, not a program
        cond |= {"poverty_line": line, "housing_costs": row["variant"]}
        span = _SPAN.match(row["period"])
        if span:
            start, end = int(span.group(1)) + 1, int(span.group(3)) + 1
            cond["window_kind"] = "annual_average"
            scores.append(
                _score(
                    row,
                    "dwp_hbai",
                    metric,
                    unit,
                    cond,
                    end,
                    TimeBasis.FISCAL_YEAR,
                    value_kind,
                    _HBAI_PUB,
                    period_start=start,
                    period_end=end,
                )
            )
        else:
            period, fy = _fy(row["period"])
            cond["fy"] = fy
            scores.append(
                _score(
                    row,
                    "dwp_hbai",
                    metric,
                    unit,
                    cond,
                    period,
                    TimeBasis.FISCAL_YEAR,
                    value_kind,
                    _HBAI_PUB,
                )
            )
    return finish(scores, "dwp_hbai"), {}


# --- HMRC liabilities tables + ready reckoner ----------------------------

_HMRC_PUB = {
    "title": "Income Tax liabilities statistics 2023-24 to 2026-27 + June 2025 tax ready reckoner",
    "url": "https://www.gov.uk/government/statistics/income-tax-liabilities-statistics-tax-year-2023-to-2024-to-tax-year-2026-to-2027",
    "date": "2026-07-15",
}

_HMRC_LEVELS = {
    "taxpayer_count": (Metric.TAXPAYER_COUNT, UnitConcept.PERSONS, "count"),
    "tax_liability": (Metric.TAX_LIABILITY, UnitConcept.GBP, "usd"),
    "total_income": (Metric.INCOME_AGGREGATE, UnitConcept.GBP, "usd"),
    "average_tax_rate": (Metric.AVERAGE_TAX_RATE, UnitConcept.SHARE, "share"),
    "average_tax_amount": (Metric.AVERAGE_TAX_AMOUNT, UnitConcept.GBP, "usd"),
}

_RECKONER_BASELINE = "hmrc_indexed_baseline_spring_2025"


def _reckoner_policy(program: str, description: str) -> str:
    """Distinct reform world per (tax head, change).

    HMRC prints "Change standard rate by 1 percentage point" under BOTH
    the VAT and the Insurance Premium Tax sections; on the description
    alone the two collapse into one reform key, and a single PE compute of
    a VAT change would be joined as the counterpart to the IPT claim
    (the two differ 14x in magnitude). The tax head is part of the world.
    """
    slug = re.sub(r"[^a-z0-9]+", "_", description.lower()).strip("_")
    return f"trr_{program}_{slug}"


def stage_hmrc() -> tuple[list[ExternalScore], dict]:
    scores = []
    for row in _load("hmrc-personal-tax"):
        period, fy = _fy(row["period"])
        if row["metric"] == "revenue_effect":
            # Reform deltas against HMRC's indexed baseline; the verbatim
            # change description is the policy world.
            cond = {
                "country": "UK",
                "geography": row["geography"],
                "program": row["program"],
                "fy": fy,
                "option": row["subgroup"],
                "baseline_policy": _RECKONER_BASELINE,
            }
            reform = ReformRef(
                framework="policy_ref",
                reform={"policy": _reckoner_policy(row["program"], row["subgroup"])},
                baseline={"policy": _RECKONER_BASELINE},
            )
            scores.append(
                _score(
                    row,
                    "uk_hmrc",
                    Metric.REVENUE_CHANGE,
                    UnitConcept.GBP,
                    cond,
                    period,
                    TimeBasis.FISCAL_YEAR,
                    "usd",
                    _HMRC_PUB,
                    reform=reform,
                    source_model="hmrc_personal_tax_model",
                )
            )
            continue
        metric, unit, value_kind = _HMRC_LEVELS[row["metric"]]
        cond = _base_conditions(row) | {"fy": fy}
        if row["variant"] is not None:  # table 2.5 income-range rows
            cond["income_group"] = row["variant"]
        scores.append(
            _score(
                row,
                "uk_hmrc",
                metric,
                unit,
                cond,
                period,
                TimeBasis.FISCAL_YEAR,
                value_kind,
                _HMRC_PUB,
                source_model="hmrc_spi",
            )
        )
    return finish(scores, "uk_hmrc"), {}


# --- OBR EFO welfare baseline --------------------------------------------

_OBR_PUB = {
    "title": "Economic and fiscal outlook March 2026, detailed expenditure Table 4.9",
    "url": "https://obr.uk/efo/economic-and-fiscal-outlook-march-2026/",
    "date": "2026-03-03",
}

_OBR_OUTTURN_FY = "2024-25"


def stage_obr() -> tuple[list[ExternalScore], dict]:
    scores = []
    for row in _load("obr-welfare"):
        if row["metric"] != "welfare_spending":
            raise ValueError(f"obr: unknown metric {row['metric']!r}")
        period, fy = _fy(row["period"])
        basis = "outturn" if fy == _OBR_OUTTURN_FY else "forecast"
        # aggregate_level (component/subtotal/total) + parent make the
        # roll-up hierarchy explicit on every row: without them all 259
        # rows read as sibling benefit_cost claims and any consumer
        # summing OBR benefit_cost by FY double-counts (total_welfare +
        # dwp_social_security + their components).
        cond = _base_conditions(row) | {
            "fy": fy,
            "basis": basis,
            "aggregate_level": row["aggregate_level"],
        }
        if row["parent"] is not None:
            cond["parent"] = row["parent"]
        if row["variant"] is not None:
            cond["welfare_cap"] = row["variant"]
        scores.append(
            _score(
                row,
                "obr",
                Metric.BENEFIT_COST,
                UnitConcept.GBP,
                cond,
                period,
                TimeBasis.FISCAL_YEAR,
                "usd",
                _OBR_PUB,
                source_model="obr_efo",
                obr_basis=basis,
            )
        )
    return finish(scores, "obr"), {}


# --- UKMOD country report ------------------------------------------------

_UKMOD_PUB = {
    "title": "UKMOD Country Report 2023-2030 (CeMPA WP 8/26, B2026.01)",
    "url": "https://www.iser.essex.ac.uk/research/publications/publication-589013",
    "date": "2026-04-15",
}

_UKMOD_TAX_PROGRAMS = re.compile(r"^(income_tax|nic_)")

_UKMOD_UNITS = {
    "families": UnitConcept.FAMILIES,
    "households": UnitConcept.HOUSEHOLDS,
    "individuals": UnitConcept.PERSONS,
    "children": UnitConcept.CHILDREN,
}

_UKMOD_POVERTY = re.compile(r"^poverty_rate_below_(\d{2})pct_median$")


def stage_ukmod() -> tuple[list[ExternalScore], dict]:
    scores, drops = [], {"non_primary_variants": 0}
    for row in _load("ukmod-stats"):
        if row["variant"] != "ukmod":
            drops["non_primary_variants"] += 1
            continue
        period = int(row["period"])
        program = row["program"]
        cond = _base_conditions(row)
        if row["metric"] == "caseload":
            metric = (
                Metric.TAXPAYER_COUNT
                if _UKMOD_TAX_PROGRAMS.match(program)
                else Metric.CASELOAD
            )
            unit, value_kind = _UKMOD_UNITS[row["unit_concept"]], "count"
        elif row["metric"] == "expenditure":
            metric = (
                Metric.TAX_LIABILITY
                if _UKMOD_TAX_PROGRAMS.match(program)
                else Metric.BENEFIT_COST
            )
            unit, value_kind = UnitConcept.GBP, "usd"
        elif row["metric"] == "gini":
            metric, unit, value_kind = Metric.GINI, UnitConcept.SHARE, "share"
            cond.pop("program", None)
        elif row["metric"] in (
            "mean_income",
            "median_income",
            "quintile_median_income",
        ):
            metric, unit, value_kind = Metric.INCOME_STATISTIC, UnitConcept.GBP, "usd"
            cond.pop("program", None)
            cond["per"] = "month"
            if row["metric"] == "mean_income":
                pass  # mean is the default statistic
            else:
                cond["statistic"] = "median"
            if row["metric"] == "quintile_median_income":
                cond["quantile"] = cond.pop("subgroup")
        elif row["metric"] == "quintile_income_share":
            metric, unit, value_kind = Metric.INCOME_SHARE, UnitConcept.SHARE, "share"
            cond.pop("program", None)
            cond["quantile"] = cond.pop("subgroup")
        elif _UKMOD_POVERTY.match(row["metric"]):
            metric, unit, value_kind = Metric.POVERTY_RATE, UnitConcept.SHARE, "share"
            cond.pop("program", None)
            cond["poverty_line"] = _UKMOD_POVERTY.match(row["metric"]).group(1)
            cond["housing_costs"] = "bhc"
        else:
            raise ValueError(f"ukmod: unknown metric {row['metric']!r}")
        scores.append(
            _score(
                row,
                "ukmod",
                metric,
                unit,
                cond,
                period,
                TimeBasis.ANNUAL,
                value_kind,
                _UKMOD_PUB,
                source_model="ukmod_b2026.01",
            )
        )
    return finish(scores, "ukmod"), drops


STAGERS = {
    "dwp_takeup": stage_dwp_takeup,
    "dwp_hbai": stage_hbai,
    "uk_hmrc": stage_hmrc,
    "obr": stage_obr,
    "ukmod": stage_ukmod,
}


def ingest(db_path: Path) -> dict:
    db = ScorecardDB(db_path)
    summary: dict = {"claims": {}, "drops": {}}
    for name, stager in STAGERS.items():
        scores, drops = stager()
        n = db.upsert_scores(scores)
        summary["claims"][name] = n
        if drops:
            summary["drops"][name] = drops
    db.close()
    return summary


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
