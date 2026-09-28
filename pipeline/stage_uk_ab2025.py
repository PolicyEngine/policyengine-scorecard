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
STAGING_TALLY.json with its reason (and one receipt line per claim in
STAGING_UNANSWERED.jsonl), never guessed. A claim in the OBR costings slice (it
carries ``obr_measure_key``) belongs to that lane's compute and is tallied
``owned_elsewhere`` here, never attached: one claim, one computed answer. A
measure whose lever never bites in any year of the run is tallied inert; a year
before a measure's RECORDED commencement (registry ``commences_fy``) attaches
its real zero, annotated; identical worlds in any other year assert nothing.

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
# one line per claim the stager did not answer, with its reason (the receipt
# behind the tally's counts)
UNANSWERED = ARTIFACTS / "STAGING_UNANSWERED.jsonl"
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
                # engine's gov_tax / gov_spending do not carry this head (a
                # loan repayment, a devolved payment), so the exchequer effect
                # is read from the head itself, receipts positive and outlays
                # negative; a head with no recorded side is not guessed
                moved = {
                    h: T["reform"]["heads"][h] - T["baseline"]["heads"][h]
                    for h in T["baseline"]["heads"]
                    if T["reform"]["heads"].get(h) != T["baseline"]["heads"].get(h)
                }
                unknown = sorted(h for h in moved if h not in HEAD_SIDE)
                if unknown:
                    raise Unanswerable(
                        f"exchequer aggregates do not carry the measure's head variables {unknown} on the certified engine, and the head's side (receipt or outlay) is not recorded"
                    )
                eff = sum(
                    d if HEAD_SIDE[h] == "receipt" else -d for h, d in moved.items()
                )
                return (
                    sign * eff,
                    [
                        "PE static exchequer effect read from the head variable(s) "
                        + ", ".join(f"{h} ({HEAD_SIDE[h]})" for h in sorted(moved))
                        + ", which gov_tax / gov_spending do not carry on the certified engine",
                        snote,
                    ],
                    None,
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


def identical_worlds(art: dict) -> bool:
    """True when the artifact's reform world equals its baseline world on
    gov_tax, gov_spending, household_net_income and every head variable (the
    decile and poverty blocks are not compared: they are functions of the
    same frames)."""
    b, r = art["totals"]["baseline"], art["totals"]["reform"]
    return all(
        b.get(k) == r.get(k)
        for k in ("gov_tax", "gov_spending", "household_net_income")
    ) and all(
        b.get("heads", {}).get(h) == r.get("heads", {}).get(h)
        for h in b.get("heads", {})
    )


INERT = "lever inert on the certified world in every year of the run (reform world identical to the baseline world)"


def inert_measures(
    artifacts: dict[tuple[str, int], dict],
    years: list[int],
    commences: dict[str, str] | None = None,
) -> set[str]:
    """Measures whose reform world equals the baseline world in EVERY year of
    the run: the lever did not bite on the certified engine and data (a switch
    the engine ignores, a data-driven variable, a world that is already current
    law). Their claims are tallied, never attached as zeros. Sound only over
    the FULL run, so a measure whose artifacts do not cover every run year
    raises (a --years subset would call the threshold freeze inert). A measure
    identical in every year because it commences after the run is not inert."""
    commences = commences or {}
    by_key: dict[str, dict[int, bool]] = {}
    for (key, year), art in artifacts.items():
        by_key.setdefault(key, {})[year] = identical_worlds(art)
    out = set()
    for key, same in by_key.items():
        if sorted(same) != sorted(years):
            raise ValueError(
                f"{key}: artifacts for {sorted(same)}, the run is {sorted(years)}: "
                "inertness is only judged over the full run"
            )
        c = commences.get(key)
        if c and int(c[:4]) > max(years):
            continue
        if all(same.values()):
            out.add(key)
    return out


def identical_year_verdict(
    fy: str, commences_fy: str | None
) -> tuple[str | None, str | None]:
    """(annotation, None) when identical worlds in ``fy`` are a real zero —
    the year is before the measure's RECORDED commencement (registry
    ``commences_fy``, from the HM Treasury Table 4.1 title) — else
    (None, reason): identical worlds in a year the measure is in force, or
    with no commencement on record, are a construction that does not carry
    the measure, and no zero is asserted."""
    if commences_fy and fy < commences_fy:
        return (
            f"not yet in force in FY {fy}: the measure commences in FY {commences_fy} "
            "(registry commences_fy) and the reform and baseline worlds are identical "
            "in this year; the counterpart is zero",
            None,
        )
    if commences_fy:
        return (
            None,
            f"reform and baseline worlds identical in FY {fy}, a year the measure is in "
            f"force (commences FY {commences_fy}): the construction does not carry it "
            "in this year, so no zero is asserted",
        )
    return (
        None,
        "reform and baseline worlds identical and no commencement on record: no zero is asserted",
    )


# heads the certified engine's gov_tax / gov_spending aggregates do NOT carry:
# an exchequer effect for these measures is read from the head itself
HEAD_SIDE = {
    "student_loan_repayment": "receipt",
    "scottish_child_payment": "outlay",
}


def owned_elsewhere(cond: dict) -> str | None:
    """The #56 / #140 ownership rule: a claim carrying ``obr_measure_key`` is
    in the OBR costings slice and is answered only by that lane's compute
    (pipeline/compute_uk_obr_costings.py, per OBR head in OBR's conventions);
    this stager never attaches to it, so no claim gets two computed answers."""
    if cond.get("obr_measure_key"):
        return "owned by the OBR costings lane (claim carries obr_measure_key)"
    return None


def stage(
    db_path: Path, artifacts: dict | None = None, years: list[int] | None = None
) -> tuple[list[dict], dict, list[dict]]:
    from_disk = artifacts is None
    artifacts = artifacts or load_artifacts()
    index = {m["measure_key"]: m for m in json.loads(REGISTRY.read_text())["measures"]}
    alias = {
        k: str(m.get("construction")).removeprefix("same_lever_as_")
        for k, m in index.items()
        if str(m.get("construction", "")).startswith("same_lever_as_")
    }
    conn = sqlite3.connect(db_path)
    rows = []
    if years is None:
        years = (
            json.loads((ARTIFACTS / "RUN_MANIFEST.json").read_text())["years"]
            if from_disk
            else sorted({y for _, y in artifacts})
        )
    commences = {
        k: m["commences_fy"] for k, m in index.items() if m.get("commences_fy")
    }
    inert = inert_measures(artifacts, years, commences)
    tally: dict = {
        "attached": 0,
        "owned_elsewhere": 0,
        "unmapped": {},
        "inert_measures": sorted(inert),
        "by_measure": {},
    }
    unanswered: list[dict] = []

    def receipt(c: dict, key: str, reason: str) -> None:
        bm = tally["by_measure"][key]
        bm["reasons"][reason] = bm["reasons"].get(reason, 0) + 1
        unanswered.append(
            {
                "claim_id": c["claim_id"],
                "measure_key": key,
                "source": c["source"],
                "metric": c["metric"],
                "fy": c["conditions"].get("fy"),
                "reason": reason,
            }
        )

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
                "reasons": {},
            },
        )
        bm["claims"] += 1
        owner = owned_elsewhere(c["conditions"])
        if owner:
            bm["owned_elsewhere"] += 1
            tally["owned_elsewhere"] += 1
            receipt(c, key, owner)
            continue
        # the claim's fiscal year picks the artifact (calendar year = FY
        # start); a claim without one, or outside the run's years, is tallied
        fy = c["conditions"].get("fy") or ""
        m = re.fullmatch(r"(\d{4})-(\d{2})", fy)
        if not m:
            bm["unmapped"] += 1
            reason = "no fiscal year on the claim"
            tally["unmapped"][reason] = tally["unmapped"].get(reason, 0) + 1
            receipt(c, key, reason)
            continue
        year = int(m.group(1))
        # a year the registry itself marks non-comparable (the claim measures
        # something no household microsimulation carries) is never answered
        nc = (index.get(target) or {}).get("non_comparable_fys", {}).get(fy)
        if nc:
            bm["unmapped"] += 1
            reason = f"not comparable in FY {fy} per the registry: {nc}"
            tally["unmapped"][reason] = tally["unmapped"].get(reason, 0) + 1
            receipt(c, key, reason)
            continue
        art = artifacts.get((target, year))
        if art is None:
            bm["no_artifact"] += 1
            reason = f"no artifact for the claim's fiscal year ({fy})"
            tally["unmapped"][reason] = tally["unmapped"].get(reason, 0) + 1
            receipt(c, key, reason)
            continue
        if target in inert:
            bm["unmapped"] += 1
            tally["unmapped"][INERT] = tally["unmapped"].get(INERT, 0) + 1
            receipt(c, key, INERT)
            continue
        not_yet = []
        if identical_worlds(art):
            note, gap = identical_year_verdict(fy, commences.get(target))
            if gap:
                bm["unmapped"] += 1
                tally["unmapped"][gap] = tally["unmapped"].get(gap, 0) + 1
                receipt(c, key, gap)
                continue
            not_yet = [note]
        value, notes, reason = map_claim(c, art)
        period_note = []
        if c["period"] is None or int(c["period"]) != year + 1:
            period_note = [
                f"claim period {c['period']} is the FY START year (the known IFS/RF follow-up); matched on fy {fy}"
            ]
        if reason:
            bm["unmapped"] += 1
            tally["unmapped"][reason] = tally["unmapped"].get(reason, 0) + 1
            receipt(c, key, reason)
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
                + not_yet
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
    unanswered.sort(key=lambda r: (r["measure_key"], r["claim_id"]))
    return rows, tally, unanswered


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    db = Path(argv[0] if argv else "data/scorecard.db")
    rows, tally, unanswered = stage(db)
    STAGED_DIR.mkdir(parents=True, exist_ok=True)
    STAGED.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in rows) + ("\n" if rows else "")
    )
    TALLY.write_text(json.dumps(tally, indent=1, sort_keys=True) + "\n")
    UNANSWERED.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in unanswered)
        + ("\n" if unanswered else "")
    )
    print(
        json.dumps(
            {"attached": tally["attached"], "unmapped": tally["unmapped"]}, indent=1
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
