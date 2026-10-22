"""Comparables: every PolicyEngine analysis is searched against every external
producer before it is published and again before it is promoted
(docs/COMPARABLES.md).

One directory per analysis, ``sources/analysis-<country>-<slug>/``:

    analysis.json         the analysis: its registry entry on policyengine.org,
                          scope, search terms, the policy worlds it scores and
                          the PolicyEngine estimates it publishes, each pinned
                          to the results file it was read from (SHA-256)
    search_log.json       every search: date, kind, who ran it, the results
                          files it compared against, and one entry per producer
                          in data/comparables/producers.json (found /
                          none_found / found_not_staged / not_applicable, the
                          queries run and the pages checked)
    manifest.jsonl        one line per primary publication, hashed
    claims_staged.jsonl   every comparable found, staged under the harvest
                          rules: the value as printed and normalised, the
                          quantity it measures (metric, unit, period, basis,
                          programme, world), attribution and benchmark class;
                          plus the PolicyEngine estimate it is compared with,
                          or the nearest one and why they differ
    annotations.json      the status and cause of anything that is not a plain
                          comparison within the threshold, each citing a basis

The validator below is the gate: a directory that fails it fails CI and the
database build, so everything on main is a complete record. ``build_index``
writes data/comparables/index.json, which policyengine-app-v2's and
PolicyEngine/newsletters' CI read. Nothing in this module reads the network.

    PYTHONPATH=. python -m scorecard_db.comparables check
    PYTHONPATH=. python -m scorecard_db.comparables index [--check]
    PYTHONPATH=. python -m scorecard_db.comparables scaffold --country uk \\
        --kind app --slug childcare-100k-threshold
    PYTHONPATH=. python -m scorecard_db.comparables pins \\
        analysis-uk-childcare-100k-threshold
    PYTHONPATH=. python -m scorecard_db.comparables record \\
        analysis-uk-childcare-100k-threshold
    PYTHONPATH=. python -m scorecard_db.comparables due \\
        --apps apps.json --posts posts.json --today 2026-10-26
    PYTHONPATH=. python -m scorecard_db.comparables report \\
        analysis-uk-childcare-100k-threshold --since 2026-10-21
    PYTHONPATH=. python -m scorecard_db.comparables fresh \\
        analysis-uk-childcare-100k-threshold --on 2026-10-26
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from . import signs
from .models import ComparisonStatus, Metric, TimeBasis, UnitConcept

REPO = Path(__file__).resolve().parent.parent
SOURCES = REPO / "sources"
COMPARABLES = REPO / "data" / "comparables"
POLICY_PATH = COMPARABLES / "policy.json"
PRODUCERS_PATH = COMPARABLES / "producers.json"
INDEX_PATH = COMPARABLES / "index.json"
REPO_URL = "https://github.com/PolicyEngine/policyengine-scorecard"

ANALYSIS_SCHEMA = "comparables/analysis/1"
SEARCH_SCHEMA = "comparables/search/1"
INDEX_SCHEMA = "comparables/index/1"
DIR_PREFIX = "analysis-"

# prepublish: before the analysis is listed. backfill: the first search of an
# analysis listed before the gate, made after it was published. reharvest: the
# weekly search after publication. prepromotion: a fresh search before a
# newsletter, social campaign, webinar or press push features the analysis.
SEARCH_KINDS = ("prepublish", "backfill", "reharvest", "prepromotion")
FIRST_KINDS = ("prepublish", "backfill")
LATER_KINDS = ("reharvest", "prepromotion")
# Searches made after publication. What they find may wait on its owner's
# tracking issue (`pending`); what a prepublish search finds never may, and an
# analysis is never promoted with a pending gap (``fresh``).
POST_PUBLICATION_KINDS = ("backfill", "reharvest", "prepromotion")
# found_not_staged: a comparable exists but its primary cannot be read (harvest
# rule 8: a figure whose primary could not be read is never a claim); the note
# says what it is and where it was seen.
RESULTS = ("found", "none_found", "found_not_staged", "not_applicable")
VALUE_KINDS = (
    "point",
    "central",
    "range_low",
    "range_high",
    "approx_chart_reading",
    "cumulative",
)
RANGE_KINDS = ("range_low", "range_high")
ATTRIBUTIONS = ("own", "restated", "same_assumptions")
BENCHMARK_CLASSES = ("different_model", "administrative_fact", "same_assumptions")
PARSE_CONFIDENCE = ("high", "medium", "low")
BASIS_KINDS = ("issue", "document", "engine_metadata", "diagnostic")
# The basis of an estimate or claim: what it holds fixed. Required on every
# estimate and claim, and part of what makes two figures the same quantity.
BASES = ("static", "post_behavioural", "forecast", "outturn")
# A claim compared with an estimate has one of these statuses; a mismatch
# means it is not compared, so it never labels a compared claim.
COMPARED_STATUSES = (
    ComparisonStatus.COMPARABLE.value,
    ComparisonStatus.CONSTRUCTED.value,
    ComparisonStatus.PE_GAP.value,
    "pending",
)
# An uncompared claim beside its nearest estimate carries one of these.
MISMATCH_STATUSES = (
    ComparisonStatus.CONCEPT_MISMATCH.value,
    ComparisonStatus.PE_GAP.value,
)
ANNOTATION_STATUSES = tuple(dict.fromkeys(COMPARED_STATUSES + MISMATCH_STATUSES))
BASELINE_WORLD = "baseline"
# Searches that may find a producer not on the list; the claim then names
# that producer's own slug.
OPEN_FINDERS = ("open_search", "academic")
# A claim's source is the producer that published it: never a search, and
# never PolicyEngine, which is not its own comparable.
BANNED_SOURCES = ("open_search", "academic", "policyengine")
# Everything that makes a claim and an estimate the same quantity.
IDENTITY_FIELDS = ("metric", "unit_concept", "period", "time_basis", "world")
IDENTITY_CONDITIONS = ("basis", "program")

# What makes a policyengine.org entry publish an estimate, and when it may say
# it publishes none. The same rule is in policyengine-app-v2's
# website/src/data/comparables.ts and PolicyEngine/newsletters.
ANALYSIS_TAGS = frozenset(
    {
        "policy",
        "technical",
        "autumn-budget",
        "tax",
        "benefit",
        "reconciliation",
        "healthcare",
        "vat",
        "tariffs",
        "child-tax-credit",
        "behavioral-responses",
        "inflation",
        "election",
        "2024-election",
        "benefit-access",
        "interactives",
    }
)
NO_ESTIMATE_TAGS = frozenset(
    {"org", "event", "giving", "conferences", "year-in-review", "april-fools"}
)
COUNTRY_TAGS = ("uk", "us", "ca", "ng", "il")
DEFAULT_COUNTRY = "us"  # the website files a post with no country tag under us

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FY = re.compile(r"^(\d{4})-(\d{2})$")
_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$"
)
_SLUG = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
_KEY = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_REGISTRY_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_PIN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}:[0-9a-f]{64}$")
_GITHUB_ISSUE = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(issues|pull)/\d+"
    r"(#[A-Za-z0-9_-]+)?$"
)
_GITHUB_PINNED = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(blob|tree)/[0-9a-f]{40}/\S+$"
)
_URL = re.compile(r"^https?://\S+$")
# A document or diagnostic URL names a page, not just a host.
_URL_WITH_PATH = re.compile(r"^https://[^/\s]+\.[^/\s]+/\S+$")

# Harvest rule 1: ``value`` is ``value_raw`` normalised to the unit, with the
# conversion named, and the scale a printed value states must be the one the
# conversion assumes. Only these conversions are checked mechanically; a new
# one is added here deliberately, never improvised in a staged row.
NORMALIZATIONS = {
    "as printed": (1.0, None),
    "percent as printed": (1.0, "pct"),
    "fraction x 100 -> percent": (100.0, None),
    "percent / 100 -> fraction": (0.01, "pct"),
    "thousands x 1e3": (1e3, "k"),
    "millions x 1e6": (1e6, "m"),
    "billions x 1e9": (1e9, "bn"),
    "GBP k x 1e3 -> GBP": (1e3, "k"),
    "GBP m x 1e6 -> GBP": (1e6, "m"),
    "GBP bn x 1e9 -> GBP": (1e9, "bn"),
    "USD k x 1e3 -> USD": (1e3, "k"),
    "USD m x 1e6 -> USD": (1e6, "m"),
    "USD bn x 1e9 -> USD": (1e9, "bn"),
    "USD tn x 1e12 -> USD": (1e12, "tn"),
}
_SCALE_WORDS = (
    (re.compile(r"^\s*(?:bn|billion)\b", re.I), "bn"),
    (re.compile(r"^\s*(?:tn|trillion)\b", re.I), "tn"),
    (re.compile(r"^\s*(?:m|mn|million)\b", re.I), "m"),
    (re.compile(r"^\s*(?:k|thousand)\b", re.I), "k"),
    (
        re.compile(r"^\s*(?:%|per\s?cent\b|percent\b|pp\b|percentage points?\b)", re.I),
        "pct",
    ),
)

_NUMBER = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?|\.\d+")
_MINUS = "-−–‒－"
_SIGN_BEFORE = re.compile(r"[" + _MINUS + r"]\s*[£$€]?\s*$")
_MINUS_WORD_BEFORE = re.compile(r"\bminus\s*[£$€]?\s*$", re.I)
_PAREN_BEFORE = re.compile(r"\(\s*[£$€]?\s*$")
_PAREN_AFTER = re.compile(
    r"^\s*(?:bn|billion|mn|m|million|k|thousand|tn|trillion|%)?\s*\)", re.I
)


def _number_match(value_raw: str) -> re.Match:
    if not isinstance(value_raw, str) or not value_raw.strip():
        raise ValueError(f"value_raw must be a nonempty string: {value_raw!r}")
    numbers = list(_NUMBER.finditer(value_raw.strip()))
    if len(numbers) != 1:
        raise ValueError(
            f"value_raw {value_raw!r} carries {len(numbers)} numbers; stage one "
            "number per claim (a range is two claims)"
        )
    return numbers[0]


def parse_printed(value_raw: str) -> float:
    """The number a printed string carries, without its unit or scale.

    "£0.80bn" -> 0.8, "-800m" -> -800, "13,360" -> 13360, "(0.4)" -> -0.4,
    "£(0.4)bn" -> -0.4, "−£1.2 billion" -> -1.2, "2.1 per cent" -> 2.1,
    "post-tax £0.8bn" -> 0.8. A minus sign counts only directly before the
    number (a currency symbol may sit between them). Exactly one number must
    appear; a string with two ("£1.2bn to £1.5bn") is two claims (range_low,
    range_high), never one.
    """
    match = _number_match(value_raw)
    text = value_raw.strip()
    magnitude = float(match.group().replace(",", ""))
    before, after = text[: match.start()], text[match.end() :]
    negative = bool(_SIGN_BEFORE.search(before) or _MINUS_WORD_BEFORE.search(before))
    if _PAREN_BEFORE.search(before) and _PAREN_AFTER.match(after):
        negative = True
    return -magnitude if negative else magnitude


def printed_scale(value_raw: str) -> str | None:
    """The scale a printed value states right after its number, if any."""
    match = _number_match(value_raw)
    after = value_raw.strip()[match.end() :]
    for pattern, scale in _SCALE_WORDS:
        if pattern.match(after):
            return scale
    return None


def quote_contains(quote: str, value_raw: str) -> bool:
    """Whether the quote prints this value as a whole number, sign included:
    "0.07" is not in "10.07", and "800m" is not in "-800m"."""
    q = " ".join(str(quote).split())
    raw = " ".join(str(value_raw).split())
    if not raw:
        return False
    lead = "" if raw[0] in _MINUS else _MINUS
    pattern = rf"(?<![\d.,{re.escape(lead)}]){re.escape(raw)}(?![\d])"
    return re.search(pattern, q) is not None


def check_value(row: dict, where: str, signed: bool = False) -> list[str]:
    """Harvest rule 1 for one row: the value parses back from what was printed,
    at the scale it states.

    A staged claim is never re-signed (its sign convention travels in
    conditions). A PolicyEngine estimate is stated in PolicyEngine's own
    orientation for its metric (signs.ORIENTATION), so ``signed`` rows may
    carry ``sign: -1`` with a ``sign_basis`` when the results file prints the
    quantity the other way round (a cost as a positive number)."""
    errors = []
    sign = row.get("sign", 1)
    if signed:
        if type(sign) is not int or sign not in (1, -1):
            return [f"{where}: sign must be the integer 1 or -1"]
        if sign == -1 and not _nonempty_str(row.get("sign_basis"), 10):
            errors.append(f"{where}: sign -1 needs sign_basis saying why")
    elif "sign" in row:
        return [f"{where}: a staged claim is never re-signed (harvest rule 1)"]
    normalization = row.get("normalization")
    if normalization not in NORMALIZATIONS:
        return [
            (
                f"{where}: normalization {normalization!r} is not registered "
                f"(scorecard_db/comparables.py NORMALIZATIONS: {sorted(NORMALIZATIONS)})"
            )
        ]
    factor, scale = NORMALIZATIONS[normalization]
    value = row.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return [f"{where}: value must be a number, got {value!r}"]
    if not math.isfinite(value):
        return [f"{where}: value must be finite, got {value!r}"]
    try:
        parsed = parse_printed(row.get("value_raw"))
        stated = printed_scale(row.get("value_raw"))
    except ValueError as exc:
        return [f"{where}: {exc}"]
    if stated is not None and stated != scale:
        errors.append(
            f"{where}: value_raw {row.get('value_raw')!r} states the scale "
            f"{stated!r}, but {normalization!r} assumes {scale or 'none'}"
        )
    expected = sign * parsed * factor
    if not math.isclose(value, expected, rel_tol=1e-9, abs_tol=1e-9):
        errors.append(
            f"{where}: value {value!r} is not value_raw {row.get('value_raw')!r} "
            f"under {normalization!r}{' with sign -1' if sign == -1 else ''} "
            f"(expected {expected!r})"
        )
    return errors


# --- the gap -----------------------------------------------------------------

# Words that turn a "positive = ..." phrase around, which signs.py's substring
# match would otherwise read as the plain phrase ("positive = yield forgone").
_INVERTING_WORDS = ("forgone", "foregone", "lost")
# signs.py reads "positive = increase in ..." as the same direction for these
# families whatever follows; a convention naming the other side of the
# ledger ("positive = increase in federal revenue" for a spending metric)
# is not that direction.
_OTHER_SIDE_WORDS = {
    "spending": ("revenue", "receipt", "yield", "tax"),
    "tax_increase": ("credit", "refund", "benefit"),
}


def orientation(claim: dict, country: str) -> tuple[str, str]:
    """How the published value points relative to PolicyEngine's value for the
    metric: scorecard_db/signs.py decides it from the stated sign convention,
    never from comparing the two signs.

    For a change metric the convention must say what a positive value means
    ("positive = ..."), match exactly one of signs.py's directions, and not
    turn its phrase around. Anything else is unknown, so the claim cannot be
    compared until the convention is stated plainly."""
    metric = claim.get("metric")
    conditions = claim.get("conditions") or {}
    text = (conditions.get("sign_convention") or "").strip().lower()
    family = signs.ORIENTATION.get(metric)
    if family is not None:
        if not text.startswith("positive ="):
            return signs.UNKNOWN, "convention must start 'positive = '"
        unanswerable, opposite, same = signs._PHRASES[family]
        hits_opposite = any(p in text for p in opposite)
        hits_same = any(p in text for p in same)
        if hits_opposite and hits_same:
            return signs.UNKNOWN, "convention matches both directions"
        if hits_same and any(w in text for w in _INVERTING_WORDS):
            return signs.UNKNOWN, "convention turns its phrase around"
        if hits_same and any(w in text for w in _OTHER_SIDE_WORDS.get(family, ())):
            return signs.UNKNOWN, "convention names the other side of the ledger"
    return signs.classify(
        {
            "metric": metric,
            "conditions": conditions,
            "country": country,
            "source": claim.get("source"),
        }
    )


def oriented(external_value: float, relation: str) -> float | None:
    """The published value in PolicyEngine's orientation."""
    if relation == signs.SAME:
        return external_value
    if relation == signs.OPPOSITE:
        return -external_value
    return None


def relative_gap(pe_value: float, external_value: float, relation: str) -> float | None:
    """PolicyEngine / external - 1, with the external value in PolicyEngine's
    orientation. None when no rule orients the external value.

    A zero external value gives 0 when PolicyEngine is also zero and +inf
    otherwise, so a nonzero estimate against a published zero is always over
    any threshold. Opposite signs give a gap below -1, which is over every
    threshold the policy allows (thresholds are below 1)."""
    if relation == signs.MAGNITUDE:
        pe, ext = abs(pe_value), abs(external_value)
    else:
        ext = oriented(external_value, relation)
        if ext is None:
            return None
        pe = pe_value
    if ext == 0:
        return 0.0 if pe == 0 else math.inf
    return pe / ext - 1.0


def over_threshold(gap: float | None, threshold: float) -> bool:
    return gap is not None and abs(gap) > threshold


def sign_disagrees(pe_value: float, external_value: float | None) -> bool:
    return (
        external_value is not None
        and pe_value != 0
        and external_value != 0
        and (pe_value > 0) != (external_value > 0)
    )


# --- loading -----------------------------------------------------------------


def today_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def _is_date(value) -> bool:
    if not (isinstance(value, str) and _DATE.match(value)):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate key {key!r}")
        out[key] = value
    return out


def _loads(text: str):
    return json.loads(text, object_pairs_hook=_no_duplicate_keys)


def load_policy(path: Path = POLICY_PATH) -> dict:
    policy = _loads(path.read_text())
    threshold = policy.get("gap_threshold")
    # below 1, so a sign disagreement (a gap below -1) is always over it
    if not (
        isinstance(threshold, (int, float))
        and not isinstance(threshold, bool)
        and 0 < threshold < 1
    ):
        raise ValueError(
            f"{path}: gap_threshold must be a number between 0 and 1: {threshold!r}"
        )
    # PolicyEngine/newsletters refuses an index whose window is outside
    # 1-90 days, so a mistyped window cannot make an old search count
    for key, most in (("promotion_window_days", 90), ("reharvest_window_days", 366)):
        days = policy.get(key)
        if not (
            isinstance(days, int) and not isinstance(days, bool) and 0 < days <= most
        ):
            raise ValueError(
                f"{path}: {key} must be a whole number of days from 1 to {most}: {days!r}"
            )
    return policy


def load_producers(path: Path = PRODUCERS_PATH, today: str | None = None) -> dict:
    data = _loads(path.read_text())
    today = today or today_utc()
    for country, producers in data["countries"].items():
        slugs = [p["slug"] for p in producers]
        if len(slugs) != len(set(slugs)):
            raise ValueError(f"{path}: duplicate producer slugs for {country}")
        for p in producers:
            applies_to = p["applies_to"]
            if applies_to != "all" and not set(applies_to) <= set(
                data["scopes"][country]
            ):
                raise ValueError(
                    f"{path}: {p['slug']} applies_to unknown scope {applies_to}"
                )
            if not _is_date(p["added"]) or p["added"] > today:
                raise ValueError(
                    f"{path}: {p['slug']} added must be a real date, no later than today"
                )
    return data


def required_producers(producers: dict, country: str, on: str) -> list[dict]:
    """Every producer a search on date ``on`` must log, in list order."""
    return [p for p in producers["countries"][country] if p["added"] <= on]


def first_list_date(producers: dict, country: str) -> str:
    return min(p["added"] for p in producers["countries"][country])


def applies(producer: dict, scope: str) -> bool:
    return producer["applies_to"] == "all" or scope in producer["applies_to"]


def producer_for_source(producers: dict, country: str, source: str) -> str | None:
    """The producer slug a claim's ``source`` belongs to, or None when the
    source is not on the list (allowed only for open_search/academic finds)."""
    for p in producers["countries"][country]:
        if source == p["slug"] or source in p.get("aliases", []):
            return p["slug"]
        pattern = p.get("alias_pattern")
        if pattern and re.match(pattern, source):
            return p["slug"]
    return None


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(_loads(line))
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}:{n}: {exc}") from exc
    return rows


@dataclass
class AnalysisRecord:
    directory: Path
    analysis: dict
    search_log: dict
    manifest: list[dict]
    claims: list[dict]
    annotations: list[dict]
    load_errors: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.directory.name


FILES = (
    "analysis.json",
    "search_log.json",
    "manifest.jsonl",
    "claims_staged.jsonl",
    "annotations.json",
)


def load_analysis(directory: Path) -> AnalysisRecord:
    errors: list[str] = []
    parts: dict = {}
    for name in FILES:
        path = directory / name
        if not path.exists():
            errors.append(f"{directory.name}: missing {name}")
            continue
        try:
            parts[name] = (
                _read_jsonl(path)
                if name.endswith(".jsonl")
                else _loads(path.read_text())
            )
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{directory.name}: {name} does not parse: {exc}")
    return AnalysisRecord(
        directory=directory,
        analysis=parts.get("analysis.json") or {},
        search_log=parts.get("search_log.json") or {},
        manifest=parts.get("manifest.jsonl") or [],
        claims=parts.get("claims_staged.jsonl") or [],
        annotations=parts.get("annotations.json") or [],
        load_errors=errors,
    )


def analysis_dirs(root: Path = SOURCES) -> list[Path]:
    return sorted(
        p for p in root.iterdir() if p.is_dir() and p.name.startswith(DIR_PREFIX)
    )


def pin(provenance: dict) -> str:
    """One results file an estimate was read from: repo@commit:sha256."""
    return f"{provenance['repo']}@{provenance['commit']}:{provenance['sha256']}"


def current_pins(analysis: dict) -> list[str]:
    return sorted({pin(e["provenance"]) for e in analysis.get("pe_estimates") or []})


# --- validation --------------------------------------------------------------


def _registered(enum, value) -> bool:
    return value in {m.value for m in enum}


def _string_map(value) -> bool:
    return isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    )


def _nonempty_str(value, minimum: int = 1) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def _string_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _baseline_labels() -> set[str]:
    from .baselines import BASELINES

    return {label for _, label, *_ in BASELINES}


def _repo_file(ref: str) -> bool:
    path_part = ref.split("#")[0].strip()
    if not path_part or path_part in (".", "/"):
        return False
    path = (REPO / path_part).resolve()
    root = REPO.resolve()
    return path.is_file() and root in path.parents


def _check_basis(basis: dict, where: str) -> list[str]:
    """A basis is a GitHub issue or pull request, engine metadata pinned to a
    commit, or a document or diagnostic: a page URL or a file in this
    repository. URLs and issues are checked for shape only; a reviewer opens
    them."""
    kind, ref = basis.get("kind"), basis.get("ref")
    if kind not in BASIS_KINDS:
        return [f"{where}: basis kind {kind!r} not in {BASIS_KINDS}"]
    if not _nonempty_str(ref) or ref.strip() in ("#", ".", "/"):
        return [f"{where}: basis ref is empty or a placeholder"]
    if kind == "issue":
        if not _GITHUB_ISSUE.match(ref):
            return [f"{where}: an issue basis is a GitHub issue or pull URL: {ref!r}"]
        return []
    if kind == "engine_metadata":
        if _GITHUB_PINNED.match(ref) or _repo_file(ref):
            return []
        return [
            (
                f"{where}: engine metadata is a file pinned to a commit "
                f"(github.com/<org>/<repo>/blob/<40-hex>/<path>) or a file in this repo: {ref!r}"
            )
        ]
    if _URL_WITH_PATH.match(ref) or _repo_file(ref):
        return []
    return [
        f"{where}: {kind} basis {ref!r} is neither an https page URL nor a file in this repo"
    ]


def _check_bases(bases, where: str) -> list[str]:
    if not (isinstance(bases, list) and bases):
        return [
            f"{where}: basis must cite at least one source (no fabricated mechanisms)"
        ]
    errors = []
    for b in bases:
        errors.extend(_check_basis(b if isinstance(b, dict) else {}, where))
    return errors


def _check_identity(row: dict, where: str) -> list[str]:
    """The conditions that, with metric, unit, period, time basis and world,
    say what quantity a figure is."""
    errors = []
    conditions = row.get("conditions")
    if not _string_map(conditions):
        return [f"{where}: conditions must map strings to strings"]
    if conditions.get("basis") not in BASES:
        errors.append(f"{where}: conditions.basis must be one of {BASES}")
    if not _SLUG.match(conditions.get("program", "")):
        errors.append(f"{where}: conditions.program must name the programme (a slug)")
    fy = conditions.get("fy")
    if fy is not None:
        match = _FY.match(fy)
        if not match or (int(match.group(1)) + 1) % 100 != int(match.group(2)):
            errors.append(
                f"{where}: conditions.fy {fy!r} is not a financial year like 2027-28"
            )
        else:
            end = int(match.group(1)) + 1
            if row.get("period") != end:
                errors.append(
                    f"{where}: period {row.get('period')!r} is not {fy}'s end year {end}"
                )
            if row.get("time_basis") != TimeBasis.FISCAL_YEAR.value:
                errors.append(f"{where}: a figure for {fy} has time_basis fiscal_year")
    return errors


def _check_estimate(e: dict, where: str, world_keys: set) -> list[str]:
    errors = []
    if not _nonempty_str(e.get("label")):
        errors.append(f"{where}: label is empty")
    if e.get("world") not in world_keys:
        errors.append(f"{where}: world {e.get('world')!r} is not defined")
    if not _registered(Metric, e.get("metric")):
        errors.append(f"{where}: metric {e.get('metric')!r} is not registered")
    if not _registered(UnitConcept, e.get("unit_concept")):
        errors.append(
            f"{where}: unit_concept {e.get('unit_concept')!r} is not registered"
        )
    if not _registered(TimeBasis, e.get("time_basis")):
        errors.append(f"{where}: time_basis {e.get('time_basis')!r} is not registered")
    if type(e.get("period")) is not int:
        errors.append(f"{where}: period must be an integer year")
    errors.extend(_check_identity(e, where))
    errors.extend(check_value(e, where, signed=True))
    prov = e.get("provenance") or {}
    if not (isinstance(prov.get("repo"), str) and _REPO.match(prov["repo"])):
        errors.append(f"{where}: provenance.repo must be <org>/<repo>")
    if not (isinstance(prov.get("commit"), str) and _COMMIT.match(prov["commit"])):
        errors.append(f"{where}: provenance.commit must be a 40-hex commit")
    if not (isinstance(prov.get("sha256"), str) and _SHA256.match(prov["sha256"])):
        errors.append(f"{where}: provenance.sha256 must be the results file's SHA-256")
    for f in ("path", "field", "dataset"):
        if not _nonempty_str(prov.get(f)):
            errors.append(f"{where}: provenance.{f} is empty")
    if not (
        isinstance(prov.get("computed_at"), str)
        and _DATETIME.match(prov["computed_at"])
    ):
        errors.append(f"{where}: provenance.computed_at must be an ISO date or time")
    engine = prov.get("engine")
    if not (_string_map(engine) and engine):
        errors.append(f"{where}: provenance.engine must map package names to versions")
    return errors


def _same_quantity(claim: dict, estimate: dict) -> bool:
    return all(claim.get(f) == estimate.get(f) for f in IDENTITY_FIELDS) and all(
        (claim.get("conditions") or {}).get(f)
        == (estimate.get("conditions") or {}).get(f)
        for f in IDENTITY_CONDITIONS
    )


def _near(claim: dict, estimate: dict) -> bool:
    """An estimate is near a claim when it is for the same period and, where the
    claim names them, the same metric and unit: a claim on a published
    quantity is either compared or set beside it with a stated mismatch."""
    if claim.get("period") != estimate.get("period"):
        return False
    for f in ("metric", "unit_concept"):
        if claim.get(f) is not None and claim.get(f) != estimate.get(f):
            return False
    return True


def validate(
    record: AnalysisRecord,
    producers: dict | None = None,
    policy: dict | None = None,
    today: str | None = None,
) -> list[str]:
    """Every reason this directory is not a complete comparables record."""
    producers = producers or load_producers()
    policy = policy or load_policy()
    today = today or today_utc()
    errors = list(record.load_errors)
    if errors:
        return errors
    name = record.name
    a = record.analysis
    labels = _baseline_labels()

    # analysis.json -----------------------------------------------------------
    if a.get("schema") != ANALYSIS_SCHEMA:
        errors.append(f"{name}: analysis.json schema must be {ANALYSIS_SCHEMA!r}")
    country = a.get("country")
    if country not in producers["countries"]:
        errors.append(f"{name}: country {country!r} has no producer list")
        return errors
    registry = a.get("registry") or {}
    kind, slug = registry.get("kind"), registry.get("slug")
    if kind not in ("app", "post"):
        errors.append(f"{name}: registry.kind must be 'app' or 'post'")
    if not (isinstance(slug, str) and _REGISTRY_SLUG.match(slug)):
        errors.append(f"{name}: registry.slug {slug!r} is not a policyengine.org slug")
    if registry.get("country_id") != country.lower():
        errors.append(f"{name}: registry.country_id must be {country.lower()!r}")
    expected_dir = f"{DIR_PREFIX}{country.lower()}-{slug}"
    if name != expected_dir:
        errors.append(f"{name}: directory must be named {expected_dir!r}")
    if a.get("id") != f"{country.lower()}/{slug}":
        errors.append(f"{name}: id must be {country.lower()}/{slug}")
    if not (isinstance(a.get("url"), str) and a["url"].startswith("https://")):
        errors.append(f"{name}: url must be the analysis's https URL")
    if not _nonempty_str(a.get("title")):
        errors.append(f"{name}: title is empty")
    scope = a.get("scope")
    if scope not in producers["scopes"][country]:
        errors.append(f"{name}: scope {scope!r} not in {producers['scopes'][country]}")
    if not _nonempty_str(a.get("subject"), 10):
        errors.append(f"{name}: subject must say what the analysis estimates")
    terms = a.get("search_terms")
    if not (isinstance(terms, list) and terms and all(_nonempty_str(t) for t in terms)):
        errors.append(f"{name}: search_terms must be a nonempty list of strings")
    owner = a.get("owner") or {}
    if not (
        isinstance(owner.get("author"), str) and _REGISTRY_SLUG.match(owner["author"])
    ):
        errors.append(f"{name}: owner.author must be the app-v2 authors.json key")
    published = a.get("published")
    if published is not None and not (_is_date(published) and published <= today):
        errors.append(
            f"{name}: published must be a real date no later than today, or null"
        )
        published = None
    worlds = a.get("worlds")
    if not isinstance(worlds, dict):
        errors.append(f"{name}: worlds must map a world key to its policy slug")
        worlds = {}
    for wkey, world in worlds.items():
        if wkey == BASELINE_WORLD or not _KEY.match(wkey):
            errors.append(f"{name}: world key {wkey!r} is reserved or malformed")
        if not (isinstance(world, dict) and _SLUG.match(str(world.get("policy", "")))):
            errors.append(f"{name}: world {wkey!r} needs a policy slug")
            continue
        if not _nonempty_str(world.get("description"), 10):
            errors.append(f"{name}: world {wkey!r} needs a description")
        if world.get("baseline") is not None and world["baseline"] not in labels:
            errors.append(
                f"{name}: world {wkey!r} baseline {world['baseline']!r} is not "
                "registered in scorecard_db/baselines.py"
            )
    world_keys = set(worlds) | {BASELINE_WORLD}

    estimates: dict[str, dict] = {}
    for i, e in enumerate(a.get("pe_estimates") or []):
        key = e.get("key")
        if not (isinstance(key, str) and _KEY.match(key)) or key in estimates:
            errors.append(
                f"{name}: pe_estimates[{i}]: key {key!r} missing, malformed or repeated"
            )
            continue
        estimates[key] = e
        errors.extend(_check_estimate(e, f"{name}: estimate {key}", world_keys))
    # A household calculator computes figures for the household a reader
    # describes and publishes no fixed estimate: its producers are still
    # searched (decision d1816's default), but it may pin none.
    calculator = a.get("calculator")
    if calculator is not None and not (
        isinstance(calculator, dict)
        and set(calculator) == {"reason"}
        and _nonempty_str(calculator.get("reason"), 20)
    ):
        errors.append(
            f'{name}: calculator must be {{"reason": "<what the page computes>"}}'
        )
    if not estimates and calculator is None:
        errors.append(
            f"{name}: pe_estimates is empty; pin every figure the analysis publishes, "
            "or declare a household calculator that publishes none (`calculator`)"
        )
    superseded_pins = set()
    for i, e in enumerate(a.get("superseded_estimates") or []):
        where = f"{name}: superseded_estimates[{i}]"
        if e.get("key") not in estimates:
            errors.append(f"{where}: key {e.get('key')!r} is not a current estimate's")
        if not (_is_date(e.get("superseded_on")) and e["superseded_on"] <= today):
            errors.append(
                f"{where}: superseded_on must be a real date no later than today"
            )
        errors.extend(_check_estimate(e, where, world_keys))
        if not any(err.startswith(where) and "provenance" in err for err in errors):
            superseded_pins.add(pin(e["provenance"]))
    pins_now = (
        set(current_pins(a))
        if not any("provenance" in err for err in errors)
        else set()
    )

    # manifest ----------------------------------------------------------------
    manifest: dict[str, dict] = {}
    for i, m in enumerate(record.manifest):
        where = f"{name}: manifest.jsonl line {i + 1}"
        if not (isinstance(m.get("sha256"), str) and _SHA256.match(m["sha256"])):
            errors.append(f"{where}: sha256 must be 64 hex")
            continue
        if not (isinstance(m.get("url"), str) and _URL.match(m["url"])):
            errors.append(f"{where}: url is not a URL")
        for f in ("title", "publisher", "retrieved", "access"):
            if not _nonempty_str(m.get(f)):
                errors.append(f"{where}: {f} is empty")
        if m["sha256"] in manifest:
            errors.append(f"{where}: sha256 repeated")
        manifest[m["sha256"]] = m

    # search_log ----------------------------------------------------------------
    log = record.search_log
    if log.get("schema") != SEARCH_SCHEMA:
        errors.append(f"{name}: search_log.json schema must be {SEARCH_SCHEMA!r}")
    searches = log.get("searches") or []
    if not searches:
        errors.append(f"{name}: search_log has no searches")
    claim_found: dict[str, tuple[str, str, str]] = {}  # key -> (date, kind, producer)
    earliest = first_list_date(producers, country)
    first_date = None
    previous_date = ""
    for i, s in enumerate(searches):
        where = f"{name}: search {i + 1}"
        date, skind = s.get("date"), s.get("kind")
        if not _is_date(date):
            errors.append(f"{where}: date must be a real YYYY-MM-DD date")
            continue
        if date > today:
            errors.append(f"{where}: dated {date}, after today ({today})")
        if date < earliest:
            errors.append(
                f"{where}: dated {date}, before the {country} producer list ({earliest})"
            )
        if date < previous_date:
            errors.append(f"{where}: searches must be in date order")
        previous_date = date
        if skind not in SEARCH_KINDS:
            errors.append(f"{where}: kind {skind!r} not in {SEARCH_KINDS}")
        if i == 0:
            first_date = date
            if skind not in FIRST_KINDS:
                errors.append(
                    f"{where}: the first search is a prepublish or backfill search"
                )
        elif skind in FIRST_KINDS:
            errors.append(f"{where}: only the first search is {skind}")
        if skind == "prepublish" and published is not None and date > published:
            errors.append(
                f"{where}: a prepublish search is dated on or before publication ({published})"
            )
        if skind == "backfill":
            if published is None:
                errors.append(
                    f"{where}: a backfill search needs analysis.json published"
                )
            elif date < published:
                errors.append(
                    f"{where}: a backfill search is dated after publication ({published})"
                )
        if skind in LATER_KINDS:
            if published is None:
                errors.append(
                    f"{where}: a {skind} search needs analysis.json published"
                )
            elif date <= published:
                errors.append(
                    f"{where}: a {skind} search is dated after publication ({published})"
                )
            if first_date is not None and date <= first_date:
                errors.append(
                    f"{where}: a {skind} search is dated after the first search ({first_date})"
                )
        if not _nonempty_str(s.get("by")):
            errors.append(f"{where}: by must name the session or job that ran it")
        pins = s.get("results_pins")
        no_results = calculator is not None and not estimates
        if no_results and pins != []:
            errors.append(
                f"{where}: a calculator with no estimates compares no results file "
                "(results_pins: [])"
            )
        elif not no_results and not (
            _string_list(pins) and pins and all(_PIN.match(p) for p in pins)
        ):
            errors.append(
                f"{where}: results_pins must list the results files compared "
                "(repo@commit:sha256; `comparables pins` prints them)"
            )
        elif pins_now and not set(pins) <= pins_now | superseded_pins:
            errors.append(
                f"{where}: results_pins name a results file no estimate is read from"
            )
        entries = s.get("producers")
        if not isinstance(entries, list):
            errors.append(f"{where}: producers must be a list")
            entries = []
        logged = [p.get("producer") for p in entries if isinstance(p, dict)]
        required = required_producers(producers, country, date)
        required_slugs = [p["slug"] for p in required]
        missing = [p for p in required_slugs if p not in logged]
        unknown = [p for p in logged if p not in required_slugs]
        if missing:
            errors.append(f"{where}: producers not searched: {missing}")
        if unknown:
            errors.append(
                f"{where}: producers not on the {country} list on {date}: {unknown}"
            )
        if len(logged) != len(set(logged)):
            errors.append(f"{where}: a producer is logged twice")
        by_slug = {p["slug"]: p for p in required}
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"{where}: each producer entry is an object")
                continue
            slug_ = entry.get("producer")
            pwhere = f"{where} {slug_}"
            result = entry.get("result")
            claims = entry.get("claims", [])
            queries = entry.get("queries", [])
            checked = entry.get("checked", [])
            if not (
                _string_list(claims) and _string_list(queries) and _string_list(checked)
            ):
                errors.append(
                    f"{pwhere}: claims, queries and checked are lists of strings"
                )
                continue
            if result not in RESULTS:
                errors.append(f"{pwhere}: result {result!r} not in {RESULTS}")
                continue
            if not all(_nonempty_str(q) for q in queries):
                errors.append(f"{pwhere}: queries must be nonempty strings")
            if not all(_URL.match(u) for u in checked):
                errors.append(f"{pwhere}: checked must be URLs")
            producer = by_slug.get(slug_)
            if result == "not_applicable":
                if producer is not None and applies(producer, scope):
                    errors.append(
                        f"{pwhere}: not_applicable, but this producer applies to "
                        f"{scope!r} analyses; search it"
                    )
                if claims:
                    errors.append(f"{pwhere}: not_applicable with claims")
                continue
            if not (queries or checked):
                errors.append(
                    f"{pwhere}: {result} with no query run and no page checked"
                )
            if result == "none_found" and claims:
                errors.append(f"{pwhere}: none_found with claims")
            if result == "found_not_staged":
                if claims:
                    errors.append(f"{pwhere}: found_not_staged with claims")
                if not checked:
                    errors.append(
                        f"{pwhere}: found_not_staged lists the pages it was seen on"
                    )
                if not _nonempty_str(entry.get("note"), 20):
                    errors.append(
                        f"{pwhere}: found_not_staged says what was found and why it is not staged"
                    )
            if result == "found" and not claims:
                errors.append(f"{pwhere}: found with no claims")
            for key in claims:
                if key in claim_found:
                    errors.append(
                        f"{pwhere}: claim {key} already found by an earlier search"
                    )
                claim_found[key] = (date, skind, slug_)
    if searches and pins_now:
        latest = searches[-1].get("results_pins")
        if _string_list(latest) and set(latest) != pins_now:
            errors.append(
                f"{name}: the latest search compared {sorted(latest)}, but the estimates "
                f"are now read from {sorted(pins_now)}; a new results file needs a new search"
            )

    # claims ----------------------------------------------------------------------
    claims_by_key: dict[str, dict] = {}
    must_annotate: list[str] = []
    compared_keys: list[str] = []
    used_primaries: set[str] = set()
    range_groups: dict[str, list[dict]] = defaultdict(list)
    for i, c in enumerate(record.claims):
        key = c.get("key")
        where = f"{name}: claim {key or i + 1}"
        if not (isinstance(key, str) and _KEY.match(key)) or key in claims_by_key:
            errors.append(f"{where}: key missing, malformed or repeated")
            continue
        claims_by_key[key] = c
        found = claim_found.get(key)
        if found is None:
            errors.append(f"{where}: no search entry lists this claim")
        else:
            if c.get("found_on") != found[0]:
                errors.append(
                    f"{where}: found_on must be {found[0]}, the search that found it"
                )
            if c.get("found_by") != found[2]:
                errors.append(
                    f"{where}: found_by must be {found[2]}, the producer logged"
                )
        source = c.get("source")
        found_by = c.get("found_by")
        if not (isinstance(source, str) and _SLUG.match(source)):
            errors.append(f"{where}: source must be a producer slug")
        elif source in BANNED_SOURCES:
            errors.append(
                f"{where}: source names the producer that published the figure "
                f"(not {source!r})"
            )
        else:
            belongs = producer_for_source(producers, country, source)
            if belongs is not None and belongs != found_by:
                errors.append(
                    f"{where}: {source!r} is on the list as {belongs}; its claims are "
                    f"logged under {belongs}'s own entry, not {found_by}"
                )
            if belongs is None and found_by not in OPEN_FINDERS:
                errors.append(
                    f"{where}: {source!r} is not on the {country} list; log it under "
                    "open_search or academic"
                )
        metric = c.get("metric")
        if metric is None:
            if not _nonempty_str(c.get("proposed_metric")):
                errors.append(f"{where}: metric null needs proposed_metric")
        elif not _registered(Metric, metric):
            errors.append(
                f"{where}: metric {metric!r} is not registered; use proposed_metric"
            )
        unit = c.get("unit_concept")
        if unit is None:
            if not _nonempty_str(c.get("proposed_unit")):
                errors.append(f"{where}: unit_concept null needs proposed_unit")
        elif not _registered(UnitConcept, unit):
            errors.append(
                f"{where}: unit_concept {unit!r} is not registered; use proposed_unit"
            )
        value_kind = c.get("value_kind")
        if value_kind not in VALUE_KINDS:
            errors.append(f"{where}: value_kind {value_kind!r} not in {VALUE_KINDS}")
        errors.extend(check_value(c, where))
        if value_kind == "approx_chart_reading":
            if not _nonempty_str(c.get("note"), 10):
                errors.append(f"{where}: a chart reading says how it was read in note")
        elif not quote_contains(c.get("quote", ""), c.get("value_raw", "")):
            errors.append(
                f"{where}: quote does not print the value {c.get('value_raw')!r} "
                "(as a whole number, sign included)"
            )
        if type(c.get("period")) is not int:
            errors.append(f"{where}: period must be an integer year (FY end year)")
        if not _registered(TimeBasis, c.get("time_basis")):
            errors.append(
                f"{where}: time_basis {c.get('time_basis')!r} is not registered"
            )
        errors.extend(_check_identity(c, where))
        world = c.get("world")
        if world not in world_keys:
            errors.append(f"{where}: world {world!r} is not defined in analysis.json")
        if world != BASELINE_WORLD and not _nonempty_str(c.get("reform_hint")):
            errors.append(
                f"{where}: reform_hint must quote the producer's own words for the world"
            )
        if c.get("attribution") not in ATTRIBUTIONS:
            errors.append(
                f"{where}: attribution {c.get('attribution')!r} not in {ATTRIBUTIONS}"
            )
        bclass = c.get("benchmark_class")
        if bclass not in BENCHMARK_CLASSES:
            errors.append(
                f"{where}: benchmark_class {bclass!r} not in {BENCHMARK_CLASSES}"
            )
        if (c.get("attribution") == "same_assumptions") != (
            bclass == "same_assumptions"
        ):
            errors.append(
                f"{where}: same_assumptions attribution and benchmark_class go together"
            )
        if bclass == "administrative_fact" and world == BASELINE_WORLD:
            errors.append(
                f"{where}: an administrative level is calibration material; stage it "
                "under a producer-level source, where relationships.py assigns it"
            )
        baseline = c.get("baseline_policy")
        if baseline is not None and baseline not in labels:
            errors.append(
                f"{where}: baseline_policy {baseline!r} is not registered in "
                "scorecard_db/baselines.py (harvest rule 7: register it first)"
            )
        if "proposed_baseline" in c:
            errors.append(
                f"{where}: register the baseline before staging (harvest rule 7)"
            )
        pub = c.get("publication") or {}
        for f in ("title", "url", "publisher", "locator", "access"):
            if not _nonempty_str(pub.get(f)):
                errors.append(f"{where}: publication.{f} is empty")
        if not _is_date(pub.get("date")):
            errors.append(f"{where}: publication.date must be a real YYYY-MM-DD date")
        elif _is_date(c.get("found_on")) and pub["date"] > c["found_on"]:
            errors.append(
                f"{where}: published {pub['date']}, after it was found ({c['found_on']})"
            )
        sha = pub.get("primary_sha256")
        if sha not in manifest:
            errors.append(
                f"{where}: publication.primary_sha256 is not in manifest.jsonl"
            )
        else:
            used_primaries.add(sha)
            if manifest[sha].get("url") != pub.get("url"):
                errors.append(
                    f"{where}: publication.url differs from its manifest line"
                )
        for f in ("source_table", "source_column", "quote"):
            if not _nonempty_str(c.get(f)):
                errors.append(f"{where}: {f} is empty")
        if c.get("parse_confidence") not in PARSE_CONFIDENCE:
            errors.append(f"{where}: parse_confidence not in {PARSE_CONFIDENCE}")
        if c.get("status") != "ok":
            errors.append(f"{where}: status must be 'ok'")
        if value_kind in RANGE_KINDS:
            group = (c.get("conditions") or {}).get("range_group")
            if not (isinstance(group, str) and _SLUG.match(group)):
                errors.append(
                    f"{where}: a range bound names its range_group in conditions"
                )
            else:
                range_groups[group].append(c)
        compare = c.get("compare_to")
        nearest = c.get("nearest_estimate")
        if compare is None:
            if not _nonempty_str(c.get("pe_missing"), 10):
                errors.append(f"{where}: not compared, so pe_missing must say why")
            near = sorted(k for k, e in estimates.items() if _near(c, e))
            if near and nearest not in near:
                errors.append(
                    f"{where}: estimates {', '.join(near)} are for the same period"
                    + (" and metric" if metric else "")
                    + "; compare it (compare_to), or name the nearest in "
                    "nearest_estimate and annotate why they differ"
                )
            elif not near and nearest is not None:
                errors.append(
                    f"{where}: nearest_estimate {nearest!r} is not near this claim"
                )
            elif near:
                must_annotate.append(key)
                est = estimates[nearest]
                if (
                    _same_quantity(c, est)
                    and c.get("attribution") == "own"
                    and value_kind not in ("cumulative",)
                    and baseline == worlds.get(est.get("world"), {}).get("baseline")
                ):
                    errors.append(
                        f"{where}: it is the same quantity as {nearest} (metric, unit, "
                        "period, time basis, world, basis and programme); compare it"
                    )
            continue
        if nearest is not None:
            errors.append(f"{where}: a compared claim has no nearest_estimate")
        if c.get("pe_missing") is not None:
            errors.append(f"{where}: compared, so pe_missing must be absent")
        if not isinstance(compare, dict):
            errors.append(f"{where}: compare_to must be an object naming pe_estimate")
            continue
        est = estimates.get(compare.get("pe_estimate"))
        if est is None:
            errors.append(f"{where}: compare_to names no PolicyEngine estimate")
            continue
        compared_keys.append(key)
        if c.get("attribution") != "own":
            errors.append(
                f"{where}: only a producer's own estimate is compared ({c.get('attribution')})"
            )
        if value_kind == "cumulative":
            errors.append(
                f"{where}: a cumulative figure is not compared with a single-year estimate"
            )
        if c.get("world") != est.get("world"):
            across = compare.get("across_worlds")
            if not isinstance(across, dict):
                errors.append(
                    f"{where}: world {c.get('world')!r} differs from {est['key']}'s "
                    f"{est.get('world')!r}; compare across worlds only with "
                    "compare_to.across_worlds giving the reason and its basis"
                )
            else:
                if not _nonempty_str(across.get("reason"), 20):
                    errors.append(
                        f"{where}: across_worlds.reason must say why the quantities match"
                    )
                errors.extend(_check_bases(across.get("basis"), where))
        for f in ("metric", "unit_concept", "period", "time_basis"):
            if c.get(f) != est.get(f):
                errors.append(
                    f"{where}: {f} {c.get(f)!r} differs from {est['key']}'s {est.get(f)!r}; "
                    "a different quantity is not compared"
                )
        for f in IDENTITY_CONDITIONS:
            mine = (c.get("conditions") or {}).get(f)
            theirs = (est.get("conditions") or {}).get(f)
            if mine != theirs:
                errors.append(
                    f"{where}: {f} {mine!r} differs from {est['key']}'s {theirs!r}; "
                    "a different quantity is not compared"
                )
        executed = worlds.get(est.get("world"), {}).get("baseline")
        if baseline != executed:
            errors.append(
                f"{where}: scored against baseline {baseline or 'current law'}, but "
                f"{est['key']} against {executed or 'current law'}"
            )
        relation, why = orientation(c, country)
        if relation not in (signs.SAME, signs.OPPOSITE) and metric in signs.ORIENTATION:
            errors.append(
                f"{where}: the sign convention does not orient the value ({why}); "
                "state what a positive value means in conditions.sign_convention, "
                "in words signs.py reads"
            )
        elif relation == signs.UNKNOWN:
            errors.append(f"{where}: the value cannot be oriented ({why})")

    for key in claim_found:
        if key not in claims_by_key:
            errors.append(f"{name}: search lists claim {key}, which is not staged")
    for sha, m in manifest.items():
        if sha not in used_primaries:
            errors.append(
                f"{name}: manifest line for {m.get('url')} is cited by no claim"
            )
    for group, members in range_groups.items():
        kinds = sorted(m.get("value_kind") for m in members)
        if kinds != ["range_high", "range_low"]:
            errors.append(
                f"{name}: range_group {group} needs exactly one range_low and one range_high"
            )
            continue
        low, high = members
        shared = (
            "source",
            "metric",
            "unit_concept",
            "period",
            "time_basis",
            "world",
            "compare_to",
        )
        if any(low.get(f) != high.get(f) for f in shared) or any(
            (low.get("conditions") or {}).get(f)
            != (high.get("conditions") or {}).get(f)
            for f in IDENTITY_CONDITIONS
        ):
            errors.append(
                f"{name}: range_group {group}'s bounds measure different things"
            )

    # annotations -------------------------------------------------------------------
    annotated: dict[str, dict] = {}
    ids = set()
    for i, n in enumerate(record.annotations):
        nid = n.get("id")
        where = f"{name}: annotation {nid or i + 1}"
        if not (isinstance(nid, str) and _SLUG.match(nid)) or nid in ids:
            errors.append(f"{where}: id missing, malformed or repeated")
            continue
        ids.add(nid)
        status = n.get("status")
        if status not in ANNOTATION_STATUSES:
            errors.append(f"{where}: status {status!r} not in {ANNOTATION_STATUSES}")
        if not _nonempty_str(n.get("cause"), 20):
            errors.append(f"{where}: cause must state the cause (20+ characters)")
        errors.extend(_check_bases(n.get("basis"), where))
        if not isinstance(n.get("explains_gap"), bool):
            errors.append(f"{where}: explains_gap must be true or false")
        if status == "pending":
            if n.get("explains_gap"):
                errors.append(
                    f"{where}: a pending annotation does not explain the gap yet"
                )
            if not (
                isinstance(n.get("tracking_issue"), str)
                and _GITHUB_ISSUE.match(n["tracking_issue"])
            ):
                errors.append(
                    f"{where}: pending needs the tracking_issue opened for the owner"
                )
        keys = n.get("claims")
        if not (isinstance(keys, list) and keys):
            errors.append(f"{where}: claims must list the claim keys it covers")
            continue
        for key in keys:
            if key not in claims_by_key:
                errors.append(f"{where}: claim {key} is not staged")
                continue
            if key in annotated:
                errors.append(
                    f"{where}: claim {key} already has a status from {annotated[key]['id']}"
                )
                continue
            annotated[key] = n
            c = claims_by_key[key]
            if key in compared_keys:
                if status not in COMPARED_STATUSES:
                    errors.append(
                        f"{where}: {key} is compared, so its status is one of "
                        f"{COMPARED_STATUSES}; a concept mismatch is not compared"
                    )
                est = estimates[c["compare_to"]["pe_estimate"]]
                if status == ComparisonStatus.COMPARABLE.value and c.get(
                    "world"
                ) != est.get("world"):
                    errors.append(
                        f"{where}: {key} is compared across worlds, so it is constructed, "
                        "not comparable"
                    )
            elif status not in MISMATCH_STATUSES:
                errors.append(
                    f"{where}: {key} is not compared, so its status is one of {MISMATCH_STATUSES}"
                )
            if (
                status == "pending"
                and claim_found.get(key, ("", ""))[1] not in POST_PUBLICATION_KINDS
            ):
                errors.append(
                    f"{where}: {key} was found before publication; its gap is "
                    "explained before the analysis is listed, not left pending"
                )

    for key in must_annotate:
        if key not in annotated:
            errors.append(
                f"{name}: claim {key} sits beside its nearest estimate uncompared, so an "
                f"annotation with status {' or '.join(MISMATCH_STATUSES)} must say why"
            )

    # the gate ------------------------------------------------------------------------
    if errors:
        return errors
    for row in evaluate(record, policy):
        if not row["over"]:
            continue
        note = annotated.get(row["key"])
        gap = row["group_gap"] if row["range_group"] else row["gap"]
        shown = "unbounded" if gap is None or math.isinf(gap) else f"{gap:+.1%}"
        if note is None:
            errors.append(
                f"{name}: claim {row['key']} is {shown} from {row['estimate']}"
                f"{' (its sign disagrees)' if row['sign_disagrees'] else ''} "
                f"(threshold {policy['gap_threshold']:.0%}) and no annotation explains it"
            )
        elif note["status"] != "pending" and not note.get("explains_gap"):
            errors.append(
                f"{name}: claim {row['key']} is over the threshold; its annotation "
                f"{note['id']} must explain the gap (explains_gap: true)"
            )
    return errors


def evaluate(record: AnalysisRecord, policy: dict | None = None) -> list[dict]:
    """One row per staged claim: the comparison and its gap, or its nearest
    estimate and that gap for information. Assumes a valid record."""
    policy = policy or load_policy()
    threshold = policy["gap_threshold"]
    country = record.analysis["country"]
    estimates = {e["key"]: e for e in record.analysis["pe_estimates"]}
    annotated = {}
    for n in record.annotations:
        for key in n["claims"]:
            annotated[key] = n
    rows = []
    for c in record.claims:
        note = annotated.get(c["key"])
        row = {
            "key": c["key"],
            "source": c["source"],
            "found_on": c["found_on"],
            "estimate": None,
            "nearest": c.get("nearest_estimate"),
            "relation": None,
            "gap": None,
            "nearest_gap": None,
            "over": False,
            "sign_disagrees": False,
            "range_group": (c.get("conditions") or {}).get("range_group")
            if c.get("value_kind") in RANGE_KINDS
            else None,
            "group_gap": None,
            "status": note["status"] if note else None,
            "annotation": note["id"] if note else None,
            "explains_gap": bool(note and note.get("explains_gap")),
            "tracking_issue": (note or {}).get("tracking_issue"),
        }
        relation, _ = orientation(c, country)
        compare = c.get("compare_to")
        if compare:
            est = estimates[compare["pe_estimate"]]
            gap = relative_gap(est["value"], c["value"], relation)
            disagrees = sign_disagrees(est["value"], oriented(c["value"], relation))
            # a comparison across two policy worlds is a documented
            # construction, never plainly comparable
            default = (
                ComparisonStatus.CONSTRUCTED.value
                if c["world"] != est["world"]
                else ComparisonStatus.COMPARABLE.value
            )
            row.update(
                estimate=est["key"],
                relation=relation,
                gap=gap,
                sign_disagrees=disagrees,
                over=over_threshold(gap, threshold) or disagrees,
                status=row["status"] or default,
            )
        elif row["nearest"] and c.get("metric") is not None:
            row["relation"] = relation
            row["nearest_gap"] = relative_gap(
                estimates[row["nearest"]]["value"], c["value"], relation
            )
        rows.append(row)

    # A range is over only when the estimate lies outside it by more than the
    # threshold from the nearer bound, or on the other side of zero.
    by_group: dict[str, list[dict]] = defaultdict(list)
    for row, c in zip(rows, record.claims):
        if row["range_group"] and row["estimate"]:
            by_group[row["range_group"]].append((row, c))
    for members in by_group.values():
        if len(members) != 2:
            continue
        pe = estimates[members[0][0]["estimate"]]["value"]
        bounds = [oriented(c["value"], r["relation"]) for r, c in members]
        if None in bounds:
            continue
        lo, hi = min(bounds), max(bounds)
        if lo <= pe <= hi:
            group_gap, over = 0.0, False
        else:
            nearer = lo if pe < lo else hi
            group_gap = (pe / nearer - 1.0) if nearer != 0 else math.inf
            over = over_threshold(group_gap, threshold) or sign_disagrees(pe, nearer)
        for r, _ in members:
            r["group_gap"] = group_gap
            r["over"] = over
    return rows


# --- the index ------------------------------------------------------------------


def _search_summary(search: dict) -> dict:
    by_result: dict[str, list[str]] = {r: [] for r in RESULTS}
    for p in search["producers"]:
        by_result[p["result"]].append(p["producer"])
    searched = sorted(
        p["producer"] for p in search["producers"] if p["result"] != "not_applicable"
    )
    return {
        "date": search["date"],
        "kind": search["kind"],
        "results_pins": sorted(search["results_pins"]),
        "producers_searched": searched,
        "producers_with_finds": sorted(by_result["found"]),
        "found_not_staged": sorted(by_result["found_not_staged"]),
        "not_applicable": sorted(by_result["not_applicable"]),
        "found": sum(len(p.get("claims") or []) for p in search["producers"]),
    }


def _round(x: float | None) -> float | None:
    if x is None or math.isinf(x):
        return None
    return round(x, 4)


def index_entry(record: AnalysisRecord, policy: dict) -> dict:
    a = record.analysis
    rows = evaluate(record, policy)
    compared = [r for r in rows if r["estimate"]]
    gaps = [abs(r["gap"]) for r in compared if r["gap"] is not None]
    over = [r for r in compared if r["over"]]
    return {
        "id": a["id"],
        "kind": a["registry"]["kind"],
        "country_id": a["registry"]["country_id"],
        "slug": a["registry"]["slug"],
        "title": a["title"],
        "url": a["url"],
        "owner": a["owner"]["author"],
        "published": a.get("published"),
        "current_pins": current_pins(a),
        "searches": [_search_summary(s) for s in record.search_log["searches"]],
        "claims": len(rows),
        "compared": len(compared),
        "beside_nearest": sum(1 for r in rows if r["nearest"]),
        "over_threshold": len(over),
        "sign_disagreements": sum(1 for r in compared if r["sign_disagrees"]),
        "explained": sum(1 for r in over if r["explains_gap"]),
        "pending": sum(1 for r in rows if r["status"] == "pending"),
        "unbounded_gaps": sum(1 for g in gaps if math.isinf(g)),
        "max_abs_gap": _round(
            max((g for g in gaps if not math.isinf(g)), default=None)
        ),
        "tracking_issues": sorted(
            {r["tracking_issue"] for r in rows if r["tracking_issue"]}
        ),
        "search_log": f"{REPO_URL}/blob/main/sources/{record.name}/search_log.json",
        "comparisons": _comparisons(record, rows),
    }


def _comparisons(record: AnalysisRecord, rows: list[dict]) -> list[dict]:
    """Every staged estimate as a reader would see it: the producer's figure
    as printed, ours where one compares (or the nearest one), the gap and
    why. The data a "How we compare" section on the analysis's page reads."""
    claims = {c["key"]: c for c in record.claims}
    estimates = {e["key"]: e for e in record.analysis["pe_estimates"]}
    causes = {n["id"]: n["cause"] for n in record.annotations}
    out = []
    for row in rows:
        c = claims[row["key"]]
        est = estimates.get(row["estimate"]) if row["estimate"] else None
        conditions = c.get("conditions") or {}
        out.append(
            {
                "claim": c["key"],
                "found_on": c["found_on"],
                "source": c["source"],
                "publisher": c["publication"]["publisher"],
                "title": c["publication"]["title"],
                "url": c["publication"]["url"],
                "locator": c["publication"]["locator"],
                "metric": c.get("metric") or c.get("proposed_metric"),
                "basis": conditions.get("basis"),
                "program": conditions.get("program"),
                "period": c["period"],
                "fy": conditions.get("fy"),
                "value_kind": c["value_kind"],
                "range_group": row["range_group"],
                "value": c["value"],
                "value_raw": c["value_raw"],
                "sign_convention": conditions.get("sign_convention"),
                "estimate": row["estimate"],
                "estimate_label": est["label"] if est else None,
                "pe_value": est["value"] if est else None,
                "gap": _round(row["gap"]),
                "gap_unbounded": row["gap"] is not None and math.isinf(row["gap"]),
                "group_gap": _round(row["group_gap"]),
                "sign_disagrees": row["sign_disagrees"],
                "over_threshold": row["over"],
                "nearest_estimate": row["nearest"],
                "nearest_pe_value": estimates[row["nearest"]]["value"]
                if row["nearest"]
                else None,
                "nearest_gap": _round(row["nearest_gap"]),
                "status": row["status"],
                "cause": causes.get(row["annotation"]),
                "pe_missing": c.get("pe_missing"),
            }
        )
    return out


def build_index(
    root: Path = SOURCES, producers: dict | None = None, policy: dict | None = None
) -> dict:
    """The published index. Raises if any analysis directory is incomplete:
    the index lists only complete records, so a listing is the proof."""
    producers = producers or load_producers()
    policy = policy or load_policy()
    analyses = {}
    problems = []
    for directory in analysis_dirs(root):
        record = load_analysis(directory)
        errors = validate(record, producers, policy)
        if errors:
            problems.extend(errors)
            continue
        analyses[directory.name] = index_entry(record, policy)
    if problems:
        raise ValueError("incomplete comparables records:\n  " + "\n  ".join(problems))
    return {
        "_what": (
            "Every PolicyEngine analysis whose comparables search is recorded in "
            "this repository, keyed by its sources/ directory. Generated by "
            "`python -m scorecard_db.comparables index` from the directories "
            "themselves; policyengine-app-v2 and PolicyEngine/newsletters read it "
            "to check an entry's comparables. A listing means the record passed "
            "the gate."
        ),
        "schema": INDEX_SCHEMA,
        "gap_threshold": policy["gap_threshold"],
        "promotion_window_days": policy["promotion_window_days"],
        # The rules for which policyengine.org entries need a record, so the
        # sites that check entries against this index can check they apply
        # the same ones (research_entries, may_declare_no_estimate).
        "entry_rules": {
            "analysis_tags": sorted(ANALYSIS_TAGS),
            "no_estimate_tags": sorted(NO_ESTIMATE_TAGS),
            "country_tags": list(COUNTRY_TAGS),
            "default_country": DEFAULT_COUNTRY,
            "search_kinds": list(SEARCH_KINDS),
        },
        "analyses": analyses,
    }


def render_index(index: dict) -> str:
    # NaN and infinity are not JSON; another repository's JSON.parse would throw
    return json.dumps(index, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


# --- the app-v2 record ------------------------------------------------------------


def app_record(record: AnalysisRecord, search_date: str | None = None) -> dict:
    """The ``comparables`` block for the analysis's apps.json / posts.json entry."""
    searches = [s for s in record.search_log["searches"] if s["kind"] in FIRST_KINDS]
    if search_date:
        searches = [s for s in searches if s["date"] == search_date]
    if not searches:
        raise ValueError(
            f"{record.name}: no prepublish or backfill search on {search_date}"
        )
    summary = _search_summary(searches[-1])
    return {
        "status": "reviewed",
        "scorecardSource": record.name,
        "searchDate": summary["date"],
        "searchKind": summary["kind"],
        "producersSearched": summary["producers_searched"],
        "found": summary["found"],
        "searchLog": f"{REPO_URL}/blob/main/sources/{record.name}/search_log.json",
    }


# --- scaffolding -----------------------------------------------------------------


def scaffold(
    country: str, kind: str, slug: str, today: str, root: Path = SOURCES
) -> Path:
    """A skeleton directory for a new search, with every producer to log."""
    producers = load_producers()
    country = country.upper()
    if country not in producers["countries"]:
        raise SystemExit(
            f"no producer list for {country}; add one to data/comparables/producers.json first"
        )
    directory = root / f"{DIR_PREFIX}{country.lower()}-{slug}"
    if directory.exists():
        raise SystemExit(
            f"{directory} exists; add a search to its search_log.json instead"
        )
    directory.mkdir(parents=True)
    analysis = {
        "schema": ANALYSIS_SCHEMA,
        "id": f"{country.lower()}/{slug}",
        "country": country,
        "registry": {"kind": kind, "slug": slug, "country_id": country.lower()},
        "title": "",
        "url": f"https://policyengine.org/{country.lower()}/{'research/' if kind == 'post' else ''}{slug}",
        "published": None,
        "owner": {"author": ""},
        "scope": "",
        "subject": "",
        "search_terms": [],
        "worlds": {},
        "pe_estimates": [],
    }
    log = {
        "schema": SEARCH_SCHEMA,
        "searches": [
            {
                "date": today,
                "kind": "prepublish",
                "by": "",
                "results_pins": [],
                "producers": [
                    {
                        "producer": p["slug"],
                        "result": "",
                        "queries": [],
                        "checked": [],
                        "claims": [],
                        "note": "",
                    }
                    for p in required_producers(producers, country, today)
                ],
            }
        ],
    }
    (directory / "analysis.json").write_text(
        json.dumps(analysis, indent=1, ensure_ascii=False) + "\n"
    )
    (directory / "search_log.json").write_text(
        json.dumps(log, indent=1, ensure_ascii=False) + "\n"
    )
    (directory / "manifest.jsonl").write_text("")
    (directory / "claims_staged.jsonl").write_text("")
    (directory / "annotations.json").write_text("[]\n")
    return directory


# --- registry entries and re-harvest support ---------------------------------------


def post_slug(filename: str) -> str:
    """The website's post slug (website/src/data/posts/postTransformers.ts):
    the file name up to its first dot, lowercased, underscores to hyphens."""
    stem = filename[: filename.index(".")] if "." in filename else filename
    return stem.lower().replace("_", "-")


def may_declare_no_estimate(kind: str, tags: list[str]) -> bool:
    """Only a post that is plainly not an analysis (an event, an announcement)
    may say it publishes no estimate; an app never may."""
    tags = set(tags)
    return kind == "post" and bool(tags & NO_ESTIMATE_TAGS) and not tags & ANALYSIS_TAGS


def research_entries(apps: list[dict], posts: list[dict]) -> list[dict]:
    """policyengine.org entries the comparables rules cover: apps listed with
    research or tagged policy, and every post. A post is one entry whatever its
    country tags; the website serves it under every country."""
    out = []
    for app in apps:
        if not app.get("slug") or not app.get("countryId"):
            continue
        tags = app.get("tags", [])
        if not (app.get("displayWithResearch") or "policy" in tags):
            continue
        out.append(
            {
                "kind": "app",
                "country_ids": [app["countryId"]],
                "slug": app["slug"],
                "date": (app.get("date") or "")[:10] or None,
                "title": app.get("title", ""),
                "authors": app.get("authors", []),
                "tags": tags,
                "comparables": app.get("comparables"),
            }
        )
    for post in posts:
        tags = post.get("tags", [])
        countries = [t for t in tags if t in COUNTRY_TAGS] or [DEFAULT_COUNTRY]
        out.append(
            {
                "kind": "post",
                "country_ids": countries,
                "slug": post_slug(post["filename"]),
                "date": (post.get("date") or "")[:10] or None,
                "title": post.get("title", ""),
                "authors": post.get("authors", []),
                "tags": tags,
                "comparables": post.get("comparables"),
            }
        )
    return out


def publishes_estimate(entry: dict) -> bool:
    record = entry.get("comparables") or {}
    if record.get("status") == "no_estimate" and may_declare_no_estimate(
        entry["kind"], entry["tags"]
    ):
        return False
    return record.get("status") == "reviewed" or bool(
        set(entry["tags"]) & ANALYSIS_TAGS
    )


def due(
    apps: list[dict],
    posts: list[dict],
    today: str,
    window_days: int,
    root: Path = SOURCES,
) -> list[dict]:
    """Research entries published within the re-harvest window that publish an
    estimate, with the directory that holds (or will hold) their record."""
    start = (dt.date.fromisoformat(today) - dt.timedelta(days=window_days)).isoformat()
    rows = []
    sources: dict[str, str] = {}
    for e in research_entries(apps, posts):
        if (
            not e["date"]
            or not (start <= e["date"] <= today)
            or not publishes_estimate(e)
        ):
            continue
        record = e.get("comparables") or {}
        candidates = [f"{DIR_PREFIX}{c}-{e['slug']}" for c in e["country_ids"]]
        name = (
            record.get("scorecardSource")
            if record.get("status") == "reviewed"
            else None
        )
        name = name or next(
            (n for n in candidates if (root / n).is_dir()), candidates[0]
        )
        label = f"{e['kind']} {e['slug']}"
        if name in sources and sources[name] != label:
            raise ValueError(
                f"{sources[name]} and {label} would share the record {name}"
            )
        sources[name] = label
        rows.append(
            {
                **{k: v for k, v in e.items() if k != "comparables"},
                "source": name,
                "recorded": (root / name).is_dir(),
            }
        )
    return sorted(rows, key=lambda r: (r["date"], r["source"]))


def fresh(entry: dict, on: str, window_days: int) -> list[str]:
    """Why an analysis may not be promoted on date ``on`` (a newsletter, social
    campaign, webinar or press push), read from its index entry. It needs a
    search in the ``window_days`` up to and including ``on`` that compared the
    results files the page reads now, and no gap found by then still pending.
    Empty when it may. PolicyEngine/newsletters applies the same rule; the
    shared cases are tests/fixtures/comparables_fresh_cases.json."""
    start = (dt.date.fromisoformat(on) - dt.timedelta(days=window_days)).isoformat()
    reasons = []
    pins = sorted(entry.get("current_pins") or [])
    recent = [s for s in entry["searches"] if start <= s["date"] <= on]
    if not recent:
        last = max(
            (s["date"] for s in entry["searches"] if s["date"] <= on), default=None
        )
        reasons.append(
            f"no comparables search between {start} and {on} (last: {last or 'none'}); "
            "run a prepromotion search before the push"
        )
    elif not any(sorted(s.get("results_pins") or []) == pins for s in recent):
        reasons.append(
            f"no search between {start} and {on} compared the results the page reads "
            "now; run a prepromotion search against them"
        )
    pending = [
        c["claim"]
        for c in entry.get("comparisons", [])
        if c.get("status") == "pending" and c.get("found_on", "") <= on
    ]
    if pending:
        reasons.append(
            f"gaps still pending by {on}: {', '.join(pending)}; explain them before the push"
        )
    return reasons


def report(record: AnalysisRecord, since: str, policy: dict | None = None) -> dict:
    """New comparables found on or after ``since`` and every gap over the
    threshold among them: the text of a re-harvest's issue for the owner."""
    rows = [r for r in evaluate(record, policy) if r["found_on"] >= since]
    return {
        "source": record.name,
        "since": since,
        "new_claims": [r["key"] for r in rows],
        "over_threshold": [
            {
                k: r[k]
                for k in (
                    "key",
                    "source",
                    "estimate",
                    "gap",
                    "group_gap",
                    "sign_disagrees",
                    "status",
                    "annotation",
                    "tracking_issue",
                )
            }
            for r in rows
            if r["over"]
        ],
    }


# --- CLI ------------------------------------------------------------------------------


def _local_today() -> str:
    # the stager's own date: never later than UTC's in the Americas, so a
    # scaffolded search is never dated tomorrow
    return dt.date.today().isoformat()


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m scorecard_db.comparables")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check", help="validate analysis directories")
    p_check.add_argument(
        "dirs", nargs="*", help="directories (default: every sources/analysis-*)"
    )
    p_index = sub.add_parser("index", help="write data/comparables/index.json")
    p_index.add_argument(
        "--check", action="store_true", help="fail if the committed index is stale"
    )
    p_scaffold = sub.add_parser("scaffold", help="start a record for a new analysis")
    p_scaffold.add_argument("--country", required=True)
    p_scaffold.add_argument("--kind", required=True, choices=("app", "post"))
    p_scaffold.add_argument("--slug", required=True)
    p_scaffold.add_argument("--today", default=_local_today())
    p_pins = sub.add_parser("pins", help="print the results_pins a new search records")
    p_pins.add_argument("source")
    p_record = sub.add_parser("record", help="print the app-v2 comparables block")
    p_record.add_argument("source")
    p_record.add_argument("--search-date")
    p_due = sub.add_parser("due", help="analyses due for re-harvest")
    p_due.add_argument("--apps", required=True)
    p_due.add_argument("--posts", required=True)
    p_due.add_argument("--today", default=today_utc())
    p_report = sub.add_parser("report", help="comparables found since a date")
    p_report.add_argument("source")
    p_report.add_argument("--since", required=True)
    p_fresh = sub.add_parser("fresh", help="may the analysis be promoted on a date?")
    p_fresh.add_argument("source")
    p_fresh.add_argument("--on", default=today_utc())
    args = parser.parse_args(argv)

    if args.cmd == "check":
        dirs = [Path(d) for d in args.dirs] or analysis_dirs()
        producers, policy = load_producers(), load_policy()
        failed = 0
        for d in dirs:
            errors = validate(load_analysis(d.resolve()), producers, policy)
            if errors:
                failed += 1
                print(f"FAIL {d.name}")
                for e in errors:
                    print(f"  {e}")
            else:
                print(f"ok   {d.name}")
        return 1 if failed else 0
    if args.cmd == "index":
        text = render_index(build_index())
        if args.check:
            if not INDEX_PATH.exists() or INDEX_PATH.read_text() != text:
                print(
                    f"{INDEX_PATH} is stale: run python -m scorecard_db.comparables index"
                )
                return 1
            print(f"{INDEX_PATH} is current")
            return 0
        INDEX_PATH.write_text(text)
        print(f"wrote {INDEX_PATH}")
        return 0
    if args.cmd == "scaffold":
        print(scaffold(args.country, args.kind, args.slug, args.today))
        return 0
    if args.cmd == "pins":
        record = load_analysis(SOURCES / args.source)
        print(json.dumps(current_pins(record.analysis), indent=1))
        return 0
    if args.cmd in ("record", "report", "fresh"):
        record = load_analysis(SOURCES / args.source)
        policy = load_policy()
        errors = validate(record, policy=policy)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        if args.cmd == "record":
            print(
                json.dumps(
                    app_record(record, args.search_date), indent=2, ensure_ascii=False
                )
            )
            return 0
        if args.cmd == "report":
            print(
                json.dumps(
                    report(record, args.since, policy),
                    indent=1,
                    ensure_ascii=False,
                    default=str,
                )
            )
            return 0
        reasons = fresh(
            index_entry(record, policy), args.on, policy["promotion_window_days"]
        )
        for reason in reasons:
            print(f"NOT FRESH {args.source}: {reason}")
        if not reasons:
            print(f"fresh {args.source} on {args.on}")
        return 1 if reasons else 0
    if args.cmd == "due":
        apps = _loads(Path(args.apps).read_text())
        posts = _loads(Path(args.posts).read_text())
        window = load_policy()["reharvest_window_days"]
        print(
            json.dumps(
                due(apps, posts, args.today, window), indent=1, ensure_ascii=False
            )
        )
        return 0
    return 2


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
