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

Column names only, read with h5py from the two cuts:

| Column | Microcosm UK 2024-25 (`810ba980…`) | policyengine-uk-data enhanced FRS 2024-25 (HF cache snapshot `2526edbb…`) |
|---|---|---|
| `self_employment_gross_receipts` | absent | absent |
| `uses_property_allowance` | absent | absent |
| `self_employment_income` | present | present |
| `property_income` | present | present |
