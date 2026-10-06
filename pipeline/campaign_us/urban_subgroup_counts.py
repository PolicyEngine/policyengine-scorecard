"""Family ``urban_subgroup_counts`` (78 rows, original run_id
campaign-20260802-subgroups).

Urban SotSN subgroup counts (claims matched claim_id-direct), CY2024,
baseline (as-served take-up). One simulation, period 2024. Every count is
a weighted person count: a person-level numpy mask indexing a person-level
boolean MicroSeries of ones (``age >= -1``), exactly as the year-grid
counterpart runner (``pipeline/compute_counterparts.py``) cuts subgroups.

Program concepts, from the original ``pe_construction`` texts:

* ``pass2 snap elig_pop`` — "persons in SNAP-eligible SPM units (BBCE
  incl.)": ``is_snap_eligible`` mapped to persons, > 0.
* ``pass2 housing elig_pop`` — "persons in PE-eligible units (recipients OR
  renter <=80% AMI)": ``is_eligible_for_housing_assistance`` mapped to
  persons, > 0. ``elig_pop - part_pop`` subtracts persons in units with
  ``housing_assistance > 0``.
* ``pass2 ssi elig_pop`` — "adults+children in units w/ PE
  is_ssi_eligible (pre-income-test ...)": two readings are computed —
  (a) the person's own ``is_ssi_eligible`` (person variable, all ages) and
  (b) persons whose SPM unit has any ``is_ssi_eligible`` member. The
  staged reading is ``SSI_READING = "person"``: on the old bundle (us-5.0.1)
  it reproduces all 11 original SSI rows exactly, while reading (b)
  overstates them by 9% (age_65plus) to 98% (status_citizen). Both are
  recorded in the run metadata.
* ``pass2 tanf elig_pop`` — "persons in DEMOGRAPHIC-tanf-eligible units":
  ``is_demographic_tanf_eligible`` mapped to persons, > 0.
* ``pass2 wic elig_pop`` — "WIC-eligible persons ALL AGES (... restrict to
  u5 per year-grid Urban child concept)": ``is_wic_eligible`` (person) > 0
  within the WIC age band; ``elig_pop - part_pop`` subtracts persons with
  ``wic > 0`` in the band.

Subgroup axes (``subgroup=`` in the construction text):

* age bands — the year-grid bands: age_0thr17 (<18), age_18plus, age_0thr3
  (<4), age_4thr5, age_6thr17, age_18thr24, age_25thr59, age_60thr64,
  age_65plus; WIC: age_0thr3 (<4), age_4 (4), age_1thr4 (1-4).
* race5 — original annotation "hispanic first, then PRDTRACE
  1/2/{4,5}/other": ``is_hispanic`` -> race_hispanic; else ``cps_race``
  (= PRDTRACE) 1 -> race_white, 2 -> race_black, 4 or 5 -> race_aapi,
  anything else -> race_multi_other.
* disability_yes/no — ``is_disabled``.
* status_citizen/noncitizen — ``immigration_status == CITIZEN`` / not.
* fam_earners_yes/no — the annotation names the PE side a "tax-unit-earner"
  concept: the person's tax unit has ``tax_unit_earned_income > 0``.
"""

from __future__ import annotations

import re

import numpy as np
from common import emit_row, load_original, now_utc, provenance, run_job

STEM = "urban_subgroup_counts"
YEAR = 2024
SSI_READING = "person"  # "person" (own is_ssi_eligible) or "unit"


def _pmask(sim, var: str, map_to: str | None = "person") -> np.ndarray:
    kw = {"map_to": map_to} if map_to else {}
    return np.asarray(sim.calculate(var, YEAR, **kw).values) > 0


SUBGROUP_INPUTS = ["cps_race", "is_hispanic", "is_disabled", "immigration_status_str"]


def measures(sim) -> dict:
    # A subgroup axis whose input the dataset does not store would silently
    # fall back to the variable default (e.g. cps_race = 0 -> everyone in
    # race_multi_other): require stored data for every axis input.
    missing = [v for v in SUBGROUP_INPUTS if not sim.get_holder(v).get_known_periods()]
    if missing:
        raise RuntimeError(f"subgroup inputs not stored in the dataset: {missing}")
    age_ms = sim.calculate("age", YEAR)
    ones = age_ms >= -1
    age = np.asarray(age_ms.values, dtype=float)

    subs = {
        "age_0thr17": age < 18,
        "age_18plus": age >= 18,
        "age_0thr3": age < 4,
        "age_4thr5": (age >= 4) & (age < 6),
        "age_6thr17": (age >= 6) & (age < 18),
        "age_18thr24": (age >= 18) & (age < 25),
        "age_25thr59": (age >= 25) & (age < 60),
        "age_60thr64": (age >= 60) & (age < 65),
        "age_65plus": age >= 65,
        "age_4": (age >= 4) & (age < 5),
        "age_1thr4": (age >= 1) & (age < 5),
    }
    hisp = np.asarray(sim.calculate("is_hispanic", YEAR).values).astype(bool)
    race = np.asarray(sim.calculate("cps_race", YEAR).values).astype(int)
    subs["race_hispanic"] = hisp
    subs["race_white"] = ~hisp & (race == 1)
    subs["race_black"] = ~hisp & (race == 2)
    subs["race_aapi"] = ~hisp & np.isin(race, [4, 5])
    subs["race_multi_other"] = ~hisp & ~np.isin(race, [1, 2, 4, 5])
    dis = np.asarray(sim.calculate("is_disabled", YEAR).values).astype(bool)
    subs["disability_yes"], subs["disability_no"] = dis, ~dis
    imm = np.asarray(sim.calculate("immigration_status", YEAR).values).astype(str)
    cit = imm == "CITIZEN"
    subs["status_citizen"], subs["status_noncitizen"] = cit, ~cit
    earn = _pmask(sim, "tax_unit_earned_income")
    subs["fam_earners_yes"], subs["fam_earners_no"] = earn, ~earn

    ssi_unit = (
        sim.map_result(
            np.asarray(
                sim.calculate("is_ssi_eligible", YEAR, map_to="spm_unit").values
            ),
            "spm_unit",
            "person",
        )
        > 0
    )
    progs = {
        "snap": {"elig": _pmask(sim, "is_snap_eligible")},
        "housing": {
            "elig": _pmask(sim, "is_eligible_for_housing_assistance"),
            "part": _pmask(sim, "housing_assistance"),
        },
        "ssi_person": {"elig": _pmask(sim, "is_ssi_eligible", None)},
        "ssi_unit": {"elig": ssi_unit},
        "tanf": {"elig": _pmask(sim, "is_demographic_tanf_eligible")},
        "wic": {
            "elig": _pmask(sim, "is_wic_eligible", None),
            "part": _pmask(sim, "wic", None),
        },
    }
    out = {}
    for prog, masks in progs.items():
        for sub, sm in subs.items():
            for kind, m in masks.items():
                out[f"{prog}|{kind}|{sub}"] = ones[m & sm].sum()
    # diagnostics: alternative earner concept (any member with earnings)
    any_earner = (
        sim.map_result(
            np.asarray(sim.calculate("earned_income", YEAR, map_to="tax_unit").values),
            "tax_unit",
            "person",
        )
        > 0
    )
    for prog in ("snap", "tanf", "housing"):
        out[f"{prog}|elig|fam_earners_yes_anymember"] = ones[
            progs[prog]["elig"] & any_earner
        ].sum()
    return out


_PAT = re.compile(r"^pass2 (\w+) (elig_pop(?: - part_pop)?) subgroup=(\w+) CY2024")


def value_for(row: dict, m: dict) -> float:
    prog, metric, sub = _PAT.match(row["pe_construction"]).groups()
    if prog == "ssi":
        prog = f"ssi_{SSI_READING}"
    v = m[f"{prog}|elig|{sub}"]
    if metric == "elig_pop - part_pop":
        v -= m[f"{prog}|part|{sub}"]
    return v


def run() -> tuple[list[dict], dict]:
    originals = load_original(STEM)
    res = run_job(
        {"label": "urban subgroups CY2024", "measure": "urban_subgroup_counts:measures"}
    )
    prov = provenance([res])
    at = now_utc()
    rows = [emit_row(o, value_for(o, res["values"]), prov, at) for o in originals]
    return rows, {"provenance": prov, "jobs": [res], "ssi_reading": SSI_READING}
