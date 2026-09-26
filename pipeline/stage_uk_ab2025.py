"""Stage PolicyEngine counterparts for Autumn Budget 2025 claims (#136, tranche 3).

Reads the artifacts `pipeline/compute_uk_ab2025.py` wrote (one per measure
and calendar year) and the claims in the built DB whose
`conditions.measure_key` is a registry measure, and writes the campaign
staging `ingest_campaign` attaches: one row per claim that a computed
quantity can answer, in the strict claim_id-direct form, carrying the
world PE EXECUTED as `baseline_key`.

Every row is `constructed`: the certified world's calendar year proxies
the claim's fiscal year, PE is static where the producer may be
behavioural, and a reversal executes a registered pre-measure world
rather than the producer's counterfactual. The axes are named in
`annotations`. A claim shape no computed quantity answers is tallied in
STAGING_TALLY.json with its reason, never guessed. A claim in the OBR costings
slice (it carries ``obr_measure_key``) belongs to that lane's compute and is
tallied ``owned_elsewhere`` here, never attached: one claim, one computed answer.

Shapes answered (metric -> artifact quantity):
    revenue_change (geography UK, no OBR head)  -> Δ(gov_tax − gov_spending), oriented by the claim's sign_convention
    poverty_count_change / poverty_rate_change   -> persons or children in poverty, on the claim's line and basis
    average_household_income_change (income_group) -> Δ household net income per household in the group
    pct_change_after_tax_income (income_group)   -> Δ household net income / baseline, per cent
    share_gaining / share_losing / share_no_change -> households over the claim's threshold / households
    income_share (income_group)                  -> the group's household net income / total
    affected_count (persons or households)       -> the population whose head variables moved

    PYTHONPATH=. uv run python pipeline/stage_uk_ab2025.py data/scorecard.db
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scorecard_db.baselines import BASELINES  # noqa: E402
from scorecard_db.models import BASELINE, baseline_key  # noqa: E402

ARTIFACTS = ROOT / "results" / "uk" / "ab2025"
STAGED_DIR = ROOT / "results" / "uk" / "staged_ab2025"
STAGED = STAGED_DIR / "ab2025_counterparts.jsonl"
TALLY = ARTIFACTS / "STAGING_TALLY.json"
REGISTRY = ROOT / "data" / "uk" / "ab2025_measures.json"

_LABELS = {label: baseline_key(desc) for desc, label, *_ in BASELINES}
_CURRENT_LAW = BASELINE.baseline_key()
PACKAGE_WORLDS = {
    "ab2025__package_ifs_decile_chart_scope": "pre_ab2025__package_ifs_decile_chart_scope",
    "ab2025__package_ukmod_wp3_26": "pre_ab2025__package_ukmod_wp3_26",
}


def executed_world_key(measure_key: str, artifact: dict) -> str:
    """The registered world PE executed as the baseline for this artifact."""
    if artifact["baseline_world"]["reform_dict"] is None:
        return _CURRENT_LAW
    construction = str(artifact.get("construction") or "")
    if measure_key in PACKAGE_WORLDS:
        label = PACKAGE_WORLDS[measure_key]
    elif "_variant_of_" in construction:
        # a variant scored on another measure's pre-Budget path (the two-year
        # threshold freeze on the announced freeze's indexed path): the
        # executed baseline IS that measure's registered world
        base = construction.split("_variant_of_", 1)[1]
        label = f"pre_ab2025__{base.removeprefix('ab2025__')}"
    else:
        slug = measure_key.removeprefix("ab2025__")
        label = f"pre_ab2025__{slug}"
        if label not in _LABELS and slug == "uc_child_element_remove_two_child_limit":
            label = "pre_ab2025"
    if label not in _LABELS:
        raise ValueError(f"{measure_key}: executed world {label!r} is not registered")
    return _LABELS[label]


def load_artifacts() -> dict[tuple[str, int], dict]:
    out = {}
    for p in sorted(ARTIFACTS.glob("*_20[0-9][0-9].json")):
        a = json.loads(p.read_text())
        a["_path"] = str(p.relative_to(ROOT))
        out[(a["measure_key"], a["year"])] = a
    return out


def claims(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT claim_id, source, metric, period, unit_concept, value, conditions"
        " FROM external_scores WHERE json_extract(conditions, '$.measure_key') LIKE 'ab2025%'"
    ).fetchall()
    return [
        {
            "claim_id": r[0],
            "source": r[1],
            "metric": r[2],
            "period": r[3],
            "unit": r[4],
            "value": r[5],
            "conditions": json.loads(r[6]),
        }
        for r in rows
    ]


# --- shape mapping ------------------------------------------------------------


class Unanswerable(LookupError):
    """A claim shape no computed quantity answers: tallied with its reason,
    never defaulted. A wrong sign or unit is worse than a gap."""


# --- closed vocabularies -------------------------------------------------------
# The sign convention a producer states, read against PE's own orientation
# (a positive exchequer effect is a yield; a positive poverty change is more
# people in poverty). Phrasings are matched as lower-case substrings of the
# claim's `sign_convention`; anything outside the lists is UNANSWERABLE.
YIELD_POSITIVE = (
    "positive = yield to the exchequer",
    "positive = revenue yield",
    "positive = yield / reduction in borrowing",
    "here we present higher taxes as positive numbers",
    "positive = higher government revenue",
    "positive = net gain to the exchequer",
    "(positive = yield)",
    "(positive = increase in yield)",
    "(positive = reduction in borrowing)",
    "(positive = reduction in welfare spending)",
)
COST_POSITIVE = (
    "positive = cost to the exchequer",
    "positive = increase in borrowing",
    "a positive sign implies an increase in borrowing",
    "a negative figure means a reduction in psnb",
    "positive = cost / increase in borrowing",
)
# Component adjustments a static exchequer effect does not answer (a
# reduction in a yield from a behavioural or timing adjustment, receipts
# brought forward): recognised so the tally names them.
ADJUSTMENT_PHRASINGS = (
    "reduction in yield",
    "reduction in the static yield",
    "reduce the static costing",
    "brought forward",
)
POVERTY_INCREASE_POSITIVE = (
    "positive = more people in poverty",
    "positive = additional children in poverty",
    "positive = children in poverty because of",
    "positive = children kept in poverty",
)
POVERTY_REDUCTION_POSITIVE = (
    "lifted out of poverty",
    "brought out of poverty",
    "fewer children in poverty",
    "prevented from being drawn into poverty",
    "reduction in the child poverty rate",
    "'lift ... out of poverty'",
)
POVERTY_LINES = {
    "relative_60_median": "relative_60_median_moving",
    "fixed_at_baseline": "relative_60_median_fixed_at_baseline",
    "absolute_60_fye2011_median": "absolute",
}
INCOME_CHANGE_UNITS = {
    "gbp": 1.0,
    "gbp_per_household": 1.0,
    "gbp_per_week": 1.0 / 52.0,
    "gbp_per_month": 1.0 / 12.0,
}


def _sign(cond: dict) -> tuple[int, str]:
    text = (cond.get("sign_convention") or "").lower()
    if not text:
        raise Unanswerable("no sign convention on the claim")
    if any(k in text for k in ADJUSTMENT_PHRASINGS):
        raise Unanswerable(
            "claim is a component adjustment to a yield (reduction, timing), "
            "not the measure's exchequer effect"
        )
    if any(k in text for k in COST_POSITIVE):
        return (
            -1,
            "claim sign: positive = cost / increase in borrowing; PE oriented to it",
        )
    if any(k in text for k in YIELD_POSITIVE):
        return 1, "claim sign: positive = yield to the Exchequer, PE's own orientation"
    raise Unanswerable(f"sign convention not recognised: {text[:90]!r}")


def _poverty_sign(cond: dict) -> tuple[int, str]:
    text = (cond.get("sign_convention") or "").lower()
    if not text:
        raise Unanswerable("no sign convention on the poverty claim")
    if any(k in text for k in POVERTY_INCREASE_POSITIVE):
        return 1, "claim sign: positive = more in poverty, PE's own orientation"
    if any(k in text for k in POVERTY_REDUCTION_POSITIVE):
        return -1, "claim sign: positive = fewer in poverty; PE oriented to it"
    raise Unanswerable(f"poverty sign convention not recognised: {text[:90]!r}")


def _group(cond: dict) -> tuple[str, int | None]:
    g = cond.get("income_group") or "all"
    m = re.fullmatch(r"(decile|vigintile)_(\d+)", g)
    if m:
        return m.group(1), int(m.group(2))
    if g == "all":
        return "all", None
    raise Unanswerable(f"income_group {g!r} is not a decile, vigintile or all")


def _basis(cond: dict, default: str | None) -> tuple[str, str]:
    hc = (cond.get("housing_costs") or "").lower()
    if hc in ("ahc", "bhc"):
        return hc, f"housing basis {hc.upper()} as the claim states"
    axis = (cond.get("income_axis") or "").lower()
    if "after housing" in axis or "ahc" in axis:
        return "ahc", "housing basis AHC from the claim's income axis"
    if default is None:
        raise Unanswerable("the claim states no housing basis")
    return (
        default,
        f"housing basis {default.upper()} ASSUMED (the claim does not state it)",
    )


def _group_row(art: dict, cond: dict, default_basis: str | None):
    kind, n = _group(cond)
    basis, note = _basis(cond, default_basis)
    dist = art["distribution"]
    row = dist["all"] if kind == "all" else dist[f"{basis}_{kind}"][n - 1]
    undefined = row.get("undefined_change")
    if undefined:
        note += (
            f"; {undefined:g} households with zero baseline income counted as unchanged"
        )
    return row, basis, note


def _threshold(cond: dict) -> float:
    t = (cond.get("threshold") or "").lower()
    m = re.search(r"(\d+(?:\.\d+)?)_percent", t)
    return float(m.group(1)) / 100 if m else 0.0


def _poverty(art: dict, cond: dict, unit: str):
    basis, bnote = _basis(cond, None)
    line = cond.get("poverty_line")
    if line not in POVERTY_LINES:
        raise Unanswerable(
            f"poverty line {line!r} is not one PE computed (60% lines only)"
        )
    key = f"{POVERTY_LINES[line]}_{basis}"
    sub = (cond.get("unit_population") or cond.get("subgroup") or "").lower()
    counted = unit in ("children", "children_under_18", "persons", "people")
    if unit in ("children", "children_under_18") or sub.startswith("child"):
        who = "children"
    elif (counted and unit in ("persons", "people") or not counted) and sub in (
        "",
        "all",
        "all people",
        "persons",
    ):
        who = "people"  # a count in persons, or a rate with no subgroup
    else:
        raise Unanswerable(
            f"poverty population {unit!r}/{sub!r} is not persons or children"
        )
    b = art["poverty"][f"{key}__baseline"][who]
    r = art["poverty"][f"{key}__reform"][who]
    return b, r, who, f"{key} ({bnote})"


def map_claim(claim: dict, art: dict) -> tuple[float | None, list[str], str | None]:
    """(pe_value, annotations, reason_if_unmapped)."""
    cond = claim["conditions"]
    metric = claim["metric"]
    unit = claim["unit"] or ""
    if cond.get("geography") not in (None, "UK"):
        return None, [], "geography other than UK (no sub-national compute)"
    T = art["totals"]
    try:
        if metric == "revenue_change":
            if any(k in cond for k in ("tax_head", "spending_head", "line_item")):
                raise Unanswerable(
                    "OBR head-level costing row: the OBR costings lane (#56) answers per head"
                )
            if unit != "gbp":
                raise Unanswerable(f"unit {unit!r} for an exchequer effect")
            sign, snote = _sign(cond)
            eff = (T["reform"]["gov_tax"] - T["baseline"]["gov_tax"]) - (
                T["reform"]["gov_spending"] - T["baseline"]["gov_spending"]
            )
            heads_moved = any(
                T["reform"]["heads"].get(h) != T["baseline"]["heads"].get(h)
                for h in T["baseline"].get("heads", {})
            )
            if eff == 0 and heads_moved:
                # the head moved but neither aggregate did: the certified
                # engine's gov_tax / gov_spending do not carry this head
                # (a devolved payment, a loan repayment), so the aggregate
                # exchequer effect is not an answer for this measure
                raise Unanswerable(
                    "exchequer aggregates do not carry the measure's head variables on the certified engine (head moved, gov_tax and gov_spending did not)"
                )
            return (
                sign * eff,
                [
                    "PE static exchequer effect = Δgov_tax − Δgov_spending on the certified world",
                    snote,
                ],
                None,
            )
        if metric in ("poverty_count_change", "poverty_rate_change"):
            sign, snote = _poverty_sign(cond)
            b, r, who, note = _poverty(art, cond, unit)
            if metric == "poverty_count_change":
                return sign * (r - b), [f"{who} in poverty, {note}", snote], None
            if unit != "percentage_points":
                raise Unanswerable(f"unit {unit!r} for a poverty rate change")
            pop = (
                T["baseline"]["children"]
                if who == "children"
                else T["baseline"]["people"]
            )
            return (
                sign * 100.0 * (r - b) / pop,
                [f"{who} poverty rate change in percentage points, {note}", snote],
                None,
            )
        if metric == "average_household_income_change":
            if unit not in INCOME_CHANGE_UNITS:
                raise Unanswerable(f"unit {unit!r} for an income change")
            row, basis, note = _group_row(art, cond, "bhc")
            per_hh = (row["hni_reform"] - row["hni_baseline"]) / row["households"]
            return (
                per_hh * INCOME_CHANGE_UNITS[unit],
                [
                    f"mean change in household net income per household in the group ({note})"
                ],
                None,
            )
        if metric == "pct_change_after_tax_income":
            if unit != "percent":
                raise Unanswerable(f"unit {unit!r} for a per-cent income change")
            row, basis, note = _group_row(art, cond, "bhc")
            return (
                100.0 * (row["hni_reform"] - row["hni_baseline"]) / row["hni_baseline"],
                [f"per cent change in the group's household net income ({note})"],
                None,
            )
        if metric in ("share_gaining", "share_losing", "share_no_change"):
            if unit != "share":
                raise Unanswerable(f"unit {unit!r} for a share of households")
            row, basis, note = _group_row(art, cond, "ahc")
            t = _threshold(cond)
            g = row[f"gaining_over_{t:g}"] / row["households"]
            lo = row[f"losing_over_{t:g}"] / row["households"]
            val = {
                "share_gaining": g,
                "share_losing": lo,
                "share_no_change": 1.0 - g - lo,
            }[metric]
            return (
                val,
                [
                    f"share of households with a change over {t:g} of baseline household net income ({note})"
                ],
                None,
            )
        if metric == "income_share":
            row, basis, note = _group_row(art, cond, "ahc")
            total = art["distribution"]["all"]
            scenario = cond.get("scenario")
            if unit == "share" and scenario in ("baseline", "reform"):
                return (
                    row[f"hni_{scenario}"] / total[f"hni_{scenario}"],
                    [
                        f"group share of household net income in the {scenario} world ({note})"
                    ],
                    None,
                )
            if unit == "percentage_points" and scenario == "reform_minus_baseline":
                delta = (
                    row["hni_reform"] / total["hni_reform"]
                    - row["hni_baseline"] / total["hni_baseline"]
                )
                return (
                    100.0 * delta,
                    [
                        f"change in the group's share of household net income, percentage points ({note})"
                    ],
                    None,
                )
            raise Unanswerable(f"income_share unit {unit!r} with scenario {scenario!r}")
        if metric == "affected_count":
            if not art.get("head_variables"):
                raise Unanswerable(
                    "the measure names no head variables, so the affected population is undefined"
                )
            who = {
                "persons": "people",
                "people": "people",
                "households": "households",
                "children": "children",
            }.get(unit)
            if who is None:
                raise Unanswerable(
                    f"affected population unit {unit!r} is not persons, households or children"
                )
            return (
                art["affected"][who],
                [f"{who} whose head variables moved by more than 50p"],
                None,
            )
    except Unanswerable as e:
        return None, [], f"{metric}: {e}"
    except (KeyError, ZeroDivisionError) as e:
        return None, [], f"{metric}: artifact lacks {e}"
    return None, [], f"no counterpart shape for metric {metric!r}"


def inert(art: dict) -> str | None:
    """An artifact whose reform world is identical to its baseline world on
    every aggregate and every head answers nothing: the lever did not bite on
    the certified engine and data (a data-driven variable, a switch the engine
    ignores, a world that is already current law). Tallied, never attached as
    a zero — a zero counterpart is a claim about the measure, not about the
    engine's reach."""
    b, r = art["totals"]["baseline"], art["totals"]["reform"]
    moved = any(
        b.get(k) != r.get(k)
        for k in ("gov_tax", "gov_spending", "household_net_income")
    ) or any(
        b.get("heads", {}).get(h) != r.get("heads", {}).get(h)
        for h in b.get("heads", {})
    )
    if moved:
        return None
    return "lever inert on the certified world (reform world identical to the baseline world)"


def owned_elsewhere(cond: dict) -> str | None:
    """The #56 / #140 ownership rule: a claim carrying ``obr_measure_key`` is
    in the OBR costings slice and is answered only by that lane's compute
    (pipeline/compute_uk_obr_costings.py, per OBR head in OBR's conventions);
    this stager never attaches to it, so no claim gets two computed answers."""
    if cond.get("obr_measure_key"):
        return "owned by the OBR costings lane (claim carries obr_measure_key)"
    return None


def stage(db_path: Path, artifacts: dict | None = None) -> tuple[list[dict], dict]:
    artifacts = artifacts or load_artifacts()
    index = {m["measure_key"]: m for m in json.loads(REGISTRY.read_text())["measures"]}
    alias = {
        k: str(m.get("construction")).removeprefix("same_lever_as_")
        for k, m in index.items()
        if str(m.get("construction", "")).startswith("same_lever_as_")
    }
    conn = sqlite3.connect(db_path)
    rows = []
    tally: dict = {
        "attached": 0,
        "owned_elsewhere": 0,
        "unmapped": {},
        "by_measure": {},
    }
    for c in claims(conn):
        key = c["conditions"]["measure_key"]
        target = alias.get(key, key)
        bm = tally["by_measure"].setdefault(
            key,
            {
                "claims": 0,
                "attached": 0,
                "no_artifact": 0,
                "unmapped": 0,
                "owned_elsewhere": 0,
            },
        )
        bm["claims"] += 1
        owner = owned_elsewhere(c["conditions"])
        if owner:
            bm["owned_elsewhere"] += 1
            tally["owned_elsewhere"] += 1
            continue
        # the claim's fiscal year picks the artifact (calendar year = FY
        # start); a claim without one, or outside the run's years, is tallied
        fy = c["conditions"].get("fy") or ""
        m = re.fullmatch(r"(\d{4})-(\d{2})", fy)
        if not m:
            bm["unmapped"] += 1
            reason = "no fiscal year on the claim"
            tally["unmapped"][reason] = tally["unmapped"].get(reason, 0) + 1
            continue
        year = int(m.group(1))
        art = artifacts.get((target, year))
        if art is None:
            bm["no_artifact"] += 1
            reason = f"no artifact for the claim's fiscal year ({fy})"
            tally["unmapped"][reason] = tally["unmapped"].get(reason, 0) + 1
            continue
        dead = inert(art)
        if dead:
            bm["unmapped"] += 1
            tally["unmapped"][dead] = tally["unmapped"].get(dead, 0) + 1
            continue
        value, notes, reason = map_claim(c, art)
        period_note = []
        if c["period"] is None or int(c["period"]) != year + 1:
            period_note = [
                f"claim period {c['period']} is the FY START year (the known IFS/RF follow-up); matched on fy {fy}"
            ]
        if reason:
            bm["unmapped"] += 1
            tally["unmapped"][reason] = tally["unmapped"].get(reason, 0) + 1
            continue
        bm["attached"] += 1
        tally["attached"] += 1
        world = executed_world_key(target, art)
        claim_world = c["conditions"].get("baseline_policy") or "current_law"
        rows.append(
            {
                "external_claim_match": {"claim_id": c["claim_id"]},
                "measure_key": key,
                "source": c["source"],
                "metric": c["metric"],
                "pe_value": value,
                "status": "constructed",
                "pe_construction": f"{art['construction']} on the certified world ({', '.join(art['components'])}); artifact {art['_path']}",
                "engine_version": art["engine_version"],
                "data_bundle": art["data_bundle"],
                "computed_at": art["computed_at"],
                "run_id": art["run_id"],
                "baseline_key": world,
                "annotations": period_note
                + [
                    f"PE calendar year {art['year']} on the certified world proxies FY {art['fy_proxy']}; static, no behavioural response",
                    f"executed baseline: {art['baseline_world']['executed']}; the claim is scored against {claim_world}",
                    *notes,
                ]
                + (
                    [
                        f"null registry values executed as {1e100:g} (no limit): {', '.join(art['null_executed_as_no_limit'])}"
                    ]
                    if art.get("null_executed_as_no_limit")
                    else []
                ),
            }
        )
    conn.close()
    rows.sort(key=lambda r: (r["measure_key"], r["external_claim_match"]["claim_id"]))
    return rows, tally


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    db = Path(argv[0] if argv else "data/scorecard.db")
    rows, tally = stage(db)
    STAGED_DIR.mkdir(parents=True, exist_ok=True)
    STAGED.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in rows) + ("\n" if rows else "")
    )
    TALLY.write_text(json.dumps(tally, indent=1, sort_keys=True) + "\n")
    print(
        json.dumps(
            {"attached": tally["attached"], "unmapped": tally["unmapped"]}, indent=1
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
