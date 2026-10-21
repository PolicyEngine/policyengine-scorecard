"""Run policy experiments on the modern population in one offline Modal container.

Experiments are not replays (docs/uk_replay/POLICY_EXPERIMENTS.md). This
adapter follows pipeline/modal_uk_event.py: an exact allowlist of uploaded
files, the dataset's SHA-256 checked before the upload and again remotely,
runtime network blocked, no credential sent, and one of the replay's two
shared simulation slots held for the run, so experiments and replays together
never run more than two simulations at once.

Inspect the inputs without a provider call::

    python3 -m pipeline.modal_uk_experiment --event autumn_statement_2022 \\
        --dataset-file PATH --plan

Probe a new population's installed identity and data years (one simulation)::

    .venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_experiment \\
        --event autumn_statement_2022 --dataset-file PATH --probe --execute

Run an event's experiments (optionally --years / --experiments)::

    .venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_experiment \\
        --event autumn_statement_2022 --dataset-file PATH --execute

Downloads land under .venv-replay-checks/experiment-downloads/; --adopt then
copies a verified, complete download into results/uk/experiments/.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

from pipeline import modal_uk_event as replay_modal

ROOT = Path(__file__).resolve().parent.parent
REMOTE_ROOT = "/experiment"
REMOTE_VENV = "/opt/experiment-venv"
REMOTE_PYTHON = f"{REMOTE_VENV}/bin/python"
REMOTE_DATASET = "input/dataset.h5"
REMOTE_OUTPUT = ".venv-replay-checks/experiment-output"
PYTHON_VERSION = replay_modal.PYTHON_VERSION
UV_VERSION = replay_modal.UV_VERSION
MODAL_VERSION = replay_modal.MODAL_VERSION
MAX_RETURN_BYTES = replay_modal.MAX_RETURN_BYTES
DOWNLOAD_ROOT = ".venv-replay-checks/experiment-downloads"
# policyengine.py installed from its release commit while the wheel is not
# yet on PyPI; the requirements freeze records the same source.
WRAPPER_SOURCE = re.compile(
    r"^# policyengine installed from (git\+https://github\.com/PolicyEngine/policyengine\.py@[0-9a-f]{40})"
)
REPOSITORY_FILES = (
    "pipeline/uk_policy_experiment.py",
    "pipeline/modal_uk_experiment.py",
    "pipeline/modal_uk_event.py",
    "pipeline/compute_uk_event.py",
    "pipeline/compute_uk_ab2025.py",
    "pipeline/stage_uk_ab2025.py",
    "pipeline/compute_uk_obr_costings.py",
    "pipeline/build_uk_event_registry.py",
    "pipeline/uk_engine_registry.py",
    "pipeline/uk_replay_variants.py",
    "pipeline/uk_construction_revisions.py",
    "data/uk/events/construction_revisions.json",
    "data/uk/experiments/populations.json",
    "data/uk/experiments/obr_head_forecasts.json",
)
RESOURCE_LIMITS = {**replay_modal.RESOURCE_LIMITS}
OFFLINE_ENV = {**replay_modal.OFFLINE_ENV}


def canonical_bytes(value: object) -> bytes:
    return replay_modal.canonical_bytes(value)


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return replay_modal.sha256_file(path)


def experiment_module():
    from pipeline import uk_policy_experiment

    return uk_policy_experiment


def repository_files(event: str, population: dict) -> tuple[str, ...]:
    experiments = experiment_module()
    spec_relative = str(experiments.spec_path(event).relative_to(ROOT))
    spec = json.loads((ROOT / spec_relative).read_bytes())
    return (
        *REPOSITORY_FILES,
        spec_relative,
        spec["registry"]["path"],
        population["requirements"]["path"],
    )


def wrapper_source(requirements: Path) -> str | None:
    for line in requirements.read_text().splitlines():
        match = WRAPPER_SOURCE.match(line)
        if match:
            return match[1]
    return None


def request_spec(event: str, population_id: str, *, years, experiments, probe) -> dict:
    module = experiment_module()
    module.spec_path(event)
    if not module.POPULATION_ID.fullmatch(population_id):
        raise ValueError("not an experiment population id")
    if len(years) != len(set(years)) or len(experiments) != len(set(experiments)):
        raise ValueError("years and experiments must be unique")
    return {
        "schema_version": 1,
        "kind": "uk_policy_experiment_modal_request",
        "label": module.LABEL,
        "is_replay": False,
        "event": event,
        "population_id": population_id,
        "years": sorted(years),
        "experiments": list(experiments),
        "probe": probe,
    }


def input_manifest(
    event: str, population: dict, dataset_file: Path
) -> tuple[dict, dict[str, Path]]:
    """Exact mounts. The dataset's bytes must be the population's."""
    dataset = population["identity"]["dataset"]
    if dataset_file.stat().st_size != dataset["size_bytes"]:
        raise ValueError("the dataset file's size differs from the population record")
    digest = sha256_file(dataset_file)
    if digest != dataset["sha256"]:
        raise ValueError(
            "the dataset file's SHA-256 differs from the population record"
        )
    mounts = {
        relative: ROOT / relative for relative in repository_files(event, population)
    }
    rows = []
    for relative, source in sorted(mounts.items()):
        replay_modal.relative_path(relative)
        if not source.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("an allowlisted input resolves outside the workspace")
        rows.append(
            {
                "path": relative,
                "size_bytes": source.stat().st_size,
                "sha256": sha256_file(source),
                "kind": "input",
            }
        )
    mounts[REMOTE_DATASET] = dataset_file.resolve(strict=True)
    rows.append(
        {
            "path": REMOTE_DATASET,
            "size_bytes": dataset["size_bytes"],
            "sha256": dataset["sha256"],
            "kind": "population_dataset",
        }
    )
    return {
        "schema_version": 1,
        "event": event,
        "population_id": population["population_id"],
        "files": rows,
        "resource_limits": RESOURCE_LIMITS,
    }, mounts


def verify_inputs(manifest: dict, *, root: Path) -> None:
    """Remote: uploaded bytes equal the manifest before any engine import."""
    for row in manifest["files"]:
        replay_modal.relative_path(row["path"])
        path = root / row["path"]
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("an uploaded input escapes the remote root")
        if (
            path.stat().st_size != row["size_bytes"]
            or sha256_file(path) != row["sha256"]
        ):
            raise ValueError(f"uploaded input differs from its digest: {row['path']}")


def probe_identity(population: dict, dataset: Path) -> dict:
    """Remote, engine: what a population record must bind. One simulation,
    for the dataset's year set."""
    from pipeline import compute_uk_ab2025 as worlds
    from pipeline import compute_uk_obr_costings as fiscal
    from pipeline import uk_replay_variants as variants

    experiments = experiment_module()
    view = experiments.variant_view(population)
    variants.isolate_certification_environment()
    fiscal.configure_offline()
    worlds.configure_offline()
    runtime_root = (experiments.RUNTIME_ROOT / population["population_id"]).resolve()
    materialized = variants.materialize_dataset(view, runtime_root, source=dataset)
    os.chdir(runtime_root)
    variants.isolate_bytecode(runtime_root)
    import policyengine as pe

    installed = variants.installed_identity()
    release_bundle = dict(pe.uk.uk_latest.release_bundle)
    sim = pe.uk.managed_microsimulation()
    years = sorted(int(year) for year in sim.dataset.years)
    bundle = dict(sim.policyengine_bundle)
    sim = None
    return {
        "installed": installed,
        "release_bundle": release_bundle,
        "runtime_bundle_dataset_source": bundle.get("runtime_dataset_source"),
        "materialized": str(materialized),
        "dataset_years": years,
    }


def run_worker(payload: dict) -> int:
    started = time.perf_counter()
    root = Path(REMOTE_ROOT)
    for key, value in OFFLINE_ENV.items():
        os.environ[key] = value
    verify_inputs(payload["inputs"], root=root)
    request = payload["request"]
    experiments = experiment_module()
    population = (
        _probe_population(request["population_id"])
        if request["probe"]
        else experiments.get_population(request["population_id"])
    )
    output = root / REMOTE_OUTPUT
    if output.exists() and any(output.iterdir()):
        raise ValueError("the remote output directory already holds files")
    output.mkdir(parents=True, exist_ok=True)
    dataset = root / REMOTE_DATASET
    if request["probe"]:
        result = probe_identity(population, dataset)
        (output / "PROBE.json").write_bytes(canonical_bytes(result))
    else:
        argv = [
            "run",
            "--event",
            request["event"],
            "--population",
            request["population_id"],
            "--dataset-file",
            str(dataset),
            "--output-dir",
            str(output),
        ]
        if request["years"]:
            argv += ["--years", *map(str, request["years"])]
        if request["experiments"]:
            argv += ["--experiments", *request["experiments"]]
        if experiments.main(argv):
            raise RuntimeError("the experiment runner returned a failure")
    files = {}
    total = 0
    for path in sorted(output.iterdir()):
        if not path.is_file() or not re.fullmatch(r"[A-Za-z0-9_]+\.json", path.name):
            raise ValueError(f"unexpected output file {path.name}")
        total += path.stat().st_size
        if total > MAX_RETURN_BYTES:
            raise ValueError("output exceeds the small-artifact return limit")
        files[path.name] = sha256_file(path)
    receipt = {
        "schema_version": 1,
        "kind": "uk_policy_experiment_modal_receipt",
        "label": experiments.LABEL,
        "is_replay": False,
        "runner": "Modal offline Linux; pipeline.uk_policy_experiment",
        "request": request,
        "request_sha256": digest_bytes(canonical_bytes(request)),
        "input_manifest_sha256": digest_bytes(canonical_bytes(payload["inputs"])),
        "files": files,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output / "MODAL_RECEIPT.json").write_bytes(canonical_bytes(receipt))
    return 0


def modal_function(mounts: dict[str, Path], requirements: Path):
    """Lazy SDK objects; only main's explicit --execute starts them."""
    if sys.version_info[:2] != (3, 12):
        raise ValueError("Modal execution needs a Python 3.12 control interpreter")
    import modal

    if importlib.metadata.version("modal") != MODAL_VERSION:
        raise ValueError(f"Modal control SDK must be =={MODAL_VERSION}")
    source = wrapper_source(requirements)
    install = [
        f"uv python install {PYTHON_VERSION}",
        f"uv venv --python {PYTHON_VERSION} {REMOTE_VENV}",
    ]
    if source:
        install += [
            "grep -v '^policyengine==' /opt/experiment-requirements.txt > /opt/requirements-pypi.txt",
            f"uv pip install --python {REMOTE_PYTHON} --requirements /opt/requirements-pypi.txt",
            f"uv pip install --python {REMOTE_PYTHON} --no-deps 'policyengine @ {source}'",
        ]
    else:
        install.append(
            f"uv pip install --python {REMOTE_PYTHON} --requirements /opt/experiment-requirements.txt"
        )
    image = (
        modal.Image.debian_slim(python_version="3.12")
        .apt_install("git")
        .pip_install(f"uv=={UV_VERSION}")
        .add_local_file(requirements, "/opt/experiment-requirements.txt", copy=True)
        .run_commands(*install)
        .env({**OFFLINE_ENV, "PYTHONPATH": REMOTE_ROOT})
    )
    for relative, path in sorted(mounts.items()):
        image = image.add_local_file(path, f"{REMOTE_ROOT}/{relative}", copy=False)
    app = modal.App("scorecard-uk-policy-experiments", include_source=False)
    timeout_seconds = RESOURCE_LIMITS["timeout_seconds"]
    guard_seconds = timeout_seconds + replay_modal.GUARD_MARGIN_SECONDS

    @app.function(
        image=image,
        serialized=True,
        include_source=False,
        cpu=(2, 2),
        memory=(32768, 32768),
        timeout=timeout_seconds,
        max_containers=1,
        retries=0,
        block_network=True,
        restrict_modal_access=True,
    )
    @modal.concurrent(max_inputs=1)
    def experiment(payload: dict, lease_expires: float) -> dict:
        import hashlib
        import json
        import subprocess
        import time
        from pathlib import Path

        if time.time() + guard_seconds > lease_expires:
            return {"refused": "the simulation slot lease does not cover the timeout"}
        subprocess.run(
            [
                "/opt/experiment-venv/bin/python",
                "-m",
                "pipeline.modal_uk_experiment",
                "--worker-request",
                json.dumps(payload, separators=(",", ":")),
            ],
            cwd="/experiment",
            check=True,
        )
        output = Path("/experiment/.venv-replay-checks/experiment-output")
        receipt = json.loads((output / "MODAL_RECEIPT.json").read_bytes())
        files = {}
        total = 0
        for name in [*receipt["files"], "MODAL_RECEIPT.json"]:
            data = (output / name).read_bytes()
            total += len(data)
            if total > 8 * 1024 * 1024:
                raise ValueError("result exceeds the small-artifact return limit")
            files[name] = {"bytes": data, "sha256": hashlib.sha256(data).hexdigest()}
        return {"files": files}

    @app.function(
        image=modal.Image.debian_slim(python_version="3.12"),
        serialized=True,
        include_source=False,
        timeout=60,
        block_network=True,
        restrict_modal_access=True,
    )
    def modal_time() -> float:
        import time

        return time.time()

    return modal, app, experiment, modal_time


def download_dir(download_root: str, payload: dict) -> Path:
    """One folder per request and exact inputs, so a rerun on a corrected
    spec never meets an earlier run's files."""
    replay_modal.relative_path(download_root)
    if not PurePosixPath(download_root).is_relative_to(".venv-replay-checks"):
        raise ValueError("downloads must stay under .venv-replay-checks")
    request = payload["request"]
    stamp = digest_bytes(canonical_bytes(payload))[:12]
    target = ROOT / download_root / request["population_id"] / request["event"] / stamp
    if not target.resolve().is_relative_to((ROOT / ".venv-replay-checks").resolve()):
        raise ValueError("the download directory escapes .venv-replay-checks")
    return target


def save_download(response: dict, payload: dict, target: Path) -> list[Path]:
    files = response.get("files", {})
    total = 0
    for name, row in files.items():
        if not re.fullmatch(r"[A-Za-z0-9_]+\.json", name):
            raise ValueError(f"returned file name {name!r}")
        total += len(row["bytes"])
        if total > MAX_RETURN_BYTES or digest_bytes(row["bytes"]) != row["sha256"]:
            raise ValueError("a returned file fails its size or SHA-256 receipt")
    receipt = json.loads(files["MODAL_RECEIPT.json"]["bytes"])
    if (
        receipt["request"] != payload["request"]
        or receipt["input_manifest_sha256"]
        != digest_bytes(canonical_bytes(payload["inputs"]))
        or receipt["files"]
        != {
            name: row["sha256"]
            for name, row in files.items()
            if name != "MODAL_RECEIPT.json"
        }
    ):
        raise ValueError("the receipt does not bind the request, inputs and files")
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"{target} already holds files")
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name, row in files.items():
        with tempfile.NamedTemporaryFile(dir=target, delete=False) as handle:
            handle.write(row["bytes"])
        Path(handle.name).replace(target / name)
        written.append(target / name)
    return written


def adopt(downloads: list[Path], event: str, population_id: str) -> Path:
    """Merge verified downloads (one per year batch) into the event's results.

    Each download's receipt binds its files; the merged manifest lists every
    artifact. Existing results for the same experiment-years are replaced."""
    experiments = experiment_module()
    destination = experiments.contained_output_dir(population_id, event)
    destination.mkdir(parents=True, exist_ok=True)
    manifests = []
    for directory in downloads:
        receipt = json.loads((directory / "MODAL_RECEIPT.json").read_bytes())
        if (
            receipt["request"]["event"] != event
            or receipt["request"]["population_id"] != population_id
        ):
            raise ValueError(f"{directory}: another event or population")
        for name, digest in receipt["files"].items():
            if sha256_file(directory / name) != digest:
                raise ValueError(f"{directory / name}: bytes differ from the receipt")
        manifests.append(
            json.loads((directory / "EXPERIMENT_MANIFEST.json").read_bytes())
        )
        for name in receipt["files"]:
            if name == "EXPERIMENT_MANIFEST.json":
                continue
            shutil.copyfile(directory / name, destination / name)
    existing = destination / "EXPERIMENT_MANIFEST.json"
    if existing.exists():
        manifests.insert(0, json.loads(existing.read_bytes()))
    first = manifests[-1]
    for manifest in manifests:
        for field in ("registry_sha256", "spec_sha256", "population_identity"):
            if manifest[field] != first[field]:
                raise ValueError(f"downloads disagree on {field}; rerun on one spec")
    files = {}
    grid = {}
    for manifest in manifests:
        for row in manifest["files"]:
            files[row["path"]] = row
        for cell in manifest["grid"]:
            grid[(cell["experiment_id"], cell["year"])] = cell
    merged = {
        **first,
        "years": sorted({year for _, year in grid}),
        "experiments": [e for e in first["experiments"]],
        "grid": [grid[key] for key in sorted(grid)],
        "files": [files[name] for name in sorted(files)],
    }
    merged["experiments"] = sorted({eid for eid, _ in grid})
    existing.write_bytes(canonical_bytes(merged))
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event")
    parser.add_argument("--population")
    parser.add_argument("--dataset-file", type=Path)
    parser.add_argument("--years", nargs="*", type=int, default=[])
    parser.add_argument("--experiments", nargs="*", default=[])
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--download-root", default=DOWNLOAD_ROOT)
    parser.add_argument("--adopt", nargs="*", type=Path)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--plan", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--worker-request", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker_request:
        return run_worker(json.loads(args.worker_request))
    experiments = experiment_module()
    population = (
        experiments.get_population(args.population)
        if not args.probe
        else _probe_population(args.population)
    )
    if args.adopt is not None:
        destination = adopt(args.adopt, args.event, population["population_id"])
        print(f"adopted into {destination}")
        return 0
    request = request_spec(
        args.event,
        population["population_id"],
        years=args.years,
        experiments=args.experiments,
        probe=args.probe,
    )
    inputs, mounts = input_manifest(args.event, population, args.dataset_file)
    payload = {"request": request, "inputs": inputs}
    target = download_dir(args.download_root, payload)
    if not args.execute:
        print(
            canonical_bytes(
                {
                    **payload,
                    "download_dir": str(target.relative_to(ROOT)),
                    "cloud_call": False,
                }
            ).decode(),
            end="",
        )
        return 0
    modal, app, experiment, modal_time = modal_function(
        mounts, ROOT / population["requirements"]["path"]
    )
    response = None
    lease = slots = None
    started = False
    try:
        with modal.enable_output(), app.run():
            slots = replay_modal.SimulationSlots(
                modal.Dict.from_name(replay_modal.SLOTS_DICT, create_if_missing=True),
                holder=f"{platform.node()}:{os.getpid()}:experiment:{digest_bytes(canonical_bytes(request))[:12]}",
                clock=modal_time.remote,
            )
            lease = slots.acquire()
            started = True
            response = experiment.remote(payload, lease.expires)
    except replay_modal.NoSlotFree as error:
        print(f"Modal run not started: {error}", file=sys.stderr)
        return 75
    except Exception as error:
        if response is None:
            raise
        print(f"Modal app exit failed after the run returned: {error}", file=sys.stderr)
    finally:
        returned = response is not None and "refused" not in response
        if lease is not None and (not started or returned):
            try:
                slots.release(lease)
            except Exception as error:  # noqa: BLE001 - the claim lapses
                print(
                    f"simulation slot not released ({error}); it will lapse",
                    file=sys.stderr,
                )
    if response is None:
        print("Modal run interrupted; nothing downloaded", file=sys.stderr)
        return 130
    if "refused" in response:
        print(f"Modal run refused: {response['refused']}", file=sys.stderr)
        return 75
    written = save_download(response, payload, target)
    print(f"verified and downloaded {len(written)} files to {target.relative_to(ROOT)}")
    return 0


def _probe_population(population_id: str | None) -> dict:
    """A probe runs before the record binds installed digests: read the
    record without the environment fields a probe is there to supply."""
    experiments = experiment_module()
    document = json.loads(experiments.POPULATIONS_PATH.read_bytes())
    wanted = population_id or document["default_population"]
    for record in document["populations"]:
        if record["population_id"] == wanted:
            return record
    raise ValueError(f"no experiment population {wanted!r}")


if __name__ == "__main__":
    sys.exit(main())
