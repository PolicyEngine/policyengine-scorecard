#!/usr/bin/env python3
"""Stage IPPR's Autumn Budget 2026 claims (#230, family uk_ippr).

The rows are data in this file. Running it rewrites manifest.jsonl and
claims_staged.jsonl.gz byte for byte:

    python sources/harvest-uk-ab2026-2026-10-29/uk_ippr/stage.py

`--verify` also checks, where the primaries are present under
.ab2026-primaries/uk_ippr/ (git-ignored, hashed not vendored), that each
primary hashes to its manifest sha256 and that every quote occurs in its
page's text.
"""

import gzip
import hashlib
import io
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIMARIES = ROOT / ".ab2026-primaries" / "uk_ippr"
SOURCE = "ippr"
EVENT = "autumn_budget_2026"

PUBS = {
    "UB": {
        "url": "https://www.ippr.org/media-office/unfinished-business-on-economic-reform-after-sound-budget-says-ippr",
        "title": "‘Unfinished business’ on economic reform after sound Budget, says IPPR",
        "date": "2026-10-28",
        "publisher": "IPPR",
        "sha256": "f834beaad7802472dc5f2e6f59738e3fb6ee953dd4357f7fc234e53939b1ea14",
        "bytes": 60580,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "Press release. datePublished 2026-10-28T13:54:00Z, dateModified 2026-10-29T16:04:19Z (JSON-LD); fetched 2026-10-29T16:17Z (curl, browser User-Agent, HTTP 200).",
        "file": "unfinished-business.html",
    },
    "NORTH": {
        "url": "https://www.ippr.org/media-office/ippr-north-reacts-to-andy-burnhams-first-budget",
        "title": "IPPR North reacts to Andy Burnham’s first Budget",
        "date": "2026-10-28",
        "publisher": "IPPR North",
        "sha256": "9b1e6ee72f3af251748526f7911a27e508d207d2f8909e9e9d0074a42f45cab9",
        "bytes": 58127,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "Press release, found on the ippr.org media-office listing; its £285m of Good Growth Funds and £1.5bn borrowing facilities are HM Treasury allocations and financing (design, README rule 8), not staged. datePublished 2026-10-28T14:12:00Z, dateModified 2026-10-29T16:21:46Z; fetched 2026-10-29T16:35Z.",
        "file": "ippr-north-reacts.html",
    },
    "SCOT": {
        "url": "https://www.ippr.org/media-office/ippr-scotland-reacts-to-andy-burnhams-first-budget",
        "title": "IPPR Scotland reacts to Andy Burnham's first Budget",
        "date": "2026-10-28",
        "publisher": "IPPR Scotland",
        "sha256": "9f328d542179e8f8f4a5a88d48a8f5a61680b3c2acb98bbc2eec95a25eb5b153",
        "bytes": 57561,
        "doc_type": "html",
        "access": "direct",
        "retrieved": "2026-10-29",
        "note": "Press release, found on the ippr.org media-office listing; 0 rows (its only figure is the £100 Household Energy Payment, a policy parameter). datePublished 2026-10-28T14:21:00Z, dateModified 2026-10-29T16:34:34Z; fetched 2026-10-29T16:35Z.",
        "file": "ippr-scotland-reacts.html",
    },
}

ROWS = []
CHECKS = []


def add(pub, value, value_raw, quote, locator, *, metric=None, pmetric=None, unit=None, punit=None,
        normalization="as printed", fy=None, period=None, time_basis=None, key=None, pkey=None,
        attribution="own", bclass="different_model", model="not_stated", kind="point",
        cond=None, hint=None, note="", conf="high", geography="UK"):
    p = PUBS[pub]
    c = {"fiscal_event": EVENT, "geography": geography}
    if fy:
        c["fy"] = fy
        period = int(fy[:4]) + 1
        time_basis = "fiscal_year"
    c.update(cond or {})
    if pkey:
        assert key is None
        c["proposed_measure_key"] = pkey
    r = {
        "source": SOURCE, "source_model": model, "value": value, "value_raw": value_raw,
        "normalization": normalization, "value_kind": kind, "period": period, "time_basis": time_basis,
        "conditions": c, "reform_hint": hint, "measure_key": key, "attribution": attribution,
        "benchmark_class": bclass, "baseline_policy": None,
        "publication": {"title": p["title"], "url": p["url"], "date": p["date"], "publisher": p["publisher"],
                        "primary_sha256": p["sha256"], "locator": locator, "access": p["access"]},
        "source_table": None, "source_column": None, "quote": quote, "note": note,
        "parse_confidence": conf, "status": "ok",
    }
    for k, v in (("metric", metric), ("proposed_metric", pmetric), ("unit_concept", unit), ("proposed_unit", punit)):
        if v:
            r[k] = v
    assert value_raw in quote, (value_raw, quote)
    assert len(quote.split()) < 15, quote
    CHECKS.append((len(ROWS), pub))
    ROWS.append(r)


# --- 'Unfinished business' (Carsten Jung, on the Budget's macro-economic impact) ---
add("UB", -0.2, "0.2 percentage points", "It will lower inflation by at least 0.2 percentage points",
    "quote from Carsten Jung, first paragraph",
    metric="cpi_inflation_effect", unit="percentage_points",
    normalization="'lower inflation by at least 0.2 percentage points' -> -0.2 (magnitude at least 0.2)",
    period=2027, time_basis="point_in_time", kind="range_low", attribution="restated", model="obr_efo_forecast",
    pkey="ab2026__package_cost_of_living_support", conf="medium",
    cond={"sign_convention": "positive = higher CPI inflation",
          "originator": "not named; matches the OBR's peak effect (EFO October 2026 para 3.10: 0.22 percentage points in 2027 Q2)",
          "year_note": "no period stated; staged at 2027, the year of the OBR's peak effect"},
    hint="the cost of living support announced today",
    note="IPPR names no source. The OBR's paragraph 3.10 says the fuel duty changes and the temporary VAT cut on domestic electricity (Table 6.1 lines 2 and 3) reduce CPI inflation by 0.22 percentage points at their peak in the second quarter of 2027; staged as restated with medium confidence.")
add("UB", 18_000_000_000, "£18 billion", "address the £18 billion annual taxpayer losses at the Bank of England",
    "quote from Carsten Jung, second paragraph",
    pmetric="apf_indemnity_losses", unit="gbp", normalization="£ billion × 1e9", fy="2026-27",
    attribution="restated", conf="medium",
    cond={"sign_convention": "positive = losses to the taxpayer",
          "originator": "source not stated on the page",
          "year_note": "'annual'; no year stated; staged at the scoring year 2026-27"},
    note="Context level, no measure key; the AB2025 uk_ippr family staged IPPR's '£22 billion taxpayer losses at the Bank of England' the same way.")

# --- IPPR North ---
add("NORTH", 4_000_000_000, "£4billion", "Five per cent of income tax devolved to mayors would see an additional £4billion",
    "statement, third paragraph", pmetric="devolved_revenue", unit="gbp", normalization="£ billion × 1e9",
    fy="2026-27", pkey="ab2026_option__income_tax_5pc_share_devolved_to_mayors", geography="England", conf="medium",
    cond={"sign_convention": "positive = revenue held by mayors",
          "year_note": "no year stated; staged at the scoring year 2026-27",
          "origin": "IPPR and IPPR North, 'Devolution that delivers: Fiscal power for regional growth' (linked from the release)"},
    hint="devolve five per cent of income tax to England's mayors",
    note="IPPR North's own estimate of an option beyond the Budget's income tax devolution commitment.")


# === review fixes, 3 November 2026 ========================================
# verify-thinktanks-a.md, uk_ippr (PR #231). No primary was re-opened (the
# session's network policy refused ippr.org), and no printed value changes.

# Finding 1: IPPR's words ("the cost of living support announced today") do
# not define a scope; lines 2 and 3 were our match to the OBR, so under rule
# 3 the row is context. "At least 0.2" lower makes the signed -0.2 an upper
# bound.
_r = ROWS[0]
assert _r["value_raw"] == "0.2 percentage points"
del _r["conditions"]["proposed_measure_key"]
_r["value_kind"] = "range_high"


# === review B fixes, 4 November 2026 ======================================
# Review B (PR #231, issue comment 6635498758), uk_ippr finding 1, taken as
# the coordinator's brief says. IPPR prints an unsigned 0.2 ("lower ... by at
# least"); README rule 10 keeps the sign the producer prints, so the row
# keeps the magnitude with an "as worded" convention, as uk_obr_tables row
# 2653 does, and "at least" makes it a lower bound.
_r = ROWS[0]
assert _r["value_raw"] == "0.2 percentage points"
_r["value"] = 0.2
_r["value_kind"] = "range_low"
_r["normalization"] = "'lower inflation by at least 0.2 percentage points' -> 0.2 (magnitude as worded; 'at least' -> lower bound)"
_r["conditions"]["sign_convention"] = "as worded: positive = reduction in CPI inflation"


def manifest_lines():
    keys = ["url", "title", "date", "publisher", "sha256", "bytes", "doc_type", "access", "retrieved", "note"]
    return "".join(json.dumps({k: p[k] for k in keys}, ensure_ascii=False) + "\n" for p in PUBS.values())


def claims_bytes():
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in ROWS:
            gz.write((json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    return buf.getvalue()


class _Text(HTMLParser):
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "br", "td", "th", "section", "article"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip = max(0, self.skip - 1)
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def _norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def verify():
    texts, bad = {}, 0
    for k, p in PUBS.items():
        f = PRIMARIES / p["file"]
        if not f.exists():
            continue
        b = f.read_bytes()
        assert hashlib.sha256(b).hexdigest() == p["sha256"], f"{k}: sha256 mismatch"
        assert len(b) == p["bytes"], f"{k}: byte count"
        t = _Text()
        t.feed(b.decode("utf-8"))
        texts[k] = _norm("".join(t.out))
    for idx, pub in CHECKS:
        if pub in texts and _norm(ROWS[idx]["quote"]) not in texts[pub]:
            print(f"row {idx}: quote not in {pub}: {ROWS[idx]['quote']!r}")
            bad += 1
    print(f"verify: {len(ROWS)} rows, {len(texts)} primaries read, {bad} problems")
    return bad


if __name__ == "__main__":
    (HERE / "manifest.jsonl").write_text(manifest_lines(), encoding="utf-8")
    data = claims_bytes()
    (HERE / "claims_staged.jsonl.gz").write_bytes(data)
    print(f"{len(ROWS)} rows, sha256 {hashlib.sha256(data).hexdigest()}")
    if "--verify" in sys.argv[1:]:
        sys.exit(1 if verify() else 0)
