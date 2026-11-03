# Stage Autumn Budget 2026 claims for the PolicyEngine scorecard (#230)

You are staging one or more producer families for the Autumn Budget 2026 (AB2026) harvest in PolicyEngine/policyengine-scorecard. A family is the figures one producer group published about the UK Autumn Budget of 28 October 2026. Each figure becomes one JSON row, quoted from a primary document whose sha256 you record. The coordinator merges your families into PR #231. You don't commit, push or open anything.

## Where you are

Your working directory is a git worktree of the scorecard repository, detached at commit 9a0189cf. It is yours alone, and the coordinator copies your family directories out of it when you finish.

Read these first, in order:

1. `sources/harvest-uk-ab2026-2026-10-29/README.md`: the AB2026 rules, which are the AB2025 rules with seven exceptions.
2. `sources/harvest-uk-ab2025-2026-09-24/README.md`: the full row contract, the proposal lists (`proposed_metric`, `proposed_unit`, `proposed_baseline`) and the AB2025 rules 1–10. Where the AB2026 README differs, it wins.
3. `sources/harvest-uk-ab2026-2026-10-29/REGISTRY_KEYS.md`: every measure key you may use, with its HM Treasury Table 6.1 line and title.
4. `sources/harvest-uk-ab2026-2026-10-29/uk_hmt_tables/`: a finished AB2026 family (its NOTES.md, manifest.jsonl and rows). Read rows with:
   `python3 -c "import gzip,json;[print(json.dumps(json.loads(l),indent=1)) for l in list(gzip.open('PATH/claims_staged.jsonl.gz','rt'))[:3]]"`
5. The AB2025 family of the same producer, if there is one (`sources/harvest-uk-ab2025-2026-09-24/<family>/`). Read its NOTES.md and a dozen rows, and follow its conventions for that producer: `source` slug, `source_model`, metric choices and condition names.
6. `pipeline/ab2026_harvest_contract.py`: the checker your output must pass.

## What you produce, per family

Write only inside `sources/harvest-uk-ab2026-2026-10-29/<family>/`, plus the primaries folder below. Don't touch anything else in the repository: not COUNTS.json, the README, REGISTRY_KEYS.md, tests, the registry or other families. Don't run git commands that change state.

- **`manifest.jsonl`:** one line per primary document. Keys: url, title, date (publication date, YYYY-MM-DD), publisher, sha256, bytes, doc_type, access, retrieved (YYYY-MM-DD) and note.
- **`claims_staged.jsonl.gz`:** one JSON object per line, written deterministically:
  `gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="")`, each line `json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n"`, rows in reading order (document, then page or table, then position).
  Write it from a small Python script. Keep the script in the family directory as `stage.py`, with the rows as data inside it, so a re-run reproduces the file byte for byte.
- **`NOTES.md`:** what the family is and the access recipe (how each primary was fetched, and any fallback to a local copy). Also the coverage tally (rows per primary and per measure key), conventions (sign, units, period, what "central" means for this producer), and every proposed key with its exact scope. Finally, what you did **not** stage and why: charts without printed values, figures restated from another producer, numbers you couldn't tie to a measure, pages you couldn't reach.

## Primaries

- Fetch each primary fresh: `curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"`.
- Save the bytes under `.ab2026-primaries/<family>/` in your worktree (git ignores it), and hash them with `shasum -a 256`. Primaries are hashed, not vendored.
- **Web pages:** hash the HTML bytes you fetched. Quote from the page's own text. A page's HTML can change between fetches, so record the fetch time in `note`.
- **Blocked fetches:** if a site refuses (403, Cloudflare challenge, login wall), don't try to get round it. Use the local copy listed in your assignment if there is one: hash those bytes, set `access` to "local copy" and explain in `note`. Otherwise list the page as unreached in NOTES.md.
- **Changed primaries** (README rule 7): if a primary changed since the copy listed in your assignment, hash both versions as two manifest lines. Rows cite the version they were read from, and NOTES.md says what changed.
- **Reading files:** use `pdftotext -layout` for PDFs and openpyxl for spreadsheets. Never read values off a chart's bars. A number counts only if the document prints it: in text, a table, or a chart's data label.

## Row rules that lanes get wrong

- **Verbatim values only.**
  - `value_raw` is the string as printed, for example "£1.2bn", "-2,625" or "3.4%".
  - `value` is that number normalised to the unit, and `normalization` says how, for example "£ billion × 1e9".
  - A number you can't see in the primary is not a row.
- **Never invent enums.** `metric` must be a `scorecard_db.models.Metric` value and `unit_concept` a `UnitConcept` value. Otherwise leave `metric` or `unit_concept` out and set `proposed_metric` or `proposed_unit`, reusing a proposal already listed in the AB2025 README where one fits.
- **`conditions`:**
  - Every value is a string.
  - Always include `fiscal_event: "autumn_budget_2026"`.
  - Include `fy` ("2027-28") only for fiscal-year figures; then `period` is the end year (2028) and `time_basis` is "fiscal_year".
  - A calendar-year or point-in-time figure has no `fy`. Its `period` is that year and `time_basis` is "annual" or "point_in_time".
  - Distributional figures carry their breakdown as conditions, for example `income_decile: "3"`, `household_type: "..."` or `vigintile: "..."`. Follow the AB2025 family's names.
- **`measure_key`** (README rules 2 and 3):
  - Use a registry key only when the producer's figure is for exactly that measure, or exactly that package's lines.
  - When the scope differs (a different set of measures, an option the producer costed, the Budget "as a whole" by the producer's own definition), set `measure_key: null` and `conditions.proposed_measure_key` to `ab2026__package_<slug>` or `ab2026_option__<slug>`. List each such key in NOTES.md with its scope as Table 6.1 line numbers and the producer's own words.
  - A context figure about no measure (a forecast, a poverty level under current policy, a living-standards projection) has `measure_key: null` and no proposed key.
- **`attribution`:**
  - "own": the producer's own estimate.
  - "restated": the producer repeats an official (HMT, OBR, DWP) or other producer's number. Stage it as restated, with `note` naming the original source.
  - "same_assumptions": only for a producer that restates a PolicyEngine figure.
- **`benchmark_class`:** "different_model" for a model estimate, "administrative_fact" for an outturn or official count.
- **`quote`** (README rule 6):
  - **HM Treasury and OBR:** quote the full sentence or cell (Open Government Licence).
  - **Everyone else:** fewer than 15 words, carrying the number. Never paste longer passages.
  - `quote` must contain `value_raw`.
- **`publication`:** {title, url, date, publisher, primary_sha256, locator, access}. `locator` is a page, slide, table or paragraph reference precise enough to find the number in seconds.
- **`status`:** "ok". `parse_confidence`: "high" unless something makes it less certain, and then `note` says what.
- **Units and periods:** don't convert a producer's real-terms or cash basis, or its year basis. Record the basis in `conditions`, for example `price_basis: "2026-27 prices"`.

## Verify before you report

1. `PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/<family>` must report 0 problems.
2. Re-run `stage.py` and confirm the gzip's sha256 is unchanged.
3. Pick 10 rows at random (more for families over 300 rows). For each, re-open the primary at its locator and confirm the number, the sign, the unit and the period. List those checks in your report.
4. Check that no measure_key is attached to a figure whose scope differs from the key's title.

## Report (your final message, and the -o file)

- Per family: rows, primaries (with sha256), and rows by measure_key, including null.
- Every proposed key with its scope.
- What you did not stage and why, including unreached pages.
- The checker output and your 10-row spot check.
- Anything in the primaries that looks wrong or contradictory. Report it; don't fix it.
