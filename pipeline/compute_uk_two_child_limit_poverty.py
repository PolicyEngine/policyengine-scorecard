"""PolicyEngine counterparts for the two-child limit poverty benchmarks
(lane uk-two-child-limit-poverty).

The benchmarks (sources/dwp-two-child-limit-poverty, sources/rf-no-half-measures
and the HM Treasury costings already in the AB2025 registry) score removing
the Universal Credit two-child limit against a world that keeps it. The
certified engine already removes it from 6 April 2026, so the comparison is
run as two managed simulations on the certified pair:

    with_limit    the certified world with
                  gov.dwp.universal_credit.elements.child.limit.child_count
                  set to 2 (the sources' baseline)
    current_law   the certified world as served (the limit removed)

plus two worlds for single claims: ``three_child_limit`` (the count set to 3,
RF's partial-repeal option) and ``removed_2025`` (the limit removed in
2025-26, for RF's "330,000 today" and DWP's FYE 2026 figure, when current
law still applies it).

Each world-year records weighted counts only, for every concept the sources
use, so the stager chooses the counterpart and derives every difference:

- populations: people, HBAI dependent children (is_hbai_dependent_child),
  under-18s (is_child, the Sept 2026 run's count), HBAI working-age adults
  and pensioners;
- people, children, working-age adults and pensioners below each line, BHC
  and AHC: the relative line at 60% of the world's own person-weighted
  median (the engine's in_relative_poverty_* flags, and the same line
  recomputed here as a check), the relative line held at the with-limit
  world's median, the absolute line the engine serves (FYE 2025 reference)
  and an absolute line on the FYE 2011 reference (constructed: see
  ``fye2011_line``);
- sums: universal_credit, child_tax_credit, two_child_limit_payment,
  benefit_cap_reduction, gov_tax, gov_spending, gov_balance,
  household_net_income, hbai_household_net_income;
- the executed limit, the children the limit affects, benefit units on
  Universal Credit, and (for current law against the with-limit world) the
  households and children whose HBAI income rises.

Two routes:

    certified   pe.uk.managed_microsimulation() on a certified pair in
                data/uk/certified_pairs.json (default DEFAULT_PAIR), through
                that registry's preflight (pipeline/uk_certified_pairs.py:
                the installed wheels' RECORD hashes, the packaged bundle
                manifest, Python, offline isolation, the dataset
                materialised and hashed, the runtime release bundle). Each
                simulation must read the hashed file with the record's data
                years, and the file is hashed again after each world. The
                result is the attached artifact.
    diagnostic  a bare policyengine_uk Microsimulation on an explicit
                dataset file, for the decomposition of the September and
                October estimates (engine x data). Never attached.

    PYTHONPATH=. <the pair's venv>/bin/python -m pipeline.compute_uk_two_child_limit_poverty \\
        certified [--pair <pair id>] [--dataset-file <certified bytes>] [--dry-run]
    PYTHONPATH=. .venv-pe289/bin/python -m pipeline.compute_uk_two_child_limit_poverty \\
        diagnostic --dataset <populace_uk_2023.h5> --label populace_uk2.89.2
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "results" / "uk" / "two_child_limit_poverty"
# policyengine.py 6.11.0's certified bundle: policyengine-uk 2.132.6 and the
# Microcosm UK 2024-25 national build made with it (data/uk/certified_pairs.json).
DEFAULT_PAIR = (
    "pair-pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71"
)
UC_LIMIT = "gov.dwp.universal_credit.elements.child.limit.child_count"
WINDOW = "2025-01-01.2035-12-31"
# policyengine-core has no infinity in a reform dict; the repo's no-limit
# sentinel (pipeline/compute_uk_ab2025.NO_LIMIT).
NO_LIMIT = 1e100
WORLDS = {
    "with_limit": {UC_LIMIT: {WINDOW: 2}},
    "current_law": None,
    "three_child_limit": {UC_LIMIT: {WINDOW: 3}},
    "removed_2025": {UC_LIMIT: {"2025-01-01.2025-12-31": NO_LIMIT}},
}
# world -> the engine years it runs
CERTIFIED_YEARS = {
    "with_limit": [2025, 2026, 2027, 2028, 2029, 2030],
    "current_law": [2025, 2026, 2027, 2028, 2029, 2030],
    "three_child_limit": [2029],
    "removed_2025": [2025],
}
DIAGNOSTIC_YEARS = {"with_limit": [2029], "current_law": [2029]}
# The FYE 2011-reference absolute line as policyengine-uk served it before
# it rebased to FYE 2025 (2.89.2: parameters/household/poverty/
# absolute_poverty_threshold_{bhc,ahc}.yaml, 2020-01-01 values, the FYE 2011
# line in FYE 2021 prices). fye2011_line reads the same entry from the
# running engine and refuses to run if it differs.
FYE2011_LINE_2020 = {"bhc": 305.7, "ahc": 261.92}
CPI = "gov.economic_assumptions.indices.obr.consumer_price_index"
WEEKS_IN_YEAR = 52
INCOME = {
    "bhc": "equiv_hbai_household_net_income",
    "ahc": "equiv_hbai_household_net_income_ahc",
}
RELATIVE_FLAG = {"bhc": "in_relative_poverty_bhc", "ahc": "in_relative_poverty_ahc"}
ABSOLUTE_FLAG = {"bhc": "in_poverty_bhc", "ahc": "in_poverty_ahc"}
SUMS = (
    "universal_credit",
    "child_tax_credit",
    "two_child_limit_payment",
    "benefit_cap_reduction",
    "gov_tax",
    "gov_spending",
    "gov_balance",
    "household_net_income",
    "hbai_household_net_income",
)
GROUPS = ("people", "children", "under_18", "working_age_adults", "pensioners")

t0 = time.time()


def log(msg: str) -> None:
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def configure_offline() -> None:
    for k in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_DATASETS_OFFLINE"):
        os.environ[k] = "1"
    # A concurrent reader (a hash, a copy) must not abort a run on HDF5's
    # advisory lock; integrity is asserted by SHA-256 instead
    # (pipeline/compute_uk_ab2025.configure_offline).
    os.environ.setdefault("HDF5_USE_FILE_LOCKING", "FALSE")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fy_label(year: int) -> str:
    return f"{year}-{(year + 1) % 100:02d}"


def installed(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def distributions() -> dict[str, str]:
    return {
        d.metadata["Name"].lower(): d.version
        for d in importlib.metadata.distributions()
    }


# --- the certified pair ----------------------------------------------------------


def preflight_pair(pair_id: str, dataset_file: Path | None) -> tuple[dict, dict]:
    """The registry's record and its preflight, before any engine import:
    returns (record, pre). The working directory is then the pair's runtime
    directory, whose ./data holds the verified dataset."""
    sys.path.insert(0, str(ROOT))
    from pipeline import uk_certified_pairs as pairs

    record = pairs.get_record(pair_id)
    if not pairs.is_pair(record):
        raise SystemExit(f"{pair_id} is not a certified pair (pair-...)")
    pre = pairs.preflight(
        record, dataset_source=dataset_file.resolve() if dataset_file else None
    )
    return record, pre


def check_runtime(sim, name: str, pre: dict) -> list[int]:
    """The simulation read the hashed file, under the certified bundle, with
    the record's data years (pipeline/compute_uk_childcare_100k.check_runtime)."""
    from pipeline import compute_uk_obr_costings as fiscal

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
            f"{name}: dataset years {dataset_years} != the pair's {pre['data_years']}"
        )
    return dataset_years


def peak_rss_gib() -> float:
    """ru_maxrss is bytes on macOS and KiB on Linux."""
    scale = 1 if sys.platform == "darwin" else 1024
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * scale / 2**30


# --- worlds -----------------------------------------------------------------------


def build_certified(reform: dict | None):
    import policyengine as pe

    return (
        pe.uk.managed_microsimulation()
        if reform is None
        else pe.uk.managed_microsimulation(reform=reform)
    )


def build_diagnostic(dataset: Path, reform: dict | None):
    from policyengine_uk import Microsimulation

    return (
        Microsimulation(dataset=str(dataset))
        if reform is None
        else Microsimulation(dataset=str(dataset), reform=reform)
    )


def _arr(series) -> np.ndarray:
    return np.asarray(series, dtype=float)


def person_weighted_median(income: np.ndarray, person_weight: np.ndarray) -> float:
    """The engine's own median (in_relative_poverty_* formulas: microdf
    MicroSeries.median over household incomes weighted by household weight
    times household size)."""
    from microdf import MicroSeries

    return float(MicroSeries(income, weights=person_weight).median())


def fye2011_line(sim, year: int, basis: str) -> float:
    """The FYE 2011-reference absolute line in ``year``, £ a year,
    constructed with the running engine's own uprating: the 2020-01-01 entry
    of absolute_poverty_threshold_<basis> (the FYE 2011 line, unchanged
    since 2.89.2) times CPI(year) / CPI(2020), the same index and instants
    by which the engine uprates the line it serves beyond its last entry.
    HBAI uprates with CPI variants; the engine's headline-CPI uprating is the
    approximation it already makes for its own line."""
    params = sim.tax_benefit_system.parameters
    node = getattr(params.household.poverty, f"absolute_poverty_threshold_{basis}")
    entry = {v.instant_str: v.value for v in node.values_list}.get("2020-01-01")
    if entry is None or abs(entry - FYE2011_LINE_2020[basis]) > 1e-9:
        raise SystemExit(
            f"absolute_poverty_threshold_{basis} 2020-01-01 = {entry}, not the "
            f"FYE 2011 line {FYE2011_LINE_2020[basis]}"
        )
    cpi = params.get_child(CPI)
    return entry * cpi(f"{year}-01-01") / cpi("2020-01-01") * WEEKS_IN_YEAR


def has_variable(sim, name: str) -> bool:
    return name in sim.tax_benefit_system.variables


def limit_counts_gb(sim, year: int, uc: np.ndarray, bw: np.ndarray) -> dict:
    """Great Britain benefit units on Universal Credit by the limit, in the
    shape of DWP's two-child limit statistics (Table 1, which covers GB:
    Universal Credit in Northern Ireland is administered separately):
    children for whom no child element is paid (uc_is_child_limit_affected),
    the benefit units with at least one, the UC children in those units,
    and the units on UC with three or more UC children."""
    country = np.asarray(sim.calculate("country", year, decode_enums=True)).astype(str)
    gb = (
        sim.map_result(
            (country != "NORTHERN_IRELAND").astype(float), "household", "benunit"
        )
        > 0
    )
    affected = _arr(sim.calculate("uc_is_child_limit_affected", year, map_to="benunit"))
    children = _arr(
        sim.calculate(
            "is_child_or_qualifying_young_person_for_universal_credit",
            year,
            map_to="benunit",
        )
    )
    on_uc = uc > 0
    with_affected = gb & on_uc & (affected > 0)
    return {
        "children_without_child_element": float((bw * affected)[gb & on_uc].sum()),
        "benunits_with_child_without_element": float(bw[with_affected].sum()),
        "uc_children_in_those_benunits": float((bw * children)[with_affected].sum()),
        "benunits_on_uc_with_three_or_more_children": float(
            bw[gb & on_uc & (children >= 3)].sum()
        ),
    }


def household_frame(sim, year: int) -> dict:
    """Household-level arrays for one world and year."""
    w = _arr(sim.calculate("household_weight", year))
    people = _arr(sim.calculate("household_count_people", year))
    frame: dict = {"weight": w, "people": people}
    hbai_child = has_variable(sim, "is_hbai_dependent_child")
    frame["concepts"] = {
        "children": "is_hbai_dependent_child" if hbai_child else None,
        "working_age_adults": "is_hbai_working_age_adult"
        if has_variable(sim, "is_hbai_working_age_adult")
        else None,
    }
    frame["children"] = (
        _arr(sim.calculate("is_hbai_dependent_child", year, map_to="household"))
        if hbai_child
        else np.full_like(w, np.nan)
    )
    frame["under_18"] = _arr(sim.calculate("is_child", year, map_to="household"))
    if frame["concepts"]["working_age_adults"]:
        frame["working_age_adults"] = _arr(
            sim.calculate("is_hbai_working_age_adult", year, map_to="household")
        )
        frame["pensioners"] = people - frame["children"] - frame["working_age_adults"]
    else:
        frame["working_age_adults"] = np.full_like(w, np.nan)
        frame["pensioners"] = np.full_like(w, np.nan)
    for basis, var in INCOME.items():
        frame[f"income_{basis}"] = _arr(sim.calculate(var, year))
        frame[f"relative_flag_{basis}"] = _arr(
            sim.calculate(RELATIVE_FLAG[basis], year)
        ).astype(bool)
        frame[f"absolute_flag_{basis}"] = _arr(
            sim.calculate(ABSOLUTE_FLAG[basis], year)
        ).astype(bool)
        frame[f"fye2011_line_{basis}"] = fye2011_line(sim, year, basis)
        if has_variable(sim, f"poverty_threshold_{basis}"):
            served = _arr(sim.calculate(f"poverty_threshold_{basis}", year))
            frame[f"served_absolute_line_{basis}"] = float(served.max())
            if not np.allclose(served, served.max()):
                raise SystemExit(f"poverty_threshold_{basis} varies by household")
        else:
            frame[f"served_absolute_line_{basis}"] = None
    frame["sums"] = {
        v: _arr(sim.calculate(v, year, map_to="household"))
        for v in SUMS
        if has_variable(sim, v)
    }
    frame["limit_affected_children"] = _arr(
        sim.calculate("uc_is_child_limit_affected", year, map_to="household")
    )
    uc = _arr(sim.calculate("universal_credit", year))
    bw = _arr(sim.calculate("benunit_weight", year))
    frame["benunits_on_uc"] = float(bw[uc > 0].sum())
    frame["uc_benunit"] = uc
    frame["benunit_weight"] = bw
    frame["limit_gb"] = limit_counts_gb(sim, year, uc, bw)
    params = sim.tax_benefit_system.parameters
    frame["executed_limit"] = float(params.get_child(UC_LIMIT)(f"{year}"))
    return frame


def weighted(frame: dict, mask: np.ndarray | None = None) -> dict:
    """Weighted members of each group; None for a group the engine does not
    define (2.89.2 has no HBAI groups)."""
    w = frame["weight"] if mask is None else frame["weight"] * mask
    return {
        g: None if np.isnan(frame[g]).all() else float((w * frame[g]).sum())
        for g in GROUPS
    }


def world_year(frame: dict, line_anchor: dict) -> dict:
    """Weighted counts for one world-year; ``line_anchor`` holds the
    with-limit world's relative lines for the fixed-line counts."""
    pw = frame["weight"] * frame["people"]
    out = {
        "population": weighted(frame),
        "concepts": frame["concepts"],
        "executed_limit": frame["executed_limit"],
        "lines_gbp_year": {},
        "below": {},
        "sums_gbp": {
            v: float((frame["weight"] * a).sum()) for v, a in frame["sums"].items()
        },
        "limit_affected_children": float(
            (frame["weight"] * frame["limit_affected_children"]).sum()
        ),
        "benunits_on_uc": frame["benunits_on_uc"],
        "limit_gb": frame["limit_gb"],
    }
    for basis in ("bhc", "ahc"):
        income = frame[f"income_{basis}"]
        own_line = 0.6 * person_weighted_median(income, pw)
        recomputed = income < own_line
        flag = frame[f"relative_flag_{basis}"]
        disagree = float(frame["weight"][recomputed != flag].sum())
        fixed_line = line_anchor[basis]
        fye2011 = frame[f"fye2011_line_{basis}"]
        out["lines_gbp_year"][basis] = {
            "relative_own_median": own_line,
            "relative_fixed_at_with_limit": fixed_line,
            "absolute_served": None
            if frame[f"served_absolute_line_{basis}"] is None
            else frame[f"served_absolute_line_{basis}"],
            "absolute_fye2011": fye2011,
        }
        out["below"][basis] = {
            "relative_moving": weighted(frame, flag),
            "relative_moving_disagreeing_households": disagree,
            "relative_fixed_at_with_limit": weighted(frame, income < fixed_line),
            "absolute_served": weighted(frame, frame[f"absolute_flag_{basis}"]),
            "absolute_fye2011": weighted(frame, income < fye2011),
        }
    return out


def gainers(base: dict, ref: dict) -> dict:
    """Households and their members whose HBAI income (BHC) rises from the
    with-limit world to the comparison world, and benefit units whose
    Universal Credit rises."""
    out = {}
    d = (
        ref["sums"]["hbai_household_net_income"]
        - base["sums"]["hbai_household_net_income"]
    )
    for name, threshold in (("over_0", 0.0), ("over_1_a_week", WEEKS_IN_YEAR)):
        m = d > threshold
        out[f"hbai_income_{name}"] = {
            "households": float(base["weight"][m].sum()),
            **weighted(base, m),
        }
    # the converse, for the invariant that removing a limit makes no
    # household worse off (so a count below any line held fixed across the
    # two worlds cannot rise); a penny of float noise is not a loss
    lose = d < -0.01
    out["hbai_income_falls"] = {
        "households": float(base["weight"][lose].sum()),
        "largest_loss_gbp_year": float(-d.min()) if lose.any() else 0.0,
    }
    for basis in ("bhc", "ahc"):
        de = ref[f"income_{basis}"] - base[f"income_{basis}"]
        out[f"equivalised_{basis}_income_falls_households"] = float(
            base["weight"][de < -0.01].sum()
        )
    duc = ref["uc_benunit"] - base["uc_benunit"]
    out["benunits_uc_rises"] = float(base["benunit_weight"][duc > 0].sum())
    out["benunits_uc_falls"] = float(base["benunit_weight"][duc < 0].sum())
    return out


def anchor_lines(frame: dict) -> dict:
    pw = frame["weight"] * frame["people"]
    return {
        basis: 0.6 * person_weighted_median(frame[f"income_{basis}"], pw)
        for basis in ("bhc", "ahc")
    }


# --- runs ----------------------------------------------------------------------


def run(route: str, dataset: Path, years_by_world: dict, build, check=None) -> dict:
    """Every world's frames, then the derived entries. ``check(sim, name)``,
    when given, verifies a built simulation before any read and returns its
    dataset years (the certified route's check_runtime)."""
    digest_before = sha256_file(dataset)
    frames: dict[str, dict[int, dict]] = {}
    worlds: dict = {}
    for name, years in years_by_world.items():
        reform = WORLDS[name]
        log(f"{route}: building {name}")
        before = sha256_file(dataset)
        if before != digest_before:
            raise SystemExit(f"the dataset changed before the {name} simulation")
        sim = build(reform)
        dataset_years = check(sim, name) if check is not None else None
        frames[name] = {}
        for year in years:
            log(f"  {name} {year}")
            frames[name][year] = household_frame(sim, year)
        worlds[name] = {
            "reform_dict": reform,
            "years": {},
            "dataset_sha256_before": before,
            "dataset_sha256_after": sha256_file(dataset),
        }
        if worlds[name]["dataset_sha256_after"] != digest_before:
            raise SystemExit(f"the dataset changed during the {name} simulation")
        if dataset_years is not None:
            worlds[name]["dataset_years"] = dataset_years
        del sim
    for name, by_year in frames.items():
        for year, frame in by_year.items():
            anchor_year = year if year in frames["with_limit"] else None
            anchor = (
                anchor_lines(frames["with_limit"][anchor_year])
                if anchor_year is not None
                else anchor_lines(frame)
            )
            entry = world_year(frame, anchor)
            entry["fy"] = fy_label(year)
            if name != "with_limit" and anchor_year is not None:
                entry["gainers_vs_with_limit"] = gainers(
                    frames["with_limit"][anchor_year], frame
                )
            if name == "removed_2025":
                entry["gainers_vs_current_law"] = gainers(
                    frames["current_law"][year], frame
                )
            worlds[name]["years"][str(year)] = entry
    return {"dataset_sha256": digest_before, "worlds": worlds}


def check_executed(worlds: dict) -> None:
    """Each world executed the limit it names."""
    want = {"with_limit": 2.0, "three_child_limit": 3.0}
    for name, world in worlds.items():
        for year, entry in world["years"].items():
            got = entry["executed_limit"]
            if name in want:
                ok = got == want[name]
            elif name == "removed_2025":
                ok = got >= NO_LIMIT
            else:  # current_law: the limit from 2026-04-06 is infinite
                ok = got == 2.0 if int(year) < 2026 else np.isinf(got)
            if not ok:
                raise SystemExit(f"{name} {year}: executed limit {got}")


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, sort_keys=True, default=float) + "\n")
    log(f"wrote {path.relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="route", required=True)
    cert = sub.add_parser("certified")
    cert.add_argument("--pair", default=DEFAULT_PAIR)
    cert.add_argument(
        "--dataset-file",
        type=Path,
        help="a local file holding the pair's certified dataset bytes "
        "(default: the Hugging Face cache)",
    )
    cert.add_argument("--dry-run", action="store_true")
    diag = sub.add_parser("diagnostic")
    diag.add_argument("--dataset", type=Path, required=True)
    diag.add_argument("--label", required=True)
    diag.add_argument(
        "--all-worlds",
        action="store_true",
        help="run every certified world and year (default: with_limit and current_law, 2029)",
    )
    args = ap.parse_args(argv)

    meta = {
        "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "installed": {
            k: installed(k)
            for k in (
                "policyengine",
                "policyengine-uk",
                "policyengine-core",
                "microdf-python",
            )
        },
        "behavioural_response": "none (static)",
        "uc_limit_parameter": UC_LIMIT,
        "no_limit_sentinel": NO_LIMIT,
        "fye2011_line_construction": (
            "absolute_poverty_threshold_<basis> 2020-01-01 entry (the FYE 2011 "
            "line, BHC 305.7 / AHC 261.92 a week) x CPI(year)/CPI(2020) on "
            f"{CPI}, x {WEEKS_IN_YEAR}"
        ),
    }
    if args.route == "certified":
        record, pre = preflight_pair(args.pair, args.dataset_file)
        dataset = Path(pre["runtime_dataset_source"])
        identity = record["identity"]
        verified = pre["installed"]
        log(f"certified pair {record['variant_id']}: dataset {dataset} verified")
        if args.dry_run:
            print(json.dumps({"pair": record["variant_id"], "dataset": str(dataset)}))
            return 0
        result = run(
            "certified",
            dataset,
            CERTIFIED_YEARS,
            build_certified,
            check=lambda sim, name: check_runtime(sim, name, pre),
        )
        check_executed(result["worlds"])
        if result["dataset_sha256"] != identity["dataset"]["sha256"]:
            raise SystemExit("the dataset is not the certified artifact")
        from pipeline import uk_replay_variants as variants

        variants.verify_import_origins()
        payload = {
            **meta,
            "kind": "uk_two_child_limit_poverty_counterparts",
            "route": "certified: policyengine.py managed_microsimulation",
            "pair_id": record["variant_id"],
            "variant_identity_sha256": record["identity_sha256"],
            "run_id": f"uk-two-child-limit-poverty-{record['variant_id']}",
            "packages": {
                name: {
                    "version": verified["packages"][name]["version"],
                    "record_sha256": verified["packages"][name]["record_sha256"],
                }
                for name in variants.PACKAGES
            },
            "packaged_bundle_manifest_sha256": verified[
                "packaged_bundle_manifest_sha256"
            ],
            "release_bundle": pre["release_bundle"],
            "dataset": {
                key: identity["dataset"][key]
                for key in ("repo_id", "revision", "path", "sha256")
            },
            "data_years": pre["data_years"],
            "distributions": distributions(),
            "peak_rss_gib": peak_rss_gib(),
            **result,
        }
        write(OUTPUT_DIR / f"{record['variant_id']}.json", payload)
        return 0
    configure_offline()
    dataset = args.dataset.resolve()
    result = run(
        "diagnostic",
        dataset,
        CERTIFIED_YEARS if args.all_worlds else DIAGNOSTIC_YEARS,
        lambda reform: build_diagnostic(dataset, reform),
    )
    check_executed(result["worlds"])
    payload = {
        **meta,
        "kind": "uk_two_child_limit_poverty_diagnostic",
        "route": "diagnostic: bare policyengine_uk Microsimulation on an explicit dataset file (not attached)",
        "label": args.label,
        "dataset_file": dataset.name,
        "dataset_bytes": dataset.stat().st_size,
        "peak_rss_gib": peak_rss_gib(),
        **result,
    }
    write(OUTPUT_DIR / "diagnostics" / f"{args.label}.json", payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
