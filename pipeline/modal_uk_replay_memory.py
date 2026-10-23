"""Measure the UK replay qualifier's memory on Modal; aggregates only.

The release replay qualifies each policyengine.py release on a GitHub-hosted
runner (uk-replay.yml), whose memory is fixed. This measures what a slice of
that qualification needs. The image builds the candidate environment with
the qualifier's own ``prepare``; the remote function runs its ``probe`` and
then ``compute_uk_event`` for one event's years and measures with a given
worker count, exactly as ``run_corpus`` calls it, and samples the resident
memory of the whole process tree (the event runner and its spawned year
workers) every 0.2 s. Only memory, timings and the runner's own aggregate
log lines come back; the dataset and anything household-level stay in the
container, whose network is blocked while it runs.

Plan first (no provider call)::

    .venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_replay_memory \\
        --request REQUEST.json --dataset-file microcosm_uk_2024_25.h5 \\
        --event autumn_budget_2025 --years 2029 \\
        --measures ab2025__personal_tax_thresholds_freeze_to_2031 --workers 1 \\
        --output .venv-replay-checks/memory/microcosm-w1.json

Add ``--execute`` to run it. Each run holds one shared simulation slot per
worker (pipeline/modal_uk_event.py, ``SimulationSlots``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REMOTE_ROOT = "/scorecard"
REMOTE_WORK = "/work"
UV_VERSION = "0.13.4"
CONTROL_PINS = ("psutil==7.0.0", "rfc8785==0.1.4", "jsonschema==4.23.0")
# A GitHub-hosted ubuntu-latest runner for a public repository has 4 CPUs
# and 16 GB of memory. The container gets the same CPUs and twice the memory,
# so a slice that would not fit on the runner still runs and is measured.
CPU = 4
MEMORY_MIB = 32768
TIMEOUT_SECONDS = 3 * 60 * 60
GUARD_MARGIN_SECONDS = 10 * 60
SAMPLE_SECONDS = 0.2
SLOT_POLL_SECONDS = 3
# The qualifier runs in a checkout of the whole repository; the web app is
# the one part the pipeline never reads.
SNAPSHOT_EXCLUDED = ("app/",)
# compute_uk_event's own progress and aggregate lines, exactly; nothing
# else it or the engine prints is kept or printed.
SLUG = r"[a-z0-9]+(?:_+[a-z0-9]+)*"
RUNNER_LINE = re.compile(
    r"^\[pid (\d+)\] (starting offline bundle preflight"
    r"|offline bundle preflight complete; starting processed-world reversal guard"
    r"|processed-world reversal guard complete"
    r"|stopping owned year workers after interruption or job failure)$"
)
BASELINE_START = re.compile(
    r"^\[pid (\d+) year (\d{4})\] starting certified baseline \(\d+ heads\)$"
)
BASELINE_DONE = re.compile(
    r"^\[pid (\d+) year (\d{4})\] certified baseline extracted once in \d+\.\ds$"
)
WORLD_START = re.compile(
    rf"^\[pid (\d+) year (\d{{4}})\] starting ({SLUG}) "
    rf"(baseline modifier|reform delta) \(({SLUG})\)$"
)
MEASURE_LINE = re.compile(
    rf"^\[(\d{{4}})\] ({SLUG}): [+-]\d+\.\d{{3}}bn gain to Exchequer$"
)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selection(args: argparse.Namespace, request: dict) -> dict:
    data = request["candidate"]["data"]
    if args.workers not in (1, 2):
        raise ValueError("the qualifier runs one or two year workers")
    return {
        "event": args.event,
        "years": sorted(args.years),
        "measures": list(args.measures),
        "workers": args.workers,
        "dataset": {
            key: data[key] for key in ("dataset", "build_id", "sha256", "size_bytes")
        },
        "packages": {
            "policyengine": request["candidate"]["policyengine"]["version"],
            "policyengine-uk": request["candidate"]["policyengine_uk"]["version"],
            "policyengine-core": request["candidate"]["policyengine_core"]["version"],
        },
    }


def snapshot(destination: Path, *, root: Path = ROOT) -> Path:
    """Copy the tracked files the remote side needs, as committed or edited."""
    listed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True
    ).stdout.split(b"\0")
    for name in filter(None, (item.decode() for item in listed)):
        if name.startswith(SNAPSHOT_EXCLUDED) or not (root / name).is_file():
            continue
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, target)
    return destination


# --- remote: runs in the container ---------------------------------------------------


def process_role(process) -> str:
    try:
        command = " ".join(process.cmdline())
    except Exception:  # noqa: BLE001 - a process may end between listing and reading
        return "ended"
    if "resource_tracker" in command:
        return "multiprocessing_helper"
    if "multiprocessing.spawn" in command or "spawn_main" in command:
        return "year_worker"
    return "child"


class TreeSampler:
    """Peak resident memory of a process and every descendant.

    The total sums each process's RSS, so pages two processes share (the
    shared libraries both map) count twice: an upper bound on what the tree
    holds, and the measure the kernel's OOM accounting comes closest to.
    Phases follow the runner's own progress lines, one per process.
    """

    def __init__(self, pid: int, interval: float = SAMPLE_SECONDS):
        import threading

        import psutil

        self.root = psutil.Process(pid)
        self.interval = interval
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.peak_total = 0
        self.peak_by_pid: dict[int, int] = {}
        # The latest sample, so a phase starts from the process's memory at
        # its boundary rather than from the peak of everything before it.
        self.current_by_pid: dict[int, int] = {}
        self.current_total = 0
        self.role_by_pid: dict[int, str] = {pid: "event_runner"}
        self.min_available = psutil.virtual_memory().available
        self.phase_peak: dict[int, int] = {}
        self.phase_total: dict[int, int] = {}
        self.thread = threading.Thread(target=self._run, daemon=True)

    def sample(self) -> None:
        import psutil

        rss = {}
        try:
            processes = [self.root, *self.root.children(recursive=True)]
        except psutil.Error:
            return
        for process in processes:
            try:
                rss[process.pid] = process.memory_info().rss
            except psutil.Error:
                continue
            if process.pid not in self.role_by_pid:
                self.role_by_pid[process.pid] = process_role(process)
        total = sum(rss.values())
        available = psutil.virtual_memory().available
        with self.lock:
            self.current_by_pid, self.current_total = rss, total
            self.peak_total = max(self.peak_total, total)
            self.min_available = min(self.min_available, available)
            for pid, value in rss.items():
                self.peak_by_pid[pid] = max(self.peak_by_pid.get(pid, 0), value)
                if pid in self.phase_peak:
                    self.phase_peak[pid] = max(self.phase_peak[pid], value)
            for pid in self.phase_total:
                self.phase_total[pid] = max(self.phase_total[pid], total)

    def _run(self) -> None:
        while not self.stop.wait(self.interval):
            self.sample()

    def __enter__(self) -> "TreeSampler":
        self.sample()
        self.thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop.set()
        self.thread.join(timeout=5)

    def begin(self, pid: int) -> tuple[int, int]:
        """Start a phase for pid; returns the closing phase's (own, tree) peaks."""
        with self.lock:
            closed = (self.phase_peak.get(pid, 0), self.phase_total.get(pid, 0))
            self.phase_peak[pid] = self.current_by_pid.get(pid, 0)
            self.phase_total[pid] = self.current_total
        return closed

    def end(self, pid: int) -> tuple[int, int]:
        with self.lock:
            closed = (self.phase_peak.pop(pid, 0), self.phase_total.pop(pid, 0))
        return closed


def measured_run(command: list[str], *, cwd: str, env: dict) -> dict:
    """Run a command and sample its process tree.

    Only the runner's own progress and aggregate lines are printed (Modal
    streams the container's output to the caller) or kept; any other line,
    a warning or a traceback included, stays in the container."""
    started = time.perf_counter()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    phases, open_phases, year_pid, log = [], {}, {}, []
    with TreeSampler(process.pid) as sampler:

        def close(pid: int, *, ending: bool) -> None:
            peak, tree = sampler.end(pid) if ending else sampler.begin(pid)
            if pid in open_phases:
                phase = open_phases.pop(pid)
                phases.append(
                    {
                        **phase,
                        "seconds": round(time.perf_counter() - phase.pop("_t"), 1),
                        "process_peak_rss_bytes": peak,
                        "tree_peak_rss_bytes": tree,
                    }
                )

        def begin(pid: int, year: int | None, phase: str) -> None:
            close(pid, ending=False)
            open_phases[pid] = {
                "process": sampler.role_by_pid.get(pid, "year_worker"),
                "year": year,
                "phase": phase,
                "_t": time.perf_counter(),
            }
            if year is not None:
                year_pid[year] = pid

        for line in process.stdout:
            line = line.rstrip("\n")
            sampler.sample()
            matched = {
                name: pattern.match(line)
                for name, pattern in (
                    ("runner", RUNNER_LINE),
                    ("baseline", BASELINE_START),
                    ("extracted", BASELINE_DONE),
                    ("world", WORLD_START),
                    ("measure", MEASURE_LINE),
                )
            }
            if not any(matched.values()):
                continue
            print(line, flush=True)
            if runner := matched["runner"]:
                if runner[2].startswith("starting ") or "; starting " in runner[2]:
                    begin(int(runner[1]), None, runner[2].rsplit("starting ", 1)[1])
            elif baseline := matched["baseline"]:
                begin(int(baseline[1]), int(baseline[2]), "certified baseline")
            elif world := matched["world"]:
                begin(int(world[1]), int(world[2]), f"{world[3]} {world[4]}")
            elif extracted := matched["extracted"]:
                if int(extracted[1]) in open_phases:
                    close(int(extracted[1]), ending=True)
                log.append(line)
            elif measure := matched["measure"]:
                pid = year_pid.get(int(measure[1]))
                if pid is not None:
                    close(pid, ending=True)
                log.append(line)
        returncode = process.wait()
        for pid in list(open_phases):
            close(pid, ending=True)
        sampler.sample()
    roles: dict[str, int] = {}
    for pid, peak in sampler.peak_by_pid.items():
        role = sampler.role_by_pid.get(pid, "child")
        roles[role] = max(roles.get(role, 0), peak)
    return {
        "exit_code": returncode,
        "wall_seconds": round(time.perf_counter() - started, 1),
        "tree_peak_rss_bytes": sampler.peak_total,
        "min_available_bytes": sampler.min_available,
        "peak_rss_bytes_by_role": roles,
        "process_count_by_role": {
            role: sum(1 for value in sampler.role_by_pid.values() if value == role)
            for role in sorted(set(sampler.role_by_pid.values()))
        },
        "phases": phases,
        "log": log,
    }


def remote_measure(spec: dict, lease_expires: float) -> dict:
    """In the container: probe the candidate, then measure the slice."""
    import psutil

    if time.time() + TIMEOUT_SECONDS + GUARD_MARGIN_SECONDS > lease_expires:
        return {"refused": "the simulation slot lease does not cover the timeout"}
    work = Path(REMOTE_WORK)
    request = json.loads((work / "REQUEST.json").read_bytes())
    dataset = Path("/inputs/dataset.h5")
    data = request["candidate"]["data"]
    if (
        dataset.stat().st_size != data["size_bytes"]
        or sha256_file(dataset) != data["sha256"]
    ):
        raise ValueError("the uploaded dataset differs from the request")
    python = str(work / "venv" / "bin" / "python")
    env = {
        "PATH": os.environ["PATH"],
        "HOME": os.environ.get("HOME", "/root"),
        "LANG": "C.UTF-8",
        "PYTHONPATH": REMOTE_ROOT,
    }
    probe = measured_run(
        [
            python,
            "-m",
            "pipeline.uk_replay_qualify",
            "probe",
            "--request",
            str(work / "REQUEST.json"),
            "--runtime-root",
            str(work / "runtime"),
            "--dataset-file",
            str(dataset),
            "--wheel-digests",
            str(work / "wheel-digests.json"),
            "--variants-file",
            str(work / "variants.json"),
            "--rejection-file",
            str(work / "rejection.json"),
        ],
        cwd=REMOTE_ROOT,
        env=env,
    )
    if probe["exit_code"]:
        return {"failed": "probe", "probe": probe}
    variants = json.loads((work / "variants.json").read_bytes())
    variant_id = variants["variants"][-1]["variant_id"]
    output = Path(REMOTE_ROOT) / ".venv-replay-checks" / "memory" / spec["event"]
    command = [
        python,
        "-m",
        "pipeline.compute_uk_event",
        "--event",
        spec["event"],
        "--variant",
        variant_id,
        "--allow-uncertified",
        "--variants-file",
        str(work / "variants.json"),
        "--workers",
        str(spec["workers"]),
        "--output-dir",
        str(output),
        "--dataset-file",
        str(dataset),
    ]
    if spec["years"]:
        command += ["--years", *map(str, spec["years"])]
    if spec["measures"]:
        command += ["--measures", *spec["measures"]]
    compute = measured_run(command, cwd=REMOTE_ROOT, env=env)
    # compute_uk_event writes its manifest only for a complete requested grid;
    # full_event_complete says whether that grid was the whole event's.
    manifest_path = output / "RUN_MANIFEST.json"
    manifest = (
        json.loads(manifest_path.read_bytes()) if manifest_path.is_file() else None
    )
    coverage = (
        {
            "full_event_complete": manifest["full_event_complete"],
            "full_event_pairs": len(manifest["full_event_grid"]),
            "artifact_pairs": len(manifest["artifact_grid"]),
            "years": manifest["years"],
        }
        if manifest
        else None
    )
    memory = psutil.virtual_memory()
    return {
        "variant_id": variant_id,
        # How prepare resolved the candidate's environment, as the qualifier
        # records it in the namespace's INSTALL.json.
        "install": json.loads((work / "INSTALL.json").read_bytes()),
        "coverage": coverage,
        "container": {
            "cpu": CPU,
            "memory_limit_mib": MEMORY_MIB,
            "mem_total_bytes": memory.total,
            "cpu_count": os.cpu_count(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "probe": {key: probe[key] for key in probe if key != "log"},
        "compute": compute,
    }


# --- local: plan, slots and the provider call ---------------------------------------


def modal_objects(request_path: Path, dataset_path: Path, repository: Path):
    if sys.version_info[:2] != (3, 12):
        raise ValueError("run with the Python 3.12 Modal control environment")
    import modal

    image = (
        modal.Image.debian_slim(python_version="3.12")
        .pip_install(f"uv=={UV_VERSION}", *CONTROL_PINS)
        .add_local_dir(repository, REMOTE_ROOT, copy=True)
        .add_local_file(request_path, f"{REMOTE_WORK}/REQUEST.json", copy=True)
        # The qualifier's own environment build, with the package index
        # reachable only here, at image build.
        .run_commands(
            f"cd {REMOTE_ROOT} && PYTHONPATH={REMOTE_ROOT} python -m "
            f"pipeline.uk_replay_qualify prepare --request {REMOTE_WORK}/REQUEST.json "
            f"--venv {REMOTE_WORK}/venv --wheels {REMOTE_WORK}/wheels "
            f"--output {REMOTE_WORK}/wheel-digests.json"
        )
        .env({"PYTHONPATH": REMOTE_ROOT})
        .add_local_file(dataset_path, "/inputs/dataset.h5", copy=False)
    )
    app = modal.App("scorecard-uk-replay-memory", include_source=False)
    measure = app.function(
        image=image,
        cpu=(CPU, CPU),
        memory=(MEMORY_MIB, MEMORY_MIB),
        timeout=TIMEOUT_SECONDS,
        max_containers=1,
        retries=0,
        block_network=True,
        restrict_modal_access=True,
        serialized=True,
    )(remote_measure)

    def modal_now() -> float:
        return time.time()

    clock = app.function(
        image=modal.Image.debian_slim(python_version="3.12"),
        timeout=60,
        block_network=True,
        restrict_modal_access=True,
        serialized=True,
    )(modal_now)
    return modal, app, measure, clock


def scheduling_workload(measurement: dict) -> dict | None:
    """The workload a measurement stands for when scheduling two workers;
    None when it cannot stand for one.

    That takes a completed run with exactly two year workers, both spawned,
    of the whole scheduling event (no year or measure selection, and the run
    manifest's full event grid complete), recorded with the candidate's
    identity and the workload digest. A slice leaves out years, worlds and
    the memory a worker accumulates over them."""
    from pipeline import uk_replay_qualify as qualify

    compute = measurement.get("compute") or {}
    coverage = measurement.get("coverage") or {}
    if (
        type(measurement.get("workers")) is not int
        or measurement["workers"] != 2
        or compute.get("exit_code") != 0
        or compute.get("process_count_by_role", {}).get("year_worker") != 2
        or measurement.get("event") != qualify.MEMORY_SCHEDULING_EVENT
        or measurement.get("years") != []
        or measurement.get("measures") != []
        or coverage.get("full_event_complete") is not True
        or not isinstance(measurement.get("candidate"), dict)
        or not isinstance(measurement.get("workload_sha256"), str)
    ):
        return None
    return {
        "candidate": measurement["candidate"],
        "corpus_version": measurement["corpus_version"],
        "event": measurement["event"],
        "workload_sha256": measurement["workload_sha256"],
    }


def summarize(measurements: list[dict]) -> dict:
    """The evidence document: every measurement, and per dataset its peaks.

    The qualifier reads only ``two_worker_peaks``: the largest peak of each
    workload that ``scheduling_workload`` accepts. ``one_worker_peak_rss_bytes``
    is the largest completed one-worker peak of any slice, for reading only."""
    datasets: dict[str, dict] = {}
    for measurement in sorted(measurements, key=lambda m: m["label"]):
        dataset = measurement["dataset"]
        entry = datasets.setdefault(
            dataset["sha256"],
            {
                "dataset": dataset["dataset"],
                "build_id": dataset["build_id"],
                "size_bytes": dataset["size_bytes"],
                "one_worker_peak_rss_bytes": None,
                "two_worker_peaks": [],
                "measurements": [],
            },
        )
        entry["measurements"].append(measurement["label"])
        compute = measurement.get("compute") or {}
        peak = compute.get("tree_peak_rss_bytes")
        if compute.get("exit_code") != 0 or type(peak) is not int or peak <= 0:
            continue
        if type(measurement.get("workers")) is int and measurement["workers"] == 1:
            entry["one_worker_peak_rss_bytes"] = max(
                entry["one_worker_peak_rss_bytes"] or 0, peak
            )
            continue
        workload = scheduling_workload(measurement)
        if workload is None:
            continue
        row = next(
            (r for r in entry["two_worker_peaks"] if r["workload"] == workload),
            None,
        )
        if row is None:
            row = {"workload": workload, "peak_rss_bytes": 0, "measurements": []}
            entry["two_worker_peaks"].append(row)
        row["peak_rss_bytes"] = max(row["peak_rss_bytes"], peak)
        row["measurements"].append(measurement["label"])
    return {
        "schema_version": 1,
        "measured_with": "pipeline/modal_uk_replay_memory.py",
        "measure": "peak summed RSS of compute_uk_event and its year workers",
        "datasets": datasets,
        "measurements": sorted(measurements, key=lambda m: m["label"]),
    }


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv[:1] == ["summarize"]:
        summary = argparse.ArgumentParser(prog="summarize")
        summary.add_argument("--output", type=Path, required=True)
        summary.add_argument("measurements", nargs="+", type=Path)
        args = summary.parse_args(argv[1:])
        args.output.write_bytes(
            canonical_bytes(
                summarize([json.loads(path.read_bytes()) for path in args.measurements])
            )
        )
        return 0
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--dataset-file", type=Path, required=True)
    parser.add_argument("--event", required=True)
    parser.add_argument("--years", nargs="*", type=int, default=[])
    parser.add_argument("--measures", nargs="*", default=[])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    from pipeline import uk_replay_interface as interface

    request = json.loads(args.request.read_bytes())
    request_id = interface.request_id(request)
    spec = selection(args, request)
    data = request["candidate"]["data"]
    if (
        args.dataset_file.stat().st_size != data["size_bytes"]
        or sha256_file(args.dataset_file) != data["sha256"]
    ):
        raise ValueError("the dataset file differs from the request")
    from pipeline import uk_replay_qualify as qualify

    # The workload this run stands for, from the files the snapshot copies.
    workload = qualify.memory_workload(request)
    plan = {
        "label": args.label,
        "request_id": request_id,
        "candidate": workload["candidate"],
        "corpus_version": workload["corpus_version"],
        "workload_sha256": workload["workload_sha256"],
        **spec,
    }
    if not args.execute:
        print(canonical_bytes({**plan, "cloud_call": False}).decode(), end="")
        return 0
    from pipeline.modal_uk_event import SLOTS_DICT, NoSlotFree, SimulationSlots

    leases = []
    response = None
    started = False
    slots = None
    with tempfile.TemporaryDirectory() as temporary:
        repository = snapshot(Path(temporary) / "repository")
        modal, app, measure, clock = modal_objects(
            args.request.resolve(), args.dataset_file.resolve(), repository
        )
        try:
            with modal.enable_output(), app.run():
                slots = SimulationSlots(
                    modal.Dict.from_name(SLOTS_DICT, create_if_missing=True),
                    holder=f"{platform.node()}:{os.getpid()}:memory:{args.label}",
                    clock=clock.remote,
                    minimum=TIMEOUT_SECONDS + GUARD_MARGIN_SECONDS + 60,
                )
                # One slot per simulation the run holds at once. Other
                # holders take a freed slot within seconds, so poll often.
                for _ in range(args.workers):
                    leases.append(slots.acquire(poll_seconds=SLOT_POLL_SECONDS))
                started = True
                response = measure.remote(spec, min(lease.expires for lease in leases))
        except NoSlotFree as error:
            print(f"Modal run not started: {error}", file=sys.stderr)
            return 75
        finally:
            # As modal_uk_event: free the slots when the run returned or
            # never started; otherwise they lapse with their lease.
            returned = response is not None and "refused" not in response
            if slots is not None and (not started or returned):
                for lease in leases:
                    try:
                        slots.release(lease)
                    except Exception as error:  # noqa: BLE001 - the claim lapses
                        print(f"slot not released ({error})", file=sys.stderr)
    if response is None or "refused" in response:
        print(f"Modal run did not return a measurement: {response}", file=sys.stderr)
        return 75
    result = {
        "schema_version": 1,
        **plan,
        "phase_peaks": "process_and_tree",
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **response,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(result))
    compute = response.get("compute", {})
    print(
        f"{args.label}: exit {compute.get('exit_code')}, peak tree RSS "
        f"{compute.get('tree_peak_rss_bytes', 0) / 2**30:.2f} GiB in "
        f"{compute.get('wall_seconds')} s"
    )
    return 0 if compute.get("exit_code") == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
