"""PolicyEngine's counterparts for Autumn Budget 2026 claims (#230, tranche 3).

pipeline/stage_uk_ab2026.py pairs each AB2026 claim on a ``pe_modifier``
measure with one cell of the dashboard's Budget-day artifacts, or tallies a
written reason. These tests pin its invariants:

1. every vendored file's bytes hash to MANIFEST.json, each CSV to its
   receipt, and each receipt to the registry, at the pinned commit, and
   ``vendor`` writes the committed manifest and files;
2. the 6.11.1 pair record states what every receipt states about the run;
3. every counterpart traces to one file, column and row, and we rederive it
   from its CSV cell and the producer's sign convention, byte for byte;
4. the accounting closes per measure and in total, against the pin;
5. a sign flip in a claim flips the sign relation and the counterpart's
   sign, and leaves its magnitude alone;
6. two runs give the same output, and so does any order of the claims;
7. no claim gets two computed answers;
8. a database built with the AB2026 ingest and these results shows each
   comparison, and build_db.py calls none of it;
9. each row carries exactly the annotations its producer, measure and year
   call for. On an exchequer row, those run from the fiscal year, baseline,
   change, timing and sign sentences to its measure's scope sentences, the
   behavioural sentence on property rows from 2028-29, and one sentence naming
   every nonzero line of the OBR's breakdown for its measure and year except
   the receipts heads, the welfare line and the behavioural line, each with
   its amount, its direction and the test's own name for it;
10. each measure whose receipt names part of the UK takes a tally or a scope
    annotation;
11. the expected file pins each paired claim's value, file, column and row, and
    the year from the claim matches the year from the cell;
12. we reject claims with a different geography or unit, claims assigned to the
    OBR costings lane, exchequer claims without a readable sign, and a named OBR
    line under another sign convention or none;
13. we name in each reason the producers whose claims it covers, or write "the
    producer" when it covers several, and we state the dashboard's £1 minimum and
    income decile filter in the two count reasons.

Hypothesis drives 5, 6 and the OBR costings lane's rejection.
"""

import copy
import csv
import hashlib
import io
import json
import random
import re
import sqlite3
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import clone_copy
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pipeline import stage_uk_ab2026 as S
from pipeline import uk_certified_pairs as pairs
from scorecard_db import ScorecardDB, ingest_campaign, ingest_obr_costings, signs
from scorecard_db import ingest_uk_ab2026 as I

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = S.load_manifest()
REGISTRY = S.registry()
MEASURES = S.modifier_measures(REGISTRY)
CLAIMS = S.claims()
ROWS, TALLY, UNANSWERED = S.stage(CLAIMS)
BY_ID = {c["claim_id"]: c for c in CLAIMS}
SETTINGS = settings(
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- 1. the vendored artifacts --------------------------------------------------


def test_every_vendored_file_hashes_to_the_manifest():
    assert MANIFEST["artifacts"] == {
        p: f["sha256"] for p, f in MANIFEST["files"].items()
    }
    for path, sha in MANIFEST["artifacts"].items():
        assert _sha(ROOT / path) == sha, path
    on_disk = {
        str(p.relative_to(ROOT))
        for p in S.ARTIFACTS.rglob("*")
        if p.is_file() and p.parent != S.ARTIFACTS
    }
    assert on_disk == set(MANIFEST["artifacts"])


def test_every_receipt_hashes_to_the_registry_at_the_pinned_commit():
    assert set(MANIFEST["measures"]) == set(MEASURES)
    for key, m in MEASURES.items():
        rec = m["pe_modifier"]["receipt"]
        entry = MANIFEST["measures"][key]
        assert entry["receipt_file_sha256"] == rec["receipt_file_sha256"]
        assert _sha(ROOT / entry["receipt"]) == rec["receipt_file_sha256"]
        assert MANIFEST["files"][entry["receipt"]]["source_path"] == rec["path"]
        assert entry["receipt"] == S.local_path(rec["path"])
    commits = {f["source_commit"] for f in MANIFEST["files"].values()}
    assert commits == {MANIFEST["source"]["commit"]}
    assert commits == {m["pe_modifier"]["receipt"]["commit"] for m in MEASURES.values()}


def test_every_csv_hashes_to_its_receipt_and_is_used():
    used = {r["trace"]["file"] for r in ROWS}
    for key, entry in MANIFEST["measures"].items():
        rec = S.receipt(key)
        for path in entry["files"]:
            name = path.rsplit("/", 1)[1]
            if name == "receipt.json":
                continue
            assert MANIFEST["artifacts"][path] == rec["dashboard"]["files"][name]
            assert path in used, f"{path} is vendored but no counterpart reads it"


def test_a_changed_byte_is_refused(tmp_path, monkeypatch):
    path = next(p for p in MANIFEST["artifacts"] if p.endswith(".csv"))
    copy_root = tmp_path / "root"
    target = copy_root / path
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / path).read_bytes() + b"\n")
    monkeypatch.setattr(S, "ROOT", copy_root)
    with pytest.raises(ValueError, match="differ from MANIFEST"):
        S.read_file(path, MANIFEST)


def _vendor_from_committed_bytes(tmp_path, monkeypatch, change=None):
    """Point ``vendor`` at a scratch root, and answer each ``git show`` with the
    committed copy of that file, changed by ``change`` if it names the file."""

    def show(cmd, **_):
        assert cmd[:2] == ["git", "show"]
        commit, path = cmd[2].split(":", 1)
        assert commit == MANIFEST["source"]["commit"]
        data = (ROOT / S.local_path(path)).read_bytes()
        return SimpleNamespace(stdout=change(path, data) if change else data)

    monkeypatch.setattr(S, "ROOT", tmp_path)
    monkeypatch.setattr(S, "ARTIFACTS", tmp_path / "results" / "uk" / "ab2026")
    monkeypatch.setattr(
        S, "MANIFEST", tmp_path / "results" / "uk" / "ab2026" / "MANIFEST.json"
    )
    monkeypatch.setattr(S.subprocess, "run", show)
    return tmp_path / "checkout"


def test_vendor_writes_the_committed_manifest_and_files(tmp_path, monkeypatch):
    committed = (ROOT / "results" / "uk" / "ab2026" / "MANIFEST.json").read_bytes()
    checkout = _vendor_from_committed_bytes(tmp_path, monkeypatch)
    assert S.vendor(checkout) == MANIFEST
    assert S.MANIFEST.read_bytes() == committed
    for path in MANIFEST["artifacts"]:
        assert (tmp_path / path).read_bytes() == (ROOT / path).read_bytes(), path


@pytest.mark.parametrize(
    ("suffix", "message"),
    [
        ("receipt.json", "bytes differ from the registry"),
        ("budgetary_impact.csv", "differs from its receipt"),
        ("age_impact.csv", "differs from its receipt"),
    ],
)
def test_vendor_refuses_a_file_whose_bytes_changed(
    tmp_path, monkeypatch, suffix, message
):
    def change(path, data):
        return data + b"\n" if path.endswith(suffix) else data

    checkout = _vendor_from_committed_bytes(tmp_path, monkeypatch, change)
    with pytest.raises(ValueError, match=message):
        S.vendor(checkout)


# --- 2. the pair record --------------------------------------------------------


def test_the_pair_record_states_what_every_receipt_states():
    record = pairs.get_record(S.PAIR_ID)
    identity = record["identity"]
    bundle = identity["release_bundle"]
    pin = REGISTRY["engine_pin"]["budget_day_runs"]
    assert identity["packages"]["policyengine"]["version"] == pin["policyengine"]
    assert bundle["model_version"] == REGISTRY["engine_pin"]["policyengine_uk"]
    assert identity["dataset"]["revision"] == pin["dataset_revision"]
    assert identity["dataset"]["sha256"] == pin["dataset_sha256"]
    for key in MEASURES:
        r = S.receipt(key)
        ex = r["execution_receipt"]
        cert, data = ex["certificate"], ex["data"]
        assert ex["wrapper"]["version"] == bundle["policyengine_version"]
        assert cert["bundle_version"] == bundle["policyengine_version"]
        assert (
            ex["model"]["version"] == identity["packages"]["policyengine-uk"]["version"]
        )
        assert (
            ex["core"]["version"]
            == identity["packages"]["policyengine-core"]["version"]
        )
        assert (
            cert["certified_for_model_version"]
            == (record["certification"]["certified_for_model_version"])
        )
        assert cert["certified_for_core_version"] == ex["core"]["version"]
        assert cert["compatibility_basis"] == bundle["compatibility_basis"]
        assert cert["certified_by"] == bundle["certified_by"]
        assert cert["certified_dataset_sha256"] == identity["dataset"]["sha256"]
        assert data["dataset_sha256"] == bundle["certified_data_artifact_sha256"]
        assert data["build_id"] == record["certification"]["data_build_id"]
        assert data["dataset_uri"] == bundle["default_dataset_uri"]
        assert data["data_package"] == bundle["data_package"]
        assert data["dataset"] == bundle["default_dataset"]
        assert data["release_version"] == bundle["data_version"]
        assert data["build_model_version"] == bundle["data_build_model_version"]
        assert r["dashboard"]["dataset_years"] == record["data_years"]
        assert ex["supported_years"] == record["data_years"]
        assert ex["fiscal_year"]["year_label"] == "start_year"
        assert ex["baseline"]["kind"] == "current_law"


# --- 3. traces -----------------------------------------------------------------


# The sign conventions on the paired rows. Each shows a cost to the Exchequer as
# negative, as the dashboard's budgetary impact column does.
COST_IS_NEGATIVE = (
    "Note (verbatim): This table uses the convention that a negative sign implies "
    "a loss to the Exchequer",
    "positive = yield to the Exchequer",
)


def _rederive(row: dict) -> float:
    """We rederive the counterpart from its CSV cell and the producer's sign
    convention."""
    trace = row["trace"]
    text = (ROOT / trace["file"]).read_text()
    hits = [
        r
        for r in csv.DictReader(io.StringIO(text))
        if all(r[k] == v for k, v in trace["where"].items())
    ]
    assert len(hits) == 1, trace
    raw = hits[0][trace["column"]]
    assert raw == trace["cell"]
    claim = BY_ID[row["external_claim_match"]["claim_id"]]
    if trace["column"] == "value":
        assert trace["file"].endswith("/budgetary_impact.csv")
        assert claim["conditions"]["sign_convention"].startswith(COST_IS_NEGATIVE)
        return float(raw) * 1e9
    assert trace["column"] == "people_directly_affected"
    assert trace["where"]["age_band"] == "all"
    return float(raw)


def test_every_counterpart_traces_to_one_cell_and_rederives_exactly():
    assert ROWS
    for row in ROWS:
        claim = BY_ID[row["external_claim_match"]["claim_id"]]
        assert json.dumps(_rederive(row)) == json.dumps(row["pe_value"])
        folder = MANIFEST["measures"][claim["measure_key"]]["receipt"].rsplit("/", 1)[0]
        assert row["trace"]["file"].startswith(folder + "/")
        assert row["trace"]["where"]["year"] == claim["conditions"]["fy"][:4]
        assert row["engine_version"] == "2.151.0"
        assert row["data_bundle"] == MANIFEST["data_bundle"]
        assert row["baseline_key"] == S.CURRENT_LAW
        assert row["status"] == "constructed"


def test_the_committed_staging_is_this_run():
    assert S.STAGED.read_text() == S.dumps_jsonl(ROWS)
    assert S.UNANSWERED.read_text() == S.dumps_jsonl(UNANSWERED)
    assert json.loads(S.TALLY.read_text()) == TALLY


# --- 4. the accounting ---------------------------------------------------------


def test_the_accounting_closes_per_measure_and_in_total():
    S.check(TALLY)
    assert TALLY["claims"] == len(CLAIMS)
    for key, bm in TALLY["by_measure"].items():
        mine = [c for c in CLAIMS if c["measure_key"] == key]
        assert bm["claims"] == len(mine)
        assert bm["claims"] == bm["computed"] + sum(bm["reasons"].values())
    computed = {r["external_claim_match"]["claim_id"] for r in ROWS}
    tallied = {u["claim_id"] for u in UNANSWERED}
    assert not computed & tallied
    assert computed | tallied == set(BY_ID)
    assert Counter(u["reason"] for u in UNANSWERED) == Counter(TALLY["reasons"])


def test_every_reason_is_written_out():
    for reason in TALLY["reasons"]:
        text = S.REASONS[reason]
        assert len(text) > 60 and text[0].isupper() and text.endswith("."), reason
    assert set(S.REASONS) == set(TALLY["reasons"])


REASONS = {
    "devolved_share_not_modelled": (
        "HM Treasury and the OBR count the UK cost, including the funding the "
        "government gives Scotland, Wales and Northern Ireland, and we estimate "
        "the payment to households in England only."
    ),
    "england_only_average": (
        "IFS averages the payment across households in England, and we publish an "
        "average across all UK households, with no figure for England alone."
    ),
    "fuel_duty_base": (
        "HM Treasury scores fuel duty on every litre of taxable fuel in the UK, "
        "and we estimate the duty and VAT on the fuel households buy."
    ),
    "zero_both_sides": (
        "We and the producer both estimate no change in this year, so we leave it "
        "out of the comparison."
    ),
    "measure_ended": (
        "The government ends the allowance on 5 April 2030, so we estimate no "
        "change in this year, while HM Treasury and the OBR each count a change in "
        "receipts."
    ),
    "exchequer_component": (
        "The OBR estimates one part of the measure's effect on the public finances, "
        "such as a tax head, spending line or block grant adjustment, and we "
        "estimate the whole effect."
    ),
    "cumulative_real_terms": (
        "Tax Policy Associates sums 2026-27 to 2031-32 in 2026-27 prices, and we "
        "estimate each year in cash."
    ),
    "vigintile_ahc_breakdown": (
        "Resolution Foundation groups households into twentieths of income after "
        "housing costs, and we group them into tenths of income before housing "
        "costs."
    ),
    "household_count": (
        "HM Treasury counts households receiving support, and we publish no count "
        "of households."
    ),
    "share_of_households": (
        "The producer reports the share of households or properties eligible for, "
        "receiving or missing the payment; we estimate the share of people whose "
        "household income changes."
    ),
    "typical_bill": (
        "The producer prices one typical household's energy bill, and we estimate "
        "changes in household income, not bills."
    ),
    "worked_example": (
        "The producer works through one example household's tax or income, and we "
        "compare population totals here."
    ),
    "motorists_count": (
        "HM Treasury counts motorists and businesses, and we count no drivers."
    ),
    "benefit_recipients_count": (
        "HM Treasury counts carers who gain Carer's Allowance, and we count people "
        "whose own taxes or earnings change by at least £1 in households with an "
        "income decile."
    ),
    "taken_out_of_tax_count": (
        "HM Treasury counts pensioners who stop paying income tax, and we count "
        "people whose own income tax falls by at least £1 in households with an "
        "income decile."
    ),
    "no_fiscal_year": (
        "HM Treasury counts people by the end of the Parliament, rather than in one "
        "fiscal year."
    ),
}


def test_each_reason_reads_as_we_wrote_it():
    """We pin each reason's words, not only the producers it names."""
    assert S.REASONS == REASONS


PRODUCER_NAMES = {
    "hm_treasury": "HM Treasury",
    "ifs": "IFS",
    "obr_efo": "the OBR",
    "resolution_foundation": "Resolution Foundation",
    "tax_policy_associates": "Tax Policy Associates",
}


def _names(reason, producer):
    pattern = rf"\b{re.escape(PRODUCER_NAMES[producer])}\b"
    return re.search(pattern, S.REASONS[reason], re.IGNORECASE) is not None


def test_each_reason_names_the_producers_whose_claims_it_covers():
    covers = {}
    for claim in CLAIMS:
        reason = S.classify(claim)[1]
        if reason:
            covers.setdefault(reason, set()).add(claim["source"])
    assert set(covers) == set(S.REASONS)
    for reason, sources in covers.items():
        if "the producer" in S.REASONS[reason].lower():
            assert len(sources) > 1, reason
            continue
        named = {p for p in PRODUCER_NAMES if _names(reason, p)}
        assert named == sources, reason


@pytest.mark.parametrize(
    "reason", ["benefit_recipients_count", "taken_out_of_tax_count"]
)
def test_the_count_reasons_state_the_dashboards_minimum_and_filter(reason):
    assert "by at least £1 in households with an income decile." in S.REASONS[reason]


def _england_average():
    (claim,) = [
        c
        for c in CLAIMS
        if c["metric"] == "average_household_income_change"
        and c["conditions"].get("geography") == "England"
    ]
    return copy.deepcopy(claim)


def test_the_england_only_average_is_tallied():
    claim = _england_average()
    assert claim["source"] == "ifs"
    assert claim["measure_key"] == next(iter(S.DEVOLVED_SHARE_NOT_MODELLED))
    assert claim["unit"] == "gbp_per_household"
    assert S.classify(claim) == (None, "england_only_average")
    assert TALLY["reasons"]["england_only_average"] == 1


def test_a_spending_decile_average_on_another_measure_or_area_raises():
    moved = _england_average()
    moved["measure_key"] = S.TRADING
    with pytest.raises(S.Unmatched, match="income axis"):
        S.classify(moved)
    uk = _england_average()
    uk["conditions"]["geography"] = "UK"
    with pytest.raises(S.Unmatched, match="income axis"):
        S.classify(uk)


def _paired_claim(metric):
    row = next(r for r in ROWS if r["metric"] == metric)
    return copy.deepcopy(BY_ID[row["external_claim_match"]["claim_id"]])


NOT_THE_UK = ["England", "Scotland", "Wales", "Northern Ireland", "Great Britain", None]


@pytest.mark.parametrize("geography", NOT_THE_UK)
def test_a_gainer_claim_on_part_of_the_uk_raises(geography):
    claim = _paired_claim("gainer_count")
    claim["conditions"]["geography"] = geography
    with pytest.raises(S.Unmatched, match="gainer geography"):
        S.classify(claim)


@pytest.mark.parametrize("unit", ["households", "gbp", "gbp_per_household", "percent"])
def test_a_gainer_claim_in_another_unit_raises(unit):
    claim = _paired_claim("gainer_count")
    claim["unit"] = unit
    with pytest.raises(S.Unmatched, match="gainers on"):
        S.classify(claim)


@pytest.mark.parametrize(
    "field, value",
    [
        *(("unit", u) for u in ("usd", "eur", "gbp_per_household", "persons")),
        *(("geography", g) for g in NOT_THE_UK),
        *(("fy", y) for y in ("2027", "2027-2028", None)),
    ],
)
def test_an_exchequer_claim_of_another_shape_raises(field, value):
    claim = _paired_claim("revenue_change")
    if field == "unit":
        claim["unit"] = value
    else:
        claim["conditions"][field] = value
    with pytest.raises(S.Unmatched, match="exchequer claim shape"):
        S.classify(claim)


@pytest.mark.parametrize(
    "convention, reading",
    [
        (None, "unknown"),
        ("", "unknown"),
        ("the tables print no legend", "unknown"),
        (signs.MAGNITUDE_CONVENTION, "magnitude"),
    ],
)
def test_an_exchequer_claim_without_a_readable_sign_raises(convention, reading):
    """The stager raises on a convention it can't read and on one that leaves
    the direction to a label."""
    for row in EXCHEQUER_ROWS():
        claim = copy.deepcopy(BY_ID[row["external_claim_match"]["claim_id"]])
        claim["conditions"]["sign_convention"] = convention
        with pytest.raises(S.Unmatched, match=f"sign {reading} "):
            S.classify(claim)


@SETTINGS
@given(
    metric=st.sampled_from(["revenue_change", "gainer_count"]),
    key=st.one_of(
        st.sampled_from(sorted(ingest_obr_costings.measures())),
        st.text(min_size=1, max_size=20),
    ),
)
def test_a_claim_on_the_obr_costings_lane_raises(metric, key):
    claim = _paired_claim(metric)
    claim["conditions"]["obr_measure_key"] = key
    with pytest.raises(S.Unmatched, match="OBR costings lane"):
        S.classify(claim)


def _exchequer_claims(key):
    return [
        c
        for c in CLAIMS
        if c["measure_key"] == key
        and c["metric"] == "revenue_change"
        and S.classify(c)[1] not in ("exchequer_component", "cumulative_real_terms")
    ]


def test_every_fuel_duty_exchequer_row_is_tallied_for_its_base():
    rows = _exchequer_claims(S.FUEL_DUTY)
    assert len(rows) == 6
    assert {c["source"] for c in rows} == {"hm_treasury"}
    assert {S.classify(c) for c in rows} == {(None, "fuel_duty_base")}


def test_the_pension_tax_allowance_after_it_ends_is_tallied():
    ended = [
        c
        for c in _exchequer_claims(S.PENSION_TAX_ALLOWANCE)
        if c["conditions"]["fy"] in ("2030-31", "2031-32")
    ]
    assert len(ended) == 4
    for c in ended:
        assert c["value"] != 0
        path, column, where = S.exchequer_cell(c)
        assert float(S.cell(path, column, where)) == 0
        assert S.classify(c) == (None, "measure_ended")


def test_a_nonzero_claim_against_our_zero_on_another_measure_raises():
    zero = next(
        c
        for c in UNANSWERED
        if c["reason"] == "zero_both_sides" and c["measure_key"] == S.PROPERTY
    )
    claim = copy.deepcopy(BY_ID[zero["claim_id"]])
    claim["value"] = 50_000_000.0
    with pytest.raises(S.Unmatched, match="reads zero"):
        S.classify(claim)


def test_zero_rows_read_zero_in_the_claim_and_the_cell():
    zeros = [u for u in UNANSWERED if u["reason"] == "zero_both_sides"]
    assert zeros
    for u in zeros:
        claim = BY_ID[u["claim_id"]]
        assert claim["value"] == 0
        path, column, where = S.exchequer_cell(claim)
        assert float(S.cell(path, column, where)) == 0
    for row in EXCHEQUER_ROWS():
        assert row["pe_value"] != 0


def EXCHEQUER_ROWS():
    return [r for r in ROWS if r["metric"] == "revenue_change"]


# --- reader-facing annotations ---------------------------------------------------

TIMING = (
    "We count each year's tax liabilities and benefit payments, while HM "
    "Treasury and the OBR count tax when it reaches the Exchequer, often in a "
    "later year."
)
SIGN = "Both sides show a cost to the Exchequer as negative (PE's own orientation)."
REVERSED = "We reverse our sign to match the claim's (PE oriented to it)."
CHANGE = (
    "We estimate the change in government revenue less spending from the "
    "dashboard's budgetary impact table."
)


# The test's own reading of the OBR's breakdown: which lines gov_balance
# counts, which take their own sentence, and what a reader calls the rest.
SKIP_PREFIXES = ("Receipts:", "Tax head (receipts)")
SKIP_LINES = ("Current AME: Welfare inside cap", "behavioural erosion of yield")
READER_NAME = {
    "Current AME: Scottish BGA (current)": "the Scottish block grant adjustment",
    "Current AME: Scottish self-financed expenditure": (
        "Scottish self-financed expenditure"
    ),
    "Current DEL: PSCE in RDEL": "departmental resource spending",
    "Current AME: Other AME (current)": "other annually managed expenditure",
}
VOWEL_SOUND = {8, 11, 18, *range(80, 90), *range(800, 900)}


def _breakdown(claim):
    """(article, £m, cost or gain, reader name) for every nonzero line of the
    OBR's breakdown on the claim's measure and year that our run doesn't
    model, read from the claims."""
    key, fy = claim["measure_key"], claim["conditions"]["fy"]
    out = []
    for c in sorted(
        (
            c
            for c in CLAIMS
            if c["source"] == "obr_efo"
            and c["measure_key"] == key
            and c["conditions"].get("fy") == fy
            and c["metric"] == "revenue_change"
            and c["conditions"].get("row_type") == "measure_component"
            and c["value"] != 0
        ),
        key=lambda c: c["conditions"]["component"],
    ):
        name = c["conditions"]["component"]
        if name.startswith(SKIP_PREFIXES) or name in SKIP_LINES:
            continue
        m = round(abs(c["value"]) / 1e6)
        out.append(
            (
                "an" if m in VOWEL_SOUND else "a",
                m,
                "cost" if c["value"] < 0 else "gain",
                READER_NAME[name],
            )
        )
    return out


def _expected_breakdown(claim):
    lines = _breakdown(claim)
    if not lines:
        return None
    parts = [f"{a} £{m:,}m {kind} from {name}" for a, m, kind, name in lines]
    if len(parts) == 1:
        return f"The OBR also counts {parts[0]} in this year, which we don't model."
    tail = "we model neither" if len(parts) == 2 else "we model none of them"
    listed = ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"The OBR also counts {listed} in this year, and {tail}."


def _opening(claim):
    """The two sentences every row opens with."""
    theirs = (
        "the OBR measures it from its forecast before the Budget's measures"
        if claim["source"] == "obr_efo"
        else "HM Treasury names no baseline in its table"
    )
    return [
        f"We estimate fiscal year {claim['conditions']['fy']} from PolicyEngine's "
        "static Budget-day run on the Autumn Budget dashboard, with no behavioural "
        "response.",
        "We measure the change from current law in policyengine-uk 2.151.0, and "
        f"{theirs}.",
    ]


def _erosion():
    (line,) = [
        c
        for c in CLAIMS
        if c["measure_key"] == S.PROPERTY
        and c["conditions"].get("component") == "behavioural erosion of yield"
    ]
    return line


def test_every_exchequer_row_carries_exactly_its_annotations():
    rows = EXCHEQUER_ROWS()
    assert len(rows) == 34
    for row in rows:
        claim = BY_ID[row["external_claim_match"]["claim_id"]]
        key = claim["measure_key"]
        want = [*_opening(claim), CHANGE, TIMING, SIGN, *SCOPE[key]]
        if key == S.PROPERTY and int(claim["conditions"]["fy"][:4]) >= 2028:
            want.append(BEHAVIOURAL.format(f"{_erosion()['value'] / 1e9:.1f}"))
        if (lines := _expected_breakdown(claim)) is not None:
            want.append(lines)
        assert row["annotations"] == want, row["external_claim_match"]


def test_the_article_follows_the_spoken_amount():
    for m, a in [
        (1, "a"),
        (5, "a"),
        (8, "an"),
        (10, "a"),
        (11, "an"),
        (18, "an"),
        (21, "a"),
        (80, "an"),
        (89, "an"),
        (90, "a"),
        (100, "a"),
        (110, "a"),
        (180, "a"),
        (800, "an"),
        (11000, "an"),
    ]:
        assert S.article(m) == a, m


def test_a_lines_sign_chooses_cost_or_gain():
    assert S.cost_or_gain("x", -8e6) == "an £8m cost from x"
    assert S.cost_or_gain("x", 7e6) == "a £7m gain from x"
    (row,) = [
        r
        for r in EXCHEQUER_ROWS()
        if r["measure_key"] == S.TRADING
        and r["source"] == "obr_efo"
        and r["trace"]["where"]["year"] == "2027"
    ]
    assert (
        "The OBR also counts an £8m cost from the Scottish block grant adjustment "
        "and a £7m gain from Scottish self-financed expenditure in this year, and we "
        "model neither."
    ) in row["annotations"]


SCOPE = {
    "ab2026__carers_allowance_earnings_taper": (
        "We apply the taper in England and Wales and leave Northern Ireland's "
        "Carer's Allowance at current law.",
        "We count the extra allowance in full against Universal Credit but omit the "
        "PAYE deduction from earnings that DWP would apply, so we can show some "
        "carers losing overall.",
    ),
    "ab2026__property_income_rates_plus_2pp": (
        "We raise property income tax rates in England, Wales and Northern Ireland, "
        "and finance cost relief for landlords across the UK, as the government "
        "does from 6 April 2027.",
    ),
    "ab2026__electricity_vat_zero_rate_to_july_2027": (
        "HM Treasury costs the zero rate on household, charity, residential care "
        "and a small amount of business electricity, and we estimate it on "
        "household electricity only.",
    ),
    "ab2026__pension_tax_allowance": (
        "We net off any change in means-tested benefits that follows from lower "
        "income tax, and the OBR counts no change in welfare spending on this "
        "measure.",
    ),
    "ab2026__trading_allowance_3000": (
        "We have no gross trading receipts in our data, so we relieve profits up "
        "to £3,000 in full and give no relief above it. As a result, we may "
        "overstate the Exchequer's cost for some traders and understate it for "
        "others.",
    ),
}
BEHAVIOURAL = (
    "The OBR expects more landlords to incorporate to save tax and more to underpay, "
    "cutting the yield by £{} billion a year, and we hold incomes fixed."
)


def test_the_carers_allowance_receipt_states_the_universal_credit_limit():
    description = S.receipt(S.CARERS, MANIFEST)["dashboard"]["description"]
    assert "deducts none of the PAYE on it from earnings, as DWP would" in description
    assert "such a carer can lose overall" in description


def test_property_rows_from_2028_29_carry_the_behavioural_line():
    want = BEHAVIOURAL.format(f"{_erosion()['value'] / 1e9:.1f}")
    rows = [r for r in EXCHEQUER_ROWS() if r["measure_key"] == S.PROPERTY]
    assert len(rows) == 10
    for row in rows:
        late = int(row["trace"]["where"]["year"]) >= 2028
        assert (want in row["annotations"]) == late, row["trace"]
    assert all(
        "incorporate" not in n
        for r in EXCHEQUER_ROWS()
        if r["measure_key"] != S.PROPERTY
        for n in r["annotations"]
    )


def _with_convention(monkeypatch, component, convention):
    moved = copy.deepcopy(CLAIMS)
    line = next(
        c
        for c in moved
        if c["source"] == "obr_efo" and c["conditions"].get("component") == component
    )
    line["conditions"]["sign_convention"] = convention
    monkeypatch.setattr(S, "claims", lambda: moved)
    monkeypatch.setattr(S, "_COMPONENTS", None)


@pytest.mark.parametrize(
    "convention",
    [
        "Note (verbatim): A positive sign implies an increase in borrowing.",
        "Note (verbatim): This table uses the convention that a negative sign implies "
        "a gain to the Exchequer",
        None,
    ],
    ids=["borrowing", "gain", "none"],
)
def test_a_named_line_under_another_sign_convention_raises(monkeypatch, convention):
    _with_convention(monkeypatch, "Current AME: Scottish BGA (current)", convention)
    with pytest.raises(S.Unmatched, match="another sign convention"):
        S.components()


@pytest.mark.parametrize(
    "convention",
    ["as worded: positive = increase in yield", None],
    ids=["yield", "none"],
)
def test_the_behavioural_line_under_another_sign_convention_raises(
    monkeypatch, convention
):
    _with_convention(monkeypatch, "behavioural erosion of yield", convention)
    with pytest.raises(S.Unmatched, match="another sign convention"):
        S.components()


def test_two_claims_on_one_named_line_raise(monkeypatch):
    line = next(
        c
        for c in CLAIMS
        if c["source"] == "obr_efo"
        and c["conditions"].get("component") == "Current AME: Scottish BGA (current)"
    )
    twin = copy.deepcopy(line)
    twin["claim_id"] = "twin"
    monkeypatch.setattr(S, "claims", lambda: [*CLAIMS, twin])
    monkeypatch.setattr(S, "_COMPONENTS", None)
    with pytest.raises(S.Unmatched, match="two OBR claims"):
        S.components()


def test_two_claims_on_a_receipts_head_pass(monkeypatch):
    line = next(
        c
        for c in CLAIMS
        if c["source"] == "obr_efo"
        and c["conditions"].get("component", "").startswith("Receipts:")
    )
    twin = copy.deepcopy(line)
    twin["claim_id"] = "twin"
    twin["value"] = -line["value"]
    monkeypatch.setattr(S, "claims", lambda: [*CLAIMS, twin])
    monkeypatch.setattr(S, "_COMPONENTS", None)
    S.components()


def test_carers_allowance_rows_name_northern_ireland():
    for row in EXCHEQUER_ROWS():
        if row["measure_key"] == S.CARERS:
            assert any(
                "leave Northern Ireland's Carer's Allowance at current law" in n
                for n in row["annotations"]
            )


def test_electricity_rows_name_hm_treasurys_base():
    rows = [r for r in EXCHEQUER_ROWS() if r["measure_key"] == S.ELECTRICITY]
    assert len(rows) == 4
    for row in rows:
        assert set(SCOPE[S.ELECTRICITY]) <= set(row["annotations"])


def test_a_welfare_change_on_the_pension_tax_allowance_raises(monkeypatch):
    row = next(
        r for r in EXCHEQUER_ROWS() if r["measure_key"] == S.PENSION_TAX_ALLOWANCE
    )
    claim = BY_ID[row["external_claim_match"]["claim_id"]]
    fake = dict(S.components())
    fake[(S.PENSION_TAX_ALLOWANCE, claim["conditions"]["fy"], S.WELFARE)] = -5e6
    monkeypatch.setattr(S, "_COMPONENTS", fake)
    with pytest.raises(S.Unmatched, match="welfare"):
        S.scope_annotations(claim)


def test_a_behavioural_line_on_another_measure_raises(monkeypatch):
    row = next(r for r in EXCHEQUER_ROWS() if r["measure_key"] == S.TRADING)
    claim = BY_ID[row["external_claim_match"]["claim_id"]]
    fake = dict(S.components())
    fake[(S.TRADING, claim["conditions"]["fy"], "behavioural erosion of yield")] = 5e7
    monkeypatch.setattr(S, "_COMPONENTS", fake)
    with pytest.raises(S.Unmatched, match="no reader name"):
        S.scope_annotations(claim)


@pytest.mark.parametrize(
    "name", ["Current AME: Something new", "Capital DEL: something", "a new line"]
)
def test_an_unnamed_breakdown_line_raises(monkeypatch, name):
    row = EXCHEQUER_ROWS()[0]
    claim = BY_ID[row["external_claim_match"]["claim_id"]]
    fake = dict(S.components())
    fake[(claim["measure_key"], claim["conditions"]["fy"], name)] = 3e6
    monkeypatch.setattr(S, "_COMPONENTS", fake)
    with pytest.raises(S.Unmatched, match="no reader name"):
        S.scope_annotations(claim)


def test_the_gainer_row_carries_its_population():
    (row,) = [r for r in ROWS if r["metric"] == "gainer_count"]
    assert row["annotations"] == [
        *_opening(BY_ID[row["external_claim_match"]["claim_id"]]),
        "We count people whose own income tax, National Insurance, student loan "
        "repayment or earnings change by £1 a year or more, leaving out households "
        "we place in no income decile.",
        "Of the four, the government changes only income tax through this "
        'allowance. HM Treasury counts "pensioners in total benefitting from a tax '
        'reduction" and states no minimum.',
    ]


SUB_UK = (
    "England",
    "Wales",
    "Scotland",
    "Northern Ireland",
    "Great Britain",
    "GB",
    "Scottish",
    "Welsh",
)


def test_every_sub_uk_measure_takes_a_tally_or_a_scope_annotation():
    named = 0
    for key in MEASURES:
        if not any(c["measure_key"] == key for c in CLAIMS):
            continue
        description = S.receipt(key, MANIFEST)["dashboard"]["description"]
        if not any(re.search(rf"\b{p}\b", description) for p in SUB_UK):
            continue
        named += 1
        tallied = TALLY["by_measure"][key]["reasons"].get(
            "devolved_share_not_modelled", 0
        )
        rows = [r for r in EXCHEQUER_ROWS() if r["measure_key"] == key]
        annotated = rows and all(
            len(S.scope_annotations(BY_ID[r["external_claim_match"]["claim_id"]])) >= 1
            and set(S.scope_annotations(BY_ID[r["external_claim_match"]["claim_id"]]))
            <= set(r["annotations"])
            for r in rows
        )
        assert tallied or annotated, key
    assert named == 4  # Carer's Allowance, electricity, the payment, property


# --- the pinned pairing -------------------------------------------------------


def test_the_staging_pins_each_claims_file_column_and_row():
    pinned = json.loads(S.EXPECTED.read_text())["pairing"]
    assert pinned == S.pairing(ROWS, CLAIMS)
    S.check(TALLY, ROWS, CLAIMS)
    shifted = copy.deepcopy(ROWS)
    year = shifted[0]["trace"]["where"]["year"]
    shifted[0]["trace"]["where"]["year"] = str(int(year) + 1)
    with pytest.raises(ValueError, match="pairing drifted"):
        S.check(TALLY, shifted, CLAIMS)
    moved = copy.deepcopy(CLAIMS)
    paired = ROWS[0]["external_claim_match"]["claim_id"]
    next(c for c in moved if c["claim_id"] == paired)["value"] += 1e6
    with pytest.raises(ValueError, match="pairing drifted"):
        S.check(TALLY, ROWS, moved)


def test_the_cell_year_and_the_claim_year_agree():
    for row in ROWS:
        claim = BY_ID[row["external_claim_match"]["claim_id"]]
        start, end = claim["conditions"]["fy"].split("-")
        from_claim = int(start)
        assert int(end) == (from_claim + 1) % 100
        rec = S.receipt(claim["measure_key"], MANIFEST)
        label = rec["execution_receipt"]["fiscal_year"]
        assert label["year_label"] == "start_year"
        from_cell = int(row["trace"]["where"]["year"])
        assert from_cell == from_claim


def test_a_claim_no_rule_names_raises():
    claim = copy.deepcopy(CLAIMS[0])
    claim["metric"] = "gini_change"
    with pytest.raises(S.Unmatched):
        S.classify(claim)


def test_drifted_accounting_raises():
    tally = copy.deepcopy(TALLY)
    tally["computed"] -= 1
    tally["reasons"]["typical_bill"] = tally["reasons"].get("typical_bill", 0) + 1
    with pytest.raises(ValueError, match="drifted"):
        S.check(tally)


# --- 5. signs ------------------------------------------------------------------

EXCHEQUER = [r for r in ROWS if r["metric"] == "revenue_change"]
FLIPPED = {
    signs.SAME: "positive = cost to the Exchequer",
    signs.OPPOSITE: "positive = yield to the Exchequer",
}


@SETTINGS
@given(i=st.integers(min_value=0, max_value=len(EXCHEQUER) - 1))
def test_a_sign_flip_flips_the_relation_and_keeps_the_magnitude(i):
    row = EXCHEQUER[i]
    claim = BY_ID[row["external_claim_match"]["claim_id"]]
    relation, _ = S.sign_relation(claim)
    flipped = copy.deepcopy(claim)
    flipped["conditions"]["sign_convention"] = FLIPPED[relation]
    flipped["value"] = -claim["value"]
    other, _ = S.sign_relation(flipped)
    assert {relation, other} == {signs.SAME, signs.OPPOSITE}
    again = S.counterpart(flipped, "exchequer", MANIFEST)
    oriented = {signs.SAME: SIGN, signs.OPPOSITE: REVERSED}
    assert oriented[other] in again["annotations"]
    assert oriented[relation] not in again["annotations"]
    assert again["pe_value"] == -row["pe_value"]
    assert abs(again["pe_value"]) == abs(row["pe_value"])
    # the comparison's relation: the claim's value and the counterpart, both
    # in the claim's orientation, keep their ratio when both flip
    if row["pe_value"] and claim["value"]:
        assert again["pe_value"] / flipped["value"] == pytest.approx(
            row["pe_value"] / claim["value"]
        )


def test_an_exported_counterpart_reads_as_oriented_to_its_claim():
    for row in EXCHEQUER:
        claim = BY_ID[row["external_claim_match"]["claim_id"]]
        exported = {
            "metric": claim["metric"],
            "conditions": claim["conditions"],
            "country": "UK",
            "source": claim["source"],
            "latest": {"annotations": row["annotations"]},
        }
        assert signs.classify(exported) == (signs.SAME, "result_oriented_to_claim")


# --- 6. determinism ------------------------------------------------------------


def test_two_runs_give_the_same_output():
    assert S.stage(S.claims()) == (ROWS, TALLY, UNANSWERED)


@SETTINGS
@given(seed=st.integers(min_value=0, max_value=2**32 - 1))
def test_any_order_of_the_claims_gives_the_same_output(seed):
    shuffled = list(CLAIMS)
    random.Random(seed).shuffle(shuffled)
    rows, tally, unanswered = S.stage(shuffled, MANIFEST)
    assert S.dumps_jsonl(rows) == S.dumps_jsonl(ROWS)
    assert tally == TALLY
    assert unanswered == UNANSWERED


@SETTINGS
@given(data=st.data())
def test_any_sample_of_the_claims_closes_its_accounting(data):
    picks = data.draw(st.sets(st.sampled_from(sorted(BY_ID)), max_size=60))
    sample = [BY_ID[i] for i in sorted(picks)]
    rows, tally, unanswered = S.stage(sample, MANIFEST)
    assert tally["claims"] == len(sample)
    assert tally["claims"] == tally["computed"] + sum(tally["reasons"].values())
    want = {r["external_claim_match"]["claim_id"]: r for r in ROWS}
    for r in rows:
        assert r == want[r["external_claim_match"]["claim_id"]]


# --- 7. one answer per claim, and 8. the database ------------------------------


def test_no_claim_gets_two_computed_answers_in_the_staging():
    ids = [r["external_claim_match"]["claim_id"] for r in ROWS]
    assert len(ids) == len(set(ids))
    assert not any(c["conditions"].get("obr_measure_key") for c in CLAIMS)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("ab2026")
    db_path = tmp / "t.db"
    ScorecardDB(db_path).close()
    feed = tmp / "lanes.json"  # a copy: never the committed feed
    clone_copy.copy(ROOT / "data" / "lanes.json", feed)
    I.ingest(db_path, feed)
    I.ingest_verdicts(db_path)
    attached = ingest_campaign.ingest(db_path, I.STAGED_COUNTERPARTS)
    lanes = I.advance_lanes(db_path, feed)
    I.advance_lanes(db_path, feed)  # idempotent
    return db_path, feed, attached, lanes


def test_a_built_database_shows_each_comparison(built):
    db_path, _, attached, _ = built
    assert attached["attached"] == len(ROWS)
    conn = sqlite3.connect(db_path)
    got = {
        cid: (value, status, bk, run)
        for cid, value, status, bk, run in conn.execute(
            "SELECT claim_id, computed_value, status, baseline_key, run_id"
            " FROM pe_results WHERE run_id = ?",
            (S.RUN_ID,),
        )
    }
    assert got == {
        r["external_claim_match"]["claim_id"]: (
            r["pe_value"],
            "constructed",
            S.CURRENT_LAW,
            S.RUN_ID,
        )
        for r in ROWS
    }
    # each claim holds at most one counterpart, and none holds a pe_gap
    # verdict beside it
    many = conn.execute(
        "SELECT claim_id, COUNT(*) FROM pe_results GROUP BY claim_id"
        " HAVING COUNT(*) > 1"
    ).fetchall()
    assert many == []
    conn.close()


def test_advance_lanes_moves_only_the_lanes_with_counterparts(built):
    db_path, feed, _, lanes = built
    answered = Counter()
    families = {f: lane for f, (lane, _) in I.FAMILIES.items()}
    conn = sqlite3.connect(db_path)
    for row in ROWS:
        fam = conn.execute(
            "SELECT json_extract(publication, '$.family') FROM external_scores"
            " WHERE claim_id = ?",
            (row["external_claim_match"]["claim_id"],),
        ).fetchone()[0]
        answered[families[fam]] += 1
    stages = dict(
        conn.execute("SELECT lane, stage FROM lanes WHERE lane LIKE 'uk-ab2026-%'")
    )
    conn.close()
    for lane in I.LANES:
        assert lanes[lane]["answered"] == answered[lane]
        assert stages[lane] == ("computed" if answered[lane] else "ingested")
    fed = {lane["id"]: lane for lane in json.loads(feed.read_text())["lanes"]}
    assert {lane: fed[lane]["stage"] for lane in I.LANES} == stages


def test_build_db_calls_none_of_tranche_3():
    text = (ROOT / "scorecard_db" / "build_db.py").read_text()
    assert "ingest_uk_ab2026" not in text
    assert "stage_uk_ab2026" not in text
    assert "staged_ab2026" not in text
