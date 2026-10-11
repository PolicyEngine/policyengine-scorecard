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

One premise changed: how 2.125.1 annualises the AB2024 Capital Gains Tax
rates.

| Measure | Premise | 2.89.2 | 2.125.1 |
|---|---|---|---|
| `autumn_budget_2024__capital_gains_main_rates_and_reliefs` | `annual_value_matches_30_april_sample` | holds | fails |

## AB2024 Capital Gains Tax main rates

**What changed in the engine.** In 2.125.1,
`parameters/gov/hmrc/cgt/basic_rate.yaml` (and the higher and additional
rate files) date the 18%/24% rates from 30 October 2024 and set
`metadata.fiscal_year_blend: true`. `utils/parameters.convert_to_fiscal_year_parameters`
day-weights such parameters across the fiscal year (6 April–5 April,
`fiscal_year_average`) instead of sampling 30 April. 2.89.2's conversion
reads no such metadata and sampled 30 April; its raw schedule started the
higher rates on 6 April 2025.

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
the blended FY2024–25 increase; on 2.89.2 it would remain inert for CY2024
because current law already holds those rates, so the change is safe for the
legacy record. Remove the measure from `DOCUMENTED_ANNUAL_ACTIVATIONS` only
for variants whose engine blends these paths. Proposed; running it changes
the construction and waits on d1344.

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
| `class4_threshold_indexation_from_2027` | resolved (limits held at £12,570/£50,270 through 2028) |
| `uc_lcwra_protection_stops_at_2030` | persists |
| `employer_nics_state_pension_age_exemption` | resolved (employer NICs at age 70 equal those at 45) |
| `pension_taper_omits_employer_contributions` | persists |
| `annual_allowance_charge_single_marginal_rate` | persists |

A status describes the case's own synthetic observation. It does not size a
national effect or explain a replay movement on its own.
