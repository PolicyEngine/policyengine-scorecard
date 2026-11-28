# Fiscal Lab Memo Bill Scores

Fiscal Lab on Capitol Hill released its Memo Bill Scores on 2026-11-24 with
its "open, fast scores" announcement. The page scores 110 bills and proposals
from the Cost-of-Living Healthcare Working Group memo. For each one it gives a
ten-year effect on federal deficits, FY2027-2036, against current law (CBO's
February 2026 baseline). 69 of them also get a low and a high case. Fiscal
Lab's models are not public; its score documents are available on request.

## What this source stages

There are 248 claims on `primary_deficit_change` in USD:

- 110 central cases.
- 69 low cases and 69 high cases, under `conditions.scenario`.

Every claim is a FY2027-2036 total (period 2036, `window_kind` total). Every
claim is held out, sits on the null current-law baseline, and has
`publication.publish_without_result`, so the app shows it before any
PolicyEngine run.

The figure covers direct spending and revenues. Fiscal Lab shows interest
and spending subject to appropriation separately, and neither is part of the
figure. A PolicyEngine counterpart has to leave both out as well.

## What is committed and what is not

Fiscal Lab's Terms of Use (section 5, effective 2026-11-16) allow sharing
links to its public pages and quoting short excerpts with attribution. They
reserve its publications and ask anyone republishing to contact it first.

Nothing raw is committed: not the page, not the CSV, not the announcement
and not the terms. Of Fiscal Lab's text, the repository holds:

- each bill's title and its model and effect labels;
- the CSV's column headings, and a few short phrases the adapter matches in
  the page's bill notes to read each bill's version and Congress;
- the titles of the memo, the page and the announcement, and the short terms
  quote, in `source.json`.

The CSV ends with a source line, which the adapter reads from the fetched
page's own code at build time, so the line is not in this repository. The
changelog check reads the entry's structured figures, not its sentences.

- `source.json` records each raw file's URL, fetch date and SHA-256 with
  `stored_in_repo: false`, following `sources/cbo-pl119-21`.
- `adapter.py fetch` replaces the page in the git-ignored `raw/` only when
  it matches the pinned hash. The URL serves only Fiscal Lab's latest build, so
  a page that differs is saved beside the pinned copy, named by its hash,
  and the pinned copy is left as it was. Each fetch stages its page in a file
  of its own, so overlapping fetches cannot swap pages. The staging file has
  a short fixed name, so it fits wherever the page's own name does. The copy
  kept beside the pinned one is 13 bytes longer than the page's name and is
  never cut short. Where the filesystem refuses that name as too long, the
  fetch stops with an error, removes its staging file and leaves the pinned
  copy as it was.
- `adapter.py build` checks the page against its pinned hash and rebuilds the
  page's own CSV byte for byte. The rebuilt CSV is checked against the hash
  of the copy captured from the page, but it is not written.
- `build` then writes `data/externals/fiscal-lab-memo-scores.json`.

That extract carries the following for each bill:

- identifiers: slug, bill number, Congress, version and the bill's title;
- Fiscal Lab's model labels and effect label;
- the CSV's printed total, plus the low and high cases where the bill has them;
- a link to the bill's own page on the dashboard, and the congress.gov link
  the page gives for it.

H.R. 4849 also carries its 3 superseded values (see Vintage), so the extract
holds 251 figures: 248 current and 3 superseded.

The extract carries no annual paths, components, coverage tables, State
tables or CBO comparison runs.

Publishing even these 251 figures is a judgment call against the terms.
Max made it on 2026-11-26 (decision d3450): publish them in this public
repository.

## Rounded ranges

On 6 bills the CSV's low and high are the bill's score-table total rounded
to $0.1 billion, not the total itself: H.J.Res. 189, H.R. 3521, H.R. 5343,
H.R. 7920, H.R. 7961 and S. 1096. The extract keeps the CSV's values, because
the page's headline range prints the same ones. The three-decimal total
exists only in the page's embedded data, since the page's own table prints
one decimal. The extract flags these bills `range_rounded`. Their low and
high claims carry a note saying so, and their source column names the
rounding, which the app shows.
`adapter.py` QC 9 checks every bill's table total against its central figure
and range, and fails if the set of rounded bills moves.

## Vintage

The page was rebuilt on November 25. Against the November 21 build that was
released on the 24th, only H.R. 4849's score changed: Fiscal Lab added
sections it had left out, as its changelog records. The extract stages the
current build. H.R. 4849's rows carry the released values under `superseded`.
`adapter.py build --release <November 21 page>` checks those values against
the pinned November 21 page and against the changelog's before-and-after
sentence.

## PolicyEngine statuses

`pe_status.json` judges each bill against the policyengine-us 2.2.2 source.
No PolicyEngine number is recorded for any bill. There are two statuses:

- `not_computed`: the household model has levers for the bill's main
  provisions, so a run could be built. The bill gets no result row, and the
  feed shows the synthetic not_computed status.
- `pe_gap`: the household model and its default dataset offer no lever for
  the provisions that carry the bill's score. For most of these bills
  (`none`) there is no lever at all, for example for provider payment rules,
  drug pricing, Medicare program design and regulatory or reporting changes.
  For 9 (`partial`) there are levers for only a minority of the score. The
  bill gets a valueless `pe_gap` result
  row with the reason. It gets no diagnosis, because a gated `pe_gap`
  diagnosis needs a citable issue, and none is filed.

The classification ran as a workflow against the 2.2.2 source. Each bill got
one classifier and one adversarial verifier. The verifiers disagreed on two
bills, and both were settled by hand:

- H.R. 711 went to `pe_gap`. Its score is a premium response whose size
  Fiscal Lab does not publish.
- H.R. 9257 stays `pe_gap` partial. Fiscal Lab states its benchmark premium
  rise, the same treatment as H.R. 3762 and H.R. 6423.

The reasons in `pe_status.json` are in our own words, not copied from Fiscal
Lab, and quote none of its dollar figures. Both the status builder and the
ingest reject a reason with a dollar sign, the words million, billion,
trillion, dollars or USD, or a figure in bn, mn, B or M. Program names that
look like figures, such as 340B and H-1B, are exempt. That check catches a
quoted figure, not a paraphrase, so the reasons were also reviewed by hand.

A Fiscal Lab assumption counts as a lever only when a reform can impose it
through policyengine-us. A stated premium rise counts, applied to the
benchmark the premium tax credit reads (`slcsp`). That moves H.R. 9941 and
H.R. 3415 to `pe_gap` partial, because each has a premium tax credit line
behind a premium rise that Fiscal Lab states. The rise has to go on `slcsp`,
not on the benchmark parameter `state_rating_area_cost` or on
`slcsp_age_0`. In 2.2.2 both also feed the Medicaid cost index
(`medicaid_slcsp_cost_index`), so changing them would move PolicyEngine's
Medicaid cost as well. The reasons for the seven bills that use this lever
say so.

The test is whether a reform can apply the assumption as Fiscal Lab states
it to an amount PolicyEngine computes, as with a uniform percentage on
`slcsp`. A take-up response fails it. It means choosing which eligible people
or units newly enroll, and 2.2.2's take-up flags (on a person, tax unit or
SPM unit) have no rate parameter or enrollment model to choose them, so a
run would rest on an assignment PolicyEngine does not make. H.R. 3947,
H.R. 3907, H.R. 4641 and H.R. 10045 therefore stay `pe_gap` none.

The independent review of PR #261 found reasons that misstated how 2.2.2
works, and a sweep of all 110 reasons found more of the same kind. After its
first round, 30 reasons were reworded against the source, and 2 more,
H.R. 3415's and H.R. 8375's, only had their files corrected:

- Medicaid has two match rates in each state, not one: ACA expansion adults
  get one national expansion rate, and every other enrollee gets the state's
  regular rate. Cost per enrollee is not a state average either. 2.2.2 splits
  each state's spending total across enrollees by a benchmark-premium cost
  index (age, rating area and, where it applies, family tier).
- Each enrollee's Part B premium is computed: the standard premium plus the
  income-related adjustment, less Medicare Savings Program coverage. Only the
  standard premium is a parameter, and it does not follow Part B spending.
- Medicare spending per enrollee is the per-capita parameter
  (`medicare_gross_cost`). The reasons now cite that, not `medicare_cost`,
  which nets out each person's premiums and feeds no aggregate.
- H.R. 3257's match lever applies to every enrollee in PolicyEngine's adult
  expansion category, which also holds Wisconsin's waiver adults and some
  parents that States match at the regular rate. H.R. 6455's lever needs
  Fiscal Lab's stated Part D and Medigap averages, because 2.2.2 has no
  input for those premiums alone.
- H.R. 9833 moved from `pe_gap` partial to none. Its score is one
  dental-wraparound line, and the only lever would price it as full CHIP
  coverage.

No other bill's status or scope changed.

The review's second round found four more misstatements. A sweep of every
reason on a bill with an employer exclusion or Basic Health Program line found
the first two elsewhere too. 16 reasons were reworded, and no status or scope
changed:

- A structural reform can move pay from taxable wages into employer-paid
  premiums, which never enter taxable income, so the employer exclusion is
  not missing from the rules. It has no base: 2.2.2's certified default
  dataset, a Microcosm build, carries no employer-paid or pre-tax premium
  amounts. A lever needs its amount in that data, so a stated employer
  premium rise is not one. The reasons for H.R. 5509, H.R. 5448, H.R. 3415,
  H.R. 9257, H.R. 7227, H.R. 9941, H.R. 3762, H.R. 6423, H.R. 3069,
  H.R. 7023 and H.R. 9702 now place that gap in the data.
- The Basic Health Program has a lever of its own: its premium adjustment
  factor, a parameter, scales the program's reference premium without moving
  the Medicaid cost index. H.R. 3415 and H.R. 9257 now name it.
- The federal Medicare Savings Program cost (`msp_federal_cost`) leaves out
  anyone enrolled in full Medicaid, so a run of S. 4886 would not count every
  newly eligible person.
- The premium tax credit's income bracket is national, so H.R. 3257's
  below-poverty credit needs a structural override limited to states that
  have not expanded Medicaid.
- H.R. 4206 now names Parts A and B, since for Part D 2.2.2 computes only
  the income-related surcharge. H.R. 711 gives the selected-plan ratio on the
  benchmark silver premium, and H.R. 6609 adds the family tier to the cost
  index.

The third round found two more omissions, and a sweep of every bill with a
Basic Health Program line found three of the same kind. 5 reasons were
reworded, and no status or scope changed:

- 2.2.2's Basic Health Program payment uses the credit's contribution
  percentage and income bracket, so credit parameters reach it. Its reference
  premium reads `slcsp_age_0` directly, though, so a discount placed on
  `slcsp` does not reach it, and the premium adjustment factor carries one
  there. H.R. 9702 now names that factor.
- Medicare for Kids now names the program's minimum age as its lever, and
  H.R. 1589 and H.R. 9432 name its immigrant status list.
- H.R. 3069's exclusion line covers payroll tax too, which has a pre-tax
  deduction list of its own (`fica_pre_tax_contributions`). The reason now
  names both lists.

The result is 9 bills `not_computed`, all partial, and 101 `pe_gap` (92 none,
9 partial). A partial `not_computed` bill is one where PolicyEngine's levers
carry most of the score but not all of it, so a run would leave a named
remainder out.

H.R. 4849 and H.R. 1428 stay `not_computed` in every case.
[PolicyEngine/fiscal-lab-comparison](https://github.com/PolicyEngine/fiscal-lab-comparison)
is replicating their named provisions:

- H.R. 4849's coverage provisions, 2027-2036;
- H.R. 1428's FPG × 1.97 from 2030 and its SNAP deduction from FY2031.

Their counterparts come from that repository once its results pass review,
and they cover only those provisions, not the whole bill.
