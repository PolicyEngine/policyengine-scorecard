"""Checks of the engine-free certified construction audit."""

import hashlib
import json

import pytest

from pipeline import audit_uk_event_constructions as audit


def test_wrong_digest_is_rejected_before_population_or_source_read(
    tmp_path, monkeypatch
):
    dataset = tmp_path / "data.h5"
    dataset.write_bytes(b"not the certified population")
    bundle = {
        "size_bytes": dataset.stat().st_size,
        "sha256": "0" * 64,
        "artifact": "data.h5",
        "revision": "test",
    }

    def premature_read(*args):
        pytest.fail(
            "wrong digest must be rejected before opening H5 or reading packages"
        )

    monkeypatch.setattr(audit, "inspect_h5", premature_read)
    monkeypatch.setattr(audit, "package_version", premature_read)
    monkeypatch.setattr(audit, "source_evidence", premature_read)
    with pytest.raises(ValueError, match="SHA-256"):
        audit.collect_audit(dataset, tmp_path, bundle)


def test_wrong_model_version_is_rejected_before_hdf5_open(tmp_path, monkeypatch):
    dataset = tmp_path / "data.h5"
    raw = b"valid digest, incompatible model"
    dataset.write_bytes(raw)
    bundle = {
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "artifact": "data.h5",
        "revision": "test",
    }
    versions = {
        "policyengine": "5.0.2",
        "policyengine-uk": "3.0.0",
        "policyengine-core": "3.27.1",
    }
    monkeypatch.setattr(audit, "package_version", lambda root, name: versions[name])

    def premature_read(*args):
        pytest.fail("incompatible model must be rejected before reading HDF5")

    monkeypatch.setattr(audit, "inspect_h5", premature_read)
    with pytest.raises(ValueError, match="pinned replay packages"):
        audit.collect_audit(dataset, tmp_path, bundle)


def test_saved_receipt_has_certified_identity_and_keeps_contributions_unsized():
    receipt = json.loads(
        (audit.ROOT / "results/uk/events/CONSTRUCTION_AUDIT.json").read_text()
    )
    bundle = json.loads((audit.ROOT / "data/uk/certified_bundle.json").read_text())
    for field in ("sha256", "size_bytes", "artifact", "revision"):
        assert receipt["certified_dataset"][field] == bundle[field]
    assert receipt["certified_dataset"]["digest_checked_before_hdf5_open"] is True
    # This is the historical execution receipt. Its source digest must remain
    # the original version, even as the current auditor gains bundle selection.
    assert receipt["inspection_script"]["sha256"] == (
        "ec1c6354653da622530b617f5a651c0ddde9320dda15505e4d79136981d9ea8c"
    )
    assert receipt["observations"]["time_period"] == "2023"
    columns = receipt["observations"]["input_columns"]
    assert "property_purchased" in columns["household"]
    assert "other_residential_property_value" in columns["household"]
    assert "additional_residential_property_purchased" not in columns["household"]
    assert "main_residential_property_purchased" not in columns["household"]
    assert "capital_gains" in columns["person"]
    assert "capital_gains_before_response" not in columns["person"]
    totals = receipt["observations"]["household_aggregates"]
    assert (
        totals["purchased_and_other_property_positive_rows"]
        <= totals["property_purchased_true_rows"]
        <= receipt["observations"]["entity_rows"]["household"]
    )
    assert (
        0
        < totals["other_property_stock_gated_by_purchase_weighted_gbp"]
        < totals["other_property_stock_weighted_gbp"]
    )
    assert all(
        row["national_contribution"] == "unsized"
        for row in receipt["construction_limits"]
    )
    source_hashes = {row["file"]: row["sha256"] for row in receipt["source_evidence"]}
    assert (
        source_hashes[
            "policyengine_uk/variables/gov/hmrc/capital_gains_tax/capital_gains_tax.py"
        ]
        == "943c3269a89c74a6470451b5c41fb4863d419e3087a7bc330d79ff79e440a3be"
    )
    assert (
        source_hashes[
            "policyengine_uk/variables/household/consumption/additional_residential_property_purchased.py"
        ]
        == "9547795632c1da3cacba2f11b8b109082e02e18c74cc35e5a726cb504507ba25"
    )
