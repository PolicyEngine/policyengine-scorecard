"""CI's replay-engine matrix comes from the variant index, so no workflow
lists variants (.github/scripts/uk_replay_engine_matrix.py).

Invariants (deterministic cases and Hypothesis properties):

* on any index it accepts, the matrix is exactly the certified ids, in index
  order;
* an index it cannot build the matrix from (an id that is not plain, an
  unknown status, a repeated id, a record that is not an object, no
  certified variant) fails the job, never yields a shorter matrix;
* its plain-id rule is the results pull request's, on any string;
* the job's output is the engine job's matrix, as CI runs the step, and no
  workflow names a variant.
"""

import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import uk_replay_results_pr as builder
from pipeline import uk_replay_variants as rv

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / ".github/scripts/uk_replay_engine_matrix.py"
CI = ROOT / ".github/workflows/ci.yml"
DETERMINISM = ROOT / ".github/workflows/uk-replay-determinism.yml"
INDEX = "data/uk/replay_variants.json"

_spec = importlib.util.spec_from_file_location("uk_replay_engine_matrix", SCRIPT)
matrix = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(matrix)


def certified(document):
    return [v["variant_id"] for v in document["variants"] if v["status"] == "certified"]


def document_of(rows):
    return {
        "schema_version": 1,
        "default_variant": rows[0][0],
        "variants": [
            {**extra, "variant_id": variant_id, "status": status}
            for variant_id, status, extra in rows
        ],
    }


def lister_step():
    return yaml.safe_load(CI.read_text())["jobs"]["replay-variants"]["steps"][-1]


def run_step(directory):
    """The listing step's script as CI runs it: bash, from the checkout,
    with the runner's python3 and a GITHUB_OUTPUT file."""
    tools = directory / "bin"
    tools.mkdir(exist_ok=True)
    if not (tools / "python3").exists():
        (tools / "python3").symlink_to(sys.executable)
    output = directory / "github-output.txt"
    output.write_text("")
    result = subprocess.run(
        ["bash", "-e", "-c", lister_step()["run"]],
        cwd=directory,
        env={
            **{k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
            "PATH": f"{tools}:{os.environ['PATH']}",
            "GITHUB_OUTPUT": str(output),
        },
        capture_output=True,
        text=True,
        check=False,
    )
    return result, output.read_text()


def checkout_copy(tmp_path, index_bytes):
    """What the job's sparse checkout holds: the script and the index."""
    (tmp_path / ".github/scripts").mkdir(parents=True)
    shutil.copyfile(SCRIPT, tmp_path / ".github/scripts" / SCRIPT.name)
    (tmp_path / INDEX).parent.mkdir(parents=True)
    (tmp_path / INDEX).write_bytes(index_bytes)
    return tmp_path


# --- the committed index ---------------------------------------------------------


def test_the_matrix_is_the_committed_certified_variants_in_index_order():
    document = rv.load_document()
    ids = certified(document)
    assert matrix.certified_ids(document) == ids
    # Every one is a record the engine job can select.
    assert [rv.get_variant(variant_id)["variant_id"] for variant_id in ids] == ids
    # As CI runs it, the runner's Python isolated, and without site-packages.
    for flags in (["-I"], ["-I", "-S"]):
        result = subprocess.run(
            [sys.executable, *flags, str(SCRIPT), str(rv.VARIANTS_PATH)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout == json.dumps(ids, separators=(",", ":")) + "\n"


def test_the_listing_step_writes_the_matrix_ci_reads(tmp_path):
    result, output = run_step(checkout_copy(tmp_path, rv.VARIANTS_PATH.read_bytes()))
    assert result.returncode == 0, result.stderr
    lines = output.splitlines()
    assert len(lines) == 1 and lines[0].startswith("variants=")
    assert json.loads(lines[0].removeprefix("variants=")) == certified(
        rv.load_document()
    )


@pytest.mark.parametrize(
    "corrupt",
    [
        lambda d: d["variants"].append({**d["variants"][-1]}),
        lambda d: d["variants"][-1].update(status="certifed"),
        lambda d: d["variants"][-1].update(variant_id="pe9_$(id)"),
        lambda d: d.update(schema_version=2),
    ],
)
def test_a_bad_index_fails_the_step_and_writes_no_matrix(tmp_path, corrupt):
    document = json.loads(rv.VARIANTS_PATH.read_bytes())
    corrupt(document)
    result, output = run_step(checkout_copy(tmp_path, json.dumps(document).encode()))
    assert result.returncode != 0
    assert "::error::" in result.stderr
    assert output == ""


def test_an_unreadable_index_fails(tmp_path):
    checkout_copy(tmp_path, b"{not json")
    for arguments, code in (
        ([str(tmp_path / INDEX)], 1),
        ([str(tmp_path / "missing.json")], 1),
        ([], 2),
        ([str(tmp_path / INDEX), "extra"], 2),
    ):
        result = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == code and result.stdout == "", arguments
    (tmp_path / INDEX).write_bytes(b"\xff\xfe")
    assert matrix.main([str(tmp_path / INDEX)]) == 1


def test_the_lister_needs_only_the_standard_library_and_the_index_statuses():
    imported = set()
    for node in ast.walk(ast.parse(SCRIPT.read_text())):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            assert not node.level
            imported.add(node.module.split(".")[0])
    assert imported <= set(sys.stdlib_module_names) | {"__future__"}
    assert matrix.STATUSES == rv.STATUSES


# --- any index --------------------------------------------------------------------

plain_ids = st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._-]{0,24}", fullmatch=True).filter(
    lambda s: ".." not in s
)
statuses = st.sampled_from(rv.STATUSES)
extras = st.dictionaries(
    st.text(max_size=6),
    st.one_of(st.integers(), st.text(max_size=6), st.none(), st.booleans()),
    max_size=3,
)
rows = st.lists(
    st.tuples(plain_ids, statuses, extras),
    min_size=1,
    max_size=12,
    unique_by=lambda row: row[0],
)


@settings(max_examples=200, deadline=None)
@given(rows)
def test_any_index_gives_exactly_its_certified_ids_in_order(rows):
    document = document_of(rows)
    expected = [variant_id for variant_id, status, _ in rows if status == "certified"]
    if expected:
        assert matrix.certified_ids(document) == expected
    else:
        with pytest.raises(matrix.MatrixError, match="no certified variant"):
            matrix.certified_ids(document)


unplain_ids = st.one_of(
    st.text(max_size=12).filter(lambda s: not builder.plain_variant_id(s)),
    st.sampled_from(["", "-a", ".a", "a..b", "a/b", "a b", "a'b", "a\nb", "a$b"]),
    st.integers(),
    st.none(),
)
corruptions = st.one_of(
    st.tuples(st.just("id"), unplain_ids),
    st.tuples(
        st.just("status"),
        st.one_of(st.text(max_size=10), st.none(), st.integers()).filter(
            lambda s: s not in rv.STATUSES
        ),
    ),
    st.tuples(st.just("repeat"), st.none()),
    st.tuples(
        st.just("record"),
        st.one_of(st.none(), st.text(max_size=4), st.lists(st.integers(), max_size=2)),
    ),
)


@settings(max_examples=200, deadline=None)
@given(rows, corruptions, st.integers(0, 11))
def test_one_bad_record_fails_the_whole_matrix(rows, corruption, position):
    document = document_of([*rows, (f"{rows[0][0]}-c", "certified", {})])
    variants = document["variants"]
    at = position % len(variants)
    kind, value = corruption
    if kind == "id":
        variants[at]["variant_id"] = value
    elif kind == "status":
        variants[at]["status"] = value
    elif kind == "repeat":
        variants.insert(at, dict(variants[(at + 1) % len(variants)]))
    else:
        variants[at] = value
    with pytest.raises(matrix.MatrixError):
        matrix.certified_ids(document)


# Plain ids on both sides of the length cap.
long_ids = st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._-]{110,130}", fullmatch=True)


@settings(max_examples=300, deadline=None)
@given(st.one_of(st.text(max_size=16), plain_ids, long_ids))
def test_the_plain_id_rule_is_the_results_pull_requests(variant_id):
    # Differential: CI's lister and the results pull request's check on a
    # new variant accept exactly the same ids.
    assert matrix.plain(variant_id) == builder.plain_variant_id(variant_id)


def test_ids_stop_at_120_characters_and_the_output_stays_far_under_1_mb():
    # Review of 6866605d (2): the count cap alone let one huge id exceed
    # GitHub's 1 MB job output. Two ids joined by "__" name a release
    # diff's directory, one path component of at most 255 bytes.
    assert matrix.MAX_ID_LENGTH == builder.MAX_VARIANT_ID_LENGTH == 120
    assert 2 * matrix.MAX_ID_LENGTH + len("__") <= 255
    assert matrix.plain("a" * 120) and not matrix.plain("a" * 121)
    longest = [
        f"{i:03d}" + "x" * (matrix.MAX_ID_LENGTH - 3) for i in range(matrix.MAX_JOBS)
    ]
    ids = matrix.certified_ids(document_of([(v, "certified", {}) for v in longest]))
    output = "variants=" + json.dumps(ids, separators=(",", ":"))
    # GitHub sizes outputs as UTF-16.
    assert len(output.encode("utf-16-le")) < 100_000 < 1_000_000
    committed = max(len(v["variant_id"]) for v in rv.load_document()["variants"])
    assert committed <= matrix.MAX_ID_LENGTH


def test_the_document_and_matrix_limits_are_refused():
    for document in (
        None,
        [],
        {"schema_version": 1},
        {"schema_version": 1, "variants": []},
    ):
        with pytest.raises(matrix.MatrixError):
            matrix.certified_ids(document)
    many = document_of([(f"v{i}", "certified", {}) for i in range(matrix.MAX_JOBS + 1)])
    with pytest.raises(matrix.MatrixError, match="256 jobs per matrix"):
        matrix.certified_ids(many)
    many["variants"] = many["variants"][: matrix.MAX_JOBS]
    assert len(matrix.certified_ids(many)) == matrix.MAX_JOBS


# --- the wiring ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("workflow", "job", "name"),
    [
        (CI, "replay-engine", "replay engine · ${{ matrix.variant }}"),
        (DETERMINISM, "real-replay", "real replay · ${{ matrix.variant }}"),
    ],
)
def test_the_engine_matrix_is_the_listing_jobs_output(workflow, job, name):
    # CI's engine checks and the push-only real replay each list the
    # certified variants the same way, from the index alone.
    jobs = yaml.safe_load(workflow.read_text())["jobs"]
    lister = jobs["replay-variants"]
    assert lister["permissions"] == {"contents": "read"}
    assert lister["outputs"] == {"variants": "${{ steps.list.outputs.variants }}"}
    assert "secrets." not in json.dumps(lister) and "needs" not in lister
    checkout, step = lister["steps"]
    # The script and the index only, with no persisted credential; no uv,
    # no setup-python, nothing installed: the runner's own python3.
    assert checkout == {
        "uses": "actions/checkout@v4",
        "with": {
            "persist-credentials": False,
            "sparse-checkout": f".github/scripts/{SCRIPT.name}\n{INDEX}\n",
            "sparse-checkout-cone-mode": False,
        },
    }
    assert step["id"] == "list" and set(step) == {"name", "id", "run"}
    assert step["run"].startswith("set -euo pipefail\n")
    assert f"$(python3 -I .github/scripts/{SCRIPT.name} {INDEX})" in step["run"]
    assert "${{" not in step["run"]
    engine = jobs[job]
    assert engine["needs"] == "replay-variants"
    assert engine["name"] == name
    assert engine["strategy"] == {
        "fail-fast": False,
        "matrix": {
            "variant": "${{ fromJSON(needs.replay-variants.outputs.variants) }}"
        },
    }
    assert engine["env"]["VARIANT"] == "${{ matrix.variant }}"


def test_no_workflow_names_a_variant():
    # The index is the only list: a workflow that named a variant would be a
    # second one, for a results pull request to edit.
    ids = [v["variant_id"] for v in rv.load_document()["variants"]]
    for workflow in sorted((ROOT / ".github/workflows").glob("*.y*ml")):
        text = workflow.read_text()
        assert not [variant_id for variant_id in ids if variant_id in text], workflow
