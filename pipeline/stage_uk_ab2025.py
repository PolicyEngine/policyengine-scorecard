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
STAGING_TALLY.json with its reason, never guessed.

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
    if measure_key in PACKAGE_WORLDS:
        label = PACKAGE_WORLDS[measure_key]
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


def _sign(cond: dict) -> tuple[int, str]:
    text = (cond.get("sign_convention") or "").lower()
    if "cost" in text and (
        "positive = cost" in text
        or "positive = a cost" in text
        or "positive cost" in text
    ):
        return -1, "claim sign: positive = cost; PE oriented to it"
    return (
        1,
        "claim sign: positive = yield to the Exchequer (default; HMT prints costs negative)",
    )


def _group(cond: dict) -> tuple[str, int | None]:
    g = cond.get("income_group") or "all"
    m = re.fullmatch(r"(decile|vigintile)_(\d+)", g)
    if m:
        return m.group(1), int(m.group(2))
    if g == "all":
        return "all", None
    raise LookupError(f"income_group {g!r} is not a decile, vigintile or all")


def _basis(cond: dict, default: str) -> tuple[str, str]:
    hc = (cond.get("housing_costs") or "").lower()
    if hc in ("ahc", "bhc"):
        return hc, f"housing basis {hc.upper()} as the claim states"
    axis = (cond.get("income_axis") or "").lower()
    if "after housing" in axis or "ahc" in axis:
        return "ahc", "housing basis AHC from the claim's income axis"
    return (
        default,
        f"housing basis {default.upper()} ASSUMED (the claim does not state it)",
    )


def _group_row(art: dict, cond: dict, default_basis: str):
    kind, n = _group(cond)
    basis, note = _basis(cond, default_basis)
    dist = art["distribution"]
    if kind == "all":
        return dist["all"], basis, note
    rows = dist[f"{basis}_{kind}"]
    return rows[n - 1], basis, note


def _threshold(cond: dict) -> float:
    t = (cond.get("threshold") or "").lower()
    m = re.search(r"(\d+(?:\.\d+)?)_percent", t)
    return float(m.group(1)) / 100 if m else 0.0


def _poverty(art: dict, cond: dict, unit: str):
    basis, bnote = _basis(cond, "ahc")
    line = (cond.get("poverty_line") or "relative_60_median").lower()
    if "absolute" in line:
        key = f"absolute_{basis}"
    elif (
        "fixed" in line
        or (cond.get("scenario") or "") == "reform_minus_baseline"
        and "fixed" in json.dumps(cond).lower()
    ):
        key = f"relative_60_median_fixed_at_baseline_{basis}"
    else:
        key = f"relative_60_median_moving_{basis}"
    who = (
        "children"
        if unit in ("children", "children_under_18")
        or (cond.get("unit_population") or cond.get("subgroup") or "")
        .lower()
        .startswith("child")
        else "people"
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
                return (
                    None,
                    [],
                    "OBR head-level costing row: the OBR costings lane (#56) answers per head",
                )
            sign, snote = _sign(cond)
            eff = (T["reform"]["gov_tax"] - T["baseline"]["gov_tax"]) - (
                T["reform"]["gov_spending"] - T["baseline"]["gov_spending"]
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
            b, r, who, note = _poverty(art, cond, unit)
            if metric == "poverty_count_change":
                return r - b, [f"{who} in poverty, {note}"], None
            pop = (
                T["baseline"]["children"]
                if who == "children"
                else T["baseline"]["people"]
            )
            return (
                100.0 * (r - b) / pop,
                [f"{who} poverty rate change in percentage points, {note}"],
                None,
            )
        if metric == "average_household_income_change":
            row, basis, note = _group_row(art, cond, "bhc")
            per_hh = (row["hni_reform"] - row["hni_baseline"]) / row["households"]
            if unit == "gbp_per_week":
                per_hh /= 52.0
            elif unit not in ("gbp", "gbp_per_household", ""):
                return None, [], f"unit {unit!r} for an income change"
            return (
                per_hh,
                [
                    f"mean change in household net income per household in the group ({note})"
                ],
                None,
            )
        if metric == "pct_change_after_tax_income":
            row, basis, note = _group_row(art, cond, "bhc")
            return (
                100.0 * (row["hni_reform"] - row["hni_baseline"]) / row["hni_baseline"],
                [f"per cent change in the group's household net income ({note})"],
                None,
            )
        if metric in ("share_gaining", "share_losing", "share_no_change"):
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
            world = "reform" if cond.get("scenario") == "reform" else "baseline"
            return (
                row[f"hni_{world}"] / art["distribution"]["all"][f"hni_{world}"],
                [f"group share of household net income in the {world} world ({note})"],
                None,
            )
        if metric == "affected_count":
            who = "households" if unit == "households" else "people"
            return (
                art["affected"][who],
                [f"{who} whose head variables moved by more than 50p"],
                None,
            )
    except (KeyError, LookupError, ZeroDivisionError) as e:
        return None, [], f"{metric}: {e}"
    return None, [], f"no counterpart shape for metric {metric!r}"


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
    tally: dict = {"attached": 0, "unmapped": {}, "by_measure": {}}
    for c in claims(conn):
        key = c["conditions"]["measure_key"]
        target = alias.get(key, key)
        art = artifacts.get((target, int(c["period"]) - 1))
        bm = tally["by_measure"].setdefault(
            key, {"claims": 0, "attached": 0, "no_artifact": 0, "unmapped": 0}
        )
        bm["claims"] += 1
        if art is None:
            bm["no_artifact"] += 1
            continue
        value, notes, reason = map_claim(c, art)
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
                "annotations": [
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
