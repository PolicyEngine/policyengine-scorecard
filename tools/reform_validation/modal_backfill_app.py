"""Modal app that runs the reform-validation backfill for a microcosm release.

Why Modal: the producer needs one full Microsimulation per batch plus the
microcosm/torch import stack, which no longer fits GitHub's 7GB ubuntu-latest
runner — every scheduled run since 2026-07-21 died to the runner's OOM
shutdown signal, including post-chunking (#107) runs where even a single
16-spec levels chunk was killed before its first simulation finished. This
app runs the IDENTICAL producer path (tools/reform_validation/backfill.py,
mounted verbatim from the repo checkout at deploy time) in a 64GB container.

Division of labor with the scheduled workflow
(.github/workflows/reform-validation-backfill.yml):

  GitHub Actions          resolve release id -> spawn this app (fire-and-
  (trigger/commit layer)  forget) -> on a LATER tick, harvest the finished
                          artifact from the Volume -> land it under
                          sources/populace-reform-validation/raw/, re-run
                          scorecard_db.ingest_reform_validation, commit the
                          rebuilt DB, open a PR. No simulation ever runs on
                          the runner, so ticks take seconds.

  This app                clone microcosm at the requested ref, install the
  (simulation layer)      release-exact policyengine-us/-core from the
                          release manifest at runtime, drive backfill.py
                          with a Volume-backed workdir (batch partials
                          survive interruptions and resume), and publish
                          reform_validation_<release_id>.json to the Volume.

Engine versions are installed at RUNTIME (not baked into the image) because
they are release-exact and change per release; the image carries only the
heavy version-stable dependencies. The producer ref is an argument for the
same reason — no image rebuild per microcosm commit.

Manual use:
    modal deploy tools/reform_validation/modal_backfill_app.py
    python -c "
    import modal
    fn = modal.Function.from_name('scorecard-reform-validation-backfill', 'backfill')
    print(fn.spawn('<release-id>', '<microcosm-ref>').object_id)"

Requires Modal credentials (MODAL_TOKEN_ID / MODAL_TOKEN_SECRET) for the
PolicyEngine workspace.
"""

from pathlib import Path

import modal

APP_NAME = "scorecard-reform-validation-backfill"
app = modal.App(APP_NAME)

VOLUME_NAME = "scorecard-reform-validation"
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

# Heavy, version-stable dependencies only. The release-exact engine
# (policyengine-us / policyengine-core) installs at runtime per release.
image = (
    modal.Image.debian_slim(python_version="3.13")
    .apt_install("git")
    .pip_install(
        "tables",
        "microdf-python",
        "h5py",
        "numpy",
        "pandas",
        "scipy",
        "scikit-learn",
        "tqdm",
        "requests",
    )
    .pip_install("torch", index_url="https://download.pytorch.org/whl/cpu")
    .add_local_file(str(Path(__file__).parent / "backfill.py"), "/root/backfill.py")
)

PRODUCER_PACKAGES = (
    "microcosm-build",
    "microcosm-frame",
    "microcosm-calibrate",
    "microcosm-fit",
    "microcosm-data",
)


@app.function(
    image=image, timeout=8 * 3600, memory=65536, cpu=8.0, volumes={"/vol": volume}
)
def backfill(
    release_id: str, producer_ref: str = "main", driver_ref: str = "unknown"
) -> str:
    """Produce reform_validation.json for ``release_id`` on the Volume.

    Writes, in order:
      /vol/rv_<sha8>/...                     durable workdir (H5, partials)
      /vol/reform_validation_<release_id>.json  the finished artifact
    The workdir's ``started`` marker (timestamped) plus the spawner-recorded
    ``call_id`` let the workflow distinguish in-flight from dead runs
    (spawn_or_wait.py) instead of trusting the marker alone.
    """
    import hashlib
    import json
    import os
    import subprocess
    import time
    import urllib.request

    subprocess.run(
        ["git", "clone", "https://github.com/PolicyEngine/microcosm", "/opt/microcosm"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", "/opt/microcosm", "checkout", producer_ref], check=True
    )
    producer_commit = subprocess.run(
        ["git", "-C", "/opt/microcosm", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    manifest_url = (
        "https://huggingface.co/datasets/policyengine/populace-us/resolve/main/"
        f"releases/{release_id}/release_manifest.json"
    )
    with urllib.request.urlopen(manifest_url, timeout=60) as r:
        build = json.loads(r.read())["build"]
    peus = build["built_with_model_package"]["version"]
    pecore = build["built_with_core_package"]["version"]
    subprocess.run(
        [
            "pip",
            "install",
            "--quiet",
            f"policyengine-us=={peus}",
            f"policyengine-core=={pecore}",
        ],
        check=True,
    )
    print(
        f"engines installed: policyengine-us {peus} / policyengine-core {pecore}",
        flush=True,
    )

    workdir = f"/vol/rv_{hashlib.sha256(release_id.encode()).hexdigest()[:8]}"
    os.makedirs(workdir, exist_ok=True)
    with open(f"{workdir}/started", "w") as f:
        f.write(
            f"{release_id}\nproducer {producer_commit}\nstarted_at {int(time.time())}\n"
        )
    volume.commit()

    env = {
        **os.environ,
        "PYTHONPATH": ":".join(
            f"/opt/microcosm/packages/{p}/src" for p in PRODUCER_PACKAGES
        ),
        # The scorecard checkout backfill.py was baked from at `modal deploy`
        # time; merge() refuses partials that mix driver revisions (blocker 4).
        "RV_DRIVER_COMMIT": driver_ref,
    }
    proc = subprocess.run(
        [
            "python",
            "/root/backfill.py",
            "--release-id",
            release_id,
            "--workdir",
            workdir,
            "--producer-commit",
            producer_commit,
        ],
        env=env,
    )
    volume.commit()  # keep partials even on failure so a re-spawn resumes
    proc.check_returncode()

    artifact = json.loads(Path(workdir, "reform_validation.json").read_text())
    n_rows = len(artifact["reforms"])
    # Bind the compute environment into the attestation backfill.py started
    # (blocker 6): which Modal app/call/image and producer ref actually
    # produced this artifact. Defensive getattr — the call-id accessor has
    # moved across Modal client versions.
    call_id = ""
    for getter in ("current_function_call_id", "current_call_id"):
        fn = getattr(modal, getter, None)
        if callable(fn):
            try:
                call_id = fn() or ""
            except Exception:
                call_id = ""
            break
    att = artifact.setdefault("_attestation", {})
    att.update(
        {
            "modal_app": APP_NAME,
            # Real, container-populated identifiers only. The old `modal_image_id`
            # read MODAL_IMAGE_ID, which the pinned client never sets (always
            # ""), so it was a forged-provenance no-op — dropped (blocker 6).
            "modal_call_id": call_id or os.environ.get("MODAL_TASK_ID", ""),
            "modal_task_id": os.environ.get("MODAL_TASK_ID", ""),
            "producer_ref": producer_ref,
            "driver_ref": driver_ref,
        }
    )
    with open(f"/vol/reform_validation_{release_id}.json", "w") as f:
        json.dump(artifact, f, indent=1)
    volume.commit()
    print(
        f"published {n_rows} rows for {release_id} (producer {producer_commit})",
        flush=True,
    )
    return f"{n_rows} rows"
