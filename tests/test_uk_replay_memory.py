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


def request_for(sha256: str) -> dict:
    request = golden_request()
    request["candidate"]["data"]["sha256"] = sha256
    return request


def evidence_root(tmp_path, datasets: dict) -> Path:
    path = tmp_path / qualify.MEMORY_EVIDENCE
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"datasets": datasets}))
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


def test_two_workers_when_the_measured_peak_fits(tmp_path):
    root = evidence_root(tmp_path, {"a" * 64: {"two_worker_peak_rss_bytes": 9 * GIB}})
    workers, reason = qualify.simulation_workers(
        request_for("a" * 64), root=root, memory_total=16 * GIB
    )
    assert workers == 2
    assert reason == (
        "measured two-worker peak 9.0 GiB plus 2.0 GiB reserve fits in this "
        "runner's 16.0 GiB"
    )


def test_one_worker_when_the_measured_peak_does_not_fit(tmp_path):
    root = evidence_root(
        tmp_path, {"a" * 64: {"two_worker_peak_rss_bytes": int(14.5 * GIB)}}
    )
    workers, reason = qualify.simulation_workers(
        request_for("a" * 64), root=root, memory_total=16 * GIB
    )
    assert (workers, reason) == (
        1,
        "measured two-worker peak 14.5 GiB plus 2.0 GiB reserve exceeds this "
        "runner's 16.0 GiB",
    )


@pytest.mark.parametrize(
    "datasets, memory_total, reason",
    [
        ({}, 16 * GIB, "no measured two-worker peak for dataset aaaaaaaaaaaa"),
        (
            {"a" * 64: {"two_worker_peak_rss_bytes": None}},
            16 * GIB,
            "no measured two-worker peak for dataset aaaaaaaaaaaa",
        ),
        (
            {"a" * 64: {"two_worker_peak_rss_bytes": 1.5e9}},
            16 * GIB,
            "no measured two-worker peak for dataset aaaaaaaaaaaa",
        ),
        (
            {"a" * 64: {"two_worker_peak_rss_bytes": GIB}},
            None,
            "this runner's memory is unknown",
        ),
    ],
)
def test_one_worker_without_a_measured_fit(tmp_path, datasets, memory_total, reason):
    root = evidence_root(tmp_path, datasets)
    assert qualify.simulation_workers(
        request_for("a" * 64), root=root, memory_total=memory_total
    ) == (1, reason)


@pytest.mark.parametrize("content", [None, "not json", "[]", '{"datasets": []}'])
def test_unreadable_evidence_means_one_worker(tmp_path, content):
    if content is not None:
        path = tmp_path / qualify.MEMORY_EVIDENCE
        path.parent.mkdir(parents=True)
        path.write_text(content)
    workers, reason = qualify.simulation_workers(
        request_for("a" * 64), root=tmp_path, memory_total=64 * GIB
    )
    assert workers == 1 and reason.startswith("memory evidence unreadable")


@settings(max_examples=300, deadline=None)
@given(
    peak=st.integers(min_value=0, max_value=64 * GIB),
    total=st.integers(min_value=0, max_value=64 * GIB),
    more=st.integers(min_value=0, max_value=8 * GIB),
)
def test_the_choice_is_the_fit_and_monotone(tmp_path_factory, peak, total, more):
    """Two workers exactly when peak + reserve <= memory; more memory never
    means fewer workers, and a higher peak never means more."""
    root = evidence_root(
        tmp_path_factory.mktemp("evidence"),
        {"a" * 64: {"two_worker_peak_rss_bytes": peak}},
    )

    def choose(peak_root, memory):
        return qualify.simulation_workers(
            request_for("a" * 64), root=peak_root, memory_total=memory
        )[0]

    assert choose(root, total) == (
        2 if peak + qualify.MEMORY_RESERVE_BYTES <= total else 1
    )
    assert choose(root, total + more) >= choose(root, total)
    higher = evidence_root(
        tmp_path_factory.mktemp("evidence"),
        {"a" * 64: {"two_worker_peak_rss_bytes": peak + more}},
    )
    assert choose(higher, total) <= choose(root, total)


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
    """The two datasets the replay has run, on a 16 GB hosted runner (its
    MemTotal is a little under 16 GiB)."""
    evidence = committed_evidence()["datasets"]
    by_name = {entry["dataset"]: sha for sha, entry in evidence.items()}
    runner = 15 * GIB + 600 * 2**20
    microcosm = qualify.simulation_workers(
        request_for(by_name["microcosm_uk_2024_25"]), memory_total=runner
    )
    efrs = qualify.simulation_workers(
        request_for(by_name["enhanced_frs_2024_25"]), memory_total=runner
    )
    assert microcosm[0] == 1, microcosm
    assert efrs[0] == 2, efrs


# --- summarizing measurements ---------------------------------------------------------


def measurement(label, sha, workers, peak, *, exit_code=0):
    return {
        "label": label,
        "dataset": {
            "dataset": "d",
            "build_id": "b",
            "sha256": sha,
            "size_bytes": 1,
        },
        "workers": workers,
        "compute": {"exit_code": exit_code, "tree_peak_rss_bytes": peak},
    }


def test_summarize_takes_the_largest_completed_peak_per_worker_count():
    summary = measure.summarize(
        [
            measurement("b", "x", 1, 5),
            measurement("a", "x", 2, 9),
            measurement("c", "x", 2, 12),
            measurement("d", "x", 2, 99, exit_code=1),
            measurement("e", "y", 1, 3),
        ]
    )
    assert summary["datasets"]["x"]["one_worker_peak_rss_bytes"] == 5
    assert summary["datasets"]["x"]["two_worker_peak_rss_bytes"] == 12
    assert summary["datasets"]["x"]["measurements"] == ["a", "b", "c", "d"]
    # Only a one-worker run: no two-worker peak, so the qualifier runs one.
    assert summary["datasets"]["y"]["two_worker_peak_rss_bytes"] is None
    assert [m["label"] for m in summary["measurements"]] == ["a", "b", "c", "d", "e"]


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
"""


def test_measured_run_samples_the_tree_and_keeps_only_aggregate_lines(tmp_path):
    script = tmp_path / "fake_compute.py"
    script.write_text(FAKE_COMPUTE)
    result = measure.measured_run(
        [sys.executable, str(script)], cwd=str(tmp_path), env={"PATH": ""}
    )
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
