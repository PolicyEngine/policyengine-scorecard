"""Baseline-moments capability: adapters, counterparts, and the join."""

import csv
import json
import runpy
from collections import Counter
from pathlib import Path

import pytest

from pipeline import build_moments

ROOT = Path(__file__).resolve().parent.parent


def load(relative):
    return json.loads((ROOT / relative).read_text())


def test_yale_adapter_rows_match_raw():
    rows = load("data/externals/yale-tariff-tracker.json")
    assert all(r["variant"] == "effective_statutory_fixed2024_weights" for r in rows)
    jan = next(
        r
        for r in rows
        if r["period"] == "2025-01" and r["metric"] == "average_tariff_rate"
    )
    # Raw daily weighted_etr is constant over 2025-01 at 0.02909405...
    assert abs(jan["value"] - 0.02909405387654365) < 1e-12
    assert jan["n_days"] == 31
    metrics = {r["metric"] for r in rows}
    assert metrics == {"average_tariff_rate", "average_additional_tariff_rate"}


def test_tpc_adapter_converts_percent_and_splits_types():
    rows = load("data/externals/tpc-tariffs.json")
    assert all(r["variant"] == "statutory_fixed2025_weights_ex_adcvd" for r in rows)
    oct24 = next(
        r for r in rows if r["period"] == "2024-10" and r["subgroup"] == "total"
    )
    assert abs(oct24["value"] - 0.020963804913120545) < 1e-12  # 2.0964% -> fraction
    subgroups = {r["subgroup"] for r in rows}
    assert "section_122" in subgroups and "ieepa" in subgroups


def test_counterparts_match_committed_extract():
    payload = load("data/pe/tariff_counterparts.json")
    with open(ROOT / "data" / "pe" / "tariff_expost_monthly.csv") as handle:
        extract = {r["period"]: r for r in csv.DictReader(handle)}
    assert len(payload["rows"]) == len(extract) == 18
    jan = next(r for r in payload["rows"] if r["period"] == "2025-01")
    assert jan["numerator_usd"] == int(extract["2025-01"]["cal_dut_mo"])
    assert abs(jan["value"] - 7133693804 / 321908039017) < 1e-15
    assert payload["rows"][-1]["period"] == "2026-06"


def test_moments_join_statuses_and_deltas():
    payload = load("app/public/data/moments.json")
    rows = [
        row
        for row in payload["rows"]
        if row["source"] in {"yale-tariff-tracker", "tpc-tariffs"}
    ]
    assert Counter(row["status"] for row in rows) == {
        "not_computed": 510,
        "concept_mismatch": 36,
    }
    # The additive KFF source must not change the existing tariff population.
    assert len(rows) == 546
    mismatch = [r for r in rows if r["status"] == "concept_mismatch"]
    # Mismatch rows are exactly the total-series months our margins cover.
    assert all(r["subgroup"] == "total" for r in mismatch)
    assert all(
        r["pe_variant"] == "expost_collections_contemporaneous" for r in mismatch
    )
    assert all("2025-01" <= r["period"] <= "2026-06" for r in mismatch)
    sample = next(
        r for r in mismatch if r["source"] == "tpc-tariffs" and r["period"] == "2026-06"
    )
    assert sample["delta"] == sample["pe_value"] - sample["external_value"]
    # Fixed-base statutory sits above contemporaneous collections mid-2026.
    assert sample["external_value"] > sample["pe_value"]
    assert all(r["claim_class"] == "baseline_moment" for r in rows)
    annotation_ids = {a["id"] for a in payload["annotations"]}
    assert all(set(r["annotation_ids"]) <= annotation_ids for r in rows)


def _kff_external(period, metric, subgroup="total"):
    return next(
        row
        for row in load("data/externals/kff-remaining-uninsured.json")
        if row["period"] == period
        and row["metric"] == metric
        and row["subgroup"] == subgroup
        and row["geography"] == "US"
    )


def test_kff_adapter_population_percent_units_and_suppression_parser():
    rows = load("data/externals/kff-remaining-uninsured.json")
    adapter = runpy.run_path(
        ROOT / "sources" / "kff-remaining-uninsured" / "adapter.py"
    )
    state_rows = [
        row for row in rows if row["publication_population"] == "state_indicator"
    ]
    brief_rows = [
        row for row in rows if row["publication_population"] == "flagship_brief"
    ]

    assert len(rows) == 57
    assert len(state_rows) == 52
    assert len(brief_rows) == 5
    assert {row["geography"] for row in state_rows} == {
        "US",
        *adapter["STATE_CODES"].values(),
    }
    assert all(row["unit_concept"] == "percent" for row in state_rows)
    assert all(0 <= row["value"] <= 100 for row in state_rows)
    assert _kff_external("2024", "eligible_share_among_uninsured")["value"] == 24.9

    assert adapter["parse_percent"]("NSD") == (None, "suppressed", "NSD")
    assert adapter["parse_percent"]("24.9%") == (24.9, "ok", None)


def _kff_pe_row(
    coverage_variant,
    value,
    *,
    metric="eligible_share_among_uninsured",
    subgroup="total",
):
    return {
        "source": "pe",
        "program": "medicaid",
        "metric": metric,
        "subgroup": subgroup,
        "variant": (f"pe_{coverage_variant}_all_medicaid_pathways_2024_rules"),
        "coverage_variant": coverage_variant,
        "geography": "US",
        "unit_concept": (
            "percent" if metric == "eligible_share_among_uninsured" else "persons"
        ),
        "period": "2024",
        "value": value,
        "engine_version": "1.764.6",
        "data_bundle": (
            "populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z"
        ),
        "bundle_id": "us-5.0.2",
        "computed_at": "2026-08-18T20:00:00+00:00",
        "benchmark_class": "different_model",
        "calibration_relationship": "held_out",
    }


def test_kff_primary_variant_is_descriptive_concept_mismatch():
    external = _kff_external("2024", "eligible_share_among_uninsured")
    reported = _kff_pe_row("reported_uninsured", 31.2)
    modeled = _kff_pe_row("modeled_uninsured", 28.1)
    counterparts = build_moments.index_counterparts([modeled, reported])
    annotations = load("sources/kff-remaining-uninsured/annotations.json")

    row = build_moments.join_external_row(external, counterparts, annotations)

    assert row["status"] == "concept_mismatch"
    assert row["pe_value"] == 31.2
    assert row["pe_variant"] == reported["variant"]
    assert row["delta"] == pytest.approx(31.2 - 24.9)
    assert row["pe_counterpart"] == reported
    assert row["pe_alternatives"] == [modeled]
    assert row["benchmark_class"] == "different_model"
    assert row["calibration_relationship"] == "held_out"
    assert row["engine_version"] == "1.764.6"
    assert row["data_bundle"] == reported["data_bundle"]
    assert {
        "kff-medicaid-pathway-breadth",
        "kff-medicaid-chip-scope",
        "kff-medicaid-coverage-measurement",
        "kff-medicaid-data-and-imputations",
        "kff-medicaid-rules-vintage",
    } <= set(row["annotation_ids"])
    assert "kff-medicaid-rendered-column-caution" in row["annotation_ids"]
    assert "kff-medicaid-brief-vintage" not in row["annotation_ids"]


def test_kff_2022_claim_keeps_2024_reference_out_of_main_comparison():
    external = _kff_external("2022", "eligible_uninsured_count", "children")
    reported = _kff_pe_row(
        "reported_uninsured",
        2_700_000,
        metric="eligible_uninsured_count",
        subgroup="children",
    )
    modeled = _kff_pe_row(
        "modeled_uninsured",
        2_100_000,
        metric="eligible_uninsured_count",
        subgroup="children",
    )
    counterparts = build_moments.index_counterparts([reported, modeled])
    annotations = load("sources/kff-remaining-uninsured/annotations.json")

    row = build_moments.join_external_row(external, counterparts, annotations)

    assert row["period"] == "2022"
    assert row["status"] == "not_computed"
    assert row["pe_value"] is None
    assert row["pe_variant"] is None
    assert row["pe_counterpart"] is None
    assert row["pe_alternatives"] == []
    assert row["delta"] is None
    assert row["pe_reference"] == reported
    assert row["pe_reference_alternatives"] == [modeled]
    assert row["engine_version"] == "1.764.6"
    assert "kff-medicaid-brief-vintage" in row["annotation_ids"]
    assert "kff-medicaid-rendered-column-caution" not in row["annotation_ids"]


def test_kff_suppressed_value_is_retained_without_a_delta():
    external = dict(_kff_external("2024", "eligible_share_among_uninsured"))
    external.update(value=None, status="suppressed", suppression_flag="NSD")
    reported = _kff_pe_row("reported_uninsured", 31.2)
    counterparts = build_moments.index_counterparts([reported])

    row = build_moments.join_external_row(external, counterparts, [])

    assert row["external_status"] == "suppressed"
    assert row["external_value"] is None
    assert row["suppression_flag"] == "NSD"
    assert row["status"] == "suppressed"
    assert row["pe_value"] is None
    assert row["pe_counterpart"] is None
    assert row["delta"] is None


def test_kff_moments_wiring_carries_source_and_pe_provenance():
    external = _kff_external("2024", "eligible_share_among_uninsured")
    reported = _kff_pe_row("reported_uninsured", 31.2)
    modeled = _kff_pe_row("modeled_uninsured", 28.1)
    external_rows = {source: [] for source in build_moments.SOURCES}
    external_rows["kff-remaining-uninsured"] = [external]
    source_meta = {
        source: {"id": source, "claim_class": "baseline_moment"}
        for source in build_moments.SOURCES
    }
    source_meta["kff-remaining-uninsured"] = load(
        "sources/kff-remaining-uninsured/source.json"
    )
    counterpart_payloads = {
        "kff_medicaid": {
            "provenance": {
                "engine_version": reported["engine_version"],
                "data_bundle": reported["data_bundle"],
            },
            "rows": [reported, modeled],
        }
    }

    payload = build_moments.build_payload(
        external_rows,
        source_meta,
        counterpart_payloads,
        load("sources/kff-remaining-uninsured/annotations.json"),
        built="2026-08-18",
    )

    assert "kff-remaining-uninsured" in payload["sources"]
    assert payload["source_meta"]["kff-remaining-uninsured"]["benchmark_class"] == (
        "different_model"
    )
    assert (
        payload["pe_provenance"]["kff_medicaid"]
        == (counterpart_payloads["kff_medicaid"]["provenance"])
    )
    assert payload["summary"] == {
        "rows": 1,
        "by_status": {"concept_mismatch": 1},
    }


def test_committed_kff_moments_have_expected_statuses_and_variants():
    payload = load("app/public/data/moments.json")
    rows = [
        row for row in payload["rows"] if row["source"] == "kff-remaining-uninsured"
    ]
    state_rows = [row for row in rows if row["period"] == "2024"]
    brief_rows = [row for row in rows if row["period"] == "2022"]

    assert len(rows) == 57
    assert Counter(row["status"] for row in rows) == {
        "concept_mismatch": 52,
        "not_computed": 5,
    }
    assert all(row["unit_concept"] == "percent" for row in state_rows)
    assert all(
        row["pe_counterpart"]["coverage_variant"] == "reported_uninsured"
        for row in state_rows
    )
    assert all(
        [alternative["coverage_variant"] for alternative in row["pe_alternatives"]]
        == ["modeled_uninsured"]
        for row in state_rows
    )
    assert all(row["pe_value"] is None for row in brief_rows)
    assert all(row["pe_reference"]["period"] == "2024" for row in brief_rows)
    assert all(row["benchmark_class"] == "different_model" for row in rows)
    assert all(row["calibration_relationship"] == "held_out" for row in rows)


def test_divergence_decomposition_annotation_present():
    payload = load("app/public/data/moments.json")
    ids = {a["id"] for a in payload["annotations"]}
    assert "yale-tpc-divergence-decomposed" in ids
    entry = next(
        a for a in payload["annotations"] if a["id"] == "yale-tpc-divergence-decomposed"
    )
    # The quantification travels with the annotation.
    assert "-1.34p" in entry["text"] and "0.08" in entry["text"]
    # Both tariff sources carry it on their rows.
    for source in ("yale-tariff-tracker", "tpc-tariffs"):
        row = next(r for r in payload["rows"] if r["source"] == source)
        assert "yale-tpc-divergence-decomposed" in row["annotation_ids"]
