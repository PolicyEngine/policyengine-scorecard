# Energy bills and the Autumn Budget 2026: comparables record

A backfill under the pre-publish comparables gate (docs/COMPARABLES.md). The dashboard was
published on 14 October 2026, before the gate existed. The search ran on 21 October 2026, a
week before the Budget, so no Budget-day costing exists yet.

## What is pinned

`analysis.json` pins 39 estimates from `PolicyEngine/uk-energy-autumn-budget` at `4d916d5`,
the commit behind the production deployment of 14 October 2026:

- for each option and year, the cost to government, the share of households helped and the
  average gain over all households (`src/data/options.json`);
- the reach of the Warm Home Discount top-up in 2026-27, 7.85m households (`options.json`);
- the average extra energy cost against April–June 2026 rates (`src/data/years.json`).

Both files match the run's receipt (`reproducibility.json`, 12 October 2026: policyengine
6.2.7, policyengine-uk 2.125.1, Microcosm UK 2024-25).

Some published figures are not pinned:

- The breakdowns by decile, household type and region. The search found no producer that
  publishes them for these options.
- The bill levels: a mean of £1,649 and £1,789, and a typical bill of £1,996 and £2,170. The
  vocabulary has no metric for an energy bill level, only `energy_bill_change`.
- The quarterly price path. It is the dashboard's input (Ofgem caps and forecasts), not an
  estimate.
- The poverty effects. They are in the results file but not on the page.

## What the search found

The search covered every UK producer and staged 30 claims from 11 producers.

| Producer | What was staged |
|---|---|
| Resolution Foundation | The targeted discount's cost, reach and average; the levies in total and one by one; the VAT rate's annual cost; a £570 Warm Home Discount increase |
| IFS | A permanent 0% VAT rate on electricity |
| Centre for British Progress | The remaining 25% of the Renewables Obligation (RO) and the Feed-in Tariffs (FiT), the option's exact scope |
| JRF | A wider levy scope; an EPG-style cap |
| Open search | DESNZ's Warm Home Discount caseload and the VAT cut's average saving; Good Energy's levy components and its £300 to Warm Home Discount recipients; wider-levy costings (MCS Foundation, REA, the Electricity Bills Taskforce, Octopus Energy); the Green Party's freeze |

Two figures were logged as found but not staged, because neither has a readable primary:
the Treasury's reported £600m for a £100 Warm Home Discount top-up, and the energy secretary's
reported £120 and £3.2bn levy plan.

## The gaps

**Levy removal.** The dashboard puts the option at £3.83bn and £130 a household. That is
155% above CBP's c. £1.5bn, and 145% and 210% above CBP's and RF's per-household values.

- The option does not price its two levies. It applies a press-reported £120 typical-bill
  saving (`LEVY_SAVING_TYPICAL`) as a 12.6% cut to every electricity bill.
- The two levies it names are worth about £50 a household. RF's mean averages are £26 and
  £24; Good Energy puts them at £0.61bn and £0.57bn.
- £120 is what producers put on removing every remaining policy cost: RF's mean of £128, the
  MCS Foundation's £120 and the REA's £112. Those estimates sit beside the option as concept
  mismatches.
- Against those wider scopes, the dashboard's cost is within 2% of RF's £3.75bn (every
  remaining policy cost plus the Carbon Price Support) and 20–28% above the REA's £3.2bn and
  the MCS Foundation's £3bn.
- The annotation cites the code, CBP, RF, MCS Foundation, REA, Good Energy and HM Treasury's
  costing of the 75% of the RO already moved.

**Warm Home Discount top-up reach.** The dashboard reaches 7.85m households, 33% above DESNZ's
5.9m rebates.

- The dashboard's proxy pays every household with a means-tested benefit. That population is
  close to DESNZ's 8.3m households on a qualifying benefit, an English Housing Survey count
  cited in the annotation rather than staged.
- DESNZ's impact assessment explains why only about 70–85% of those households get the rebate.
- On DESNZ's 5.9m, £100 a household would cost about £0.59bn, against the dashboard's £0.78bn.
  No producer's costing of the top-up has a readable primary.

**Close matches.**

| Comparison | Dashboard against producer |
|---|---|
| Targeted discount cost (RF) | +7% |
| Targeted discount share of households (RF) | +4% |
| VAT extension cost in 2027-28 (IFS) | −3% |
| VAT extension cost in 2027-28 (RF) | −15% |
| VAT cut's average saving (DESNZ) | +9% |

RF's £1.7bn is twice the government's £850m for six winter months, so it is staged with
`source_model: arithmetic`.

**Denominators.** The dashboard's shares and means count all UK households, with Northern
Ireland at zero for the options paid only in Great Britain. Against Great Britain figures they
therefore read slightly low.

## Periods

Producers give levy, VAT and per-household figures per year at 2026 rates. These are staged
against 2027-28, the first full year of a measure announced at the Budget and the only year the
dashboard costs those options; `conditions.period_basis` says so on each claim.

The year does not explain the levy gap. On the Treasury's costing the RO part falls in 2027-28,
and the FiT part (£0.57bn to c. £0.73bn) is too small to make up a difference of about £2.3bn.

## Not read

- Energy UK's report returned 401.
- Cornwall Insight, the Commons Library and obr.uk returned 403. The OBR was read through
  Wayback and gov.uk mirrors.
- ifs.org.uk's HTML pages returned 403. The Green Budget PDF was read, but its launch day
  could not be confirmed (the PDF was created on 10 October, first archived on 15 October), so
  its date is the month as printed.
- landmaneconomics.co.uk did not resolve.
- The Guardian and FT reports are known only from press citations.
- The session's web search budget ran out before an obr.uk site search and deeper searches of
  ECIU, Green Alliance, Uswitch and MoneySavingExpert.
