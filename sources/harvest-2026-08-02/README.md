# Overnight harvest staging (2026-08-02)

One dir per source: manifest.jsonl (one line per document: url, title, date,
sha256, local_path, doc_type), downloads/, claims_staged.jsonl (Scorecard
ExternalScore-shaped rows — verbatim extracted values ONLY, with
source_column + publication provenance; use proposed_metric/proposed_unit
when the closed vocabularies in
~/PolicyEngine/policyengine-scorecard/scorecard_db/models.py lack a fit —
NEVER invent enum values), NOTES.md (coverage, gaps, parse confidence).

Ingestion (morning): validate claims_staged rows against models.py, extend
Metric/UnitConcept deliberately where proposed_* recur, then adapter per
source into data/scorecard.db (see scorecard_db/ingest_urban.py as the
pattern). Repo tree is owned by the platform session — stage here, never
write there. Lane updates on ingest, not harvest.
