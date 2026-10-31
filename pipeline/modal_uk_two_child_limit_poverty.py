"""Run the lane's computations in offline Modal containers (lane
uk-two-child-limit-poverty).

The same scripts, unchanged, in a container per engine environment: a uv
venv built from pinned requirements, the dataset file mounted read-only, the
function's network blocked and no credential sent. The host's local runs
are left alone (a fleet capacity reservation may hold them); the artifacts
are identical in shape and record the container's platform and Python.

    .venv-modal-control/bin/python -m pipeline.modal_uk_two_child_limit_poverty --plan
    .venv-modal-control/bin/python -m pipeline.modal_uk_two_child_limit_poverty --execute [--only <run>]
    .venv-modal-control/bin/python -m pipeline.modal_uk_two_child_limit_poverty --execute \\
        --release 2.140.0 [--release ...] [--data microcosm]

Environments:

    pair     the certified pair's own requirements file
             (data/uk/certified_pairs.json -> docs/uk_replay/requirements/
             pairs/), resolved for Linux; the certified run and the losers
             diagnostic go through that registry's preflight, which checks
             the installed wheels' RECORD hashes against the pair
    uk21483  policyengine-uk 2.148.3 (main when policyengine-uk#1724 was
             written), frozen from the local venv that ran the same code
    pe289    policyengine-uk 2.89.2, the September 2026 run's engine
    release:<v>  a bisection cell: the pair's requirements with
             policyengine-uk==<v> in place of 2.132.6 and the wrapper
             dropped (the bare route needs no wrapper); policyengine-core
             stays 3.33.3, so a cell measures the model package alone, and
             a release that needs a newer core fails to install, recorded

RUNS name each run: the certified pair through the managed route, the
losers diagnostic, and the decomposition grid (two datasets x three
engines, bare Microsimulation). Each run's output lands where the local run
would write it; a run that fails, in its container or while its image
builds, is recorded in diagnostics/FAILED.json with its error, never filled
in.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REMOTE = "/work"
PAIR_ID = (
    "pair-pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71"
)
PAIR = next(
    p
    for p in json.loads((ROOT / "data" / "uk" / "certified_pairs.json").read_text())[
        "pairs"
    ]
    if p["pair_id"] == PAIR_ID
)
DATA_BUILD = PAIR["identity"]["dataset"]["revision"]
LOCAL_MIRROR = ROOT / "data" / "uk" / "policyengine-local"
DATASETS = {
    "microcosm": {
        "local": LOCAL_MIRROR / DATA_BUILD / PAIR["identity"]["dataset"]["path"],
        "sha256": PAIR["identity"]["dataset"]["sha256"],
        "remote": f"{REMOTE}/input/{PAIR['identity']['dataset']['path']}",
        "memory_mib": 16384,
    },
    "populace": {
        "local": LOCAL_MIRROR
        / "populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z"
        / "populace_uk_2023.h5",
        # data/uk/certified_bundle.json: the bundle the September run used
        "sha256": json.loads(
            (ROOT / "data" / "uk" / "certified_bundle.json").read_text()
        )["sha256"],
        "remote": f"{REMOTE}/input/populace_uk_2023.h5",
        # docs/uk_replay/RELEASE_REPLAY.md: the 1.3 GB populace dataset
        # needs Modal's 32 GiB (at 16 GiB the container is lost mid-run);
        # policyengine-uk 2.132.6 and 2.148.3 ran out of memory at 32 GiB
        # here on 2026-10-26 (Modal: "killed after running out of memory")
        "memory_mib": 98304,
    },
}
ENVS = {
    "pair": PAIR["requirements"]["path"],
    "uk21483": "docs/uk_two_child_limit_poverty/requirements-uk21483.txt",
    "pe289": "docs/uk_two_child_limit_poverty/requirements-pe289.txt",
}
COMPUTE = "pipeline.compute_uk_two_child_limit_poverty"
LOSERS = "pipeline.diagnose_uk_two_child_limit_losers"
OUT = "results/uk/two_child_limit_poverty"
MICROCOSM = DATASETS["microcosm"]["remote"]


def diagnostic(env: str, data: str, label: str) -> tuple:
    return (
        env,
        data,
        [
            COMPUTE,
            "diagnostic",
            "--dataset",
            DATASETS[data]["remote"],
            "--label",
            label,
        ],
        f"{OUT}/diagnostics/{label}.json",
    )


# runs that hold more than one world in memory at once
MEMORY_MIB = {"losers": 32768}
# run -> (env, dataset, module and arguments, output path relative to ROOT)
RUNS = {
    "certified": (
        "pair",
        "microcosm",
        [COMPUTE, "certified", "--pair", PAIR_ID, "--dataset-file", MICROCOSM],
        f"{OUT}/{PAIR_ID}.json",
    ),
    "losers": (
        "pair",
        "microcosm",
        [LOSERS, "--pair", PAIR_ID, "--dataset-file", MICROCOSM],
        f"{OUT}/diagnostics/losers.json",
    ),
    **{
        f"{data}_uk{engine}": diagnostic(env, data, f"{data}_uk{engine}")
        for env, engine in (
            ("pair", "2.132.6"),
            ("uk21483", "2.148.3"),
            ("pe289", "2.89.2"),
        )
        for data in ("microcosm", "populace")
    },
}
# Uploaded beside the scripts: the pair registry's preflight and what it
# imports and reads (pipeline/compute_uk_event.py and its modules).
FILES = (
    "pipeline/compute_uk_two_child_limit_poverty.py",
    "pipeline/diagnose_uk_two_child_limit_losers.py",
    "pipeline/uk_certified_pairs.py",
    "pipeline/uk_replay_variants.py",
    "pipeline/compute_uk_event.py",
    "pipeline/compute_uk_ab2025.py",
    "pipeline/compute_uk_obr_costings.py",
    "pipeline/stage_uk_ab2025.py",
    "pipeline/build_uk_event_registry.py",
    "pipeline/uk_engine_registry.py",
    "pipeline/uk_construction_revisions.py",
    "data/uk/certified_pairs.json",
    "data/uk/replay_variants.json",
    "data/uk/certified_bundle.json",
    "data/uk/events/construction_revisions.json",
    "data/uk/events/construction_revisions_enacted.json",
    "data/uk/two_child_limit_poverty/owned_claims.json",
    PAIR["requirements"]["path"],
)
MODAL_VERSION = "1.3.2"
# uv before 0.13.4 trusts a CA whose intermediate keys are public
# (pipeline/modal_uk_event.UV_VERSION).
UV_VERSION = "0.13.4"
PYTHON = "3.12.13"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def release_run(data: str, version: str) -> tuple:
    """A bisection cell: the 2029 worlds, bare Microsimulation, at one
    policyengine-uk release."""
    return diagnostic(
        f"release:{version}", data, f"bisect_{data}_uk{version}_core3.33.3"
    )


def requirements(env: str) -> Path:
    if not env.startswith("release:"):
        return ROOT / ENVS[env]
    version = env.removeprefix("release:")
    lines = [
        line
        for line in (ROOT / ENVS["pair"]).read_text().splitlines()
        if not line.startswith(("#", "policyengine==", "policyengine-uk=="))
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
        handle.write("\n".join([*lines, f"policyengine-uk=={version}"]) + "\n")
    return Path(handle.name)


def plan(runs: dict) -> dict:
    out = {"runs": {}, "datasets": {}}
    for name, ds in DATASETS.items():
        present = ds["local"].is_file()
        out["datasets"][name] = {
            "local": str(ds["local"].relative_to(ROOT)),
            "present": present,
            "sha256_ok": present and sha256_file(ds["local"]) == ds["sha256"],
        }
    for run, (env, data, args, output) in runs.items():
        out["runs"][run] = {"env": env, "dataset": data, "args": args, "output": output}
    return out


def build(env: str, data: str, memory_mib: int | None = None):
    import modal

    if __import__("importlib.metadata").metadata.version("modal") != MODAL_VERSION:
        raise SystemExit(f"Modal control SDK must be =={MODAL_VERSION}")
    image = (
        modal.Image.debian_slim(python_version="3.12")
        .pip_install(f"uv=={UV_VERSION}")
        .add_local_file(requirements(env), "/opt/requirements.txt", copy=True)
        .run_commands(
            f"uv python install {PYTHON}",
            f"uv venv --python {PYTHON} /opt/venv",
            "uv pip install --python /opt/venv/bin/python --requirements /opt/requirements.txt",
        )
        .env(
            {
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
                "HF_DATASETS_OFFLINE": "1",
                "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
                "HDF5_USE_FILE_LOCKING": "FALSE",
                "OMP_NUM_THREADS": "2",
                "OPENBLAS_NUM_THREADS": "2",
                "PYTHONPATH": REMOTE,
            }
        )
    )
    for relative in FILES:
        image = image.add_local_file(
            ROOT / relative, f"{REMOTE}/{relative}", copy=False
        )
    image = image.add_local_file(
        DATASETS[data]["local"], DATASETS[data]["remote"], copy=False
    )
    slug = env.replace(":", "-").replace(".", "-")
    app = modal.App(f"scorecard-uk-two-child-limit-{slug}-{data}", include_source=False)

    @app.function(
        image=image,
        serialized=True,
        include_source=False,
        cpu=(2, 2),
        memory=(memory_mib or DATASETS[data]["memory_mib"],) * 2,
        timeout=7200,
        retries=0,
        block_network=True,
        restrict_modal_access=True,
    )
    def compute(args: list[str], output: str) -> dict:
        import hashlib
        import platform
        import subprocess
        from pathlib import Path

        done = subprocess.run(
            ["/opt/venv/bin/python", "-m", *args],
            cwd="/work",
            capture_output=True,
            text=True,
            check=False,
        )
        if done.returncode:
            return {"error": done.stderr[-4000:], "returncode": done.returncode}
        data = Path("/work", output).read_bytes()
        return {
            "bytes": data,
            "sha256": hashlib.sha256(data).hexdigest(),
            "platform": platform.platform(),
            "log": done.stdout[-4000:],
        }

    return app, compute


def record_failure(run: str, error: str | None) -> None:
    """Read, update and write diagnostics/FAILED.json for one run, so runner
    processes started side by side keep each other's entries."""
    path = ROOT / OUT / "diagnostics" / "FAILED.json"
    failed = json.loads(path.read_text()) if path.exists() else {}
    if error is None:
        failed.pop(run, None)
    else:
        failed[run] = error
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(sorted(failed.items())), indent=1) + "\n")


def execute(runs: dict) -> int:
    for name in {data for _, data, _, _ in runs.values()}:
        ds = DATASETS[name]
        if sha256_file(ds["local"]) != ds["sha256"]:
            raise SystemExit(f"{name}: local dataset is not the pinned artifact")
    for run, (env, data, args, output) in runs.items():
        try:
            app, compute = build(env, data, MEMORY_MIB.get(run))
            with app.run():
                result = compute.remote(args, output)
        except Exception as exc:  # noqa: BLE001 an image build or provider failure
            result = {"error": f"{type(exc).__name__}: {exc}"}
        if "error" in result:
            error = result["error"].strip().splitlines()[-1]
            record_failure(run, error)
            print(f"{run}: FAILED {error}", flush=True)
            continue
        if hashlib.sha256(result["bytes"]).hexdigest() != result["sha256"]:
            raise SystemExit(f"{run}: returned bytes do not match their digest")
        path = ROOT / output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result["bytes"])
        record_failure(run, None)
        print(f"{run}: wrote {output} ({result['platform']})", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--only", action="append", help="a run in RUNS (repeatable)")
    ap.add_argument(
        "--release",
        action="append",
        help="a policyengine-uk release for a bisection cell (repeatable)",
    )
    ap.add_argument("--data", default="microcosm", choices=sorted(DATASETS))
    a = ap.parse_args(argv)
    if a.release:
        runs = {f"{a.data}_uk{v}": release_run(a.data, v) for v in a.release}
    else:
        runs = {k: v for k, v in RUNS.items() if not a.only or k in a.only}
        unknown = sorted(set(a.only or ()) - set(RUNS))
        if unknown:
            raise SystemExit(f"unknown runs {unknown}")
    if a.plan or not a.execute:
        print(json.dumps(plan(runs), indent=1))
        return 0
    return execute(runs)


if __name__ == "__main__":
    sys.exit(main())
