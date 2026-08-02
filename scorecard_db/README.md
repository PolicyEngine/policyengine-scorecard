# scorecard_db

The Scorecard database: every claim an external model makes that PolicyEngine
can check, one SQLite file, reform-keyed.

## Design (Max, 2026-08-01)

- **Reform-keyed.** Every row references the policy world it scores:
  `baseline` (current law) for level validation, a PolicyEngine parametric
  reform for score validation, an Axiom rulespec reference reserved. A level
  is a score of the null reform — modes 1 and 2 share one table.
- **Populace-targets shape.** Row = `ledger_fact` (a Ledger
  `validation_comparator` fact id once cataloged; inline publication
  provenance until then) + closed-vocabulary `metric` / `unit_concept` /
  `time_basis` + an open `conditions` mapping (geography, program, subgroup,
  methodological `variant`, `rate_unit`, …). Adapters fail loudly on
  anything unmapped.
- **`calibration_relationship` mandatory** (`consumed_as_target` /
  `seed_source` / `held_out`). Published validation wins = held_out only.
- **History, not state.** `pe_results` keeps every computation (engine
  version × certified data bundle × run); the `comparisons` view joins each
  claim to its latest result. Re-scoring on a new certified artifact appends.
- **Mission control.** `lanes` tracks live stage per source×area lane
  (registered → cataloged → ingested → computed → diagnosing → published →
  regressed); `diagnoses` records adjudications with action links.

## Use

```bash
PYTHONPATH=. python -m scorecard_db.ingest_urban data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_platform data/scorecard.db
python -m pytest tests/test_scorecard_db.py
```

```python
from scorecard_db import ScorecardDB
db = ScorecardDB("data/scorecard.db")
db.comparisons(program="snap", geography="US", held_out_only=True)
db.coverage()
```

First population: Urban SotSN — 30,004 claims (24,717 published values).
`calibration_relationship` is assigned per (program, metric) from the
certified build's documented target surface and seeds
(`scorecard_db/relationships.py`), never defaulted: SNAP/SSI participation
and refundable-CTC counts are `consumed_as_target`, TANF participation is
`seed_source` (ASPE/TRIM3), everything else `held_out`. PE results: the
interchange's 678 totals (run `sotsn-first-cut`) plus the platform's 7,912
subgroup × state grid (run `platform-grid-2024`, with the real status
taxonomy and annotation ids); the `comparisons` view serves the latest per
claim. Counterfactual worlds use the `policyengine_us_inputs` framework —
input-override descriptors (forced take-up flags), not parametric reform
paths, because no such parameters exist in the engine.
