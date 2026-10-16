"""CI's real-replay comparison (pipeline/uk_replay_determinism.py)."""

import json
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import uk_replay_determinism as determinism
from pipeline.compute_uk_event import canonical_bytes

ROOT = Path(__file__).resolve().parent.parent
NEWEST = "pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1"
KEY = "autumn_budget_2024__private_school_vat_20pct"
COMMITTED = (
    ROOT / "results/uk/replays" / NEWEST / "autumn_budget_2024" / f"{KEY}_2026.json"
)
EVIDENCE = {
    "processed_parameter_values": {
        "baseline_world": {
            "gov.hmrc.vat.private_school": {"intended": 0.2, "processed": 0.2}
        },
        "reform_world": {
            "gov.hmrc.vat.private_school": {"intended": 0.0, "processed": 0.0}
        },
    },
    "parameter_reform_routes": {
        "baseline_world": {
            "entry_point": "construction_reform",
            "submitted_reform": {},
        },
        "reform_world": {
            "entry_point": "certified_current_law",
            "submitted_reform": None,
        },
    },
}

leaves = st.one_of(
    st.integers(-(10**12), 10**12),
    st.floats(allow_nan=False, allow_infinity=False, width=64),
    st.text(max_size=8),
    st.booleans(),
    st.none(),
)
keys = st.text(min_size=1, max_size=8).filter(
    lambda k: k not in determinism.PROCESSED_EVIDENCE_FIELDS
)
artifacts = st.dictionaries(
    keys,
    st.recursive(leaves, lambda c: st.dictionaries(keys, c, max_size=3), max_leaves=6),
    min_size=1,
    max_size=6,
)


def with_evidence(record, fields=EVIDENCE):
    return canonical_bytes({**record, **fields})


def test_identical_bytes_match_without_notice():
    record = canonical_bytes({"measure_total_gbp": 1.0})
    assert determinism.compare(record, record) == (True, None)


def test_the_committed_6_4_1_artifact_predates_evidence_and_still_reproduces():
    # Review of 500bf94: the 6.4.1 namespace was sealed before #186, whose
    # code adds the evidence fields to every variant artifact.
    committed = COMMITTED.read_bytes()
    record = json.loads(committed)
    assert not set(determinism.PROCESSED_EVIDENCE_FIELDS) & set(record)
    matches, notice = determinism.compare(with_evidence(record), committed)
    assert matches and "predates processed-value evidence" in notice
    assert "processed_parameter_values, parameter_reform_routes" in notice


def test_a_numerical_difference_fails_with_or_without_evidence():
    committed = COMMITTED.read_bytes()
    record = json.loads(committed)
    changed = {**record, "measure_total_gbp": record["measure_total_gbp"] + 1}
    assert determinism.compare(with_evidence(changed), committed) == (False, None)
    assert determinism.compare(canonical_bytes(changed), committed) == (False, None)


def test_a_committed_artifact_with_evidence_is_compared_whole():
    committed = with_evidence({"measure_total_gbp": 1.0})
    other = {
        **EVIDENCE,
        "processed_parameter_values": {
            "baseline_world": {"p": {"intended": 1, "processed": 2}}
        },
    }
    replay = canonical_bytes({"measure_total_gbp": 1.0, **other})
    assert determinism.compare(replay, committed) == (False, None)
    # A partial set of evidence fields also means the whole artifact counts.
    partial = canonical_bytes(
        {
            "measure_total_gbp": 1.0,
            "parameter_reform_routes": EVIDENCE["parameter_reform_routes"],
        }
    )
    assert determinism.compare(with_evidence({"measure_total_gbp": 1.0}), partial) == (
        False,
        None,
    )


def test_a_noncanonical_replay_never_matches_by_stripping():
    committed = canonical_bytes({"measure_total_gbp": 1.0})
    replay = json.dumps({"measure_total_gbp": 1.0, **EVIDENCE}).encode()
    assert determinism.compare(replay, committed) == (False, None)


def test_a_replay_without_evidence_that_differs_fails():
    committed = canonical_bytes({"measure_total_gbp": 1.0})
    assert determinism.compare(
        canonical_bytes({"measure_total_gbp": 2.0}), committed
    ) == (
        False,
        None,
    )


@settings(max_examples=200, deadline=None)
@given(
    artifacts,
    st.sets(st.sampled_from(determinism.PROCESSED_EVIDENCE_FIELDS), min_size=1),
)
def test_removing_exactly_the_evidence_fields_reproduces_an_older_artifact(
    record, fields
):
    evidence = {field: {"any": [1, "x"]} for field in fields}
    matches, notice = determinism.compare(
        canonical_bytes({**record, **evidence}), canonical_bytes(record)
    )
    assert matches and all(field in notice for field in fields)


@settings(max_examples=200, deadline=None)
@given(artifacts, keys, leaves)
def test_any_other_difference_fails(record, key, value):
    changed = {**record, key: value}
    if changed == record:
        return
    replay = canonical_bytes({**changed, **EVIDENCE})
    assert determinism.compare(replay, canonical_bytes(record)) == (False, None)


def test_main_exit_codes_and_notice(tmp_path, capsys):
    committed = tmp_path / "committed.json"
    replayed = tmp_path / "replayed.json"
    committed.write_bytes(canonical_bytes({"a": 1}))
    replayed.write_bytes(canonical_bytes({"a": 1, **EVIDENCE}))
    assert determinism.main([str(replayed), str(committed)]) == 0
    assert "::notice::" in capsys.readouterr().out
    replayed.write_bytes(canonical_bytes({"a": 2, **EVIDENCE}))
    assert determinism.main([str(replayed), str(committed)]) == 1
    assert determinism.main([str(replayed)]) == 2


def test_ci_compares_the_real_replay_through_the_module():
    ci = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    steps = {s.get("name"): s for s in ci["jobs"]["replay-engine"]["steps"]}
    run = steps["One real measure-year replays byte for byte"]["run"]
    assert "-m pipeline.uk_replay_determinism" in run
    assert "cmp " not in run
    # Every certified replay-namespace variant is in the engine matrix.
    document = json.loads((ROOT / "data/uk/replay_variants.json").read_text())
    certified = [
        v["variant_id"] for v in document["variants"] if v["status"] == "certified"
    ]
    assert ci["jobs"]["replay-engine"]["strategy"]["matrix"]["variant"] == certified


@pytest.mark.parametrize("variant", [NEWEST])
def test_the_next_qualification_compares_against_the_newest_committed_run(variant):
    # Review of 500bf94: with 6.4.1's comparisons committed, a new candidate's
    # latest_certified base is that namespace rather than the legacy run.
    from pipeline import uk_replay_qualify as qualify
    from pipeline import uk_replay_variants as rv

    document = rv.load_document()
    record = {"variant_id": "a_new_candidate"}
    base = qualify.base_namespace(
        {"compare_to": "latest_certified"}, record, document, root=ROOT
    )
    assert base == rv.namespace_root(rv.get_variant(variant), root=ROOT)
