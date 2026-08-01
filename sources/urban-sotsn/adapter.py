"""Adapter: Urban Institute State of the Safety Net -> tidy external rows.

Input:  raw/sotsn_map.json — the webtool's own data file (52 geographies x
        586 columns), fetched from apps.urban.org.
Output: data/externals/urban-sotsn.json — tidy rows in the scorecard schema.

Column grammar (verified against the full 586-column inventory):
    {program}_base_{metric}_{unit}_{subgroup}_2023
    base_spm_pov_rate_100_pop_{total,child}_2023
    fullpart[_change]_spm_pov_{rate,num}_100_pop_{total,child}_2023

Value semantics (verified against Urban's published headline numbers):
    - counts are in THOUSANDS (snap eligible US = 69128 -> 69.128M),
      except fullpart_change_spm_pov_num_* which is raw persons (-15391000)
    - rates are fractions 0-1 (0.575 = 57.5%)
    - part_gap = count of eligible non-participants, thousands
    - '.' = suppressed cell
    - *_2023_1 columns are exact duplicates -> dropped
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "urban-sotsn"

PROGRAMS = [
    "ctc_refund",  # longest prefixes first
    "ccdf",
    "housing",
    "liheap",
    "snap",
    "ssi",
    "tanf",
    "wic",
    "eitc",
]

METRICS = {
    "elig_rate": "eligibility_rate",
    "elig": "eligible_count",
    "part_rate": "participation_rate",
    "part_gap": "participation_gap_count",
}

# What each program's counting unit means in Urban's publication
# (denominators verified numerically: e.g. housing 16.781M / 0.128 = 131M
# households; eitc 18.445M / 0.106 = 174M tax units; wic 9.444M / 0.517 =
# 18.3M children under 5; ssi 12.602M / 0.05 = 252M adults 18+).
UNIT_CONCEPTS = {
    ("snap", "pop"): "persons",
    ("ssi", "pop"): "adults_18plus",
    ("tanf", "pop"): "persons",
    ("tanf", "units"): "families",
    ("wic", "pop"): "children_0thr4",
    ("ccdf", "pop"): "children_under_13",
    ("housing", "units"): "households",
    ("liheap", "units"): "households",
    ("eitc", "units"): "tax_units",
    ("ctc_refund", "units"): "tax_units",
}

POVERTY_COLS = {
    "base_spm_pov_rate_100_pop_total": ("poverty_rate", "total"),
    "base_spm_pov_rate_100_pop_child": ("poverty_rate", "child"),
    "fullpart_spm_pov_rate_100_pop_total": ("poverty_rate_fullpart", "total"),
    "fullpart_spm_pov_rate_100_pop_child": ("poverty_rate_fullpart", "child"),
    "fullpart_change_spm_pov_rate_100_pop_total": (
        "poverty_rate_relative_change_fullpart", "total",
    ),
    "fullpart_change_spm_pov_rate_100_pop_child": (
        "poverty_rate_relative_change_fullpart", "child",
    ),
    "fullpart_change_spm_pov_num_100_pop_total": (
        "poverty_count_change_fullpart", "total",
    ),
    "fullpart_change_spm_pov_num_100_pop_child": (
        "poverty_count_change_fullpart", "child",
    ),
}

VARIANTS = ("with_SSF", "no_SSF")


def parse_column(col):
    """Return a row template dict, or None for non-data columns."""
    if col in ("state_fips", "state_name", "state_abbreviation"):
        return None
    if col.endswith("_2023_1"):  # exact duplicates of the _2023 columns
        return None
    name = re.sub(r"_2023$", "", col)

    if name in POVERTY_COLS:
        metric, subgroup = POVERTY_COLS[name]
        raw_count = metric == "poverty_count_change_fullpart"
        return {
            "program": "spm_poverty",
            "metric": metric,
            "unit": "pop",
            "unit_concept": "persons" if subgroup == "total" else "children",
            "subgroup": subgroup,
            "variant": None,
            "is_rate": not raw_count,
            "scale": 1,  # poverty numbers are raw persons or fractions
        }

    program = next((p for p in PROGRAMS if name.startswith(p + "_base_")), None)
    if program is None:
        raise ValueError(f"unparsed column: {col}")
    rest = name[len(program) + len("_base_"):]
    metric_slug = next(
        (m for m in ("elig_rate", "elig", "part_rate", "part_gap")
         if rest == m or rest.startswith(m + "_")),
        None,
    )
    if metric_slug is None:
        raise ValueError(f"unparsed metric in: {col}")
    rest = rest[len(metric_slug):].lstrip("_")

    variant = None
    for v in VARIANTS:
        if rest.endswith("_" + v):
            variant = v
            rest = rest[: -len(v) - 1]
            break

    if rest.startswith("pop"):
        unit, sub = "pop", rest[3:].lstrip("_")
    elif rest.startswith("units"):
        unit, sub = "units", rest[5:].lstrip("_")
    else:
        # e.g. snap_base_part_rate_child_60plus_dis — unit implied by program
        unit = "pop" if (program, "pop") in UNIT_CONCEPTS else "units"
        sub = rest
    subgroup = sub or "total"

    is_rate = metric_slug in ("elig_rate", "part_rate")
    return {
        "program": program,
        "metric": METRICS[metric_slug],
        "unit": unit,
        "unit_concept": UNIT_CONCEPTS.get((program, unit), unit),
        "subgroup": subgroup,
        "variant": variant,
        "is_rate": is_rate,
        "scale": 1 if is_rate else 1000,  # counts published in thousands
    }


def run():
    raw = json.loads((HERE / "raw" / "sotsn_map.json").read_text())
    rows = []
    parse_errors = []
    for rec in raw:
        geo = rec["state_abbreviation"]
        for col, val in rec.items():
            try:
                t = parse_column(col)
            except ValueError as e:
                parse_errors.append(str(e))
                continue
            if t is None:
                continue
            suppressed = isinstance(val, str)
            rows.append(
                {
                    "source": SOURCE_ID,
                    "program": t["program"],
                    "metric": t["metric"],
                    "subgroup": t["subgroup"],
                    "variant": t["variant"],
                    "geography": geo,
                    "unit_concept": t["unit_concept"],
                    "period": (
                        "2023"
                        if t["program"] == "spm_poverty"
                        else "2023 average month"
                    ),
                    "value": (
                        None if suppressed else float(val) * t["scale"]
                    ),
                    "status": "suppressed" if suppressed else "ok",
                    "source_column": col,
                }
            )
    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows))
    print(f"{len(rows)} rows -> {out}")
    if parse_errors:
        print(f"PARSE ERRORS ({len(set(parse_errors))} unique):")
        for e in sorted(set(parse_errors)):
            print(" ", e)
        raise SystemExit(1)

    # --- validation against Urban's published headline numbers ---
    def get(program, metric, geo="US", subgroup="total", variant=None):
        for r in rows:
            if (
                r["program"] == program
                and r["metric"] == metric
                and r["geography"] == geo
                and r["subgroup"] == subgroup
                and r["variant"] == variant
            ):
                return r["value"]
        raise KeyError((program, metric, geo, subgroup, variant))

    checks = [
        ("snap eligible 69.128M", get("snap", "eligible_count"), 69_128_000),
        ("snap part rate 57.5%", get("snap", "participation_rate"), 0.575),
        ("ssi eligible 12.602M", get("ssi", "eligible_count"), 12_602_000),
        ("wic part rate 53.5%", get("wic", "participation_rate"), 0.535),
        ("liheap part rate 17.2%", get("liheap", "participation_rate"), 0.172),
        (
            "tanf units rate no-SSF 19%",
            get("tanf", "participation_rate", variant="no_SSF"),
            0.19,
        ),
        (
            "eitc eligible 18.445M",
            get("eitc", "eligible_count"),
            18_445_000,
        ),
        (
            "poverty change -15.391M",
            get("spm_poverty", "poverty_count_change_fullpart"),
            -15_391_000,
        ),
        (
            "child pov rel change -43.6%",
            get(
                "spm_poverty",
                "poverty_rate_relative_change_fullpart",
                subgroup="child",
            ),
            -0.436,
        ),
    ]
    ok = True
    for label, got, want in checks:
        good = got is not None and abs(got - want) < abs(want) * 1e-6 + 1e-9
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'} {label}: {got}")
    if not ok:
        raise SystemExit(1)
    print("all validations passed")


if __name__ == "__main__":
    run()
