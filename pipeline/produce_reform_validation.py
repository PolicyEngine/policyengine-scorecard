"""Run microcosm's US post-export probe (reform_validation stage) at
policyengine-us 2.2.1 with the legacy WIC input rename applied.

The certified populace-us-2024-spm-20260915 H5 stores the WIC claim gate as
``would_claim_wic``; policyengine-us 2.x reads ``takes_up_wic_if_eligible``
(monthly, default True). policyengine.py's managed simulation maps the stored
column onto the live input for every month of the year
(``legacy_inputs.apply_legacy_input_renames``); microcosm's loader does not,
so without this every WIC-eligible person would take up WIC. This wrapper
applies the same mapping to every engine the probe builds (baseline, reform
and household batches) by subclassing ``policyengine_us.Microsimulation``
before the probe's local ``from policyengine_us import Microsimulation``
imports run. microcosm itself is not modified.

Usage (from a PolicyEngine/microcosm checkout's venv; MICROCOSM defaults to
../microcosm next to this repo):

    MICROCOSM=~/microcosm ~/microcosm/.venv-rv/bin/python \
      pipeline/produce_reform_validation.py \
      --export data/populace_us_2024.h5 --out <dir> \
      --census --stages reform_validation --batch-size 5000 \
      --release-id populace-us-2024-spm-20260915 \
      --calibration-diagnostics <release calibration_diagnostics.json>

then copy <dir>/reform_validation.json to
sources/populace-reform-validation/raw/<release_id>.json with a
_backfill_note (see the spm-20260915 file).
"""

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import policyengine_us

MICROCOSM = Path(
    os.environ.get(
        "MICROCOSM", Path(__file__).resolve().parent.parent.parent / "microcosm"
    )
).expanduser()
TOOLS = MICROCOSM / "tools"
LEGACY, LIVE = "would_claim_wic", "takes_up_wic_if_eligible"
_Base = policyengine_us.Microsimulation
_applied = {"engines": 0}


def _dataset_of(args, kwargs):
    return kwargs.get("dataset", args[0] if args else None)


class Microsimulation(_Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dataset = _dataset_of(args, kwargs)
        person = getattr(dataset, "person", None)
        if person is None or LEGACY not in person.columns:
            return
        if LIVE not in self.tax_benefit_system.variables:
            return
        if LIVE in person.columns:
            return  # the dataset already carries the live input
        year = int(dataset.time_period)
        sim_ids = np.asarray(self.calculate("person_id", year).values)
        if not np.array_equal(sim_ids, person["person_id"].to_numpy()):
            raise ValueError(f"cannot map {LEGACY!r}: person order differs")
        values = person[LEGACY].to_numpy()
        if values.dtype != bool:
            if not np.isin(values, [0, 1]).all():
                raise ValueError(f"{LEGACY!r} holds non-boolean values")
            values = values.astype(bool)
        for month in range(1, 13):
            self.set_input(LIVE, f"{year}-{month:02d}", values)
        _applied["engines"] += 1


policyengine_us.Microsimulation = Microsimulation

sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location(
    "probe_us_post_export", TOOLS / "probe_us_post_export.py"
)
probe = importlib.util.module_from_spec(spec)
sys.modules["probe_us_post_export"] = probe
spec.loader.exec_module(probe)

if __name__ == "__main__":
    code = probe.main(sys.argv[1:])
    print(
        f"[produce_reform_validation] WIC legacy rename applied to {_applied['engines']} engines"
    )
    sys.exit(code)
