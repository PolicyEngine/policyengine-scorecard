"""Inspect pinned SDLT/CGT source and certified input fields without an engine.

Only h5py/numpy read the population. The certified bytes are verified before
opening HDF5; no policyengine package or simulation is imported or constructed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RANGES = {
    "policyengine_uk/variables/gov/hmrc/sdlt_on_residential_property_transactions.py": [
        (13, 38)
    ],
    "policyengine_uk/variables/household/consumption/additional_residential_property_purchased.py": [
        (4, 17)
    ],
    "policyengine_uk/variables/input/consumption/property/property_purchased.py": [
        (4, 18)
    ],
    "policyengine_uk/variables/input/other_residential_property_value.py": [(4, 17)],
    "policyengine_uk/variables/gov/hmrc/stamp_duty_land_tax.py": [(4, 16)],
    "policyengine_uk/variables/gov/hmrc/sdlt_liable.py": [(12, 18)],
    "policyengine_uk/variables/gov/hmrc/capital_gains_tax/capital_gains_tax.py": [
        (12, 57)
    ],
    "policyengine_uk/variables/household/income/capital_gains.py": [(6, 15)],
    "policyengine_uk/variables/gov/hmrc/capital_gains_tax/capital_gains_behavioural_response.py": [
        (12, 28)
    ],
    "policyengine_uk/parameters/gov/simulation/capital_gains_responses/elasticity.yaml": [
        (1, 6)
    ],
    "policyengine_uk/simulation.py": [(191, 208), (440, 455), (495, 501), (548, 563)],
    "policyengine_uk/data/dataset_schema.py": [(153, 174)],
    "policyengine_uk/data/economic_assumptions.py": [(35, 52), (80, 112)],
    "policyengine_uk/data/uprating_indices.yaml": [(58, 76)],
    "policyengine/tax_benefit_models/uk/model.py": [(280, 330)],
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_dataset(path: Path, bundle: dict) -> dict:
    """Refuse a different population before any HDF5 opening or reading."""
    size = path.stat().st_size
    if size != bundle["size_bytes"]:
        raise ValueError("dataset size differs from the certified bundle")
    digest = sha256_file(path)
    if digest != bundle["sha256"]:
        raise ValueError("dataset SHA-256 differs from the certified bundle")
    return {
        "artifact": bundle["artifact"],
        "revision": bundle["revision"],
        "sha256": digest,
        "size_bytes": size,
        "digest_checked_before_hdf5_open": True,
    }


def package_version(site_packages: Path, distribution: str) -> str:
    directories = list(
        site_packages.glob(f"{distribution.replace('-', '_')}-*.dist-info")
    )
    if len(directories) != 1:
        raise ValueError(f"expected one installed {distribution} distribution")
    for line in (directories[0] / "METADATA").read_text().splitlines():
        if line.startswith("Version: "):
            return line.removeprefix("Version: ")
    raise ValueError(f"missing {distribution} version metadata")


def source_evidence(site_packages: Path) -> list[dict]:
    evidence = []
    for relative, ranges in SOURCE_RANGES.items():
        path = site_packages / relative
        raw = path.read_bytes()
        source = raw.decode()
        lines = source.splitlines(keepends=True)
        evidence.append(
            {
                "file": relative,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "excerpts": [
                    {
                        "start_line": start,
                        "end_line": end,
                        "source": "".join(lines[start - 1 : end]),
                    }
                    for start, end in ranges
                ],
            }
        )
    return evidence


def inspect_h5(path: Path) -> dict:
    """Read field names and aggregates, never individual household records."""
    import h5py
    import numpy as np

    with h5py.File(path, "r") as data:
        household = data["household/table"]
        person = data["person/table"]
        columns = {
            "household": list(household.dtype.names),
            "person": list(person.dtype.names),
        }
        fields = [
            "property_purchased",
            "other_residential_property_value",
            "household_weight",
            "household_is_capital_gains_clone",
        ]
        values = household.fields(fields)[()]
        purchased = values["property_purchased"].astype(bool)
        stock = values["other_residential_property_value"]
        weights = values["household_weight"]
        household_aggregates = {
            "property_purchased_true_rows": int(purchased.sum()),
            "property_purchased_true_weighted_households": float(
                weights[purchased].sum()
            ),
            "other_property_positive_rows": int((stock > 0).sum()),
            "purchased_and_other_property_positive_rows": int(
                (purchased & (stock > 0)).sum()
            ),
            "other_property_stock_weighted_gbp": float(np.dot(stock, weights)),
            "other_property_stock_gated_by_purchase_weighted_gbp": float(
                np.dot(stock * purchased, weights)
            ),
            "weighted_households": float(weights.sum()),
            "other_property_nonfinite_rows": int((~np.isfinite(stock)).sum()),
            "capital_gains_clone_household_rows": int(
                values["household_is_capital_gains_clone"].sum()
            ),
        }
        del values
        gains = person.fields("capital_gains")[()]
        return {
            "time_period": data["time_period/table"][()]["values"][0].decode(),
            "entity_rows": {"household": len(household), "person": len(person)},
            "input_columns": columns,
            "household_aggregates": household_aggregates,
            "capital_gains_input_rows": {
                "positive": int((gains > 0).sum()),
                "negative": int((gains < 0).sum()),
                "nonfinite": int((~np.isfinite(gains)).sum()),
            },
        }


def collect_audit(dataset: Path, site_packages: Path, bundle: dict) -> dict:
    identity = verify_dataset(dataset, bundle)
    versions = {
        package: package_version(site_packages, package)
        for package in ("policyengine", "policyengine-uk", "policyengine-core")
    }
    if versions != {
        "policyengine": "5.0.2",
        "policyengine-uk": "2.89.2",
        "policyengine-core": "3.27.1",
    }:
        raise ValueError("construction audit requires the pinned replay packages")
    evidence = source_evidence(site_packages)
    observations = inspect_h5(dataset)
    return {
        "schema_version": 1,
        "method": "Engine-free source reading and HDF5 aggregate inspection; no simulation.",
        "inspection_script": {
            "path": "pipeline/audit_uk_event_constructions.py",
            "sha256": sha256_file(Path(__file__)),
        },
        "packages": versions,
        "certified_dataset": identity,
        "observations": observations,
        "source_evidence": evidence,
        "construction_limits": [
            {
                "id": "sdlt_flagged_stock_transaction_proxy",
                "variables": [
                    "property_purchased",
                    "other_residential_property_value",
                    "additional_residential_property_purchased",
                ],
                "finding": "The bundle supplies property stock and a purchase flag, but no direct main/additional purchase prices. Additional purchase price is stock multiplied by that flag. This is a transaction-price proxy; full stock is not taxed unconditionally.",
                "annual_projection": "Population extension copies the purchase flag; per-capita GDP uprating grows property values. There is no annual purchaser resampling in this path.",
                "aggregate_scope": "Base-year raw input aggregates precede SDLT geography, minimum-price thresholds, annual uprating and reform aggregation. Raw row counts include capital-gains clones.",
                "divergence_axes": [
                    "construction_scope",
                    "head_scope",
                    "population_vintage",
                ],
                "national_contribution": "unsized",
            },
            {
                "id": "cgt_pooled_gain_types_and_zero_elasticity",
                "variables": [
                    "capital_gains",
                    "capital_gains_before_response",
                    "capital_gains_behavioural_response",
                    "capital_gains_tax",
                ],
                "finding": "The tax formula applies the main CGT rate schedule to one pooled gains amount, with no asset-type, BADR, Investors' Relief or carried-interest branch. The bundle has one capital_gains input. The loader moves it to before_response; the default zero elasticity makes the response formula return zero.",
                "annual_projection": "Both capital_gains and capital_gains_before_response are uprated by per-capita GDP. No gain-type allocation is supplied by this path.",
                "divergence_axes": [
                    "construction_scope",
                    "head_scope",
                    "behavioural_adjustment",
                    "population_vintage",
                ],
                "national_contribution": "unsized",
            },
        ],
        "interpretation": "These observations document construction and data-flow limits. They do not establish national model errors, causal residual amounts or an explained share. No new model diagnostic is asserted.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument(
        "--site-packages", type=Path, default=Path(sysconfig.get_paths()["purelib"])
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/uk/events/CONSTRUCTION_AUDIT.json",
    )
    args = parser.parse_args()
    bundle = json.loads((ROOT / "data/uk/certified_bundle.json").read_text())
    audit = collect_audit(args.dataset, args.site_packages, bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(audit, indent=1, sort_keys=True, allow_nan=False) + "\n"
    )
    print(f"Wrote engine-free audit: {args.output}")


if __name__ == "__main__":
    main()
