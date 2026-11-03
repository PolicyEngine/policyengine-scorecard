I've finished the IFS family in the worktree. It now has 144 rows: the 87 deck rows are unchanged and the 57 new rows come after them. Every check passes, with one exception: the exact pytest command you gave can't run in this sparse worktree, so I ran it with `--noconftest` (details below). One thing to sort before landing: while my context was being compacted, the harness made a commit (`a0a7e470`) that includes `stage.py`, which must not go on the PR branch. Nothing is committed by me, pushed or posted.

## Before landing

- **The auto-commit.** `a0a7e470` ("fixup! …", parent `5bd845ba`) holds an earlier draft's stale NOTES.md, COUNTS.json and claims file, plus `stage.py`. My final files are uncommitted changes on top of it. I left the commit in place. README line 68 says `stage.py` belongs on `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/ifs/uk_ifs_ab2026/stage.py`, and this branch carries only each family's three files.
- **Stale README (outside my write scope).** Line 51 still says 5,891 rows and 401 restated; the new totals are 5,948 and 446. Line 60 still says 87 rows and 5 primaries for IFS; it is now 144 and 14. Line 77's "Still to come from the coordinator" paragraph is now done.
- **Cross-family mismatch.** The OBR family stages the Table 3.1 direct effects under `revenue_change`. The HM Treasury red book, RF and these IFS rows use `decisions_effect_on_borrowing`.

## Rows added (57)

| Primary | Rows | Metrics | Keys | Examples |
|---|--:|---|---|---|
| Initial response (text) | 5 | `fiscal_headroom` (2), `decisions_effect_on_borrowing` (2), `affected_share` | government decisions (2, proposed); household energy payment (1, registered) | "£13 billion": £13bn, 2029–30, before the Budget's measures, restated. "£8 billion this year": £8bn, 2026–27. "around 80% of households in England": 0.8 |
| Opening remarks (text) | 6 | proposed `measure_count`, `spending_pressure` (2), `reserve_allocated_share` (2); `affected_share` | household energy payment (1) | "98 measures": 98. "£17 billion in 2030-21": £17bn, medium confidence. "25% of the capital reserve": 25 |
| Flourish 30734907 (decade income index) | 5 | proposed `real_household_disposable_income_index`, unit `index` | none | Year 6: 99.78742437 (2026). Year 8: 100.8444439. Year 10: 102.2952697 |
| Flourish 30726471 (current budget deficit) | 11 | proposed `current_budget_deficit`, £ | none | 2026–27 October: 40.6 → £40.6bn. 2028–29 March: −3.3. 2031–32 October: −20.9 |
| Flourish 30726788 (headroom) | 2 | `fiscal_headroom`, share of GDP | none | March 2026: 0.0067196. October 2026: 0.0041001 |
| Flourish 30726917 (real GDP) | 11 | proposed `real_gdp_index`, unit `index` | none | 2026–27 March: 101.2853395. 2027–28 October: 102.4. 2031–32 October: 109.5 |
| Flourish 30726939 (income growth by parliament) | 1 | `real_income_growth`, percent | none | 2024–2029: 0.4 |
| Flourish 30726047 (announced tax changes) | 1 | `revenue_change`, percent | new proposed `ab2026__package_ifs_announced_tax_changes` | Budget 2026: 0.2 |
| Flourish 30727239 (higher-rate taxpayers) | 15 | `taxpayer_count`, persons | none | 2026–27 freeze, March forecast: 8,890,000. 2030–31 freeze, October forecast: 10,800,000. 2030–31 with CPI uprating: 4,776,000 |

Of the 57 rows, 12 are IFS's own calculations and 45 restate OBR forecasts. The family total is 48 own and 96 restated.

## Figures not staged

**The two pages: 11 figures.**
- 3% of GDP on defence (twice on the initial response, three times in the remarks), 3.5% by 2035 and 2.7% from next year to 2029–30: government targets (rule 8).
- £100, once per page: the payment's design, which stays in the 80% rows' `reform_hint`.
- "property values 35 years out of date": describes council tax, estimates no Budget effect.
- "100% of business rates": the design of a devolution plan.

The pages' other numbers aren't estimates: dates, horizons, the rule year 2029–30 (which the headroom rows carry as `fy`), "10 year plan", G7, "two big problems" and "one-off". "Almost halved" prints no number, and no row invents one.

**The seven charts: 256 of 302 non-null data cells.**

| Chart | Cells left out | Why |
|---|--:|---|
| 30734907 | 84 | Earlier decades (77), the 2020s years 0–5 (6), and the year-5 cell where the forecast line joins (1) |
| 30726471 | 2 | 2025–26, 47.4 in both forecasts |
| 30726788 | 30 | Earlier fiscal events |
| 30726917 | 2 | The 2025–26 base of 100 |
| 30726939 | 11 | Earlier parliaments |
| 30726047 | 84 | Earlier fiscal events |
| 30727239 | 43 | The "Current plans" history (36); the two freeze series' 2025–26 cells, which equal current plans (2); and the CPI-uprating path for 2021–22 to 2025–26 (5) |

Also not staged: the headroom chart's "2010s average: 0.9% of GDP" reference line, and the lead sentences, which aren't a manifested primary and whose estimates repeat staged cells.

**Unreached:** nothing. I made no request to ifs.org.uk, so each data item's chart comes from its public Flourish embed. The explainer and the fiscal devolution comment hold nothing to stage, per the browser README.

## Judgement calls

- **£8bn and £4bn** share the government-decisions key with the direct-effects component. They match OBR's 7.6 and 3.5. Neither the total effect (6.3 and 7.0) nor Table 6.1 (7,595 and 2,475) matches both years.
- **£13bn and £15bn** are restated OBR figures, before and after the Budget's measures, at the page's rounding. The OBR family has 12.5 and 14.5.
- **"2030-21"** stays as printed, with no fiscal year, medium confidence, and a note that it's a typo.
- **£11bn** imports no year from Boileau's slide 4.
- **25% and 40%** are restated `administrative_fact`, like the Boileau slide 11 rows.
- **Attribution.**
  - Own: the decade chart, as the addendum directs, and the parliament and tax-change charts, whose footers credit IFS calculations.
  - Restated: the other four charts.
  - The deficit chart prints no source. Its title and series name the March and October 2026 forecasts, and its 2029–30 October cell (−14.5) equals OBR's £14.5bn headroom.
- **Units and periods.**
  - Headroom stays as the served fraction (`share`).
  - Both indices use a proposed `index` unit, not `index_0_1`.
  - Taxpayer cells are multiplied by 1,000, because the lead's 10.8 million is the 10800 cell.
  - The decade chart's years 6–10 are read as 2026–2030, at medium confidence.
- **The tax chart's 0.2** gets a new proposed key, because one rounded number can't tie it to Table 6.1 or OBR scope.
- **The CPI-uprating counterfactual** before 2026–27 is left out, so the three scenarios cover the same forecast years. This is the closest call.
- **Cleanup of the earlier draft.**
  - Flourish locators now use one format.
  - Notes are in active voice and claim nothing the chart settings don't show.
  - The manifest uses `doc_type "flourish_json"` and records each fetch time.
  - NOTES.md restores the first lane's per-deck record word for word.
  - The proposed-metrics table is regenerated; the old one listed metrics that rule 8 had already dropped.

## Verification

| Check | Result |
|---|---|
| Contract checker | `uk_ifs_ab2026: 144 rows, 0 problems` |
| `stage.py`, run twice | Before `2e8b2dc5a85bb66f…`; after `40331bc6beb36fc78d2e10731730c4c8a15942d4419bd840d0cebc95988e6125` both times |
| First 87 rows | Identical to the checkpoint, byte for byte (3,247 fields, 0 differences); manifest lines 1–5 identical |
| New rows | A script re-opened all 57 at their locator: the text line, or the embed's cell read as served text. It checked hash, quote, value, sign, unit, period and forecast vintage: `57 pass, 0 fail`. Planted errors of nine kinds were each caught |
| Cell accounting | `302 non-null cells: 46 staged, 256 excluded` |
| `pytest -n 4`, exact command | `INTERNALERROR> ModuleNotFoundError: No module named 'be'`: the conftest builds the full database, which needs folders this sparse worktree doesn't check out |
| Same command with `--noconftest` | `52 passed`. Neither test file uses the database |
| PROPOSED_KEYS.md, then `--check` | `matches the families`; 84 keys on 958 rows; only the IFS entries change |
| COUNTS.json, then `--check` | `matches the families`; only the IFS entry and the two totals change |

Scripts and outputs are in the git-ignored `.ab2026-primaries/uk_ifs_ab2026/a3/`.

`git status --short`, against the auto-commit:
```
 M sources/harvest-uk-ab2026-2026-10-29/COUNTS.json
 M sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026/NOTES.md
 M sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026/claims_staged.jsonl.gz
 M sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026/manifest.jsonl
 M sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026/stage.py
```
PROPOSED_KEYS.md doesn't show because my regenerated copy matches the auto-committed one. Against the checkpoint, six files differ, with `stage.py` new.

HANDED TO the PR #231 coordinator.