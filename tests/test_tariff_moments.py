"""Baseline-moments capability: adapters, counterparts, and the join."""

import csv
import hashlib
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
    feb = next(
        r
        for r in rows
        if r["period"] == "2025-02" and r["metric"] == "average_tariff_rate"
    )
    # Exact decimal averaging prevents one-ULP drift across Python runtimes.
    assert feb["value"] == 0.04102927158966089
    canada = [r for r in rows if r["geography"] == "ca"]
    assert len(canada) == 24
    assert {r["metric"] for r in canada} == {"average_tariff_rate"}
    canada_jan = next(r for r in canada if r["period"] == "2025-01")
    # Yale's pinned country file reports Canada weighted_etr daily; January is
    # constant at this value before Canada-specific 2025 actions take effect.
    assert abs(canada_jan["value"] - 0.0010094623285953584) < 1e-15
    assert canada_jan["n_days"] == 31
    assert {r["metric"] for r in rows} == {
        "average_tariff_rate",
        "average_additional_tariff_rate",
    }


def test_yale_adapter_output_has_stable_snapshot():
    contract = load("sources/yale-tariff-tracker/source.json")["adapted_output"]
    output = ROOT / contract["path"]
    assert hashlib.sha256(output.read_bytes()).hexdigest() == contract["sha256"]
    assert len(json.loads(output.read_text())) == contract["rows"] == 72


def test_yale_canada_raw_extract_is_authenticated():
    meta = load("sources/yale-tariff-tracker/source.json")["country_series"]
    source_dir = ROOT / "sources" / "yale-tariff-tracker"
    manifest_path = source_dir / meta["vendored_manifest_path"]
    manifest_payload = manifest_path.read_bytes()
    assert (
        hashlib.sha256(manifest_payload).hexdigest()
        == meta["publication_manifest_sha256"]
    )
    manifest = json.loads(manifest_payload)
    country_entry = next(
        entry for entry in manifest["files"] if entry["name"] == "daily_by_country"
    )
    assert country_entry["path"] == meta["publication_path"].removeprefix("release/")
    assert country_entry["sha256"] == meta["publication_sha256"]
    assert country_entry["n_rows"] == meta["publication_rows"]
    assert country_entry["size_bytes"] == meta["publication_size_bytes"]
    overall_entry = next(
        entry for entry in manifest["files"] if entry["name"] == "daily_overall"
    )
    overall_raw = source_dir / "raw" / "daily_overall_2026-06-09.csv"
    assert (
        hashlib.sha256(overall_raw.read_bytes()).hexdigest() == overall_entry["sha256"]
    )

    raw = source_dir / meta["extract_path"]
    payload = raw.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == meta["extract_sha256"]
    assert meta["publication_commit"] == ("39d394d9d1e65af5486dd785e2b3eeb912170ee8")
    assert meta["publication_sha256"] == (
        "15704e514ffe57fde8eaec79c44d0b48232f24ef36c00c1a6d3d8354bcbf0603"
    )
    assert meta["publication_rows"] == 175_200
    assert meta["publication_size_bytes"] == 26_672_778
    assert len(payload) == meta["extract_size_bytes"] == 110_970
    with raw.open() as handle:
        records = list(csv.DictReader(handle))
    assert len(records) == meta["extract_rows"] == 730
    assert {(r["country"], r["country_name"], r["country_abbr"]) for r in records} == {
        ("1220", "Canada", "canada")
    }


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
    assert len(payload["rows"]) == 36
    jan = next(
        r
        for r in payload["rows"]
        if r["period"] == "2025-01" and r["geography"] == "us"
    )
    assert jan["numerator_usd"] == int(extract["2025-01"]["cal_dut_mo"])
    assert abs(jan["value"] - 7133693804 / 321908039017) < 1e-15
    canada = [r for r in payload["rows"] if r["geography"] == "ca"]
    assert len(canada) == 18
    canada_extract = ROOT / "data" / "pe" / "tariff_expost_canada_monthly.csv"
    assert (
        hashlib.sha256(canada_extract.read_bytes()).hexdigest()
        == payload["provenance"]["committed_extract_sha256"]["ca"]
    )
    with canada_extract.open() as handle:
        canada_extract_rows = list(csv.DictReader(handle))
    assert {
        (r["cty_code"], r["iso2"], r["country_name"]) for r in canada_extract_rows
    } == {("1220", "CA", "Canada")}
    canada_jan = next(r for r in canada if r["period"] == "2025-01")
    assert canada_jan["numerator_usd"] == 42259879
    assert canada_jan["denominator_usd"] == 38990368429
    canada_june = next(r for r in canada if r["period"] == "2026-06")
    assert abs(canada_june["value"] - 1060310570 / 37201104889) < 1e-15
    assert payload["provenance"]["margins_parquet_sha256"] == (
        "f7f88f5824112d1a9c6beaaf4addc9b15f795f6ba6d6e4447e72957731c29607"
    )


def test_moments_join_statuses_and_deltas():
    payload = load("app/public/data/moments.json")
    rows = payload["rows"]
    assert payload["summary"]["by_status"] == {
        "not_computed": 516,
        "concept_mismatch": 54,
    }
    # Every external row appears; misses stay on the page.
    assert payload["summary"]["rows"] == len(rows) == 570
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
    canada = [
        r
        for r in rows
        if r["source"] == "yale-tariff-tracker" and r["geography"] == "ca"
    ]
    assert len(canada) == 24
    assert sum(r["status"] == "concept_mismatch" for r in canada) == 18
    assert sum(r["status"] == "not_computed" for r in canada) == 6
    june = next(r for r in canada if r["period"] == "2026-06")
    assert june["external_value"] > june["pe_value"]
    assert "yale-canada-construct-mismatch" in june["annotation_ids"]
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


def test_canada_annotation_is_geography_scoped():
    payload = load("app/public/data/moments.json")
    yale = [r for r in payload["rows"] if r["source"] == "yale-tariff-tracker"]
    assert all(
        "yale-canada-construct-mismatch" in r["annotation_ids"]
        for r in yale
        if r["geography"] == "ca"
    )
    assert all(
        "yale-tpc-divergence-decomposed" not in r["annotation_ids"]
        for r in yale
        if r["geography"] == "ca"
    )
    assert all(
        "yale-vintage-missing-brazil-301-338" not in r["annotation_ids"]
        for r in yale
        if r["geography"] == "ca"
    )
    assert all(
        "yale-canada-construct-mismatch" not in r["annotation_ids"]
        for r in yale
        if r["geography"] == "us"
    )
