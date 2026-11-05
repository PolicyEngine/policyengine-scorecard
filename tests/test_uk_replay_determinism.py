"""CI's real-replay comparison (pipeline/uk_replay_determinism.py)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import uk_replay_determinism as determinism
from pipeline.compute_uk_event import canonical_bytes

ROOT = Path(__file__).resolve().parent.parent
# Sealed before #186 (its artifacts carry no processed-value evidence).
PRE_EVIDENCE = "pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1"
# The first namespace sealed after #186 (its artifacts carry the evidence).
POST_EVIDENCE = "pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1"
# The newest certified variant; the results pull request
# (pipeline/uk_replay_results_pr.py) moves it to each newly certified one.
NEWEST = "pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504"
KEY = "autumn_budget_2024__private_school_vat_20pct"
COMMITTED = (
    ROOT
    / "results/uk/replays"
    / PRE_EVIDENCE
    / "autumn_budget_2024"
    / f"{KEY}_2026.json"
)
# What #186's code writes for this forward delta on policyengine-uk 2.130.1
# (review of f0ff21a): the baseline is certified current law, the reform the
# construction's window.
PATH = "gov.contrib.labour.private_school_vat"
EVIDENCE = {
    "processed_parameter_values": {
        "baseline_world": {PATH: {"intended": 0.0, "processed": 0.0}},
        "reform_world": {PATH: {"intended": 0.2, "processed": 0.2}},
    },
    "parameter_reform_routes": {
        "baseline_world": {
            "entry_point": "certified_current_law",
            "submitted_reform": None,
        },
        "reform_world": {
            "entry_point": "construction_reform",
            "submitted_reform": {PATH: {"2025-01-01.2035-12-31": 0.2}},
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


def test_a_namespace_sealed_after_186_is_compared_whole():
    # The 6.5.0 artifacts carry the evidence, so the replay must match every
    # byte: removing the fields never makes a replay match one of them.
    committed = (
        ROOT
        / "results/uk/replays"
        / POST_EVIDENCE
        / "autumn_budget_2024"
        / f"{KEY}_2026.json"
    ).read_bytes()
    record = json.loads(committed)
    assert {"processed_parameter_values", "parameter_reform_routes"} <= set(record)
    assert determinism.compare(committed, committed) == (True, None)
    stripped = {
        k: v
        for k, v in record.items()
        if k not in determinism.PROCESSED_EVIDENCE_FIELDS
    }
    assert determinism.compare(canonical_bytes(stripped), committed) == (False, None)
    other = {**record, "measure_total_gbp": record["measure_total_gbp"] + 1}
    assert determinism.compare(canonical_bytes(other), committed) == (False, None)


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
    # Bytes, not Python equality: True and 1, or -0.0 and 0.0, serialise
    # differently and must fail too.
    if canonical_bytes(changed) == canonical_bytes(record):
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
    # The replay runs in the candidate sandbox; the comparison runs outside
    # it, under the runner's own Python (-E: no PYTHON* variables, -s: no
    # user site), on the runner's checkout, against the committed artifact
    # the job itself names.
    workflow = ROOT / ".github/workflows/uk-replay-determinism.yml"
    job = yaml.safe_load(workflow.read_text())["jobs"]["real-replay"]
    steps = {s.get("name"): s for s in job["steps"]}
    run = steps["One real measure-year replays byte for byte"]["run"]
    assert run.split() == [
        "/usr/bin/python3",
        "-E",
        "-s",
        "-m",
        "pipeline.uk_replay_determinism",
        "\\",
        '"output/${REPLAY_MEASURE}_${REPLAY_YEAR}.json"',
        '"$RESULT_ROOT/$REPLAY_EVENT/${REPLAY_MEASURE}_${REPLAY_YEAR}.json"',
    ]
    assert {k: job["env"][k] for k in ("REPLAY_EVENT", "REPLAY_MEASURE")} == {
        "REPLAY_EVENT": "autumn_budget_2024",
        "REPLAY_MEASURE": KEY,
    }
    assert job["env"]["REPLAY_YEAR"] == "2026"
    # Every sealed namespace holds the artifact the job compares against.
    from pipeline import uk_replay_variants as rv

    for variant in rv.load_document()["variants"]:
        root = ROOT / variant["result_root"]
        if (root / "REPLAY_RECEIPT.json").is_file():
            assert (root / "autumn_budget_2024" / f"{KEY}_2026.json").is_file()
    # The engine matrix is every certified variant: CI lists them from the
    # index (tests/test_uk_replay_engine_matrix.py).


def test_the_runners_python_needs_only_the_standard_library():
    # Outside the sandbox the job imports these two modules under the
    # runner's own Python, which has nothing installed. Without site (-S)
    # nothing but the standard library can be imported.
    program = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "import pipeline.uk_replay_determinism, pipeline.uk_replay_variants; "
        "print(sorted(name for name in sys.modules if name.startswith('pipeline')))"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", program, str(ROOT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == repr(
        ["pipeline", "pipeline.uk_replay_determinism", "pipeline.uk_replay_variants"]
    )


def test_the_find_step_runs_on_the_standard_library_alone(tmp_path):
    # The job's own program, under the runner's Python without site-packages
    # (-S), reaches find_dataset_bytes: with an empty hub cache it reports
    # the missing dataset, not a missing module.
    workflow = ROOT / ".github/workflows/uk-replay-determinism.yml"
    job = yaml.safe_load(workflow.read_text())["jobs"]["real-replay"]
    (find,) = [
        s
        for s in job["steps"]
        if s.get("name") == "Find the fetched dataset by its digest"
    ]
    program = find["run"].split("/usr/bin/python3 -I -c '", 1)[1].split("'", 1)[0]
    from pipeline import uk_replay_variants as rv

    variant = [
        v["variant_id"]
        for v in rv.load_document()["variants"]
        if v["status"] == "certified" and v["layout"] == "replay_namespace"
    ][-1]
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", program, variant],
        cwd=ROOT,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(tmp_path),
            "HF_HUB_CACHE": str(tmp_path),
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "VariantError" in result.stderr and "no local file holds" in result.stderr
    assert "ModuleNotFoundError" not in result.stderr


json_values = st.recursive(
    leaves,
    lambda children: st.one_of(
        st.lists(children, max_size=3),
        st.dictionaries(st.text(max_size=8), children, max_size=3),
    ),
    max_leaves=12,
)


@settings(max_examples=300, deadline=None)
@given(json_values)
def test_the_comparisons_canonical_bytes_are_the_engines(value):
    # Differential: the module's own copy against compute_uk_event's, which
    # writes the committed artifacts.
    assert determinism.canonical_bytes(value) == canonical_bytes(value)


@pytest.mark.parametrize("value", [float("nan"), {"x": float("inf")}])
def test_both_canonical_forms_refuse_what_json_cannot_hold(value):
    for encode in (determinism.canonical_bytes, canonical_bytes):
        with pytest.raises(ValueError):
            encode(value)


def test_main_takes_only_a_regular_file_as_the_replay(tmp_path, capsys):
    committed = tmp_path / "committed.json"
    committed.write_bytes(canonical_bytes({"a": 1}))
    # A link to the committed artifact reproduces nothing.
    link = tmp_path / "link.json"
    link.symlink_to(committed)
    assert determinism.main([str(link), str(committed)]) == 1
    assert "not a regular file" in capsys.readouterr().err
    directory = tmp_path / "directory.json"
    directory.mkdir()
    assert determinism.main([str(directory), str(committed)]) == 1
    assert determinism.main([str(tmp_path / "absent.json"), str(committed)]) == 1
    copy = tmp_path / "copy.json"
    copy.write_bytes(committed.read_bytes())
    assert determinism.main([str(copy), str(committed)]) == 0


def test_the_module_runs_as_the_job_runs_it(tmp_path):
    committed = tmp_path / "committed.json"
    replayed = tmp_path / "replayed.json"
    committed.write_bytes(canonical_bytes({"a": 1}))
    replayed.write_bytes(canonical_bytes({"a": 1, **EVIDENCE}))
    # The job's environment sets PYTHONPATH, which comes before the standard
    # library; -E keeps an impostor json there from standing in for it.
    impostor = tmp_path / "impostor"
    impostor.mkdir()
    (impostor / "json.py").write_text("raise SystemExit(97)")
    environment = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(impostor)}
    result = subprocess.run(
        [sys.executable, "-E", "-s", "-m", "pipeline.uk_replay_determinism"]
        + [str(replayed), str(committed)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "::notice::" in result.stdout and "reproduces" in result.stdout


@pytest.mark.parametrize("variant", [NEWEST])
def test_the_next_qualification_compares_against_the_newest_committed_run(variant):
    # Review of 500bf94: a new candidate's latest_certified base is the
    # newest certified namespace with committed comparisons, not the legacy run.
    from pipeline import uk_replay_qualify as qualify
    from pipeline import uk_replay_variants as rv

    document = rv.load_document()
    record = {"variant_id": "a_new_candidate"}
    base = qualify.base_namespace(
        {"compare_to": "latest_certified"}, record, document, root=ROOT
    )
    assert base == rv.namespace_root(rv.get_variant(variant), root=ROOT)
