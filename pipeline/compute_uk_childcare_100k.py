"""PolicyEngine counterparts for the £100,000 childcare limit costings.

Two external scores cost removing the £100,000 adjusted-net-income limit on
the working-parent childcare offers in England:

    sources/centax-childcare-100k   CenTax (Advani, Flew, Pepin-Hall and
                                    Summers, September 2026), Table 4.2:
                                    the free hours only
    sources/cbp-rates-and-wrongs    Centre for British Progress (25 March
                                    2026), technical appendix Tables 2-3:
                                    the free hours and Tax-Free Childcare

This script runs the managed policyengine-uk simulation on the certified
populace-uk bundle (the default replay variant, data/uk/certified_bundle.json)
through the same preflight as the variant's event replays
(pipeline/compute_uk_event.py), and writes one artifact with weighted SUMS
and COUNTS per world and year, UK-wide and for people in English households.
Every ratio and delta is derived downstream
(scorecard_db/ingest_uk_childcare_100k.py).

Worlds (static: no behavioural response is applied):

    baseline            the certified world as served (current law)
    free_hours          the 30-hours limit removed
                        (gov.dfe.extended_childcare_entitlement.income.limit)
    free_hours_and_tfc  both limits removed (also
                        gov.hmrc.tax_free_childcare.income.income_limit)

A removed limit executes as compute_uk_ab2025.NO_LIMIT (1e100), the repo's
sentinel for "no limit" in a policyengine-core reform dict; the artifact
records the executed value of each limit in each world and year.

Diagnostic worlds (2027 and 2029 by default): baseline and free_hours with
the input ``maximum_extended_childcare_hours_usage`` set to 30 for every
benefit unit in every simulated year, before any calculation (the engine's
own default for the variable, i.e. full use of the 30 hours). They measure
how much of the static cost turns on the dataset's hours-usage draw
(microcosm#1126); they are never attached to a claim.

Offline and pinned, through compute_uk_event's preflight for the variant
(the legacy one or a materialised one): the installed wheels checked
against the variant record before the engine is imported (versions, RECORD
hashes, the packaged bundle manifest, Python), each engine package imported
from its own distribution, Hugging Face offline mode, and the runtime
release bundle equal to the record's. Each simulation must report as its
runtime_dataset_source the exact file hashed against the certified bundle
immediately before construction, and that file is hashed again after the
world's reads. One artifact per variant; ingest keeps every certified
variant's run in the history.

    PYTHONPATH=. .venv-pe289m/bin/python pipeline/compute_uk_childcare_100k.py
    PYTHONPATH=. <that variant's venv>/bin/python pipeline/compute_uk_childcare_100k.py --variant <id>
"""

from __future__ import annotations

import argparse
import datetime as dt
import gc
import inspect
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import compute_uk_ab2025 as ab
from pipeline import compute_uk_event as event
from pipeline import compute_uk_obr_costings as fiscal
from pipeline import uk_replay_variants as variants

OUTPUT_DIR = ROOT / "results" / "uk" / "childcare_100k"
YEARS = (2026, 2027, 2028, 2029, 2030)
DIAGNOSTIC_YEARS = (2027, 2029)

THIRTY_HOURS_LIMIT = "gov.dfe.extended_childcare_entitlement.income.limit"
TFC_LIMIT = "gov.hmrc.tax_free_childcare.income.income_limit"
LIMITS = (THIRTY_HOURS_LIMIT, TFC_LIMIT)
REFORMS = {
    "free_hours": (THIRTY_HOURS_LIMIT,),
    "free_hours_and_tfc": (THIRTY_HOURS_LIMIT, TFC_LIMIT),
}
HOURS_USAGE = "maximum_extended_childcare_hours_usage"
FULL_USE_HOURS = 30.0
# Benefit-unit take-up inputs (each offer's eligibility is defined_for one;
# the engine's default is True).
TAKE_UP = (
    "would_claim_extended_childcare",
    "would_claim_universal_childcare",
    "would_claim_targeted_childcare",
    "would_claim_tfc",
)
# Inputs whose presence in the dataset is recorded: holder periods filled at
# construction, before any calculation, are the dataset's own values.
DATASET_INPUTS = (HOURS_USAGE, *TAKE_UP, "childcare_expenses")

# The three free early-years entitlements (policyengine-uk's gov_spending
# lists all three) and Tax-Free Childcare.
FREE_HOURS = (
    "extended_childcare_entitlement",
    "universal_childcare_entitlement",
    "targeted_childcare_entitlement",
)
TFC = "tax_free_childcare"
SUMMED = (*FREE_HOURS, TFC, "gov_spending", "gov_tax")
# Both offers are England's, but policyengine-uk 2.89.2 applies Tax-Free
# Childcare UK-wide (only the extended hours test country == ENGLAND), so
# the childcare heads are also summed for people in English households.
HEADS = (*FREE_HOURS, TFC)
ENGLAND = "ENGLAND"
# Variables whose engine metadata is recorded (the pe_meta contract): every
# variable year_block calculates.
METADATA = (
    *SUMMED,
    HOURS_USAGE,
    "is_child",
    "is_child_receiving_extended_childcare",
    "country",
    *TAKE_UP,
    "childcare_expenses",
    "max_free_entitlement_hours_used",
    "extended_childcare_entitlement_eligible",
    "extended_childcare_entitlement_meets_income_requirements",
    "universal_childcare_entitlement_eligible",
    "targeted_childcare_entitlement_eligible",
    "tax_free_childcare_meets_income_requirements",
    "adjusted_net_income",
    "age",
)


def worlds(years) -> dict[str, dict | None]:
    """name -> executed reform dict (None: the certified world as served)."""
    out: dict[str, dict | None] = {"baseline": None}
    for name, paths in REFORMS.items():
        rd, sentinels = ab.reform_dict({p: None for p in paths}, years=list(years))
        if sorted(sentinels) != sorted(paths):
            raise SystemExit(f"{name}: sentinel paths {sentinels} != {paths}")
        out[name] = rd
    return out


def variable_metadata(system) -> dict:
    out = {}
    for name in METADATA:
        v = system.variables[name]
        source = inspect.getsourcefile(type(v)) or ""
        out[name] = {
            "label": v.label,
            "entity": v.entity.key,
            "definition_period": str(v.definition_period),
            "unit": str(getattr(v, "unit", None)),
            "documentation": v.documentation,
            "defined_for": str(getattr(v, "defined_for", None) or "") or None,
            "default_value": v.default_value
            if isinstance(v.default_value, (int, float, bool, str))
            else None,
            "engine_source": "policyengine_uk/"
            + source.split("/policyengine_uk/", 1)[-1]
            if "/policyengine_uk/" in source
            else source,
        }
    return out


def _weighted(series) -> tuple[np.ndarray, np.ndarray]:
    return np.asarray(series.values, dtype=float), np.asarray(
        series.weights, dtype=float
    )


def _share(series) -> float:
    values, weights = _weighted(series)
    return float((values * weights).sum() / weights.sum())


def limit_values(sim, year: int) -> dict[str, float]:
    params = sim.tax_benefit_system.parameters
    out = {}
    for path in LIMITS:
        node = ab._resolve_parameter(params, path)
        out[path] = float(node(f"{year}-04-30"))
    return out


def england_masks(sim, year: int) -> dict[str, np.ndarray]:
    """entity key -> True where the household is in England.

    country is a household variable; core's map_result projects it onto
    each member (household -> person), and a benefit unit lies inside one
    household, so any member gives its country (person -> benunit)."""
    country = np.asarray(sim.calculate("country", year).values)
    unknown = set(np.unique(country)) - {
        "ENGLAND",
        "NORTHERN_IRELAND",
        "SCOTLAND",
        "WALES",
    }
    if unknown or ENGLAND not in set(country):
        raise SystemExit(f"{year}: unexpected country values {sorted(unknown)}")
    person = np.asarray(
        sim.map_result(country == ENGLAND, "household", "person"), dtype=bool
    )
    benunit = np.asarray(
        sim.map_result(person, "person", "benunit", how="any"), dtype=bool
    )
    if not np.array_equal(
        person, np.asarray(sim.map_result(benunit, "benunit", "person"), dtype=bool)
    ):
        raise SystemExit(f"{year}: a benefit unit spans two countries")
    return {"person": person, "benunit": benunit}


def england_sums(sim, year: int, masks: dict[str, np.ndarray]) -> dict[str, float]:
    out = {}
    for v in HEADS:
        values, weights = _weighted(sim.calculate(v, year))
        mask = masks[sim.tax_benefit_system.variables[v].entity.key]
        out[v] = float((values * weights)[mask].sum())
    return out


def year_block(sim, year: int) -> dict:
    """Weighted sums and counts for one world and year (microdf weights)."""
    sums = {v: float(sim.calculate(v, year).sum()) for v in SUMMED}
    masks = england_masks(sim, year)
    ext, w_bu = _weighted(sim.calculate("extended_childcare_entitlement", year))
    hours, _ = _weighted(sim.calculate(HOURS_USAGE, year))
    receiving = ext > 0
    age, w_p = _weighted(sim.calculate("age", year))
    is_child = np.asarray(sim.calculate("is_child", year).values, dtype=bool)
    universal, _ = _weighted(sim.calculate("universal_childcare_entitlement", year))
    targeted, _ = _weighted(sim.calculate("targeted_childcare_entitlement", year))
    tfc, _ = _weighted(sim.calculate(TFC, year))
    extended_child = np.asarray(
        sim.calculate("is_child_receiving_extended_childcare", year).values,
        dtype=bool,
    )
    under_one = is_child & (age < 1)
    fractional_age = np.abs(age - np.round(age)) > 1e-9
    return {
        "sums_gbp": sums,
        "sums_gbp_england": england_sums(sim, year, masks),
        "counts": {
            "benunits_receiving_extended": float(w_bu[receiving].sum()),
            "children_receiving_extended": float(w_p[extended_child].sum()),
            "children_receiving_universal": float(w_p[universal > 0].sum()),
            "children_receiving_targeted": float(w_p[targeted > 0].sum()),
            "people_receiving_tfc": float(w_p[tfc > 0].sum()),
            "people_receiving_tfc_england": float(
                w_p[(tfc > 0) & masks["person"]].sum()
            ),
            "children_under_one": float(w_p[under_one].sum()),
            "children_under_one_receiving_extended": float(
                w_p[under_one & extended_child].sum()
            ),
            "people_with_fractional_age": float(w_p[fractional_age].sum()),
        },
        # weighted share of benefit units with each take-up input True
        "take_up": {v: _share(sim.calculate(v, year)) for v in TAKE_UP},
        "hours_usage": {
            "mean_all_benunits": float((hours * w_bu).sum() / w_bu.sum()),
            "mean_benunits_receiving_extended": float(
                (hours[receiving] * w_bu[receiving]).sum() / w_bu[receiving].sum()
            )
            if receiving.any()
            else None,
        },
        "limits_executed": limit_values(sim, year),
        "records": {
            "benunits_receiving_extended": int(receiving.sum()),
        },
    }


def set_full_use(sim, years) -> dict[int, float]:
    """Set the hours-usage input to full use in every simulated year before
    anything that reads it is calculated; return the post-set weighted mean
    per requested year and the (empty) dependent holders checked first."""
    # Nothing that reads the input may have been calculated yet, or the
    # override would not reach it: every dependent holder must be empty.
    computed = {
        v: [str(p) for p in sim.get_holder(v).get_known_periods()]
        for v in (*FREE_HOURS, "extended_childcare_entitlement_eligible")
    }
    if any(computed.values()):
        raise SystemExit(f"calculated before the override: {computed}")
    dataset_years = sorted(int(y) for y in sim.dataset.years)
    # the entity count, read without any calculation
    n = sim.populations["benunit"].count
    for y in dataset_years:
        sim.set_input(HOURS_USAGE, y, np.full(n, FULL_USE_HOURS))
    out = {"dependents_calculated_before_override": computed}
    for y in years:
        h, w = _weighted(sim.calculate(HOURS_USAGE, y))
        out[y] = float((h * w).sum() / w.sum())
        if not np.allclose(h, FULL_USE_HOURS):
            raise SystemExit(f"{HOURS_USAGE} override did not take effect in {y}")
    return out


def dataset_inputs(sim) -> dict[str, list[str]]:
    """input -> the periods the dataset filled, read before any calculation."""
    return {
        v: sorted(str(p) for p in sim.get_holder(v).get_known_periods())
        for v in DATASET_INPUTS
    }


def check_runtime(sim, name: str, pre: dict) -> list[int]:
    """The simulation read the hashed file, under the certified bundle, with
    the record's data years; returns those years."""
    bundle = dict(getattr(sim, "policyengine_bundle", {}) or {})
    reported = bundle.get("runtime_dataset_source")
    source = Path(pre["runtime_dataset_source"])
    if not isinstance(reported, str) or Path(reported).resolve() != source.resolve():
        raise SystemExit(
            f"{name}: the managed simulation read {reported!r}, not the file "
            f"hashed before construction ({source})"
        )
    fiscal.assert_managed_bundle(bundle, pre["release_bundle"])
    dataset_years = sorted(int(y) for y in sim.dataset.years)
    if dataset_years != pre["data_years"]:
        raise SystemExit(
            f"{name}: dataset years {dataset_years} != the variant's {pre['data_years']}"
        )
    return dataset_years


def run_world(name: str, reform, years, pre: dict, *, full_use: bool = False):
    t0 = time.perf_counter()
    source = Path(pre["runtime_dataset_source"])
    before = fiscal.verify_runtime_dataset_sha256(
        source, pre["sha256"], phase=f"{name}: immediately before construction"
    )
    sim = ab.build_sim(reform)
    dataset_years = check_runtime(sim, name, pre)
    supplied = dataset_inputs(sim)
    check = set_full_use(sim, years) if full_use else None
    blocks = {str(y): year_block(sim, y) for y in years}
    metadata = variable_metadata(sim.tax_benefit_system)
    after = fiscal.verify_runtime_dataset_sha256(
        source,
        pre["sha256"],
        phase=f"{name}: after the world's reads",
        before_sha256=before,
    )
    del sim
    gc.collect()
    print(f"{name}: {len(years)} years in {time.perf_counter() - t0:.0f}s", flush=True)
    out = {
        "reform_dict": reform,
        "years": blocks,
        "runtime_dataset_source": fiscal.relative_to_root(source),
        "dataset_sha256_before": before,
        "dataset_sha256_after": after,
        "dataset_years": dataset_years,
        "dataset_inputs": supplied,
    }
    if full_use:
        out["input_override"] = {
            "variable": HOURS_USAGE,
            "value": FULL_USE_HOURS,
            "set_for_years": dataset_years,
            "dependents_calculated_before_override": check.pop(
                "dependents_calculated_before_override"
            ),
            "post_set_weighted_mean": {str(k): v for k, v in check.items()},
        }
    return out, metadata


def default_run_id(variant_id: str, started: dt.datetime) -> str:
    """Distinct across variants, and across one variant's runs started in
    different seconds. Ingest refuses two artifacts that share a run_id."""
    return f"childcare-100k-{variant_id}-{started:%Y%m%dT%H%M%SZ}"


def main(argv: list[str] | None = None) -> int:
    started = dt.datetime.now(dt.timezone.utc)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--years", nargs="*", type=int, default=list(YEARS))
    ap.add_argument(
        "--diagnostic-years", nargs="*", type=int, default=list(DIAGNOSTIC_YEARS)
    )
    ap.add_argument(
        "--run-id", help="default: childcare-100k-<variant>-<UTC start second>"
    )
    ap.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    ap.add_argument(
        "--variant",
        help="a certified variant in data/uk/replay_variants.json (default: its default)",
    )
    ap.add_argument(
        "--dataset-file",
        type=Path,
        help="a local file holding a materialised variant's certified dataset bytes",
    )
    args = ap.parse_args(argv)
    # absolute before a variant preflight moves into its runtime directory
    args.output_dir = args.output_dir.resolve()

    variant = variants.get_variant(args.variant)
    run_id = args.run_id or default_run_id(variant["variant_id"], started)
    missing = sorted(
        (set(args.years) | set(args.diagnostic_years)) - set(variant["data_years"])
    )
    if missing:
        # a year outside the dataset calculates defaults without raising
        raise SystemExit(f"{missing} are outside {variant['variant_id']}'s data years")
    if variants.is_legacy(variant):
        if args.dataset_file is not None:
            raise SystemExit("the legacy variant reads its pinned Hugging Face cache")
        # Engine-free and before any engine import: the record is certified
        # and the installed wheels are its own. Then the event runner's
        # legacy preflight: offline, isolated, the managed release equal to
        # certified_bundle.json and to the record, import origins checked,
        # and a verified writable mirror that POLICYENGINE_UK_DATA_REPO
        # points at.
        installed = event.check_variant_environment(variant)
        pre = {
            **event.preflight(variant),
            "data_years": list(variant["data_years"]),
        }
    else:
        # The same checks for a variant whose dataset is materialised into
        # its runtime directory (the event runner's variant preflight).
        pre = event.variant_preflight(
            variant,
            dataset_source=args.dataset_file.resolve() if args.dataset_file else None,
        )
        installed = pre["installed"]
    revision = fiscal.data_bundle_id(pre["release_bundle"])
    identity = variant["identity"]
    if (revision, pre["sha256"]) != (
        identity["dataset"]["revision"],
        identity["dataset"]["sha256"],
    ):
        raise SystemExit("the managed release and the variant's record disagree")
    print(
        f"certified artifact {revision} sha256 verified at "
        f"{fiscal.relative_to_root(Path(pre['runtime_dataset_source']))}",
        flush=True,
    )
    executed = worlds(args.years)
    out_worlds = {}
    metadata = None
    for name, reform in executed.items():
        out_worlds[name], metadata = run_world(name, reform, args.years, pre)
    diag = {}
    if args.diagnostic_years:
        dworlds = worlds(args.diagnostic_years)
        for name in ("baseline", "free_hours"):
            diag[f"{name}__full_use_hours"], _ = run_world(
                f"{name}__full_use_hours",
                dworlds[name],
                args.diagnostic_years,
                pre,
                full_use=True,
            )
    variants.verify_import_origins()
    packages = {
        p: {
            "version": installed["packages"][p]["version"],
            "record_sha256": installed["packages"][p]["record_sha256"],
        }
        for p in variants.PACKAGES
    }
    artifact = {
        "schema_version": 2,
        "run_id": run_id,
        "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "variant_id": variant["variant_id"],
        "variant_identity_sha256": variant["identity_sha256"],
        "engine_version": packages["policyengine-uk"]["version"],
        "packages": packages,
        "python": installed["python"],
        "packaged_bundle_manifest_sha256": installed["packaged_bundle_manifest_sha256"],
        "release_bundle": pre["release_bundle"],
        "data_bundle": revision,
        "dataset": {
            "repo_id": identity["dataset"]["repo_id"],
            "revision": revision,
            "sha256": pre["sha256"],
            "hf_commit": variants_hf_commit() if variants.is_legacy(variant) else None,
        },
        "years": args.years,
        "fy_rule": "PE year Y is fiscal year Y-(Y+1): policyengine_uk/utils/parameters.py convert_to_fiscal_year_parameters sets every gov parameter for year Y to its 30 April Y value",
        "limit_sentinel": ab.NO_LIMIT,
        "behavioural_response": "none (static)",
        "worlds": out_worlds,
        "diagnostics": diag,
        "variable_metadata": metadata,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / f"{variant['variant_id']}.json"
    path.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n")
    print(f"wrote {path.relative_to(ROOT)}")
    return 0


def variants_hf_commit() -> str:
    from pipeline import modal_uk_event

    return modal_uk_event.HF_COMMIT


if __name__ == "__main__":
    sys.exit(main())
