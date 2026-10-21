# Pre-publish comparables

Before PolicyEngine publishes an analysis, someone searches for every external estimate of what
it estimates, records each one here, and explains any large gap. Max set the rule on
2026-10-21 ("how do we ensure we always do a full review of comparables to add to scorecard
before publishing an analysis - pe-wide").

The case that prompted it: the £100,000 childcare dashboard went live on 12 October 2026 with the
30 funded hours costing £0.43bn in 2027-28. CenTax had published £0.80bn in September, from HMRC
administrative data. The dashboard even listed CenTax as a benchmark, but nothing required the
gap to be explained, and the cause, a Microcosm hours draw ([microcosm#1126]), was found only
after Arun Advani pointed it out. Its record is
`sources/analysis-uk-childcare-100k-threshold/`; without the annotation it carries, the
validator below fails it on six rows.

[microcosm#1126]: https://github.com/PolicyEngine/microcosm/issues/1126

## How it is enforced

1. **The search** runs before publishing, as the `policyengine-comparables-review` skill in
   PolicyEngine/policyengine-skills (or a Subfleet research job from its brief). It writes a
   directory here and opens a scorecard PR.
2. **This repository's CI** validates every directory (`tests/test_comparables.py`, and the build,
   which refuses an incomplete record) and checks that `data/comparables/index.json` is exactly
   what the directories build. So everything on main is a complete record.
3. **policyengine-app-v2's CI** checks every research entry dated on or after its cutover: the
   entry's `comparables` block must name a directory that the index on this repository's main
   lists, with the same search date, producers and count. The scorecard PR therefore lands
   before the registry entry can.
4. **After publishing**, a weekly launchd job (`comparables-reharvest`) searches again for every
   analysis published in the last `reharvest_window_days` (183). A new comparable becomes a row
   here; a new gap over the threshold also opens an issue for the analysis's owner.

## The directory

`sources/analysis-<country>-<slug>/`, where `<slug>` is the analysis's slug on policyengine.org
(the apps.json slug, or the post's filename without `.md`).

| File | What it holds |
|---|---|
| `analysis.json` | The registry entry, scope, search terms, the policy worlds it scores, and every PolicyEngine estimate it publishes, each pinned to its results file by repo, commit, path, field and SHA-256 |
| `search_log.json` | Every search: date, kind (`prepublish`, `backfill`, `reharvest`), who ran it, and one entry per listed producer |
| `manifest.jsonl` | One line per primary publication, with its SHA-256 |
| `claims_staged.jsonl` | Every comparable found, staged under the harvest rules |
| `annotations.json` | The status and cause of anything that is not a plain comparison, each citing a basis |

Start one with:

```bash
PYTHONPATH=. python -m scorecard_db.comparables scaffold --country uk --kind app --slug <slug>
```

### The search

`data/comparables/producers.json` lists the producers for each country. A search logs every
producer whose `added` date is on or before the search date, with one of:

- `found`: the claim keys it found;
- `none_found`: with the queries run or pages checked;
- `found_not_staged`: a comparable exists but its primary cannot be read (harvest rule 8), so the
  note says what it is and the pages it was seen on;
- `not_applicable`: only when the producer's `applies_to` excludes the analysis's scope (the
  Scottish Fiscal Commission for a UK-wide analysis, state fiscal notes for a federal one).

`open_search` and `academic` are on every list: a comparable from a producer not on the list is
logged under them and keeps its producer's own slug. When an open search keeps finding one
producer, add it to the list with a `why` (the first search added DfE this way).

### The claims

Staged under the harvest rules (`sources/harvest-uk-ab2025-2026-09-24/README.md`), checked
mechanically where they can be:

- **Verbatim values.** `value_raw` is the string as printed; `value` is it under a registered
  `normalization`; the validator parses one back to the other, and `quote` must contain the
  printed value. A claim is never re-signed: its sign convention travels in
  `conditions.sign_convention`, in words `scorecard_db/signs.py` reads.
- **Registered vocabulary** for `metric` and `unit_concept`, or `null` with a proposal (such a
  claim is staged but waits for its vocabulary decision before it reaches the database).
- **Named baselines**: `baseline_policy` is a label in `scorecard_db/baselines.py`, or null for
  current law.
- **Attribution and benchmark class.** Only a producer's own estimate (`attribution: own`) is
  compared. An administrative level is calibration material and belongs in a producer-level
  source, where `relationships.py` assigns it.
- **Primaries, hashed**: `publication.primary_sha256` is a line in `manifest.jsonl`.

### The comparison

A claim either names the PolicyEngine estimate it is compared with (`compare_to`), or says in
`pe_missing` why there is none. A compared claim has the estimate's metric, unit, period and time
basis. When the two score different policy worlds, `compare_to.across_worlds` gives the reason
the quantities match and its basis, and the comparison is `constructed`, not `comparable`.

The gap is PolicyEngine's value over the external value, minus one, with the external value in
PolicyEngine's orientation (`signs.py`; an unsigned magnitude compares absolute values). A
nonzero estimate against a published zero is over any threshold. Each PolicyEngine estimate is
stated in PolicyEngine's own orientation for its metric; when the results file prints it the
other way round (a cost as a positive number), the estimate carries `sign: -1` and a
`sign_basis`.

### The threshold

`data/comparables/policy.json` `gap_threshold`, 0.25 by default. A compared claim whose absolute
gap exceeds it needs an annotation with `explains_gap: true`: its `cause`, and a `basis` that is a
GitHub issue or pull request, engine metadata pinned to a commit, a document, or a measured
diagnostic. This is the scorecard's existing rule against fabricated mechanisms: a cause that
cannot cite one of those does not ship. A miss is allowed; an unexplained one is not.

A comparable that a post-publication re-harvest finds may instead carry a `pending` annotation
naming the issue opened for the owner; the index counts it until the cause is written.

### The database

`scorecard_db/ingest_analysis_comparables.py` (build step `analysis_comparables`) puts every
record on the scorecard: claims held out (another producer's estimate is a comparator, never a
calibration target), with `conditions.analysis` naming the analysis; one result per compared
claim, the analysis's own figure with its record's status; uncompared claims published without a
result. Lanes `analysis-comparables-uk` and `analysis-comparables-us` show the tally.

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

An entry that publishes no estimate (an event, an announcement) declares
`{"status": "no_estimate", "reason": "..."}` instead; app-v2 refuses that for an entry tagged
`policy`.

## Re-harvest support

```bash
# analyses published in the window, and whether each has a record
PYTHONPATH=. python -m scorecard_db.comparables due --apps apps.json --posts posts.json
# what a re-harvest found since a date, and its gaps over the threshold
PYTHONPATH=. python -m scorecard_db.comparables report analysis-uk-<slug> --since 2026-10-26
```
