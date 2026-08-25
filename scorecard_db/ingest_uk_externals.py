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
through relationships.uk_relationship(), the canonical home, rebuilt
2026-08-19 from the LITERAL consumption surfaces read at the certified
pins (pe-uk-data@dd68c73 targets/sources/{obr,dwp,hmrc_spi}.py;
policyengine-uk takeup.yaml parameters). Administrative OUTTURN cells —
OBR's FY2024-25 column, HMRC's 2023-24 SPI-outturn liabilities, DWP's
recipient counts and amounts claimed — route to
data/ledger/uk_admin_outturns.jsonl (the 2026-08-02 boundary rule:
outturns are Chronicle material for Microcosm calibration, never
scorecard claims),
each with a deterministic fact id and, where pe-uk-data literally
consumes the cell, the consuming pin named. Condition identities route
through scorecard_db/uk_aliases.py, the closed (source, axis, value)
registry: unknown values raise; cross-source aliases and
distinct-do-not-alias pairs are explicit.

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

import hashlib

from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, require_fields
from .uk_aliases import canon
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
LEDGER_PATH = REPO / "data" / "ledger" / "uk_admin_outturns.jsonl"
UK_SOURCES = ("dwp_takeup", "dwp_hbai", "uk_hmrc", "obr", "ukmod")


def _ledger_row(source, row, fy, metric, unit, publication, consumed_by=None):
    """An admin-outturn fact routed to Chronicle staging (never a claim).

    fact_id is deterministic over the cell's identity so re-ingest
    rewrites the same facts and downstream Chronicle consumers can key on
    it."""
    unit = canon(source, "unit", unit)
    program = (
        canon(source, "program", row["program"])
        if row.get("program") not in (None, "total")
        else row.get("program")
    )
    subgroup = (
        canon(source, "subgroup", row["subgroup"])
        if row.get("subgroup") is not None
        else None
    )
    geography = canon(source, "geography", row["geography"])
    identity = "|".join(
        str(x)
        for x in (
            source,
            metric,
            program,
            subgroup,
            geography,
            fy,
            row.get("variant"),
        )
    )
    return {
        "fact_id": "uk-admin-" + hashlib.sha256(identity.encode()).hexdigest()[:16],
        "source": source,
        "publication": publication,
        "metric": metric,
        "program": program,
        "subgroup": subgroup,
        "geography": geography,
        "fy": fy,
        "variant": row.get("variant"),
        "unit": unit,
        "value": row["value"],
        "status": row["status"],
        "source_column": row.get("source_column"),
        "aggregate_level": row.get("aggregate_level"),
        "parent": row.get("parent"),
        "consumed_by": consumed_by,
        "routing": "chronicle: admin outturn (boundary rule 2026-08-02)",
    }


def _fy(label: str) -> tuple[int, str]:
    """UK financial-year label -> (end-year int, canonical fy string).

    'FYE 2024' -> (2024, '2023-24'); '2023-24' -> (2024, '2023-24');
    '2024/25' -> (2025, '2024-25').
    """
    # fullmatch, not match-with-$: Python's $ also matches before a
    # trailing newline, so "2029-30\n" would parse (round-2 gate).
    m = re.fullmatch(r"FYE (\d{4})", label)
    if m:
        end = int(m.group(1))
        return end, f"{end - 1}-{str(end)[2:]}"
    m = re.fullmatch(r"(\d{4})[-/](\d{2})", label)
    if m:
        start = int(m.group(1))
        # the suffix must be the start year + 1 — '2029-99' is malformed,
        # never year 2030 (round-1 gate on the deductions family)
        if (start + 1) % 100 != int(m.group(2)):
            raise ValueError(
                f"UK financial-year label {label!r}: suffix is not start year + 1"
            )
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


def _base_conditions(source: str, row: dict) -> dict:
    """Alias-validated base conditions: every identity value must be in
    the closed registry (uk_aliases) — unknowns raise there."""
    cond: dict = {
        "country": "UK",
        "geography": canon(source, "geography", row["geography"]),
    }
    if row["subgroup"] != "total":
        cond["subgroup"] = canon(source, "subgroup", row["subgroup"])
    if row["program"] not in (None, "total"):
        cond["program"] = canon(source, "program", row["program"])
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
    program=None,
    kind=None,
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
        calibration_relationship=uk_relationship(
            source, metric, program=program, kind=kind
        )[0],
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

# Administrative cells (the recipient numerator and claimed amounts are
# published admin statistics, not model output) route to CHRONICLE, never
# to claims — the 2026-08-02 boundary rule.
_DWP_ADMIN_METRICS = frozenset(
    {
        "recipients_count",
        "total_amount_claimed",
        "mean_weekly_amount_claimed",
    }
)

_DWP_METRICS = {
    # metric -> (Metric, UnitConcept, value_kind, kind, extra conditions).
    # `kind` keys relationships.uk_relationship's exact assignment.
    "entitled_nonrecipients_count": (
        Metric.PARTICIPATION_GAP_COUNT,
        UnitConcept.BENEFIT_UNITS,
        "count",
        "modeled_estimate",
        {},
    ),
    "caseload_takeup_rate": (
        Metric.PARTICIPATION_RATE,
        UnitConcept.SHARE,
        "share",
        "takeup_rate",
        {"basis": "caseload"},
    ),
    "expenditure_takeup_rate": (
        Metric.PARTICIPATION_RATE,
        UnitConcept.SHARE,
        "share",
        "takeup_rate",
        {"basis": "expenditure"},
    ),
    "mean_weekly_amount_unclaimed": (
        Metric.AVERAGE_WEEKLY_BENEFIT,
        UnitConcept.GBP_PER_WEEK,
        "gbp_per_week",
        "modeled_estimate",
        {"component": "unclaimed"},
    ),
    "median_weekly_amount_unclaimed": (
        Metric.AVERAGE_WEEKLY_BENEFIT,
        UnitConcept.GBP_PER_WEEK,
        "gbp_per_week",
        "modeled_estimate",
        {"component": "unclaimed", "statistic": "median"},
    ),
    "amount_unclaimed": (
        Metric.UNCLAIMED_BENEFIT_AMOUNT,
        UnitConcept.GBP,
        "gbp",
        "modeled_estimate",
        {},
    ),
}


def stage_dwp_takeup() -> tuple[list[ExternalScore], list[dict], dict]:
    scores, ledger, drops = [], [], {"range_variants": 0}
    for row in _load("dwp-takeup"):
        if row["variant"] in ("range_low", "range_high"):
            drops["range_variants"] += 1
            continue
        if row["variant"] is not None:
            raise ValueError(f"dwp_takeup: unknown variant {row['variant']!r}")
        period, fy = _fy(row["period"])
        if row["metric"] in _DWP_ADMIN_METRICS:
            # pe-uk-data@dd68c73 consumes DWP benefit STATISTICS caseloads
            # (targets/sources/dwp.py), a different publication — these
            # take-up-release admin cells are Chronicle material with no
            # consuming pin.
            ledger.append(
                _ledger_row(
                    "dwp_takeup",
                    row,
                    fy,
                    row["metric"],
                    row["unit_concept"],
                    _DWP_PUB,
                )
            )
            continue
        canon("dwp_takeup", "unit", row["unit_concept"])
        metric, unit, value_kind, kind, extra = _DWP_METRICS[row["metric"]]
        cond = _base_conditions("dwp_takeup", row) | extra | {"fy": fy}
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
                program=cond.get("program"),
                kind=kind,
            )
        )
    return finish(scores, "dwp_takeup"), ledger, drops


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


def stage_hbai() -> tuple[list[ExternalScore], list[dict], dict]:
    scores = []
    for row in _load("hbai-poverty"):
        canon("dwp_hbai", "unit", row["unit_concept"])
        metric, unit, value_kind, line = _HBAI_METRICS[row["metric"]]
        cond = _base_conditions("dwp_hbai", row)
        cond.pop("program", None)  # hbai_low_income is the source, not a program
        housing = canon("dwp_hbai", "housing_costs", row["variant"])

        def _absolute_anchor(start_year: int, end_year: int) -> str:
            """Notes sheet Note 3 (vendored): the absolute fixed reference
            year is FYE 2025 for 2021/22-2024/25; years before 2021/22
            remain anchored at FYE 2011. A window straddling the break is
            an explicit mixed construction, never averaged away."""
            starts = range(start_year, end_year)
            anchors = {"fye_2025" if s >= 2021 else "fye_2011" for s in starts}
            return anchors.pop() if len(anchors) == 1 else ("mixed_fye2011_fye2025")

        cond |= {
            "poverty_line": canon("dwp_hbai", "poverty_line", line),
            "housing_costs": housing,
            # FYE-2025 methodology report: "The main equivalence scales now
            # used in HBAI are the modified OECD scales"; AHC uses the
            # companion scale.
            "equivalisation": (
                "modified_oecd_companion_ahc" if housing == "ahc" else "modified_oecd"
            ),
        }
        span = _SPAN.fullmatch(row["period"])
        if span:
            start, end = int(span.group(1)) + 1, int(span.group(3)) + 1
            cond["window_kind"] = "annual_average"
            if line == "absolute":
                cond["poverty_line_anchor"] = _absolute_anchor(start - 1, end)
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
            if line == "absolute":
                cond["poverty_line_anchor"] = _absolute_anchor(period - 1, period)
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
    return finish(scores, "dwp_hbai"), [], {}


# --- HMRC liabilities tables + ready reckoner ----------------------------

_HMRC_PUB = {
    "title": "Income Tax liabilities statistics 2023-24 to 2026-27 + June 2025 tax ready reckoner",
    "url": "https://www.gov.uk/government/statistics/income-tax-liabilities-statistics-tax-year-2023-to-2024-to-tax-year-2026-to-2027",
    "date": "2026-07-15",
}

_HMRC_LEVELS = {
    "taxpayer_count": (Metric.TAXPAYER_COUNT, UnitConcept.PERSONS, "count"),
    "tax_liability": (Metric.TAX_LIABILITY, UnitConcept.GBP, "gbp"),
    "total_income": (Metric.INCOME_AGGREGATE, UnitConcept.GBP, "gbp"),
    "average_tax_rate": (Metric.AVERAGE_TAX_RATE, UnitConcept.SHARE, "share"),
    "average_tax_amount": (
        Metric.AVERAGE_TAX_AMOUNT,
        UnitConcept.GBP,
        "gbp",
    ),
}

# The liabilities publication's own description sheet (vendored
# workbook, 2_1_Description!A5): every year through 2023-24 is OUTTURN;
# 2024-25 onward are projections. All outturn years -> Chronicle.
_HMRC_LAST_OUTTURN_END = 2024  # FY 2023-24

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


def stage_hmrc() -> tuple[list[ExternalScore], list[dict], dict]:
    scores, ledger = [], []
    for row in _load("hmrc-personal-tax"):
        # Unit validation before ANY branch: the reckoner branch below
        # returns early and previously bypassed the closed registry
        # (round-2 gate probe — an unknown unit sailed through as GBP).
        canon("uk_hmrc", "unit", row["unit_concept"])
        period, fy = _fy(row["period"])
        if row["metric"] == "revenue_effect":
            # Reform deltas against HMRC's indexed baseline; the verbatim
            # change description is the policy world.
            cond = {
                "country": "UK",
                "geography": canon("uk_hmrc", "geography", row["geography"]),
                "program": canon("uk_hmrc", "program", row["program"]),
                "fy": fy,
                "option": row["subgroup"],
                "baseline_policy": _RECKONER_BASELINE,
            }
            # machine-readable comparison orientation (the source's own
            # requirement: asymmetric (cost)/(yield) pairs are distinct)
            for key in ("sign_convention", "direction", "change_direction"):
                if row.get(key) is not None:
                    cond[key] = row[key]
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
                    "gbp",
                    _HMRC_PUB,
                    reform=reform,
                    source_model="hmrc_personal_tax_model",
                    program=row["program"],
                    kind="reckoner",
                )
            )
            continue
        if period <= _HMRC_LAST_OUTTURN_END:
            ledger.append(
                _ledger_row(
                    "uk_hmrc",
                    row,
                    fy,
                    row["metric"],
                    row["unit_concept"],
                    _HMRC_PUB,
                    consumed_by=(
                        "shared SPI base: pe-uk-data@dd68c73 consumes SPI "
                        "Tables 3.6/3.7 (targets/sources/hmrc_spi.py); this "
                        "outturn cell is the same SPI year's liability "
                        "projection surface"
                    ),
                )
            )
            continue
        metric, unit, value_kind = _HMRC_LEVELS[row["metric"]]
        cond = _base_conditions("uk_hmrc", row) | {"fy": fy}
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
                program=row["program"],
                kind="liabilities",
            )
        )
    return finish(scores, "uk_hmrc"), ledger, {}


# --- OBR EFO welfare baseline --------------------------------------------

_OBR_PUB = {
    "title": "Economic and fiscal outlook March 2026, detailed expenditure Table 4.9",
    "url": "https://obr.uk/efo/economic-and-fiscal-outlook-march-2026/",
    "date": "2026-03-03",
}

_OBR_OUTTURN_FY = "2024-25"


def stage_obr() -> tuple[list[ExternalScore], list[dict], dict]:
    scores, ledger = [], []
    for row in _load("obr-welfare"):
        if row["metric"] != "welfare_spending":
            raise ValueError(f"obr: unknown metric {row['metric']!r}")
        canon("obr", "unit", row["unit_concept"])
        period, fy = _fy(row["period"])
        if fy == _OBR_OUTTURN_FY:
            from .relationships import OBR_CONSUMED_WELFARE_PROGRAMS

            consumed = (
                "pe-uk-data@dd68c73 targets/sources/obr.py reads this "
                "line's FY2024-25 column as a calibration target value"
                if row["program"] in OBR_CONSUMED_WELFARE_PROGRAMS
                else None
            )
            ledger.append(
                _ledger_row(
                    "obr",
                    row,
                    fy,
                    row["metric"],
                    row["unit_concept"],
                    _OBR_PUB,
                    consumed_by=consumed,
                )
            )
            continue
        basis = "forecast"
        # aggregate_level (component/subtotal/total) + parent make the
        # roll-up hierarchy explicit on every row: without them all 259
        # rows read as sibling benefit_cost claims and any consumer
        # summing OBR benefit_cost by FY double-counts (total_welfare +
        # dwp_social_security + their components).
        cond = _base_conditions("obr", row) | {
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
                "gbp",
                _OBR_PUB,
                source_model="obr_efo",
                program=cond.get("program"),
                kind=basis,
            )
        )
    return finish(scores, "obr"), ledger, {}


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


def stage_ukmod() -> tuple[list[ExternalScore], list[dict], dict]:
    scores, drops = [], {"non_primary_variants": 0}
    for row in _load("ukmod-stats"):
        if row["variant"] != "ukmod":
            drops["non_primary_variants"] += 1
            continue
        canon("ukmod", "unit", row["unit_concept"])
        period = int(row["period"])
        program = canon("ukmod", "program", row["program"])
        cond = _base_conditions("ukmod", row)
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
            unit, value_kind = UnitConcept.GBP, "gbp"
        elif row["metric"] == "gini":
            metric, unit, value_kind = (
                Metric.GINI,
                UnitConcept.INDEX_0_1,
                "index",
            )
            cond.pop("program", None)
            cond["housing_costs"] = canon("ukmod", "housing_costs", "bhc")
            cond["equivalisation"] = "modified_oecd"
        elif row["metric"] in (
            "mean_income",
            "median_income",
            "quintile_median_income",
        ):
            metric, unit, value_kind = (
                Metric.INCOME_STATISTIC,
                UnitConcept.GBP_PER_MONTH,
                "gbp_per_month",
            )
            cond.pop("program", None)
            cond["housing_costs"] = canon("ukmod", "housing_costs", "bhc")
            cond["equivalisation"] = "modified_oecd"
            if row["metric"] == "mean_income":
                pass  # mean is the default statistic
            else:
                cond["statistic"] = "median"
            if row["metric"] == "quintile_median_income":
                cond["quantile"] = cond.pop("subgroup")
        elif row["metric"] == "quintile_income_share":
            metric, unit, value_kind = Metric.INCOME_SHARE, UnitConcept.SHARE, "share"
            cond["housing_costs"] = canon("ukmod", "housing_costs", "bhc")
            cond["equivalisation"] = "modified_oecd"
            cond.pop("program", None)
            cond["quantile"] = cond.pop("subgroup")
        elif _UKMOD_POVERTY.fullmatch(row["metric"]):
            metric, unit, value_kind = (
                Metric.POVERTY_RATE,
                UnitConcept.SHARE,
                "share",
            )
            cond.pop("program", None)
            cond["poverty_line"] = canon(
                "ukmod",
                "poverty_line",
                _UKMOD_POVERTY.fullmatch(row["metric"]).group(1),
            )
            cond["housing_costs"] = canon("ukmod", "housing_costs", "bhc")
            cond["equivalisation"] = "modified_oecd"
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
                program=cond.get("program"),
            )
        )
    return finish(scores, "ukmod"), [], drops


STAGERS = {
    "dwp_takeup": stage_dwp_takeup,
    "dwp_hbai": stage_hbai,
    "uk_hmrc": stage_hmrc,
    "obr": stage_obr,
    "ukmod": stage_ukmod,
}


# Exact accounting for the current committed adapter outputs. A drifted
# adapter regeneration must fail HERE, never shrink or grow the catalog
# silently (adjudication blocker 7: the earlier >0 assertions let a
# +168-claim drift pass unseen).
# 15,851 claims + 1,073 Chronicle facts + 1,829 deliberate drops account
# for every adapter row (16,924 pre-routing; the admin outturns — DWP
# recipient/claimed cells, HMRC's full 1990-91..2023-24 outturn span,
# OBR's FY2024-25 column — route to Chronicle per the boundary rule).
_EXPECTED = {
    "claims": {
        "dwp_takeup": 1092,
        "dwp_hbai": 13056,
        "uk_hmrc": 723,
        "obr": 222,
        "ukmod": 758,
    },
    "ledger": {"dwp_takeup": 546, "uk_hmrc": 490, "obr": 37},
    "drops": {
        "dwp_takeup": {"range_variants": 1456},
        "ukmod": {"non_primary_variants": 373},
    },
}


def stage_all() -> tuple[list[ExternalScore], list[dict], dict]:
    """Stage every source; nothing touches the DB here."""
    all_scores: list[ExternalScore] = []
    all_ledger: list[dict] = []
    summary: dict = {"claims": {}, "ledger": {}, "drops": {}}
    for name, stager in STAGERS.items():
        scores, ledger, drops = stager()
        summary["claims"][name] = len(scores)
        if ledger:
            summary["ledger"][name] = len(ledger)
        if drops:
            summary["drops"][name] = drops
        all_scores.extend(scores)
        all_ledger.extend(ledger)
    if _EXPECTED["claims"] and summary["claims"] != _EXPECTED["claims"]:
        raise ValueError(
            f"claim accounting drifted: {summary['claims']} != {_EXPECTED['claims']}"
        )
    if _EXPECTED["ledger"] and summary["ledger"] != _EXPECTED["ledger"]:
        raise ValueError(
            f"ledger accounting drifted: {summary['ledger']} != {_EXPECTED['ledger']}"
        )
    if _EXPECTED["drops"] and summary["drops"] != _EXPECTED["drops"]:
        raise ValueError(
            f"drop accounting drifted: {summary['drops']} != {_EXPECTED['drops']}"
        )
    return all_scores, all_ledger, summary


def ingest(db_path: Path) -> dict:
    """All staging and validation first; then ONE transaction replaces
    this module's five sources wholesale AND runs every persistence
    gate inside it — delete, insert, the deliberate-registration gate
    (#13), lane rows: commit or nothing. A claim referencing an
    unregistered baseline world therefore never persists past its own
    gate (round-2 fix: registration used to run post-commit, which
    validated the state but did not guard it). The Chronicle staging file
    and the lane-feed mirror are rewritten only after the commit; both
    regenerations are idempotent (deterministic fact ids, sorted; feed
    merge keyed by lane id)."""
    all_scores, all_ledger, summary = stage_all()
    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(s) for s in all_scores]
    placeholders = ",".join("?" * len(UK_SOURCES))
    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    # One lane id per source, matching the adapter-created feed entries
    # (data/lanes.json) so DB and feed never disagree about stage.
    lane_meta = {
        "dwp-takeup": ("dwp_takeup", "DWP", "income-related benefits take-up"),
        "hbai-poverty": ("dwp_hbai", "DWP", "HBAI low income"),
        "hmrc-personal-tax": ("uk_hmrc", "HMRC", "personal tax liabilities + reckoner"),
        "obr-welfare": ("obr", "OBR", "EFO welfare baseline"),
        "ukmod-stats": ("ukmod", "UKMOD", "Country Report validation tables"),
    }
    with db.conn:
        db.conn.execute(
            f"DELETE FROM external_scores WHERE source IN ({placeholders})",
            UK_SOURCES,
        )
        db.conn.executemany(SCORES_SQL, rows)
        register_baselines_txn(db)
        for lane_id, (name, _src_label, _area) in lane_meta.items():
            db.conn.execute(
                LANE_SQL,
                (
                    lane_id,
                    "ingested",
                    f"{summary['claims'][name]} claims"
                    + (
                        f", {summary['ledger'][name]} Chronicle facts"
                        if name in summary["ledger"]
                        else ""
                    ),
                    "2026-08-19",
                ),
            )
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        "2026-08-19",
        lanes={
            lane_id: {"source": s, "area": a, "mode": 1, "country": "UK"}
            for lane_id, (_, s, a) in lane_meta.items()
        },
    )
    db.close()

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_ledger.sort(key=lambda r: r["fact_id"])
    LEDGER_PATH.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in all_ledger) + "\n"
    )
    summary["ledger_path"] = str(LEDGER_PATH)
    return summary


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
