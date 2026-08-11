"""Baseline-moments capability: adapters, counterparts, and the join."""

import csv
import json
from pathlib import Path

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
    rows = payload["rows"]
    assert payload["summary"]["by_status"] == {
        "not_computed": 510,
        "concept_mismatch": 36,
    }
    # Every external row appears; misses stay on the page.
    assert payload["summary"]["rows"] == len(rows) == 546
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
