# Evidence for the policy-experiment findings

Each file backs a claim in [EXPERIMENTS.md](../../EXPERIMENTS.md) or the PR body.

## Marriage Allowance trigger (PolicyEngine/policyengine-uk#2551)

`marriage_allowance_cps_trigger.py` takes two synthetic married couples in
2025 and sets the statutory rate to 0. It was run on policyengine-uk 2.143.0
with policyengine-core 3.33.3:

    uvx --python 3.12 --with policyengine-uk==2.143.0 --with policyengine-core==3.33.3 python -I marriage_allowance_cps_trigger.py

Output on 21 October 2026, `marriage_allowance` and `income_tax` for the
earner and the partner:

| Couple | Current law (10%) | Statutory rate 0 |
|---|---|---|
| £30,000 earner (basic rate) | allowance 1,260 / 0; income tax 3,234 / 0 | allowance 1,260 / 0; income tax 3,234 / 0 (unchanged) |
| £60,000 earner (higher rate) | allowance 0 / 0; income tax 11,432 / 0 | allowance 1,260 / 0; income tax 10,928 / 0 (−£504) |

The UK hub session confirmed the trigger on policyengine-uk main (`ecd531776`):
`create_marriage_tax_reform` still switches on with
`remove_income_condition or rate != original_rate`.

## The dataset token reads `populace-uk-private`

A scratch workflow on branch `scratch/hf-access-check` (deleted after the
run) sent HEAD requests with the organisation secret
`PE_UK_PRIVATE_HF_READ_TOKEN` and printed only the status codes. The run is
https://github.com/PolicyEngine/policyengine-scorecard/actions/runs/39639406596
(21 October 2026, success):

| Status | Path |
|---|---|
| 302 | `datasets/policyengine/populace-uk-private/resolve/microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/microcosm_uk_2024_25.h5` |
| 200 | `datasets/policyengine/populace-uk-private/resolve/microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/releases/microcosm-uk-2024-25-national/release_manifest.json` |
| 302 | `policyengine/policyengine-uk-data-private/resolve/1.58.1/enhanced_frs_2024_25.h5` (control) |

Both 302 (a redirect to the file store) and 200 are answers to an accepted
token. For comparison, the same HEAD request for the release manifest without
a token returned 401 on 21 October 2026.

## Gross receipts are absent from both data lines

`column_check.py` lists which of four variables a dataset carries, by name
only:

    uvx --with h5py python -I column_check.py <dataset.h5>

Output on 22 October 2026:

| Column | Microcosm UK 2024-25 (SHA-256 `810ba980…`) | policyengine-uk-data enhanced FRS 2024-25 (HF cache snapshot `2526edbb…`) |
|---|---|---|
| `self_employment_gross_receipts` | absent | absent |
| `uses_property_allowance` | absent | absent |
| `self_employment_income` | present | present |
| `property_income` | present | present |

## Model-swap mechanisms

`swap_mechanisms.py` puts two synthetic households through policyengine-uk
2.132.6 and 2.143.0 in 2025:

    uvx --python 3.12 --with policyengine-uk==<version> --with policyengine-core==3.33.3 python -I swap_mechanisms.py

Output on 22 October 2026:

| Household | 2.132.6 | 2.143.0 |
|---|---|---|
| £20,000 of earnings, £3,000 of interest | starting-rate income £3,000; income tax £1,486 with or without the personal savings allowance | starting-rate income £0; income tax £1,886, or £2,086 without the allowance |
| £62,000 of earnings, £4,000 of employee pension contributions, one child | adjusted net income £62,000; child benefit charge £135 | adjusted net income £58,000; charge £0 |

The first is the savings starting-rate taper (35f992c6a, #1799). The second is
relieved pension contributions in adjusted net income (1dbc88172). Both are in
`data/uk/experiments/diagnoses.json`.
