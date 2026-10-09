# SDLT and CGT construction audit

The pinned formulas and certified inputs identify two limits relevant to the
Autumn Budget 2024 comparisons. Their national contributions remain **unsized**.
These are construction and data-flow observations, not additional model-error
diagnoses or an explained share. The
[receipt](../../results/uk/events/CONSTRUCTION_AUDIT.json) retains full source
file SHA-256 values, line-numbered excerpts, input column names and aggregates.

For SDLT, the bundle supplies `property_purchased` and
`other_residential_property_value`, but no direct main/additional purchase-price
fields. `additional_residential_property_purchased.py:12–17` multiplies the stock
of other residential property by that purchase flag. The flag's documentation
says whether all property wealth was bought in the year; its default is false.
The transaction tax formula applies the additional-property scale to the
resulting price. This uses a transaction-price proxy based on flagged wealth.
It does not charge SDLT on every household's property stock.

In the base-year inputs, 20,080 of 535,080 household rows have the flag set;
1,740 also have positive other-property wealth. The weighted purchaser count
is 943,619.65, within 28,840,551.18 weighted households. Weighted other-property
wealth is £1,140.779bn overall and £94.693bn after applying the purchase flag.
These aggregates precede the England/Northern Ireland eligibility mask,
minimum-price thresholds, annual uprating and reform aggregation. Raw row
counts include 267,540 capital-gains clone households. They are not counts of
independent observations or a national SDLT effect.

`economic_assumptions.py:35–52` copies the base population into subsequent
years. The uprating table grows other-property values with per-capita GDP but
does not change the purchase flag. This path supplies no annual purchaser
resampling or direct replacement with observed transaction-price flows. Its
relevance belongs to `construction_scope`, `head_scope` and
`population_vintage`; the audit does not size their contributions.

For CGT, `capital_gains_tax.py:34–55` takes one pooled gains amount, subtracts
the annual exemption, allocates gains by income bands and applies the main
basic/higher/additional rate parameters. The formula has no asset-type, BADR,
Investors' Relief or carried-interest branch. The bundle supplies one
`capital_gains` column, without gain-type allocation. A reversal of the main
rate parameters therefore cannot isolate announcement-affected gain types
through these inputs. This is a scope limitation, without a quantified
residual attribution.

The CGT replay is static. The loader moves the supplied gains into
`capital_gains_before_response` (`simulation.py:191,548–563`), so direct input
does not bypass the response calculation. Instead, the pinned
`capital_gains_responses/elasticity.yaml:2–3` sets elasticity to zero, and
`capital_gains_behavioural_response.py:17–18` returns zero at that setting.
The managed wrapper forwards the registry reform without an elasticity
override. Gains are subsequently uprated with per-capita GDP. This supports
the `behavioural_adjustment` tag alongside the construction and vintage axes.

The [source-head audit](../../results/uk/events/SOURCE_HEAD_AUDIT.md) separately
establishes that the small OBR CGT-head amount is a genuine disaggregated
original-event costing. The OBR whole-package yield also includes other tax
and spending heads. Neither the pooled-gains observation nor the SDLT input
proxy resolves the remaining numerical differences by itself.

Reproduce the inspection from the repository root in the pinned environment:

```bash
.venv-replay/bin/python -m pipeline.audit_uk_event_constructions --dataset data/uk/policyengine-local/policyengine_uk_data/storage/populace_uk_2023.h5
```

Use `--dataset` to point to another local copy of the same certified bytes,
and `--output` for an isolated receipt. The script hashes the dataset before
opening HDF5 and checks the installed package metadata. It reads source files
and aggregate inputs only; it imports no PolicyEngine package, constructs no
simulation and uses no network or compute-provider calls. Source hashes and
script hash in the receipt allow the inspection to be checked against the
same pinned files.
