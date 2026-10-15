# Construction revisions for new engines

The five event registries freeze constructions authored against
policyengine-uk 2.89.2. When a certified variant runs them on another engine,
`pipeline/audit_uk_event_premises.py` records what each executed world holds
at every annual lookup and whether the construction's premises still hold.
This document reviews the premises that changed and proposes revisions.

**Every revision below is proposed, not applied.** Running a revised
construction changes the experiment, which is a methodology call under cos
decision d1344. Until that is ruled, variant reruns execute the frozen
registries unchanged, and the release diff carries the premise changes as
construction flags.

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

**What the frozen construction now measures.** The construction reverses the
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

**Proposed revision.** Extend the reversal to CY2024 at the pre-announcement
rates (`basic_rate` 0.10, `higher_rate` and `additional_rate` 0.20 from
1 January 2024), keeping CY2025 onwards unchanged. On 2.125.1 that scores
the blended FY2024–25 increase. On 2.89.2 the CY2024 worlds would remain
identical because current law already holds those rates. Editing the frozen
registry nevertheless changes its SHA-256: every legacy comparison must be
regenerated along with the registry-bound artifacts and staging receipts
before the comparison provenance can verify again
(`pipeline/compare_uk_event.py`, `load_verified_comparison`). This remains
proposed under cos decision d1344; no registry or activation rule changes
are applied here.

## Notes that state 2.89.2 facts

These are not construction changes; the comparison now labels them.
`compare_uk_event.construction_note` prints the authored note on another
engine as "Authored against policyengine-uk 2.89.2" and omits the
2.89.2-only corrections, and the review diagnoses become
`prior_diagnoses` with `status: not_reverified`.

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
records an independent investigation of the largest legacy-to-6.2.6 moves. It
attributes both structural moves to upstream fixes: the Class 2 abolition's
Class 4 head to policyengine-uk #1884 and #2058, and the HICBC Child Benefit
head to #2140, which models payment resuming once the charge is zero (an
assumption, since a real claim has to be restarted). It reads the AB2024 CGT
decline (×0.51) as a smaller capital-gains base in the new population rather
than day-weighting, and keeps the pooled-gains limitation. It finds the
private-school VAT replay figure consistent with a zero dedicated baseline
head; it does not show £2.0bn missing from total baseline VAT, because generic
VAT is calibrated to whole OBR receipts. It names LHA (×2.45) as only partly
attributed. These are its findings, not re-verified here.
