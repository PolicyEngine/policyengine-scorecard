"""The qualifier's simulation worker count and its memory logging.

Engine-free. The worker count comes from measured evidence: two year workers
only where a dataset's measured two-worker peak, plus the reserve, fits in
the runner's memory. The evidence file is regenerated from its own
measurements here, so the committed per-dataset peaks are derived, not typed.
"""

import json
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import modal_uk_replay_memory as measure
from pipeline import uk_replay_qualify as qualify

FIXTURES = Path(__file__).parent / "fixtures" / "uk_replay"
GIB = 2**30
EVIDENCE = qualify.ROOT / qualify.MEMORY_EVIDENCE


def golden_request():
    return json.loads((FIXTURES / "qualification_request_golden.json").read_text())


def request_for(sha256: str, packages: dict | None = None) -> dict:
    request = golden_request()
    request["candidate"]["data"]["sha256"] = sha256
    if packages:
        candidate = request["candidate"]
        candidate["policyengine"]["version"] = packages["policyengine"]
        candidate["policyengine_uk"]["version"] = packages["policyengine-uk"]
        candidate["policyengine_core"]["version"] = packages["policyengine-core"]
    return request


def workload(request=None, **changes) -> dict:
    """The scheduling workload a request needs measured."""
    return {
        "packages": qualify.requested_versions(request or golden_request()),
        "corpus_version": qualify.CORPUS_VERSION,
        "event": measure.SCHEDULING_EVENT,
        **changes,
    }


def evidence_root(tmp_path, peaks, *, sha="a" * 64, schema_version=1, **changes):
    """Evidence holding two-worker peaks for one dataset and workload."""
    path = tmp_path / qualify.MEMORY_EVIDENCE
    path.parent.mkdir(parents=True)
    rows = [{"workload": workload(**changes), "peak_rss_bytes": p} for p in peaks]
    path.write_text(
        json.dumps(
            {
                "schema_version": schema_version,
                "datasets": {sha: {"two_worker_peaks": rows}},
            }
        )
    )
    return tmp_path


# --- reading the machine ----------------------------------------------------------


def test_meminfo_parsing(tmp_path):
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(
        "MemTotal:       16374960 kB\nMemFree:  1 kB\nMemAvailable:   15012345 kB\n"
    )
    assert qualify.memory_total_bytes(meminfo) == 16374960 * 1024
    assert qualify.memory_available_bytes(meminfo) == 15012345 * 1024
    assert qualify.memory_total_bytes(tmp_path / "absent") is None
    assert qualify.memory_available_bytes(tmp_path / "absent") is None
    meminfo.write_text("MemTotal: not-a-number kB\n")
    assert qualify.memory_total_bytes(meminfo) is None


def fake_proc(tmp_path, processes: dict[int, tuple[int, int | None]]) -> Path:
    """processes: pid -> (ppid, VmRSS in kB or None for a kernel thread)."""
    proc = tmp_path / "proc"
    for pid, (ppid, rss) in processes.items():
        (proc / str(pid)).mkdir(parents=True)
        lines = [f"Name:\tp{pid}", f"PPid:\t{ppid}"]
        if rss is not None:
            lines.append(f"VmRSS:\t{rss} kB")
        (proc / str(pid) / "status").write_text("\n".join(lines) + "\n")
    (proc / "self").mkdir()
    (proc / "meminfo").write_text("MemTotal: 1 kB\n")
    return proc


def test_process_tree_rss_sums_the_root_and_every_descendant_only(tmp_path):
    proc = fake_proc(
        tmp_path,
        {
            1: (0, 10),
            100: (1, 1000),  # the corpus runner
            101: (100, 2000),  # compute_uk_event
            102: (101, 3000),  # a year worker
            103: (101, 4000),  # another
            104: (102, None),  # no VmRSS: counts nothing
            200: (1, 9_999_999),  # unrelated
        },
    )
    assert qualify.process_tree_rss(100, proc) == (1000 + 2000 + 3000 + 4000) * 1024
    assert qualify.process_tree_rss(102, proc) == 3000 * 1024
    assert qualify.process_tree_rss(999, proc) == 0
    assert qualify.process_tree_rss(100, tmp_path / "no-proc") is None


@settings(max_examples=100, deadline=None)
@given(
    st.lists(st.integers(min_value=0, max_value=10**6), min_size=1, max_size=12),
    st.data(),
)
def test_process_tree_rss_is_the_sum_over_the_subtree(tmp_path_factory, sizes, data):
    """For any tree, the root's total is its own RSS plus each child's total."""
    tmp_path = tmp_path_factory.mktemp("proc")
    parents = {
        10 + i: (data.draw(st.integers(10, 9 + i)) if i else 1)
        for i in range(len(sizes))
    }
    proc = fake_proc(
        tmp_path, {pid: (parents[pid], sizes[pid - 10]) for pid in parents}
    )
    for pid in parents:
        children = [child for child, parent in parents.items() if parent == pid]
        assert qualify.process_tree_rss(pid, proc) == sizes[pid - 10] * 1024 + sum(
            qualify.process_tree_rss(child, proc) for child in children
        )


# --- choosing the worker count ----------------------------------------------------


def choose(root, memory_total=16 * GIB, request=None):
    return qualify.simulation_workers(
        request or request_for("a" * 64), root=root, memory_total=memory_total
    )


def test_two_workers_when_the_measured_peak_fits(tmp_path):
    assert choose(evidence_root(tmp_path, [9 * GIB])) == (
        2,
        "measured two-worker peak 9.0 GiB plus 2.0 GiB reserve fits in this "
        "runner's 16.0 GiB",
    )


def test_one_worker_when_the_measured_peak_does_not_fit(tmp_path):
    assert choose(evidence_root(tmp_path, [int(14.5 * GIB)])) == (
        1,
        "measured two-worker peak 14.5 GiB plus 2.0 GiB reserve exceeds this "
        "runner's 16.0 GiB",
    )


def test_the_largest_matching_peak_decides(tmp_path):
    assert choose(evidence_root(tmp_path, [9 * GIB, 15 * GIB]))[0] == 1


UNMEASURED = (
    "no measured two-worker peak for dataset aaaaaaaaaaaa with these engine "
    "versions and corpus"
)


@pytest.mark.parametrize(
    "changes",
    [
        {"sha": "b" * 64},
        {"corpus_version": "uk-fiscal-event-replay/1"},
        {
            "packages": {
                "policyengine": "0.0.1",
                "policyengine-uk": "0.0.1",
                "policyengine-core": "0.0.1",
            }
        },
    ],
)
def test_another_dataset_engine_or_corpus_is_unmeasured(tmp_path, changes):
    assert choose(evidence_root(tmp_path, [GIB], **changes)) == (1, UNMEASURED)


@pytest.mark.parametrize("peak", [0, -1, 1.5e9, "9", None, True])
def test_a_peak_that_is_not_a_positive_integer_means_one_worker(tmp_path, peak):
    assert choose(evidence_root(tmp_path, [9 * GIB, peak])) == (
        1,
        "the memory evidence holds an invalid two-worker peak",
    )


def test_unknown_memory_means_one_worker(tmp_path):
    assert choose(evidence_root(tmp_path, [GIB]), memory_total=None) == (
        1,
        "this runner's memory is unknown",
    )


@pytest.mark.parametrize(
    "content",
    [
        None,
        "not json",
        "[]",
        '{"datasets": {}}',
        '{"schema_version": 1, "datasets": []}',
        '{"schema_version": 1, "datasets": {"%s": {"two_worker_peaks": [{}]}}}'
        % ("a" * 64),
    ],
)
def test_unreadable_evidence_means_one_worker(tmp_path, content):
    if content is not None:
        path = tmp_path / qualify.MEMORY_EVIDENCE
        path.parent.mkdir(parents=True)
        path.write_text(content)
    workers, reason = choose(tmp_path, memory_total=64 * GIB)
    assert workers == 1 and reason.startswith("memory evidence unreadable")


def test_an_unknown_evidence_format_means_one_worker(tmp_path):
    workers, reason = choose(evidence_root(tmp_path, [GIB], schema_version=2))
    assert workers == 1 and reason == "memory evidence unreadable (ValueError)"


@settings(max_examples=300, deadline=None)
@given(
    peak=st.integers(min_value=1, max_value=64 * GIB),
    total=st.integers(min_value=0, max_value=64 * GIB),
    more=st.integers(min_value=0, max_value=8 * GIB),
)
def test_the_choice_is_the_fit_and_monotone(tmp_path_factory, peak, total, more):
    """Two workers exactly when peak + reserve <= memory; more memory never
    means fewer workers, and a higher peak never means more."""
    root = evidence_root(tmp_path_factory.mktemp("evidence"), [peak])
    assert choose(root, total)[0] == (
        2 if peak + qualify.MEMORY_RESERVE_BYTES <= total else 1
    )
    assert choose(root, total + more)[0] >= choose(root, total)[0]
    higher = evidence_root(tmp_path_factory.mktemp("evidence"), [peak + more])
    assert choose(higher, total)[0] <= choose(root, total)[0]


# --- the committed evidence ---------------------------------------------------------


def committed_evidence() -> dict:
    return json.loads(EVIDENCE.read_bytes())


def test_the_committed_evidence_is_its_own_measurements_summarized():
    evidence = committed_evidence()
    assert evidence == measure.summarize(evidence["measurements"])
    assert EVIDENCE.read_bytes() == measure.canonical_bytes(evidence)


def test_every_committed_measurement_is_aggregates_only():
    """Memory, timings and the runner's own aggregate lines; no table."""
    for measurement in committed_evidence()["measurements"]:
        compute = measurement["compute"]
        assert set(compute) == {
            "exit_code",
            "wall_seconds",
            "tree_peak_rss_bytes",
            "min_available_bytes",
            "peak_rss_bytes_by_role",
            "process_count_by_role",
            "phases",
            "log",
        }
        for line in compute["log"]:
            assert measure.MEASURE_LINE.match(line) or "extracted once in" in line


def test_microcosm_runs_one_worker_and_the_enhanced_frs_two_on_the_runner():
    """The two datasets the replay has run, each with the engine versions
    measured on it, on a 16 GB hosted runner (MemTotal a little under 16 GiB)."""
    runner = 15 * GIB + 600 * 2**20
    chosen = {}
    for sha, entry in committed_evidence()["datasets"].items():
        (row,) = entry["two_worker_peaks"]
        chosen[entry["dataset"]] = qualify.simulation_workers(
            request_for(sha, row["workload"]["packages"]), memory_total=runner
        )
    assert chosen["microcosm_uk_2024_25"][0] == 1, chosen
    assert chosen["enhanced_frs_2024_25"][0] == 2, chosen


def test_slices_and_one_worker_runs_never_schedule_two_workers():
    for entry in committed_evidence()["datasets"].values():
        for row in entry["two_worker_peaks"]:
            for label in row["measurements"]:
                (run,) = [
                    m
                    for m in committed_evidence()["measurements"]
                    if m["label"] == label
                ]
                assert run["workers"] == 2 and not run["years"] and not run["measures"]
                assert run["event"] == measure.SCHEDULING_EVENT


# --- summarizing measurements ---------------------------------------------------------


def measurement(label, sha, workers, peak, *, exit_code=0, **changes):
    return {
        "label": label,
        "dataset": {"dataset": "d", "build_id": "b", "sha256": sha, "size_bytes": 1},
        "workers": workers,
        "event": measure.SCHEDULING_EVENT,
        "years": [],
        "measures": [],
        "packages": workload()["packages"],
        "corpus_version": qualify.CORPUS_VERSION,
        "compute": {"exit_code": exit_code, "tree_peak_rss_bytes": peak},
        **changes,
    }


def test_summarize_keeps_only_completed_whole_event_runs_for_scheduling():
    other = {"policyengine": "9", "policyengine-uk": "9", "policyengine-core": "9"}
    summary = measure.summarize(
        [
            measurement("b", "x", 1, 5),
            measurement("a", "x", 2, 9),
            measurement("c", "x", 2, 12),
            measurement("d", "x", 2, 99, exit_code=1),
            measurement("f", "x", 2, 7, years=[2029]),
            measurement("g", "x", 2, 7, measures=["m"]),
            measurement("h", "x", 2, 50, event="autumn_budget_2024"),
            measurement("i", "x", 2, 4, packages=other),
            measurement("e", "y", 1, 3),
        ]
    )
    x = summary["datasets"]["x"]
    assert x["one_worker_peak_rss_bytes"] == 5
    assert x["two_worker_peaks"] == [
        {"workload": workload(), "peak_rss_bytes": 12, "measurements": ["a", "c"]},
        {
            "workload": workload(packages=other),
            "peak_rss_bytes": 4,
            "measurements": ["i"],
        },
    ]
    assert x["measurements"] == ["a", "b", "c", "d", "f", "g", "h", "i"]
    # Only a one-worker run: no two-worker peak, so the qualifier runs one.
    assert summary["datasets"]["y"]["two_worker_peaks"] == []
    labels = [m["label"] for m in summary["measurements"]]
    assert labels == sorted(labels)


@settings(max_examples=200, deadline=None)
@given(
    st.lists(
        st.tuples(
            st.sampled_from([1, 2]),
            st.integers(min_value=1, max_value=64 * GIB),
            st.sampled_from([0, 1]),
            st.booleans(),
        ),
        max_size=8,
    )
)
def test_a_scheduling_peak_is_the_largest_completed_whole_event_two_worker_run(runs):
    measurements = [
        measurement(
            f"m{i}",
            "x",
            workers,
            peak,
            exit_code=code,
            **({"years": [2029]} if sliced else {}),
        )
        for i, (workers, peak, code, sliced) in enumerate(runs)
    ]
    rows = (
        measure.summarize(measurements)["datasets"]
        .get("x", {})
        .get("two_worker_peaks", [])
    )
    eligible = [
        peak
        for workers, peak, code, sliced in runs
        if workers == 2 and not code and not sliced
    ]
    assert [row["peak_rss_bytes"] for row in rows] == (
        [max(eligible)] if eligible else []
    )


# --- the measurement's own sampling ---------------------------------------------------

FAKE_COMPUTE = r"""
import multiprocessing, os, sys, time

def year(y):
    print(f"[pid {os.getpid()} year {y}] starting certified baseline (7 heads)", flush=True)
    block = bytearray(40 * 2**20)
    time.sleep(0.6)
    print(f"[pid {os.getpid()} year {y}] certified baseline extracted once in 0.6s", flush=True)
    print(f"[pid {os.getpid()} year {y}] starting m baseline modifier (reversal_on_certified_world)", flush=True)
    time.sleep(0.6)
    print(f"[{y}] m: +0.000bn gain to Exchequer", flush=True)
    del block

if __name__ == "__main__":
    print(f"[pid {os.getpid()}] starting offline bundle preflight", flush=True)
    with multiprocessing.get_context("spawn").Pool(2) as pool:
        pool.map(year, [2029, 2030])
    print("private row 1,2,3", flush=True)
    print("private traceback 4,5,6", file=sys.stderr, flush=True)
"""


def test_measured_run_samples_the_tree_and_keeps_only_aggregate_lines(tmp_path, capfd):
    script = tmp_path / "fake_compute.py"
    script.write_text(FAKE_COMPUTE)
    result = measure.measured_run(
        [sys.executable, str(script)], cwd=str(tmp_path), env={"PATH": ""}
    )
    # Modal streams what the container prints: only the runner's own lines.
    printed = capfd.readouterr()
    assert "private row" not in printed.out + printed.err
    assert "private traceback" not in printed.out + printed.err
    assert "[2029] m: +0.000bn gain to Exchequer" in printed.out
    assert result["exit_code"] == 0
    assert result["tree_peak_rss_bytes"] >= 2 * 40 * 2**20
    assert result["process_count_by_role"]["year_worker"] == 2
    assert result["peak_rss_bytes_by_role"]["year_worker"] >= 40 * 2**20
    worlds = sorted((p["year"], p["phase"]) for p in result["phases"] if p["year"])
    assert worlds == [
        (2029, "certified baseline"),
        (2029, "m baseline modifier"),
        (2030, "certified baseline"),
        (2030, "m baseline modifier"),
    ]
    assert all(
        p["process_peak_rss_bytes"] >= 40 * 2**20
        for p in result["phases"]
        if p["phase"] == "certified baseline"
    )
    # A phase starts from its boundary sample, so it never reports more than
    # the tree held during it.
    assert all(
        p["process_peak_rss_bytes"] <= p["tree_peak_rss_bytes"]
        for p in result["phases"]
    )
    assert "private row 1,2,3" not in result["log"]
    assert sorted(result["log"]) == sorted(
        [
            line
            for y in (2029, 2030)
            for line in (f"[{y}] m: +0.000bn gain to Exchequer",)
        ]
        + [
            line
            for line in result["log"]
            if "certified baseline extracted once in 0.6s" in line
        ]
    )


def test_the_plan_names_the_request_and_dataset_without_a_cloud_call(tmp_path, capsys):
    dataset = tmp_path / "dataset.h5"
    dataset.write_bytes(b"dataset fixture")
    request = golden_request()
    request["candidate"]["data"]["sha256"] = qualify.variants.sha256_file(dataset)
    request["candidate"]["data"]["size_bytes"] = dataset.stat().st_size
    path = tmp_path / "REQUEST.json"
    path.write_text(json.dumps(request))
    args = [
        "--request",
        str(path),
        "--dataset-file",
        str(dataset),
        "--event",
        "autumn_budget_2025",
        "--years",
        "2030",
        "2029",
        "--workers",
        "2",
        "--label",
        "plan",
        "--output",
        str(tmp_path / "out.json"),
    ]
    assert measure.main(args) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["cloud_call"] is False and plan["years"] == [2029, 2030]
    assert plan["workers"] == 2 and not (tmp_path / "out.json").exists()
    dataset.write_bytes(b"other bytes")
    with pytest.raises(ValueError, match="differs from the request"):
        measure.main(args)
