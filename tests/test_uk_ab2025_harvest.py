"""The Autumn Budget 2025 harvest (#136): vendored data, checked as data.

sources/harvest-uk-ab2025-2026-09-24/ is the staging every producer's AB2025
claims land in before the tranche-2 ingest exists. Nothing reads it yet, so
these tests are the only thing standing between a staged row and the row
contract in that directory's README.md: field names, closed enums, the
FY-END-year period rule, the fiscal_event slug, measure keys that exist in
the registry, sha256-shaped manifests, and per-family row counts that the
ingest's exact accounting will later read as `read`.
"""

import gzip
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HARVEST = ROOT / "sources" / "harvest-uk-ab2025-2026-09-24"
REGISTRY = json.loads((ROOT / "data" / "uk" / "ab2025_measures.json").read_text())
KEYS = {m["measure_key"] for m in REGISTRY["measures"]}

# Pinned when the harvest was vendored (2026-09-24). A family that gains or
# loses rows changes this table deliberately, in the same commit.
COUNTS = json.loads((HARVEST / "COUNTS.json").read_text())
FAMILIES = sorted(k for k in COUNTS if not k.startswith("_"))

REQUIRED = {
    "source",
    "source_model",
    "value",
    "value_raw",
    "normalization",
    "value_kind",
    "period",
    "time_basis",
    "conditions",
    "reform_hint",
    "measure_key",
    "attribution",
    "benchmark_class",
    "baseline_policy",
    "publication",
    "source_table",
    "source_column",
    "quote",
    "parse_confidence",
    "status",
}
OPTIONAL = {
    "metric",
    "proposed_metric",
    "unit_concept",
    "proposed_unit",
    "proposed_baseline",
    "note",
    "local_artifact",
}
ATTRIBUTION = {"own", "restated", "same_assumptions"}
BENCHMARK_CLASS = {"different_model", "administrative_fact", "same_assumptions"}
VALUE_KIND = {
    "point",
    "central",
    "range_low",
    "range_high",
    "approx_chart_reading",
    "cumulative",
    "categorical",
}
TIME_BASIS = {"fiscal_year", "annual", "point_in_time"}
CONFIDENCE = {"high", "medium", "low"}

from scorecard_db.models import Metric, UnitConcept  # noqa: E402

METRICS = {m.value for m in Metric}
UNITS = {u.value for u in UnitConcept}


def families():
    return sorted(
        p.name
        for p in HARVEST.iterdir()
        if p.is_dir() and (p / "claims_staged.jsonl.gz").exists()
    )


def rows(family):
    with gzip.open(HARVEST / family / "claims_staged.jsonl.gz", "rt") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def manifest(family):
    return [
        json.loads(line)
        for line in (HARVEST / family / "manifest.jsonl").read_text().splitlines()
        if line.strip()
    ]


def test_every_pinned_family_is_present_and_complete():
    assert set(FAMILIES) == set(families()), set(FAMILIES) ^ set(families())
    for fam in families():
        for name in ("NOTES.md", "manifest.jsonl", "claims_staged.jsonl.gz"):
            assert (HARVEST / fam / name).exists(), (fam, name)


@pytest.mark.parametrize("family", FAMILIES)
def test_row_counts_are_pinned(family):
    assert len(rows(family)) == COUNTS[family]["rows"], family
    assert len(manifest(family)) == COUNTS[family]["primaries"], family


@pytest.mark.parametrize("family", FAMILIES)
def test_rows_follow_the_contract(family):
    for i, r in enumerate(rows(family)):
        where = (family, i)
        keys = set(r)
        assert REQUIRED <= keys, (where, REQUIRED - keys)
        assert keys <= REQUIRED | OPTIONAL, (where, keys - REQUIRED - OPTIONAL)
        assert r["status"] == "ok", where
        assert r["attribution"] in ATTRIBUTION, where
        assert r["benchmark_class"] in BENCHMARK_CLASS, where
        assert r["value_kind"] in VALUE_KIND, where
        assert r["time_basis"] in TIME_BASIS, where
        assert r["parse_confidence"] in CONFIDENCE, where
        assert isinstance(r["value"], (int, float)) and not isinstance(
            r["value"], bool
        ), where
        assert isinstance(r["value_raw"], str) and r["value_raw"].strip(), where
        assert isinstance(r["quote"], str) and r["quote"].strip(), where
        # exactly one of metric / proposed_metric, unit / proposed_unit
        assert bool(r.get("metric")) != bool(r.get("proposed_metric")), where
        assert bool(r.get("unit_concept")) != bool(r.get("proposed_unit")), where
        if r.get("metric"):
            assert r["metric"] in METRICS, (where, r["metric"])
        if r.get("unit_concept"):
            assert r["unit_concept"] in UNITS, (where, r["unit_concept"])
        # conditions: str -> str, the fiscal_event slug on every row
        c = r["conditions"]
        assert isinstance(c, dict) and c, where
        for k, v in c.items():
            assert isinstance(k, str) and isinstance(v, str), (where, k, v)
        assert c["fiscal_event"] == "autumn_budget_2025", where
        # period is the FY END year when an fy label is present
        if "fy" in c:
            m = re.fullmatch(r"(\d{4})-(\d{2})", c["fy"])
            assert m, (where, c["fy"])
            assert r["period"] == int(m.group(1)) + 1, (where, c["fy"], r["period"])
            assert r["time_basis"] == "fiscal_year", where
        # OBR costs some measures to 2050-51; RF's parliament-by-parliament
        # context series runs back to 1959; anchors cite FYE 2011
        assert isinstance(r["period"], int) and 1945 <= r["period"] <= 2060, where
        # measure keys exist; a reform score names a measure or explains why not
        if r["measure_key"] is not None:
            assert r["measure_key"] in KEYS, (where, r["measure_key"])
        # publication provenance
        pub = r["publication"]
        for k in ("title", "url", "date", "publisher", "primary_sha256"):
            assert pub.get(k), (where, k)
        assert re.fullmatch(r"[0-9a-f]{64}", pub["primary_sha256"]), where
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", pub["date"]), where


@pytest.mark.parametrize("family", FAMILIES)
def test_every_row_cites_a_manifest_primary(family):
    shas = {m["sha256"] for m in manifest(family)}
    for m in manifest(family):
        assert re.fullmatch(r"[0-9a-f]{64}", m["sha256"]), (family, m.get("url"))
        assert m.get("url") and m.get("title") and m.get("retrieved"), (family, m)
    for i, r in enumerate(rows(family)):
        assert r["publication"]["primary_sha256"] in shas, (family, i)


@pytest.mark.parametrize("family", FAMILIES)
def test_the_family_hash_is_pinned(family):
    """The ingest pins these digests (NZ precedent); a silent edit to a
    vendored row is the failure this catches."""
    digest = hashlib.sha256(
        (HARVEST / family / "claims_staged.jsonl.gz").read_bytes()
    ).hexdigest()
    assert digest == COUNTS[family]["claims_sha256"], family


def test_restated_rows_are_tallied_not_hidden():
    """Re-published official figures are staged with attribution=restated so
    the ingest can drop them under the #86 rule with a count, rather than
    the harvest quietly omitting them."""
    total = sum(
        1 for fam in families() for r in rows(fam) if r["attribution"] == "restated"
    )
    assert total == COUNTS["_totals"]["restated"]


def test_same_assumptions_rows_are_policyengine_computed():
    for fam in families():
        for r in rows(fam):
            if r["attribution"] == "same_assumptions":
                assert r["benchmark_class"] == "same_assumptions", fam
                assert r["source_model"] == "policyengine_uk", fam


def test_totals_reconcile():
    total = sum(v["rows"] for k, v in COUNTS.items() if not k.startswith("_"))
    assert total == COUNTS["_totals"]["rows"]
    assert total == sum(len(rows(fam)) for fam in families())


def test_no_hmt_decile_bar_readings_were_staged():
    """data/uk/hmt_da_packages.yaml value_availability_rule (#61)."""
    for fam in families():
        for r in rows(fam):
            if r["source"] == "hm_treasury":
                assert "Impact on households" not in r["publication"]["title"] or (
                    r["value_kind"] != "approx_chart_reading"
                ), (fam, r["quote"][:80])


def test_the_key_listing_is_derived_from_the_registry():
    """REGISTRY_KEYS.md is a reading aid for the harvest; it must list exactly
    the registry's keys so a staged measure_key can be checked against it."""
    text = (HARVEST / "REGISTRY_KEYS.md").read_text()
    listed = set(re.findall(r"^- `([a-z0-9_]+)` \|", text, flags=re.M))
    assert listed == KEYS, listed ^ KEYS
