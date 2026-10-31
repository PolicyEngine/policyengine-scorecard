# Construction revisions for new engines

The event registries freeze constructions authored against
policyengine-uk 2.89.2. When a certified variant runs them on another engine,
`pipeline/audit_uk_event_premises.py` records each world's intended value
at every annual lookup and whether the construction's premises still hold.
The executor separately reads the processed values from each simulation's
own parameter tree and refuses differences (see [RELEASE_REPLAY.md](RELEASE_REPLAY.md)).

**The CGT revision below is selected when the installed rate parameters
carry `fiscal_year_blend`; the frozen registries remain unchanged.** It is
the W6 methodology choice under cos d1344 (Max, 15 October 2026): choose the
reading supported by the law, record exceptions, and obtain agreement from
independent review. The revision is stored beside the registries in
`data/uk/events/construction_revisions.json`; its SHA-256 is bound in the
run manifest and construction premises. Selection reads installed engine
metadata, never its version string. A failed premise without a selected
revision remains a construction revision candidate.

`data/uk/events/construction_revisions_enacted.json` holds the revisions for
engines that have since enacted a measure; see
[Summary for 2.132.6 → 2.151.0](#summary-for-21326--21510). A run binds each
revision to the SHA-256 of the file holding it, so no file changes once a
sealed namespace records it. Each later revision goes in a later file, and
every sealed namespace keeps validating. A later file's revision can supersede
an earlier one for new runs, and a sealed run keeps the revision it recorded.
Selection reads either metadata or current-law values in the installed engine,
never its version string.

Inputs (both parameter-tree only; no dataset or simulation):

* `results/uk/events/CONSTRUCTION_PREMISES.json`: policyengine-uk 2.89.2
  (policyengine 5.0.2, core 3.27.1), the engine the registries were authored
  against.
* `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/CONSTRUCTION_PREMISES.json`:
  policyengine-uk 2.125.1 (policyengine 6.2.6, core 3.33.0).

Regenerate either with
`PYTHONPATH=. python -m pipeline.audit_uk_event_premises --all --expect-engine <version> --output <path>`
in that engine's environment; `--check` compares with the committed bytes.

## Summary for 2.89.2 → 2.125.1

Of the 16 executable constructions, 15 keep every premise: the two forward
deltas still change current law, every reversal still differs from current
law in an in-force year, and every authored construction re-derives the same
values from 2.125.1's parameters. That includes the counterfactuals derived
from live engine values: the SB2023 UC childcare caps, the SS2025 UC standard
allowance and the SS2025 UC health element.

One metadata premise changed: how 2.125.1 annualises the AB2024 Capital
Gains Tax rates. The historical key `annual_value_matches_30_april_sample`
is retained for legacy receipt compatibility. It checks whether an in-force
touched path carries `fiscal_year_blend` or `preserve_calendar_dates`
metadata read by the installed converter; it does not compare values.
Metadata can select a different annualisation policy even when that year's
annual and raw 30 April values happen to be equal. The recorded
`current_law` and `raw_30_april` values give separate numerical evidence.

| Measure | Premise | 2.89.2 | 2.125.1 |
|---|---|---|---|
| `autumn_budget_2024__capital_gains_main_rates_and_reliefs` | `annual_value_matches_30_april_sample` | holds | fails |

## AB2024 Capital Gains Tax main rates

**What changed in the engine.** In 2.125.1,
`parameters/gov/hmrc/cgt/basic_rate.yaml` (and the higher and additional
rate files) date the 18%/24% rates from 30 October 2024 and set
`metadata.fiscal_year_blend: true` (`policyengine_uk/parameters/gov/hmrc/cgt/basic_rate.yaml:8-14`
and `higher_rate.yaml:8-14`). `utils/parameters.convert_to_fiscal_year_parameters`
day-weights such parameters across the fiscal year (6 April–5 April,
`fiscal_year_average`, `policyengine_uk/utils/parameters.py:28-54,106-119`
in 2.125.1) instead of sampling 30 April. 2.89.2's conversion reads no such
metadata and sampled 30 April (`policyengine_uk/utils/parameters.py:39-45`);
its raw schedule started the higher rates on 6 April 2025.

**What the frozen construction measured.** The construction reverses the
announced rates to 10%/20% from 30 October 2024; the executor moves that to
the next 1 January annual lookup (`compute_uk_event.annual_reform`), so the
reversal applies from CY2025.

| CY | Path | 2.89.2 current law | 2.125.1 current law | Reversal world (both) |
|---|---|---:|---:|---:|
| 2024 | `basic_rate` | 0.10 | 0.13463 | current law |
| 2024 | `higher_rate`, `additional_rate` | 0.20 | 0.21732 | current law |
| 2025 | `basic_rate` | 0.18 | 0.18 | 0.10 |
| 2025 | `higher_rate`, `additional_rate` | 0.24 | 0.24 | 0.20 |

On 2.89.2 the CY2024 worlds were identical because current law itself had no
2024 increase; the registry records the FY2024–25 row as a documented annual
activation (`stage_uk_event.DOCUMENTED_ANNUAL_ACTIVATIONS`). On 2.125.1 current
law does carry a 2024 increase (0.1346 = 0.10 × 207/365 + 0.18 × 158/365),
but the reversal leaves it in both worlds. The frozen construction therefore
omits a part-year FY2024–25 effect that the new engine models.

That description applies to the annual-lookup route in 2.125.1. It does not
describe construction-time reform dictionaries in 2.130.1. In that engine,
`utils/dated_reforms.read_reform_dict` reads a `start.stop` interval as a
statutory-timeline assignment; `CountryTaxBenefitSystem._rebuild` writes the
assignment before `process_parameter_tree` reannualises it. Thus a reversal
starting on 1 January 2025 also changes 95 days of FY2024–25. Its processed
2024 baseline rate would be 0.11380821917808219 (basic) or
0.2069041095890411 (higher/additional), rather than the intended unchanged
2024 current-law values above. An annual-lookup audit alone could report
equal worlds while this route executes different values. The processed-value
check refuses that mismatch.

**Law and d1344 choice.** [Finance Act 2025, section 7(1)(b) and (3)](https://www.legislation.gov.uk/ukpga/2025/8/section/7)
raises the main rates from 10%/20% to 18%/24% for disposals on or after
30 October 2024. This was verified against the [enacted Act](https://www.legislation.gov.uk/ukpga/2025/8/pdfs/ukpga_20250008_en.pdf),
and the 2.125.1 installed files and 2.130.1 wheel files cite section 7.
The [annualisation contract](contracts/annualisation_fy_start_year.v1.json)
keeps the engine's own `fiscal_year_blend` treatment for CGT, although CGT
is charged on transactions. Under that recorded exception, period 2024
takes the day-weighted FY2024–25 rate in both worlds. There are 207 days
from 6 April to 29 October 2024 and 158 from 30 October to 5 April 2025.

**Selected revision.** On engines carrying `fiscal_year_blend` on the CGT
rate files, hold the baseline's pre-announcement rates (`basic_rate` 0.10;
`higher_rate` and `additional_rate` 0.20) through the whole of FY2024–25
and later years in the construction's existing window. The executor uses
the engine's actual reform route to express those annual values. On a
statutory-reprocessing route the interval starts on 6 April 2024, so it
does not alter FY2023–24. On an annual-lookup route the override includes
1 January 2024. Staging reads the selected revision's activation of
FY2024–25, comparison notes identify the revision, and the release diff
flags the construction change.

The check's expected 2024 records are below. Baseline means the reversal
world; reform means current law. Each cell gives intended = processed.

| Engine route | Basic baseline | Basic reform | Higher/additional baseline | Higher/additional reform |
|---|---:|---:|---:|---:|
| 2.89.2, sampled annual lookup; no revision | 0.10 | 0.10 | 0.20 | 0.20 |
| 2.125.1, annual lookup; blend revision | 0.10 | 0.13463013698630139 | 0.20 | 0.21731506849315071 |
| 2.130.1, statutory reprocessing; blend revision | 0.10 | 0.13463013698630139 | 0.20 | 0.21731506849315071 |

The latter two current-law rates are 0.10 × 207/365 + 0.18 × 158/365
and 0.20 × 207/365 + 0.24 × 158/365, within floating-point rounding.
2.89.2 has no blend metadata: the revision and new artifact fields are
omitted, and legacy registries, namespaces and artifacts keep their bytes.

**Verification and limits.** Parameter-only reads of the installed 2.89.2
and 2.125.1 trees established the table's current-law values. The 2.130.1
route and rate files were read from its PyPI wheel on 15 October 2026
(wheel SHA-256 `f8b1b8b917c9297ff66937811dbebd9a62d3b1796ce894c326e98051cac4c873`).
Its table row is the route-derived expectation, tested with fakes, rather
than a local simulation observation; CI and the receiver must verify the
real installed 2.130.1 run. No microsimulation was run for this change.
The unreversed reliefs remain: this revision changes annualisation of the
three main rates and does not implement the full rates-and-reliefs package.
The limitation that this revision also stated about pooled gains was wrong;
see [AB2024 CGT limitation](#ab2024-cgt-limitation).

## Summary for 2.132.6 → 2.151.0

The qualification of policyengine.py 6.11.1 (request `d1e672fe…`, run
41143889866) ran on policyengine-uk 2.151.0, and that run's results (#238) did
not land because of what this section corrects. Four constructions newly failed
a premise, beside the CGT annualisation premise recorded above, and two rows
stated limitations the engine does not have.

| Measure | Failed premise on 2.151.0 | Treatment |
|---|---|---|
| AB2024 `sdlt_additional_dwelling_surcharge_2pp` | `forward_delta_changes_current_law` | `ab2024_sdlt_surcharge_in_current_law.v1` |
| SS2025 `uc_standard_allowance_above_inflation` | `authored_construction_reproduces` | `ss2025_uc_uplifts_in_current_law.v1` |
| SS2025 `uc_health_element_freeze_and_new_claimant_cut` | `authored_construction_reproduces` | Candidate |
| SB2023 `uc_childcare_cap_increase` | `authored_construction_reproduces` | Candidate |
| AB2024 `capital_gains_main_rates_and_reliefs` | None new; its limitation misdescribed the engine | `ab2024_cgt_fiscal_year_blend.v2` |

### AB2024 SDLT surcharge

**What changed in the engine.** 2.132.6's
`parameters/gov/hmrc/stamp_duty/residential/purchase/additional/rate.yaml`
holds 3/5/8/13/15%. 2.151.0's file dates 5/10/15/17% from 31 October 2024 and
7% from 1 April 2025, and cites Finance Act 2025 ss. 50 and 51. The frozen
forward delta writes those same rates, so its two worlds matched and the row
fell from £1.87–2.15bn a year on 6.11.0 to zero in 2025–2029.

**Law.** [Finance Act 2025, section 51](https://www.legislation.gov.uk/ukpga/2025/8/section/51/enacted)
substitutes the additional-dwellings table for transactions on or after
1 April 2025: 5% to £125,000, 7% to £250,000, 10% to £925,000, 15% to
£1,500,000 and 17% on the remainder. [Section 50](https://www.legislation.gov.uk/ukpga/2025/8/section/50/enacted)
covers 31 October 2024 to 31 March 2025. The rates it replaced are the
3/5/8/13/15% of 2.132.6's file.

**Selected revision.** `select_revision` reads processed current law at
1 January 2025. When all five rates equal the enacted ones, the revision
replaces the forward world with a reversal: the baseline world holds the prior
rates over the delta's own windows, and the certified world is the reform
world. The measure's sign stays the same, and the run gains no simulation. The
revision keeps annual windows, because these rates carry no `fiscal_year_blend`.
On 2.132.6 the rates differ, `select_revision` returns nothing and the frozen
delta runs. Artifacts and staged rows report `reversal_on_certified_world` when
a run selects the revision. The condition reads only those five rates, so a
later engine that keeps them and changes how a lookup reaches them would need a
new revision.

| Annual lookup | Current law (reform world) | Baseline world |
|---|---|---|
| 2024 | 3%, none, 8%, 13%, 15% | Current law |
| 2025 to 2029 | 5%, 7%, 10%, 15%, 17% | 3%, 5%, 8%, 13%, 15% |

**Limit.** FY2024-25 stays unscored, as in the frozen construction. These
rates first differ at the 2025 annual lookup, so the part year from
31 October 2024 has no effect here.

**Row size.** The revised row measures a different base from 6.11.0's forward
delta. In 2.132.6, `additional_residential_property_purchased` charged a
buyer's whole stock of other residential property. In 2.151.0 it holds an input,
nil unless set directly or imputed by a dataset, and 2.134.1's changelog entry
names that change. A one-year Modal run on the 6.11.1 candidate scored the
reversal at £0.98bn in 2025, where 6.11.0 scored £1.87bn. The Microcosm build
moved between the two releases as well, and these runs do not separate the
causes.

### SS2025 UC standard allowance

**What changed in the engine.** 2.132.6's `standard_allowance/amount.yaml`
uprates by `gov.benefit_uprating_cpi`. 2.151.0's uprates by
`gov.economic_assumptions.indices.uc_standard_allowance`, which
`rebalancing/create_standard_allowance_uprating.py` builds from that benefit
index and the uplift in `rebalancing/standard_allowance_uplift.yaml`, citing
[Universal Credit Act 2025, section 1(4)](https://www.legislation.gov.uk/ukpga/2025/22/section/1/enacted).
The registry's leg "the certified world omits legislated 2027-29 above-inflation
uplifts; standard_allowance_uplift is unused" no longer describes the engine
that ran.

**Selected revision.** This revision selects on the `uprating` metadata of the
four amounts and changes neither world. It restates the note and the legs the
comparison prints. Re-authoring on 2.151.0 raises the frozen counterfactual by
1.17–1.27% from 2027, so later-year effects carry that gap as well as the
uplifts. The revision's limitation says so, and
`authored_construction_reproduces` keeps recording it. Its condition reads only
the index name, so a later engine that keeps the name and changes what the index
applies would need a new revision.

### AB2024 CGT limitation

`ab2024_cgt_fiscal_year_blend.v1` states: "The engine pools gains rather than
distinguishing their statutory types." The 2.89.2 audit found that, and the
revision carried it forward without a check. `capital_gains_tax.py` charges
four schedules in the 2.130.1, 2.132.6 and 2.151.0 wheels, the three engines
that have run v1 or could select it. The national Microcosm build that 6.11.1
ran fills two of them: 4,220 person records hold residential property gains
and 1,702 hold relief gains, out of 33,985 with gains.

The sentence therefore misdescribes the engine in the namespaces that record
v1: `pe6.5.0_uk2.130.1…`, `pe6.9.0_uk2.130.1…` and `pe6.11.0_uk2.132.6…`.
Those namespaces keep their sealed bytes, and this section corrects them.

`ab2024_cgt_fiscal_year_blend.v2` supersedes v1 for new runs. It carries v1's
condition, windows, values and intent, so it builds the same worlds and moves
no number. It drops the sentence and states that the reversal moves the main
rates alone, while residential property gains, carried interest and relief
gains keep their installed rates in both worlds. It also states that the replay
leaves `gov.simulation.capital_gains_responses` at the engine's defaults.

Those defaults moved between the two most recent engines:
`gov.simulation.capital_gains_responses.elasticity` reads 0 on 2.132.6 and 1.0
on 2.151.0. The revision records the setting. It does not size what that move
adds to the row's fall against 6.11.0.

### Remaining candidates

Re-authoring on 2.151.0 gives 0.39–1.67% above the frozen health element in
2026–2029 and 3.5% above the frozen childcare caps in 2027 alone. Both rows
measure current law against an explicit frozen cash path, and neither states a
limitation that 2.151.0 contradicts, so both run as authored and stay
candidates.

## Notes that state 2.89.2 facts

These are not construction changes; the comparison now labels them.
`compare_uk_event.construction_note` prints the authored note on another
engine as "Authored against policyengine-uk 2.89.2" and omits the
2.89.2-only corrections, and the review diagnoses become
`prior_diagnoses` with `status: not_reverified`.

Frozen `missing_legs` carry the same label from the run that records
`missing_legs_statement` in `RUN_MANIFEST.json`. Earlier namespaces record no
such field and keep their sealed bytes, unlabelled. A selected revision can
restate the legs for the engine that ran, and those need no label.

* AS2023 Class 2 abolition: the "£3.15 for 2023-24" statement is a 2.89.2
  fact; 2.125.1's processed 2023 flat rate is £3.45. CY2023 is outside the
  6.2.6 variant's data years, so no 6.2.6 result depends on it.
* AB2024 SDLT surcharge: "the pin still has the 3% surcharge scale" also holds
  on 2.125.1 (rates 3/5/8/13/15% at every lookup), so the forward construction
  is unchanged.
* AB2024 private-school VAT: the lever is still 0 in every year on 2.125.1, so
  the forward construction is unchanged.

## Diagnoses re-verified on 2.125.1

`pipeline/diagnose_uk_event_models.py --reverify` reruns the ten measured
candidates on the installed engine; results are in the variant namespace's
`MODEL_DIAGNOSTICS.json`.

| Candidate | 2.125.1 status |
|---|---|
| `carers_allowance_earnings_test_absent` | persists |
| `cgt_main_rate_commencement` | resolved (the blend above) |
| `sdlt_additional_home_hike_absent` | persists |
| `private_school_vat_current_law_lever_zero` | persists |
| `dividend_band_threshold_lag` | persists |
| `class4_threshold_indexation_from_2027` | resolved (limits held at £12,570/£50,270 in 2027) |
| `uc_lcwra_protection_stops_at_2030` | persists |
| `employer_nics_state_pension_age_exemption` | resolved (employer NICs at age 70 equal those at 45) |
| `pension_taper_omits_employer_contributions` | persists |
| `annual_allowance_charge_single_marginal_rate` | persists |

A status describes the case's own synthetic observation. It does not size a
national effect or explain a replay movement on its own.

The Class 4 fix is the 2027-04-06 entry, whose reference cites the Autumn
Statement 2022 freeze to April 2028
(`policyengine_uk/parameters/gov/hmrc/national_insurance/class_4/thresholds/lower_profits_limit.yaml:67-74`
in 2.125.1). The 2028–2030 entries cite Budget 2025's later freeze to 2031
(`lower_profits_limit.yaml:75-110`). For the AS2023 and SB2024 replays, those
later entries are a baseline-vintage difference from 2028, separate from
the correction observed by the 2027 predicate.

## Independent investigation of the largest moves

[`research/triage_6.2.6_vs_legacy.md`](research/triage_6.2.6_vs_legacy.md)
records an independent investigation of the largest legacy-to-6.2.6 moves.
Its headline: both structural moves are upstream fixes, the other large
moves are best explained by population differences, and the certified pair
keeps material current-law defects, so a smaller replay figure does not
establish that a costing is correct. Its findings, not re-verified here
except where noted:

* Class 2 abolition: the Class 4 head moves because of policyengine-uk #1884
  and #2058.
* HICBC: the Child Benefit head moves because of #2140. In the installed
  2.125.1 (`variables/gov/hmrc/child_benefit.py:30-35`, verified here), an
  opted-out family stays opted out only while its charge share is at least
  `gov.hmrc.child_benefit.opt_out_charge_share`, which is 1 and documented
  as a behavioural assumption; payment therefore resumes as soon as the
  family is not fully charged. A real claim has to be restarted.
* UC childcare cap (×122.69, the largest move): the childcare-cost tail among
  reported UC families in the new population; eligibility fixes contribute an
  unsized share.
* AB2024 CGT (×0.51): a smaller capital-gains base, not day-weighting.
* Private-school VAT: the replay figure is consistent with a zero dedicated
  baseline head, and the dedicated statutory mechanism defect persists. It
  does not show £2.0bn missing from total baseline VAT: generic VAT targets
  whole OBR receipts, though whether that target includes private-school VAT
  is an inference and the overlap is unmeasured.
* LHA (×2.45): only partly attributed.
