# Belgian PIT reform 2026 source notes

## Scope

This package stages seven descriptive revenue-change claims for the Belgian personal-income-tax reform enacted by the loi du 15 juillet 2026 and published in the *Moniteur belge* on 29 July 2026, page 40196. It does not claim that the three models share a period basis, population, baseline construction, or methodology.

Raw PDFs and the upstream Axiom artifacts remain outside this repository. `manifest.jsonl` pins their SHA-256 digests; every row in `claims.json` names its source pins.

## Official horizon statements

- SPF Finances: −EUR 4,000,000,000 at horizon 2030. DOC 56 1243/004 states “diminution des recettes fiscales de 4 milliards d’euros à l’horizon 2030”; the debate also states EUR 4.3 billion by 2030. The registered value is the requested −EUR 4.0 billion claim. The bill says the internal model uses assessment-year-2023 microdata; its methodology is unpublished. Pins: `doc56_1243_004_pdf`, `doc56_1243_001_pdf`.
- Cour des comptes: −EUR 5,000,000,000 at horizon 2030. DOC 56 1243/004 states “la Cour des comptes évalue celle-ci à près de 5 milliards d’euros à l’horizon 2030”. This is a secondary citation: the Cour des comptes advice document is not pinned. Pin: `doc56_1243_004_pdf`.

Neither horizon-2030 statement identifies whether 2030 is an income year, an assessment year, or another annual basis. The adapter records that ambiguity and does not resolve it.

## PolicyEngine series

The requested claim values are keyed to income year, with the assessment year carried separately:

| Income year | Assessment year | Revenue change, EUR | Pins |
|---:|---:|---:|---|
| 2026 | 2027 | −513,450,000 | `lane_aged3_report`, `v05h_aged_results` |
| 2027 | 2028 | −456,510,000 | `lane_aged3_report`, `v05h_aged_results` |
| 2028 | 2029 | −779,680,000 | `lane_aged3_report`, `v05h_aged_results` |
| 2029 | 2030 | −2,457,460,000 | `lane_aged3_report`, `v05h_aged_results` |
| 2030 | 2031 | −4,155,520,000 | `lane_aged3_report`, `v05h_aged_results` |

These are nominal-EUR, no-behavioural-response results from the corrected v05h aged run at commit `3d9f690`. Each result compares the reform with its same-year indexed current-law baseline: the encoded Article 178 chain and statutory special coefficients, declared FPB income uprating on fixed 2025 weights, and Royal-Decree-pending Article 147 values carried at their last enacted levels. The series is draft and pending standard validation procedures.

## Registry treatment

All seven claims are held out; none is a calibration target. The official claims are `different_model`; the five PolicyEngine claims are `same_assumptions` because their result rows project the same pinned computation. Those self-attachments let the committed populations feed carry the computation provenance, but they are not independent validation. The income-year-2030 result also attaches to the two official horizon-2030 claims with `constructed` status solely to make the three sources visible in the existing result-backed export. Its annotation preserves the unknown official period basis and does not treat the values as sharing the PolicyEngine income-year basis.
