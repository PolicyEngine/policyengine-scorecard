"""Ingest the £100,000 childcare limit costings and their PolicyEngine
counterparts (lane uk-childcare-100k).

Two external scores of removing the £100,000 adjusted-net-income limit on
the working-parent childcare offers in England:

    sources/centax-childcare-100k   CenTax, "Removing the childcare
        cliff-edge" (September 2026), Table 4.2: the free hours only, on
        HMRC administrative data; static cost, two behavioural margins and
        the net cost, for three scenarios in 2027-28 and 2029-30
    sources/cbp-rates-and-wrongs    Centre for British Progress, "Rates and
        wrongs" technical appendix (25 March 2026), Tables 2-3: the free
        hours and Tax-Free Childcare on a synthetic population; net of
        behaviour only, two behavioural models, 2026-27 to 2031-32

Inputs: the adapters' tidy rows (data/externals/<id>.json, QC'd there),
each source's annotations.json, the certified-pair artifact
results/uk/childcare_100k/<variant>.json (pipeline/compute_uk_childcare_100k.py)
with its construction_annotations.json, and the published dashboard figure
in sources/centax-childcare-100k/pe/published_dashboard.json.

Claims: 24 CenTax money cells and 12 CBP "Abolish Cliff" cells, all
revenue_change in pounds, the value as published. Tallied drops (still in
data/externals): CenTax's 12 bunching counts (a behavioural-model count of
parents with no registered metric; minting one waits for a counterpart)
and CBP's 60 taper cells (a per-child taper replacing the cliff, which no
PolicyEngine construction in this lane executes).

Results:
  - certified pair (the default replay variant, data/uk/certified_bundle.json):
    CenTax static rows (6) are `comparable`, CenTax net rows (6) and CBP
    rows (10) `concept_mismatch`; the status comes from the source's
    annotations.json, and exactly one status-setting annotation must match
  - published dashboard history (4): PolicyEngine's published 30-hours cost
    (£0.434bn in 2027-28, £0.505bn in 2029-30) on the CenTax central
    static and net rows, the comparison the dashboard itself drew:
    `constructed` (static; the dashboard's local corrections) and
    `concept_mismatch` (net). It is older than the certified run, so the
    comparisons view and the app's latest point at the certified run and
    the published miss stays in the history beside it.
CenTax's behavioural margins (12) and CBP's 2031-32 cells (2) carry no
result; they are published without one and say why in ``pe_missing``.

Diagnosis: the CenTax central static rows carry a pe_gap diagnosis linked
to microcosm#1126 (the hours-usage draw), with the evidence measured on the
certified pair.

calibration_relationship comes from relationships.uk_relationship: held out
for both sources. Each is a reform estimate, and no calibration target is a
reform-world quantity (tests/test_uk_childcare_100k.py checks the built DB).

    PYTHONPATH=. python -m scorecard_db.ingest_uk_childcare_100k data/scorecard.db
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .db import DIAGNOSES_SQL, LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields
from .models import (
    BASELINE,
    STANDARD_CONDITIONS,
    ComparisonStatus,
    DiagnosisClass,
    ExternalScore,
    Metric,
    PEResult,
    TimeBasis,
    UnitConcept,
)
from .relationships import uk_relationship

EXTERNALS = REPO / "data" / "externals"
CENTAX_DIR = REPO / "sources" / "centax-childcare-100k"
CBP_DIR = REPO / "sources" / "cbp-rates-and-wrongs"
RESULTS_DIR = REPO / "results" / "uk" / "childcare_100k"
VARIANTS = REPO / "data" / "uk" / "replay_variants.json"
CERTIFIED = REPO / "data" / "uk" / "certified_bundle.json"

CENTAX = "centax"
CBP = "centre_for_british_progress"
SOURCES = (CENTAX, CBP)
SOURCE_MODELS = {
    # the spelling the Autumn Budget 2025 harvest already uses for CenTax
    CENTAX: "hmrc_administrative_microdata",
    CBP: "cbp_synthetic_microsimulation",
}
MEASURES = {
    CENTAX: "uk_free_childcare_hours_100k_limit_removed",
    CBP: "uk_free_childcare_hours_and_tfc_100k_limit_removed",
}
PROGRAMS = {
    CENTAX: "free_childcare_hours",
    CBP: "free_childcare_hours_and_tax_free_childcare",
}
# which certified-pair world answers which source
WORLDS = {CENTAX: "free_hours", CBP: "free_hours_and_tfc"}
FREE_HOURS = (
    "extended_childcare_entitlement",
    "universal_childcare_entitlement",
    "targeted_childcare_entitlement",
)
TFC = "tax_free_childcare"
VARIABLES = {CENTAX: list(FREE_HOURS), CBP: [*FREE_HOURS, TFC]}

LANE_ID = "uk-childcare-100k"
LANE_UPDATED = "2026-10-21"
# The UK family's shared top-level feed literal (sync_lane_feed's contract).
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "CenTax + Centre for British Progress",
    "area": "£100,000 childcare limit (30 funded hours, Tax-Free Childcare)",
    "mode": 2,
    "country": "UK",
}
REGISTRY_MARK = "uk_childcare_100k"

CENTAX_PUBLICATION = {
    "title": "Removing the childcare cliff-edge: impacts and cost of reform",
    "authors": "Advani, Flew, Pepin-Hall and Summers",
    "publisher": "CenTax",
    "url": "https://centax.org.uk/wp-content/uploads/2026/09/AdvaniFlewPepin-HallSummers2026_Removing-the-childcare-cliff-edge.pdf",
    "date": "2026-09",
    "table": "4.2",
    "printed_page": "41",
    "vintage": "as published September 2026 (fetched 2026-10-21)",
}
CBP_PUBLICATION = {
    "title": "Technical Appendix: underlying modelling and analysis for each of the policies in the Rates and Wrongs paper",
    "publisher": "Centre for British Progress",
    "url": "https://britishprogress.org/api/media/file/rates_and_wrongs_technical_appendix.pdf",
    "date": "2026-03-25",
    "vintage": "as published 25 March 2026 (fetched 2026-10-21)",
}

CENTAX_MONEY = (
    "static_cost",
    "intensive_margin",
    "extensive_margin",
    "net_fiscal_cost",
)
CENTAX_ATTACHED = ("static_cost", "net_fiscal_cost")
CENTAX_SIGN = (
    "positive = gain to the Exchequer (published: 'negative = cost to the Exchequer')"
)
SCORING = {
    "static_cost": "static",
    "net_fiscal_cost": "post_behavioural",
}
PE_MISSING_MARGIN = (
    "behavioural leg: this lane's PolicyEngine counterpart is static "
    "(policyengine_uk Simulation.apply_dynamics is not run)"
)

_CENTAX_FIELDS = frozenset(
    {
        "column",
        "country",
        "fy",
        "period",
        "printed_page",
        "scenario",
        "source",
        "source_column",
        "status",
        "table",
        "tax_year_label",
        "unit_concept",
        "value",
        "value_verbatim",
    }
)
_CBP_FIELDS = frozenset(
    {
        "assumptions",
        "country",
        "fy",
        "model",
        "pdf_page",
        "period",
        "policy",
        "source",
        "source_column",
        "status",
        "table",
        "unit_concept",
        "value",
        "value_verbatim",
    }
)
_DROPS = {
    "centax_bunching_counts": (
        "CenTax's Table 4.2 bunching counts (parents holding income at "
        "£100,000, before and after removal) are outputs of its behavioural "
        "model with no registered metric here; minting one waits for a "
        "counterpart or a second source. The rows stay in data/externals."
    ),
    "cbp_taper_rows": (
        "CBP's 1%-5% rows replace the cliff with a per-child opt-in taper "
        "(section 1.3.6), a reform no PolicyEngine construction in this lane "
        "executes. The rows stay in data/externals."
    ),
}


def _load(adapter_id: str, known: frozenset, source: str) -> list[dict]:
    path = EXTERNALS / f"{adapter_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run python sources/{adapter_id}/adapter.py"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, known, source)
        if row["source"] != adapter_id or row["country"] != "UK":
            raise ValueError(f"{source}: unexpected row identity {row}")
    return rows


def _check_conditions(cond: dict) -> dict:
    unknown = set(cond) - STANDARD_CONDITIONS
    if unknown:
        raise ValueError(f"conditions outside STANDARD_CONDITIONS: {sorted(unknown)}")
    return cond


def _centax_claim(row: dict) -> ExternalScore:
    component = row["column"]
    cond = {
        "country": "UK",
        "geography": "England",
        "fy": row["fy"],
        "program": PROGRAMS[CENTAX],
        "measure_key": MEASURES[CENTAX],
        "component": component,
        "scenario": row["scenario"],
        "benchmark_class": "different_model",
        "data_scope": "hmrc_administrative",
        "sign_convention": CENTAX_SIGN,
        "value_verbatim": row["value_verbatim"],
    }
    if component in SCORING:
        cond["scoring_method"] = SCORING[component]
    else:
        cond["pe_missing"] = PE_MISSING_MARGIN
    relationship, _ = uk_relationship(CENTAX, Metric.REVENUE_CHANGE)
    return ExternalScore(
        source=CENTAX,
        source_model=SOURCE_MODELS[CENTAX],
        metric=Metric.REVENUE_CHANGE,
        unit_concept=UnitConcept.GBP,
        period=int(row["period"]),
        time_basis=TimeBasis.FISCAL_YEAR,
        value=float(row["value"]),
        conditions=_check_conditions(cond),
        reform=policy_ref(MEASURES[CENTAX]),
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication={
            **CENTAX_PUBLICATION,
            "registry": REGISTRY_MARK,
            "publish_without_result": True,
        },
        value_kind="gbp",
        status=row["status"],
    )


def _cbp_claim(row: dict, data_years: list[int]) -> ExternalScore:
    cond = {
        "country": "UK",
        "geography": "England",
        "fy": row["fy"],
        "program": PROGRAMS[CBP],
        "measure_key": MEASURES[CBP],
        "scoring_method": "post_behavioural",
        "behavioral_response": row["model"],
        "benchmark_class": "different_model",
        "data_scope": "synthetic_ons_births_spi_2022_23",
        # no sign_convention: the appendix states none, so the exporter's
        # signs.classify reads "no_stated_convention" (unknown); CenTax's
        # reading of the sign is in the cbp-sign-unstated annotation
        "value_verbatim": row["value_verbatim"],
    }
    if int(row["period"]) - 1 not in data_years:
        cond["pe_missing"] = (
            f"fiscal year {row['fy']} is outside the certified pair's data "
            f"years ({data_years[0]}-{data_years[-1]}; data/uk/replay_variants.json)"
        )
    relationship, _ = uk_relationship(CBP, Metric.REVENUE_CHANGE)
    return ExternalScore(
        source=CBP,
        source_model=SOURCE_MODELS[CBP],
        metric=Metric.REVENUE_CHANGE,
        unit_concept=UnitConcept.GBP,
        period=int(row["period"]),
        time_basis=TimeBasis.FISCAL_YEAR,
        value=float(row["value"]),
        conditions=_check_conditions(cond),
        reform=policy_ref(MEASURES[CBP]),
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication={
            **CBP_PUBLICATION,
            "table": row["table"],
            "pdf_page": str(row["pdf_page"]),
            "assumptions": row["assumptions"],
            "registry": REGISTRY_MARK,
            "publish_without_result": True,
        },
        value_kind="gbp",
        status=row["status"],
    )


def load_artifact() -> tuple[dict, Path]:
    """The certified-pair artifact for the default variant, checked against
    the certified bundle it claims to have run on."""
    variants = json.loads(VARIANTS.read_text())
    variant_id = variants["default_variant"]
    path = RESULTS_DIR / f"{variant_id}.json"
    art = json.loads(path.read_text())
    cert = json.loads(CERTIFIED.read_text())
    if art["variant_id"] != variant_id:
        raise ValueError(f"artifact variant {art['variant_id']} != {variant_id}")
    if (art["data_bundle"], art["dataset"]["sha256"]) != (
        cert["revision"],
        cert["sha256"],
    ):
        raise ValueError("artifact data bundle is not the certified bundle")
    for world in (*art["worlds"].values(), *art["diagnostics"].values()):
        if (
            not world["dataset_sha256_before"]
            == world["dataset_sha256_after"]
            == cert["sha256"]
        ):
            raise ValueError(
                "artifact dataset digest does not match the certified bundle"
            )
    if art["behavioural_response"] != "none (static)":
        raise ValueError("artifact is not a static run")
    return art, path


def stage() -> tuple[list[ExternalScore], dict, dict, Path]:
    """(claims, drop tally, artifact, artifact path)."""
    art, art_path = load_artifact()
    data_years = art["worlds"]["baseline"]["dataset_years"]
    scores: list[ExternalScore] = []
    drops: Counter = Counter()
    for row in _load("centax-childcare-100k", _CENTAX_FIELDS, CENTAX):
        if row["column"] in CENTAX_MONEY:
            scores.append(_centax_claim(row))
        else:
            drops["centax_bunching_counts"] += 1
    for row in _load("cbp-rates-and-wrongs", _CBP_FIELDS, CBP):
        if row["policy"] == "abolish_cliff":
            scores.append(_cbp_claim(row, data_years))
        else:
            drops["cbp_taper_rows"] += 1
    return finish(scores, LANE_ID), dict(sorted(drops.items())), art, art_path


# --- annotations -------------------------------------------------------------


def _spec(path: Path) -> list[dict]:
    spec = json.loads(path.read_text())
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
    return spec["annotations"]


_MATCHERS = {
    CENTAX: {"components", "scenarios", "periods", "results"},
    CBP: {"models", "periods", "results"},
}


def _facets(score: ExternalScore) -> dict:
    c = score.conditions
    if score.source == CENTAX:
        return {
            "components": c["component"],
            "scenarios": c["scenario"],
            "periods": score.period,
        }
    return {"models": c["behavioral_response"], "periods": score.period}


def match_annotations(
    score: ExternalScore, result_kind: str, spec: list[dict]
) -> tuple[list[str], ComparisonStatus]:
    """(texts, status) for one result; exactly one status-setting
    annotation must match, so a status is always a stated decision."""
    facets = {**_facets(score), "results": result_kind}
    texts, statuses = [], []
    for a in spec:
        match = a["applies_to"]
        if set(match) != _MATCHERS[score.source]:
            raise ValueError(f"annotation {a['id']}: matcher keys {sorted(match)}")
        if any(v is not None and facets[k] not in v for k, v in match.items()):
            continue
        texts.append(a["text"])
        if "status" in a:
            statuses.append((a["id"], a["status"]))
    if len(statuses) != 1:
        raise ValueError(
            f"{score.source} {score.conditions.get('component', '')} {score.period} "
            f"{result_kind}: status-setting annotations {statuses} (want exactly one)"
        )
    return texts, ComparisonStatus(statuses[0][1])


# --- results -----------------------------------------------------------------


def _bn(x: float) -> str:
    return f"£{x / 1e9:+.3f}bn"


def _delta(art: dict, world: str, year: int, variable: str) -> float:
    ref = art["worlds"][world]["years"][str(year)]["sums_gbp"][variable]
    base = art["worlds"]["baseline"]["years"][str(year)]["sums_gbp"][variable]
    return ref - base


def counterpart(art: dict, source: str, year: int) -> float:
    """PolicyEngine's static revenue_change, oriented to the Exchequer
    (negative = cost): minus the change in the counted spending."""
    return -sum(_delta(art, WORLDS[source], year, v) for v in VARIABLES[source])


def measured_notes(art: dict, source: str, year: int, fy: str) -> list[str]:
    world = WORLDS[source]
    w = art["worlds"][world]["years"][str(year)]
    b = art["worlds"]["baseline"]["years"][str(year)]
    d = {
        v: _delta(art, world, year, v)
        for v in (*FREE_HOURS, TFC, "gov_spending", "gov_tax")
    }
    # Nothing outside the four childcare heads may move (£1m tolerance on
    # sums of order £1e11), and the free-hours-only world leaves
    # Tax-Free Childcare where it was; the annotations say both.
    heads = sum(d[v] for v in (*FREE_HOURS, TFC))
    if abs(d["gov_spending"] - heads) > 1e6 or abs(d["gov_tax"]) > 1e6:
        raise ValueError(
            f"{source} {year}: the reform moved spending or tax outside the childcare heads"
        )
    if source == CENTAX and abs(d[TFC]) > 1e6:
        raise ValueError(
            f"{year}: removing the 30-hours limit moved Tax-Free Childcare"
        )
    notes = [
        (
            f"Measured on the certified pair, {fy} (engine period {year}, the start "
            f"year, for claim period {year + 1}): extended hours "
            f"{_bn(d['extended_childcare_entitlement'])}, universal "
            f"{_bn(d['universal_childcare_entitlement'])}, targeted "
            f"{_bn(d['targeted_childcare_entitlement'])}, Tax-Free Childcare "
            f"{_bn(d[TFC])} (reform minus current law); gov_spending moves "
            f"{_bn(d['gov_spending'])} and gov_tax {_bn(d['gov_tax'])}."
        ),
        (
            "Families receiving the extended hours: "
            f"{b['counts']['benunits_receiving_extended'] / 1e6:.2f}m under current "
            f"law, {w['counts']['benunits_receiving_extended'] / 1e6:.2f}m with the "
            "limit removed."
        ),
        (
            "Hours-usage draw: the families receiving the extended hours use a "
            f"weighted mean of {b['hours_usage']['mean_benunits_receiving_extended']:.1f}"
            " of 30 weekly hours under current law "
            "(maximum_extended_childcare_hours_usage). microcosm#1126 traces this "
            "draw and puts DfE's mean at about 28.5 hours."
        ),
        "Executed limits on 30 April {y}: 30 hours {a:g}, Tax-Free Childcare {t:g} (1e+100 is the "
        "repo's no-limit sentinel, compute_uk_ab2025.NO_LIMIT).".format(
            y=year,
            a=w["limits_executed"][
                "gov.dfe.extended_childcare_entitlement.income.limit"
            ],
            t=w["limits_executed"]["gov.hmrc.tax_free_childcare.income.income_limit"],
        ),
    ]
    diag = art["diagnostics"]
    if (
        str(year) in diag.get("baseline__full_use_hours", {}).get("years", {})
        and source == CENTAX
    ):
        full = sum(
            diag["free_hours__full_use_hours"]["years"][str(year)]["sums_gbp"][v]
            - diag["baseline__full_use_hours"]["years"][str(year)]["sums_gbp"][v]
            for v in FREE_HOURS
        )
        notes.append(
            f"Diagnostic, not attached: with every family at the full 30 hours (the input set to 30 in "
            f"both worlds before any calculation) the same reform costs £{full / 1e9:.3f}bn in {fy} "
            "on this pair."
        )
    return notes


def _construction(art: dict, path: Path, source: str, year: int) -> str:
    world = WORLDS[source]
    limits = sorted(art["worlds"][world]["reform_dict"])
    return (
        f"static: the certified world with {', '.join(limits)} set to "
        f"{art['limit_sentinel']:g} minus the certified world as served, engine period {year} "
        f"(FY {year}-{(year + 1) % 100:02d}); minus the change in "
        f"{' + '.join(VARIABLES[source])} (microdf weights); artifact {path.relative_to(REPO)}"
    )


def published_result(
    score: ExternalScore, spec: list[dict], pub: dict
) -> PEResult | None:
    """The published figure, on the central rows: the comparison the
    dashboard itself drew (its benchmark text names CenTax's central
    static and net costs)."""
    if score.conditions["scenario"] != "central":
        return None
    year = score.period - 1
    value = pub["values_gbp_bn"]["thirty_hours"].get(str(year))
    if value is None:
        return None
    texts, status = match_annotations(score, "published_dashboard", spec)
    return PEResult(
        claim_id=score.claim_id(),
        computed_value=-value * 1e9,
        status=status,
        engine_version=pub["engine"]["policyengine_uk"],
        data_bundle=pub["dataset"]["release"],
        pe_construction=(
            f"published: the 30-hours leg of PolicyEngine's dashboard ({pub['page']}), "
            f"{pub['values_gbp_bn']['field']}, year {year} (FY {year}-{(year + 1) % 100:02d}); "
            f"{pub['repo']}@{pub['commit'][:7]} {pub['results_file']} (sha256 "
            f"{pub['results_file_sha256'][:12]}); policyengine {pub['engine']['policyengine']}, "
            f"dataset passed unmanaged ({pub['dataset']['management']})"
        ),
        run_id=pub["run_id"],
        computed_at=pub["generated_at"],
        annotations=[
            *texts,
            f"Published figure: £{value:.3f}bn. {pub['corrections']}",
            (
                f"{pub['hours_draw']}. The fix is in {pub['pending_fix']['pr']} on "
                f"{pub['pending_fix']['release']}: "
                f"£{pub['pending_fix']['thirty_hours_gbp_bn'][str(year)]:.3f}bn in "
                f"this year; not attached: {pub['pending_fix']['why_not_attached']}"
            ),
        ],
        baseline_key=BASELINE.baseline_key(),
        policyengine_variables=list(FREE_HOURS),
    )


def results(scores: list[ExternalScore], art: dict, art_path: Path) -> list[PEResult]:
    specs = {
        CENTAX: _spec(CENTAX_DIR / "annotations.json"),
        CBP: _spec(CBP_DIR / "annotations.json"),
    }
    construction = [
        a["text"] for a in _spec(RESULTS_DIR / "construction_annotations.json")
    ]
    pub = json.loads((CENTAX_DIR / "pe" / "published_dashboard.json").read_text())
    out = []
    for s in scores:
        if s.source == CENTAX and s.conditions["component"] not in CENTAX_ATTACHED:
            continue
        year = s.period - 1
        if str(year) not in art["worlds"][WORLDS[s.source]]["years"]:
            continue
        texts, status = match_annotations(s, "certified", specs[s.source])
        out.append(
            PEResult(
                claim_id=s.claim_id(),
                computed_value=counterpart(art, s.source, year),
                status=status,
                engine_version=art["engine_version"],
                data_bundle=art["data_bundle"],
                pe_construction=_construction(art, art_path, s.source, year),
                run_id=art["run_id"],
                computed_at=art["computed_at"],
                annotations=[
                    *texts,
                    *construction,
                    *measured_notes(art, s.source, year, s.conditions["fy"]),
                ],
                baseline_key=BASELINE.baseline_key(),
                policyengine_variables=VARIABLES[s.source],
            )
        )
        if s.source == CENTAX:
            hist = published_result(s, specs[CENTAX], pub)
            if hist is not None:
                if hist.computed_at >= art["computed_at"]:
                    raise ValueError(
                        "the published figure must be older than the certified run"
                    )
                out.append(hist)
    return out


def diagnoses(scores: list[ExternalScore], art: dict) -> list[tuple]:
    """pe_gap on the CenTax central static rows, linked to microcosm#1126."""
    rows = []
    for s in scores:
        c = s.conditions
        if (s.source, c.get("component"), c.get("scenario")) != (
            CENTAX,
            "static_cost",
            "central",
        ):
            continue
        year = s.period - 1
        pe = counterpart(art, CENTAX, year)
        hours = art["worlds"]["baseline"]["years"][str(year)]["hours_usage"][
            "mean_benunits_receiving_extended"
        ]
        diag = art["diagnostics"]
        full = sum(
            diag["free_hours__full_use_hours"]["years"][str(year)]["sums_gbp"][v]
            - diag["baseline__full_use_hours"]["years"][str(year)]["sums_gbp"][v]
            for v in FREE_HOURS
        )
        rationale = (
            f"PolicyEngine's static cost on the certified pair is £{-pe / 1e9:.3f}bn in {c['fy']}, "
            f"{abs(pe / s.value - 1) * 100:.0f}% {'below' if pe > s.value else 'above'} CenTax's "
            f"£{-s.value / 1e9:.2f}bn. Our side first: "
            f"the pair's hours-usage draw gives families receiving the extended hours a weighted mean of "
            f"{hours:.1f} of 30 weekly hours (measured); microcosm#1126 identifies this draw as the main "
            "reason PolicyEngine's free-hours spending is low and derives DfE's mean as about 28.5 hours. "
            f"With every family at the full 30 hours the same reform costs £{full / 1e9:.3f}bn on this pair "
            "(diagnostic run). The fix merged in microcosm on 16 October 2026 (microcosm#1299); this "
            "certified pair was built on 19 June 2026, before it. PolicyEngine's published dashboard "
            "figure ran on the 2 October Microcosm release that microcosm#1126 examines, with the same "
            "draw. Two smaller PolicyEngine-side factors are recorded on the result: the universal-hours "
            "switch-off (policyengine-uk#1930, changed after the pin by policyengine-uk#2177) and no "
            "hours for children under 1."
        )
        rows.append(
            ScorecardDB.diagnosis_row(
                s.claim_id(),
                DiagnosisClass.PE_GAP.value,
                rationale,
                "https://github.com/PolicyEngine/microcosm/issues/1126",
            )
        )
    return rows


_EXPECTED = {
    "claims": 36,
    "claims_by_source": {CENTAX: 24, CBP: 12},
    "results": 26,
    "results_by_kind": {"certified": 22, "published_dashboard": 4},
    "statuses": {"comparable": 6, "concept_mismatch": 18, "constructed": 2},
    "diagnoses": 2,
    "drops": {"cbp_taper_rows": 60, "centax_bunching_counts": 12},
}


def accounting(scores, pe, diag, drops, art) -> dict:
    return {
        "claims": len(scores),
        "claims_by_source": dict(Counter(s.source for s in scores)),
        "results": len(pe),
        "results_by_kind": dict(
            Counter(
                "certified" if r.run_id == art["run_id"] else "published_dashboard"
                for r in pe
            )
        ),
        "statuses": dict(Counter(r.status.value for r in pe)),
        "diagnoses": len(diag),
        "drops": drops,
    }


def ingest(db_path: Path) -> dict:
    scores, drops, art, art_path = stage()
    pe = results(scores, art, art_path)
    diag = diagnoses(scores, art)
    counts = accounting(scores, pe, diag, drops, art)
    if counts != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {counts} != {_EXPECTED}")
    db = ScorecardDB(db_path)

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        old = [
            r[0]
            for r in db.conn.execute(
                "SELECT claim_id FROM external_scores "
                "WHERE json_extract(publication, '$.registry') = ?",
                (REGISTRY_MARK,),
            )
        ]
        for table in ("diagnoses", "pe_results", "external_scores"):
            db.conn.executemany(
                f"DELETE FROM {table} WHERE claim_id = ?", [(c,) for c in old]
            )
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(RESULTS_SQL, [ScorecardDB.result_row(r) for r in pe])
        db.conn.executemany(DIAGNOSES_SQL, diag)
        register_baselines_txn(db)
        detail = (
            f"{counts['results_by_kind']['certified']} of {len(scores)} claims computed on the "
            f"certified pair ({art['data_bundle']}, policyengine-uk {art['engine_version']}) — "
            "CenTax Table 4.2 (24 cells: static cost comparable, net cost concept_mismatch) and CBP's "
            "technical appendix (12 abolition cells, concept_mismatch); PolicyEngine's published "
            "dashboard figure kept as history; pe_gap on the central static rows (microcosm#1126)"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return counts


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
