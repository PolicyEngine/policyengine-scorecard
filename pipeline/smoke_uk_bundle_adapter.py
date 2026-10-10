"""Sequential, offline adapter observations; never fiscal-event results."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pipeline import compute_uk_event as compute
from pipeline import uk_bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output_dir.resolve()
    checks = (compute.ROOT / ".venv-replay-checks").resolve()
    if not output.is_relative_to(checks):
        raise ValueError("adapter receipts must be under ignored .venv-replay-checks")
    if args.bundle == uk_bundle.DEFAULT_BUNDLE:
        raise ValueError(
            "this smoke check requires an explicitly selected development bundle"
        )
    pin = uk_bundle.load_bundle(args.bundle)
    first, last = uk_bundle.bundle_window(pin)
    if not first <= args.year <= last:
        raise ValueError("smoke year outside bundle window")
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    pre = compute.preflight(args.bundle)
    (output / "PREFLIGHT.json").write_bytes(compute.canonical_bytes(pre))
    observations = {}
    reform = {
        "gov.hmrc.income_tax.allowances.personal_allowance.amount": {
            f"{args.year}-01-01.{args.year}-12-31": 12571,
        }
    }
    for name, parameters in (("baseline", None), ("dated_reform", reform)):
        print(f"Starting {name} adapter observation", flush=True)
        result = compute.run_sim(args.year, ["income_tax"], parameters, pre)
        observations[name] = result
        (output / f"{name.upper()}.json").write_bytes(compute.canonical_bytes(result))
    effect = (
        observations["dated_reform"]["aggregates_gbp"]["income_tax"]
        - observations["baseline"]["aggregates_gbp"]["income_tax"]
    )
    if not effect < 0:
        raise RuntimeError("the dated £1 allowance increase did not reduce income tax")
    receipt = {
        "kind": "development_adapter_observation",
        "year": args.year,
        "head_variable": "income_tax",
        "reform": reform,
        "income_tax_change_gbp": effect,
        "runtime_dataset_source_hashed": pre["runtime_dataset_source"],
        "runtime_dataset_source_resolved": str(
            Path(pre["runtime_dataset_source"]).resolve()
        ),
        "dataset_sha256": pre["sha256"],
        "data_year": pin["data_year"],
        "runtime_network_blocked": pre["runtime_network_blocked"],
        "wall_seconds": time.perf_counter() - started,
        "inputs_and_observations": {
            p.name: compute.fiscal.sha256_file(p)
            for p in sorted(output.glob("*.json"))
            if p.name != "SMOKE_RECEIPT.json"
        },
        **uk_bundle.bundle_identity(args.bundle),
    }
    (output / "SMOKE_RECEIPT.json").write_bytes(compute.canonical_bytes(receipt))
    print(json.dumps(receipt, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
