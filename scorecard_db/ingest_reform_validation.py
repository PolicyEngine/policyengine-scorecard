"""Ingest the populace reform-validation registry (per-release artifacts).

Third population: the external-checks registry that previously rendered as
calibration-diagnostics' "External checks" tab, now consolidated into the
scorecard. Each ``sources/populace-reform-validation/raw/<release_id>.json``
is one certified populace-us release's ``reform_validation.json``, produced
at the release's exact engine pins — so ingesting all of them yields a
per-release **regression history** in ``pe_results`` (same claim, one result
per release), which the interchange and platform grids don't have.

Mapping (categories -> scorecard vocabulary):

  OBBBA / Federal reform / State reform   REVENUE_CHANGE, policy_ref reform
  State program (repeal construction)     BENEFIT_COST, BASELINE — resolves
                                          to the SAME claim as the matching
                                          "State program actual" row; the
                                          repeal-delta is just a second
                                          pe_construction of that claim
  State program actual / Fed EITC by st.  BENEFIT_COST, BASELINE
  IRS SOI actual                          TAX_LIABILITY / TAX_CREDITS_APPLIED
  Tax expenditure / JCT tax expenditure   TAX_EXPENDITURE (the reserved
                                          metric's first rows)
  Census state SPM                        POVERTY_RATE (SHARE fractions)
  Mechanical check                        BENEFIT_COST, policy_ref reform

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
payload extension (see the integration issue).

Rows whose benchmark is null (score_type "none": unscoreable expenditures)
are skipped and tallied. Re-ingest is idempotent: claims upsert by claim_id
and this module's own pe_results (run_id prefix ``populace-rv-``) are
replaced wholesale.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
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

# Exact engine pins per release (from each release_manifest.json on HF;
# the artifact's PE values were computed at these versions).
ENGINE_VERSIONS = {
    "populace-us-2024-f0af251-703bd81a565c-20260620T201958Z": "1.729.0",
    "populace-us-2024-sparse-l0-refit-57k-71a0887-national-only-20260701": "1.752.2",
    "populace-us-2024-buildi-sparse-rmloss100-6e8e929-20260709T034135Z": "1.764.6",
    "populace-us-2024-buildj-sparse-rmloss100-75d5add-20260710T094201Z": "1.764.6",
    "populace-us-2024-buildo-sparse-rmloss100-22bd902-20260722T232627Z": "1.764.6",
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


def _map_row(row: dict) -> tuple[ExternalScore, str] | None:
    """(claim, pe_construction) for one artifact row; None -> skip."""
    value = row["jct"].get("score")
    if value is None:
        return None
    cat = row["category"]
    measure = row["populace"].get("measure") or ""
    window = row["jct"].get("window") or str(row["period"])
    time_basis = (
        TimeBasis.FISCAL_YEAR if window.upper().startswith("FY")
        else TimeBasis.ANNUAL
    )
    conditions: dict[str, str] = {}
    state = _state_of(row)
    construction = f"level:{measure}"

    if cat in ("OBBBA", "Federal reform", "State reform", "Mechanical check"):
        metric, uc, kind = Metric.REVENUE_CHANGE, UnitConcept.USD, "usd"
        if cat == "Mechanical check":
            metric = Metric.BENEFIT_COST
        reform = ReformRef(
            framework="policy_ref",
            reform={"policy": row["id"], "registry": "populace_reform_validation"},
        )
        conditions["geography"] = state or "US"
        construction = f"reform_delta:{measure}"
    elif cat in ("State program", "State program actual"):
        # Both categories describe the same external claim (the admin
        # actual); "State program" rows are the repeal-delta construction.
        program = row["id"].removeprefix("state_repeal_").removeprefix("state_")
        metric, uc, kind = Metric.BENEFIT_COST, UnitConcept.USD, "usd"
        reform = BASELINE
        conditions["geography"] = state or "US"
        conditions["program"] = program
        if cat == "State program":
            construction = f"repeal_delta:{measure}"
        else:
            construction = f"level:{measure}"
    elif cat == "Federal EITC by state":
        metric, uc, kind = Metric.BENEFIT_COST, UnitConcept.USD, "usd"
        reform = BASELINE
        conditions["geography"] = row["id"].rsplit("_", 1)[-1].upper()
        conditions["program"] = "eitc"
    elif cat == "IRS SOI actual":
        uc, kind = UnitConcept.USD, "usd"
        reform = BASELINE
        conditions["geography"] = "US"
        if measure in _SOI_TAXES:
            metric = Metric.TAX_LIABILITY
            conditions["tax"] = measure
        else:
            metric = Metric.TAX_CREDITS_APPLIED
            conditions["program"] = measure
    elif cat in ("Tax expenditure", "JCT tax expenditure"):
        metric, uc, kind = Metric.TAX_EXPENDITURE, UnitConcept.USD, "usd"
        reform = BASELINE
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
        reform = BASELINE
        geo = row["id"].rsplit("_", 1)[-1]
        conditions["geography"] = geo.upper() if geo != "us" else "US"
        if "child" in row["id"]:
            conditions["subgroup"] = "children_under_18"
    else:
        raise ValueError(f"unmapped category {cat!r} ({row['id']})")

    relationship = "held_out"
    if cat in ("JCT tax expenditure", "IRS SOI actual"):
        relationship = "consumed_as_target"

    return (
        ExternalScore(
            source=_publisher(row),
            metric=metric,
            unit_concept=uc,
            period=int(row["period"]),
            time_basis=time_basis,
            value=float(value),
            conditions=conditions,
            reform=reform,
            calibration_relationship=relationship,
            source_column=row["id"],
            publication={
                "title": row["jct"].get("source") or "",
                "url": row["jct"].get("source_url") or "",
                "score_type": row["jct"].get("score_type") or "",
                "window": window,
                "name": row.get("name") or "",
            },
            value_kind=kind,
        ),
        construction,
    )


def _pe_value(row: dict) -> float | None:
    pop = row["populace"]
    if pop.get("reform_total") is None and row["category"] not in (
        "OBBBA", "Federal reform", "State reform", "State program",
        "Mechanical check",
    ):
        return pop.get("baseline_total")
    return pop.get("budget_effect")


def _release_timestamp(release_id: str) -> str:
    tail = release_id.rsplit("-", 1)[-1]
    if "T" in tail and len(tail) >= 15:
        return f"{tail[0:4]}-{tail[4:6]}-{tail[6:8]}T{tail[9:11]}:{tail[11:13]}:{tail[13:15]}"
    if len(tail) == 8 and tail.isdigit():  # date-only ids (l0-refit)
        return f"{tail[0:4]}-{tail[4:6]}-{tail[6:8]}T00:00:00"
    raise ValueError(f"cannot parse release timestamp from {release_id!r}")


def ingest(db_path: Path, raw_dir: Path | None = None) -> dict:
    raw_dir = raw_dir or RAW
    db = ScorecardDB(db_path)
    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_results WHERE run_id LIKE ?", (f"{RUN_PREFIX}%",)
        )

    claims: dict[str, ExternalScore] = {}
    results: list[PEResult] = []
    skipped: list[str] = []
    releases = sorted(
        raw_dir.glob("*.json"), key=lambda p: _release_timestamp(p.stem)
    )
    if not releases:
        raise SystemExit(f"no artifacts in {raw_dir}")
    for path in releases:
        artifact = json.loads(path.read_text())
        release_id = artifact["release_id"]
        engine = ENGINE_VERSIONS.get(release_id)
        if engine is None:
            raise SystemExit(
                f"{release_id} missing from ENGINE_VERSIONS — add its "
                "release_manifest.json pin"
            )
        computed_at = _release_timestamp(release_id)
        # Repeal-construction rows first, so the direct level result is the
        # later insert and wins the comparisons view's latest-result tiebreak.
        rows = sorted(
            artifact["reforms"],
            key=lambda r: 0 if r["category"] == "State program" else 1,
        )
        for row in rows:
            mapped = _map_row(row)
            if mapped is None:
                skipped.append(f"{release_id[:20]}…:{row['id']}")
                continue
            claim, construction = mapped
            cid = claim.claim_id()
            claims.setdefault(cid, claim)
            pe_value = _pe_value(row)
            if pe_value is None:
                continue
            status = (
                ComparisonStatus.CONSTRUCTED
                if row["jct"].get("score_type") in ("approximation", "tax_expenditure")
                or construction.startswith("repeal_delta")
                else ComparisonStatus.COMPARABLE
            )
            results.append(
                PEResult(
                    claim_id=cid,
                    computed_value=float(pe_value),
                    status=status,
                    engine_version=engine,
                    data_bundle=release_id,
                    pe_construction=construction,
                    run_id=f"{RUN_PREFIX}{release_id}",
                    computed_at=computed_at,
                )
            )

    n_claims = db.upsert_scores(claims.values())
    n_results = db.add_results(results)
    db.set_lane(
        "populace-reform-validation",
        "ingested",
        f"{n_claims} claims, {n_results} per-release results "
        f"({len(releases)} releases); {len(skipped)} unscoreable rows skipped",
        "2026-08-03",
    )
    cov = db.coverage()
    db.close()
    return {
        "releases": len(releases),
        "claims_upserted": n_claims,
        "results": n_results,
        "skipped": len(skipped),
        **cov,
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
