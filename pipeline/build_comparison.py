"""Join external tidy rows with PE counterpart metrics -> data/comparison.json.

Counts come raw from pipeline/compute_counterparts.py (data/pe/pe_metrics.json);
every rate/gap/delta is derived HERE so there is one source of arithmetic truth.

Status taxonomy (honesty made structural — misses stay on the page):
  comparable       PE measures the same concept (annotations may still apply)
  constructed      PE approximates Urban's concept via a documented
                   construction (e.g. payable-under-forced-take-up denominators)
  concept_mismatch PE value exists but measures a different concept (housing)
  pe_gap           the model/artifact cannot produce this today (LIHEAP, CCDF,
                   metro/non-metro)
  not_computed     producible but not yet in the pipeline (v1 backlog)
  suppressed       Urban suppressed the cell
"""

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PE_GAP_PROGRAMS = {"liheap", "ccdf"}
PE_GAP_SUBGROUPS = {"locale_metro", "locale_nonmetro"}

# Person-level subgroups the sim emits for snap/ssi/tanf (age bands + probed
# demographics); wic uses its own band set. Anything else -> not_computed.
AGE_SUBS = {
    "age_0thr17", "age_18plus", "age_0thr3", "age_4thr5", "age_6thr17",
    "age_18thr24", "age_25thr59", "age_60thr64", "age_65plus",
}
DEMO_SUBS = {
    "race_white", "race_black", "race_hispanic", "race_aapi",
    "race_multi_other", "disability_yes", "disability_no",
}
WIC_SUBS = {"total", "age_0", "age_1thr4", "age_0thr3", "age_4"}
SSI_SUBS = {"total", "age_18thr24", "age_25thr59", "age_60thr64",
            "age_65plus"} | DEMO_SUBS


def load_pe():
    rows = json.loads((DATA / "pe" / "pe_metrics.json").read_text())
    idx = {}
    for r in rows:
        idx[(r["run"], r["program"], r["metric"], r["subgroup"],
             r["geography"])] = r["value"]
    return idx


class PE:
    def __init__(self, idx):
        self.idx = idx

    def get(self, run, program, metric, subgroup, geo):
        return self.idx.get((run, program, metric, subgroup, geo))


def ratio(a, b):
    if a is None or b in (None, 0):
        return None
    return a / b


# The unit concept each program's PE construction measures. External rows in
# a different unit (e.g. TANF family-unit rows next to its person rows) are
# not_computed rather than silently compared across units.
EXPECTED_UNIT = {
    "snap": "persons",
    "ssi": "adults_18plus",
    "tanf": "persons",
    "wic": "children_0thr4",
    "eitc": "tax_units",
    "ctc_refund": "tax_units",
    "housing": "households",
}


def counterpart(pe, program, metric, subgroup, variant, geo, unit_concept):
    """Return (pe_value, status, construction) for one external row.

    construction is a short machine-readable recipe string; None value with a
    non-gap status means the lookup failed unexpectedly (kept visible).
    """
    g = pe.get

    if program in PE_GAP_PROGRAMS:
        return None, "pe_gap", None
    if subgroup in PE_GAP_SUBGROUPS:
        return None, "pe_gap", None
    if program in EXPECTED_UNIT and unit_concept != EXPECTED_UNIT[program]:
        return None, "not_computed", None

    def person_denom(sub, denom_program="_persons"):
        s = "total" if sub == "total" else sub
        return g("baseline", denom_program, "count", s, geo)

    if program == "snap":
        if subgroup not in ({"total"} | AGE_SUBS | DEMO_SUBS):
            return None, "not_computed", None
        elig = g("baseline", "snap", "eligible_count", subgroup, geo)
        both = g("baseline", "snap", "elig_participant_count", subgroup, geo)
        if metric == "eligible_count":
            return elig, "comparable", "baseline is_snap_eligible→person"
        if metric == "eligibility_rate":
            return (
                ratio(elig, person_denom(subgroup)), "comparable",
                "baseline is_snap_eligible→person ÷ persons",
            )
        if metric == "participation_rate":
            return (
                ratio(both, elig), "comparable",
                "baseline snap>0 & eligible, ÷ eligible (persons)",
            )
        if metric == "participation_gap_count":
            if elig is None or both is None:
                return None, "not_computed", None
            return elig - both, "comparable", "eligible − participating & eligible"

    if program == "ssi":
        if subgroup not in SSI_SUBS:
            return None, "not_computed", None
        payable = g("fullpart_urban6", "ssi", "participant_count", subgroup, geo)
        base = g("baseline", "ssi", "participant_count", subgroup, geo)
        recipe = "adults with ssi>0 under forced take-up (fullpart_urban6)"
        if metric == "eligible_count":
            return payable, "constructed", recipe
        if metric == "eligibility_rate":
            denom_sub = "age_18plus" if subgroup == "total" else subgroup
            return (
                ratio(payable, person_denom(denom_sub)), "constructed",
                recipe + " ÷ adults",
            )
        if metric == "participation_rate":
            return (
                ratio(base, payable), "constructed",
                "baseline ssi>0 ÷ " + recipe,
            )
        if metric == "participation_gap_count":
            if payable is None or base is None:
                return None, "not_computed", None
            return payable - base, "constructed", recipe + " − baseline"

    if program == "tanf":
        # Urban publishes person-level (pop) plus family-unit variants; the
        # unit/SSF rows are not yet computed.
        if variant is not None:
            return None, "not_computed", None
        if subgroup not in ({"total"} | AGE_SUBS | DEMO_SUBS):
            return None, "not_computed", None
        payable = g(
            "fullpart_urban6", "tanf", "participant_count", subgroup, geo
        )
        base = g("baseline", "tanf", "participant_count", subgroup, geo)
        recipe = "persons in units with tanf>0 under forced take-up"
        if metric == "eligible_count":
            return payable, "constructed", recipe
        if metric == "eligibility_rate":
            return (
                ratio(payable, person_denom(subgroup)), "constructed",
                recipe + " ÷ persons",
            )
        if metric == "participation_rate":
            return (
                ratio(base, payable), "constructed",
                "baseline tanf>0 persons ÷ " + recipe,
            )
        if metric == "participation_gap_count":
            if payable is None or base is None:
                return None, "not_computed", None
            return payable - base, "constructed", recipe + " − baseline"

    if program == "wic":
        if subgroup not in (WIC_SUBS | DEMO_SUBS):
            return None, "not_computed", None
        elig = g("baseline", "wic", "eligible_count", subgroup, geo)
        both = g("baseline", "wic", "elig_participant_count", subgroup, geo)
        if metric == "eligible_count":
            return elig, "comparable", "baseline is_wic_eligible, ages 0–4"
        if metric == "eligibility_rate":
            return (
                ratio(elig, person_denom(subgroup, "_children_0thr4")),
                "comparable",
                "eligible children ÷ children 0–4",
            )
        if metric == "participation_rate":
            return (
                ratio(both, elig), "comparable",
                "wic>0 & eligible ÷ eligible (children 0–4)",
            )
        if metric == "participation_gap_count":
            if elig is None or both is None:
                return None, "not_computed", None
            return elig - both, "comparable", "eligible − participating & eligible"

    if program == "eitc":
        sub_map = {"total": "total", "age_child": "age_child",
                   "age_nochild": "age_nochild"}
        if subgroup not in sub_map:
            return None, "not_computed", None
        forced = g(
            "fullpart_urban6", "eitc", "participant_count",
            sub_map[subgroup], geo,
        )
        recipe = "tax units with eitc>0 under forced take-up"
        if metric == "eligible_count":
            return forced, "constructed", recipe
        if metric == "eligibility_rate":
            if subgroup != "total":
                return None, "not_computed", None
            return (
                ratio(forced, g("baseline", "_tax_units", "count", "total",
                                geo)),
                "constructed", recipe + " ÷ tax units",
            )

    if program == "ctc_refund":
        if subgroup != "total":
            return None, "not_computed", None
        claims = g("baseline", "ctc_refund", "participant_count", "total", geo)
        recipe = "baseline refundable_ctc>0 (claims-calibrated; no take-up flag)"
        if metric == "eligible_count":
            return claims, "constructed", recipe
        if metric == "eligibility_rate":
            return (
                ratio(claims, g("baseline", "_tax_units", "count", "total",
                                geo)),
                "constructed", recipe + " ÷ tax units",
            )

    if program == "housing":
        if subgroup != "total":
            return None, "not_computed", None
        elig = g("baseline", "housing", "eligible_count", "total", geo)
        both = g("baseline", "housing", "elig_participant_count", "total", geo)
        if metric == "eligible_count":
            return (
                elig, "concept_mismatch",
                "spm units: recipient OR renter ≤80% AMI (Urban: households ≤50% AMI)",
            )
        if metric == "eligibility_rate":
            return (
                ratio(elig, g("baseline", "_spm_units", "count", "total",
                              geo)),
                "concept_mismatch", "eligible spm units ÷ spm units",
            )
        if metric == "participation_rate":
            return (
                ratio(both, elig), "concept_mismatch",
                "housing_assistance>0 & eligible ÷ eligible (spm units)",
            )
        if metric == "participation_gap_count":
            if elig is None or both is None:
                return None, "not_computed", None
            return elig - both, "concept_mismatch", "eligible − participating"

    if program == "spm_poverty":
        sub = subgroup  # total | child
        def pov(run):
            poor = g(run, "_poverty", "poor_count", sub, geo)
            popn = g(run, "_poverty", "population", sub, geo)
            return poor, popn
        b_poor, b_pop = pov("baseline")
        f_poor, f_pop = pov("fullpart_all")
        if metric == "poverty_rate":
            return ratio(b_poor, b_pop), "comparable", "baseline SPM poverty"
        if metric == "poverty_rate_fullpart":
            return (
                ratio(f_poor, f_pop), "constructed",
                "all stored take-up flags True + WIC gate (see pe_meta runs)",
            )
        if metric == "poverty_rate_relative_change_fullpart":
            br, fr = ratio(b_poor, b_pop), ratio(f_poor, f_pop)
            if br in (None, 0) or fr is None:
                return None, "not_computed", None
            return (fr - br) / br, "constructed", "(fullpart − base) ÷ base"
        if metric == "poverty_count_change_fullpart":
            if b_poor is None or f_poor is None:
                return None, "not_computed", None
            return f_poor - b_poor, "constructed", "fullpart poor − base poor"

    return None, "not_computed", None


def load_annotations():
    spec = json.loads(
        (ROOT / "sources" / "urban-sotsn" / "annotations.json").read_text()
    )
    return spec["annotations"]


def annotation_ids(annotations, row):
    out = []
    for a in annotations:
        m = a["applies_to"]
        if m.get("has_2026") and row.get("pe_value_2026") is None:
            continue
        if m.get("program") not in (None, row["program"]):
            continue
        if m.get("metrics") is not None and row["metric"] not in m["metrics"]:
            continue
        if (
            m.get("subgroups") is not None
            and row["subgroup"] not in m["subgroups"]
        ):
            continue
        if (
            m.get("variants") is not None
            and row["variant"] not in m["variants"]
        ):
            continue
        if m.get("geography") == "states" and row["geography"] == "US":
            continue
        out.append(a["id"])
    return out


# --- calibration_relationship (oracle doctrine, issue #1 point 2) ---
# Mandatory on every external number: agreement on consumed targets is a
# tautology, never a win; the published validation column is held_out only.
# Mapping is (program, metric)-level, evidence-based from the replication
# assessment (docs/replication-assessment.md §3 seeds, §4 target surface).
_FNS = ("consumed_as_target",
        "§3-§4: SNAP participating units count-calibrated to FNS "
        "average-month household counts (national + state) — the same "
        "admin-caseload class as Urban's numerator")
_SSA = ("consumed_as_target",
        "§3: SSI count-calibrated to SSA state recipient counts and payments")
_ASPE = ("seed_source",
         "§3: TANF flag seeded at ASPE 0.219 — a TRIM3 rate, the same model "
         "family as ATTIS; only dollar targets exist (missed −36%)")
_HELD_ELIG = ("held_out",
              "§4: no eligibility targets; eligibility is disciplined only "
              "indirectly via income/demographic margins")
CALIBRATION_RELATIONSHIP = {
    ("snap", "participation_rate"): _FNS,
    ("snap", "participation_gap_count"): _FNS,
    ("snap", "eligible_count"): _HELD_ELIG,
    ("snap", "eligibility_rate"): _HELD_ELIG,
    ("ssi", "participation_rate"): _SSA,
    ("ssi", "participation_gap_count"): _SSA,
    ("ssi", "eligible_count"): ("held_out",
        "payable-under-forced construction; §4 targets recipient counts, "
        "not eligible counts"),
    ("ssi", "eligibility_rate"): ("held_out",
        "payable-under-forced construction; §4 targets recipient counts, "
        "not eligible counts"),
    ("tanf", "participation_rate"): _ASPE,
    ("tanf", "participation_gap_count"): _ASPE,
    ("tanf", "eligible_count"): _HELD_ELIG,
    ("tanf", "eligibility_rate"): _HELD_ELIG,
    ("eitc", "eligible_count"): ("held_out",
        "forced-flag positive-credit count is not itself a target; SOI "
        "claims targets discipline a subset (see construction annotation)"),
    ("eitc", "eligibility_rate"): ("held_out",
        "forced-flag positive-credit count is not itself a target; SOI "
        "claims targets discipline a subset (see construction annotation)"),
    ("ctc_refund", None): ("consumed_as_target",
        "§4-§5: refundable CTC claims and dollars are SOI-targeted; no "
        "take-up flag exists, so the count is claims-shaped"),
    ("wic", None): ("held_out",
        "§4: zero WIC calibration targets; §6: the near-match is "
        "out-of-sample"),
    ("housing", None): ("held_out", "§4: zero housing targets"),
    ("spm_poverty", None): ("held_out",
        "§4: no poverty targets in the Build P surface"),
    ("liheap", None): ("held_out", "no PE national model consumes these"),
    ("ccdf", None): ("held_out", "no PE national model consumes these"),
}


def calibration_relationship(program, metric):
    hit = CALIBRATION_RELATIONSHIP.get((program, metric)) or \
        CALIBRATION_RELATIONSHIP.get((program, None))
    return hit if hit else ("held_out", "no PE consumption identified")


INTERCHANGE = Path.home() / "populace-sotsn-takeup" / "comparison"

# Interchange (program, metric) -> platform (program, metric). Poverty maps
# from A's base/fullpart pseudo-programs; fullpart 2026 rows are excluded
# (their 2026 run predates the WIC-gate fix — RECONCILIATION.md #2).
INTERCHANGE_METRIC = {
    "elig_pop": "eligible_count",
    "elig_units": "eligible_count",
    "elig_rate": "eligibility_rate",
    "part_rate": "participation_rate",
    "part_gap": "participation_gap_count",
}


def load_2026():
    """{(program, metric, geography): pe_value_2026} from the canonical
    interchange, keyed in platform vocabulary. Only totals rows exist."""
    import csv

    path = INTERCHANGE / "comparison.csv"
    if not path.exists():
        return {}, {}
    v2026, v2024 = {}, {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if r.get("breakdown") != "total":
                continue
            prog, met = r["program"], r["metric"]
            if prog == "base" and met.startswith("spm_pov_rate_100"):
                key = ("spm_poverty", "poverty_rate", r["geography"],
                       "child" if met.endswith("_child") else "total")
            elif prog in ("base", "fullpart"):
                continue  # fullpart 2026 excluded; change rows derive from it
            elif met in INTERCHANGE_METRIC:
                key = (prog, INTERCHANGE_METRIC[met], r["geography"], "total")
            else:
                continue
            for col, store in (("pe_value_2026", v2026), ("pe_value", v2024)):
                val = r.get(col)
                if val not in (None, ""):
                    store[key] = float(val)
    return v2026, v2024


def load_pe_2026():
    """Own 2026 grid (full constructions), if computed."""
    p = DATA / "pe" / "pe_metrics_2026.json"
    if not p.exists():
        return None
    rows = json.loads(p.read_text())
    return PE({
        (r["run"], r["program"], r["metric"], r["subgroup"], r["geography"]):
            r["value"]
        for r in rows
    })


def main():
    pe = PE(load_pe())
    pe26 = load_pe_2026()
    annotations = load_annotations()
    ic_2026, ic_2024 = load_2026()
    externals = []
    for f in sorted((DATA / "externals").glob("*.json")):
        externals.extend(json.loads(f.read_text()))

    pe_meta = json.loads((DATA / "pe" / "pe_meta.json").read_text())

    out_rows = []
    for ext in externals:
        if ext["status"] == "suppressed":
            status, pe_value, construction = "suppressed", None, None
        else:
            pe_value, status, construction = counterpart(
                pe, ext["program"], ext["metric"], ext["subgroup"],
                ext["variant"], ext["geography"], ext["unit_concept"],
            )
        row = dict(ext)
        row["external_value"] = row.pop("value")
        row["pe_value"] = pe_value
        row["pe_period"] = "2024 annual" if pe_value is not None else None
        row["status"] = status
        row["pe_construction"] = construction
        # 2026 projection. Preferred source: our own 2026 grid (identical
        # constructions by definition — full subgroup/state coverage).
        # Fallback: the canonical interchange behind a 0.5%
        # same-construction gate on the 2024 value.
        row["pe_value_2026"] = None
        if pe_value is not None and pe26 is not None:
            v26, s26, _ = counterpart(
                pe26, ext["program"], ext["metric"], ext["subgroup"],
                ext["variant"], ext["geography"], ext["unit_concept"],
            )
            if v26 is not None and s26 == status:
                row["pe_value_2026"] = v26
        if (
            row["pe_value_2026"] is None and pe_value is not None
            and ext["subgroup"] == "total" and not ext["variant"]
        ):
            k = (ext["program"], ext["metric"], ext["geography"],
                 ext["subgroup"] if ext["program"] == "spm_poverty"
                 else "total")
            ic24 = ic_2024.get(k)
            ic26 = ic_2026.get(k)
            if (
                ic24 is not None and ic26 is not None
                and abs(ic24 - pe_value) <= abs(pe_value) * 0.005 + 1e-9
            ):
                row["pe_value_2026"] = ic26
        rel, rel_basis = calibration_relationship(
            ext["program"], ext["metric"]
        )
        row["calibration_relationship"] = rel
        row["calibration_basis"] = rel_basis
        if pe_value is not None and row["external_value"] not in (None, 0):
            row["ratio"] = pe_value / row["external_value"]
            row["delta"] = pe_value - row["external_value"]
        else:
            row["ratio"] = None
            row["delta"] = None
        row["annotations"] = annotation_ids(annotations, row)
        out_rows.append(row)

    by_status = {}
    by_relationship = {}
    for r in out_rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        rel = r["calibration_relationship"]
        by_relationship[rel] = by_relationship.get(rel, 0) + 1

    comparison = {
        "built": str(date.today()),
        "source_meta": json.loads(
            (ROOT / "sources" / "urban-sotsn" / "source.json").read_text()
        ),
        "pe_bundle": pe_meta.get("bundle", {}),
        "pe_runs": pe_meta.get("runs", {}),
        "annotations": {a["id"]: a for a in annotations},
        "summary": {
            "n_rows": len(out_rows),
            "by_status": by_status,
            "by_relationship": by_relationship,
        },
        "rows": out_rows,
    }
    out = DATA / "comparison.json"
    out.write_text(json.dumps(comparison))
    print(f"{len(out_rows)} rows -> {out}")
    print("by status:", json.dumps(by_status, indent=2))

    # Headline sanity block (national, total rows)
    for prog, metric in [
        ("snap", "participation_rate"), ("ssi", "participation_rate"),
        ("tanf", "participation_rate"), ("wic", "participation_rate"),
        ("housing", "participation_rate"),
        ("snap", "eligible_count"), ("eitc", "eligible_count"),
        ("spm_poverty", "poverty_rate_relative_change_fullpart"),
    ]:
        for r in out_rows:
            if (
                r["program"] == prog and r["metric"] == metric
                and r["geography"] == "US" and r["subgroup"] in ("total",)
                and r["variant"] is None
            ):
                print(
                    f"  {prog:12s} {metric:38s} urban={r['external_value']!r} "
                    f"pe={r['pe_value']!r} status={r['status']}"
                )


if __name__ == "__main__":
    main()
