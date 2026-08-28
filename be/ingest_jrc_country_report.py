"""Ingest Belgium model claims from the JRC EUROMOD country report.

Primary input is vendored from the Chronicle repository's local
``origin/main`` at commit ``1cab80987a462e00055f259cc56dc6b311c030bf``.
The CSV SHA-256 is
``2ed1f8a677799fefe7cc2f092b4f30221940a2a2fc9deecbf29e7a5f7d71b69f``;
the copied manifest SHA-256 is
``04cb66729ae960f3a6e5c13eff43967ec276b715f6134a9ad599824ea7f3ddb0``.

The artifact has 18 data records, despite the lane brief's 19-row / eight-
claim description: five ``euromod`` MODEL outputs become Scorecard claims; the sixth
``euromod``-labelled value (unemployment benefits) is a NON-SIMULATED
uprated EU-SILC survey input (Table A3.6 marks ``bun`` Simulated=N, p. 127;
``bun_be`` is switched off in the baseline, p. 24; the 11,706 for 2023 is
the SILC income-year-2021 base of 10,416 uprated) and routes to Chronicle
staging with that provenance pinned, never to a model claim; six
``external`` statistical/outturn values route to deterministic Chronicle
staging facts; and six rounded ``ratio`` values are recomputable and never
persisted. Periods are calendar policy-system/output years simulated from EUROMOD
database BE_2022_c1 (EU-SILC 2022 collection, income reference year 2021,
coverage private households — Table 3.1, p. 97), with monetary values
uprated into each simulation year; they are not matched income-reference
years, not SILC collection years, and 2025 is only the report vintage.

Two demo-grade Axiom worker aggregates are attached as ``concept_mismatch``
results. Their vendored inputs are hash-gated, and every annotation names
the period, population-basis, and scope gaps. They are descriptive cross-
model constructions, never replication claims or plain agreement.

Usage:
    PYTHONPATH=. python -m be.ingest_jrc_country_report data/scorecard.db
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from scorecard_db.baselines import register_baselines_txn
from scorecard_db.db import (
    LANE_SQL,
    RESULTS_SQL,
    SCORES_SQL,
    ScorecardDB,
)
from scorecard_db.harvest import REPO, finish
from scorecard_db.ingest_harvest import sync_lane_feed
from scorecard_db.models import (
    BenchmarkClass,
    CalibrationRelationship,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    ReformRef,
    TimeBasis,
    UnitConcept,
    baseline_key,
)

from .aliases import SOURCE, canon
from .worlds import AXIOM_BE_2026_DEMO_WORLD, EUROMOD_WORLD_BY_PERIOD

SOURCE_DIR = REPO / "sources" / "jrc-euromod-be-2025"
SOURCE_CSV = SOURCE_DIR / "jrc_euromod_be_baseline_statistics_2025.csv"
SOURCE_MANIFEST = SOURCE_DIR / "manifest.yaml"
WORKER_RESULTS = SOURCE_DIR / "microcosm_be_v02_worker_results.json"
WORKER_MANIFEST = SOURCE_DIR / "microcosm_be_v02_manifest.json"
LEDGER_PATH = REPO / "data" / "ledger" / "be_admin_outturns.jsonl"

CHRONICLE_COMMIT = "1cab80987a462e00055f259cc56dc6b311c030bf"
CHRONICLE_INTRO_COMMIT = "243c4afb2ebc350af17ad1cd9b4c46d1e7c01ccc"
CSV_SHA256 = "2ed1f8a677799fefe7cc2f092b4f30221940a2a2fc9deecbf29e7a5f7d71b69f"
MANIFEST_SHA256 = "04cb66729ae960f3a6e5c13eff43967ec276b715f6134a9ad599824ea7f3ddb0"
WORKER_RESULTS_SHA256 = (
    "910a7d7756b65fdee4fb8c8a9e711a13f0c78faa9e1839ba7e354101710c335c"
)
WORKER_MANIFEST_SHA256 = (
    "f69cfce742f603c089ba7777749df8afb6c4b5266af2b80097d5480955e2851d"
)
REPORT_URL = (
    "https://euromod-web.jrc.ec.europa.eu/sites/default/files/2025-02/"
    "Y15_CR_BE_final.pdf"
)
# Front matter, Y15_CR_BE_final.pdf p. 3: "The results presented in this
# report are derived using EUROMOD version J1.0+." (2025 is the report
# vintage, not the model release.)
SOURCE_MODEL = "EUROMOD BE (J1.0+)"
DEMO_BANNER = (
    "demo-grade: US survey support records reweighted to Belgian "
    "administrative targets — not Belgian microdata."
)
RULESPEC_COMMIT = "7c85808ae99f5731b21059e643e5e19b66438904"
LANE_ID = "jrc-euromod-be-country-report"
UPDATED = "2026-08-21"

_FIELDS = [
    "value_id",
    "period",
    "validation.metric",
    "validation.series",
    "table_id",
    "source_url",
    "value",
]

# Exact source census. The file hash catches byte drift; this map also makes
# a deliberately injected/parsed row drift fail with an intelligible message.
_EXPECTED_SOURCE_ROWS = {
    "a3_4_national_income_tax_euromod_2023": (
        2023,
        "national_income_tax",
        "euromod",
        "A3.4",
        "77531",
    ),
    "a3_4_national_income_tax_external_2023": (
        2023,
        "national_income_tax",
        "external",
        "A3.4",
        "69325",
    ),
    "a3_4_employee_sics_euromod_2023": (
        2023,
        "employee_social_insurance_contributions",
        "euromod",
        "A3.4",
        "28861",
    ),
    "a3_4_employee_sics_external_2023": (
        2023,
        "employee_social_insurance_contributions",
        "external",
        "A3.4",
        "23715",
    ),
    "a3_6_child_benefits_euromod_2023": (
        2023,
        "child_benefits",
        "euromod",
        "A3.6",
        "7454",
    ),
    "a3_6_child_benefits_external_2023": (
        2023,
        "child_benefits",
        "external",
        "A3.6",
        "8191",
    ),
    "a3_6_unemployment_benefits_euromod_2023": (
        2023,
        "unemployment_benefits",
        "euromod",
        "A3.6",
        "11706",
    ),
    "a3_6_unemployment_benefits_external_2023": (
        2023,
        "unemployment_benefits",
        "external",
        "A3.6",
        "6391",
    ),
    "a3_4_national_income_tax_ratio_2023": (
        2023,
        "national_income_tax",
        "ratio",
        "A3.4",
        "1.12",
    ),
    "a3_4_employee_sics_ratio_2023": (
        2023,
        "employee_social_insurance_contributions",
        "ratio",
        "A3.4",
        "1.22",
    ),
    "a3_6_child_benefits_ratio_2023": (
        2023,
        "child_benefits",
        "ratio",
        "A3.6",
        "0.91",
    ),
    "a3_6_unemployment_benefits_ratio_2023": (
        2023,
        "unemployment_benefits",
        "ratio",
        "A3.6",
        "1.83",
    ),
    "a3_7_gini_euromod_2022": (2022, "gini", "euromod", "A3.7", "22.28"),
    "a3_7_gini_external_2022": (2022, "gini", "external", "A3.7", "24.20"),
    "a3_8_poverty_60_total_euromod_2022": (
        2022,
        "at_risk_poverty_60_median_total",
        "euromod",
        "A3.8",
        "11.23",
    ),
    "a3_8_poverty_60_total_external_2022": (
        2022,
        "at_risk_poverty_60_median_total",
        "external",
        "A3.8",
        "12.30",
    ),
    "a3_7_gini_ratio_2022": (2022, "gini", "ratio", "A3.7", "0.92"),
    "a3_8_poverty_60_total_ratio_2022": (
        2022,
        "at_risk_poverty_60_median_total",
        "ratio",
        "A3.8",
        "0.91",
    ),
}

_EXPECTED_SERIES = {"euromod": 6, "external": 6, "ratio": 6}

# Table A3.6 (p. 127) marks Unemployment benefits (bun) Simulated=N and
# p. 24 states bun_be is switched off in the baseline; its "EUROMOD"
# column is the SILC income-year-2021 base (10,416) uprated per year
# (11,706 for 2023). A survey input is not a model output: it routes to
# Chronicle staging, never to a claim.
_NON_SIMULATED_EUROMOD_METRICS = {"unemployment_benefits"}

_METRICS = {
    "national_income_tax": {
        "name": "National income tax",
        "metric": Metric.TAX_LIABILITY,
        "unit": UnitConcept.EUR,
        "value_kind": "eur",
        "source_unit": "eur_millions",
        "scale": Decimal("1000000"),
        "program": "national_income_tax",
        "underlying_issuer": "NBB",
        "conditions": {
            "population_scope": "national_all_taxpayers",
            "tax_scope": "national_income_tax",
        },
    },
    "employee_social_insurance_contributions": {
        "name": "Employee social insurance contributions",
        "metric": Metric.TAX_LIABILITY,
        "unit": UnitConcept.EUR,
        "value_kind": "eur",
        "source_unit": "eur_millions",
        "scale": Decimal("1000000"),
        "program": "employee_social_insurance_contributions",
        "underlying_issuer": "NBB",
        "conditions": {
            "population_scope": "national_all_employees",
            "contribution_payer": "employee",
        },
    },
    "child_benefits": {
        "name": "Child benefits",
        "metric": Metric.BENEFIT_COST,
        "unit": UnitConcept.EUR,
        "value_kind": "eur",
        "source_unit": "eur_millions",
        "scale": Decimal("1000000"),
        "program": "child_benefit",
        "underlying_issuer": "NBB",
        "conditions": {
            "population_scope": "national_all_recipients",
            "benefit_scope": "child_benefits",
        },
    },
    "unemployment_benefits": {
        "name": "Unemployment benefits",
        "metric": Metric.BENEFIT_COST,
        "unit": UnitConcept.EUR,
        "value_kind": "eur",
        "source_unit": "eur_millions",
        "scale": Decimal("1000000"),
        "program": "unemployment_benefit",
        "underlying_issuer": "RVA",
        "conditions": {
            "population_scope": "national_all_recipients",
            "benefit_scope": "unemployment_benefits",
        },
    },
    "gini": {
        "name": "Gini coefficient",
        "metric": Metric.GINI,
        "unit": UnitConcept.INDEX_0_1,
        "value_kind": "index",
        "source_unit": "gini_x100",
        "scale": Decimal("0.01"),
        "program": None,
        "underlying_issuer": "EU-SILC",
        "conditions": {
            "population_scope": "total_person_population",
            "income_concept": "equivalised_household_standard_disposable_income",
            "housing_costs": "not_deducted",
            "equivalisation": "modified_oecd",
        },
    },
    "at_risk_poverty_60_median_total": {
        "name": "At-risk-of-poverty rate, 60% of median, total",
        "metric": Metric.POVERTY_RATE,
        "unit": UnitConcept.SHARE,
        "value_kind": "share",
        "source_unit": "percent_share",
        "scale": Decimal("0.01"),
        "program": None,
        "underlying_issuer": "EU-SILC",
        "conditions": {
            "population_scope": "total_person_population",
            "income_concept": "equivalised_household_standard_disposable_income",
            "housing_costs": "not_deducted",
            "equivalisation": "modified_oecd",
            "poverty_line": "relative_60_median",
            "subgroup": "total",
        },
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_rows(path: Path = SOURCE_CSV, *, verify_sha: bool = True) -> list[dict]:
    if _sha256(SOURCE_MANIFEST) != MANIFEST_SHA256:
        raise ValueError("vendored Chronicle manifest SHA-256 drifted")
    if verify_sha and _sha256(path) != CSV_SHA256:
        raise ValueError(f"{path}: SHA-256 drifted from vendored Chronicle source")
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != _FIELDS:
            raise ValueError(
                f"{path}: CSV fields {reader.fieldnames!r} != expected {_FIELDS!r}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return rows


def _validate_rows(rows: list[dict]) -> None:
    seen: dict[str, tuple] = {}
    for row in rows:
        if set(row) != set(_FIELDS):
            raise ValueError(
                f"{row.get('value_id', '<unknown>')}: unhandled CSV fields "
                f"{sorted(set(row) ^ set(_FIELDS))}"
            )
        value_id = row["value_id"]
        if value_id in seen:
            raise ValueError(f"duplicate source value_id: {value_id}")
        try:
            period = int(row["period"])
            value = Decimal(row["value"])
        except (ValueError, ArithmeticError) as exc:
            raise ValueError(f"{value_id}: invalid period/value") from exc
        if not value.is_finite():
            raise ValueError(f"{value_id}: non-finite value")
        metric = canon(SOURCE, "metric", row["validation.metric"])
        series = canon(SOURCE, "series", row["validation.series"])
        table = canon(SOURCE, "table", row["table_id"])
        canon(SOURCE, "geography", "BE")
        canon(SOURCE, "publisher", SOURCE)
        canon(SOURCE, "model", SOURCE_MODEL)
        if row["source_url"] != REPORT_URL:
            raise ValueError(f"{value_id}: unregistered source URL")
        seen[value_id] = (period, metric, series, table, row["value"])
    if seen != _EXPECTED_SOURCE_ROWS:
        missing = sorted(set(_EXPECTED_SOURCE_ROWS) - set(seen))
        extra = sorted(set(seen) - set(_EXPECTED_SOURCE_ROWS))
        changed = sorted(
            key
            for key in set(seen) & set(_EXPECTED_SOURCE_ROWS)
            if seen[key] != _EXPECTED_SOURCE_ROWS[key]
        )
        raise ValueError(
            "JRC BE source census drifted: "
            f"missing={missing}, extra={extra}, changed={changed}"
        )
    counts = Counter(row["validation.series"] for row in rows)
    if dict(counts) != _EXPECTED_SERIES:
        raise ValueError(f"JRC BE series accounting drifted: {dict(counts)}")


def _condition(axis: str, value: str) -> str:
    return canon(SOURCE, axis, value)


def _conditions(metric_name: str, period: int, series: str) -> dict[str, str]:
    config = _METRICS[metric_name]
    conditions = {
        "country": "BE",
        "geography": _condition("geography", "BE"),
        "benchmark_class": (
            BenchmarkClass.DIFFERENT_MODEL.value
            if series == "euromod"
            else BenchmarkClass.ADMINISTRATIVE_FACT.value
        ),
        "series": _condition("series", series),
        "assessment_level": _condition("assessment_level", "individual"),
        "data_vintage": _condition("data_vintage", "euromod_be_country_report_2025"),
        "source_scale": _condition(
            "source_scale",
            {
                "eur_millions": "millions",
                "gini_x100": "times_100",
                "percent_share": "percent",
            }[config["source_unit"]],
        ),
    }
    if series == "euromod":
        conditions["policy_system_year"] = str(period)
        # Table 3.1, p. 97: coverage "Private households"; database
        # BE_2022_c1 = SILC 2022 collection, income reference year 2021.
        conditions["population_frame"] = _condition(
            "population_frame", "private_households"
        )
        conditions["input_database"] = _condition(
            "input_database", "be_2022_c1_silc2022_income2021"
        )
    else:
        conditions["reference_year"] = str(period)
    for axis, value in config["conditions"].items():
        conditions[axis] = _condition(axis, value)
    if config["program"] is not None:
        conditions["program"] = _condition("program", config["program"])
    return conditions


def _publication(row: dict) -> dict:
    is_model = (
        row["validation.series"] == "euromod"
        and row["validation.metric"] not in _NON_SIMULATED_EUROMOD_METRICS
    )
    is_survey_input = (
        row["validation.series"] == "euromod"
        and row["validation.metric"] in _NON_SIMULATED_EUROMOD_METRICS
    )
    publication = {
        "name": _METRICS[row["validation.metric"]]["name"],
        "title": "EUROMOD Country Report Belgium 2025",
        "publisher": "European Commission Joint Research Centre",
        "url": REPORT_URL,
        "date": "2025-02",
        "vintage": "euromod_be_country_report_2025",
        "table": row["table_id"],
        "vendored_csv": str(SOURCE_CSV.relative_to(REPO)),
        "csv_sha256": CSV_SHA256,
        "chronicle_commit": CHRONICLE_COMMIT,
        "period_semantics": (
            "calendar policy-system/output year simulated from EUROMOD "
            "database BE_2022_c1 (EU-SILC 2022, income reference year "
            "2021) with monetary uprating to the simulation year; not a "
            "matched income-reference year and not the SILC collection year"
            if is_model
            else (
                "calendar simulation year of a NON-SIMULATED uprated "
                "EU-SILC survey input (Table A3.6 Simulated=N, p. 127; "
                "bun_be off in the baseline, p. 24; SILC income-year-2021 "
                "base 10,416 uprated to 11,706 for 2023)"
                if is_survey_input
                else "calendar reference year of the statistical/admin "
                "series; not a EUROMOD policy-system year"
            )
        ),
    }
    if row["validation.metric"] in {
        "gini",
        "at_risk_poverty_60_median_total",
    }:
        publication["equivalisation_note"] = (
            "modified-OECD verified against the report itself: "
            "Y15_CR_BE_final.pdf p. 104 states household disposable income is "
            "equivalised by the 'modified OECD' equivalence scale for the "
            "section covering Tables A3.7 and A3.8 (reviewer-checked 2026-08-21)"
        )
    return publication


def _canonical_value(row: dict) -> float:
    config = _METRICS[row["validation.metric"]]
    return float(Decimal(row["value"]) * config["scale"])


def _score(row: dict) -> ExternalScore:
    metric_name = row["validation.metric"]
    config = _METRICS[metric_name]
    period = int(row["period"])
    canon(SOURCE, "unit", config["source_unit"])
    return ExternalScore(
        source=SOURCE,
        source_model=canon(SOURCE, "model", SOURCE_MODEL),
        source_column=row["value_id"],
        publication=_publication(row),
        metric=config["metric"],
        unit_concept=config["unit"],
        period=period,
        time_basis=TimeBasis.ANNUAL,
        value=_canonical_value(row),
        value_kind=config["value_kind"],
        conditions=_conditions(metric_name, period, "euromod"),
        reform=ReformRef(
            framework="baseline", baseline=EUROMOD_WORLD_BY_PERIOD[period]
        ),
        calibration_relationship=CalibrationRelationship.HELD_OUT,
    )


def _ledger_row(row: dict) -> dict:
    metric_name = row["validation.metric"]
    config = _METRICS[metric_name]
    period = int(row["period"])
    canon(SOURCE, "unit", config["source_unit"])
    series = row["validation.series"]
    non_simulated = series == "euromod"
    identity = f"{SOURCE}|{row['value_id']}"
    return {
        "fact_id": "be-admin-" + hashlib.sha256(identity.encode()).hexdigest()[:16],
        "source": SOURCE,
        "publisher": "European Commission Joint Research Centre",
        "underlying_issuer": (
            "EU-SILC" if non_simulated else config["underlying_issuer"]
        ),
        "source_column": row["value_id"],
        "publication": _publication(row),
        "table": row["table_id"],
        "metric": config["metric"].value,
        "program": config["program"],
        "period": period,
        "period_semantics": (
            "simulation_year_of_uprated_survey_input"
            if non_simulated
            else "calendar_statistical_reference_year"
        ),
        "geography": "BE",
        "subgroup": "total",
        "unit_concept": config["unit"].value,
        "unit": config["source_unit"],
        "value_kind": config["value_kind"],
        "source_unit": config["source_unit"],
        "source_value": row["value"],
        "value": _canonical_value(row),
        "conditions": (
            _survey_input_conditions(metric_name, period)
            if non_simulated
            else _conditions(metric_name, period, series)
        ),
        "benchmark_class": (
            "survey_statistic"
            if non_simulated
            else BenchmarkClass.ADMINISTRATIVE_FACT.value
        ),
        "status": "ok",
        "consumed_by": None,
        "routing": (
            "chronicle: non-simulated uprated EU-SILC survey input published "
            "in the report's EUROMOD column (Table A3.6 Simulated=N, "
            "p. 127; bun_be switched off in the baseline, p. 24; SILC "
            "income-year-2021 base 10,416 uprated to the simulation year)"
            if non_simulated
            else "chronicle: statistical/admin outturn (boundary rule 2026-08-02)"
        ),
    }


def _survey_input_conditions(metric_name: str, period: int) -> dict[str, str]:
    """Conditions for the non-simulated uprated EU-SILC survey input.

    Starts from the external-series shape (a statistical value keyed by
    reference year), then overrides the series and class: the value sits in
    the report's EUROMOD column but Table A3.6 marks it Simulated=N (p. 127)
    and ``bun_be`` is switched off in the baseline (p. 24). Model-only pins
    (policy-system year, private-household frame, input database) are
    deliberately absent — those describe executed model output.
    """
    conditions = _conditions(metric_name, period, "external")
    conditions["series"] = _condition("series", "euromod_non_simulated_input")
    conditions["benchmark_class"] = "survey_statistic"
    # One truthful period identity: 2023 is the SIMULATION year the SILC
    # income-year-2021 base is uprated to — not a statistical reference year.
    del conditions["reference_year"]
    conditions["simulation_year"] = str(period)
    return conditions


def _validate_ratios(rows: list[dict]) -> None:
    grouped: dict[tuple[int, str], dict[str, Decimal]] = {}
    for row in rows:
        key = (int(row["period"]), row["validation.metric"])
        grouped.setdefault(key, {})[row["validation.series"]] = Decimal(row["value"])
    for key, series in grouped.items():
        if set(series) != {"euromod", "external", "ratio"}:
            raise ValueError(f"{key}: incomplete euromod/external/ratio triplet")
        derived = (series["euromod"] / series["external"]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if derived != series["ratio"]:
            raise ValueError(
                f"{key}: ratio {series['ratio']} != rounded euromod/external {derived}"
            )


def stage_all(
    rows: list[dict] | None = None,
) -> tuple[list[ExternalScore], list[dict], dict]:
    """Stage the complete artifact and enforce its 5/7/6 accounting."""
    rows = _load_rows() if rows is None else rows
    _validate_rows(rows)
    _validate_ratios(rows)
    scores = finish(
        [
            _score(row)
            for row in rows
            if row["validation.series"] == "euromod"
            and row["validation.metric"] not in _NON_SIMULATED_EUROMOD_METRICS
        ],
        SOURCE,
    )
    ledger = [
        _ledger_row(row)
        for row in rows
        if row["validation.series"] == "external"
        or (
            row["validation.series"] == "euromod"
            and row["validation.metric"] in _NON_SIMULATED_EUROMOD_METRICS
        )
    ]
    ledger.sort(key=lambda row: row["fact_id"])
    summary = {
        "claims": len(scores),
        "ledger_facts": len(ledger),
        "ratios_dispositioned": sum(
            row["validation.series"] == "ratio" for row in rows
        ),
        "source_records": len(rows),
    }
    if summary != {
        "claims": 5,
        "ledger_facts": 7,
        "ratios_dispositioned": 6,
        "source_records": 18,
    }:
        raise ValueError(f"JRC BE staging accounting drifted: {summary}")
    return scores, ledger, summary


def _load_attachment_inputs() -> tuple[dict, dict]:
    if _sha256(WORKER_RESULTS) != WORKER_RESULTS_SHA256:
        raise ValueError("Belgium worker-results SHA-256 drifted")
    if _sha256(WORKER_MANIFEST) != WORKER_MANIFEST_SHA256:
        raise ValueError("Belgium population-manifest SHA-256 drifted")
    worker = json.loads(WORKER_RESULTS.read_text())
    manifest = json.loads(WORKER_MANIFEST.read_text())
    if (
        worker.get("description") != DEMO_BANNER
        or manifest.get("description") != DEMO_BANNER
    ):
        raise ValueError("Belgium demo-grade banner drifted")
    if manifest.get("year") != 2026:
        raise ValueError("Belgium demo population period drifted")
    program = worker.get("program", {})
    if (
        program.get("rulespec_be_commit") != RULESPEC_COMMIT
        or program.get("period", {}).get("period_kind") != "calendar_year"
        or program.get("period", {}).get("start") != "2026-01-01"
        or program.get("period", {}).get("end") != "2026-12-31"
    ):
        raise ValueError("Belgium worker-program identity/period drifted")
    if manifest.get("source_revisions", {}).get("rulespec_be") != RULESPEC_COMMIT:
        raise ValueError("Belgium manifest rulespec pin drifted")
    return worker, manifest


_ATTACHMENTS = {
    "a3_4_national_income_tax_euromod_2023": (
        "worker_pit_before_withholding_communal_0",
        "worker PIT before withholding, communal rate 0",
        "national all-taxpayer income-tax total",
    ),
    "a3_4_employee_sics_euromod_2023": (
        "employee_ssc_article_38_before_reductions",
        "Article 38 employee SSC before reductions",
        "national all-employee regular employee-SIC total",
    ),
}


def stage_results(scores: list[ExternalScore]) -> list[PEResult]:
    worker, manifest = _load_attachment_inputs()
    by_source_column = {score.source_column: score for score in scores}
    if not set(_ATTACHMENTS) <= set(by_source_column):
        raise ValueError("Belgium attachment claims missing from staged source")
    aggregates = worker.get("aggregates_eur", {})
    results = []
    for source_column, (
        aggregate,
        constructed_scope,
        claim_scope,
    ) in _ATTACHMENTS.items():
        value = aggregates.get(aggregate)
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(
                f"Belgium worker aggregate {aggregate!r} missing/non-finite"
            )
        score = by_source_column[source_column]
        annotation = (
            f"{DEMO_BANNER} Concept gaps: period is CY2026 versus the claim's "
            f"CY{score.period}; population basis is US survey support reweighted "
            "to Belgian administrative targets versus the country report's "
            "Belgian SILC basis; scope is a positive-remuneration worker slice "
            f"({constructed_scope}) versus {claim_scope}. Benchmark class is "
            "different_model and the executed Axiom baseline differs from the "
            "EUROMOD published-claim world; this is not a comparable result."
        )
        recipe = {
            "aggregate": f"aggregates_eur.{aggregate}",
            "attachment_class": ComparisonStatus.CONCEPT_MISMATCH.value,
            "claim_period": score.period,
            "computed_period": 2026,
            "population_basis": "US survey support reweighted to Belgian administrative targets",
            "claim_population_basis": "Belgian SILC country-report basis",
            "computed_scope": constructed_scope,
            "claim_scope": claim_scope,
            "rulespec_be_commit": RULESPEC_COMMIT,
            "worker_results_sha256": WORKER_RESULTS_SHA256,
            "population_manifest_sha256": WORKER_MANIFEST_SHA256,
        }
        results.append(
            PEResult(
                claim_id=score.claim_id(),
                computed_value=float(value),
                status=ComparisonStatus.CONCEPT_MISMATCH,
                engine_version=(
                    f"axiom-rules-engine {worker['runtime']['axiom_rules_engine']}; "
                    f"rulespec-be@{RULESPEC_COMMIT}"
                ),
                data_bundle=(
                    "microcosm_be_v02_2026@"
                    + manifest["artifacts"]["microcosm_be_v02_2026.h5"]["sha256"]
                ),
                pe_construction=json.dumps(recipe, sort_keys=True),
                run_id=f"microcosm_be_v02_worker@{WORKER_RESULTS_SHA256}",
                computed_at=worker["created_at"],
                annotations=[annotation],
                baseline_key=baseline_key(AXIOM_BE_2026_DEMO_WORLD),
            )
        )
    return results


def ingest(db_path: Path) -> dict:
    """Validate first, then atomically replace claims/results/registry/lane."""
    scores, ledger, summary = stage_all()
    results = stage_results(scores)
    score_rows = [ScorecardDB.score_row(score) for score in scores]
    result_rows = [ScorecardDB.result_row(result) for result in results]
    db = ScorecardDB(db_path)
    try:
        with db.conn:
            db.conn.execute(
                "DELETE FROM diagnoses WHERE claim_id IN "
                "(SELECT claim_id FROM external_scores WHERE source = ?)",
                (SOURCE,),
            )
            db.conn.execute(
                "DELETE FROM pe_results WHERE claim_id IN "
                "(SELECT claim_id FROM external_scores WHERE source = ?)",
                (SOURCE,),
            )
            db.conn.execute("DELETE FROM external_scores WHERE source = ?", (SOURCE,))
            pub_rows, reform_rows = ScorecardDB.provenance_rows(scores)
            db.insert_provenance(pub_rows, reform_rows)
            db.conn.executemany(SCORES_SQL, score_rows)
            db.prune_provenance()
            db.conn.executemany(RESULTS_SQL, result_rows)
            register_baselines_txn(db)
            db.conn.execute(
                LANE_SQL,
                (
                    LANE_ID,
                    "computed",
                    "5 model claims, 7 Chronicle facts (6 statistical + 1 "
                    "non-simulated uprated EU-SILC survey input), 6 derived "
                    "ratios dispositioned; 2 concept-mismatch attachments",
                    UPDATED,
                ),
            )
        sync_lane_feed(
            db,
            REPO / "data" / "lanes.json",
            UPDATED,
            lanes={
                LANE_ID: {
                    "source": "JRC EUROMOD",
                    "area": "Belgium Country Report validation tables",
                    "mode": 1,
                    "country": "BE",
                }
            },
        )
    finally:
        db.close()

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in ledger) + "\n"
    )
    return summary | {
        "attachments": len(results),
        "ledger_path": str(LEDGER_PATH),
        "lane": LANE_ID,
    }


if __name__ == "__main__":
    import sys

    output = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(output), indent=1))
