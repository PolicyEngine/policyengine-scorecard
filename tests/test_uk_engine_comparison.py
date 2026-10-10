"""Descriptive engine-comparison accounting and attribution properties."""

import copy
import hashlib
import json
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compare_uk_engines as engines
from pipeline.compare_uk_obr_costings import ratio_and_bin

FIXTURE = Path(__file__).parent / "fixtures/uk_engine_comparison/attribution.json"


def inputs(
    old=(100, -20),
    new=(120, -25),
    base_aggregate=(1000, 200),
    new_aggregate=(1100, 220),
):
    registry = {
        "event_slug": "event",
        "source": {"claims_sha256": "fixed"},
        "measures": [
            {
                "measure_key": "event__tax",
                "title": "Tax change",
                "construction": "forward_delta_on_certified_world",
                "pe_reform_delta": {"gov.tax.rate": {"2024-01-01.2030-12-31": 0.2}},
                "source_rows": [
                    {
                        "source_row_id": f"row-{i}",
                        "fy": "2024-25",
                        "tax_head": f"Head {i}",
                        "value_gbp": float(obr),
                        "value_gbp_decimal": str(obr),
                        "pe_variables": [f"head_{i}"],
                    }
                    for i, obr in enumerate((90, -15))
                ],
            },
            {
                "measure_key": "event__gap",
                "title": "Gap",
                "source_rows": [
                    {
                        "source_row_id": "gap",
                        "fy": "2023-24",
                        "tax_head": "Other",
                        "value_gbp": 0.0,
                        "value_gbp_decimal": "0",
                    }
                ],
            },
        ],
    }

    def run(values, aggregates, name):
        heads = dict(zip(("head_0", "head_1"), values))
        artifact = {
            "event": "event",
            "measure_key": "event__tax",
            "year": 2024,
            "head_effects": heads,
            "head_channels": {k: "tax" for k in heads},
            "construction": "forward_delta_on_certified_world",
            "totals": {
                "baseline": {"heads": {k: 0 for k in heads}},
                "reform": {"heads": heads},
            },
            "literal_reform_minus_baseline": heads,
            "measure_total_gbp": sum(values),
            "certified_aggregates_gbp": dict(zip(heads, aggregates)),
        }
        rows = [
            {
                "source_row_id": f"row-{i}",
                "pe_value_gbp": value,
                "artifact": name,
                "head_variables": [f"head_{i}"],
                "status": "constructed",
                "classification": "partial",
            }
            for i, value in enumerate(values)
        ]
        rows.append(
            {
                "source_row_id": "gap",
                "pe_value_gbp": None,
                "status": "not_computed",
                "classification": "out_of_household_scope",
            }
        )
        return rows, {name: artifact}

    base_rows, base_artifacts = run(old, base_aggregate, "base.json")
    new_rows, new_artifacts = run(new, new_aggregate, "new.json")
    return (
        registry,
        copy.deepcopy(registry),
        base_rows,
        new_rows,
        base_artifacts,
        new_artifacts,
    )


def verified(root, *names):
    """Treat ``names`` as artifacts from a verified default-bundle manifest."""
    from pipeline import uk_bundle as bundles

    pin = root / "data/uk/certified_bundle.json"
    if not pin.exists():
        pin.parent.mkdir(parents=True)
        pin.write_bytes(bundles.bundle_pin_path().read_bytes())
    return {name: bundles.DEFAULT_BUNDLE for name in names}


def compare(values=None, attribution=None, **kwargs):
    left, right, before, after, old, new = values or inputs()
    return engines.build_engine_rows(
        left,
        right,
        before,
        after,
        attribution or json.loads(FIXTURE.read_text()),
        base_artifacts=old,
        new_artifacts=new,
        **kwargs,
    )


def test_each_source_row_and_zero_kept_and_ratios_are_descriptive():
    rows = compare()
    assert len(rows) == 3
    tax = [r for r in rows if r["measure_key"] == "event__tax"]
    assert sum(r["change_million_gbp"] for r in tax) == pytest.approx(15 / 1e6)
    assert tax[0]["head_certified_aggregate_new_to_base_ratio"] == 1.1
    assert tax[0]["measure_new_to_base_ratio"] == 95 / 80
    assert tax[0]["head_effect_new_to_base_ratio"] == 1.2
    assert all(r["explained_share"] is None for r in rows)
    assert (
        next(r for r in rows if r["source_row_id"] == "gap")["status"]
        == "uncomputed_in_both"
    )


@pytest.mark.parametrize(
    "change",
    ["missing", "unknown", "sized_no_artifact", "unsized_value", "no_evidence"],
)
def test_attribution_rejects_missing_unknown_or_unsupported_sizing(change):
    attribution = json.loads(FIXTURE.read_text())
    driver = attribution["entries"][0]["drivers"][0]
    if change == "missing":
        attribution["entries"] = []
    elif change == "unknown":
        driver["driver"] = "guessed_population_driver"
    elif change == "sized_no_artifact":
        driver.update(sized=True, value_gbp=20)
    elif change == "unsized_value":
        driver["value_gbp"] = 20
    else:
        driver["evidence"] = []
    with pytest.raises(engines.EngineComparisonError):
        compare(attribution=attribution)


def test_explicit_unattributed_is_accepted_without_inference():
    attribution = json.loads(FIXTURE.read_text())
    attribution["entries"][0]["drivers"] = copy.deepcopy(
        attribution["entries"][1]["drivers"]
    )
    rows = compare(attribution=attribution)
    assert [r["attribution"][0]["driver"] for r in rows if r["change_million_gbp"]] == [
        "unattributed",
        "unattributed",
    ]


def test_sized_driver_requires_matching_computed_artifact_hash_and_value(tmp_path):
    values = inputs()
    artifact = values[5]["new.json"]
    payload = engines.canonical_bytes(artifact)
    (tmp_path / "paired.json").write_bytes(payload)
    attribution = json.loads(FIXTURE.read_text())
    attribution["entries"][0]["fy"] = "2024-25"
    driver = attribution["entries"][0]["drivers"][0]
    driver.update(
        sized=True,
        value_gbp=120,
        artifact={
            "path": "paired.json",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "value_path": ["head_effects", "head_0"],
        },
    )
    hashes = {}
    receipts = verified(tmp_path, "paired.json")
    compare(
        values,
        attribution,
        artifact_root=tmp_path,
        input_hashes=hashes,
        verified_artifacts=receipts,
    )
    assert hashes == {"paired.json": hashlib.sha256(payload).hexdigest()}
    # The same artifact outside a verified run manifest sizes nothing.
    with pytest.raises(engines.EngineComparisonError, match="verified run manifest"):
        compare(values, attribution, artifact_root=tmp_path)
    driver["value_gbp"] += 1
    with pytest.raises(engines.EngineComparisonError, match="differs"):
        compare(
            values, attribution, artifact_root=tmp_path, verified_artifacts=receipts
        )
    driver["value_gbp"] -= 1
    driver["artifact"]["sha256"] = "0" * 64
    with pytest.raises(engines.EngineComparisonError, match="SHA-256"):
        compare(
            values, attribution, artifact_root=tmp_path, verified_artifacts=receipts
        )


def test_sized_artifact_from_another_engine_is_rejected(tmp_path):
    """A hash-correct artifact still has to match its bundle's runtime pins."""
    values = inputs()
    artifact = {**values[5]["new.json"], "engine_version": "9.9.9"}
    payload = engines.canonical_bytes(artifact)
    (tmp_path / "foreign.json").write_bytes(payload)
    attribution = json.loads(FIXTURE.read_text())
    attribution["entries"][0]["fy"] = "2024-25"
    attribution["entries"][0]["drivers"][0].update(
        sized=True,
        value_gbp=120,
        artifact={
            "path": "foreign.json",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "value_path": ["head_effects", "head_0"],
        },
    )
    with pytest.raises(ValueError, match="runtime bundle mismatch: engine_version"):
        compare(
            values,
            attribution,
            artifact_root=tmp_path,
            verified_artifacts=verified(tmp_path, "foreign.json"),
        )


def test_total_and_one_of_its_heads_cannot_both_be_sized(tmp_path):
    values = inputs()
    payload = engines.canonical_bytes(values[5]["new.json"])
    (tmp_path / "artifact.json").write_bytes(payload)
    proof = {"path": "artifact.json", "sha256": hashlib.sha256(payload).hexdigest()}
    attribution = json.loads(FIXTURE.read_text())
    entry = attribution["entries"][0]
    entry["fy"] = "2024-25"
    entry["drivers"][0].update(
        sized=True,
        value_gbp=95,
        artifact={**proof, "value_path": ["measure_total_gbp"]},
    )
    entry["drivers"].append(
        {
            "driver": "other_engine_change",
            "evidence": [{"kind": "paired_run", "reference": "artifact.json"}],
            "sized": True,
            "value_gbp": 120,
            "artifact": {**proof, "value_path": ["head_effects", "head_0"]},
        }
    )
    with pytest.raises(engines.EngineComparisonError, match="overlap"):
        compare(
            values,
            attribution,
            artifact_root=tmp_path,
            verified_artifacts=verified(tmp_path, "artifact.json"),
        )


def test_unsized_driver_withholds_explained_share_even_beside_sized(tmp_path):
    values = inputs()
    payload = engines.canonical_bytes(values[5]["new.json"])
    (tmp_path / "artifact.json").write_bytes(payload)
    attribution = json.loads(FIXTURE.read_text())
    attribution["entries"][0]["fy"] = "2024-25"
    attribution["entries"][0]["drivers"].append(
        {
            "driver": "other_engine_change",
            "evidence": [{"kind": "paired_run", "reference": "artifact.json"}],
            "sized": True,
            "value_gbp": 120,
            "artifact": {
                "path": "artifact.json",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "value_path": ["head_effects", "head_0"],
            },
        }
    )
    rows = compare(
        values,
        attribution,
        artifact_root=tmp_path,
        verified_artifacts=verified(tmp_path, "artifact.json"),
    )
    assert all(r["explained_share"] is None for r in rows)
    assert all(
        r["explained_share_withheld"] == "unsized drivers"
        for r in rows
        if r["change_million_gbp"]
    )


@pytest.mark.parametrize(
    "change", ["drop", "duplicate", "source_value", "source_fy", "source_snapshot"]
)
def test_cross_bundle_accounting_cannot_drop_duplicate_or_change_source(change):
    values = list(inputs())
    if change == "drop":
        values[3].pop()
    elif change == "duplicate":
        values[3].append(copy.deepcopy(values[3][0]))
    elif change == "source_value":
        values[1]["measures"][0]["source_rows"][0]["value_gbp_decimal"] = (
            "90.00000000001"
        )
    elif change == "source_fy":
        values[1]["measures"][0]["source_rows"][0]["fy"] = "2025-26"
    else:
        values[1]["source"]["claims_sha256"] = "other"
    with pytest.raises(engines.EngineComparisonError):
        compare(values)


def test_base_only_window_and_changed_construction_are_explicit():
    values = list(inputs())
    values[3][0].update(pe_value_gbp=None, status="outside_bundle_window")
    rows = compare(values)
    assert (
        next(r for r in rows if r["source_row_id"] == "row-0")["status"] == "base_only"
    )
    values[1]["measures"][0]["pe_reform_delta"]["gov.tax.rate"][
        "2024-01-01.2030-12-31"
    ] = 0.3
    rows = compare(values)
    assert {r["status"] for r in rows if r["measure_key"] == "event__tax"} == {
        "construction_changed"
    }
    assert rows[-1]["base_construction_sha256"] != rows[-1]["new_construction_sha256"]


def test_construction_digest_includes_package_components_but_ignores_prose():
    registry = inputs()[0]
    measure = registry["measures"][0]
    before = engines.construction_digest(measure)
    measure["note"] = "Audited prose correction"
    assert engines.construction_digest(measure) == before
    package = {
        "measure_key": "event__package",
        "construction": "package_of_registry_measures",
        "package_of": [measure["measure_key"]],
        "source_rows": [],
    }
    index = {m["measure_key"]: m for m in (measure, package)}
    before = engines.construction_digest(package, index)
    measure["heads"] = [{"obr_head": "Head 0", "pe_variables": ["changed"]}]
    assert engines.construction_digest(package, index) != before


def test_output_order_and_rendering_are_deterministic():
    values = list(inputs())
    before = compare(values)
    values[2].reverse()
    values[3].reverse()
    values[1]["measures"].reverse()
    after = compare(values)
    assert engines.canonical_bytes(before) == engines.canonical_bytes(after)
    assert engines.render_csv(before) == engines.render_csv(after)
    assert engines.render_markdown("base", "new", before) == engines.render_markdown(
        "base", "new", after
    )


@given(
    st.tuples(st.integers(-(10**9), 10**9), st.integers(-(10**9), 10**9)),
    st.tuples(st.integers(-(10**9), 10**9), st.integers(-(10**9), 10**9)),
)
@settings(deadline=None)
def test_swapping_bundles_negates_every_change_and_heads_sum(old, new):
    values = inputs(old, new)
    rows = compare(values)
    reverse = compare(
        (values[1], values[0], values[3], values[2], values[5], values[4])
    )
    assert [r["source_row_id"] for r in rows] == [r["source_row_id"] for r in reverse]
    for left, right in zip(rows, reverse):
        if left["change_million_gbp"] is not None:
            assert left["change_million_gbp"] == -right["change_million_gbp"]
    assert sum(r["change_million_gbp"] or 0 for r in rows) == pytest.approx(
        (sum(new) - sum(old)) / 1e6, abs=1e-10
    )


@given(st.integers(1, 10**9), st.integers(-(10**9), 10**9), st.integers(1, 10**6))
def test_bins_are_invariant_to_common_positive_scale(obr, pe, scale):
    assert ratio_and_bin(obr, pe)[1] == ratio_and_bin(obr * scale, pe * scale)[1]


def test_duplicate_registry_measure_key_is_rejected():
    values = list(inputs())
    duplicate = copy.deepcopy(values[1]["measures"][0])
    duplicate["source_rows"] = []
    values[1]["measures"].append(duplicate)
    with pytest.raises(
        engines.EngineComparisonError, match="duplicate registry measure"
    ):
        compare(values)


def test_named_drivers_cannot_double_count_one_computed_term(tmp_path):
    values = inputs()
    payload = engines.canonical_bytes(values[5]["new.json"])
    (tmp_path / "artifact.json").write_bytes(payload)
    attribution = json.loads(FIXTURE.read_text())
    entry = attribution["entries"][0]
    entry["fy"] = "2024-25"
    first = entry["drivers"][0]
    first.update(
        sized=True,
        value_gbp=120,
        artifact={
            "path": "artifact.json",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "value_path": ["head_effects", "head_0"],
        },
    )
    second = {**copy.deepcopy(first), "driver": "other_engine_change"}
    entry["drivers"].append(second)
    with pytest.raises(engines.EngineComparisonError, match="same computed term"):
        compare(
            values,
            attribution,
            artifact_root=tmp_path,
            verified_artifacts=verified(tmp_path, "artifact.json"),
        )


@pytest.mark.parametrize("scope", [None, ["head_0"]])
@pytest.mark.parametrize("direction", [1, -1])
def test_paired_package_size_is_not_allocated_to_each_source_head(
    tmp_path, scope, direction
):
    from pipeline import uk_bundle as bundles

    values = inputs(
        old=(100 * direction, 100 * direction), new=(120 * direction, 120 * direction)
    )
    measured = inputs(
        old=(100 * direction, 100 * direction), new=(110 * direction, 100 * direction)
    )
    pin_path = tmp_path / "data/uk/certified_bundle.json"
    pin_path.parent.mkdir(parents=True)
    pin_path.write_bytes(bundles.bundle_pin_path().read_bytes())
    endpoints = {}
    for side, artifact in (
        ("base", measured[4]["base.json"]),
        ("new", measured[5]["new.json"]),
    ):
        payload = engines.canonical_bytes(artifact)
        path = tmp_path / f"measured-{side}.json"
        path.write_bytes(payload)
        endpoints[side] = {
            "path": path.name,
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    paired = {
        "artifact_type": "paired_run",
        "status": "computed",
        "effect_gbp": 10 * direction,
        "base_artifact": endpoints["base"],
        "new_artifact": endpoints["new"],
        "base_bundle": bundles.DEFAULT_BUNDLE,
        "new_bundle": bundles.DEFAULT_BUNDLE,
    }
    if scope is not None:
        paired["head_variables"] = scope
    payload = engines.canonical_bytes(paired)
    (tmp_path / "paired.json").write_bytes(payload)
    attribution = json.loads(FIXTURE.read_text())
    entry = attribution["entries"][0]
    entry["fy"] = "2024-25"
    entry["drivers"][0].update(
        sized=True,
        value_gbp=10 * direction,
        artifact={
            "path": "paired.json",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "value_path": ["effect_gbp"],
        },
    )
    receipts = verified(tmp_path, "measured-base.json", "measured-new.json")
    rows = compare(
        values, attribution, artifact_root=tmp_path, verified_artifacts=receipts
    )
    tax = [row for row in rows if row["measure_key"] == "event__tax"]
    if scope is None:
        assert all(row["explained_share"] is None for row in tax)
    else:
        assert tax[0]["explained_share"] == 0.5
        assert tax[1]["explained_share"] is None
    assert (
        tax[1]["explained_share_withheld"]
        == "measure sizing does not isolate this source head"
    )


def test_paired_head_subset_cannot_be_sized_beside_its_superset(tmp_path):
    """Review case: a two-head paired size plus its one-head subset."""
    from pipeline import uk_bundle as bundles

    measured = inputs(old=(100, 100), new=(110, 110))
    receipts = verified(tmp_path, "measured-base.json", "measured-new.json")
    endpoints = {}
    for side, artifact in (
        ("base", measured[4]["base.json"]),
        ("new", measured[5]["new.json"]),
    ):
        payload = engines.canonical_bytes(artifact)
        (tmp_path / f"measured-{side}.json").write_bytes(payload)
        endpoints[side] = {
            "path": f"measured-{side}.json",
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    drivers = []
    for name, driver, scope, effect in (
        ("both.json", "data_release", ["head_0", "head_1"], 20),
        ("subset.json", "other_engine_change", ["head_0"], 10),
    ):
        paired = {
            "artifact_type": "paired_run",
            "status": "computed",
            "effect_gbp": effect,
            "base_artifact": endpoints["base"],
            "new_artifact": endpoints["new"],
            "base_bundle": bundles.DEFAULT_BUNDLE,
            "new_bundle": bundles.DEFAULT_BUNDLE,
            "head_variables": scope,
        }
        payload = engines.canonical_bytes(paired)
        (tmp_path / name).write_bytes(payload)
        drivers.append(
            {
                "driver": driver,
                "evidence": [{"kind": "paired_run", "reference": name}],
                "sized": True,
                "value_gbp": effect,
                "artifact": {
                    "path": name,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "value_path": ["effect_gbp"],
                },
            }
        )
    attribution = json.loads(FIXTURE.read_text())
    attribution["entries"][0].update(fy="2024-25", drivers=drivers)
    values = inputs(old=(100, 100), new=(120, 120))
    with pytest.raises(engines.EngineComparisonError, match="overlap"):
        compare(
            values, attribution, artifact_root=tmp_path, verified_artifacts=receipts
        )
    # Disjoint heads from the same endpoints remain valid.
    drivers[0]["artifact"]["path"] = "other.json"
    other = {
        **json.loads((tmp_path / "both.json").read_bytes()),
        "head_variables": ["head_1"],
        "effect_gbp": 10,
    }
    payload = engines.canonical_bytes(other)
    (tmp_path / "other.json").write_bytes(payload)
    drivers[0]["artifact"]["sha256"] = hashlib.sha256(payload).hexdigest()
    drivers[0]["value_gbp"] = 10
    rows = compare(
        values, attribution, artifact_root=tmp_path, verified_artifacts=receipts
    )
    # Each driver is measured on one head only, so it is unmeasured for the
    # other head's row and the explained share stays withheld there.
    tax = [row for row in rows if row["measure_key"] == "event__tax"]
    assert all(row["explained_share"] is None for row in tax)
    assert all(
        row["explained_share_withheld"]
        == "measure sizing does not isolate this source head"
        for row in tax
    )
