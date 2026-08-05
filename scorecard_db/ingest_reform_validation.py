"""Ingest the populace reform-validation registry (per-release artifacts).

Third population: the external-checks registry that previously rendered as
calibration-diagnostics' "External checks" tab, now consolidated into the
scorecard. Each ``sources/populace-reform-validation/raw/<release_id>.json``
is one certified populace-us release's ``reform_validation.json``, produced
at the release's exact engine pins — so ingesting all of them yields a
per-release **regression history** in ``pe_results`` (same claim, one result
per release), which the interchange and platform grids don't have.

Mapping (categories -> scorecard vocabulary):

  OBBBA                                   results ATTACH to the harvested
                                          JCX-35-25 claims (canonical per
                                          issue #15) — both the FY2026 and
                                          FY2027 provision claims; a claim
                                          of our own is created only when
                                          the harvest is absent (fresh DBs)
  Federal reform / State reform           REVENUE_CHANGE, policy_ref reform
  State program (repeal construction)     dropped when its benchmark equals
                                          the matching "State program
                                          actual" claim (one result per
                                          claim per release; the direct
                                          level is the better construction);
                                          kept as its OWN claim when the
                                          repeal bundle spans programs
                                          (IL: entangled EITC+CTC)
  State program actual / Fed EITC by st.  BENEFIT_COST, BASELINE
  IRS SOI actual                          TAX_LIABILITY / TAX_CREDITS_APPLIED
  Tax expenditure / JCT tax expenditure   TAX_EXPENDITURE (the reserved
                                          metric's first rows)
  Census state SPM                        POVERTY_RATE (SHARE fractions);
                                          3-year averages carry
                                          period_start/period_end +
                                          conditions["window_kind"]
  Mechanical check                        BENEFIT_COST, policy_ref reform

Claim periods key the year THE CLAIM DESCRIBES, parsed from the benchmark's
window string ("FY2028 (…)" -> 2028 fiscal_year; "TY2023" -> 2023 annual),
not the PE simulation year. Whenever the two diverge — fiscal-year claims
vs calendar-year PE liability, vintage-shifted level backtests, window
averages — the result is status=constructed, never comparable.

Engine pins are per release from each release_manifest.json, with per-row
overrides where an artifact documents them: the l0-refit backfill note
covers 33 rows scored offline at policyengine-us 1.729.0 (8 State-reform
rows, the 18-row federal-EITC-by-state suite, and 7 program levels from
the populace#345 expansion) while the release was built at 1.752.2. OBBBA
scoring mode also differs by release (f0af251 chained a stack of its own;
l0-refit scored provisions in isolation against pre-OBBBA law; buildi
onward stack per JCX) and is recorded in the pe_construction so
cross-release drift can't be confused with a construction change.

calibration_relationship: "JCT tax expenditure" rows are literally labeled
"(calibration target)" in the artifact and IRS SOI totals are on the
certified target surface -> consumed_as_target. Census SPM is a permanent
holdout by doctrine. Fiscal notes, JCT/CBO scores, JCX-48-24/Treasury tax
expenditures, state agency actuals, and IRS EITC Central (TY2024 — a
different vintage/product than the TY2022 SOI targets) -> held_out.

Reform identity: rows don't carry executable reform dicts yet (the param
dicts live in populace's state_reforms.json), so scored rows key off
``policy_ref`` descriptors ``{"policy": <row id>}`` — stable across
releases. Upgrading these to framework="policyengine_us" awaits the populace
payload extension (see the integration issue). The CBO rate-option claim is
scored against a pre-OBBBA baseline and says so in ReformRef.baseline +
conditions["baseline_policy"].

Rows whose benchmark is null (score_type "none": unscoreable expenditures)
are skipped and tallied. Re-ingest is idempotent: every claim this module
creates is marked publication["registry"]="populace_reform_validation" and
replaced wholesale, along with this module's own pe_results (run_id prefix
``populace-rv-``); harvest claims we merely attach results to are never
marked, so they survive. All parsing and validation happens before any
write, and the replacement is a single transaction, so a failure at any
point — parse or write — leaves the DB untouched.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .models import (
    BASELINE,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    ReformRef,
    TimeBasis,
    UnitConcept,
)

REPO = Path(__file__).resolve().parent.parent
RAW = REPO / "sources" / "populace-reform-validation" / "raw"
RUN_PREFIX = "populace-rv-"
REGISTRY_MARK = "populace_reform_validation"

# Exact engine pins per release (from each release_manifest.json on HF;
# the artifact's PE values were computed at these versions).
ENGINE_VERSIONS = {
    "populace-us-2024-f0af251-703bd81a565c-20260620T201958Z": "1.729.0",
    "populace-us-2024-sparse-l0-refit-57k-71a0887-national-only-20260701": "1.752.2",
    "populace-us-2024-buildi-sparse-rmloss100-6e8e929-20260709T034135Z": "1.764.6",
    "populace-us-2024-buildj-sparse-rmloss100-75d5add-20260710T094201Z": "1.764.6",
    "populace-us-2024-buildo-sparse-rmloss100-22bd902-20260722T232627Z": "1.764.6",
}

# Pin overrides an artifact documents about itself, keyed per category and
# per row id. The l0-refit backfill note names three offline batches scored
# at 1.729.0 on the released H5 (the release itself was built at 1.752.2):
# "State reform rows appended offline … at policyengine-us 1.729.0", the
# populace#345 expansion's "7 new program levels (VA/OH/MO/SC EITC-family,
# CO FAC, ID/UT CTC) + 18-row federal EITC by state suite … scored locally
# at pe-us 1.729 on the release H5".
_L0 = "populace-us-2024-sparse-l0-refit-57k-71a0887-national-only-20260701"
_L0_OFFLINE_PROGRAM_LEVELS = (
    "state_va_eitc_cli", "state_oh_eitc", "state_mo_wftc", "state_sc_eitc",
    "state_co_fac", "state_id_ctc", "state_ut_ctc",
)
ENGINE_OVERRIDES = {
    _L0: {
        "categories": {
            "State reform": "1.729.0",
            "Federal EITC by state": "1.729.0",
        },
        "ids": {i: "1.729.0" for i in _L0_OFFLINE_PROGRAM_LEVELS},
    },
}

# How each release scored the OBBBA provisions, recorded in
# pe_construction so a scoring-mode change can't masquerade as
# release-over-release drift. f0af251 is a STACK — within each measure
# group, every provision's baseline_total equals the previous provision's
# reform_total (the estate/gift row interleaves on its own tax head) —
# but not the buildi+ producer stack: its chain runs through the
# pre-scope-fix exemption row and a separate senior-deduction link, so it
# gets its own label. l0-refit's note speaks only for itself: "this
# release's OBBBA effects were scored in isolation against pre-OBBBA law …
# not stacked; the stacked producer applies from the next release"
# (verified: its 17 income-tax rows share one 2,735.78B baseline; the
# estate/gift row is a different tax head).
OBBBA_SCORING_MODE = {
    "populace-us-2024-f0af251-703bd81a565c-20260620T201958Z": (
        "stacked_chained"
    ),
    "populace-us-2024-sparse-l0-refit-57k-71a0887-national-only-20260701": "isolated",
    "populace-us-2024-buildi-sparse-rmloss100-6e8e929-20260709T034135Z": "jcx_stacked",
    "populace-us-2024-buildj-sparse-rmloss100-75d5add-20260710T094201Z": "jcx_stacked",
    "populace-us-2024-buildo-sparse-rmloss100-22bd902-20260722T232627Z": "jcx_stacked",
}

# Registry OBBBA row id -> the JCX-35-25 provision label the harvest keyed
# its claims on (conditions["provision"]). Hand-verified against both the
# FY2026 and FY2027 harvest values; ingest re-verifies numerically and
# fails loudly on drift. This is the issue-#15 resolution: the harvested
# claims are canonical, the registry's per-release PE results attach to
# them instead of minting duplicate jct claims.
OBBBA_PROVISIONS = {
    "obbba_reduced_rates": "1. Extension and limited enhancement of reduced rates [1]",
    "obbba_standard_deduction": "2. Extension and enhancement of increased standard deduction [1]",
    "obbba_personal_exemption_termination": "3. Termination of deduction for personal exemptions other than temporary senior deduction [1]",
    "obbba_child_tax_credit": "4. Extension and enhancement of increased child tax credit [1]",
    "obbba_qbi_deduction": "5. Extension and enhancement of deduction for qualified business income",
    "obbba_estate_gift_exemption": "6. Extension and enhancement of increased estate and gift tax exemption amounts",
    "obbba_amt": "7. Extension of increased alternative minimum tax exemption amounts, modification of phaseout thresholds, and increased threshold phaseout rate",
    "obbba_mortgage_interest_limit": "8. Extension of limitation on deduction for qualified residence interest [1]",
    "obbba_casualty_loss_limit": "9. Extension and modification of limitation on casualty loss deduction [1]",
    "obbba_misc_itemized_deductions": "10. Termination of miscellaneous itemized deductions other than educator expenses",
    "obbba_itemized_tax_benefit_limit": "11. Limitation on tax benefit of itemized deductions",
    "obbba_salt_limit": "20. Limitation on individual deductions for certain State and local taxes [1]",
    "obbba_no_tax_on_tips": "1. No tax on tips (sunset 12/31/28) [5]",
    "obbba_no_tax_on_overtime": "2. No tax on overtime (sunset 12/31/28)",
    "obbba_auto_loan_interest": "3. No tax on car loan interest",
    "obbba_cdcc": "5. Enhancement of child and dependent care tax credit [1]",
    "obbba_charitable_nonitemizer_deduction": "4. Permanent and expanded reinstatement of partial deduction for charitable contributions of individuals who do not elect to itemize",
    "obbba_charitable_floor": "5. 0.5 percent floor on deduction of contributions made by individuals",
}

# Repeal rows whose benchmark deliberately differs from the matching
# "actual" row because neutralizing one program mechanically removes
# others. IL: il_ctc is defined as a percentage of il_eitc, so the repeal
# measures — and its benchmark quotes — the combined EITC+CTC actuals
# (the artifact's own entanglement note). These become their own claims.
REPEAL_BUNDLES = {
    "state_repeal_il_eitc": "il_eitc+il_ctc",
}

# Descriptive conditions the artifacts state about their own benchmarks
# (issue #9: descriptive, never normative). IL's bundle sums an IDOR
# TY2023 EITC actual with the IL GOMB TY2024 CTC budget ESTIMATE ($50M);
# KS HB2629's benchmark is "KDOR's single-tax-year liability simulation
# (-$10.4M on TY2024 data)" for TY2026 policy; UT's benchmark counts
# "amount CLAIMED (avg ~$1,007 = the per-child amount, i.e. pre-offset)"
# while PE's ut_ctc is the nonrefundable, liability-capped credit.
ROW_CONDITIONS = {
    "state_repeal_il_eitc": {
        "data_vintage": "ty2023_eitc_actual+ty2024_ctc_estimate",
    },
    "state.ks.hb2629": {"data_vintage": "ty2024_data"},
    "state_ut_ctc": {"benchmark_concept": "amount_claimed_pre_offset"},
}

# Rows the artifact itself flags as measuring a different concept than the
# PE variable (UT: "treat large errors as a concept flag first") — their
# results are concept_mismatch, never comparable.
STATUS_OVERRIDES = {
    "state_ut_ctc": ComparisonStatus.CONCEPT_MISMATCH,
}

_STATES = {
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "dc", "fl", "ga", "hi",
    "id", "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn",
    "ms", "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh",
    "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa",
    "wv", "wi", "wy",
}

_SOI_TAXES = {
    "income_tax", "alternative_minimum_tax", "net_investment_income_tax",
    "self_employment_tax",
}


def _state_of(row: dict) -> str | None:
    """State code from the row's measure or id prefix, else None."""
    for token in (
        (row["populace"].get("measure") or "").split("_")[0],
        row["id"].removeprefix("state_repeal_").removeprefix("state_")
        .removeprefix("fed_eitc_").split("_")[0],
        row["id"].rsplit("_", 1)[-1],
    ):
        if token in _STATES:
            return token.upper()
    return None


def _publisher(row: dict) -> str:
    src = row["jct"].get("source") or ""
    cat = row["category"]
    if cat in ("IRS SOI actual",):
        return "irs_soi"
    if cat == "Federal EITC by state":
        return "irs"
    if cat == "Census state SPM":
        return "census"
    if cat == "Mechanical check":
        return "census_pep"
    if cat in ("OBBBA", "JCT tax expenditure"):
        return "jct"
    if cat in ("Tax expenditure", "Federal reform"):
        if "JCX" in src or src.startswith("JCT"):
            return "jct"
        if "Treasury" in src:
            return "treasury"
        if "CBO" in src:
            return "cbo"
        raise ValueError(f"cannot derive publisher for {row['id']}: {src!r}")
    state = _state_of(row)
    if state is None:
        raise ValueError(f"cannot derive state for {row['id']}")
    if cat == "State reform":
        return f"{state.lower()}_fiscal_note"
    if cat in ("State program", "State program actual"):
        return f"{state.lower()}_admin"
    raise ValueError(f"unmapped category {cat!r} ({row['id']})")


# The year a claim describes, parsed from the benchmark's window string.
# Returns (period, time_basis, period_start, period_end, window_kind).
_SINGLE_TY = re.compile(r"single tax year (\d{4})")
_AVG_3YR = re.compile(r"^(\d{4})-(\d{4}) 3-year average$")
_BIENNIUM = re.compile(r"\((\d{4})-(\d{2}) biennium")
_FY_SPAN = re.compile(r"\bFY(\d{4})-(\d{2})\b")
_FY = re.compile(r"\bFY(\d{4})\b")
_TY_CY = re.compile(r"\b(?:TY|CY)(\d{4})\b")


def _parse_window(
    window: str | None, fallback: int
) -> tuple[int, TimeBasis, int | None, int | None, str | None]:
    w = (window or "").strip()
    if not w or w.startswith("annual"):
        return fallback, TimeBasis.ANNUAL, None, None, None
    if m := _SINGLE_TY.search(w):
        # JCT FY-straddled scores of a one-year policy ("FY2021+FY2022
        # (single tax year 2021)") describe that tax year.
        return int(m.group(1)), TimeBasis.ANNUAL, None, None, None
    if m := _AVG_3YR.match(w):
        start, end = int(m.group(1)), int(m.group(2))
        return end, TimeBasis.ANNUAL, start, end, "annual_average"
    if m := _BIENNIUM.search(w):
        # "per year (2025-27 biennium ÷ 2)": the 2025-27 biennium spans
        # FY2026+FY2027; the value is the per-fiscal-year average.
        start = int(m.group(1)) + 1
        end = int(m.group(1)) // 100 * 100 + int(m.group(2))
        return end, TimeBasis.FISCAL_YEAR, start, end, "annual_average"
    if m := _FY_SPAN.search(w):
        # "FY2024-25" / "first full year (FY2027-28)": a state fiscal year
        # labeled by both calendar years; period is the ending year.
        end = int(m.group(1)) // 100 * 100 + int(m.group(2))
        return end, TimeBasis.FISCAL_YEAR, None, None, None
    if m := _FY.search(w):
        return int(m.group(1)), TimeBasis.FISCAL_YEAR, None, None, None
    if m := _TY_CY.search(w):
        return int(m.group(1)), TimeBasis.ANNUAL, None, None, None
    if re.fullmatch(r"\d{4}", w):
        return int(w), TimeBasis.ANNUAL, None, None, None
    raise ValueError(f"cannot parse claim period from window {window!r}")


def _map_row(row: dict) -> tuple[ExternalScore, str] | None:
    """(claim, pe_construction) for one artifact row; None -> skip.

    OBBBA and matching-benchmark "State program" repeal rows never reach
    here — ingest() routes them (harvest attachment / drop) first.
    """
    value = row["jct"].get("score")
    if value is None:
        return None
    cat = row["category"]
    measure = row["populace"].get("measure") or ""
    window = row["jct"].get("window")
    period, time_basis, period_start, period_end, window_kind = _parse_window(
        window, int(row["period"])
    )
    conditions: dict[str, str] = {}
    if window_kind:
        conditions["window_kind"] = window_kind
    state = _state_of(row)
    reform: ReformRef = BASELINE
    construction = f"level:{measure}"

    if cat in ("Federal reform", "State reform", "Mechanical check"):
        metric, uc, kind = Metric.REVENUE_CHANGE, UnitConcept.USD, "usd"
        if cat == "Mechanical check":
            metric = Metric.BENEFIT_COST
        baseline = None
        # CBO's rate option (Dec 2024) is scored against pre-OBBBA current
        # law — a non-current baseline that must ride on the ReformRef,
        # mirrored into conditions for queryability.
        if row["id"] == "federal.cbo_rates_plus_1pt":
            baseline = {"policy": "pre_obbba_current_law"}
            conditions["baseline_policy"] = "pre_obbba_current_law"
        reform = ReformRef(
            framework="policy_ref",
            reform={"policy": row["id"], "registry": REGISTRY_MARK},
            baseline=baseline,
        )
        conditions["geography"] = state or "US"
        construction = f"reform_delta:{measure}"
    elif cat == "State program":
        # Only bundle repeals reach here (ingest() drops the rest): the
        # repeal's benchmark quotes combined program actuals, a claim the
        # direct per-program rows don't carry.
        program = REPEAL_BUNDLES[row["id"]]
        metric, uc, kind = Metric.BENEFIT_COST, UnitConcept.USD, "usd"
        conditions["geography"] = state or "US"
        conditions["program"] = program
        construction = f"repeal_delta:{measure}"
    elif cat == "State program actual":
        program = row["id"].removeprefix("state_")
        metric, uc, kind = Metric.BENEFIT_COST, UnitConcept.USD, "usd"
        conditions["geography"] = state or "US"
        conditions["program"] = program
    elif cat == "Federal EITC by state":
        metric, uc, kind = Metric.BENEFIT_COST, UnitConcept.USD, "usd"
        conditions["geography"] = row["id"].rsplit("_", 1)[-1].upper()
        conditions["program"] = "eitc"
    elif cat == "IRS SOI actual":
        uc, kind = UnitConcept.USD, "usd"
        conditions["geography"] = "US"
        if measure in _SOI_TAXES:
            metric = Metric.TAX_LIABILITY
            conditions["tax"] = measure
        else:
            metric = Metric.TAX_CREDITS_APPLIED
            conditions["program"] = measure
    elif cat in ("Tax expenditure", "JCT tax expenditure"):
        metric, uc, kind = Metric.TAX_EXPENDITURE, UnitConcept.USD, "usd"
        conditions["geography"] = "US"
        program = (
            row["id"].split(".")[-2]
            if cat == "JCT tax expenditure"
            else row["id"].removeprefix("te_")
        )
        conditions["program"] = program
        construction = f"repeal_delta:{measure}"
    elif cat == "Census state SPM":
        metric, uc, kind = Metric.POVERTY_RATE, UnitConcept.SHARE, "share"
        geo = row["id"].rsplit("_", 1)[-1]
        conditions["geography"] = geo.upper() if geo != "us" else "US"
        if "child" in row["id"]:
            conditions["subgroup"] = "children_under_18"
    else:
        raise ValueError(f"unmapped category {cat!r} ({row['id']})")

    conditions.update(ROW_CONDITIONS.get(row["id"], {}))
    relationship = "held_out"
    if cat in ("JCT tax expenditure", "IRS SOI actual"):
        relationship = "consumed_as_target"

    return (
        ExternalScore(
            source=_publisher(row),
            metric=metric,
            unit_concept=uc,
            period=period,
            time_basis=time_basis,
            period_start=period_start,
            period_end=period_end,
            value=float(value),
            conditions=conditions,
            reform=reform,
            calibration_relationship=relationship,
            source_column=row["id"],
            publication={
                "title": row["jct"].get("source") or "",
                "url": row["jct"].get("source_url") or "",
                "score_type": row["jct"].get("score_type") or "",
                "window": window or "",
                "name": row.get("name") or "",
                "registry": REGISTRY_MARK,
            },
            value_kind=kind,
        ),
        construction,
    )


def _pe_value(row: dict, construction: str) -> float:
    """The PE computation for a row, by construction.

    Levels live in baseline_total, except in early artifacts (l0-refit and
    before) which wrote the level into budget_effect; deltas always live in
    budget_effect. A mapped row without a value is a producer bug — fail.
    """
    pop = row["populace"]
    if construction.startswith("level:"):
        value = pop.get("baseline_total")
        if value is None:
            value = pop.get("budget_effect")
    else:
        value = pop.get("budget_effect")
    if value is None:
        raise ValueError(f"{row['id']}: no PE value for {construction}")
    return float(value)


def _status(row: dict, claim: ExternalScore, construction: str) -> ComparisonStatus:
    """comparable only when the claim's quantity is what PE computed.

    PE values are single-calendar-year liability at the row's simulation
    period — any fiscal-year claim, vintage-shifted level backtest, window
    average, repeal-delta construction, or stated approximation is
    constructed, not comparable.
    """
    if row["id"] in STATUS_OVERRIDES:
        return STATUS_OVERRIDES[row["id"]]
    sim_period = row["populace"].get("period") or row["period"]
    if (
        row["jct"].get("score_type") in ("approximation", "tax_expenditure")
        # MI HB4170's window is "annual (approximate)" with a fiscal_note
        # score_type — the window's own hedge counts too.
        or "approximate" in (row["jct"].get("window") or "")
        or construction.startswith("repeal_delta")
        or claim.time_basis == TimeBasis.FISCAL_YEAR
        or claim.period != int(sim_period)
        or claim.period_start is not None
    ):
        return ComparisonStatus.CONSTRUCTED
    return ComparisonStatus.COMPARABLE


def _release_timestamp(release_id: str) -> str:
    tail = release_id.rsplit("-", 1)[-1]
    if "T" in tail and len(tail) >= 15:
        return f"{tail[0:4]}-{tail[4:6]}-{tail[6:8]}T{tail[9:11]}:{tail[11:13]}:{tail[13:15]}"
    if len(tail) == 8 and tail.isdigit():  # date-only ids (l0-refit)
        return f"{tail[0:4]}-{tail[4:6]}-{tail[6:8]}T00:00:00"
    raise ValueError(f"cannot parse release timestamp from {release_id!r}")


def _harvest_claim(db: ScorecardDB, provision: str, period: int) -> dict | None:
    rows = db.conn.execute(
        "SELECT claim_id, value FROM external_scores"
        " WHERE source='jct' AND metric='revenue_change'"
        " AND time_basis='fiscal_year' AND period=?"
        " AND json_extract(conditions, '$.bill_version')='JCX-35-25'"
        " AND json_extract(conditions, '$.provision')=?"
        " AND json_extract(publication, '$.registry') IS NULL",
        (period, provision),
    ).fetchall()
    if len(rows) > 1:
        raise ValueError(
            f"ambiguous harvest claim for {provision!r} FY{period}"
        )
    return dict(rows[0]) if rows else None


def _obbba_results(
    db: ScorecardDB, row: dict, release_id: str, engine: str, computed_at: str,
    claims: dict[str, ExternalScore], tallies: dict, validate: bool,
) -> list[PEResult]:
    """Attach the registry's OBBBA computation to the canonical harvest
    claims — the FY2026 provision claim, and the FY2027 one when the
    registry carries that benchmark. Same PE value both times (calendar-2026
    liability), so both are constructed comparisons; the construction names
    the release's scoring mode and the CY-for-FY approximation."""
    provision = OBBBA_PROVISIONS.get(row["id"])
    if provision is None:
        raise ValueError(f"OBBBA row {row['id']} missing from OBBBA_PROVISIONS")
    measure = row["populace"].get("measure") or ""
    mode = OBBBA_SCORING_MODE[release_id]
    pe_value = _pe_value(row, f"reform_delta:{measure}")
    results = []
    for fy, score in (
        (2026, row["jct"].get("score")),
        (2027, row["jct"].get("score_fy2027")),
    ):
        if score is None:
            continue
        found = _harvest_claim(db, provision, fy)
        if found is not None:
            # Guard the id->provision mapping numerically — but only
            # against the latest artifact: its benchmarks carry the 7/06
            # transcription audit (e.g. mortgage FY2027 3,398M -> 3,110M),
            # while older artifacts keep their superseded columns.
            if validate and abs(found["value"] - score) > max(
                2e6, 1e-3 * abs(score)
            ):
                raise ValueError(
                    f"{row['id']} FY{fy}: registry benchmark {score:,.0f}"
                    f" != harvest claim value {found['value']:,.0f}"
                )
            cid = found["claim_id"]
            tallies["obbba_attached_results"] += 1
        else:
            # Fresh DB without the harvest (tests): mint a marked claim so
            # the ingest stays self-contained.
            claim = ExternalScore(
                source="jct",
                metric=Metric.REVENUE_CHANGE,
                unit_concept=UnitConcept.USD,
                period=fy,
                time_basis=TimeBasis.FISCAL_YEAR,
                value=float(score),
                conditions={"geography": "US", "scoring": "conventional"},
                reform=ReformRef(
                    framework="policy_ref",
                    reform={"policy": row["id"], "registry": REGISTRY_MARK},
                ),
                calibration_relationship="held_out",
                source_column=row["id"],
                publication={
                    "title": row["jct"].get("source") or "",
                    "url": row["jct"].get("source_url") or "",
                    "score_type": row["jct"].get("score_type") or "",
                    "window": f"FY{fy}",
                    "name": row.get("name") or "",
                    "registry": REGISTRY_MARK,
                },
                value_kind="usd",
            )
            cid = claim.claim_id()
            if cid not in claims:
                tallies["obbba_fallback_claims"] += 1
            # Newest artifact wins: releases ingest oldest-first and early
            # artifacts carry superseded benchmark columns (mortgage
            # FY2027 3,398M pre-audit vs 3,110M). The value isn't part of
            # claim_id, so overwriting keeps the id stable.
            claims[cid] = claim
        results.append(
            PEResult(
                claim_id=cid,
                computed_value=pe_value,
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=engine,
                data_bundle=release_id,
                pe_construction=(
                    f"reform_delta:{measure}:{mode}:cy2026_for_fy{fy}"
                ),
                run_id=f"{RUN_PREFIX}{release_id}",
                computed_at=computed_at,
            )
        )
    return results


def ingest(db_path: Path, raw_dir: Path | None = None) -> dict:
    raw_dir = raw_dir or RAW
    db = ScorecardDB(db_path)
    claims: dict[str, ExternalScore] = {}
    results: list[PEResult] = []
    skipped: list[str] = []
    tallies = {
        "superseded_repeal_constructions": 0,
        "obbba_attached_results": 0,
        "obbba_fallback_claims": 0,
    }
    releases = sorted(
        raw_dir.glob("*.json"), key=lambda p: _release_timestamp(p.stem)
    )
    if not releases:
        raise SystemExit(f"no artifacts in {raw_dir}")
    for path in releases:
        artifact = json.loads(path.read_text())
        release_id = artifact["release_id"]
        base_engine = ENGINE_VERSIONS.get(release_id)
        if base_engine is None:
            raise SystemExit(
                f"{release_id} missing from ENGINE_VERSIONS — add its "
                "release_manifest.json pin"
            )
        overrides = ENGINE_OVERRIDES.get(release_id, {})
        computed_at = _release_timestamp(release_id)
        actuals = {
            r["id"]: r["jct"].get("score")
            for r in artifact["reforms"]
            if r["category"] == "State program actual"
        }
        for row in artifact["reforms"]:
            if row["jct"].get("score") is None:
                skipped.append(f"{release_id[:20]}…:{row['id']}")
                continue
            engine = (
                overrides.get("ids", {}).get(row["id"])
                or overrides.get("categories", {}).get(row["category"])
                or base_engine
            )
            if row["category"] == "OBBBA":
                results.extend(
                    _obbba_results(
                        db, row, release_id, engine, computed_at, claims,
                        tallies, validate=path == releases[-1],
                    )
                )
                continue
            if row["category"] == "State program":
                actual_id = "state_" + row["id"].removeprefix("state_repeal_")
                if actual_id not in actuals:
                    raise ValueError(f"{row['id']}: no matching actual row")
                if row["id"] not in REPEAL_BUNDLES:
                    # Same external claim as the direct level row, which is
                    # the better construction — keep one result per claim
                    # per release.
                    if row["jct"]["score"] != actuals[actual_id]:
                        raise ValueError(
                            f"{row['id']}: benchmark differs from"
                            f" {actual_id} but is not a known bundle"
                        )
                    tallies["superseded_repeal_constructions"] += 1
                    continue
            mapped = _map_row(row)
            if mapped is None:
                skipped.append(f"{release_id[:20]}…:{row['id']}")
                continue
            claim, construction = mapped
            cid = claim.claim_id()
            claims.setdefault(cid, claim)
            results.append(
                PEResult(
                    claim_id=cid,
                    computed_value=_pe_value(row, construction),
                    status=_status(row, claim, construction),
                    engine_version=engine,
                    data_bundle=release_id,
                    pe_construction=construction,
                    run_id=f"{RUN_PREFIX}{release_id}",
                    computed_at=computed_at,
                )
            )

    seen: set[tuple[str, str]] = set()
    for r in results:
        key = (r.claim_id, r.data_bundle)
        if key in seen:
            raise ValueError(f"duplicate result for claim in release: {key}")
        seen.add(key)
    if tallies["obbba_attached_results"] and tallies["obbba_fallback_claims"]:
        # A partial harvest would silently split provisions between
        # canonical claims and minted fallbacks — refuse the mixed state.
        raise ValueError(
            f"partial JCX-35-25 harvest: "
            f"{tallies['obbba_attached_results']} results attached but "
            f"{tallies['obbba_fallback_claims']} fallback claims minted"
        )

    # All parsing and validation is done — the replacement happens in ONE
    # transaction (deletes, claims, results, lane), so any failure — above
    # or mid-write — leaves the DB exactly as it was. Deletion scope: this
    # module's own results, then every claim it minted last time (marked
    # in publication — never the harvest claims it only attaches results
    # to).
    score_rows = [ScorecardDB.score_row(c) for c in claims.values()]
    result_rows = [ScorecardDB.result_row(r) for r in results]
    n_claims, n_results = len(score_rows), len(result_rows)
    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_results WHERE run_id LIKE ?", (f"{RUN_PREFIX}%",)
        )
        db.conn.execute(
            "DELETE FROM external_scores"
            " WHERE json_extract(publication, '$.registry') = ?",
            (REGISTRY_MARK,),
        )
        db.conn.executemany(SCORES_SQL, score_rows)
        db.conn.executemany(RESULTS_SQL, result_rows)
        db.conn.execute(
            LANE_SQL,
            (
                "populace-reform-validation",
                "ingested",
                f"{n_claims} claims, {n_results} per-release results "
                f"({len(releases)} releases,"
                f" {tallies['obbba_attached_results']} attached to harvest"
                f" claims); {len(skipped)} unscoreable rows skipped",
                "2026-08-04",
            ),
        )
    cov = db.coverage()
    db.close()
    return {
        "releases": len(releases),
        "claims_upserted": n_claims,
        "results": n_results,
        "skipped": len(skipped),
        **tallies,
        **cov,
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
