"""Run pipeline/compute_uk_two_child_limit_poverty.py in offline Modal
containers (lane uk-two-child-limit-poverty).

The same script, unchanged, in a container per engine environment: a uv venv
built from the lane's frozen requirements (docs/uk_two_child_limit_poverty/
requirements-<env>.txt, each `uv pip freeze` of the local venv that ran the
same code), the dataset files mounted read-only, the function's network
blocked and no credential sent. The host's local runs are left alone (a
fleet capacity reservation may hold them); the artifacts are identical in
shape and record the container's platform and Python.

    .venv-modal-control/bin/python -m pipeline.modal_uk_two_child_limit_poverty --plan
    .venv-modal-control/bin/python -m pipeline.modal_uk_two_child_limit_poverty --execute [--only <run>]

RUNS name each run: the certified pair through the managed route, and the
decomposition grid (two datasets x three engines, bare Microsimulation).
Each run's output lands where the local run would write it; a run that
raises in its container is recorded in diagnostics/FAILED.json with its
error, never filled in.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REMOTE = "/work"
PAIR = json.loads(
    (ROOT / "data" / "uk" / "two_child_limit_poverty" / "certified_pair.json").read_text()
)
LOCAL_MIRROR = ROOT / "data" / "uk" / "policyengine-local"
DATASETS = {
    "microcosm": {
        "local": LOCAL_MIRROR / PAIR["pair_id"] / "data" / "microcosm_uk_2024_25.h5",
        "sha256": PAIR["dataset"]["sha256"],
        "remote": f"{REMOTE}/data/uk/policyengine-local/{PAIR['pair_id']}/data/microcosm_uk_2024_25.h5",
    },
    "populace": {
        "local": LOCAL_MIRROR / "populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z" / "populace_uk_2023.h5",
        # data/uk/certified_bundle.json: the bundle the September run used
        "sha256": json.loads((ROOT / "data" / "uk" / "certified_bundle.json").read_text())["sha256"],
        "remote": f"{REMOTE}/data/populace_uk_2023.h5",
    },
}
ENVS = {
    "pe6101": "docs/uk_two_child_limit_poverty/requirements-pe6101.txt",
    "uk21483": "docs/uk_two_child_limit_poverty/requirements-uk21483.txt",
    "pe289": "docs/uk_two_child_limit_poverty/requirements-pe289.txt",
}
# run -> (env, dataset, compute arguments, output path relative to ROOT)
OUT = "results/uk/two_child_limit_poverty"
RUNS = {
    "certified": ("pe6101", "microcosm", ["certified"], f"{OUT}/{PAIR['pair_id']}.json"),
    **{
        f"{data}_uk{engine}": (
            env,
            data,
            ["diagnostic", "--dataset", DATASETS[data]["remote"], "--label", f"{data}_uk{engine}"],
            f"{OUT}/diagnostics/{data}_uk{engine}.json",
        )
        for env, engine in (("pe6101", "2.132.6"), ("uk21483", "2.148.3"), ("pe289", "2.89.2"))
        for data in ("microcosm", "populace")
    },
}
FILES = (
    "pipeline/compute_uk_two_child_limit_poverty.py",
    "data/uk/two_child_limit_poverty/certified_pair.json",
)
MODAL_VERSION = "1.3.2"
UV_VERSION = "0.13.4"
PYTHON = "3.12.13"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def plan() -> dict:
    out = {"runs": {}, "datasets": {}}
    for name, ds in DATASETS.items():
        present = ds["local"].is_file()
        out["datasets"][name] = {
            "local": str(ds["local"].relative_to(ROOT)),
            "present": present,
            "sha256_ok": present and sha256_file(ds["local"]) == ds["sha256"],
        }
    for run, (env, data, args, output) in RUNS.items():
        out["runs"][run] = {"env": ENVS[env], "dataset": data, "args": args, "output": output}
    return out


def build(env: str, data: str):
    import modal

    if __import__("importlib.metadata").metadata.version("modal") != MODAL_VERSION:
        raise SystemExit(f"Modal control SDK must be =={MODAL_VERSION}")
    image = (
        modal.Image.debian_slim(python_version="3.12")
        .pip_install(f"uv=={UV_VERSION}")
        .add_local_file(ROOT / ENVS[env], "/opt/requirements.txt", copy=True)
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
        image = image.add_local_file(ROOT / relative, f"{REMOTE}/{relative}", copy=False)
    image = image.add_local_file(DATASETS[data]["local"], DATASETS[data]["remote"], copy=False)
    app = modal.App(f"scorecard-uk-two-child-limit-{env}-{data}", include_source=False)

    @app.function(
        image=image,
        serialized=True,
        include_source=False,
        cpu=(2, 2),
        memory=(16384, 16384),
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
            ["/opt/venv/bin/python", "-m", "pipeline.compute_uk_two_child_limit_poverty", *args],
            cwd="/work",
            capture_output=True,
            text=True,
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


def execute(only: str | None) -> int:
    failed_path = ROOT / OUT / "diagnostics" / "FAILED.json"
    failed = json.loads(failed_path.read_text()) if failed_path.exists() else {}
    for name, ds in DATASETS.items():
        if sha256_file(ds["local"]) != ds["sha256"]:
            raise SystemExit(f"{name}: local dataset is not the pinned artifact")
    for run, (env, data, args, output) in RUNS.items():
        if only and run != only:
            continue
        app, compute = build(env, data)
        with app.run():
            result = compute.remote(args, output)
        if "error" in result:
            failed[run] = result["error"].strip().splitlines()[-1]
            print(f"{run}: FAILED {failed[run]}")
            continue
        failed.pop(run, None)
        if hashlib.sha256(result["bytes"]).hexdigest() != result["sha256"]:
            raise SystemExit(f"{run}: returned bytes do not match their digest")
        path = ROOT / output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result["bytes"])
        print(f"{run}: wrote {output} ({result['platform']})")
    failed_path.parent.mkdir(parents=True, exist_ok=True)
    failed_path.write_text(json.dumps(dict(sorted(failed.items())), indent=1) + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args(argv)
    if a.plan or not a.execute:
        print(json.dumps(plan(), indent=1))
        return 0
    return execute(a.only)


if __name__ == "__main__":
    sys.exit(main())
