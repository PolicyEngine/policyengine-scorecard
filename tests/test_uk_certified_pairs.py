"""Certified pairs: lane records in the replay variant's identity shape.

Engine-free: the committed registry is validated as stored, mutations are
made on copies, and the preflight's engine steps are stubbed.

Invariants:
- every committed pair validates, under an id pair-<its variant slug>, and
  no pair is a replay variant (neither file names the other's ids);
- a pair binds its identity: changing any one value in it, without
  resealing the digest, is refused (property test);
- a pair's checks are the replay variant's identity checks: given a
  variant's status, layout and result root, the same record passes
  validate_record (differential), and ingest reads the same records;
- the preflight routes a pair through the pair checks and the materialised
  path, and a variant through the event runner's own preflight, never the
  other way round.
"""

import copy
import json
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compute_uk_event as event
from pipeline import uk_certified_pairs as pairs
from pipeline import uk_replay_variants as rv
from scorecard_db import ingest_uk_childcare_100k as lane

PAIR = "pair-pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71"


def stored(pair_id=PAIR) -> dict:
    return copy.deepcopy(
        next(p for p in pairs.load_pairs()["pairs"] if p["pair_id"] == pair_id)
    )


def test_committed_pairs_validate_under_their_slug_and_are_no_variants():
    document = pairs.load_pairs()
    assert document["kind"] == pairs.KIND
    ids = [p["pair_id"] for p in document["pairs"]]
    assert PAIR in ids
    variant_ids = {v["variant_id"] for v in rv.load_document()["variants"]}
    for record in document["pairs"]:
        pairs.validate_pair(record)
        assert record["pair_id"] == pairs.PREFIX + rv.variant_slug(record["identity"])
        assert record["pair_id"] not in variant_ids
        assert record["identity_sha256"] == rv.identity_sha256(record["identity"])
    assert not any(v.startswith(pairs.PREFIX) for v in variant_ids)


def test_get_record_resolves_a_pair_a_variant_and_the_default():
    pair = pairs.get_record(PAIR)
    assert pairs.is_pair(pair) and pair["variant_id"] == PAIR
    assert pair["identity"] == stored()["identity"]
    assert "layout" not in pair and "result_root" not in pair
    assert not rv.is_legacy(pair)
    default = rv.load_document()["default_variant"]
    assert pairs.get_record(None) == rv.get_variant(default)
    assert pairs.get_record(default) == rv.get_variant(default)
    assert not pairs.is_pair(pairs.get_record(default))
    with pytest.raises(rv.VariantError, match="no certified pair"):
        pairs.get_record(PAIR + "x")
    with pytest.raises(rv.VariantError, match="no replay variant"):
        pairs.get_record(PAIR.removeprefix(pairs.PREFIX))


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda r: r.update(layout="replay_namespace"), "holds exactly"),
        (lambda r: r.update(result_root="results/uk/replays/x"), "holds exactly"),
        (lambda r: r.update(variant_id=r["pair_id"]), "holds exactly"),
        (lambda r: r.pop("data_years_evidence"), "holds exactly"),
        (lambda r: r.update(status="certified"), "status must be"),
        (
            lambda r: r.update(pair_id=r["pair_id"].removeprefix(pairs.PREFIX)),
            "starts pair-",
        ),
        (lambda r: r.update(pair_id=r["pair_id"] + "x"), "differs from its identity"),
        (lambda r: r.update(identity_sha256="0" * 64), "identity_sha256 differs"),
        (lambda r: r["requirements"].update(sha256="0" * 64), "requirements"),
        (lambda r: r.update(executor=["cloud"]), "executor"),
        (lambda r: r.update(data_years=[2024, 2026]), "consecutive"),
        (
            lambda r: r["certification"].update(certified_for_model_version="2.89.2"),
            "does not name this model version",
        ),
    ],
)
def test_a_pair_is_refused_for_each_broken_field(change, message):
    record = stored()
    change(record)
    with pytest.raises(rv.VariantError, match=message):
        pairs.validate_pair(record)


def _leaves(value, path=()):
    """(path, value) for every string or integer in a nested record."""
    if isinstance(value, dict):
        for key in sorted(value):
            yield from _leaves(value[key], (*path, key))
    elif isinstance(value, str) or (
        isinstance(value, int) and not isinstance(value, bool)
    ):
        yield path, value


_IDENTITY_LEAVES = list(_leaves(stored()["identity"]))


@settings(max_examples=60, deadline=None)
@given(
    leaf=st.sampled_from(_IDENTITY_LEAVES),
    suffix=st.text(alphabet="0123456789abcdefxyz.-", min_size=1, max_size=4),
)
def test_any_change_to_a_pairs_identity_is_refused(leaf, suffix):
    """The digest binds the identity: one changed value, with the stored
    identity_sha256 kept, never validates."""
    path, value = leaf
    record = stored()
    node = record["identity"]
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value + 1 if isinstance(value, int) else value + suffix
    with pytest.raises(rv.VariantError):
        pairs.validate_pair(record)


def test_a_pairs_checks_are_the_replay_variants_identity_checks():
    """Differential: the stored pair, given a replay variant's own fields,
    is a valid variant record, so validate_identity is the whole of what the
    variant checks apply to it."""
    record = stored()
    variant_id = record.pop("pair_id").removeprefix(pairs.PREFIX)
    record.update(
        variant_id=variant_id,
        status="certified",
        layout="replay_namespace",
        result_root=f"{rv.REPLAY_RESULT_ROOT}/{variant_id}",
    )
    rv.validate_record(record)


def test_ingest_reads_the_records_the_pipeline_resolves():
    """Differential: scorecard_db reads both files itself (it does not
    import pipeline/); for each id they must give the same record."""
    read = lane.run_records()
    certified = [
        v["variant_id"]
        for v in rv.load_document()["variants"]
        if v["status"] == "certified"
    ]
    ids = [p["pair_id"] for p in pairs.load_pairs()["pairs"]]
    assert sorted(read) == sorted([*certified, *ids])
    for record_id in read:
        resolved = pairs.get_record(record_id)
        for field in ("identity", "identity_sha256", "data_years", "variant_id"):
            assert read[record_id][field] == resolved[field], (record_id, field)


def test_the_preflight_routes_each_record_its_own_way(monkeypatch):
    calls = []
    monkeypatch.setattr(
        event,
        "variant_preflight",
        lambda record, dataset_source=None: calls.append(("variant", record)),
    )
    monkeypatch.setattr(
        event,
        "materialized_preflight",
        lambda record, installed, dataset_source=None: calls.append(
            ("materialized", record, installed)
        ),
    )
    monkeypatch.setattr(rv, "verify_installed", lambda record: {"verified": True})
    variant = rv.get_variant(rv.load_document()["variants"][-1]["variant_id"])
    pairs.preflight(variant)
    pair = pairs.get_record(PAIR)
    pairs.preflight(pair, dataset_source=Path("x.h5"))
    assert calls == [
        ("variant", variant),
        ("materialized", pair, {"verified": True}),
    ]


def test_the_preflight_refuses_a_pair_view_changed_after_resolution(monkeypatch):
    monkeypatch.setattr(
        rv, "verify_installed", lambda record: pytest.fail("checked a changed pair")
    )
    pair = pairs.get_record(PAIR)
    pair["identity"]["packages"]["policyengine-uk"]["version"] = "2.143.0"
    with pytest.raises(rv.VariantError):
        pairs.preflight(pair)
    pair = pairs.get_record(PAIR)
    pair["status"] = "certified"
    with pytest.raises(rv.VariantError, match="not a certified pair"):
        pairs.preflight(pair)


def test_the_registry_refuses_a_repeated_id_and_another_kind(tmp_path):
    document = pairs.load_pairs()
    path = tmp_path / "pairs.json"
    path.write_text(json.dumps({**document, "pairs": document["pairs"] * 2}))
    with pytest.raises(rv.VariantError, match="repeats a pair_id"):
        pairs.load_pairs(path)
    path.write_text(json.dumps({**document, "kind": "uk_replay_variants"}))
    with pytest.raises(rv.VariantError, match="kind"):
        pairs.load_pairs(path)
