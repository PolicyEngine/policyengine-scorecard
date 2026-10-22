# Pre-publish comparables

Before PolicyEngine publishes an analysis, someone searches for every external estimate of what
it estimates, records each one here, and explains any large gap. Max set the rule on
2026-10-21 ("how do we ensure we always do a full review of comparables to add to scorecard
before publishing an analysis - pe-wide").

The case that prompted it: the £100,000 childcare dashboard went live on 12 October 2026 with the
30 funded hours costing £0.43bn in 2027-28. CenTax had published £0.80bn in September, from HMRC
administrative data. The dashboard listed CenTax as a benchmark, but nothing required the gap to
be explained. Its cause, a Microcosm hours draw, had been filed as [microcosm#1126] on
7 October, five days before launch. The record is
`sources/analysis-uk-childcare-100k-threshold/`; without the annotation it carries, the
validator below fails it on seven rows.

[microcosm#1126]: https://github.com/PolicyEngine/microcosm/issues/1126

## How it is enforced

1. **The search** runs before publishing, as the `policyengine-comparables-review` skill
   (PolicyEngine/policyengine-skills#100), or as a research job built from that skill's brief. It
   writes a directory here and opens a scorecard PR.
2. **This repository's CI** validates every directory (`tests/test_comparables.py`, and the build,
   which refuses an incomplete record) and checks that `data/comparables/index.json` is exactly
   what the directories build. So everything on main is a complete record.
3. **policyengine-app-v2's CI** (PolicyEngine/policyengine-app-v2#1380) checks every research
   entry that is not on its list of entries published before the cutover. The entry's
   `comparables` block must name a directory that the index on this repository's main lists,
   with the same search date, kind, producers and count. The scorecard PR therefore lands before
   the registry entry can.
4. **After publishing**, a weekly scheduled job searches again for every analysis published in the
   last `reharvest_window_days` (183). A new comparable becomes a row here; a new gap over the
   threshold also opens an issue for the analysis's owner.

## Before a push

Publishing is not the only moment that counts. When an analysis that is already published is
featured in a newsletter, a social campaign, a webinar or a press push, its comparables search is
run again first (Max, 2026-10-21: "even if we've already published something, we should do a
fresh comp review before big pushes like newsletters"). The UK newsletter dated 21 October
(PolicyEngine/newsletters `editions/2026-10-20-uk.html`) featured the childcare dashboard at
£0.59bn for both schemes. A fresh search would have put CenTax's £0.80bn static cost for the
30 hours alone beside it.

- The search is appended to the analysis's `search_log.json` with `kind: prepromotion`, or is the
  analysis's first search if it has none yet (`backfill`).
- The push may go ahead only when:
  - a search is dated on the push date or in the `promotion_window_days` before it
    (`data/comparables/policy.json`, 7 by default);
  - that search compared the results files the analysis reads now (its `results_pins` equal
    the index's `current_pins`);
  - no gap found by the push date is still `pending`. A pending gap blocks the push until its
    cause is written.
- `python -m scorecard_db.comparables fresh analysis-<country>-<slug> --on <date>` says yes or why
  not.
- PolicyEngine/newsletters' CI (PolicyEngine/newsletters#29) applies the same rule to every
  policyengine.org analysis an edition links, for editions dated on or after its cutover.
  `tests/fixtures/comparables_fresh_cases.json` holds cases both implementations are tested
  against. The index publishes the window, each search's pins and when each claim was found, so
  that check needs nothing but the index.

## The directory

`sources/analysis-<country>-<slug>/`, where `<slug>` is the analysis's slug on policyengine.org
(the apps.json slug, or the post's filename up to its first dot, lower-cased with underscores as
hyphens).

| File | What it holds |
|---|---|
| `analysis.json` | The registry entry, scope, search terms, the policy worlds it scores, and every PolicyEngine estimate it publishes, each pinned to its results file by repo, commit, path, field and SHA-256 |
| `search_log.json` | Every search: date, kind (`prepublish`, `backfill`, `reharvest`, `prepromotion`), who ran it, the results files it compared, and one entry per listed producer |
| `manifest.jsonl` | One line per primary publication, with its SHA-256; every line is cited by a claim, an annotation basis or a page a search checked |
| `claims_staged.jsonl` | Every comparable found, staged under the harvest rules |
| `annotations.json` | The status and cause of anything that is not a plain comparison, each citing a basis |

Start one with:

```bash
PYTHONPATH=. python -m scorecard_db.comparables scaffold --country uk --kind app --slug <slug>
```

The JSON files are strict: a repeated key fails the record.

### The estimates

Each estimate in `pe_estimates` names its `world`, `metric`, `unit_concept`, `period` and
`time_basis`, and two conditions:

- `conditions.basis`: `static`, `post_behavioural`, `forecast` or `outturn`;
- `conditions.program`: a slug for what is costed: the programmes or taxes whose change the
  figure counts (`thirty_hours`, `both_schemes`, or `ny_dependent_exemption_ny_state_income_tax`
  for a state tax expenditure beside a net budget effect).

A money figure in a base year's prices has `conditions.prices: real`; absent means cash.
When `conditions.fy` names a fiscal year, `period` is its end year and `time_basis` is
`fiscal_year`. Each estimate is stated in PolicyEngine's own orientation for its metric; when the
results file prints it the other way round (a cost as a positive number), the estimate carries
`sign: -1` and a `sign_basis`.

An estimate that a rerun replaced moves to `superseded_estimates` with `superseded_on`, and stays
on the scorecard as history.

A household calculator, which computes figures for the household a reader describes and
publishes no fixed estimate, is still searched: it declares `"calculator": {"reason": "..."}`
and may pin no estimates, its searches record `results_pins: []`, and every claim found says
in `pe_missing` that the calculator publishes no aggregate.

### The search

`data/comparables/producers.json` lists the producers for each country. A search logs every
producer whose `added` date is on or before the search date, with one of:

- `found`: the claim keys it found;
- `none_found`: with the queries run or pages checked;
- `found_not_staged`: a comparable exists but its primary cannot be read (harvest rule 8), so the
  note says what it is and the pages it was seen on;
- `not_applicable`: only when the producer's `applies_to` excludes the analysis's scope (the
  Scottish Fiscal Commission for a UK-wide analysis, state fiscal notes for a federal one).

The searches are in date order, and each is dated on a real day that is no later than today and
no earlier than the country's producer list. Their kinds follow the analysis's life:

| Kind | When |
|---|---|
| `prepublish` | The first search, on or before `published` |
| `backfill` | The first search of an analysis already published, on or after `published` |
| `reharvest` | A later search, after `published` and after the first search |
| `prepromotion` | A later search before a push, after `published` and after the first search |

Each search records `results_pins`, the results files it compared (`repo@commit:sha256`; `python
-m scorecard_db.comparables pins <source>` prints them). The latest search's pins are the
estimates' current pins: a new results file needs a new search.

`open_search` and `academic` are on every list: a comparable from a producer not on the list is
found under them and keeps its producer's own slug as `source`. A claim from a listed producer is
logged under that producer's entry. `source` is never `open_search`, `academic` or
`policyengine`. When an open search keeps finding one producer, add it to the list with a `why`
(the first search added DfE this way).

### The claims

Staged under the harvest rules (`sources/harvest-uk-ab2025-2026-09-24/README.md`), checked
mechanically where they can be:

- **Verbatim values.** `value_raw` is the number as printed: a minus sign, the word "minus" or
  parentheses make it negative, and a scale printed after it (`m`, `bn`, `%`) must match the
  `normalization`. `value` is it under a registered `normalization`; the validator parses one back
  to the other, for a chart reading too. `quote` must print the value as a whole number with its
  sign, except for a chart reading. A claim is never re-signed: its sign convention travels in
  `conditions.sign_convention`, in words `scorecard_db/signs.py` reads. A compared change metric
  needs a convention that starts `positive =` and says one thing.
- **The same identity as an estimate**: `metric`, `unit_concept`, `period`, `time_basis`,
  `conditions.basis`, `conditions.program` and `conditions.prices` (`cash` when absent, `real`,
  or `unstated` when the producer does not say), with the same `conditions.fy` rule. The basis is
  one word; a fuller account of it goes in `conditions.basis_note`. A claim whose producer does
  not say whether it allows for behaviour has basis `unstated`: it is never the same quantity as
  an estimate, so it can only sit beside one with a stated mismatch.
- **Registered vocabulary** for `metric` and `unit_concept`, or `null` with a proposal (such a
  claim is staged but waits for its vocabulary decision before it reaches the database).
- **Named baselines**: `baseline_policy` is a label in `scorecard_db/baselines.py`, or null for
  current law. A world in `analysis.json` may name its `baseline` the same way.
- **Attribution and benchmark class.** Only a producer's own estimate (`attribution: own`) is
  compared. An administrative level is calibration material and belongs in a producer-level
  source, where `relationships.py` assigns it.
- **Primaries, hashed**: `publication.primary_sha256` is a line in `manifest.jsonl`, and
  `publication.date` is no later than the day the claim was found.
- **Ranges**: a printed range is two claims, `value_kind` `range_low` and `range_high`, sharing a
  `conditions.range_group`, the same identity and the same `compare_to`. A one-sided figure
  ("over £1 billion") is `lower_bound` or `upper_bound`, and like a `cumulative` total it is set
  beside an estimate, never compared with one.

### The comparison

A claim either names the PolicyEngine estimate it is compared with (`compare_to`), or says in
`pe_missing` why there is none.

- A compared claim has the estimate's full identity and baseline, is the producer's own, and is
  not cumulative. When the two score different policy worlds, `compare_to.across_worlds` gives
  the reason the quantities match and its basis, and the comparison is `constructed`, not
  `comparable`.
- An uncompared claim that has an estimate near it (the same period, and the same metric and
  unit where the claim names them) cannot be waved off with a sentence. It names that estimate
  in `nearest_estimate`, and an annotation with status `concept_mismatch` (or `pe_gap`) and a
  basis says why the two differ: a net-of-behaviour cost beside a static one, for example. On
  the scorecard it then appears beside that estimate, labelled with the mismatch, rather than
  blank. A claim that is the same quantity as its nearest estimate must be compared instead.

The gap is PolicyEngine's value over the external value, minus one, with the external value in
PolicyEngine's orientation (`signs.py`; an unsigned level compares absolute values). A
nonzero estimate against a published zero is over any threshold, and so is any pair whose signs
disagree. A range is over only when the estimate lies outside it by more than the threshold,
measured from the nearer bound.

### The threshold

`data/comparables/policy.json` `gap_threshold`, 0.25 by default and always below 1, so that a
sign disagreement is always over it. A compared claim whose absolute gap exceeds it needs an
annotation with `explains_gap: true`: its `cause`, and a `basis` that is one of:

- a GitHub issue or pull request URL;
- engine metadata, as a GitHub blob pinned to a commit or a file in this repository;
- a document or a measured diagnostic, as a URL with a path or a file in this repository.

This is the scorecard's existing rule against fabricated mechanisms: a cause that cannot cite one
of those does not ship. A miss is allowed; an unexplained one is not.

A comparable that a search after publication finds (`backfill`, `reharvest` or `prepromotion`)
may instead carry a `pending` annotation naming the `tracking_issue` opened for the owner. The
index counts it, and it blocks any push, until the cause is written. Nothing found before
publication can be pending.

### The database

`scorecard_db/ingest_analysis_comparables.py` (build step `analysis_comparables`) puts every
record on the scorecard. Claims are held out (another producer's estimate is a comparator, never
a calibration target), with `conditions.analysis` naming the analysis. Each claim's result is:

- for a compared claim, the analysis's own figure with its record's status (a pending gap shows
  as `comparable` or `constructed`, with an annotation naming its tracking issue);
- for a claim beside its nearest estimate, that estimate's figure, labelled with the mismatch;
- for any other claim, none.

A superseded estimate adds a history result. Lanes `analysis-comparables-uk` and
`analysis-comparables-us` show the tally.

## The index and the app-v2 record

`python -m scorecard_db.comparables index` writes `data/comparables/index.json`, keyed by
directory. policyengine-app-v2 reads it from this repository's main branch (the repository is
public, so a raw fetch needs no token). The block to paste into the analysis's apps.json or
posts.json entry is printed by:

```bash
PYTHONPATH=. python -m scorecard_db.comparables record analysis-uk-<slug>
```

```json
"comparables": {
  "status": "reviewed",
  "scorecardSource": "analysis-uk-<slug>",
  "searchDate": "2026-10-21",
  "searchKind": "prepublish",
  "producersSearched": ["academic", "centax", "..."],
  "found": 20,
  "searchLog": "https://github.com/PolicyEngine/policyengine-scorecard/blob/main/sources/analysis-uk-<slug>/search_log.json"
}
```

A post that publishes no estimate (an event, an announcement) declares
`{"status": "no_estimate", "reason": "..."}` instead. That is allowed only for a post tagged as
one of those kinds (`org`, `event`, `giving`, `conferences`, `year-in-review`, `april-fools`) and
no analysis tag; an app never declares it.

## Re-harvest support

```bash
# analyses published in the window, and whether each has a record
PYTHONPATH=. python -m scorecard_db.comparables due --apps apps.json --posts posts.json
# what a re-harvest found since a date, and its gaps over the threshold
PYTHONPATH=. python -m scorecard_db.comparables report analysis-uk-<slug> --since 2026-10-26
```
