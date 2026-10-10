"""Record the difference between two executed replay artifacts as a paired run.

A paired-run document binds one measure-year's artifact in each of two bundles
by path and SHA-256, and states their difference for the whole measure or for
named heads. ``compare_uk_engines`` accepts it as sized attribution evidence
only when both endpoints are in verified run manifests. This tool computes
nothing new: it reads two existing artifacts and subtracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pipeline import uk_bundle as bundles
from pipeline.compare_uk_obr_costings import atomic_write_bytes

ROOT = bundles.ROOT
PAIRS = Path("results/uk/events/engine_pairs")


def canonical_bytes(value) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=1, allow_nan=False) + "\n"
    ).encode()


def artifact_reference(event: str, measure_key: str, year: int, bundle: str, root):
    path = (
        bundles.event_output_dir(event, bundle, root=root)
        / f"{measure_key}_{year}.json"
    )
    if not path.is_file():
        raise ValueError(f"no executed artifact for {measure_key} {year} in {bundle}")
    return path


def paired_run(
    event: str,
    measure_key: str,
    year: int,
    base_bundle: str,
    new_bundle: str,
    *,
    heads: list[str] | None = None,
    root: Path = ROOT,
) -> dict:
    """The new-minus-base effect of one measure-year, with both endpoints bound."""
    if base_bundle == new_bundle:
        raise ValueError("a paired run needs two different bundles")
    if heads is not None and (not heads or len(heads) != len(set(heads))):
        raise ValueError("heads must be unique and nonempty")
    document = {
        "artifact_type": "paired_run",
        "status": "computed",
        "event": event,
        "measure_key": measure_key,
        "year": year,
    }
    effects = {}
    for side, bundle in (("base", base_bundle), ("new", new_bundle)):
        path = artifact_reference(event, measure_key, year, bundle, root)
        payload = path.read_bytes()
        artifact = json.loads(payload)
        bundles.validate_runtime_bundle(artifact, bundle, root=root)
        if (
            artifact.get("event"),
            artifact.get("measure_key"),
            artifact.get("year"),
        ) != (
            event,
            measure_key,
            year,
        ):
            raise ValueError(
                "artifact identity differs from the requested measure-year"
            )
        try:
            effects[side] = (
                artifact["measure_total_gbp"]
                if heads is None
                else sum(artifact["head_effects"][head] for head in heads)
            )
        except KeyError as error:
            raise ValueError(f"{side} artifact lacks head {error}") from error
        document[side + "_bundle"] = bundle
        document[side + "_artifact"] = {
            "path": str(path.resolve().relative_to(Path(root).resolve())),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    if heads is not None:
        document["head_variables"] = list(heads)
    document["effect_gbp"] = effects["new"] - effects["base"]
    return document


def default_output(document: dict, *, root: Path = ROOT) -> Path:
    scope = "__".join(document.get("head_variables", ["measure_total"]))
    return (
        Path(root)
        / PAIRS
        / f"{document['base_bundle']}__{document['new_bundle']}"
        / f"{document['measure_key']}_{document['year']}__{scope}.json"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True)
    parser.add_argument("--measure", required=True)
    parser.add_argument("--years", required=True, nargs="+", type=int)
    parser.add_argument("--base-bundle", required=True)
    parser.add_argument("--new-bundle", required=True)
    parser.add_argument("--heads", nargs="+")
    args = parser.parse_args(argv)
    for year in args.years:
        document = paired_run(
            args.event,
            args.measure,
            year,
            args.base_bundle,
            args.new_bundle,
            heads=args.heads,
        )
        output = default_output(document)
        output.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_bytes(output, canonical_bytes(document))
        print(f"{output.relative_to(ROOT)}: {document['effect_gbp']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
