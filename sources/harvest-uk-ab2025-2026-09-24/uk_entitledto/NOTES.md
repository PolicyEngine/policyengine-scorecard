# uk_entitledto — entitledto, Autumn Budget 2025 harvest (2026-09-24)

Source `entitledto`, `source_model: scheme_survey`, `benchmark_class: administrative_fact`. One
publication, five scheme counts describing the interaction between the announced two-child-limit
removal and income-banded Council Tax Reduction schemes in England.

## Access recipe

- entitledto.co.uk `robots.txt` disallows only `?cid=` variants. The blog page fetched directly, HTTP
  200, 1,392,224 bytes (the page embeds registration lists of employment-support organisations); the
  blog body is about 1,000 words and the extractor's second occurrence of the headline marks its start.

## Coverage tally (seed bullets → rows)

- 2 Dec "Local Authorities left with their hands-tied" — 1 bullet → 5 rows, one per count in the
  sentence "Out of the 126 income-banded schemes currently in operation we found that 89 take the UC
  child element into account as income. Of these, only 8 designed a scheme that offers extra support to
  families with more than 2 children, 4 extend their household types to include households with 3+
  children and a further 4 include households with 4+ children in their scheme design." NOT staged:
  nothing quantified remains — the page gives no household count, no GBP clawback and no timetable
  modelling (the seed's "Not quantified" list is confirmed).

## Corrections to the seed inventory

- None. Survey year is not printed; "currently in operation" is carried as FY 2025-26.

## Baselines

- `baseline_policy: null`; the counts describe scheme design as it stands, keyed to
  `ab2025__uc_child_element_remove_two_child_limit` because their only relevance to the harvest is the
  knock-on of that measure (reform_hint is the page's own framing sentence). The ingest may treat them
  as non-comparable scheme facts.

## Attribution decisions

- own (5): entitledto's annual CTR scheme survey.

## Proposals (proposed_metric / proposed_unit) with the producer's definition

- `scheme_count` with `proposed_unit: ctr_schemes`: counts of English working-age Council Tax
  Reduction schemes — "income-banded CTR schemes, which have moved away from an approach based on
  applicable amounts, income is instead compared directly against a table of income ranges appropriate
  to the claimant’s household makeup"; the subgroup axis carries which nested count each row is.

## Manifest (primaries fetched 2026-09-24, sha256 + bytes)

- 2025-12-02 · html · direct · `f2b8e6dd84b40b72…` · 1,392,224 bytes · Local Authorities left with their hands-tied by lifting of the 2-child limit (Phil Agulnik, Karen Holmes)  
  https://www.entitledto.co.uk/blog/2025/december/02/local-authorities-left-with-their-hands-tied-by-lifting-of-the-2-child-limit/

## Row tally by publication and measure key

- 2025-12-02: 5 rows

- measure_key `ab2025__uc_child_element_remove_two_child_limit`: 5

## Attribution and class counts

- attribution: own 5
- benchmark_class: administrative_fact 5
- source_model: scheme_survey 5
- baseline_policy: None 5
- value_kind: point 5; time_basis: fiscal_year 5; parse_confidence: high 5

## Registered metrics and units used

- metric: 
- unit_concept: 

## Distinct values on every conditions axis

- `data_scope` (1): entitledto annual Council Tax Reduction scheme survey (working-age schemes currently in operation)
- `fiscal_event` (1): autumn_budget_2025
- `fy` (1): 2025-26
- `geography` (1): England
- `measure_type` (1): interaction of the two-child-limit removal with income-banded CTR schemes that count the UC child element as income
- `program` (1): council_tax_reduction
- `subgroup` (5): income-banded CTR schemes currently in operation | income-banded schemes that take the UC child element into account as income | of those 89: schemes designed to offer extra support to families with more than 2 children | of those 8: schemes that extend their household types to include households with 3+ children | of those 8: schemes that include households with 4+ children in their scheme design
