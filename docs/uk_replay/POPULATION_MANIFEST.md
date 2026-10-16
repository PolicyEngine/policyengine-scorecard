# Population manifest contract

The [v1 schema](schemas/population_manifest.v1.json) makes the identity tuple
in [PLAN.md](PLAN.md) machine readable. One manifest identifies one event and
costing FY. It may bind an artifact containing several annual periods, but
each event/FY identity is explicit. This slice supplies the contract only;
it creates no historical population or certification.

## Identity fields

| Field | Meaning and allowed resolved value |
|---|---|
| `event_slug` | Inventory event key, a lowercase underscore slug. |
| `costing_fy` | Original source FY `YYYY-YY`; the second year must follow the first. |
| `policy_world` | Approved contract id/digest and the calibrated world. `published_end_state_same_weights.v1` uses `published_end_state`; `documented_pre_measures_bridge.v1` uses `pre_measures`. |
| `historical_survey_release` | FRS release id `frs_YYYY_YY`, first-publication date and digest of the receipt pinning its licensed inputs and donor provenance. |
| `forecast_release_identity` | OBR EFO release id, SHA-256 of the selector file's bytes and the source lock's canonical receipt digest. This separates different forecasts of the same FY. |
| `annualisation_bridge` | Reviewed bridge id and receipt digest covering original FY versus stored annual periods, part-year law and cash/liability conventions. |
| `engine_commit` | Full 40-character lowercase Git commit of the engine used to build and score the population. A package version alone is insufficient. |
| `population_artifact_digest` | Lowercase SHA-256 of the exact population bytes. |
| `certification_receipt` | Receipt digest plus the same engine commit, population digest and certified `data_years`. The referenced receipt carries the target, holdout and compatibility evidence. |

`schema_version` is `population_manifest.v1`. `status` is `draft` or
`certified`. `data_years` lists the artifact's explicit annual coverage as
source FYs under its bridge, rather than assuming that a base-year artifact
can be aged backward. No field is inferred from today's default dataset.

## Equality and unresolved decisions

Two resolved manifests identify the same population only if all nine
identity fields above are equal. Compare their JSON values after sorting
object keys; whitespace and object-key order do not matter. Array order is
significant, so producers must sort `data_years` chronologically. This is
logical identity, not a claim that two independently generated H5 files
with different byte digests contain equivalent records. The same H5 used
for a different event, FY, forecast, policy world, bridge, engine or
certification has a different identity.

Drafts can use `{"status":"pending","value":"pending","proposal":
"docs/uk_replay/POLICY_WORLD_CONTRACT.md"}` for any unresolved identity field
other than the known event and costing FY. A pending artifact or certification
digest is never filled with zeros. Pending drafts do not establish population
equivalence and are ineligible for execution. The schema forbids pending
identity fields in a `certified` manifest.

## Semantic certification gates

In addition to schema validation, the future registry/runner must verify:

1. The selector and source-lock digests resolve to the committed bytes;
   the manifest's event, survey and forecast agree with that selector.
2. The survey publication precedes the event and its licensed input receipt
   identifies the reviewed release and donor vintages.
3. `costing_fy` belongs to the selector's full scoring horizon and to
   `data_years`; every declared year has inputs under the reviewed bridge.
4. The certification binds the actual loaded artifact digest and the same
   build/scoring engine commit. Its `data_years` equals the manifest's
   declared coverage, ordered chronologically.
5. The receipt carries source/target exclusions, held-out checks,
   policy-world orientation and FY/CY and cash/liability mappings. OBR
   policy costings remain held out. Survey-derived tax-benefit totals are
   prohibited calibration targets under [ARCHITECTURE.md](../ARCHITECTURE.md).

These equality/coverage and receipt-content checks compare values across
files and are outside JSON Schema's shape validation. They are design
requirements for the [historical adapter](HISTORICAL_ADAPTER.md), not claims
that the current runner implements them. A different scoring engine requires
a new reviewed build/certification identity; track 1's certification is not
inherited by historical releases.
