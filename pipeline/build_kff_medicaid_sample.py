"""Build the deterministic 5,000-household Medicaid validation sample.

The source is the certified managed dataset resolved by policyengine.py.  The
output is a local, unmanaged derivative used only to exercise the complete
baseline/reform path before the full-file runs; it is never staged as a
certified result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from policyengine.provenance.dataset_sources import materialize_dataset_source
from policyengine.provenance.manifest import (
    resolve_local_managed_dataset_source,
    resolve_managed_dataset_reference,
)

HOUSEHOLDS = 5_000
SEED = 20_260_818
CHUNK_SIZE = 25_000
GROUPS = ("tax_unit", "spm_unit", "family", "marital_unit")


def filtered_chunks(
    store: pd.HDFStore, key: str, column: str, ids: set
) -> pd.DataFrame:
    pieces = []
    for chunk in store.select(key, chunksize=CHUNK_SIZE):
        selected = chunk[chunk[column].isin(ids)]
        if not selected.empty:
            pieces.append(selected)
    if not pieces:
        raise ValueError(f"no {key} rows selected on {column}")
    return pd.concat(pieces, ignore_index=True)


def build(source: Path, output: Path) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with pd.HDFStore(source, mode="r") as src:
        household_ids = src.select("household", columns=["household_id"])[
            "household_id"
        ].to_numpy()
        total_households = len(household_ids)
        if total_households < HOUSEHOLDS:
            raise ValueError(f"source has only {total_households} households")
        rng = np.random.default_rng(SEED)
        selected_ids = set(
            rng.choice(household_ids, HOUSEHOLDS, replace=False).tolist()
        )
        households = filtered_chunks(src, "household", "household_id", selected_ids)
        people = filtered_chunks(src, "person", "person_household_id", selected_ids)
        membership_ids = {
            group: set(people[f"person_{group}_id"].tolist()) for group in GROUPS
        }
        group_frames = {
            group: filtered_chunks(src, group, f"{group}_id", membership_ids[group])
            for group in GROUPS
        }
        time_period = src.get("_time_period")

    scale = total_households / HOUSEHOLDS
    households["household_weight"] *= scale

    assert len(households) == HOUSEHOLDS
    assert households["household_id"].is_unique
    assert set(households["household_id"]) == selected_ids
    assert set(people["person_household_id"]) == selected_ids
    for group, frame in group_frames.items():
        id_column = f"{group}_id"
        assert frame[id_column].is_unique
        assert set(frame[id_column]) == membership_ids[group]

    with pd.HDFStore(output, mode="w") as dst:
        dst.put("_time_period", time_period, format="table", data_columns=True)
        dst.put("household", households, format="table", data_columns=True)
        dst.put("person", people, format="table", data_columns=True)
        for group, frame in group_frames.items():
            dst.put(group, frame, format="table", data_columns=True)

    metadata = {
        "source": str(source),
        "output": str(output),
        "seed": SEED,
        "households": HOUSEHOLDS,
        "source_households": total_households,
        "household_weight_scale": scale,
        "people": len(people),
        "entities": {
            "household": len(households),
            "person": len(people),
            **{group: len(frame) for group, frame in group_frames.items()},
        },
        "period": 2024,
        "certification_status": "unmanaged_sample_of_certified_artifact",
    }
    Path(f"{output}.metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def managed_source() -> tuple[str, Path]:
    uri = resolve_managed_dataset_reference("us")
    local = resolve_local_managed_dataset_source("us", uri)
    return uri, Path(materialize_dataset_source(local))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/private/tmp/kff_medicaid_sample_5000.h5"),
    )
    args = parser.parse_args()
    uri, resolved = managed_source()
    source = args.source or resolved
    metadata = build(source, args.output)
    metadata["managed_dataset_uri"] = uri
    Path(f"{args.output}.metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
